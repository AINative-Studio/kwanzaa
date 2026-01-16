"""Tests for Answer JSON Contract models and validation.

This test suite validates the Answer JSON Contract schema against
the requirements for the Kwanzaa project, ensuring that all validation
rules and business logic constraints are properly enforced.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.answer_json import (
    Answer,
    AnswerJsonContract,
    Completeness,
    FallbackBehavior,
    Integrity,
    ModelMode,
    Persona,
    Provenance,
    RetrievalConfidence,
    RetrievalFilters,
    RetrievalResult,
    RetrievalSummary,
    Source,
    Toggles,
    Tone,
    Unknowns,
    create_answer_json_contract,
)


class TestAnswerModel:
    """Test cases for Answer model."""

    def test_valid_answer_minimal(self):
        """Test valid answer with minimal required fields."""
        answer = Answer(text="This is a valid answer.")
        assert answer.text == "This is a valid answer."
        assert answer.confidence is None
        assert answer.tone is None
        assert answer.completeness is None

    def test_valid_answer_complete(self):
        """Test valid answer with all fields."""
        answer = Answer(
            text="Complete answer with metadata.",
            confidence=0.95,
            tone=Tone.EDUCATIONAL,
            completeness=Completeness.COMPLETE,
        )
        assert answer.text == "Complete answer with metadata."
        assert answer.confidence == 0.95
        assert answer.tone == Tone.EDUCATIONAL
        assert answer.completeness == Completeness.COMPLETE

    def test_answer_text_too_short(self):
        """Test that empty text fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            Answer(text="")
        assert "at least 1 character" in str(exc_info.value).lower()

    def test_answer_text_too_long(self):
        """Test that text exceeding max length fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            Answer(text="x" * 10001)
        assert "at most 10000 character" in str(exc_info.value).lower()

    def test_answer_confidence_out_of_range(self):
        """Test that confidence outside [0.0, 1.0] fails validation."""
        with pytest.raises(ValidationError):
            Answer(text="Test", confidence=1.5)

        with pytest.raises(ValidationError):
            Answer(text="Test", confidence=-0.1)


class TestSourceModel:
    """Test cases for Source model."""

    def test_valid_source_minimal(self):
        """Test valid source with required fields only."""
        source = Source(
            citation_label="Test Source (2024)",
            canonical_url="https://example.org/test",
            source_org="Test Organization",
            year=2024,
            content_type="article",
            license="Public Domain",
            namespace="test_namespace",
            doc_id="doc_123",
            chunk_id="doc_123::chunk::1",
        )
        assert source.citation_label == "Test Source (2024)"
        assert source.year == 2024
        assert source.tags is None

    def test_valid_source_with_tags(self):
        """Test valid source with tags and relevance score."""
        source = Source(
            citation_label="Test Source (2024)",
            canonical_url="https://example.org/test",
            source_org="Test Organization",
            year=2024,
            content_type="article",
            license="Public Domain",
            namespace="test_namespace",
            doc_id="doc_123",
            chunk_id="doc_123::chunk::1",
            tags=["tag1", "tag2"],
            relevance_score=0.92,
        )
        assert source.tags == ["tag1", "tag2"]
        assert source.relevance_score == 0.92

    def test_source_year_out_of_range(self):
        """Test that year outside valid range fails validation."""
        with pytest.raises(ValidationError):
            Source(
                citation_label="Test",
                canonical_url="https://example.org",
                source_org="Test Org",
                year=1599,  # Too early
                content_type="article",
                license="Public Domain",
                namespace="test",
                doc_id="test",
                chunk_id="test",
            )


class TestRetrievalFilters:
    """Test cases for RetrievalFilters model."""

    def test_valid_filters(self):
        """Test valid filters with year range."""
        filters = RetrievalFilters(
            content_type=["article", "book"],
            year_gte=1960,
            year_lte=1970,
            tags=["civil_rights"],
        )
        assert filters.year_gte == 1960
        assert filters.year_lte == 1970

    def test_invalid_year_range(self):
        """Test that year_lte < year_gte fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            RetrievalFilters(year_gte=1970, year_lte=1960)
        assert "greater than or equal to" in str(exc_info.value).lower()


class TestAnswerJsonContract:
    """Test cases for complete AnswerJsonContract model."""

    def test_minimal_valid_contract(self):
        """Test minimal valid contract with required fields only."""
        contract = AnswerJsonContract(
            version="kwanzaa.answer.v1",
            answer=Answer(text="Test answer"),
            sources=[],
            retrieval_summary=RetrievalSummary(
                query="test query",
                top_k=10,
                namespaces=["test_namespace"],
                results=[],
            ),
            unknowns=Unknowns(
                unsupported_claims=[],
                missing_context=[],
                clarifying_questions=[],
            ),
        )
        assert contract.version == "kwanzaa.answer.v1"
        assert contract.answer.text == "Test answer"
        assert len(contract.sources) == 0

    def test_complete_valid_contract(self):
        """Test complete valid contract with all fields."""
        contract = AnswerJsonContract(
            version="kwanzaa.answer.v1",
            persona=Persona.EDUCATOR,
            model_mode=ModelMode.BASE_ADAPTER_RAG,
            toggles=Toggles(
                require_citations=True,
                primary_sources_only=True,
                creative_mode=False,
            ),
            answer=Answer(
                text="Complete answer",
                confidence=0.95,
                tone=Tone.EDUCATIONAL,
                completeness=Completeness.COMPLETE,
            ),
            sources=[
                Source(
                    citation_label="Test (2024)",
                    canonical_url="https://example.org/test",
                    source_org="Test Org",
                    year=2024,
                    content_type="article",
                    license="Public Domain",
                    namespace="test",
                    doc_id="doc_1",
                    chunk_id="doc_1::chunk::1",
                )
            ],
            retrieval_summary=RetrievalSummary(
                query="test query",
                top_k=10,
                namespaces=["test"],
                results=[
                    RetrievalResult(
                        rank=1,
                        score=0.95,
                        citation_label="Test (2024)",
                        canonical_url="https://example.org/test",
                        doc_id="doc_1",
                        chunk_id="doc_1::chunk::1",
                        namespace="test",
                    )
                ],
            ),
            unknowns=Unknowns(
                unsupported_claims=[],
                missing_context=[],
                clarifying_questions=[],
            ),
            integrity=Integrity(
                citation_required=True,
                citations_provided=True,
                retrieval_confidence=RetrievalConfidence.HIGH,
                fallback_behavior=FallbackBehavior.NOT_NEEDED,
            ),
            provenance=Provenance(
                generated_at=datetime.now(timezone.utc),
                retrieval_run_id=uuid4(),
                assistant_message_id=uuid4(),
            ),
        )
        assert contract.persona == Persona.EDUCATOR
        assert len(contract.sources) == 1
        assert contract.integrity.retrieval_confidence == RetrievalConfidence.HIGH

    def test_invalid_version_format(self):
        """Test that invalid version format fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            AnswerJsonContract(
                version="v1.0.0",  # Wrong format
                answer=Answer(text="Test"),
                sources=[],
                retrieval_summary=RetrievalSummary(
                    query="test",
                    top_k=10,
                    namespaces=["test"],
                    results=[],
                ),
                unknowns=Unknowns(
                    unsupported_claims=[],
                    missing_context=[],
                    clarifying_questions=[],
                ),
            )
        assert "pattern" in str(exc_info.value).lower()

    def test_citation_integrity_validation(self):
        """Test citation integrity validator."""
        # This should fail: citations required but not provided
        with pytest.raises(ValidationError) as exc_info:
            AnswerJsonContract(
                version="kwanzaa.answer.v1",
                answer=Answer(text="Test"),
                sources=[],  # Empty sources
                retrieval_summary=RetrievalSummary(
                    query="test",
                    top_k=10,
                    namespaces=["test"],
                    results=[],
                ),
                unknowns=Unknowns(
                    unsupported_claims=[],
                    missing_context=[],
                    clarifying_questions=[],
                ),
                integrity=Integrity(
                    citation_required=True,
                    citations_provided=False,
                ),
            )
        assert "imani" in str(exc_info.value).lower()


class TestHelperFunctions:
    """Test helper functions for creating contracts."""

    def test_create_answer_json_contract_minimal(self):
        """Test helper function with minimal parameters."""
        contract = create_answer_json_contract(
            answer="Test answer",
            query="Test query",
        )
        assert contract.version == "kwanzaa.answer.v1"
        assert contract.answer.text == "Test answer"
        assert contract.retrieval_summary.query == "Test query"

    def test_create_answer_json_contract_with_options(self):
        """Test helper function with optional parameters."""
        source = Source(
            citation_label="Test (2024)",
            canonical_url="https://example.org/test",
            source_org="Test Org",
            year=2024,
            content_type="article",
            license="Public Domain",
            namespace="test",
            doc_id="doc_1",
            chunk_id="doc_1::chunk::1",
        )

        contract = create_answer_json_contract(
            answer="Test answer",
            query="Test query",
            persona=Persona.RESEARCHER,
            model_mode=ModelMode.BASE_ADAPTER_RAG,
            sources=[source],
        )
        assert contract.persona == Persona.RESEARCHER
        assert len(contract.sources) == 1


class TestExampleFiles:
    """Test validation against example JSON files."""

    @pytest.fixture
    def examples_dir(self):
        """Get examples directory path."""
        return Path(__file__).parent.parent / "app" / "schemas" / "examples"

    def test_valid_minimal_example(self, examples_dir):
        """Test that valid_minimal.json is valid."""
        with open(examples_dir / "valid_minimal.json") as f:
            data = json.load(f)

        contract = AnswerJsonContract.model_validate(data)
        assert contract.version == "kwanzaa.answer.v1"

    def test_valid_complete_example(self, examples_dir):
        """Test that valid_complete.json is valid."""
        with open(examples_dir / "valid_complete.json") as f:
            data = json.load(f)

        contract = AnswerJsonContract.model_validate(data)
        assert contract.persona == Persona.EDUCATOR
        assert len(contract.sources) == 2

    def test_valid_with_unknowns_example(self, examples_dir):
        """Test that valid_with_unknowns.json is valid."""
        with open(examples_dir / "valid_with_unknowns.json") as f:
            data = json.load(f)

        contract = AnswerJsonContract.model_validate(data)
        assert len(contract.unknowns.missing_context) > 0
        assert len(contract.unknowns.clarifying_questions) > 0

    def test_invalid_missing_required_example(self, examples_dir):
        """Test that invalid_missing_required.json fails validation."""
        with open(examples_dir / "invalid_missing_required.json") as f:
            data = json.load(f)

        with pytest.raises(ValidationError):
            AnswerJsonContract.model_validate(data)

    def test_invalid_bad_version_example(self, examples_dir):
        """Test that invalid_bad_version.json fails validation."""
        with open(examples_dir / "invalid_bad_version.json") as f:
            data = json.load(f)

        with pytest.raises(ValidationError):
            AnswerJsonContract.model_validate(data)

    def test_invalid_citation_integrity_example(self, examples_dir):
        """Test that invalid_citation_integrity.json fails validation."""
        with open(examples_dir / "invalid_citation_integrity.json") as f:
            data = json.load(f)

        with pytest.raises(ValidationError) as exc_info:
            AnswerJsonContract.model_validate(data)
        assert "imani" in str(exc_info.value).lower()


class TestSerializationRoundTrip:
    """Test serialization and deserialization."""

    def test_json_round_trip(self):
        """Test that contract can be serialized and deserialized."""
        original = create_answer_json_contract(
            answer="Test answer",
            query="Test query",
            persona=Persona.EDUCATOR,
        )

        # Serialize to JSON
        json_str = original.model_dump_json()

        # Deserialize back
        restored = AnswerJsonContract.model_validate_json(json_str)

        assert restored.answer.text == original.answer.text
        assert restored.persona == original.persona

    def test_dict_round_trip(self):
        """Test that contract can be converted to/from dict."""
        original = create_answer_json_contract(
            answer="Test answer",
            query="Test query",
        )

        # Convert to dict
        data_dict = original.model_dump()

        # Restore from dict
        restored = AnswerJsonContract.model_validate(data_dict)

        assert restored.answer.text == original.answer.text
        assert restored.version == original.version
