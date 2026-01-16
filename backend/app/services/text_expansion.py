"""Text expansion service for selective full-text processing.

This service handles the selective expansion of P0 priority sources to full text,
including chunking, embedding generation, and storage in ZeroDB.
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.db.zerodb import ZeroDBClient, ZeroDBError
from app.services.embedding import EmbeddingService


@dataclass
class ChunkMetadata:
    """Metadata for a text chunk."""

    source_id: str
    document_id: str
    chunk_index: int
    total_chunks: int
    start_char: int
    end_char: int
    source_org: Optional[str] = None
    canonical_url: Optional[str] = None
    license_info: Optional[str] = None
    year: Optional[int] = None
    content_type: Optional[str] = None
    tags: List[str] = None
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "source_id": self.source_id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "source_org": self.source_org,
            "canonical_url": self.canonical_url,
            "license_info": self.license_info,
            "year": self.year,
            "content_type": self.content_type,
            "tags": self.tags or [],
            "priority": self.priority,
            "ingested_at": datetime.utcnow().isoformat(),
        }


@dataclass
class TextChunk:
    """A chunk of text with metadata."""

    text: str
    metadata: ChunkMetadata
    chunk_hash: str

    @classmethod
    def create(cls, text: str, metadata: ChunkMetadata) -> "TextChunk":
        """Create a chunk with computed hash."""
        chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return cls(text=text, metadata=metadata, chunk_hash=chunk_hash)


class TextChunker:
    """Smart text chunking with overlap for optimal RAG performance."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 102,
        min_chunk_size: int = 100,
    ) -> None:
        """Initialize text chunker.

        Args:
            chunk_size: Target chunk size in tokens (default: 512)
            chunk_overlap: Overlap size in tokens (default: 102, ~20%)
            min_chunk_size: Minimum chunk size in tokens (default: 100)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

        # Rough token estimation: 1 token ~= 4 characters
        self.char_per_token = 4
        self.chunk_size_chars = chunk_size * self.char_per_token
        self.overlap_chars = chunk_overlap * self.char_per_token
        self.min_chunk_chars = min_chunk_size * self.char_per_token

    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any],
    ) -> List[TextChunk]:
        """Chunk text with smart sentence boundary detection.

        Args:
            text: Full text to chunk
            metadata: Base metadata for all chunks

        Returns:
            List of text chunks with metadata
        """
        if not text or not text.strip():
            return []

        # Clean and normalize text
        text = self._normalize_text(text)

        # Split into sentences for smart chunking
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0
        char_position = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds chunk size, finalize current chunk
            if current_length + sentence_length > self.chunk_size_chars and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk_metadata = ChunkMetadata(
                    source_id=metadata.get("source_id", ""),
                    document_id=metadata.get("document_id", ""),
                    chunk_index=len(chunks),
                    total_chunks=0,  # Will update after all chunks created
                    start_char=char_position - current_length,
                    end_char=char_position,
                    source_org=metadata.get("source_org"),
                    canonical_url=metadata.get("canonical_url"),
                    license_info=metadata.get("license_info"),
                    year=metadata.get("year"),
                    content_type=metadata.get("content_type"),
                    tags=metadata.get("tags", []),
                    priority=metadata.get("priority", 0),
                )
                chunks.append(TextChunk.create(chunk_text, chunk_metadata))

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.overlap_chars)
                current_chunk = [overlap_text] if overlap_text else []
                current_length = len(overlap_text) if overlap_text else 0

            current_chunk.append(sentence)
            current_length += sentence_length + 1  # +1 for space
            char_position += sentence_length + 1

        # Add final chunk if it meets minimum size
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text) >= self.min_chunk_chars:
                chunk_metadata = ChunkMetadata(
                    source_id=metadata.get("source_id", ""),
                    document_id=metadata.get("document_id", ""),
                    chunk_index=len(chunks),
                    total_chunks=0,
                    start_char=char_position - current_length,
                    end_char=char_position,
                    source_org=metadata.get("source_org"),
                    canonical_url=metadata.get("canonical_url"),
                    license_info=metadata.get("license_info"),
                    year=metadata.get("year"),
                    content_type=metadata.get("content_type"),
                    tags=metadata.get("tags", []),
                    priority=metadata.get("priority", 0),
                )
                chunks.append(TextChunk.create(chunk_text, chunk_metadata))

        # Update total_chunks for all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.metadata.total_chunks = total_chunks

        return chunks

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace and control characters.

        Args:
            text: Raw text to normalize

        Returns:
            Normalized text
        """
        # Remove control characters except newlines and tabs
        text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]", "", text)

        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple heuristics.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Split on sentence boundaries (., !, ?) followed by space and capital letter
        # Also preserve paragraph breaks
        sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z])|(?:\n\n+)"

        sentences = re.split(sentence_pattern, text)

        # Filter out empty sentences and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _get_overlap_text(self, sentences: List[str], target_length: int) -> str:
        """Get overlap text from end of current chunk.

        Args:
            sentences: Current chunk sentences
            target_length: Target overlap length in characters

        Returns:
            Overlap text
        """
        if not sentences:
            return ""

        # Take sentences from the end until we reach target length
        overlap_sentences = []
        current_length = 0

        for sentence in reversed(sentences):
            sentence_length = len(sentence)
            if current_length + sentence_length > target_length:
                break
            overlap_sentences.insert(0, sentence)
            current_length += sentence_length + 1

        return " ".join(overlap_sentences)


class TextExpansionService:
    """Service for selective full-text expansion of P0 sources.

    This service handles the complete pipeline from source identification
    through chunking, embedding, and storage in ZeroDB.
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        zerodb_client: Optional[ZeroDBClient] = None,
        chunker: Optional[TextChunker] = None,
    ) -> None:
        """Initialize text expansion service.

        Args:
            embedding_service: Service for generating embeddings
            zerodb_client: Client for ZeroDB operations
            chunker: Text chunker instance
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.zerodb_client = zerodb_client
        self.chunker = chunker or TextChunker(
            chunk_size=512,
            chunk_overlap=102,  # ~20% overlap
            min_chunk_size=100,
        )

    async def expand_document(
        self,
        document_text: str,
        metadata: Dict[str, Any],
        namespace: str = "kwanzaa_primary_sources",
        skip_if_exists: bool = True,
    ) -> Dict[str, Any]:
        """Expand a document to full text with chunking and embedding.

        This is the main entry point for processing a single document.

        Args:
            document_text: Full document text
            metadata: Document metadata including source_id, document_id, etc.
            namespace: ZeroDB namespace for storage
            skip_if_exists: Skip if document already processed

        Returns:
            Dict containing processing results and statistics

        Raises:
            ValueError: If metadata is invalid
            ZeroDBError: If storage fails
        """
        # Validate required metadata
        required_fields = ["source_id", "document_id"]
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Missing required metadata field: {field}")

        # Check if document already exists (idempotency)
        if skip_if_exists and self.zerodb_client:
            existing = await self._check_document_exists(
                metadata["document_id"], namespace
            )
            if existing:
                return {
                    "status": "skipped",
                    "reason": "document_already_exists",
                    "document_id": metadata["document_id"],
                    "chunks_stored": 0,
                }

        # Chunk the text
        chunks = self.chunker.chunk_text(document_text, metadata)

        if not chunks:
            return {
                "status": "error",
                "reason": "no_chunks_created",
                "document_id": metadata["document_id"],
                "chunks_stored": 0,
            }

        # Generate embeddings for all chunks
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings, generation_time = await self.embedding_service.generate_batch_embeddings(
            chunk_texts
        )

        # Store chunks with embeddings in ZeroDB
        stored_count = 0
        errors = []

        if self.zerodb_client:
            for chunk, embedding in zip(chunks, embeddings):
                try:
                    await self._store_chunk(chunk, embedding, namespace)
                    stored_count += 1
                except Exception as e:
                    errors.append(
                        {
                            "chunk_index": chunk.metadata.chunk_index,
                            "error": str(e),
                        }
                    )

        return {
            "status": "success" if not errors else "partial_success",
            "document_id": metadata["document_id"],
            "chunks_created": len(chunks),
            "chunks_stored": stored_count,
            "embedding_time_ms": generation_time,
            "namespace": namespace,
            "errors": errors if errors else None,
        }

    async def expand_batch(
        self,
        documents: List[Tuple[str, Dict[str, Any]]],
        namespace: str = "kwanzaa_primary_sources",
        skip_if_exists: bool = True,
    ) -> List[Dict[str, Any]]:
        """Expand multiple documents in batch.

        Args:
            documents: List of (text, metadata) tuples
            namespace: ZeroDB namespace for storage
            skip_if_exists: Skip documents that already exist

        Returns:
            List of processing results for each document
        """
        results = []

        for document_text, metadata in documents:
            try:
                result = await self.expand_document(
                    document_text, metadata, namespace, skip_if_exists
                )
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "status": "error",
                        "reason": str(e),
                        "document_id": metadata.get("document_id", "unknown"),
                        "chunks_stored": 0,
                    }
                )

        return results

    async def _check_document_exists(
        self, document_id: str, namespace: str
    ) -> bool:
        """Check if document chunks already exist in ZeroDB.

        Args:
            document_id: Document ID to check
            namespace: Namespace to search

        Returns:
            True if document exists, False otherwise
        """
        if not self.zerodb_client:
            return False

        try:
            # Search for any chunk with this document_id
            results = await self.zerodb_client.search_vectors(
                query_vector=[0.0] * settings.EMBEDDING_DIMENSIONS,
                namespace=namespace,
                filter_metadata={"document_id": document_id},
                limit=1,
                threshold=0.0,
            )
            return len(results) > 0
        except ZeroDBError:
            # If search fails, assume document doesn't exist
            return False

    async def _store_chunk(
        self,
        chunk: TextChunk,
        embedding: List[float],
        namespace: str,
    ) -> Dict[str, Any]:
        """Store a chunk with its embedding in ZeroDB.

        Args:
            chunk: Text chunk to store
            embedding: Embedding vector for the chunk
            namespace: ZeroDB namespace

        Returns:
            Storage result

        Raises:
            ZeroDBError: If storage fails
        """
        if not self.zerodb_client:
            raise ZeroDBError("ZeroDB client not initialized")

        # Generate vector ID from document_id and chunk_index
        vector_id = f"{chunk.metadata.document_id}_chunk_{chunk.metadata.chunk_index}"

        # Prepare metadata for storage
        storage_metadata = chunk.metadata.to_dict()
        storage_metadata["chunk_hash"] = chunk.chunk_hash
        storage_metadata["chunk_text_preview"] = chunk.text[:200]  # Store preview

        # Store in ZeroDB
        result = await self.zerodb_client.upsert_vector(
            vector_embedding=embedding,
            document=chunk.text,
            metadata=storage_metadata,
            namespace=namespace,
            vector_id=vector_id,
        )

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics and configuration.

        Returns:
            Dict containing service configuration and stats
        """
        return {
            "chunk_size": self.chunker.chunk_size,
            "chunk_overlap": self.chunker.chunk_overlap,
            "min_chunk_size": self.chunker.min_chunk_size,
            "embedding_model": self.embedding_service.model_name,
            "embedding_dimensions": settings.EMBEDDING_DIMENSIONS,
        }
