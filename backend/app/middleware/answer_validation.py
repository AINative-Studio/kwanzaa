"""Middleware for validating answer_json responses.

This middleware enforces that all responses returning answer_json contract
conform to the schema, preventing raw text blobs from reaching the UI.

It provides:
- Automatic validation for endpoints with answer_json response models
- Error logging via AIKit observability
- Development vs production error handling
- 422 status codes for validation errors with detailed messages
"""

import json
import time
from typing import Callable, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.middleware.observability import track_validation_event
from app.utils.answer_validation import AnswerValidationError, is_valid_answer_json


class AnswerJsonValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate answer_json responses.

    This middleware intercepts responses and validates them against the
    answer_json contract when appropriate. It ensures 100% compliance
    with the schema and provides detailed error messages when validation fails.
    """

    def __init__(
        self,
        app: ASGIApp,
        enabled: bool = True,
        log_all_validations: bool = False,
        strict_mode: bool = True,
    ):
        """Initialize validation middleware.

        Args:
            app: FastAPI application instance
            enabled: Whether validation is enabled
            log_all_validations: Log all validation attempts (not just failures)
            strict_mode: Raise errors in production (True) or log warnings (False)
        """
        super().__init__(app)
        self.enabled = enabled
        self.log_all_validations = log_all_validations
        self.strict_mode = strict_mode

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and validate response if needed.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint handler

        Returns:
            HTTP response (validated or error response)
        """
        if not self.enabled:
            return await call_next(request)

        # Get the response
        start_time = time.time()
        response = await call_next(request)
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Only validate JSON responses with 200 status
        if (
            response.status_code == status.HTTP_200_OK
            and response.headers.get("content-type", "").startswith("application/json")
        ):
            # Check if this endpoint should return answer_json
            if self._should_validate_endpoint(request.url.path):
                response = await self._validate_response(
                    request, response, processing_time_ms
                )

        return response

    def _should_validate_endpoint(self, path: str) -> bool:
        """Determine if an endpoint should have answer_json validation.

        Args:
            path: Request URL path

        Returns:
            True if validation should be applied
        """
        # Validate endpoints that return answer_json
        # This can be extended with route metadata or decorator-based detection
        answer_json_endpoints = [
            "/api/v1/rag/query",
            "/api/v1/rag/stream",
            "/api/v1/chat/message",
        ]

        return any(path.startswith(endpoint) for endpoint in answer_json_endpoints)

    async def _validate_response(
        self, request: Request, response: Response, processing_time_ms: int
    ) -> Response:
        """Validate response body against answer_json schema.

        Args:
            request: Original request
            response: Response to validate
            processing_time_ms: Request processing time

        Returns:
            Original response if valid, or error response if invalid
        """
        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            # Parse JSON
            data = json.loads(body)

            # Validate against answer_json schema
            if not is_valid_answer_json(data):
                # Get detailed validation errors
                from app.utils.answer_validation import get_validation_errors
                errors = get_validation_errors(data)

                # Track validation failure
                await track_validation_event(
                    request=request,
                    success=False,
                    errors=errors,
                    processing_time_ms=processing_time_ms,
                )

                # Return validation error response
                return self._create_validation_error_response(
                    request=request,
                    errors=errors,
                )

            # Validation successful
            if self.log_all_validations:
                await track_validation_event(
                    request=request,
                    success=True,
                    errors=[],
                    processing_time_ms=processing_time_ms,
                )

            # Return original response with body
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except json.JSONDecodeError as e:
            # Invalid JSON - this shouldn't happen but handle gracefully
            await track_validation_event(
                request=request,
                success=False,
                errors=[],
                processing_time_ms=processing_time_ms,
                additional_info={"json_error": str(e)},
            )

            return self._create_json_error_response(request, str(e))

        except Exception as e:
            # Unexpected error during validation
            await track_validation_event(
                request=request,
                success=False,
                errors=[],
                processing_time_ms=processing_time_ms,
                additional_info={"unexpected_error": str(e)},
            )

            # In production, log but don't break the response flow
            if not self.strict_mode:
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

            return self._create_internal_error_response(request, str(e))

    def _create_validation_error_response(
        self, request: Request, errors: list
    ) -> JSONResponse:
        """Create a 422 validation error response.

        Args:
            request: Original request
            errors: List of validation errors

        Returns:
            JSONResponse with validation errors
        """
        error_details = []
        for error in errors:
            error_details.append({
                "field": error.field,
                "message": error.message,
                "error_type": error.error_type,
                "location": error.location,
            })

        content = {
            "status": "error",
            "error_code": "ANSWER_JSON_VALIDATION_FAILED",
            "message": "Response does not conform to answer_json contract",
            "details": {
                "validation_errors": error_details,
                "error_count": len(errors),
                "suggestion": (
                    "Ensure the response includes all required fields: "
                    "version, answer, sources, retrieval_summary, unknowns"
                ),
            },
        }

        request_id = request.headers.get("X-Request-ID")
        if request_id:
            content["request_id"] = request_id

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=content,
        )

    def _create_json_error_response(
        self, request: Request, error_message: str
    ) -> JSONResponse:
        """Create error response for JSON parsing failures.

        Args:
            request: Original request
            error_message: Error message from JSON decoder

        Returns:
            JSONResponse with error
        """
        content = {
            "status": "error",
            "error_code": "INVALID_JSON_RESPONSE",
            "message": "Response body is not valid JSON",
            "details": {"error": error_message},
        }

        request_id = request.headers.get("X-Request-ID")
        if request_id:
            content["request_id"] = request_id

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )

    def _create_internal_error_response(
        self, request: Request, error_message: str
    ) -> JSONResponse:
        """Create error response for unexpected validation errors.

        Args:
            request: Original request
            error_message: Error message

        Returns:
            JSONResponse with error
        """
        content = {
            "status": "error",
            "error_code": "VALIDATION_MIDDLEWARE_ERROR",
            "message": "An error occurred while validating the response",
            "details": {"error": error_message if settings.DEBUG else "Internal error"},
        }

        request_id = request.headers.get("X-Request-ID")
        if request_id:
            content["request_id"] = request_id

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )
