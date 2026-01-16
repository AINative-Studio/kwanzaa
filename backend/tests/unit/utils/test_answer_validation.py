"""Unit tests for answer_json validation utilities.

These tests verify that the validation utilities correctly validate
answer_json data and provide appropriate error handling.

Test Coverage:
- Successful validation
- Error handling and reporting
- Batch validation
- Helper functions
- Edge cases
"""

import pytest

from app.utils.answer_validation import (
    AnswerValidationError,
    ValidationErrorDetail,
    get_validation_errors,
    is_valid_answer_json,
    validate_answer_json,
    validate_answer_json_dict,
    validate_multiple_responses,
)
from tests.fixtures.answer_json_fixtures import INVALID_FIXTURES, VALID_FIXTURES


class TestValidateAnswerJson:
    """Test validate_answer_json function."""

    def test_valid_complete_answer(self) -> None:
        """Test validation succeeds for complete valid answer."""
        data = VALID_FIXTURES["complete_answer_with_citations"]
        result = validate_answer_json(data)

        assert result.version == "kwanzaa.answer.v1"
        assert result.persona.value == "educator"
        assert result.answer.text is not None
        assert len(result.sources) > 0

    def test_valid_minimal_answer(self) -> None:
        """Test validation succeeds for minimal valid answer."""
        data = VALID_FIXTURES["minimal_valid_answer"]
        result = validate_answer_json(data)

        assert result.version == "kwanzaa.answer.v1"
        assert result.persona.value == "researcher"

    def test_valid_creative_mode_answer(self) -> None:
        """Test validation succeeds for creative mode answer."""
        data = VALID_FIXTURES["creative_mode_answer"]
        result = validate_answer_json(data)

        assert result.toggles.creative_mode is True
        assert result.persona.value == "creator"

    def test_valid_multiple_sources_answer(self) -> None:
        """Test validation succeeds for answer with multiple sources."""
        data = VALID_FIXTURES["multiple_sources_answer"]
        result = validate_answer_json(data)

        assert len(result.sources) == 2
        assert result.integrity.citations_provided is True

    def test_invalid_input_type_raises_error(self) -> None:
        """Test non-dict input raises AnswerValidationError."""
        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json("not a dict")  # type: ignore

        error = exc_info.value
        assert "Input must be a dictionary" in error.message
        assert len(error.errors) == 1
        assert error.errors[0].field == "__root__"

    def test_missing_version_field_raises_error(self) -> None:
        """Test missing required version field raises error."""
        data = INVALID_FIXTURES["missing_required_field_version"]["data"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(data)

        error = exc_info.value
        assert "validation failed" in error.message.lower()
        assert len(error.errors) > 0
        assert any("version" in e.field for e in error.errors)

    def test_invalid_version_format_raises_error(self) -> None:
        """Test invalid version format raises error."""
        data = INVALID_FIXTURES["invalid_version_format"]["data"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(data)

        error = exc_info.value
        assert len(error.errors) > 0
        assert any("version" in e.field for e in error.errors)

    def test_invalid_persona_raises_error(self) -> None:
        """Test invalid persona value raises error."""
        data = INVALID_FIXTURES["invalid_persona"]["data"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(data)

        error = exc_info.value
        assert any("persona" in e.field for e in error.errors)

    def test_empty_answer_text_raises_error(self) -> None:
        """Test empty answer text raises error."""
        data = INVALID_FIXTURES["empty_answer_text"]["data"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(data)

        error = exc_info.value
        assert any("text" in e.field for e in error.errors)

    def test_confidence_out_of_range_raises_error(self) -> None:
        """Test confidence out of range raises error."""
        data = INVALID_FIXTURES["confidence_out_of_range"]["data"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(data)

        error = exc_info.value
        assert any("confidence" in e.field for e in error.errors)

    def test_invalid_url_format_raises_error(self) -> None:
        """Test invalid URL format raises error."""
        data = INVALID_FIXTURES["invalid_url_format"]["data"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(data)

        error = exc_info.value
        assert any("canonical_url" in e.field for e in error.errors)

    def test_validation_error_includes_raw_data(self) -> None:
        """Test validation error includes raw data for debugging."""
        data = INVALID_FIXTURES["invalid_persona"]["data"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(data)

        error = exc_info.value
        assert error.raw_data is not None
        assert error.raw_data == data


class TestValidateAnswerJsonDict:
    """Test validate_answer_json_dict function."""

    def test_returns_dict_for_valid_input(self) -> None:
        """Test returns dictionary for valid input."""
        data = VALID_FIXTURES["complete_answer_with_citations"]
        result = validate_answer_json_dict(data)

        assert isinstance(result, dict)
        assert "version" in result
        assert "persona" in result
        assert "answer" in result

    def test_raises_error_for_invalid_input(self) -> None:
        """Test raises error for invalid input."""
        data = INVALID_FIXTURES["missing_required_field_version"]["data"]

        with pytest.raises(AnswerValidationError):
            validate_answer_json_dict(data)


class TestIsValidAnswerJson:
    """Test is_valid_answer_json helper function."""

    def test_returns_true_for_valid_data(self) -> None:
        """Test returns True for valid data."""
        data = VALID_FIXTURES["complete_answer_with_citations"]
        assert is_valid_answer_json(data) is True

    def test_returns_false_for_invalid_data(self) -> None:
        """Test returns False for invalid data."""
        data = INVALID_FIXTURES["missing_required_field_version"]["data"]
        assert is_valid_answer_json(data) is False

    def test_returns_false_for_non_dict(self) -> None:
        """Test returns False for non-dict input."""
        assert is_valid_answer_json("not a dict") is False  # type: ignore
        assert is_valid_answer_json(None) is False  # type: ignore
        assert is_valid_answer_json([]) is False  # type: ignore


class TestGetValidationErrors:
    """Test get_validation_errors helper function."""

    def test_returns_empty_list_for_valid_data(self) -> None:
        """Test returns empty list for valid data."""
        data = VALID_FIXTURES["complete_answer_with_citations"]
        errors = get_validation_errors(data)
        assert errors == []

    def test_returns_errors_for_invalid_data(self) -> None:
        """Test returns list of errors for invalid data."""
        data = INVALID_FIXTURES["missing_required_field_version"]["data"]
        errors = get_validation_errors(data)

        assert len(errors) > 0
        assert all(isinstance(e, ValidationErrorDetail) for e in errors)
        assert any("version" in e.field for e in errors)

    def test_returns_errors_for_multiple_violations(self) -> None:
        """Test returns multiple errors when multiple fields are invalid."""
        data = INVALID_FIXTURES["citation_consistency_violation"]["data"]
        errors = get_validation_errors(data)

        assert len(errors) > 0


class TestValidateMultipleResponses:
    """Test validate_multiple_responses batch validation."""

    def test_all_valid_responses(self) -> None:
        """Test batch validation with all valid responses."""
        responses = [
            VALID_FIXTURES["complete_answer_with_citations"],
            VALID_FIXTURES["minimal_valid_answer"],
            VALID_FIXTURES["creative_mode_answer"],
        ]

        valid, invalid = validate_multiple_responses(responses)

        assert len(valid) == 3
        assert len(invalid) == 0

    def test_all_invalid_responses(self) -> None:
        """Test batch validation with all invalid responses."""
        responses = [
            INVALID_FIXTURES["missing_required_field_version"]["data"],
            INVALID_FIXTURES["invalid_persona"]["data"],
            INVALID_FIXTURES["empty_answer_text"]["data"],
        ]

        valid, invalid = validate_multiple_responses(responses)

        assert len(valid) == 0
        assert len(invalid) == 3

        # Check error indices
        indices = [idx for idx, _ in invalid]
        assert indices == [0, 1, 2]

    def test_mixed_valid_and_invalid_responses(self) -> None:
        """Test batch validation with mixed responses."""
        responses = [
            VALID_FIXTURES["complete_answer_with_citations"],  # Valid
            INVALID_FIXTURES["invalid_persona"]["data"],  # Invalid
            VALID_FIXTURES["minimal_valid_answer"],  # Valid
            INVALID_FIXTURES["empty_answer_text"]["data"],  # Invalid
        ]

        valid, invalid = validate_multiple_responses(responses)

        assert len(valid) == 2
        assert len(invalid) == 2

        # Check invalid indices
        invalid_indices = [idx for idx, _ in invalid]
        assert invalid_indices == [1, 3]

    def test_empty_list(self) -> None:
        """Test batch validation with empty list."""
        responses: list = []

        valid, invalid = validate_multiple_responses(responses)

        assert len(valid) == 0
        assert len(invalid) == 0


class TestValidationErrorDetail:
    """Test ValidationErrorDetail class."""

    def test_initialization(self) -> None:
        """Test ValidationErrorDetail initialization."""
        detail = ValidationErrorDetail(
            field="test_field", message="Test error", error_type="value_error", location=["test"]
        )

        assert detail.field == "test_field"
        assert detail.message == "Test error"
        assert detail.error_type == "value_error"
        assert detail.location == ["test"]

    def test_repr(self) -> None:
        """Test ValidationErrorDetail string representation."""
        detail = ValidationErrorDetail(
            field="test_field", message="Test error", error_type="value_error", location=["test"]
        )

        repr_str = repr(detail)
        assert "ValidationErrorDetail" in repr_str
        assert "test_field" in repr_str

    def test_to_dict(self) -> None:
        """Test ValidationErrorDetail to_dict conversion."""
        detail = ValidationErrorDetail(
            field="test_field", message="Test error", error_type="value_error", location=["test"]
        )

        result = detail.to_dict()

        assert result["field"] == "test_field"
        assert result["message"] == "Test error"
        assert result["error_type"] == "value_error"
        assert result["location"] == ["test"]


class TestAnswerValidationError:
    """Test AnswerValidationError exception class."""

    def test_initialization(self) -> None:
        """Test AnswerValidationError initialization."""
        errors = [
            ValidationErrorDetail(
                field="test", message="Test error", error_type="value_error", location=["test"]
            )
        ]
        error = AnswerValidationError(message="Validation failed", errors=errors)

        assert error.message == "Validation failed"
        assert len(error.errors) == 1
        assert error.raw_data is None

    def test_initialization_with_raw_data(self) -> None:
        """Test AnswerValidationError initialization with raw data."""
        errors = [
            ValidationErrorDetail(
                field="test", message="Test error", error_type="value_error", location=["test"]
            )
        ]
        raw_data = {"test": "data"}
        error = AnswerValidationError(message="Validation failed", errors=errors, raw_data=raw_data)

        assert error.raw_data == raw_data

    def test_str_representation(self) -> None:
        """Test AnswerValidationError string representation."""
        errors = [
            ValidationErrorDetail(
                field="field1", message="Error 1", error_type="value_error", location=["field1"]
            ),
            ValidationErrorDetail(
                field="field2", message="Error 2", error_type="value_error", location=["field2"]
            ),
        ]
        error = AnswerValidationError(message="Validation failed", errors=errors)

        str_repr = str(error)
        assert "Validation failed" in str_repr
        assert "field1" in str_repr
        assert "field2" in str_repr
        assert "Error 1" in str_repr
        assert "Error 2" in str_repr

    def test_to_dict(self) -> None:
        """Test AnswerValidationError to_dict conversion."""
        errors = [
            ValidationErrorDetail(
                field="test", message="Test error", error_type="value_error", location=["test"]
            )
        ]
        error = AnswerValidationError(message="Validation failed", errors=errors)

        result = error.to_dict()

        assert result["message"] == "Validation failed"
        assert result["error_count"] == 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "test"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_validate_with_unicode_characters(self) -> None:
        """Test validation with Unicode characters in text."""
        data = VALID_FIXTURES["complete_answer_with_citations"].copy()
        data["answer"]["text"] = "Answer with émojis 🎉 and spëcial çharacters"

        result = validate_answer_json(data)
        assert "émojis" in result.answer.text

    def test_validate_with_very_long_text(self) -> None:
        """Test validation with very long text content."""
        data = VALID_FIXTURES["complete_answer_with_citations"].copy()
        data["answer"]["text"] = "x" * 10000  # 10k characters

        result = validate_answer_json(data)
        assert len(result.answer.text) == 10000

    def test_validate_with_nested_quotes(self) -> None:
        """Test validation with nested quotes in text."""
        data = VALID_FIXTURES["complete_answer_with_citations"].copy()
        data["answer"]["text"] = 'Text with "nested" and \'mixed\' quotes'

        result = validate_answer_json(data)
        assert "nested" in result.answer.text

    def test_validate_with_empty_unknowns_lists(self) -> None:
        """Test validation with all unknowns lists empty."""
        data = VALID_FIXTURES["complete_answer_with_citations"].copy()
        data["unknowns"] = {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        }

        result = validate_answer_json(data)
        assert len(result.unknowns.unsupported_claims) == 0

    def test_validate_with_maximum_sources(self) -> None:
        """Test validation with many sources."""
        data = VALID_FIXTURES["complete_answer_with_citations"].copy()

        # Create 10 sources
        sources = []
        for i in range(10):
            sources.append(
                {
                    "citation_label": f"Source {i}",
                    "canonical_url": f"https://example.com/source-{i}",
                    "source_org": f"Org {i}",
                    "year": 2000 + i,
                    "content_type": "article",
                    "license": "CC-BY-4.0",
                    "namespace": "test",
                    "doc_id": f"doc_{i}",
                    "chunk_id": f"doc_{i}::chunk::1",
                }
            )

        # Add all sources to retrieval results
        results = []
        for i in range(10):
            results.append(
                {
                    "rank": i + 1,
                    "score": 0.9 - (i * 0.05),
                    "snippet": f"Content from source {i}",
                    "citation_label": f"Source {i}",
                    "canonical_url": f"https://example.com/source-{i}",
                    "doc_id": f"doc_{i}",
                    "chunk_id": f"doc_{i}::chunk::1",
                    "namespace": "test",
                }
            )

        data["sources"] = sources
        data["retrieval_summary"]["results"] = results

        result = validate_answer_json(data)
        assert len(result.sources) == 10
