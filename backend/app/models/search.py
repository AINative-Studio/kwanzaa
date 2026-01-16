"""Search request and response models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ProvenanceFilters(BaseModel):
    """Provenance-based metadata filters for search.

    This model enforces Imani (Faith) through transparent provenance tracking.
    """

    year: Optional[int] = Field(
        default=None,
        ge=1600,
        le=2100,
        description="Exact year match",
    )
    year_gte: Optional[int] = Field(
        default=None,
        ge=1600,
        le=2100,
        description="Minimum year (inclusive)",
    )
    year_lte: Optional[int] = Field(
        default=None,
        ge=1600,
        le=2100,
        description="Maximum year (inclusive)",
    )
    source_org: Optional[List[str]] = Field(
        default=None,
        description="Filter by source organizations",
        max_length=50,
    )
    content_type: Optional[List[str]] = Field(
        default=None,
        description="Filter by content types (e.g., speech, letter, proclamation)",
        max_length=50,
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Filter by tags",
        max_length=100,
    )

    @field_validator("year_gte", "year_lte")
    @classmethod
    def validate_year_range(cls, v: Optional[int], info: Any) -> Optional[int]:
        """Validate year range consistency."""
        if v is None:
            return v

        # If both year_gte and year_lte are present, ensure year_gte <= year_lte
        if info.field_name == "year_lte":
            year_gte = info.data.get("year_gte")
            if year_gte is not None and v < year_gte:
                raise ValueError("year_lte must be greater than or equal to year_gte")

        return v

    @field_validator("source_org", "content_type", "tags")
    @classmethod
    def validate_non_empty_lists(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure lists are not empty if provided."""
        if v is not None and len(v) == 0:
            raise ValueError("List must contain at least one element if provided")
        return v

    def to_metadata_filter(self) -> Dict[str, Any]:
        """Convert to ZeroDB metadata filter format.

        Returns:
            Dict suitable for ZeroDB vector search metadata filtering
        """
        filter_dict: Dict[str, Any] = {}

        # Handle year filters
        if self.year is not None:
            filter_dict["year"] = self.year
        else:
            if self.year_gte is not None:
                filter_dict["year_gte"] = self.year_gte
            if self.year_lte is not None:
                filter_dict["year_lte"] = self.year_lte

        # Handle array filters
        if self.source_org:
            filter_dict["source_org"] = {"$in": self.source_org}
        if self.content_type:
            filter_dict["content_type"] = {"$in": self.content_type}
        if self.tags:
            filter_dict["tags"] = {"$contains_any": self.tags}

        return filter_dict


class SearchRequest(BaseModel):
    """Request model for semantic search.

    This model supports persona-driven queries (Kujichagulia - Self-Determination)
    and collection-based search (Umoja - Unity).
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Search query text (natural language)",
    )
    namespace: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Vector namespace to search within",
    )
    filters: Optional[ProvenanceFilters] = Field(
        default=None,
        description="Provenance-based metadata filters",
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    )
    threshold: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0.0 to 1.0)",
    )
    include_embeddings: Optional[bool] = Field(
        default=False,
        description="Include vector embeddings in response",
    )
    persona_key: Optional[str] = Field(
        default=None,
        pattern="^(educator|researcher|creator|builder)$",
        description="Apply persona-specific defaults and thresholds",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean query text."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or only whitespace")
        return v


class ChunkMetadata(BaseModel):
    """Metadata for a document chunk.

    This enforces provenance tracking (Imani) and enables transparent citation.
    """

    citation_label: str = Field(
        ...,
        description="Human-readable citation label",
    )
    canonical_url: str = Field(
        ...,
        description="Canonical URL to source document",
    )
    source_org: str = Field(
        ...,
        description="Source organization (e.g., National Archives)",
    )
    year: int = Field(
        ...,
        ge=1600,
        le=2100,
        description="Year of document/content",
    )
    content_type: str = Field(
        ...,
        description="Content type (e.g., speech, letter, proclamation)",
    )
    license: str = Field(
        ...,
        description="License information",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Content tags",
    )

    # Allow additional metadata fields
    class Config:
        """Pydantic configuration."""

        extra = "allow"


class SearchResult(BaseModel):
    """A single search result with provenance metadata."""

    rank: int = Field(
        ...,
        ge=1,
        description="Result rank (1-indexed)",
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score",
    )
    chunk_id: str = Field(
        ...,
        description="Unique chunk identifier",
    )
    doc_id: str = Field(
        ...,
        description="Document identifier",
    )
    namespace: str = Field(
        ...,
        description="Vector namespace",
    )
    content: str = Field(
        ...,
        description="Chunk content/snippet",
    )
    metadata: ChunkMetadata = Field(
        ...,
        description="Provenance metadata",
    )
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Vector embedding (if requested)",
    )


class SearchQuery(BaseModel):
    """Query information included in search response."""

    text: str = Field(
        ...,
        description="Original query text",
    )
    namespace: str = Field(
        ...,
        description="Namespace searched",
    )
    filters_applied: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters that were applied",
    )
    limit: int = Field(
        ...,
        description="Result limit",
    )
    threshold: float = Field(
        ...,
        description="Similarity threshold used",
    )


class SearchMetadata(BaseModel):
    """Metadata about search execution."""

    execution_time_ms: int = Field(
        ...,
        ge=0,
        description="Total execution time in milliseconds",
    )
    embedding_model: str = Field(
        ...,
        description="Embedding model used",
    )
    query_embedding_time_ms: int = Field(
        ...,
        ge=0,
        description="Time to generate query embedding",
    )
    search_time_ms: int = Field(
        ...,
        ge=0,
        description="Time for vector search",
    )


class SearchResponse(BaseModel):
    """Response model for semantic search.

    This structure supports the 'Show Your Work' principle (Ujima - Collective Work)
    by providing transparent retrieval information.
    """

    status: str = Field(
        default="success",
        description="Response status",
    )
    query: SearchQuery = Field(
        ...,
        description="Query information",
    )
    results: List[SearchResult] = Field(
        ...,
        description="Search results ordered by rank",
    )
    total_results: int = Field(
        ...,
        ge=0,
        description="Total number of results found",
    )
    search_metadata: SearchMetadata = Field(
        ...,
        description="Search execution metadata",
    )
