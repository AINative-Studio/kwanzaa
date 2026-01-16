"""Error handling and custom exceptions."""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class APIError(Exception):
    """Base class for API errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize API error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class InvalidRequestError(APIError):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="INVALID_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnauthorizedError(APIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(APIError):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundError(APIError):
    """Raised when resource is not found."""

    def __init__(self, message: str, resource_type: Optional[str] = None) -> None:
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after_seconds: int = 60) -> None:
        super().__init__(
            message=f"Rate limit exceeded. Please try again in {retry_after_seconds} seconds.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after_seconds": retry_after_seconds},
        )


class ServiceUnavailableError(APIError):
    """Raised when external service is unavailable."""

    def __init__(self, service_name: str, message: Optional[str] = None) -> None:
        super().__init__(
            message=message or f"{service_name} service is temporarily unavailable",
            error_code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service_name},
        )


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """Create a standardized error response.

    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        request_id: Request ID for tracing

    Returns:
        JSONResponse with error information
    """
    content = {
        "status": "error",
        "error_code": error_code,
        "message": message,
    }

    if details:
        content["details"] = details

    if request_id:
        content["request_id"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle APIError exceptions.

    Args:
        request: FastAPI request
        exc: APIError exception

    Returns:
        JSON error response
    """
    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        request_id=request.headers.get("X-Request-ID"),
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: ValidationError exception

    Returns:
        JSON error response
    """
    errors = exc.errors()
    details = {
        "validation_errors": [
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in errors
        ]
    }

    return create_error_response(
        error_code="INVALID_REQUEST",
        message="Request validation failed",
        status_code=status.HTTP_400_BAD_REQUEST,
        details=details,
        request_id=request.headers.get("X-Request-ID"),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException.

    Args:
        request: FastAPI request
        exc: HTTPException

    Returns:
        JSON error response
    """
    # Map HTTP status codes to error codes
    error_code_map = {
        400: "INVALID_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }

    error_code = error_code_map.get(exc.status_code, "UNKNOWN_ERROR")

    return create_error_response(
        error_code=error_code,
        message=str(exc.detail),
        status_code=exc.status_code,
        request_id=request.headers.get("X-Request-ID"),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON error response
    """
    # Log the exception here in production
    print(f"Unexpected error: {type(exc).__name__}: {str(exc)}")

    return create_error_response(
        error_code="INTERNAL_ERROR",
        message="An internal error occurred while processing your request",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request.headers.get("X-Request-ID"),
    )
