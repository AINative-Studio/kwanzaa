"""Unit tests for response enforcement utilities.

This module tests the decorators and utilities for enforcing
answer_json compliance at the route level.
"""

import pytest
from fastapi import HTTPException

from app.utils.response_enforcement import (
    enforce_answer_json_response,
    validate_and_convert_response,
    create_validation_error_response,
    AnswerJsonResponseValidator,
)
from app.utils.answer_validation import AnswerValidationError, ValidationErrorDetail


class TestEnforceAnswerJsonResponse:
    """Tests for enforce_answer_json_response decorator."""

    @pytest.fixture
    def valid_response_dict(self) -> dict:
        """Create a valid response dictionary."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": False,
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

    @pytest.mark.asyncio
    async def test_decorator_with_valid_async_response(self, valid_response_dict):
        """Test decorator with valid async function response."""
        @enforce_answer_json_response()
        async def mock_endpoint() -> dict:
            return valid_response_dict

        result = await mock_endpoint()
        assert isinstance(result, dict)
        assert result["version"] == "kwanzaa.answer.v1"

    def test_decorator_with_valid_sync_response(self, valid_response_dict):
        """Test decorator with valid sync function response."""
        @enforce_answer_json_response()
        def mock_endpoint() -> dict:
            return valid_response_dict

        result = mock_endpoint()
        assert isinstance(result, dict)
        assert result["version"] == "kwanzaa.answer.v1"

    @pytest.mark.asyncio
    async def test_decorator_with_invalid_async_response_strict(self):
        """Test decorator with invalid async response in strict mode."""
        @enforce_answer_json_response(strict=True)
        async def mock_endpoint() -> dict:
            return {"invalid": "response"}

        with pytest.raises(HTTPException) as exc_info:
            await mock_endpoint()

        assert exc_info.value.status_code == 422
        assert "ANSWER_JSON_VALIDATION_FAILED" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_decorator_with_invalid_async_response_non_strict(self):
        """Test decorator with invalid async response in non-strict mode."""
        @enforce_answer_json_response(strict=False)
        async def mock_endpoint() -> dict:
            return {"invalid": "response"}

        # Should not raise, just return the original response
        result = await mock_endpoint()
        assert result == {"invalid": "response"}

    @pytest.mark.asyncio
    async def test_decorator_with_non_dict_response(self):
        """Test decorator with non-dict response."""
        @enforce_answer_json_response()
        async def mock_endpoint() -> str:
            return "not a dict"

        # Should return as-is for non-dict responses
        result = await mock_endpoint()
        assert result == "not a dict"


class TestValidateAndConvertResponse:
    """Tests for validate_and_convert_response function."""

    @pytest.fixture
    def valid_response_dict(self) -> dict:
        """Create a valid response dictionary."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": False,
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

    def test_validate_and_convert_valid_response(self, valid_response_dict):
        """Test validating and converting valid response."""
        result = validate_and_convert_response(valid_response_dict)

        assert result is not None
        assert result.version == "kwanzaa.answer.v1"
        assert result.persona.value == "educator"

    def test_validate_and_convert_invalid_response_raise(self):
        """Test validating invalid response with raise_on_error=True."""
        with pytest.raises(AnswerValidationError):
            validate_and_convert_response({"invalid": "data"}, raise_on_error=True)

    def test_validate_and_convert_invalid_response_no_raise(self):
        """Test validating invalid response with raise_on_error=False."""
        result = validate_and_convert_response(
            {"invalid": "data"},
            raise_on_error=False,
        )

        assert result is None


class TestCreateValidationErrorResponse:
    """Tests for create_validation_error_response function."""

    def test_create_error_response_without_raw_data(self):
        """Test creating error response without raw data."""
        errors = [
            ValidationErrorDetail(
                field="version",
                message="Field required",
                error_type="missing",
                location=["version"],
            )
        ]

        validation_error = AnswerValidationError(
            message="Validation failed",
            errors=errors,
        )

        response = create_validation_error_response(
            validation_error,
            include_raw_data=False,
        )

        assert response["status"] == "error"
        assert response["error_code"] == "ANSWER_JSON_VALIDATION_FAILED"
        assert response["message"] == "Validation failed"
        assert len(response["details"]["validation_errors"]) == 1
        assert "raw_data" not in response

    def test_create_error_response_with_raw_data(self):
        """Test creating error response with raw data."""
        raw_data = {"invalid": "data"}
        errors = [
            ValidationErrorDetail(
                field="version",
                message="Field required",
                error_type="missing",
                location=["version"],
            )
        ]

        validation_error = AnswerValidationError(
            message="Validation failed",
            errors=errors,
            raw_data=raw_data,
        )

        response = create_validation_error_response(
            validation_error,
            include_raw_data=True,
        )

        assert "raw_data" in response
        assert response["raw_data"] == raw_data

    def test_create_error_response_with_suggestions(self):
        """Test that error response includes suggestions."""
        errors = [
            ValidationErrorDetail(
                field="version",
                message="Invalid pattern",
                error_type="value_error",
                location=["version"],
            )
        ]

        validation_error = AnswerValidationError(
            message="Validation failed",
            errors=errors,
        )

        response = create_validation_error_response(validation_error)

        assert "suggestions" in response["details"]
        assert len(response["details"]["suggestions"]) > 0


class TestAnswerJsonResponseValidator:
    """Tests for AnswerJsonResponseValidator class."""

    @pytest.fixture
    def valid_response_dict(self) -> dict:
        """Create a valid response dictionary."""
        return {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": False,
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

    def test_validate_single_response(self, valid_response_dict):
        """Test validating a single response."""
        validator = AnswerJsonResponseValidator()
        result = validator.validate_response(valid_response_dict)

        assert result is not None
        assert result.version == "kwanzaa.answer.v1"

    def test_validate_single_response_strict_failure(self):
        """Test validating invalid response with strict=True."""
        validator = AnswerJsonResponseValidator()

        with pytest.raises(AnswerValidationError):
            validator.validate_response({"invalid": "data"}, strict=True)

    def test_validate_single_response_non_strict_failure(self):
        """Test validating invalid response with strict=False."""
        validator = AnswerJsonResponseValidator()
        result = validator.validate_response({"invalid": "data"}, strict=False)

        assert result is None

    def test_validate_batch_all_valid(self, valid_response_dict):
        """Test validating batch of all valid responses."""
        validator = AnswerJsonResponseValidator()
        responses = [valid_response_dict, valid_response_dict.copy()]

        valid, errors = validator.validate_batch(responses)

        assert len(valid) == 2
        assert len(errors) == 0

    def test_validate_batch_mixed(self, valid_response_dict):
        """Test validating batch with mixed valid/invalid responses."""
        validator = AnswerJsonResponseValidator()
        responses = [valid_response_dict, {"invalid": "data"}]

        valid, errors = validator.validate_batch(responses)

        assert len(valid) == 1
        assert len(errors) == 1

    def test_validate_batch_fail_fast(self, valid_response_dict):
        """Test validating batch with fail_fast=True."""
        validator = AnswerJsonResponseValidator()
        responses = [valid_response_dict, {"invalid": "data"}]

        with pytest.raises(AnswerValidationError):
            validator.validate_batch(responses, fail_fast=True)

    def test_validate_streaming_chunk_intermediate(self):
        """Test validating intermediate streaming chunk."""
        validator = AnswerJsonResponseValidator()
        chunk = {"version": "kwanzaa.answer.v1", "answer": {"text": "partial"}}

        result = validator.validate_streaming_chunk(chunk, is_final_chunk=False)
        assert result is True

    def test_validate_streaming_chunk_final(self, valid_response_dict):
        """Test validating final streaming chunk."""
        validator = AnswerJsonResponseValidator()

        result = validator.validate_streaming_chunk(
            valid_response_dict,
            is_final_chunk=True,
        )
        assert result is True

    def test_validate_streaming_chunk_final_invalid(self):
        """Test validating invalid final streaming chunk."""
        validator = AnswerJsonResponseValidator()

        result = validator.validate_streaming_chunk(
            {"invalid": "data"},
            is_final_chunk=True,
        )
        assert result is False

    def test_attempt_error_recovery_missing_unknowns(self):
        """Test recovering from missing unknowns section."""
        validator = AnswerJsonResponseValidator()
        invalid_response = {
            "version": "kwanzaa.answer.v1",
            "persona": "educator",
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": False,
                "primary_sources_only": False,
                "creative_mode": False,
            },
            "answer": {
                "text": "Test",
                "confidence": 0.9,
                "tone": "neutral",
                "completeness": "complete",
            },
            "sources": [],
            "retrieval_summary": {
                "query": "test",
                "top_k": 5,
                "namespaces": ["default"],
                "results": [],
            },
            # Missing unknowns section
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

        result = validator.attempt_error_recovery(invalid_response)

        # Should successfully recover
        assert result is not None
        assert result.unknowns.unsupported_claims == []

    def test_attempt_error_recovery_unrecoverable(self):
        """Test recovery attempt on unrecoverable error."""
        validator = AnswerJsonResponseValidator()
        invalid_response = {"invalid": "data"}

        result = validator.attempt_error_recovery(invalid_response)

        # Should fail to recover
        assert result is None
