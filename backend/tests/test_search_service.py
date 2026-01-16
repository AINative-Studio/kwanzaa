"""Tests for search service."""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.search import ProvenanceFilters, SearchRequest
from app.services.search import SearchService


class TestSearchService:
    """Tests for SearchService."""

    @pytest.fixture
    def search_service(self, mock_embedding_service: MagicMock) -> SearchService:
        """Create search service with mocked dependencies."""
        return SearchService(embedding_service=mock_embedding_service)

    @pytest.fixture
    def mock_zerodb_search(
        self, mock_search_results: List[Dict]
    ) -> AsyncMock:
        """Create mock ZeroDB search function."""
        async def search_func(
            query_vector: List[float],
            namespace: str,
            filter_metadata: Dict[str, Any] | None,
            limit: int,
            threshold: float,
        ) -> List[Dict]:
            return mock_search_results

        return AsyncMock(side_effect=search_func)

    @pytest.mark.unit
    async def test_basic_search(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_zerodb_search: AsyncMock,
        mock_embedding: List[float],
        sample_search_request: Dict,
    ) -> None:
        """Test basic semantic search without filters."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        request = SearchRequest(**sample_search_request)

        # Execute search
        response = await search_service.search(request, mock_zerodb_search)

        # Verify embedding generation was called
        mock_embedding_service.generate_embedding.assert_called_once_with(request.query)

        # Verify ZeroDB search was called
        mock_zerodb_search.assert_called_once()

        # Verify response structure
        assert response.status == "success"
        assert response.query.text == request.query
        assert response.query.namespace == request.namespace
        assert response.total_results == 2
        assert len(response.results) == 2

        # Verify results are ordered by rank
        assert response.results[0].rank == 1
        assert response.results[1].rank == 2
        assert response.results[0].score >= response.results[1].score

        # Verify metadata is present
        assert response.results[0].metadata.citation_label
        assert response.results[0].metadata.canonical_url
        assert response.results[0].metadata.source_org
        assert response.results[0].metadata.year

        # Verify search metadata
        assert response.search_metadata.execution_time_ms > 0
        assert response.search_metadata.query_embedding_time_ms == 10
        assert response.search_metadata.search_time_ms >= 0

    @pytest.mark.unit
    async def test_search_with_provenance_filters(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_zerodb_search: AsyncMock,
        mock_embedding: List[float],
    ) -> None:
        """Test search with provenance filters."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        request = SearchRequest(
            query="civil rights legislation",
            namespace="kwanzaa_primary_sources",
            filters=ProvenanceFilters(
                year_gte=1960,
                year_lte=1970,
                content_type=["proclamation", "legal_document"],
                source_org=["National Archives"],
            ),
            limit=10,
            threshold=0.75,
        )

        # Execute search
        response = await search_service.search(request, mock_zerodb_search)

        # Verify ZeroDB was called with correct filters
        call_args = mock_zerodb_search.call_args
        assert call_args is not None

        filter_metadata = call_args.kwargs["filter_metadata"]
        assert filter_metadata["year_gte"] == 1960
        assert filter_metadata["year_lte"] == 1970
        assert filter_metadata["content_type"] == {"$in": ["proclamation", "legal_document"]}
        assert filter_metadata["source_org"] == {"$in": ["National Archives"]}

        # Verify response includes filter information
        assert response.query.filters_applied is not None
        assert response.query.filters_applied["year_gte"] == 1960

    @pytest.mark.unit
    async def test_search_with_persona_defaults(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_zerodb_search: AsyncMock,
        mock_embedding: List[float],
    ) -> None:
        """Test that persona key applies correct defaults."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        request = SearchRequest(
            query="explain voting rights",
            persona_key="educator",
        )

        # Execute search
        response = await search_service.search(request, mock_zerodb_search)

        # Verify educator persona defaults were applied
        # Educator should have threshold 0.80 and namespace kwanzaa_primary_sources
        call_args = mock_zerodb_search.call_args
        assert call_args is not None
        assert call_args.kwargs["threshold"] == 0.80
        assert call_args.kwargs["namespace"] == "kwanzaa_primary_sources"

    @pytest.mark.unit
    async def test_search_persona_does_not_override_explicit_values(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_zerodb_search: AsyncMock,
        mock_embedding: List[float],
    ) -> None:
        """Test that explicit values are not overridden by persona defaults."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        request = SearchRequest(
            query="test query",
            persona_key="educator",
            threshold=0.65,  # Explicit threshold (educator default is 0.80)
            namespace="kwanzaa_black_stem",  # Explicit namespace
        )

        # Execute search
        response = await search_service.search(request, mock_zerodb_search)

        # Verify explicit values were preserved
        call_args = mock_zerodb_search.call_args
        assert call_args is not None
        assert call_args.kwargs["threshold"] == 0.65  # Not 0.80
        assert call_args.kwargs["namespace"] == "kwanzaa_black_stem"

    @pytest.mark.unit
    async def test_search_with_limit(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_zerodb_search: AsyncMock,
        mock_embedding: List[float],
    ) -> None:
        """Test search respects limit parameter."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        request = SearchRequest(
            query="test",
            limit=5,
        )

        # Execute search
        await search_service.search(request, mock_zerodb_search)

        # Verify limit was passed to ZeroDB
        call_args = mock_zerodb_search.call_args
        assert call_args is not None
        assert call_args.kwargs["limit"] == 5

    @pytest.mark.unit
    async def test_search_with_embeddings_included(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_zerodb_search: AsyncMock,
        mock_embedding: List[float],
        mock_search_results: List[Dict],
    ) -> None:
        """Test search can include embeddings in results."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        # Add embeddings to mock results
        for result in mock_search_results:
            result["embedding"] = mock_embedding

        request = SearchRequest(
            query="test",
            include_embeddings=True,
        )

        # Execute search
        response = await search_service.search(request, mock_zerodb_search)

        # Verify embeddings are included in results
        assert response.results[0].embedding is not None
        assert len(response.results[0].embedding) == 1536

    @pytest.mark.unit
    async def test_search_handles_empty_results(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_embedding: List[float],
    ) -> None:
        """Test search handles empty result set gracefully."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        # Mock ZeroDB returning empty results
        async def empty_search(*args: Any, **kwargs: Any) -> List[Dict]:
            return []

        mock_empty_search = AsyncMock(side_effect=empty_search)

        request = SearchRequest(query="obscure query")

        # Execute search
        response = await search_service.search(request, mock_empty_search)

        # Verify response is valid with no results
        assert response.status == "success"
        assert response.total_results == 0
        assert len(response.results) == 0

    @pytest.mark.unit
    async def test_search_handles_zerodb_error(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_embedding: List[float],
    ) -> None:
        """Test search raises appropriate error when ZeroDB fails."""
        # Setup mocks
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)

        # Mock ZeroDB raising an error
        async def failing_search(*args: Any, **kwargs: Any) -> List[Dict]:
            raise Exception("ZeroDB connection failed")

        mock_failing_search = AsyncMock(side_effect=failing_search)

        request = SearchRequest(query="test")

        # Execute search and expect RuntimeError
        with pytest.raises(RuntimeError, match="Vector search failed"):
            await search_service.search(request, mock_failing_search)

    @pytest.mark.unit
    async def test_process_results_validates_metadata(
        self,
        search_service: SearchService,
    ) -> None:
        """Test that result processing validates required metadata fields."""
        # Result missing required metadata
        invalid_result = [
            {
                "id": "test::chunk::1",
                "score": 0.9,
                "document": "test content",
                "metadata": {
                    "citation_label": "Test",
                    # Missing: canonical_url, source_org, year, content_type, license
                },
            }
        ]

        # Process results
        processed = search_service._process_results(
            raw_results=invalid_result,
            namespace="test",
            include_embeddings=False,
        )

        # Invalid result should be skipped
        assert len(processed) == 0

    @pytest.mark.unit
    async def test_process_results_handles_missing_doc_id(
        self,
        search_service: SearchService,
    ) -> None:
        """Test that doc_id is extracted from chunk_id if not in metadata."""
        result = [
            {
                "id": "test_doc::chunk::1",
                "score": 0.9,
                "document": "test content",
                "metadata": {
                    "citation_label": "Test",
                    "canonical_url": "https://example.com",
                    "source_org": "Test Org",
                    "year": 2000,
                    "content_type": "test",
                    "license": "Public Domain",
                },
            }
        ]

        # Process results
        processed = search_service._process_results(
            raw_results=result,
            namespace="test",
            include_embeddings=False,
        )

        # doc_id should be extracted from chunk_id
        assert len(processed) == 1
        assert processed[0].doc_id == "test_doc"
        assert processed[0].chunk_id == "test_doc::chunk::1"

    @pytest.mark.unit
    async def test_generate_embedding_utility(
        self,
        search_service: SearchService,
        mock_embedding_service: MagicMock,
        mock_embedding: List[float],
    ) -> None:
        """Test generate_embedding utility method."""
        mock_embedding_service.generate_embedding.return_value = (mock_embedding, 10)
        mock_embedding_service.model_name = "test-model"

        embedding, model_name = await search_service.generate_embedding("test text")

        assert embedding == mock_embedding
        assert model_name == "test-model"
        mock_embedding_service.generate_embedding.assert_called_once_with("test text")

    @pytest.mark.unit
    def test_apply_persona_defaults_educator(
        self,
        search_service: SearchService,
    ) -> None:
        """Test persona defaults for educator."""
        request = SearchRequest(
            query="test",
            persona_key="educator",
        )

        modified = search_service._apply_persona_defaults(request)

        assert modified.threshold == 0.80
        assert modified.namespace == "kwanzaa_primary_sources"

    @pytest.mark.unit
    def test_apply_persona_defaults_researcher(
        self,
        search_service: SearchService,
    ) -> None:
        """Test persona defaults for researcher."""
        request = SearchRequest(
            query="test",
            persona_key="researcher",
        )

        modified = search_service._apply_persona_defaults(request)

        assert modified.threshold == 0.75
        assert modified.namespace == "kwanzaa_primary_sources"

    @pytest.mark.unit
    def test_apply_persona_defaults_creator(
        self,
        search_service: SearchService,
    ) -> None:
        """Test persona defaults for creator."""
        request = SearchRequest(
            query="test",
            persona_key="creator",
        )

        modified = search_service._apply_persona_defaults(request)

        assert modified.threshold == 0.65
        assert modified.namespace == "kwanzaa_primary_sources"

    @pytest.mark.unit
    def test_apply_persona_defaults_builder(
        self,
        search_service: SearchService,
    ) -> None:
        """Test persona defaults for builder."""
        request = SearchRequest(
            query="test",
            persona_key="builder",
        )

        modified = search_service._apply_persona_defaults(request)

        assert modified.threshold == 0.70
        assert modified.namespace == "kwanzaa_dev_patterns"

    @pytest.mark.unit
    def test_apply_persona_defaults_no_persona(
        self,
        search_service: SearchService,
    ) -> None:
        """Test that no persona key leaves request unchanged."""
        request = SearchRequest(
            query="test",
            threshold=0.65,
            namespace="custom_namespace",
        )

        modified = search_service._apply_persona_defaults(request)

        assert modified.threshold == 0.65
        assert modified.namespace == "custom_namespace"
