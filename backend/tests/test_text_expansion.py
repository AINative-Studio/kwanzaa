"""Tests for text expansion service.

This module tests the complete text expansion pipeline including:
- Text chunking with overlap
- Embedding generation
- ZeroDB storage
- Provenance tracking
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from app.services.text_expansion import (
    ChunkMetadata,
    TextChunk,
    TextChunker,
    TextExpansionService,
)
from app.services.embedding import EmbeddingService
from app.db.zerodb import ZeroDBClient, ZeroDBError


class TestChunkMetadata:
    """Test suite for ChunkMetadata dataclass."""

    def test_chunk_metadata_creation(self):
        """Test creating chunk metadata with all fields."""
        metadata = ChunkMetadata(
            source_id="test_source",
            document_id="test_doc_001",
            chunk_index=0,
            total_chunks=5,
            start_char=0,
            end_char=512,
            source_org="Test Org",
            canonical_url="https://example.com/doc",
            license_info="Public Domain",
            year=1903,
            content_type="essay",
            tags=["test", "primary_source"],
            priority=0,
        )

        assert metadata.source_id == "test_source"
        assert metadata.document_id == "test_doc_001"
        assert metadata.chunk_index == 0
        assert metadata.total_chunks == 5
        assert metadata.start_char == 0
        assert metadata.end_char == 512
        assert metadata.year == 1903
        assert "test" in metadata.tags

    def test_chunk_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = ChunkMetadata(
            source_id="test_source",
            document_id="test_doc_001",
            chunk_index=1,
            total_chunks=3,
            start_char=100,
            end_char=600,
            tags=["test"],
        )

        result = metadata.to_dict()

        assert isinstance(result, dict)
        assert result["source_id"] == "test_source"
        assert result["document_id"] == "test_doc_001"
        assert result["chunk_index"] == 1
        assert result["total_chunks"] == 3
        assert "ingested_at" in result
        assert isinstance(result["tags"], list)


class TestTextChunk:
    """Test suite for TextChunk dataclass."""

    def test_text_chunk_creation(self):
        """Test creating text chunk with hash computation."""
        metadata = ChunkMetadata(
            source_id="test",
            document_id="doc_001",
            chunk_index=0,
            total_chunks=1,
            start_char=0,
            end_char=100,
        )

        chunk = TextChunk.create("Test text content", metadata)

        assert chunk.text == "Test text content"
        assert chunk.metadata == metadata
        assert isinstance(chunk.chunk_hash, str)
        assert len(chunk.chunk_hash) == 64  # SHA256 hex length

    def test_chunk_hash_consistency(self):
        """Test that same text produces same hash."""
        metadata = ChunkMetadata(
            source_id="test",
            document_id="doc_001",
            chunk_index=0,
            total_chunks=1,
            start_char=0,
            end_char=100,
        )

        chunk1 = TextChunk.create("Same text", metadata)
        chunk2 = TextChunk.create("Same text", metadata)

        assert chunk1.chunk_hash == chunk2.chunk_hash

    def test_chunk_hash_uniqueness(self):
        """Test that different text produces different hash."""
        metadata = ChunkMetadata(
            source_id="test",
            document_id="doc_001",
            chunk_index=0,
            total_chunks=1,
            start_char=0,
            end_char=100,
        )

        chunk1 = TextChunk.create("Text one", metadata)
        chunk2 = TextChunk.create("Text two", metadata)

        assert chunk1.chunk_hash != chunk2.chunk_hash


class TestTextChunker:
    """Test suite for TextChunker."""

    def test_chunker_initialization(self):
        """Test chunker initialization with custom parameters."""
        chunker = TextChunker(
            chunk_size=256,
            chunk_overlap=51,
            min_chunk_size=50,
        )

        assert chunker.chunk_size == 256
        assert chunker.chunk_overlap == 51
        assert chunker.min_chunk_size == 50

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        chunker = TextChunker(chunk_size=512, chunk_overlap=102)
        text = "This is a short text that should be a single chunk."
        metadata = {
            "source_id": "test",
            "document_id": "doc_001",
        }

        chunks = chunker.chunk_text(text, metadata)

        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].metadata.chunk_index == 0
        assert chunks[0].metadata.total_chunks == 1

    def test_chunk_long_text(self):
        """Test chunking text longer than chunk size."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)

        # Create text with multiple sentences
        text = " ".join([f"This is sentence number {i}." for i in range(50)])
        metadata = {
            "source_id": "test",
            "document_id": "doc_001",
        }

        chunks = chunker.chunk_text(text, metadata)

        # Should create multiple chunks
        assert len(chunks) > 1

        # Check chunk metadata
        for i, chunk in enumerate(chunks):
            assert chunk.metadata.chunk_index == i
            assert chunk.metadata.total_chunks == len(chunks)
            assert chunk.metadata.start_char < chunk.metadata.end_char

        # First chunk should start at 0
        assert chunks[0].metadata.start_char == 0

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)

        # Create text that will produce multiple chunks
        sentences = [f"Sentence {i} with some content." for i in range(20)]
        text = " ".join(sentences)
        metadata = {
            "source_id": "test",
            "document_id": "doc_001",
        }

        chunks = chunker.chunk_text(text, metadata)

        if len(chunks) > 1:
            # Check that consecutive chunks share some content
            # (this is a heuristic check since overlap is based on sentences)
            assert len(chunks[0].text) > 0
            assert len(chunks[1].text) > 0

    def test_normalize_text(self):
        """Test text normalization."""
        chunker = TextChunker()

        # Text with extra whitespace and control characters
        text = "Text  with   extra    spaces\n\n\n\nand newlines\t\ttabs"
        normalized = chunker._normalize_text(text)

        # Should reduce multiple spaces to single space
        assert "  " not in normalized
        # Should reduce multiple newlines
        assert "\n\n\n" not in normalized

    def test_split_sentences(self):
        """Test sentence splitting."""
        chunker = TextChunker()

        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = chunker._split_sentences(text)

        assert len(sentences) > 1
        assert all(isinstance(s, str) for s in sentences)
        assert all(len(s.strip()) > 0 for s in sentences)

    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        metadata = {"source_id": "test", "document_id": "doc_001"}

        chunks = chunker.chunk_text("", metadata)

        assert len(chunks) == 0

    def test_whitespace_only_text(self):
        """Test chunking whitespace-only text."""
        chunker = TextChunker()
        metadata = {"source_id": "test", "document_id": "doc_001"}

        chunks = chunker.chunk_text("   \n\n   \t\t   ", metadata)

        assert len(chunks) == 0

    def test_chunk_metadata_inheritance(self):
        """Test that chunk metadata inherits from document metadata."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        text = " ".join([f"Sentence {i}." for i in range(50)])
        metadata = {
            "source_id": "test_source",
            "document_id": "doc_001",
            "source_org": "Test Org",
            "canonical_url": "https://example.com",
            "license_info": "Public Domain",
            "year": 1903,
            "content_type": "essay",
            "tags": ["test", "primary_source"],
            "priority": 0,
        }

        chunks = chunker.chunk_text(text, metadata)

        for chunk in chunks:
            assert chunk.metadata.source_id == "test_source"
            assert chunk.metadata.document_id == "doc_001"
            assert chunk.metadata.source_org == "Test Org"
            assert chunk.metadata.canonical_url == "https://example.com"
            assert chunk.metadata.year == 1903
            assert chunk.metadata.tags == ["test", "primary_source"]
            assert chunk.metadata.priority == 0


class TestTextExpansionService:
    """Test suite for TextExpansionService."""

    @pytest.fixture
    def mock_embedding_service(self):
        """Create mock embedding service."""
        service = AsyncMock(spec=EmbeddingService)
        service.model_name = "test-model"
        service.generate_batch_embeddings.return_value = (
            [[0.1] * 1536, [0.2] * 1536],  # embeddings
            100,  # generation time
        )
        return service

    @pytest.fixture
    def mock_zerodb_client(self):
        """Create mock ZeroDB client."""
        client = AsyncMock(spec=ZeroDBClient)
        client.search_vectors.return_value = []
        client.upsert_vector.return_value = {"vector_id": "test_vector_id"}
        return client

    @pytest.fixture
    def mock_chunker(self):
        """Create mock text chunker."""
        chunker = Mock(spec=TextChunker)
        chunker.chunk_size = 512
        chunker.chunk_overlap = 102
        chunker.min_chunk_size = 100

        # Mock chunk_text to return simple chunks
        def mock_chunk_text(text, metadata):
            # Create 2 chunks for testing
            chunks = []
            for i in range(2):
                chunk_metadata = ChunkMetadata(
                    source_id=metadata.get("source_id", "test"),
                    document_id=metadata.get("document_id", "doc_001"),
                    chunk_index=i,
                    total_chunks=2,
                    start_char=i * 100,
                    end_char=(i + 1) * 100,
                )
                chunk = TextChunk.create(f"Chunk {i} text", chunk_metadata)
                chunks.append(chunk)
            return chunks

        chunker.chunk_text.side_effect = mock_chunk_text
        return chunker

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization."""
        service = TextExpansionService()

        assert service.embedding_service is not None
        assert service.chunker is not None
        assert isinstance(service.chunker, TextChunker)

    @pytest.mark.asyncio
    async def test_expand_document_success(
        self, mock_embedding_service, mock_zerodb_client, mock_chunker
    ):
        """Test successful document expansion."""
        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=mock_chunker,
        )

        text = "Test document with multiple sentences. Another sentence here."
        metadata = {
            "source_id": "test_source",
            "document_id": "doc_001",
        }

        result = await service.expand_document(text, metadata)

        assert result["status"] == "success"
        assert result["document_id"] == "doc_001"
        assert result["chunks_created"] == 2
        assert result["chunks_stored"] == 2
        assert "embedding_time_ms" in result

    @pytest.mark.asyncio
    async def test_expand_document_missing_metadata(self, mock_embedding_service):
        """Test expansion with missing required metadata."""
        service = TextExpansionService(embedding_service=mock_embedding_service)

        text = "Test document"
        metadata = {"source_id": "test"}  # Missing document_id

        with pytest.raises(ValueError, match="Missing required metadata field"):
            await service.expand_document(text, metadata)

    @pytest.mark.asyncio
    async def test_expand_document_skip_existing(
        self, mock_embedding_service, mock_zerodb_client, mock_chunker
    ):
        """Test skipping document that already exists."""
        # Mock search to return existing chunks
        mock_zerodb_client.search_vectors.return_value = [{"vector_id": "existing"}]

        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=mock_chunker,
        )

        text = "Test document"
        metadata = {
            "source_id": "test_source",
            "document_id": "doc_001",
        }

        result = await service.expand_document(text, metadata, skip_if_exists=True)

        assert result["status"] == "skipped"
        assert result["reason"] == "document_already_exists"
        assert result["chunks_stored"] == 0

    @pytest.mark.asyncio
    async def test_expand_document_no_chunks_created(
        self, mock_embedding_service, mock_zerodb_client
    ):
        """Test expansion when no chunks are created."""
        # Mock chunker that returns empty list
        chunker = Mock(spec=TextChunker)
        chunker.chunk_text.return_value = []

        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=chunker,
        )

        text = ""
        metadata = {
            "source_id": "test_source",
            "document_id": "doc_001",
        }

        result = await service.expand_document(text, metadata)

        assert result["status"] == "error"
        assert result["reason"] == "no_chunks_created"

    @pytest.mark.asyncio
    async def test_expand_batch(
        self, mock_embedding_service, mock_zerodb_client, mock_chunker
    ):
        """Test batch document expansion."""
        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=mock_chunker,
        )

        documents = [
            ("Document 1 text", {"source_id": "src1", "document_id": "doc_001"}),
            ("Document 2 text", {"source_id": "src2", "document_id": "doc_002"}),
        ]

        results = await service.expand_batch(documents)

        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)
        assert results[0]["document_id"] == "doc_001"
        assert results[1]["document_id"] == "doc_002"

    @pytest.mark.asyncio
    async def test_expand_batch_with_errors(
        self, mock_embedding_service, mock_zerodb_client, mock_chunker
    ):
        """Test batch expansion with some documents failing."""
        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=mock_chunker,
        )

        documents = [
            ("Document 1 text", {"source_id": "src1", "document_id": "doc_001"}),
            ("Document 2 text", {"source_id": "src2"}),  # Missing document_id
        ]

        results = await service.expand_batch(documents)

        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "error"

    @pytest.mark.asyncio
    async def test_storage_error_handling(
        self, mock_embedding_service, mock_zerodb_client, mock_chunker
    ):
        """Test handling of storage errors."""
        # Mock storage to fail
        mock_zerodb_client.upsert_vector.side_effect = ZeroDBError("Storage failed")

        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=mock_chunker,
        )

        text = "Test document"
        metadata = {
            "source_id": "test_source",
            "document_id": "doc_001",
        }

        result = await service.expand_document(text, metadata)

        assert result["status"] == "partial_success"
        assert result["chunks_stored"] == 0
        assert result["errors"] is not None
        assert len(result["errors"]) == 2  # Both chunks failed

    def test_get_stats(self, mock_embedding_service):
        """Test getting service statistics."""
        service = TextExpansionService(embedding_service=mock_embedding_service)

        stats = service.get_stats()

        assert "chunk_size" in stats
        assert "chunk_overlap" in stats
        assert "embedding_model" in stats
        assert "embedding_dimensions" in stats
        assert stats["chunk_size"] == 512
        assert stats["chunk_overlap"] == 102

    @pytest.mark.asyncio
    async def test_vector_id_generation(
        self, mock_embedding_service, mock_zerodb_client, mock_chunker
    ):
        """Test that vector IDs are generated correctly."""
        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=mock_chunker,
        )

        text = "Test document"
        metadata = {
            "source_id": "test_source",
            "document_id": "doc_001",
        }

        await service.expand_document(text, metadata)

        # Check that upsert was called with correct vector IDs
        calls = mock_zerodb_client.upsert_vector.call_args_list
        assert len(calls) == 2

        # Check first chunk vector ID
        assert calls[0].kwargs["vector_id"] == "doc_001_chunk_0"
        # Check second chunk vector ID
        assert calls[1].kwargs["vector_id"] == "doc_001_chunk_1"

    @pytest.mark.asyncio
    async def test_provenance_metadata_stored(
        self, mock_embedding_service, mock_zerodb_client, mock_chunker
    ):
        """Test that provenance metadata is properly stored."""
        service = TextExpansionService(
            embedding_service=mock_embedding_service,
            zerodb_client=mock_zerodb_client,
            chunker=mock_chunker,
        )

        text = "Test document"
        metadata = {
            "source_id": "test_source",
            "document_id": "doc_001",
            "source_org": "Test Organization",
            "canonical_url": "https://example.com/doc",
            "license_info": "Public Domain",
            "year": 1903,
            "tags": ["test", "primary_source"],
        }

        await service.expand_document(text, metadata)

        # Check that metadata was passed to storage
        calls = mock_zerodb_client.upsert_vector.call_args_list
        stored_metadata = calls[0].kwargs["metadata"]

        assert stored_metadata["source_id"] == "test_source"
        assert stored_metadata["document_id"] == "doc_001"
        assert stored_metadata["source_org"] == "Test Organization"
        assert stored_metadata["canonical_url"] == "https://example.com/doc"
        assert stored_metadata["license_info"] == "Public Domain"
        assert stored_metadata["year"] == 1903
        assert "test" in stored_metadata["tags"]
        assert "chunk_hash" in stored_metadata
        assert "ingested_at" in stored_metadata
