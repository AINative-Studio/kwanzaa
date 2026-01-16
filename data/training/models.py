"""Pydantic models for Kwanzaa Adapter Training Dataset validation.

Version: 1.0.0

These models validate training samples that teach the adapter:
- Citation-following behavior
- Refusal patterns
- answer_json format compliance
- Grounded answer synthesis

Enforces strict schema compliance for high-quality training data.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TrainingCategory(str, Enum):
    """Primary training objective category."""

    CITATION = "citation"
    REFUSAL = "refusal"
    GROUNDED_ANSWER = "grounded_answer"
    FORMAT_COMPLIANCE = "format_compliance"


class Persona(str, Enum):
    """Target persona for the training sample."""

    EDUCATOR = "educator"
    RESEARCHER = "researcher"
    CREATOR = "creator"
    BUILDER = "builder"


class Difficulty(str, Enum):
    """Complexity level for the model."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class NguzoPrinciple(str, Enum):
    """Nguzo Saba (Seven Principles) of Kwanzaa."""

    UMOJA = "Umoja"
    KUJICHAGULIA = "Kujichagulia"
    UJIMA = "Ujima"
    UJAMAA = "Ujamaa"
    NIA = "Nia"
    KUUMBA = "Kuumba"
    IMANI = "Imani"


class RetrievalResultMetadata(BaseModel):
    """Metadata for a simulated retrieval result."""

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
    tags: Optional[List[str]] = Field(
        default=None,
        description="Content tags for categorization",
    )


class RetrievalResult(BaseModel):
    """Simulated retrieval result for training context."""

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
    chunk_id: str = Field(
        ...,
        min_length=1,
        description="Unique chunk identifier",
    )
    doc_id: str = Field(
        ...,
        min_length=1,
        description="Unique document identifier",
    )
    namespace: str = Field(
        ...,
        min_length=1,
        description="Vector namespace",
    )
    content: str = Field(
        ...,
        max_length=2000,
        description="Retrieved content chunk",
    )
    metadata: RetrievalResultMetadata = Field(
        ...,
        description="Source metadata",
    )


class AnswerJsonContract(BaseModel):
    """Expected answer_json output (validates against Epic 8 contract).

    This is a simplified validation model. The full validation is handled
    by backend.app.models.answer_json.AnswerJsonContract.
    """

    version: str = Field(
        ...,
        pattern=r"^kwanzaa\.answer\.v[0-9]+$",
        description="Contract version identifier",
    )
    persona: Optional[str] = Field(
        default=None,
        description="Persona mode",
    )
    model_mode: Optional[str] = Field(
        default=None,
        description="Model mode",
    )
    toggles: Optional[Dict] = Field(
        default=None,
        description="User toggles",
    )
    answer: Dict = Field(
        ...,
        description="Main answer object with text field",
    )
    sources: List[Dict] = Field(
        ...,
        description="Array of source citations",
    )
    retrieval_summary: Dict = Field(
        ...,
        description="Retrieval process summary",
    )
    unknowns: Dict = Field(
        ...,
        description="Limitations and gaps",
    )
    integrity: Optional[Dict] = Field(
        default=None,
        description="Integrity metadata",
    )
    provenance: Optional[Dict] = Field(
        default=None,
        description="Generation provenance",
    )

    @field_validator("answer")
    @classmethod
    def validate_answer_has_text(cls, v: Dict) -> Dict:
        """Ensure answer object has required text field."""
        if "text" not in v or not v["text"]:
            raise ValueError("answer.text is required and must be non-empty")
        return v

    @field_validator("retrieval_summary")
    @classmethod
    def validate_retrieval_summary_required_fields(cls, v: Dict) -> Dict:
        """Ensure retrieval_summary has required fields."""
        required = ["query", "top_k", "namespaces", "results"]
        for field in required:
            if field not in v:
                raise ValueError(f"retrieval_summary.{field} is required")
        return v

    @field_validator("unknowns")
    @classmethod
    def validate_unknowns_required_fields(cls, v: Dict) -> Dict:
        """Ensure unknowns has required fields."""
        required = ["unsupported_claims", "missing_context", "clarifying_questions"]
        for field in required:
            if field not in v:
                raise ValueError(f"unknowns.{field} is required")
        return v

    model_config = ConfigDict(extra="allow")


class TrainingMetadata(BaseModel):
    """Metadata for a training sample."""

    difficulty: Difficulty = Field(
        ...,
        description="Complexity level for the model",
    )
    principle_focus: List[NguzoPrinciple] = Field(
        ...,
        min_length=1,
        description="Which Nguzo Saba principles this sample emphasizes",
    )
    quality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Quality rating for this sample (0.0-1.0)",
    )
    reviewer: Optional[str] = Field(
        default=None,
        description="Name or ID of person who validated this sample",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about this sample",
    )
    edge_case: Optional[bool] = Field(
        default=False,
        description="Whether this tests an edge case or rare scenario",
    )
    failure_mode: Optional[str] = Field(
        default=None,
        description="What common failure mode this sample addresses",
    )


class TrainingSample(BaseModel):
    """A single training sample for adapter fine-tuning."""

    sample_id: str = Field(
        ...,
        pattern=r"^[a-z0-9_]+$",
        description="Unique identifier for the sample",
    )
    category: TrainingCategory = Field(
        ...,
        description="Primary training objective category",
    )
    persona: Persona = Field(
        ...,
        description="Target persona for this sample",
    )
    user_query: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The user's question or prompt",
    )
    retrieved_context: List[RetrievalResult] = Field(
        default_factory=list,
        description="Simulated retrieval results (can be empty for refusal cases)",
    )
    expected_output: AnswerJsonContract = Field(
        ...,
        description="The complete answer_json contract the model should generate",
    )
    metadata: TrainingMetadata = Field(
        ...,
        description="Metadata about this training sample",
    )

    @model_validator(mode="after")
    def validate_sample_consistency(self) -> "TrainingSample":
        """Validate consistency between sample fields."""
        # Validate persona consistency
        if self.expected_output.persona and self.expected_output.persona != self.persona.value:
            raise ValueError(
                f"Persona mismatch: sample.persona={self.persona.value} but "
                f"expected_output.persona={self.expected_output.persona}"
            )

        # Validate refusal samples should have empty or low-quality context
        if self.category == TrainingCategory.REFUSAL:
            if self.retrieved_context:
                # If context exists for refusal, scores should be low
                high_score_results = [r for r in self.retrieved_context if r.score > 0.7]
                if high_score_results:
                    raise ValueError(
                        f"Refusal sample {self.sample_id} has high-quality retrieval results "
                        f"(score > 0.7). Refusal samples should have no context or low-quality context."
                    )

        # Validate citation samples should have good context
        if self.category == TrainingCategory.CITATION:
            if not self.retrieved_context:
                raise ValueError(
                    f"Citation sample {self.sample_id} has no retrieval context. "
                    f"Citation samples require good retrieval results."
                )
            if not any(r.score > 0.8 for r in self.retrieved_context):
                raise ValueError(
                    f"Citation sample {self.sample_id} has no high-quality results (score > 0.8). "
                    f"Citation samples should demonstrate good retrieval."
                )

        return self


class DatasetStatistics(BaseModel):
    """Statistics for the training dataset."""

    total_samples: int = Field(
        ...,
        ge=0,
        description="Total number of samples in the dataset",
    )
    by_category: Dict[str, int] = Field(
        default_factory=dict,
        description="Sample counts by category",
    )
    by_persona: Dict[str, int] = Field(
        default_factory=dict,
        description="Sample counts by persona",
    )
    by_difficulty: Dict[str, int] = Field(
        default_factory=dict,
        description="Sample counts by difficulty",
    )


class TrainingDataset(BaseModel):
    """Complete training dataset with metadata and samples."""

    dataset_version: str = Field(
        ...,
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$",
        description="Semantic version of the dataset",
    )
    created_at: datetime = Field(
        ...,
        description="Dataset creation timestamp",
    )
    description: Optional[str] = Field(
        default=None,
        description="Overview of this dataset batch",
    )
    statistics: Optional[DatasetStatistics] = Field(
        default=None,
        description="Dataset statistics",
    )
    samples: List[TrainingSample] = Field(
        ...,
        min_length=1,
        description="Array of training samples",
    )

    @model_validator(mode="after")
    def compute_statistics(self) -> "TrainingDataset":
        """Automatically compute statistics if not provided."""
        if not self.statistics:
            from collections import Counter

            categories = Counter(s.category.value for s in self.samples)
            personas = Counter(s.persona.value for s in self.samples)
            difficulties = Counter(s.metadata.difficulty.value for s in self.samples)

            self.statistics = DatasetStatistics(
                total_samples=len(self.samples),
                by_category=dict(categories),
                by_persona=dict(personas),
                by_difficulty=dict(difficulties),
            )

        return self

    @field_validator("samples")
    @classmethod
    def validate_unique_sample_ids(cls, v: List[TrainingSample]) -> List[TrainingSample]:
        """Ensure all sample IDs are unique."""
        sample_ids = [s.sample_id for s in v]
        duplicates = [sid for sid in sample_ids if sample_ids.count(sid) > 1]
        if duplicates:
            raise ValueError(f"Duplicate sample IDs found: {set(duplicates)}")
        return v


# Convenience type aliases for clarity
CitationSample = TrainingSample
RefusalSample = TrainingSample
GroundedAnswerSample = TrainingSample
FormatComplianceSample = TrainingSample
