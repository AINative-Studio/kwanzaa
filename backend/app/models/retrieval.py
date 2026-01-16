"""Retrieval models for the RAG pipeline.

This module defines the request/response models for the complete RAG pipeline,
including query processing, retrieval, reranking, and context injection.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PersonaThresholds(BaseModel):
    """Persona-specific retrieval thresholds and settings."""

    similarity_threshold: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for retrieval",
    )
    max_results: int = Field(
        ...,
        ge=1,
        le=100,
        description="Maximum number of results to retrieve",
    )
    min_results: int = Field(
        ...,
        ge=1,
        description="Minimum number of results expected",
    )
    rerank: bool = Field(
        ...,
        description="Whether to apply reranking",
    )


class RAGQueryRequest(BaseModel):
    """Request model for RAG pipeline query processing.

    This extends SearchRequest with additional RAG-specific parameters.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query text",
    )
    persona_key: Optional[str] = Field(
        default="educator",
        pattern="^(educator|researcher|creator|builder)$",
        description="Persona for context-specific retrieval",
    )
    namespaces: Optional[List[str]] = Field(
        default=None,
        min_length=1,
        max_length=20,
        description="Specific namespaces to search (overrides persona defaults)",
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata filters for retrieval",
    )
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Number of results to retrieve (overrides persona defaults)",
    )
    similarity_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Similarity threshold (overrides persona defaults)",
    )
    enable_reranking: Optional[bool] = Field(
        default=None,
        description="Enable cross-encoder reranking (overrides persona defaults)",
    )
    rerank_top_n: Optional[int] = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of results to return after reranking",
    )
    include_context_string: bool = Field(
        default=True,
        description="Include formatted context string for LLM injection",
    )
    include_retrieval_summary: bool = Field(
        default=True,
        description="Include detailed retrieval summary",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean query text."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or only whitespace")
        return v


class RetrievalChunk(BaseModel):
    """A single retrieved chunk with full metadata."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    doc_id: str = Field(..., description="Document identifier")
    namespace: str = Field(..., description="Vector namespace")
    content: str = Field(..., description="Chunk text content")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    rank: int = Field(..., ge=1, description="Result rank (1-indexed)")

    # Provenance metadata
    citation_label: str = Field(..., description="Human-readable citation")
    canonical_url: str = Field(..., description="Source URL")
    source_org: str = Field(..., description="Source organization")
    year: int = Field(..., ge=1600, le=2100, description="Document year")
    content_type: str = Field(..., description="Content type")
    license: str = Field(..., description="License information")
    tags: List[str] = Field(default_factory=list, description="Content tags")

    # Optional reranking score
    rerank_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Cross-encoder reranking score (if applied)",
    )
    final_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Final combined score after reranking",
    )


class RetrievalStatistics(BaseModel):
    """Statistics about the retrieval process."""

    total_retrieved: int = Field(..., ge=0, description="Total chunks retrieved")
    total_reranked: int = Field(default=0, ge=0, description="Total chunks reranked")
    total_returned: int = Field(..., ge=0, description="Total chunks returned")
    top_score: float = Field(..., ge=0.0, le=1.0, description="Highest similarity score")
    average_score: float = Field(..., ge=0.0, le=1.0, description="Average similarity score")
    namespaces_searched: List[str] = Field(..., description="Namespaces searched")
    filters_applied: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters applied to search",
    )
    embedding_time_ms: int = Field(..., ge=0, description="Query embedding time")
    search_time_ms: int = Field(..., ge=0, description="Vector search time")
    rerank_time_ms: int = Field(default=0, ge=0, description="Reranking time")
    total_time_ms: int = Field(..., ge=0, description="Total pipeline time")


class ContextString(BaseModel):
    """Formatted context string for LLM prompt injection."""

    formatted_context: str = Field(
        ...,
        description="Complete formatted context string with all chunks and metadata",
    )
    num_chunks: int = Field(..., ge=0, description="Number of chunks included")
    total_tokens: Optional[int] = Field(
        default=None,
        ge=0,
        description="Approximate token count (if calculated)",
    )
    max_chunk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Highest score among included chunks",
    )


class RAGPipelineResponse(BaseModel):
    """Complete response from the RAG pipeline.

    This includes retrieved chunks, reranking results, formatted context,
    and detailed retrieval statistics for transparency.
    """

    status: str = Field(default="success", description="Response status")
    query: str = Field(..., description="Original query text")
    persona: str = Field(..., description="Persona used")

    # Retrieved and ranked chunks
    chunks: List[RetrievalChunk] = Field(
        ...,
        description="Retrieved chunks ordered by final rank",
    )

    # Context injection
    context_string: Optional[ContextString] = Field(
        default=None,
        description="Formatted context for LLM injection (if requested)",
    )

    # Retrieval transparency
    statistics: RetrievalStatistics = Field(
        ...,
        description="Retrieval process statistics",
    )

    # Metadata
    persona_thresholds: PersonaThresholds = Field(
        ...,
        description="Thresholds applied for this persona",
    )
    reranking_enabled: bool = Field(
        ...,
        description="Whether reranking was applied",
    )
    embedding_model: str = Field(..., description="Embedding model used")
    rerank_model: Optional[str] = Field(
        default=None,
        description="Reranking model used (if applicable)",
    )

    @field_validator("chunks")
    @classmethod
    def validate_chunks_order(cls, v: List[RetrievalChunk]) -> List[RetrievalChunk]:
        """Ensure chunks are ordered by rank."""
        if len(v) > 1:
            for i in range(len(v) - 1):
                if v[i].rank >= v[i + 1].rank:
                    raise ValueError("Chunks must be ordered by rank (ascending)")
        return v


class RerankRequest(BaseModel):
    """Request for cross-encoder reranking."""

    query: str = Field(..., min_length=1, description="Query text")
    chunks: List[RetrievalChunk] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Chunks to rerank",
    )
    top_n: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of top results to return",
    )


class RerankResult(BaseModel):
    """Result from reranking a single chunk."""

    chunk_id: str = Field(..., description="Chunk identifier")
    original_rank: int = Field(..., ge=1, description="Original rank")
    original_score: float = Field(..., ge=0.0, le=1.0, description="Original score")
    rerank_score: float = Field(..., ge=0.0, le=1.0, description="Reranking score")
    final_score: float = Field(..., ge=0.0, le=1.0, description="Combined final score")
    new_rank: int = Field(..., ge=1, description="New rank after reranking")


class RerankResponse(BaseModel):
    """Response from reranking service."""

    status: str = Field(default="success", description="Response status")
    results: List[RerankResult] = Field(..., description="Reranked results")
    rerank_model: str = Field(..., description="Reranking model used")
    rerank_time_ms: int = Field(..., ge=0, description="Reranking time")
    total_processed: int = Field(..., ge=0, description="Total chunks processed")
    total_returned: int = Field(..., ge=0, description="Total chunks returned")
