"""Query template models for persona-specific retrieval.

This module defines the data models for query templates that tailor
retrieval strategies to different user personas (Builder, Educator,
Creator, Researcher).

Aligned with Nguzo Saba principles:
- Kujichagulia (Self-Determination): User-driven persona selection
- Ujima (Collective Work): Shared template definitions
- Nia (Purpose): Goal-oriented query enhancement
- Kuumba (Creativity): Flexible template composition
- Imani (Faith): Transparent, trustworthy retrieval
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PersonaType(str, Enum):
    """Supported user persona types."""

    BUILDER = "builder"
    EDUCATOR = "educator"
    CREATOR = "creator"
    RESEARCHER = "researcher"


class QueryExpansionStrategy(str, Enum):
    """Query expansion strategies for different persona needs."""

    TECHNICAL = "technical"  # Extract API patterns, code terms
    HISTORICAL = "historical"  # Extract dates, figures, context
    THEMATIC = "thematic"  # Extract themes, emotions, narratives
    RESEARCH = "research"  # Extract questions, methodology terms
    NONE = "none"  # No expansion


class MetadataFilterTemplate(BaseModel):
    """Template for metadata filters to apply based on persona."""

    content_types: Optional[List[str]] = Field(
        default=None,
        description="Content types to filter for (e.g., 'speech', 'code_example')",
    )
    year_range: Optional[Dict[str, int]] = Field(
        default=None,
        description="Year range filter with 'min' and 'max' keys",
    )
    source_org_priority: Optional[List[str]] = Field(
        default=None,
        description="Prioritized source organizations",
    )
    tags_required: Optional[List[str]] = Field(
        default=None,
        description="Required tags for filtering",
    )
    tags_preferred: Optional[List[str]] = Field(
        default=None,
        description="Preferred tags for boosting",
    )

    @field_validator("year_range")
    @classmethod
    def validate_year_range(cls, v: Optional[Dict[str, int]]) -> Optional[Dict[str, int]]:
        """Validate year range has proper keys and values."""
        if v is None:
            return v

        if "min" in v and "max" in v:
            if v["min"] > v["max"]:
                raise ValueError("year_range 'min' must be <= 'max'")

        return v


class RetrievalParameterOverrides(BaseModel):
    """Retrieval parameter overrides for persona-specific behavior."""

    similarity_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold (0.0-1.0)",
    )
    result_limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of results",
    )
    min_results: Optional[int] = Field(
        default=None,
        ge=1,
        description="Minimum number of results to consider successful",
    )
    rerank: Optional[bool] = Field(
        default=None,
        description="Whether to apply reranking",
    )
    diversity_factor: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Result diversity factor (0.0=relevance only, 1.0=max diversity)",
    )


class ContextFormattingPreferences(BaseModel):
    """Preferences for how retrieved context should be formatted."""

    include_metadata: bool = Field(
        default=True,
        description="Include full metadata in context",
    )
    include_citations: bool = Field(
        default=True,
        description="Include inline citations",
    )
    citation_style: str = Field(
        default="chicago",
        pattern="^(chicago|apa|mla)$",
        description="Citation format style",
    )
    snippet_length: int = Field(
        default=512,
        ge=100,
        le=2048,
        description="Maximum snippet length in characters",
    )
    highlight_query_terms: bool = Field(
        default=False,
        description="Highlight matching query terms in snippets",
    )
    show_provenance: bool = Field(
        default=True,
        description="Show source provenance information",
    )
    deduplicate_sources: bool = Field(
        default=True,
        description="Deduplicate results from same source",
    )


class QueryExpansionRules(BaseModel):
    """Rules for expanding queries based on persona needs."""

    strategy: QueryExpansionStrategy = Field(
        default=QueryExpansionStrategy.NONE,
        description="Expansion strategy to use",
    )
    add_synonyms: bool = Field(
        default=False,
        description="Add synonyms to query",
    )
    add_related_terms: bool = Field(
        default=False,
        description="Add related technical/domain terms",
    )
    extract_entities: bool = Field(
        default=False,
        description="Extract and emphasize named entities",
    )
    temporal_context: bool = Field(
        default=False,
        description="Add temporal context (e.g., historical period)",
    )
    max_expansion_terms: int = Field(
        default=5,
        ge=0,
        le=20,
        description="Maximum additional terms to add",
    )


class QueryTemplate(BaseModel):
    """Complete query template for a persona.

    Each template defines how queries should be processed, expanded,
    and executed for a specific user persona.
    """

    persona: PersonaType = Field(
        ...,
        description="Persona this template applies to",
    )
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable persona name",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Template purpose and use case",
    )
    namespaces: List[str] = Field(
        ...,
        min_items=1,
        description="Priority-ordered vector namespaces to search",
    )
    expansion: QueryExpansionRules = Field(
        default_factory=QueryExpansionRules,
        description="Query expansion rules",
    )
    filters: MetadataFilterTemplate = Field(
        default_factory=MetadataFilterTemplate,
        description="Metadata filter templates",
    )
    retrieval: RetrievalParameterOverrides = Field(
        default_factory=RetrievalParameterOverrides,
        description="Retrieval parameter overrides",
    )
    context_formatting: ContextFormattingPreferences = Field(
        default_factory=ContextFormattingPreferences,
        description="Context formatting preferences",
    )
    nguzo_saba_principle: str = Field(
        ...,
        description="Primary Nguzo Saba principle this template embodies",
    )
    example_queries: List[str] = Field(
        default_factory=list,
        description="Example queries this template handles well",
    )

    @field_validator("namespaces")
    @classmethod
    def validate_namespaces(cls, v: List[str]) -> List[str]:
        """Ensure namespaces list is not empty."""
        if not v:
            raise ValueError("At least one namespace must be specified")
        return v


class QueryTemplateApplication(BaseModel):
    """Result of applying a query template to a user query.

    This model represents the processed query ready for execution.
    """

    original_query: str = Field(
        ...,
        description="Original user query",
    )
    expanded_query: str = Field(
        ...,
        description="Query after expansion",
    )
    expansion_terms: List[str] = Field(
        default_factory=list,
        description="Terms added during expansion",
    )
    namespaces: List[str] = Field(
        ...,
        description="Namespaces to search in priority order",
    )
    metadata_filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata filters to apply",
    )
    similarity_threshold: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity threshold to use",
    )
    result_limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Maximum results to return",
    )
    min_results: int = Field(
        default=1,
        ge=1,
        description="Minimum results to consider successful",
    )
    rerank: bool = Field(
        default=False,
        description="Whether to apply reranking",
    )
    context_formatting: ContextFormattingPreferences = Field(
        ...,
        description="How to format retrieved context",
    )
    template_used: str = Field(
        ...,
        description="Template identifier that was applied",
    )
    persona: PersonaType = Field(
        ...,
        description="Persona type",
    )


class TemplateSelectionRequest(BaseModel):
    """Request model for selecting and applying a query template."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query text",
    )
    persona: PersonaType = Field(
        ...,
        description="User persona for template selection",
    )
    template_overrides: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional overrides for template parameters",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for query processing",
    )


class TemplateSelectionResponse(BaseModel):
    """Response model after template selection and application."""

    status: str = Field(
        default="success",
        description="Response status",
    )
    application: QueryTemplateApplication = Field(
        ...,
        description="Applied template with processed query",
    )
    template_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about template selection",
    )
