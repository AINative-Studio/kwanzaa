"""Refusal models for citation enforcement.

This module defines the data models for handling refusal scenarios when
citations are required but insufficient retrieval prevents accurate responses.
Enforces Imani (Faith) through honest communication of limitations.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RefusalReason(str, Enum):
    """Reasons for refusing to answer a query."""

    INSUFFICIENT_RETRIEVAL = "insufficient_retrieval"
    LOW_SIMILARITY_SCORE = "low_similarity_score"
    NO_PRIMARY_SOURCES = "no_primary_sources"
    BELOW_MIN_SOURCES = "below_min_sources"
    CITATIONS_REQUIRED = "citations_required"
    NO_CITEABLE_CONTENT = "no_citeable_content"


class RefusalContext(BaseModel):
    """Context information about why a refusal occurred.

    This provides transparency about the decision-making process.
    """

    reason: RefusalReason = Field(
        ...,
        description="Primary reason for refusal",
    )
    persona: Optional[str] = Field(
        default=None,
        description="Persona that required citations (educator, researcher, etc.)",
    )
    similarity_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold required",
    )
    actual_similarity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Actual best similarity score achieved",
    )
    min_sources_required: Optional[int] = Field(
        default=None,
        ge=1,
        description="Minimum number of sources required",
    )
    sources_found: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of sources actually found",
    )
    primary_sources_required: Optional[bool] = Field(
        default=None,
        description="Whether primary sources were required",
    )
    primary_sources_found: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of primary sources found",
    )
    query_type: Optional[str] = Field(
        default=None,
        description="Type of query (factual, creative, analytical)",
    )


class RefusalSuggestion(BaseModel):
    """Suggestions for improving the query or corpus."""

    suggestion_type: str = Field(
        ...,
        description="Type of suggestion (refine_query, expand_corpus, adjust_filters)",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Human-readable suggestion description",
    )
    example: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Example query or action",
    )


class RefusalDecision(BaseModel):
    """Decision to refuse answering with full context and suggestions.

    This model encapsulates all information needed to generate a helpful
    refusal response that follows the answer_json contract.
    """

    should_refuse: bool = Field(
        ...,
        description="Whether to refuse answering",
    )
    context: Optional[RefusalContext] = Field(
        default=None,
        description="Context about why refusal occurred",
    )
    refusal_message: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="Clear, helpful refusal message for the user",
    )
    specific_gaps: List[str] = Field(
        default_factory=list,
        description="Specific information gaps that prevented answering",
    )
    suggestions: List[RefusalSuggestion] = Field(
        default_factory=list,
        description="Actionable suggestions for improving the query",
    )

    @property
    def is_refusal(self) -> bool:
        """Check if this represents a refusal decision.

        Returns:
            True if this is a refusal, False otherwise
        """
        return self.should_refuse


class PersonaThresholds(BaseModel):
    """Citation thresholds for different personas.

    Different personas have different requirements for citation quality
    and quantity based on their use cases.
    """

    persona: str = Field(
        ...,
        pattern="^(educator|researcher|creator|builder)$",
        description="Persona identifier",
    )
    citations_required: bool = Field(
        ...,
        description="Whether citations are mandatory for this persona",
    )
    similarity_threshold: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score to accept",
    )
    min_sources: int = Field(
        default=1,
        ge=1,
        description="Minimum number of sources required",
    )
    primary_sources_only: bool = Field(
        default=False,
        description="Whether only primary sources are acceptable",
    )
    strict_mode: bool = Field(
        default=False,
        description="Whether to apply stricter validation rules",
    )

    @classmethod
    def educator_defaults(cls) -> "PersonaThresholds":
        """Get default thresholds for educator persona.

        Returns:
            PersonaThresholds configured for educator
        """
        return cls(
            persona="educator",
            citations_required=True,
            similarity_threshold=0.80,
            min_sources=2,
            primary_sources_only=False,
            strict_mode=True,
        )

    @classmethod
    def researcher_defaults(cls) -> "PersonaThresholds":
        """Get default thresholds for researcher persona.

        Returns:
            PersonaThresholds configured for researcher
        """
        return cls(
            persona="researcher",
            citations_required=True,
            similarity_threshold=0.75,
            min_sources=3,
            primary_sources_only=True,
            strict_mode=True,
        )

    @classmethod
    def creator_defaults(cls) -> "PersonaThresholds":
        """Get default thresholds for creator persona.

        Returns:
            PersonaThresholds configured for creator
        """
        return cls(
            persona="creator",
            citations_required=False,
            similarity_threshold=0.60,
            min_sources=1,
            primary_sources_only=False,
            strict_mode=False,
        )

    @classmethod
    def builder_defaults(cls) -> "PersonaThresholds":
        """Get default thresholds for builder persona.

        Returns:
            PersonaThresholds configured for builder
        """
        return cls(
            persona="builder",
            citations_required=False,
            similarity_threshold=0.65,
            min_sources=1,
            primary_sources_only=False,
            strict_mode=False,
        )

    @classmethod
    def for_persona(cls, persona: str) -> "PersonaThresholds":
        """Get thresholds for a specific persona.

        Args:
            persona: Persona identifier (educator, researcher, creator, builder)

        Returns:
            PersonaThresholds configured for the persona

        Raises:
            ValueError: If persona is not recognized
        """
        persona_map = {
            "educator": cls.educator_defaults,
            "researcher": cls.researcher_defaults,
            "creator": cls.creator_defaults,
            "builder": cls.builder_defaults,
        }

        if persona not in persona_map:
            raise ValueError(
                f"Unknown persona: {persona}. "
                f"Valid options: {list(persona_map.keys())}"
            )

        return persona_map[persona]()
