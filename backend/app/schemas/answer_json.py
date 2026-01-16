"""Pydantic models for the answer_json contract.

This module defines the complete schema for Kwanzaa's AI response format,
enforcing Safety & Integrity (Nguzo: Imani) through strict validation.

The answer_json contract ensures:
- No raw text blobs are rendered in the UI
- All responses include proper citations and provenance
- Retrieval transparency through "Show Your Work" principle
- Explicit handling of unknowns and missing context
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Persona(str, Enum):
    """Agent persona types."""

    EDUCATOR = "educator"
    RESEARCHER = "researcher"
    CREATOR = "creator"
    BUILDER = "builder"


class ModelMode(str, Enum):
    """Model operational modes."""

    BASE_ADAPTER_RAG = "base_adapter_rag"
    BASE_RAG = "base_rag"
    BASE_ONLY = "base_only"
    CREATIVE = "creative"


class Tone(str, Enum):
    """Response tone."""

    NEUTRAL = "neutral"
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"
    ACADEMIC = "academic"


class Completeness(str, Enum):
    """Answer completeness level."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    INCOMPLETE = "incomplete"


class RetrievalConfidence(str, Enum):
    """Retrieval confidence levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FallbackBehavior(str, Enum):
    """Fallback behavior when retrieval fails."""

    NOT_NEEDED = "not_needed"
    GRACEFUL_DECLINE = "graceful_decline"
    GENERAL_KNOWLEDGE = "general_knowledge"


class TogglesSection(BaseModel):
    """Configuration toggles for response behavior."""

    require_citations: bool = Field(
        ...,
        description="Whether citations are required for this response",
    )
    primary_sources_only: bool = Field(
        ...,
        description="Whether to use only primary sources",
    )
    creative_mode: bool = Field(
        ...,
        description="Whether creative/generative mode is enabled",
    )


class AnswerSection(BaseModel):
    """Main answer content with metadata."""

    text: str = Field(
        ...,
        min_length=1,
        description="The main answer text content",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence in the answer (0.0 to 1.0)",
    )
    tone: Tone = Field(
        ...,
        description="Tone of the response",
    )
    completeness: Completeness = Field(
        ...,
        description="Completeness level of the answer",
    )

    @field_validator("text")
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        """Ensure answer text is not just whitespace."""
        if not v.strip():
            raise ValueError("Answer text cannot be empty or only whitespace")
        return v


class SourceReference(BaseModel):
    """Citation reference with full provenance metadata."""

    citation_label: str = Field(
        ...,
        min_length=1,
        description="Human-readable citation label",
    )
    canonical_url: str = Field(
        ...,
        min_length=1,
        description="Canonical URL to the source document",
    )
    source_org: str = Field(
        ...,
        min_length=1,
        description="Source organization name",
    )
    year: int = Field(
        ...,
        ge=1600,
        le=2100,
        description="Year of the source document",
    )
    content_type: str = Field(
        ...,
        min_length=1,
        description="Content type (e.g., speech, letter, proclamation)",
    )
    license: str = Field(
        ...,
        min_length=1,
        description="License information",
    )
    namespace: str = Field(
        ...,
        min_length=1,
        description="Vector namespace identifier",
    )
    doc_id: str = Field(
        ...,
        min_length=1,
        description="Document identifier",
    )
    chunk_id: str = Field(
        ...,
        min_length=1,
        description="Chunk identifier within the document",
    )

    @field_validator("canonical_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("canonical_url must start with http:// or https://")
        return v


class RetrievalResult(BaseModel):
    """A single retrieval result from the vector search."""

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
    snippet: str = Field(
        ...,
        min_length=1,
        description="Content snippet from the retrieved chunk",
    )
    citation_label: str = Field(
        ...,
        min_length=1,
        description="Human-readable citation label",
    )
    canonical_url: str = Field(
        ...,
        min_length=1,
        description="Canonical URL to the source",
    )
    doc_id: str = Field(
        ...,
        min_length=1,
        description="Document identifier",
    )
    chunk_id: str = Field(
        ...,
        min_length=1,
        description="Chunk identifier",
    )
    namespace: str = Field(
        ...,
        min_length=1,
        description="Vector namespace",
    )


class RetrievalSummarySection(BaseModel):
    """Summary of the retrieval process for transparency (Show Your Work)."""

    query: str = Field(
        ...,
        min_length=1,
        description="The search query used for retrieval",
    )
    top_k: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of results retrieved",
    )
    namespaces: List[str] = Field(
        ...,
        min_length=1,
        description="Namespaces searched",
    )
    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filters applied to the search",
    )
    results: List[RetrievalResult] = Field(
        ...,
        min_length=1,
        description="Top retrieval results",
    )

    @field_validator("results")
    @classmethod
    def validate_results_order(cls, v: List[RetrievalResult]) -> List[RetrievalResult]:
        """Ensure results are ordered by rank."""
        if len(v) > 1:
            for i in range(len(v) - 1):
                if v[i].rank >= v[i + 1].rank:
                    raise ValueError("Results must be ordered by rank (ascending)")
        return v


class UnknownsSection(BaseModel):
    """Explicit declaration of what is unknown or missing.

    This enforces intellectual honesty and prevents hallucination.
    """

    unsupported_claims: List[str] = Field(
        default_factory=list,
        description="Claims that lack source support",
    )
    missing_context: List[str] = Field(
        default_factory=list,
        description="Context that is missing from the corpus",
    )
    clarifying_questions: List[str] = Field(
        default_factory=list,
        description="Questions that could help clarify the answer",
    )


class IntegritySection(BaseModel):
    """Integrity metadata for trust and transparency."""

    citation_required: bool = Field(
        ...,
        description="Whether citations were required for this query",
    )
    citations_provided: bool = Field(
        ...,
        description="Whether citations were actually provided",
    )
    retrieval_confidence: RetrievalConfidence = Field(
        ...,
        description="Confidence in the retrieval results",
    )
    fallback_behavior: FallbackBehavior = Field(
        ...,
        description="Fallback behavior used (if any)",
    )

    @model_validator(mode="after")
    def validate_citation_consistency(self) -> "IntegritySection":
        """Ensure citation_required and citations_provided are consistent."""
        if self.citation_required and not self.citations_provided:
            raise ValueError(
                "When citation_required=True, citations_provided must also be True"
            )
        return self


class ProvenanceSection(BaseModel):
    """Provenance tracking for audit and debugging."""

    generated_at: datetime = Field(
        ...,
        description="ISO 8601 timestamp of response generation",
    )
    retrieval_run_id: str = Field(
        ...,
        min_length=1,
        description="UUID for the retrieval execution",
    )
    assistant_message_id: str = Field(
        ...,
        min_length=1,
        description="UUID for the assistant message",
    )


class AnswerJson(BaseModel):
    """Complete answer_json contract model.

    This is the top-level schema that all AI responses must conform to.
    It enforces the principle that UI should never render raw text blobs.
    """

    version: str = Field(
        ...,
        pattern=r"^kwanzaa\.answer\.v\d+$",
        description="Schema version (e.g., kwanzaa.answer.v1)",
    )
    persona: Persona = Field(
        ...,
        description="Agent persona",
    )
    model_mode: ModelMode = Field(
        ...,
        description="Model operational mode",
    )
    toggles: TogglesSection = Field(
        ...,
        description="Configuration toggles",
    )
    answer: AnswerSection = Field(
        ...,
        description="Main answer content",
    )
    sources: List[SourceReference] = Field(
        ...,
        description="Source citations with provenance",
    )
    retrieval_summary: RetrievalSummarySection = Field(
        ...,
        description="Retrieval process summary for transparency",
    )
    unknowns: UnknownsSection = Field(
        ...,
        description="Explicit unknowns and missing context",
    )
    integrity: IntegritySection = Field(
        ...,
        description="Integrity metadata",
    )
    provenance: ProvenanceSection = Field(
        ...,
        description="Provenance tracking",
    )

    @model_validator(mode="after")
    def validate_sources_consistency(self) -> "AnswerJson":
        """Ensure sources are provided when citations are required."""
        if self.integrity.citations_provided and len(self.sources) == 0:
            raise ValueError("citations_provided=True requires at least one source")
        if self.toggles.require_citations and len(self.sources) == 0:
            raise ValueError("require_citations=True requires at least one source")
        return self

    @model_validator(mode="after")
    def validate_retrieval_sources_alignment(self) -> "AnswerJson":
        """Ensure sources align with retrieval results."""
        source_doc_ids = {source.doc_id for source in self.sources}
        retrieval_doc_ids = {result.doc_id for result in self.retrieval_summary.results}

        # All sources should appear in retrieval results
        if not source_doc_ids.issubset(retrieval_doc_ids):
            missing = source_doc_ids - retrieval_doc_ids
            raise ValueError(
                f"Sources reference doc_ids not found in retrieval results: {missing}"
            )

        return self

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "version": "kwanzaa.answer.v1",
                "persona": "educator",
                "model_mode": "base_adapter_rag",
                "toggles": {
                    "require_citations": True,
                    "primary_sources_only": False,
                    "creative_mode": False,
                },
                "answer": {
                    "text": "The Civil Rights Act of 1964 was a landmark federal law.",
                    "confidence": 0.92,
                    "tone": "neutral",
                    "completeness": "partial",
                },
                "sources": [
                    {
                        "citation_label": "National Archives (1964) — Civil Rights Act",
                        "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
                        "source_org": "National Archives",
                        "year": 1964,
                        "content_type": "proclamation",
                        "license": "Public Domain",
                        "namespace": "kwanzaa_primary_sources",
                        "doc_id": "nara_cra_1964",
                        "chunk_id": "nara_cra_1964::chunk::3",
                    }
                ],
                "retrieval_summary": {
                    "query": "What did the Civil Rights Act of 1964 prohibit?",
                    "top_k": 5,
                    "namespaces": ["kwanzaa_primary_sources"],
                    "filters": {"content_type": ["proclamation"]},
                    "results": [
                        {
                            "rank": 1,
                            "score": 0.93,
                            "snippet": "An Act to enforce the constitutional right to vote...",
                            "citation_label": "National Archives (1964) — Civil Rights Act",
                            "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
                            "doc_id": "nara_cra_1964",
                            "chunk_id": "nara_cra_1964::chunk::3",
                            "namespace": "kwanzaa_primary_sources",
                        }
                    ],
                },
                "unknowns": {
                    "unsupported_claims": [],
                    "missing_context": [],
                    "clarifying_questions": [],
                },
                "integrity": {
                    "citation_required": True,
                    "citations_provided": True,
                    "retrieval_confidence": "high",
                    "fallback_behavior": "not_needed",
                },
                "provenance": {
                    "generated_at": "2026-02-03T18:42:11Z",
                    "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                    "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
                },
            }
        }
