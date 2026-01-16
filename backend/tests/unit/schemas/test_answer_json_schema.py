"""Unit tests for answer_json schema models.

These tests verify that the Pydantic schema correctly validates
answer_json data according to the contract specifications.

Test Coverage:
- Valid answer_json structures
- Field validation (required, types, constraints)
- Enum validation
- Cross-field validation
- Edge cases
"""

import pytest
from pydantic import ValidationError

from app.schemas.answer_json import (
    AnswerJson,
    AnswerSection,
    Completeness,
    FallbackBehavior,
    IntegritySection,
    ModelMode,
    Persona,
    ProvenanceSection,
    RetrievalConfidence,
    RetrievalResult,
    RetrievalSummarySection,
    SourceReference,
    Tone,
    TogglesSection,
    UnknownsSection,
)
from tests.fixtures.answer_json_fixtures import INVALID_FIXTURES, VALID_FIXTURES


class TestEnums:
    """Test enum types are correctly defined and validated."""

    def test_persona_enum_values(self) -> None:
        """Test Persona enum contains expected values."""
        assert Persona.EDUCATOR.value == "educator"
        assert Persona.RESEARCHER.value == "researcher"
        assert Persona.CREATOR.value == "creator"
        assert Persona.BUILDER.value == "builder"

    def test_model_mode_enum_values(self) -> None:
        """Test ModelMode enum contains expected values."""
        assert ModelMode.BASE_ADAPTER_RAG.value == "base_adapter_rag"
        assert ModelMode.BASE_RAG.value == "base_rag"
        assert ModelMode.BASE_ONLY.value == "base_only"
        assert ModelMode.CREATIVE.value == "creative"

    def test_tone_enum_values(self) -> None:
        """Test Tone enum contains expected values."""
        assert Tone.NEUTRAL.value == "neutral"
        assert Tone.FORMAL.value == "formal"
        assert Tone.CONVERSATIONAL.value == "conversational"
        assert Tone.ACADEMIC.value == "academic"

    def test_completeness_enum_values(self) -> None:
        """Test Completeness enum contains expected values."""
        assert Completeness.COMPLETE.value == "complete"
        assert Completeness.PARTIAL.value == "partial"
        assert Completeness.INCOMPLETE.value == "incomplete"

    def test_retrieval_confidence_enum_values(self) -> None:
        """Test RetrievalConfidence enum contains expected values."""
        assert RetrievalConfidence.HIGH.value == "high"
        assert RetrievalConfidence.MEDIUM.value == "medium"
        assert RetrievalConfidence.LOW.value == "low"

    def test_fallback_behavior_enum_values(self) -> None:
        """Test FallbackBehavior enum contains expected values."""
        assert FallbackBehavior.NOT_NEEDED.value == "not_needed"
        assert FallbackBehavior.GRACEFUL_DECLINE.value == "graceful_decline"
        assert FallbackBehavior.GENERAL_KNOWLEDGE.value == "general_knowledge"


class TestTogglesSection:
    """Test TogglesSection validation."""

    def test_valid_toggles(self) -> None:
        """Test valid toggles section."""
        toggles = TogglesSection(
            require_citations=True, primary_sources_only=False, creative_mode=False
        )
        assert toggles.require_citations is True
        assert toggles.primary_sources_only is False
        assert toggles.creative_mode is False

    def test_all_toggles_true(self) -> None:
        """Test all toggles can be True."""
        toggles = TogglesSection(
            require_citations=True, primary_sources_only=True, creative_mode=True
        )
        assert toggles.require_citations is True
        assert toggles.primary_sources_only is True
        assert toggles.creative_mode is True

    def test_missing_required_field(self) -> None:
        """Test missing required field raises error."""
        with pytest.raises(ValidationError) as exc_info:
            TogglesSection(require_citations=True, primary_sources_only=False)  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("creative_mode",) for error in errors)


class TestAnswerSection:
    """Test AnswerSection validation."""

    def test_valid_answer_section(self) -> None:
        """Test valid answer section."""
        answer = AnswerSection(
            text="This is a valid answer.", confidence=0.85, tone="neutral", completeness="complete"
        )
        assert answer.text == "This is a valid answer."
        assert answer.confidence == 0.85
        assert answer.tone == Tone.NEUTRAL
        assert answer.completeness == Completeness.COMPLETE

    def test_empty_text_fails(self) -> None:
        """Test empty text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnswerSection(text="", confidence=0.85, tone="neutral", completeness="complete")

        errors = exc_info.value.errors()
        assert any("text" in str(error["loc"]) for error in errors)

    def test_whitespace_only_text_fails(self) -> None:
        """Test whitespace-only text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnswerSection(text="   ", confidence=0.85, tone="neutral", completeness="complete")

        errors = exc_info.value.errors()
        assert any("text" in str(error["loc"]) for error in errors)

    def test_confidence_below_range_fails(self) -> None:
        """Test confidence below 0.0 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnswerSection(
                text="Valid text", confidence=-0.1, tone="neutral", completeness="complete"
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("confidence",) for error in errors)

    def test_confidence_above_range_fails(self) -> None:
        """Test confidence above 1.0 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnswerSection(text="Valid text", confidence=1.5, tone="neutral", completeness="complete")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("confidence",) for error in errors)

    def test_confidence_boundary_values(self) -> None:
        """Test confidence boundary values 0.0 and 1.0."""
        answer_min = AnswerSection(
            text="Valid text", confidence=0.0, tone="neutral", completeness="complete"
        )
        answer_max = AnswerSection(
            text="Valid text", confidence=1.0, tone="neutral", completeness="complete"
        )
        assert answer_min.confidence == 0.0
        assert answer_max.confidence == 1.0

    def test_invalid_tone_enum(self) -> None:
        """Test invalid tone enum value raises error."""
        with pytest.raises(ValidationError) as exc_info:
            AnswerSection(
                text="Valid text", confidence=0.85, tone="invalid_tone", completeness="complete"  # type: ignore
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("tone",) for error in errors)


class TestSourceReference:
    """Test SourceReference validation."""

    def test_valid_source_reference(self) -> None:
        """Test valid source reference."""
        source = SourceReference(
            citation_label="Test Source (2020)",
            canonical_url="https://example.com/test",
            source_org="Test Organization",
            year=2020,
            content_type="article",
            license="CC-BY-4.0",
            namespace="test_namespace",
            doc_id="doc_123",
            chunk_id="doc_123::chunk::1",
        )
        assert source.citation_label == "Test Source (2020)"
        assert source.year == 2020

    def test_url_without_protocol_fails(self) -> None:
        """Test URL without protocol raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SourceReference(
                citation_label="Test Source",
                canonical_url="example.com/test",  # Missing protocol
                source_org="Test Org",
                year=2020,
                content_type="article",
                license="CC-BY-4.0",
                namespace="test",
                doc_id="doc_123",
                chunk_id="doc_123::chunk::1",
            )

        errors = exc_info.value.errors()
        assert any("canonical_url" in str(error["loc"]) for error in errors)

    def test_year_below_range_fails(self) -> None:
        """Test year below 1600 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SourceReference(
                citation_label="Test",
                canonical_url="https://example.com",
                source_org="Test",
                year=1500,  # Below minimum
                content_type="test",
                license="test",
                namespace="test",
                doc_id="test",
                chunk_id="test::1",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("year",) for error in errors)

    def test_year_above_range_fails(self) -> None:
        """Test year above 2100 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SourceReference(
                citation_label="Test",
                canonical_url="https://example.com",
                source_org="Test",
                year=2150,  # Above maximum
                content_type="test",
                license="test",
                namespace="test",
                doc_id="test",
                chunk_id="test::1",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("year",) for error in errors)

    def test_year_boundary_values(self) -> None:
        """Test year boundary values 1600 and 2100."""
        source_min = SourceReference(
            citation_label="Old Source",
            canonical_url="https://example.com",
            source_org="Test",
            year=1600,
            content_type="test",
            license="test",
            namespace="test",
            doc_id="test",
            chunk_id="test::1",
        )
        source_max = SourceReference(
            citation_label="Future Source",
            canonical_url="https://example.com",
            source_org="Test",
            year=2100,
            content_type="test",
            license="test",
            namespace="test",
            doc_id="test",
            chunk_id="test::1",
        )
        assert source_min.year == 1600
        assert source_max.year == 2100


class TestRetrievalResult:
    """Test RetrievalResult validation."""

    def test_valid_retrieval_result(self) -> None:
        """Test valid retrieval result."""
        result = RetrievalResult(
            rank=1,
            score=0.95,
            snippet="Test snippet",
            citation_label="Test Source",
            canonical_url="https://example.com",
            doc_id="doc_123",
            chunk_id="doc_123::chunk::1",
            namespace="test",
        )
        assert result.rank == 1
        assert result.score == 0.95

    def test_rank_zero_fails(self) -> None:
        """Test rank=0 raises validation error (must be >= 1)."""
        with pytest.raises(ValidationError) as exc_info:
            RetrievalResult(
                rank=0,  # Invalid
                score=0.95,
                snippet="Test",
                citation_label="Test",
                canonical_url="https://example.com",
                doc_id="test",
                chunk_id="test::1",
                namespace="test",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("rank",) for error in errors)

    def test_score_out_of_range_fails(self) -> None:
        """Test score outside [0.0, 1.0] raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RetrievalResult(
                rank=1,
                score=1.5,  # Invalid
                snippet="Test",
                citation_label="Test",
                canonical_url="https://example.com",
                doc_id="test",
                chunk_id="test::1",
                namespace="test",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("score",) for error in errors)


class TestRetrievalSummarySection:
    """Test RetrievalSummarySection validation."""

    def test_valid_retrieval_summary(self) -> None:
        """Test valid retrieval summary."""
        summary = RetrievalSummarySection(
            query="test query",
            top_k=5,
            namespaces=["test_namespace"],
            filters={"year_gte": 2000},
            results=[
                RetrievalResult(
                    rank=1,
                    score=0.95,
                    snippet="Result 1",
                    citation_label="Source 1",
                    canonical_url="https://example.com/1",
                    doc_id="doc_1",
                    chunk_id="doc_1::1",
                    namespace="test_namespace",
                )
            ],
        )
        assert summary.query == "test query"
        assert summary.top_k == 5

    def test_empty_namespaces_fails(self) -> None:
        """Test empty namespaces list raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RetrievalSummarySection(
                query="test",
                top_k=1,
                namespaces=[],  # Empty list
                filters={},
                results=[
                    RetrievalResult(
                        rank=1,
                        score=0.8,
                        snippet="Test",
                        citation_label="Test",
                        canonical_url="https://example.com",
                        doc_id="test",
                        chunk_id="test::1",
                        namespace="test",
                    )
                ],
            )

        errors = exc_info.value.errors()
        assert any("namespaces" in str(error["loc"]) for error in errors)

    def test_empty_results_fails(self) -> None:
        """Test empty results list raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RetrievalSummarySection(
                query="test", top_k=1, namespaces=["test"], filters={}, results=[]  # Empty
            )

        errors = exc_info.value.errors()
        assert any("results" in str(error["loc"]) for error in errors)

    def test_results_wrong_order_fails(self) -> None:
        """Test results not ordered by rank raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RetrievalSummarySection(
                query="test",
                top_k=2,
                namespaces=["test"],
                filters={},
                results=[
                    RetrievalResult(
                        rank=2,  # Wrong order
                        score=0.8,
                        snippet="Second",
                        citation_label="Test",
                        canonical_url="https://example.com",
                        doc_id="test2",
                        chunk_id="test2::1",
                        namespace="test",
                    ),
                    RetrievalResult(
                        rank=1,  # Should be first
                        score=0.9,
                        snippet="First",
                        citation_label="Test",
                        canonical_url="https://example.com",
                        doc_id="test1",
                        chunk_id="test1::1",
                        namespace="test",
                    ),
                ],
            )

        errors = exc_info.value.errors()
        assert any("results" in str(error["loc"]) for error in errors)

    def test_single_result_valid(self) -> None:
        """Test single result is valid (no ordering check needed)."""
        summary = RetrievalSummarySection(
            query="test",
            top_k=1,
            namespaces=["test"],
            filters={},
            results=[
                RetrievalResult(
                    rank=1,
                    score=0.8,
                    snippet="Test",
                    citation_label="Test",
                    canonical_url="https://example.com",
                    doc_id="test",
                    chunk_id="test::1",
                    namespace="test",
                )
            ],
        )
        assert len(summary.results) == 1


class TestIntegritySection:
    """Test IntegritySection validation."""

    def test_valid_integrity_section(self) -> None:
        """Test valid integrity section."""
        integrity = IntegritySection(
            citation_required=True,
            citations_provided=True,
            retrieval_confidence="high",
            fallback_behavior="not_needed",
        )
        assert integrity.citation_required is True
        assert integrity.citations_provided is True

    def test_citation_inconsistency_fails(self) -> None:
        """Test citation_required=True but citations_provided=False fails."""
        with pytest.raises(ValidationError) as exc_info:
            IntegritySection(
                citation_required=True,
                citations_provided=False,  # Inconsistent
                retrieval_confidence="high",
                fallback_behavior="not_needed",
            )

        errors = exc_info.value.errors()
        # Check for model-level validation error
        assert len(errors) > 0

    def test_no_citation_required_but_provided_valid(self) -> None:
        """Test citation_required=False but citations_provided=True is valid."""
        integrity = IntegritySection(
            citation_required=False,
            citations_provided=True,  # OK to provide even if not required
            retrieval_confidence="medium",
            fallback_behavior="not_needed",
        )
        assert integrity.citations_provided is True


class TestAnswerJsonComplete:
    """Test complete AnswerJson validation."""

    @pytest.mark.parametrize("fixture_name", list(VALID_FIXTURES.keys()))
    def test_all_valid_fixtures(self, fixture_name: str) -> None:
        """Test all valid fixtures pass validation."""
        fixture_data = VALID_FIXTURES[fixture_name]
        answer = AnswerJson.model_validate(fixture_data)
        assert answer.version == fixture_data["version"]

    def test_missing_version_fails(self) -> None:
        """Test missing version field fails."""
        data = INVALID_FIXTURES["missing_required_field_version"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("version",) for error in errors)

    def test_invalid_version_format_fails(self) -> None:
        """Test invalid version format fails."""
        data = INVALID_FIXTURES["invalid_version_format"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("version",) for error in errors)

    def test_invalid_persona_fails(self) -> None:
        """Test invalid persona value fails."""
        data = INVALID_FIXTURES["invalid_persona"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("persona",) for error in errors)

    def test_empty_answer_text_fails(self) -> None:
        """Test empty answer text fails."""
        data = INVALID_FIXTURES["empty_answer_text"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert any("text" in str(error["loc"]) for error in errors)

    def test_confidence_out_of_range_fails(self) -> None:
        """Test confidence out of range fails."""
        data = INVALID_FIXTURES["confidence_out_of_range"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert any("confidence" in str(error["loc"]) for error in errors)

    def test_invalid_url_format_fails(self) -> None:
        """Test invalid URL format fails."""
        data = INVALID_FIXTURES["invalid_url_format"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert any("canonical_url" in str(error["loc"]) for error in errors)

    def test_missing_sources_when_required_fails(self) -> None:
        """Test missing sources when required fails."""
        data = INVALID_FIXTURES["missing_sources_when_required"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        # Model-level validation error
        assert len(errors) > 0

    def test_citation_consistency_violation_fails(self) -> None:
        """Test citation consistency violation fails."""
        data = INVALID_FIXTURES["citation_consistency_violation"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_retrieval_results_wrong_order_fails(self) -> None:
        """Test retrieval results in wrong order fails."""
        data = INVALID_FIXTURES["retrieval_results_wrong_order"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        assert any("results" in str(error["loc"]) for error in errors)

    def test_source_not_in_retrieval_results_fails(self) -> None:
        """Test source not in retrieval results fails."""
        data = INVALID_FIXTURES["source_not_in_retrieval_results"]["data"]
        with pytest.raises(ValidationError) as exc_info:
            AnswerJson.model_validate(data)

        errors = exc_info.value.errors()
        # Model-level validation error about doc_ids
        assert len(errors) > 0

    def test_valid_answer_serialization(self) -> None:
        """Test valid answer can be serialized back to dict."""
        fixture_data = VALID_FIXTURES["complete_answer_with_citations"]
        answer = AnswerJson.model_validate(fixture_data)
        serialized = answer.model_dump()

        # Verify key fields are present
        assert "version" in serialized
        assert "persona" in serialized
        assert "answer" in serialized
        assert "sources" in serialized
        assert "integrity" in serialized
