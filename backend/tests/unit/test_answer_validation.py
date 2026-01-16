"""Unit tests for answer_json validation utilities.

This module provides comprehensive test coverage for the validation
utilities, ensuring 100% compliance enforcement.
"""

import pytest
from datetime import datetime, timezone

from app.utils.answer_validation import (
    AnswerValidationError,
    ValidationErrorDetail,
    validate_answer_json,
    validate_answer_json_dict,
    is_valid_answer_json,
    get_validation_errors,
    validate_multiple_responses,
)


class TestValidationErrorDetail:
    """Tests for ValidationErrorDetail class."""

    def test_create_error_detail(self):
        """Test creating a validation error detail."""
        error = ValidationErrorDetail(
            field="answer.text",
            message="Field required",
            error_type="missing",
            location=["answer", "text"],
        )

        assert error.field == "answer.text"
        assert error.message == "Field required"
        assert error.error_type == "missing"
        assert error.location == ["answer", "text"]

    def test_error_detail_to_dict(self):
        """Test converting error detail to dictionary."""
        error = ValidationErrorDetail(
            field="version",
            message="Invalid pattern",
            error_type="value_error",
            location=["version"],
        )

        error_dict = error.to_dict()
        assert error_dict == {
            "field": "version",
            "message": "Invalid pattern",
            "error_type": "value_error",
            "location": ["version"],
        }

    def test_error_detail_repr(self):
        """Test string representation of error detail."""
        error = ValidationErrorDetail(
            field="sources",
            message="Expected array",
            error_type="type_error",
            location=["sources"],
        )

        repr_str = repr(error)
        assert "sources" in repr_str
        assert "Expected array" in repr_str


class TestAnswerValidationError:
    """Tests for AnswerValidationError exception."""

    def test_create_validation_error(self):
        """Test creating a validation error."""
        errors = [
            ValidationErrorDetail(
                field="answer.text",
                message="Field required",
                error_type="missing",
                location=["answer", "text"],
            )
        ]

        exc = AnswerValidationError(
            message="Validation failed",
            errors=errors,
            raw_data={"version": "kwanzaa.answer.v1"},
        )

        assert exc.message == "Validation failed"
        assert len(exc.errors) == 1
        assert exc.raw_data is not None

    def test_validation_error_str(self):
        """Test string representation of validation error."""
        errors = [
            ValidationErrorDetail(
                field="version",
                message="Invalid pattern",
                error_type="value_error",
                location=["version"],
            )
        ]

        exc = AnswerValidationError(message="Validation failed", errors=errors)

        error_str = str(exc)
        assert "Validation failed" in error_str
        assert "version" in error_str
        assert "Invalid pattern" in error_str

    def test_validation_error_to_dict(self):
        """Test converting validation error to dictionary."""
        errors = [
            ValidationErrorDetail(
                field="sources",
                message="Expected array",
                error_type="type_error",
                location=["sources"],
            )
        ]

        exc = AnswerValidationError(message="Validation failed", errors=errors)

        error_dict = exc.to_dict()
        assert error_dict["message"] == "Validation failed"
        assert error_dict["error_count"] == 1
        assert len(error_dict["errors"]) == 1


class TestValidateAnswerJson:
    """Tests for validate_answer_json function."""

    @pytest.fixture
    def valid_answer_json(self) -> dict:
        """Create a valid answer_json response."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "The Civil Rights Act of 1964 was landmark legislation.",
                "confidence": 0.92,
                "tone": "neutral",
                "completeness": "complete",
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
                "filters": {},
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

    def test_validate_valid_response(self, valid_answer_json):
        """Test validating a valid response."""
        result = validate_answer_json(valid_answer_json)

        assert result.version == "kwanzaa.answer.v1"
        assert result.persona.value == "educator"
        assert result.answer.text == "The Civil Rights Act of 1964 was landmark legislation."
        assert len(result.sources) == 1
        assert len(result.retrieval_summary.results) == 1

    def test_validate_invalid_type(self):
        """Test validation with non-dict input."""
        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json("not a dict")

        assert "Expected dict" in str(exc_info.value)

    def test_validate_missing_required_field(self, valid_answer_json):
        """Test validation with missing required field."""
        invalid_response = valid_answer_json.copy()
        del invalid_response["version"]

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(invalid_response)

        assert any(
            "version" in err.field for err in exc_info.value.errors
        )

    def test_validate_invalid_version_pattern(self, valid_answer_json):
        """Test validation with invalid version pattern."""
        invalid_response = valid_answer_json.copy()
        invalid_response["version"] = "invalid_version"

        with pytest.raises(AnswerValidationError):
            validate_answer_json(invalid_response)

    def test_validate_empty_answer_text(self, valid_answer_json):
        """Test validation with empty answer text."""
        invalid_response = valid_answer_json.copy()
        invalid_response["answer"]["text"] = ""

        with pytest.raises(AnswerValidationError):
            validate_answer_json(invalid_response)

    def test_validate_invalid_confidence(self, valid_answer_json):
        """Test validation with invalid confidence value."""
        invalid_response = valid_answer_json.copy()
        invalid_response["answer"]["confidence"] = 1.5  # Out of range

        with pytest.raises(AnswerValidationError):
            validate_answer_json(invalid_response)

    def test_validate_missing_source_fields(self, valid_answer_json):
        """Test validation with missing source fields."""
        invalid_response = valid_answer_json.copy()
        invalid_response["sources"][0].pop("canonical_url")

        with pytest.raises(AnswerValidationError) as exc_info:
            validate_answer_json(invalid_response)

        assert any(
            "canonical_url" in err.field for err in exc_info.value.errors
        )

    def test_validate_invalid_url_format(self, valid_answer_json):
        """Test validation with invalid URL format."""
        invalid_response = valid_answer_json.copy()
        invalid_response["sources"][0]["canonical_url"] = "not-a-url"

        with pytest.raises(AnswerValidationError):
            validate_answer_json(invalid_response)

    def test_validate_missing_retrieval_summary(self, valid_answer_json):
        """Test validation with missing retrieval_summary."""
        invalid_response = valid_answer_json.copy()
        del invalid_response["retrieval_summary"]

        with pytest.raises(AnswerValidationError):
            validate_answer_json(invalid_response)

    def test_validate_empty_results_array(self, valid_answer_json):
        """Test validation with empty results array."""
        # This should be valid - results can be empty
        response = valid_answer_json.copy()
        response["retrieval_summary"]["results"] = []
        response["sources"] = []

        result = validate_answer_json(response)
        assert len(result.retrieval_summary.results) == 0


class TestValidateAnswerJsonDict:
    """Tests for validate_answer_json_dict function."""

    @pytest.fixture
    def valid_answer_json(self) -> dict:
        """Create a valid answer_json response."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "Test answer",
                "confidence": 0.9,
                "tone": "neutral",
                "completeness": "complete",
            },
            "sources": [],
            "retrieval_summary": {
                "query": "test query",
                "top_k": 5,
                "namespaces": ["default"],
                "results": [],
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": [],
            },
            "integrity": {
                "citation_required": False,
                "citations_provided": False,
                "retrieval_confidence": "high",
                "fallback_behavior": "not_needed",
            },
            "provenance": {
                "generated_at": "2026-02-03T18:42:11Z",
                "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
            },
        }

    def test_validate_and_return_dict(self, valid_answer_json):
        """Test validation returning dictionary."""
        result = validate_answer_json_dict(valid_answer_json)

        assert isinstance(result, dict)
        assert result["version"] == "kwanzaa.answer.v1"
        assert result["persona"] == "educator"

    def test_validate_dict_with_error(self):
        """Test validation with invalid dict."""
        with pytest.raises(AnswerValidationError):
            validate_answer_json_dict({"invalid": "data"})


class TestIsValidAnswerJson:
    """Tests for is_valid_answer_json function."""

    @pytest.fixture
    def valid_answer_json(self) -> dict:
        """Create a valid answer_json response."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "Test answer",
                "confidence": 0.9,
                "tone": "neutral",
                "completeness": "complete",
            },
            "sources": [],
            "retrieval_summary": {
                "query": "test query",
                "top_k": 5,
                "namespaces": ["default"],
                "results": [],
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": [],
            },
            "integrity": {
                "citation_required": False,
                "citations_provided": False,
                "retrieval_confidence": "high",
                "fallback_behavior": "not_needed",
            },
            "provenance": {
                "generated_at": "2026-02-03T18:42:11Z",
                "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
            },
        }

    def test_is_valid_with_valid_response(self, valid_answer_json):
        """Test is_valid_answer_json with valid response."""
        assert is_valid_answer_json(valid_answer_json) is True

    def test_is_valid_with_invalid_response(self):
        """Test is_valid_answer_json with invalid response."""
        assert is_valid_answer_json({"invalid": "data"}) is False

    def test_is_valid_with_non_dict(self):
        """Test is_valid_answer_json with non-dict input."""
        assert is_valid_answer_json("not a dict") is False


class TestGetValidationErrors:
    """Tests for get_validation_errors function."""

    def test_get_errors_for_valid_response(self):
        """Test getting errors for valid response."""
        valid_response = {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "Test answer",
                "confidence": 0.9,
                "tone": "neutral",
                "completeness": "complete",
            },
            "sources": [],
            "retrieval_summary": {
                "query": "test query",
                "top_k": 5,
                "namespaces": ["default"],
                "results": [],
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": [],
            },
            "integrity": {
                "citation_required": False,
                "citations_provided": False,
                "retrieval_confidence": "high",
                "fallback_behavior": "not_needed",
            },
            "provenance": {
                "generated_at": "2026-02-03T18:42:11Z",
                "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
            },
        }

        errors = get_validation_errors(valid_response)
        assert len(errors) == 0

    def test_get_errors_for_invalid_response(self):
        """Test getting errors for invalid response."""
        invalid_response = {"invalid": "data"}

        errors = get_validation_errors(invalid_response)
        assert len(errors) > 0


class TestValidateMultipleResponses:
    """Tests for validate_multiple_responses function."""

    @pytest.fixture
    def valid_response_1(self) -> dict:
        """Create first valid response."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "Response 1",
                "confidence": 0.9,
                "tone": "neutral",
                "completeness": "complete",
            },
            "sources": [],
            "retrieval_summary": {
                "query": "query 1",
                "top_k": 5,
                "namespaces": ["default"],
                "results": [],
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": [],
            },
            "integrity": {
                "citation_required": False,
                "citations_provided": False,
                "retrieval_confidence": "high",
                "fallback_behavior": "not_needed",
            },
            "provenance": {
                "generated_at": "2026-02-03T18:42:11Z",
                "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
            },
        }

    @pytest.fixture
    def valid_response_2(self) -> dict:
        """Create second valid response."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "researcher",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "Response 2",
                "confidence": 0.85,
                "tone": "formal",
                "completeness": "partial",
            },
            "sources": [],
            "retrieval_summary": {
                "query": "query 2",
                "top_k": 10,
                "namespaces": ["default"],
                "results": [],
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": [],
            },
            "integrity": {
                "citation_required": False,
                "citations_provided": False,
                "retrieval_confidence": "medium",
                "fallback_behavior": "not_needed",
            },
            "provenance": {
                "generated_at": "2026-02-03T18:42:11Z",
                "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
                "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e",
            },
        }

    def test_validate_all_valid_responses(self, valid_response_1, valid_response_2):
        """Test validating multiple valid responses."""
        valid, errors = validate_multiple_responses([valid_response_1, valid_response_2])

        assert len(valid) == 2
        assert len(errors) == 0

    def test_validate_mixed_responses(self, valid_response_1):
        """Test validating mix of valid and invalid responses."""
        invalid_response = {"invalid": "data"}

        valid, errors = validate_multiple_responses([valid_response_1, invalid_response])

        assert len(valid) == 1
        assert len(errors) == 1
        assert errors[0][0] == 1  # Index of invalid response

    def test_validate_all_invalid_responses(self):
        """Test validating all invalid responses."""
        invalid_1 = {"invalid": "data1"}
        invalid_2 = {"invalid": "data2"}

        valid, errors = validate_multiple_responses([invalid_1, invalid_2])

        assert len(valid) == 0
        assert len(errors) == 2

    def test_validate_empty_list(self):
        """Test validating empty list."""
        valid, errors = validate_multiple_responses([])

        assert len(valid) == 0
        assert len(errors) == 0
