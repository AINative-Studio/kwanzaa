"""Response model enforcement utilities for answer_json compliance.

This module provides decorators and utilities for enforcing answer_json
schema compliance at the route level, ensuring that all responses conform
to the contract.

Features:
- FastAPI response_model enforcement
- Decorator-based validation
- Automatic error handling for non-compliant responses
- Integration with validation middleware
"""

from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from fastapi import HTTPException, Response, status
from pydantic import ValidationError

from app.models.answer_json import AnswerJsonContract
from app.utils.answer_validation import (
    AnswerValidationError,
    validate_answer_json,
)

T = TypeVar("T")


def enforce_answer_json_response(
    strict: bool = True,
    log_failures: bool = True,
) -> Callable:
    """Decorator to enforce answer_json response compliance.

    This decorator wraps endpoint functions to ensure their return values
    conform to the answer_json contract. It validates the response before
    returning and raises appropriate HTTP exceptions for invalid responses.

    Args:
        strict: If True, raise 422 on validation failure. If False, log and continue.
        log_failures: Whether to log validation failures

    Returns:
        Decorator function

    Example:
        @router.post("/rag/query", response_model=AnswerJsonContract)
        @enforce_answer_json_response()
        async def query_rag(request: QueryRequest) -> dict:
            # Generate response
            return response_dict
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Call the original function
            result = await func(*args, **kwargs)

            # Validate if result is a dict
            if isinstance(result, dict):
                try:
                    # Validate against answer_json schema
                    validated = validate_answer_json(result)
                    # Return the validated model (FastAPI will serialize it)
                    return validated.model_dump(mode="json")

                except AnswerValidationError as e:
                    if log_failures:
                        # Log the validation failure
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(
                            f"answer_json validation failed: {e.message}",
                            extra={
                                "errors": [err.to_dict() for err in e.errors],
                                "endpoint": func.__name__,
                            },
                        )

                    if strict:
                        # Raise 422 with detailed validation errors
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail={
                                "error_code": "ANSWER_JSON_VALIDATION_FAILED",
                                "message": e.message,
                                "errors": [err.to_dict() for err in e.errors],
                            },
                        ) from e

            # If not dict or not strict, return as-is
            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Call the original function
            result = func(*args, **kwargs)

            # Validate if result is a dict
            if isinstance(result, dict):
                try:
                    # Validate against answer_json schema
                    validated = validate_answer_json(result)
                    # Return the validated model (FastAPI will serialize it)
                    return validated.model_dump(mode="json")

                except AnswerValidationError as e:
                    if log_failures:
                        # Log the validation failure
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(
                            f"answer_json validation failed: {e.message}",
                            extra={
                                "errors": [err.to_dict() for err in e.errors],
                                "endpoint": func.__name__,
                            },
                        )

                    if strict:
                        # Raise 422 with detailed validation errors
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail={
                                "error_code": "ANSWER_JSON_VALIDATION_FAILED",
                                "message": e.message,
                                "errors": [err.to_dict() for err in e.errors],
                            },
                        ) from e

            # If not dict or not strict, return as-is
            return result

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def validate_and_convert_response(
    response_data: dict,
    raise_on_error: bool = True,
) -> Optional[AnswerJsonContract]:
    """Validate response data and convert to AnswerJsonContract model.

    Args:
        response_data: Dictionary containing response data
        raise_on_error: Whether to raise exception on validation failure

    Returns:
        AnswerJsonContract instance if valid, None if invalid and raise_on_error=False

    Raises:
        AnswerValidationError: If validation fails and raise_on_error=True
    """
    try:
        return validate_answer_json(response_data)
    except AnswerValidationError as e:
        if raise_on_error:
            raise
        return None


def create_validation_error_response(
    validation_error: AnswerValidationError,
    include_raw_data: bool = False,
) -> dict:
    """Create a standardized validation error response.

    Args:
        validation_error: The validation error
        include_raw_data: Whether to include raw data in response (for debugging)

    Returns:
        Dictionary with error information
    """
    response = {
        "status": "error",
        "error_code": "ANSWER_JSON_VALIDATION_FAILED",
        "message": validation_error.message,
        "details": {
            "validation_errors": [err.to_dict() for err in validation_error.errors],
            "error_count": len(validation_error.errors),
            "suggestions": _get_validation_suggestions(validation_error.errors),
        },
    }

    if include_raw_data and validation_error.raw_data:
        response["raw_data"] = validation_error.raw_data

    return response


def _get_validation_suggestions(errors: list) -> list[str]:
    """Generate helpful suggestions based on validation errors.

    Args:
        errors: List of ValidationErrorDetail objects

    Returns:
        List of suggestion strings
    """
    suggestions = []

    # Check for common error patterns
    error_fields = {error.field for error in errors}

    if "version" in error_fields:
        suggestions.append(
            "Ensure 'version' field follows pattern: kwanzaa.answer.v1"
        )

    if any("sources" in field for field in error_fields):
        suggestions.append(
            "Check that all sources have required fields: citation_label, "
            "canonical_url, source_org, year, content_type, license, "
            "namespace, doc_id, chunk_id"
        )

    if any("retrieval_summary" in field for field in error_fields):
        suggestions.append(
            "Ensure retrieval_summary includes: query, top_k, namespaces, results"
        )

    if any("unknowns" in field for field in error_fields):
        suggestions.append(
            "The 'unknowns' section must include: unsupported_claims, "
            "missing_context, clarifying_questions (can be empty arrays)"
        )

    if not suggestions:
        suggestions.append(
            "Review the answer_json schema at: "
            "backend/app/schemas/answer_json.schema.json"
        )

    return suggestions


class AnswerJsonResponseValidator:
    """Utility class for validating answer_json responses.

    This class provides methods for validating responses in different contexts,
    including batch validation, streaming validation, and error recovery.
    """

    @staticmethod
    def validate_response(
        response_data: dict,
        strict: bool = True,
    ) -> Optional[AnswerJsonContract]:
        """Validate a single response.

        Args:
            response_data: Response dictionary
            strict: Whether to raise on validation failure

        Returns:
            Validated AnswerJsonContract or None

        Raises:
            AnswerValidationError: If strict=True and validation fails
        """
        return validate_and_convert_response(response_data, raise_on_error=strict)

    @staticmethod
    def validate_batch(
        responses: list[dict],
        fail_fast: bool = False,
    ) -> tuple[list[AnswerJsonContract], list[tuple[int, AnswerValidationError]]]:
        """Validate multiple responses.

        Args:
            responses: List of response dictionaries
            fail_fast: Stop on first validation error

        Returns:
            Tuple of (valid_responses, errors)
            - valid_responses: List of validated AnswerJsonContract instances
            - errors: List of tuples (index, error)
        """
        from app.utils.answer_validation import validate_multiple_responses

        valid, errors = validate_multiple_responses(responses)

        if fail_fast and errors:
            # Raise the first error
            _, error = errors[0]
            raise error

        return valid, errors

    @staticmethod
    def validate_streaming_chunk(
        chunk_data: dict,
        is_final_chunk: bool = False,
    ) -> bool:
        """Validate a streaming response chunk.

        For streaming responses, we only fully validate the final chunk.
        Intermediate chunks are checked for basic structure.

        Args:
            chunk_data: Chunk data dictionary
            is_final_chunk: Whether this is the final chunk

        Returns:
            True if valid, False otherwise
        """
        if is_final_chunk:
            # Validate complete response
            try:
                validate_answer_json(chunk_data)
                return True
            except AnswerValidationError:
                return False
        else:
            # For intermediate chunks, just check basic structure
            # This allows incremental building of the response
            required_keys = {"version", "answer"}
            return all(key in chunk_data for key in required_keys)

    @staticmethod
    def attempt_error_recovery(
        invalid_response: dict,
    ) -> Optional[AnswerJsonContract]:
        """Attempt to recover from validation errors by fixing common issues.

        This method attempts to fix common validation issues automatically,
        such as missing empty arrays or default values.

        Args:
            invalid_response: The invalid response dictionary

        Returns:
            Validated AnswerJsonContract if recovery successful, None otherwise
        """
        # Make a copy to avoid mutating the original
        response = invalid_response.copy()

        # Fix missing unknowns fields
        if "unknowns" not in response:
            response["unknowns"] = {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": [],
            }
        elif isinstance(response["unknowns"], dict):
            unknowns = response["unknowns"]
            if "unsupported_claims" not in unknowns:
                unknowns["unsupported_claims"] = []
            if "missing_context" not in unknowns:
                unknowns["missing_context"] = []
            if "clarifying_questions" not in unknowns:
                unknowns["clarifying_questions"] = []

        # Fix missing sources array
        if "sources" not in response:
            response["sources"] = []

        # Try to validate the fixed response
        try:
            return validate_answer_json(response)
        except AnswerValidationError:
            # Recovery failed
            return None
