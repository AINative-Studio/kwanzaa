"""Comprehensive tests for the RAG pipeline.

This test suite covers:
1. Query processing with persona settings
2. Vector retrieval from ZeroDB
3. Cross-encoder reranking
4. Context string formatting
5. Statistics collection and transparency
6. End-to-end pipeline execution
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.retrieval import (
    RAGQueryRequest,
    RAGPipelineResponse,
    RetrievalChunk,
    PersonaThresholds,
)
from app.services.rag_pipeline import RAGPipeline
from app.services.embedding import EmbeddingService
from app.services.reranker import RerankingService
from app.db.zerodb import ZeroDBClient


# Test fixtures
@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service."""
    service = MagicMock(spec=EmbeddingService)
    service.model_name = "test-embedding-model"
    service.generate_embedding = AsyncMock(
        return_value=([0.1] * 1536, 50)  # embedding, time_ms
    )
    return service


@pytest.fixture
def mock_reranking_service():
    """Create a mock reranking service."""
    service = MagicMock(spec=RerankingService)
    service.model_name = "test-rerank-model"

    async def mock_rerank(query, chunks, top_n, **kwargs):
        # Simulate reranking by reversing order and adding rerank scores
        reranked = []
        for rank, chunk in enumerate(reversed(chunks[:top_n]), start=1):
            chunk_dict = chunk.model_dump()
            chunk_dict["rank"] = rank
            chunk_dict["rerank_score"] = 0.9 - (rank * 0.1)
            chunk_dict["final_score"] = (chunk.score + chunk_dict["rerank_score"]) / 2
            reranked.append(RetrievalChunk(**chunk_dict))
        return reranked, 100  # chunks, time_ms

    service.rerank = mock_rerank
    return service


@pytest.fixture
def mock_zerodb_client():
    """Create a mock ZeroDB client."""
    client = MagicMock(spec=ZeroDBClient)

    # Mock search results
    async def mock_search(query_vector, namespace, filter_metadata, limit, threshold):
        return [
            {
                "id": f"chunk_{i}",
                "score": 0.9 - (i * 0.1),
                "document": f"This is content for chunk {i}",
                "metadata": {
                    "doc_id": f"doc_{i}",
                    "citation_label": f"Source {i}",
                    "canonical_url": f"https://example.com/doc_{i}",
                    "source_org": "Test Organization",
                    "year": 2020 + i,
                    "content_type": "test_document",
                    "license": "Public Domain",
                    "tags": ["test", f"tag_{i}"],
                },
            }
            for i in range(min(5, limit))
        ]

    client.search_vectors = mock_search
    client.close = AsyncMock()
    return client


@pytest.fixture
def rag_pipeline(mock_embedding_service, mock_reranking_service, mock_zerodb_client):
    """Create a RAG pipeline with mocked dependencies."""
    return RAGPipeline(
        embedding_service=mock_embedding_service,
        reranking_service=mock_reranking_service,
        zerodb_client=mock_zerodb_client,
    )


# Test classes
class TestRAGQueryProcessing:
    """Test query processing and persona configuration."""

    @pytest.mark.asyncio
    async def test_query_processing_with_educator_persona(self, rag_pipeline):
        """Test query processing applies educator persona settings."""
        request = RAGQueryRequest(
            query="What is Kwanzaa?",
            persona_key="educator",
        )

        query, persona_config, namespaces, filters = await rag_pipeline._process_query(
            request
        )

        assert query == "What is Kwanzaa?"
        assert persona_config["similarity_threshold"] == 0.80
        assert persona_config["max_results"] == 10
        assert persona_config["min_results"] == 3
        assert persona_config["rerank"] is True
        assert "kwanzaa_primary_sources" in namespaces

    @pytest.mark.asyncio
    async def test_query_processing_with_researcher_persona(self, rag_pipeline):
        """Test query processing applies researcher persona settings."""
        request = RAGQueryRequest(
            query="Tell me about civil rights",
            persona_key="researcher",
        )

        query, persona_config, namespaces, filters = await rag_pipeline._process_query(
            request
        )

        assert persona_config["similarity_threshold"] == 0.75
        assert persona_config["max_results"] == 20
        assert persona_config["min_results"] == 5
        assert persona_config["rerank"] is True

    @pytest.mark.asyncio
    async def test_query_processing_with_custom_overrides(self, rag_pipeline):
        """Test request-specific overrides take precedence over persona defaults."""
        request = RAGQueryRequest(
            query="Custom query",
            persona_key="educator",
            similarity_threshold=0.85,
            top_k=15,
            namespaces=["custom_namespace"],
        )

        query, persona_config, namespaces, filters = await rag_pipeline._process_query(
            request
        )

        assert persona_config["similarity_threshold"] == 0.85
        assert persona_config["max_results"] == 15
        assert namespaces == ["custom_namespace"]

    @pytest.mark.asyncio
    async def test_query_processing_strips_whitespace(self, rag_pipeline):
        """Test query is properly cleaned."""
        request = RAGQueryRequest(
            query="  Query with whitespace  ",
            persona_key="educator",
        )

        query, _, _, _ = await rag_pipeline._process_query(request)

        assert query == "Query with whitespace"


class TestRetrieval:
    """Test vector retrieval functionality."""

    @pytest.mark.asyncio
    async def test_retrieve_chunks_success(self, rag_pipeline):
        """Test successful retrieval of chunks."""
        chunks, embed_time, search_time = await rag_pipeline._retrieve_chunks(
            query="test query",
            namespaces=["test_namespace"],
            filters=None,
            top_k=5,
            threshold=0.7,
        )

        assert len(chunks) == 5
        assert all(isinstance(chunk, RetrievalChunk) for chunk in chunks)
        assert embed_time > 0
        assert search_time > 0

        # Verify chunks are ranked properly
        for i, chunk in enumerate(chunks, start=1):
            assert chunk.rank == i

        # Verify scores are descending
        scores = [chunk.score for chunk in chunks]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_retrieve_chunks_multiple_namespaces(self, rag_pipeline):
        """Test retrieval across multiple namespaces."""
        chunks, _, _ = await rag_pipeline._retrieve_chunks(
            query="test query",
            namespaces=["namespace_1", "namespace_2"],
            filters=None,
            top_k=10,
            threshold=0.7,
        )

        # Should get results from both namespaces
        assert len(chunks) <= 10

    @pytest.mark.asyncio
    async def test_retrieve_chunks_with_filters(self, rag_pipeline):
        """Test retrieval with metadata filters."""
        filters = {"year": 2020, "source_org": "Test Organization"}

        chunks, _, _ = await rag_pipeline._retrieve_chunks(
            query="test query",
            namespaces=["test_namespace"],
            filters=filters,
            top_k=5,
            threshold=0.7,
        )

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_retrieve_chunks_empty_results(self, mock_zerodb_client, rag_pipeline):
        """Test handling of empty search results."""
        mock_zerodb_client.search_vectors = AsyncMock(return_value=[])

        chunks, _, _ = await rag_pipeline._retrieve_chunks(
            query="test query",
            namespaces=["empty_namespace"],
            filters=None,
            top_k=5,
            threshold=0.7,
        )

        assert len(chunks) == 0


class TestReranking:
    """Test cross-encoder reranking functionality."""

    @pytest.mark.asyncio
    async def test_rerank_chunks_success(self, rag_pipeline):
        """Test successful reranking of chunks."""
        # Create test chunks
        chunks = [
            RetrievalChunk(
                chunk_id=f"chunk_{i}",
                doc_id=f"doc_{i}",
                namespace="test",
                content=f"Content {i}",
                score=0.8 - (i * 0.1),
                rank=i + 1,
                citation_label=f"Source {i}",
                canonical_url=f"https://example.com/{i}",
                source_org="Test Org",
                year=2020,
                content_type="test",
                license="Public Domain",
            )
            for i in range(5)
        ]

        reranked, rerank_time = await rag_pipeline._rerank_chunks(
            query="test query",
            chunks=chunks,
            top_n=3,
        )

        assert len(reranked) == 3
        assert rerank_time > 0

        # Verify rerank scores are added
        for chunk in reranked:
            assert chunk.rerank_score is not None
            assert chunk.final_score is not None

    @pytest.mark.asyncio
    async def test_rerank_chunks_empty_list(self, rag_pipeline):
        """Test reranking with empty chunk list."""
        reranked, rerank_time = await rag_pipeline._rerank_chunks(
            query="test query",
            chunks=[],
            top_n=5,
        )

        assert len(reranked) == 0
        assert rerank_time == 0


class TestContextFormatting:
    """Test context string formatting for LLM injection."""

    @pytest.mark.asyncio
    async def test_format_context_string_success(self, rag_pipeline):
        """Test formatting of context string with metadata."""
        chunks = [
            RetrievalChunk(
                chunk_id="chunk_1",
                doc_id="doc_1",
                namespace="test",
                content="This is test content about Kwanzaa.",
                score=0.92,
                rank=1,
                citation_label="National Archives (2020) — Kwanzaa",
                canonical_url="https://archives.gov/kwanzaa",
                source_org="National Archives",
                year=2020,
                content_type="historical_document",
                license="Public Domain",
                tags=["kwanzaa", "history"],
                final_score=0.95,
            ),
            RetrievalChunk(
                chunk_id="chunk_2",
                doc_id="doc_2",
                namespace="test",
                content="Additional context about the Seven Principles.",
                score=0.88,
                rank=2,
                citation_label="Library of Congress (2019) — Seven Principles",
                canonical_url="https://loc.gov/principles",
                source_org="Library of Congress",
                year=2019,
                content_type="educational_resource",
                license="Public Domain",
                tags=["principles", "nguzo saba"],
            ),
        ]

        context = await rag_pipeline._format_context_string(chunks)

        assert context.num_chunks == 2
        assert context.max_chunk_score == 0.95
        assert context.total_tokens > 0
        assert "National Archives" in context.formatted_context
        assert "Library of Congress" in context.formatted_context
        assert "kwanzaa" in context.formatted_context
        assert "Seven Principles" in context.formatted_context

    @pytest.mark.asyncio
    async def test_format_context_string_empty(self, rag_pipeline):
        """Test formatting with empty chunk list."""
        context = await rag_pipeline._format_context_string([])

        assert context.num_chunks == 0
        assert context.max_chunk_score == 0.0
        assert context.formatted_context == ""


class TestPipelineIntegration:
    """Test complete end-to-end pipeline execution."""

    @pytest.mark.asyncio
    async def test_pipeline_end_to_end_without_reranking(self, rag_pipeline):
        """Test complete pipeline without reranking."""
        request = RAGQueryRequest(
            query="What is Kwanzaa?",
            persona_key="educator",
            enable_reranking=False,
            include_context_string=True,
        )

        response = await rag_pipeline.process(request)

        assert isinstance(response, RAGPipelineResponse)
        assert response.status == "success"
        assert response.query == "What is Kwanzaa?"
        assert response.persona == "educator"
        assert len(response.chunks) > 0
        assert response.context_string is not None
        assert response.statistics.total_retrieved > 0
        assert response.statistics.total_reranked == 0
        assert response.reranking_enabled is False

    @pytest.mark.asyncio
    async def test_pipeline_end_to_end_with_reranking(self, rag_pipeline):
        """Test complete pipeline with reranking enabled."""
        request = RAGQueryRequest(
            query="Tell me about the civil rights movement",
            persona_key="researcher",
            enable_reranking=True,
            rerank_top_n=5,
            include_context_string=True,
        )

        response = await rag_pipeline.process(request)

        assert response.status == "success"
        assert response.reranking_enabled is True
        assert response.statistics.rerank_time_ms > 0
        assert response.rerank_model is not None

        # Verify chunks have rerank scores
        for chunk in response.chunks:
            assert chunk.rerank_score is not None
            assert chunk.final_score is not None

    @pytest.mark.asyncio
    async def test_pipeline_with_filters(self, rag_pipeline):
        """Test pipeline with metadata filters."""
        request = RAGQueryRequest(
            query="Historical documents from 2020",
            persona_key="educator",
            filters={"year": 2020, "content_type": "historical_document"},
            enable_reranking=False,
        )

        response = await rag_pipeline.process(request)

        assert response.status == "success"
        assert response.statistics.filters_applied is not None

    @pytest.mark.asyncio
    async def test_pipeline_persona_thresholds(self, rag_pipeline):
        """Test that persona thresholds are correctly applied."""
        request = RAGQueryRequest(
            query="Test query",
            persona_key="educator",
        )

        response = await rag_pipeline.process(request)

        assert isinstance(response.persona_thresholds, PersonaThresholds)
        assert response.persona_thresholds.similarity_threshold == 0.80
        assert response.persona_thresholds.max_results == 10
        assert response.persona_thresholds.min_results == 3
        assert response.persona_thresholds.rerank is True

    @pytest.mark.asyncio
    async def test_pipeline_statistics_collection(self, rag_pipeline):
        """Test that statistics are properly collected."""
        request = RAGQueryRequest(
            query="Test statistics",
            persona_key="researcher",
            enable_reranking=True,
        )

        response = await rag_pipeline.process(request)

        stats = response.statistics
        assert stats.total_retrieved >= 0
        assert stats.embedding_time_ms > 0
        assert stats.search_time_ms > 0
        assert stats.total_time_ms > 0
        assert len(stats.namespaces_searched) > 0

        if stats.total_retrieved > 0:
            assert 0.0 <= stats.top_score <= 1.0
            assert 0.0 <= stats.average_score <= 1.0

    @pytest.mark.asyncio
    async def test_pipeline_without_context_string(self, rag_pipeline):
        """Test pipeline when context string is not requested."""
        request = RAGQueryRequest(
            query="Test without context",
            persona_key="educator",
            include_context_string=False,
        )

        response = await rag_pipeline.process(request)

        assert response.context_string is None

    @pytest.mark.asyncio
    async def test_pipeline_custom_namespaces(self, rag_pipeline):
        """Test pipeline with custom namespace list."""
        request = RAGQueryRequest(
            query="Custom namespace query",
            persona_key="educator",
            namespaces=["custom_ns_1", "custom_ns_2"],
        )

        response = await rag_pipeline.process(request)

        assert "custom_ns_1" in response.statistics.namespaces_searched
        assert "custom_ns_2" in response.statistics.namespaces_searched


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_pipeline_with_empty_query(self, rag_pipeline):
        """Test pipeline rejects empty queries."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            request = RAGQueryRequest(
                query="",
                persona_key="educator",
            )

    @pytest.mark.asyncio
    async def test_pipeline_with_invalid_persona(self, rag_pipeline):
        """Test pipeline handles invalid persona gracefully."""
        with pytest.raises(ValueError, match="must match pattern"):
            request = RAGQueryRequest(
                query="Test query",
                persona_key="invalid_persona",
            )

    @pytest.mark.asyncio
    async def test_pipeline_zerodb_failure_resilience(
        self, mock_embedding_service, mock_reranking_service
    ):
        """Test pipeline handles ZeroDB failures gracefully."""
        failing_client = MagicMock(spec=ZeroDBClient)
        failing_client.search_vectors = AsyncMock(
            side_effect=Exception("ZeroDB connection failed")
        )
        failing_client.close = AsyncMock()

        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            reranking_service=mock_reranking_service,
            zerodb_client=failing_client,
        )

        request = RAGQueryRequest(
            query="Test query",
            persona_key="educator",
        )

        response = await pipeline.process(request)

        # Should return empty results but not crash
        assert response.statistics.total_retrieved == 0


class TestContextManager:
    """Test async context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager_closes_client(
        self, mock_embedding_service, mock_reranking_service, mock_zerodb_client
    ):
        """Test that context manager properly closes ZeroDB client."""
        async with RAGPipeline(
            embedding_service=mock_embedding_service,
            reranking_service=mock_reranking_service,
            zerodb_client=mock_zerodb_client,
        ) as pipeline:
            request = RAGQueryRequest(
                query="Test query",
                persona_key="educator",
            )
            await pipeline.process(request)

        # Verify client was closed
        mock_zerodb_client.close.assert_called_once()
