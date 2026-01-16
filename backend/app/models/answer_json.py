"""Kwanzaa Answer JSON Contract - Pydantic Models.

Version: 1.0.0

Strict Pydantic models for AI responses with citations, provenance tracking,
and transparent uncertainty. Enforces Imani (Faith) through verifiable sources
and honest communication of limitations.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Persona(str, Enum):
    """Persona mode that generated the response."""

    EDUCATOR = "educator"
    RESEARCHER = "researcher"
    CREATOR = "creator"
    BUILDER = "builder"


class ModelMode(str, Enum):
    """Model mode used for generation."""

    BASE_ADAPTER_RAG = "base_adapter_rag"
    BASE_ONLY = "base_only"
    ADAPTER_ONLY = "adapter_only"
    CREATIVE = "creative"


class Tone(str, Enum):
    """Tone of the response."""

    NEUTRAL = "neutral"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"
    CREATIVE = "creative"


class Completeness(str, Enum):
    """Assessment of answer completeness based on available data."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    INSUFFICIENT_DATA = "insufficient_data"


class RetrievalConfidence(str, Enum):
    """Overall confidence in retrieval results."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class FallbackBehavior(str, Enum):
    """Fallback behavior used when retrieval was insufficient."""

    NOT_NEEDED = "not_needed"
    CREATIVE_GENERATION = "creative_generation"
    REFUSAL = "refusal"
    CLARIFICATION_REQUESTED = "clarification_requested"


class Toggles(BaseModel):
    """User-controlled behavior toggles enforcing Kujichagulia (Self-Determination)."""

    require_citations: bool = Field(
        ...,
        description="Whether citations are mandatory for this response",
    )
    primary_sources_only: bool = Field(
        ...,
        description="Whether only primary sources should be used",
    )
    creative_mode: bool = Field(
        ...,
        description="Whether creative generation is enabled",
    )


class Answer(BaseModel):
    """The main AI response with metadata."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The main response text",
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Model confidence score for this answer",
    )
    tone: Optional[Tone] = Field(
        default=None,
        description="Tone of the response",
    )
    completeness: Optional[Completeness] = Field(
        default=None,
        description="Assessment of answer completeness based on available data",
    )


class Source(BaseModel):
    """Source citation with full provenance metadata enforcing Imani (Faith)."""

    citation_label: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Human-readable citation label",
    )
    canonical_url: str = Field(
        ...,
        description="Canonical URL to source document",
    )
    source_org: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Source organization name",
    )
    year: int = Field(
        ...,
        ge=1600,
        le=2100,
        description="Year of document or content",
    )
    content_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Content type classification",
    )
    license: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="License information for the source",
    )
    namespace: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Vector namespace where this source resides",
    )
    doc_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique document identifier",
    )
    chunk_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Unique chunk identifier within the document",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        max_length=50,
        description="Content tags for categorization",
    )
    relevance_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relevance score for this source to the query",
    )

    # Allow additional metadata fields
    model_config = ConfigDict(extra="allow")


class RetrievalFilters(BaseModel):
    """Filters applied to the retrieval query."""

    content_type: Optional[List[str]] = Field(
        default=None,
        description="Content type filters",
    )
    year: Optional[int] = Field(
        default=None,
        description="Exact year filter",
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
        description="Source organization filters",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Tag filters",
    )

    @field_validator("year_lte")
    @classmethod
    def validate_year_range(cls, v: Optional[int], info: Any) -> Optional[int]:
        """Validate year range consistency."""
        if v is None:
            return v

        year_gte = info.data.get("year_gte")
        if year_gte is not None and v < year_gte:
            raise ValueError("year_lte must be greater than or equal to year_gte")

        return v

    # Allow additional filter fields
    model_config = ConfigDict(extra="allow")


class RetrievalResult(BaseModel):
    """Individual retrieval result with metadata."""

    rank: int = Field(
        ...,
        ge=1,
        description="Result rank (1-indexed)",
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity or relevance score",
    )
    snippet: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Text snippet from the retrieved chunk",
    )
    citation_label: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Human-readable citation label",
    )
    canonical_url: str = Field(
        ...,
        description="Canonical URL to source document",
    )
    doc_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Document identifier",
    )
    chunk_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Chunk identifier",
    )
    namespace: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Vector namespace",
    )


class RetrievalSummary(BaseModel):
    """Summary of the retrieval process enforcing Ujima (Collective Work).

    Provides transparent 'Show Your Work' information.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The original query text that was processed",
    )
    top_k: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of results requested from retrieval",
    )
    namespaces: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Vector namespaces searched",
    )
    filters: Optional[RetrievalFilters] = Field(
        default=None,
        description="Filters applied to the retrieval query",
    )
    results: List[RetrievalResult] = Field(
        ...,
        max_length=100,
        description="Top retrieval results with metadata",
    )
    execution_time_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total retrieval execution time in milliseconds",
    )
    embedding_model: Optional[str] = Field(
        default=None,
        description="Embedding model used for retrieval",
    )


class Unknowns(BaseModel):
    """Transparent communication of limitations and gaps.

    Enforces Imani (Faith) through honest acknowledgment.
    """

    unsupported_claims: List[str] = Field(
        ...,
        description="Claims that cannot be supported by the corpus",
    )
    missing_context: List[str] = Field(
        ...,
        description="Context or information gaps in the corpus",
    )
    clarifying_questions: List[str] = Field(
        ...,
        description="Questions that would help provide a better answer",
    )
    out_of_scope: Optional[List[str]] = Field(
        default=None,
        description="Topics or queries that are outside the corpus scope",
    )


class Integrity(BaseModel):
    """Integrity metadata for trust and safety."""

    citation_required: Optional[bool] = Field(
        default=None,
        description="Whether citations were required for this response",
    )
    citations_provided: Optional[bool] = Field(
        default=None,
        description="Whether citations were actually provided",
    )
    retrieval_confidence: Optional[RetrievalConfidence] = Field(
        default=None,
        description="Overall confidence in retrieval results",
    )
    fallback_behavior: Optional[FallbackBehavior] = Field(
        default=None,
        description="Fallback behavior used when retrieval was insufficient",
    )
    safety_flags: Optional[List[str]] = Field(
        default=None,
        description="Safety or policy flags triggered",
    )


class Provenance(BaseModel):
    """Generation provenance metadata.

    Enforces Ujamaa (Cooperative Economics) through shared credit.
    """

    generated_at: datetime = Field(
        ...,
        description="ISO 8601 timestamp of generation",
    )
    retrieval_run_id: Optional[UUID] = Field(
        default=None,
        description="Unique identifier for the retrieval run",
    )
    assistant_message_id: Optional[UUID] = Field(
        default=None,
        description="Unique identifier for the assistant message",
    )
    session_id: Optional[UUID] = Field(
        default=None,
        description="Session identifier for request correlation",
    )
    model_version: Optional[str] = Field(
        default=None,
        description="Model version or identifier used for generation",
    )
    adapter_version: Optional[str] = Field(
        default=None,
        description="Adapter version if used",
    )


class AnswerJsonContract(BaseModel):
    """Complete Kwanzaa Answer JSON Contract.

    This structure enforces the Seven Principles (Nguzo Saba):
    - Umoja (Unity): Unified schema across all personas
    - Kujichagulia (Self-Determination): User-controlled toggles
    - Ujima (Collective Work): Transparent retrieval and 'Show Your Work'
    - Ujamaa (Cooperative Economics): Shared credit through provenance
    - Nia (Purpose): Education and research first
    - Kuumba (Creativity): Creator tools grounded in retrieved context
    - Imani (Faith): Trust through citations and honest communication
    """

    version: str = Field(
        ...,
        pattern=r"^kwanzaa\.answer\.v[0-9]+$",
        description="Contract version identifier",
    )
    persona: Optional[Persona] = Field(
        default=None,
        description="Persona mode that generated this response",
    )
    model_mode: Optional[ModelMode] = Field(
        default=None,
        description="Model mode used for generation",
    )
    toggles: Optional[Toggles] = Field(
        default=None,
        description="User-controlled behavior toggles",
    )
    answer: Answer = Field(
        ...,
        description="The main AI response with metadata",
    )
    sources: List[Source] = Field(
        ...,
        max_length=100,
        description="Array of source citations with full provenance metadata",
    )
    retrieval_summary: RetrievalSummary = Field(
        ...,
        description="Summary of the retrieval process",
    )
    unknowns: Unknowns = Field(
        ...,
        description="Transparent communication of limitations and gaps",
    )
    integrity: Optional[Integrity] = Field(
        default=None,
        description="Integrity metadata for trust and safety",
    )
    provenance: Optional[Provenance] = Field(
        default=None,
        description="Generation provenance metadata",
    )

    @model_validator(mode="after")
    def validate_citation_integrity(self) -> "AnswerJsonContract":
        """Validate citation integrity requirements."""
        if self.integrity:
            # If citations are required, verify they are provided
            if self.integrity.citation_required and not self.integrity.citations_provided:
                if len(self.sources) == 0:
                    raise ValueError(
                        "Citations are required but none were provided. "
                        "This violates Imani (Faith) principle."
                    )

        return self

    model_config = ConfigDict(
        # Prevent additional properties not defined in schema
        extra="forbid",
        # Use enum values in JSON serialization
        use_enum_values=False,
    )


def create_answer_json_contract(
    answer: str,
    query: str,
    version: str = "kwanzaa.answer.v1",
    persona: Optional[Persona] = None,
    model_mode: Optional[ModelMode] = None,
    sources: Optional[List[Source]] = None,
    retrieval_results: Optional[List[RetrievalResult]] = None,
    unknowns: Optional[Unknowns] = None,
) -> AnswerJsonContract:
    """Helper function to create a minimal valid AnswerJsonContract.

    Args:
        answer: The main response text
        query: The original query text
        version: Contract version (default: "kwanzaa.answer.v1")
        persona: Persona mode used
        model_mode: Model mode used
        sources: List of source citations
        retrieval_results: List of retrieval results
        unknowns: Unknowns object with gaps and clarifications

    Returns:
        A valid AnswerJsonContract instance
    """
    return AnswerJsonContract(
        version=version,
        persona=persona,
        model_mode=model_mode,
        answer=Answer(text=answer),
        sources=sources or [],
        retrieval_summary=RetrievalSummary(
            query=query,
            top_k=10,
            namespaces=["kwanzaa_primary_sources"],
            results=retrieval_results or [],
        ),
        unknowns=unknowns
        or Unknowns(
            unsupported_claims=[],
            missing_context=[],
            clarifying_questions=[],
        ),
        provenance=Provenance(
            generated_at=datetime.now(timezone.utc),
        ),
    )
