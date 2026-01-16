"""Validation utilities for answer_json contract compliance.

This module provides validation functions and error handling for ensuring
all AI responses conform to the answer_json schema. It enforces the principle
that the UI should never render raw text blobs.

Usage:
    from app.utils.answer_validation import validate_answer_json

    try:
        validated_response = validate_answer_json(response_data)
        # Use validated_response with confidence
    except AnswerValidationError as e:
        # Handle validation errors
        logger.error(f"Validation failed: {e.message}")
        for detail in e.errors:
            logger.error(f"  - {detail.field}: {detail.message}")
"""

from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.models.answer_json import AnswerJsonContract


class ValidationErrorDetail:
    """Detailed validation error information."""

    def __init__(self, field: str, message: str, error_type: str, location: List[str]):
        """Initialize validation error detail.

        Args:
            field: The field that failed validation
            message: Human-readable error message
            error_type: Type of validation error
            location: Location path to the error
        """
        self.field = field
        self.message = message
        self.error_type = error_type
        self.location = location

    def __repr__(self) -> str:
        """String representation of error detail."""
        return f"ValidationErrorDetail(field={self.field}, message={self.message})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "field": self.field,
            "message": self.message,
            "error_type": self.error_type,
            "location": self.location,
        }


class AnswerValidationError(Exception):
    """Exception raised when answer_json validation fails.

    This exception provides detailed information about validation failures
    to help debug and fix non-compliant responses.
    """

    def __init__(
        self,
        message: str,
        errors: List[ValidationErrorDetail],
        raw_data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize validation error.

        Args:
            message: High-level error message
            errors: List of detailed validation errors
            raw_data: The raw data that failed validation (optional)
        """
        super().__init__(message)
        self.message = message
        self.errors = errors
        self.raw_data = raw_data

    def __str__(self) -> str:
        """String representation of validation error."""
        error_summary = "\n".join([f"  - {e.field}: {e.message}" for e in self.errors])
        return f"{self.message}\nValidation errors:\n{error_summary}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for API responses."""
        return {
            "message": self.message,
            "errors": [error.to_dict() for error in self.errors],
            "error_count": len(self.errors),
        }


def _parse_pydantic_errors(validation_error: ValidationError) -> List[ValidationErrorDetail]:
    """Parse Pydantic validation errors into our error format.

    Args:
        validation_error: Pydantic ValidationError

    Returns:
        List of ValidationErrorDetail objects
    """
    error_details: List[ValidationErrorDetail] = []

    for error in validation_error.errors():
        location = error.get("loc", [])
        field = ".".join(str(loc) for loc in location)
        message = error.get("msg", "Unknown validation error")
        error_type = error.get("type", "unknown")

        error_details.append(
            ValidationErrorDetail(
                field=field,
                message=message,
                error_type=error_type,
                location=[str(loc) for loc in location],
            )
        )

    return error_details


def validate_answer_json(data: Dict[str, Any]) -> AnswerJsonContract:
    """Validate a dictionary against the answer_json schema.

    This is the primary validation function that should be used to ensure
    all AI responses conform to the contract.

    Args:
        data: Dictionary containing the response data

    Returns:
        Validated AnswerJsonContract instance

    Raises:
        AnswerValidationError: If validation fails

    Example:
        >>> response = {"version": "kwanzaa.answer.v1", ...}
        >>> validated = validate_answer_json(response)
        >>> print(validated.answer.text)
    """
    if not isinstance(data, dict):
        raise AnswerValidationError(
            message="Input must be a dictionary",
            errors=[
                ValidationErrorDetail(
                    field="__root__",
                    message=f"Expected dict, got {type(data).__name__}",
                    error_type="type_error",
                    location=["__root__"],
                )
            ],
            raw_data=None,
        )

    try:
        # Attempt to parse and validate using Pydantic
        return AnswerJsonContract.model_validate(data)
    except ValidationError as e:
        # Convert Pydantic errors to our custom error format
        error_details = _parse_pydantic_errors(e)
        raise AnswerValidationError(
            message="answer_json validation failed",
            errors=error_details,
            raw_data=data,
        ) from e


def validate_answer_json_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and return the data as a dictionary.

    This is useful when you need to validate but don't need the Pydantic model.

    Args:
        data: Dictionary containing the response data

    Returns:
        Validated dictionary (same as input if valid)

    Raises:
        AnswerValidationError: If validation fails
    """
    validated = validate_answer_json(data)
    return validated.model_dump()


def is_valid_answer_json(data: Dict[str, Any]) -> bool:
    """Check if data is valid answer_json without raising exceptions.

    Args:
        data: Dictionary to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> if is_valid_answer_json(response):
        ...     process_response(response)
        ... else:
        ...     handle_invalid_response(response)
    """
    try:
        validate_answer_json(data)
        return True
    except AnswerValidationError:
        return False


def get_validation_errors(data: Dict[str, Any]) -> List[ValidationErrorDetail]:
    """Get validation errors without raising exceptions.

    Args:
        data: Dictionary to validate

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = get_validation_errors(response)
        >>> if errors:
        ...     for error in errors:
        ...         print(f"{error.field}: {error.message}")
    """
    try:
        validate_answer_json(data)
        return []
    except AnswerValidationError as e:
        return e.errors


def validate_multiple_responses(
    responses: List[Dict[str, Any]],
) -> tuple[List[AnswerJsonContract], List[tuple[int, AnswerValidationError]]]:
    """Validate multiple responses and return both successes and failures.

    Args:
        responses: List of response dictionaries to validate

    Returns:
        Tuple of (valid_responses, errors)
        - valid_responses: List of validated AnswerJsonContract instances
        - errors: List of tuples (index, error) for failed validations

    Example:
        >>> valid, invalid = validate_multiple_responses(batch_responses)
        >>> print(f"Valid: {len(valid)}, Invalid: {len(invalid)}")
    """
    valid_responses: List[AnswerJsonContract] = []
    errors: List[tuple[int, AnswerValidationError]] = []

    for idx, response in enumerate(responses):
        try:
            validated = validate_answer_json(response)
            valid_responses.append(validated)
        except AnswerValidationError as e:
            errors.append((idx, e))

    return valid_responses, errors
