"""AIKit observability integration for validation tracking.

This module provides integration with @ainative/ai-kit-observability
for tracking validation events, metrics, and compliance over time.

Features:
- Track validation success/failure rates
- Log common validation errors
- Monitor response compliance trends
- Alert on validation issues
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import Request

from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)


class AIKitObservabilityClient:
    """Client for AIKit observability tracking.

    This is a placeholder implementation that logs to standard logging.
    Replace with actual @ainative/ai-kit-observability SDK integration.
    """

    def __init__(self, enabled: bool = True):
        """Initialize observability client.

        Args:
            enabled: Whether observability tracking is enabled
        """
        self.enabled = enabled

    async def track_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an observability event.

        Args:
            event_type: Type of event (e.g., validation.success, validation.failed)
            event_data: Event data
            metadata: Additional metadata
        """
        if not self.enabled:
            return

        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": event_data,
            "metadata": metadata or {},
        }

        # Log the event
        logger.info(f"AIKit Event: {event_type}", extra={"event": event})

        # TODO: Send to actual AIKit observability service
        # await aikit_sdk.track_event(event)

    async def track_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Track a metric value.

        Args:
            metric_name: Metric name
            value: Metric value
            tags: Metric tags for grouping
        """
        if not self.enabled:
            return

        metric = {
            "metric_name": metric_name,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tags": tags or {},
        }

        logger.info(f"AIKit Metric: {metric_name}={value}", extra={"metric": metric})

        # TODO: Send to actual AIKit observability service
        # await aikit_sdk.track_metric(metric)

    async def log_validation_failure(
        self,
        request_path: str,
        errors: List[Dict[str, Any]],
        request_id: Optional[str] = None,
    ) -> None:
        """Log validation failure with details.

        Args:
            request_path: Request URL path
            errors: Validation error details
            request_id: Request ID for correlation
        """
        await self.track_event(
            event_type="validation.failed",
            event_data={
                "request_path": request_path,
                "error_count": len(errors),
                "errors": errors,
            },
            metadata={
                "request_id": request_id,
                "severity": "error",
            },
        )

    async def log_validation_success(
        self,
        request_path: str,
        processing_time_ms: int,
        request_id: Optional[str] = None,
    ) -> None:
        """Log successful validation.

        Args:
            request_path: Request URL path
            processing_time_ms: Request processing time
            request_id: Request ID for correlation
        """
        await self.track_event(
            event_type="validation.success",
            event_data={
                "request_path": request_path,
                "processing_time_ms": processing_time_ms,
            },
            metadata={
                "request_id": request_id,
                "severity": "info",
            },
        )

        # Track processing time metric
        await self.track_metric(
            metric_name="validation.processing_time_ms",
            value=float(processing_time_ms),
            tags={
                "endpoint": request_path,
                "status": "success",
            },
        )


# Global observability client
_observability_client: Optional[AIKitObservabilityClient] = None


def get_observability_client() -> AIKitObservabilityClient:
    """Get or create the global observability client.

    Returns:
        AIKitObservabilityClient instance
    """
    global _observability_client
    if _observability_client is None:
        _observability_client = AIKitObservabilityClient(
            enabled=True  # Can be controlled via settings.ENABLE_OBSERVABILITY
        )
    return _observability_client


async def track_validation_event(
    request: Request,
    success: bool,
    errors: List[Any],
    processing_time_ms: int,
    additional_info: Optional[Dict[str, Any]] = None,
) -> None:
    """Track a validation event.

    Args:
        request: FastAPI request
        success: Whether validation succeeded
        errors: List of validation errors (empty if success)
        processing_time_ms: Request processing time
        additional_info: Additional information to log
    """
    client = get_observability_client()
    request_id = request.headers.get("X-Request-ID")
    request_path = str(request.url.path)

    if success:
        await client.log_validation_success(
            request_path=request_path,
            processing_time_ms=processing_time_ms,
            request_id=request_id,
        )
    else:
        # Convert errors to dict format
        error_dicts = []
        for error in errors:
            if hasattr(error, "to_dict"):
                error_dicts.append(error.to_dict())
            else:
                error_dicts.append({"error": str(error)})

        await client.log_validation_failure(
            request_path=request_path,
            errors=error_dicts,
            request_id=request_id,
        )

        # Track failure metric
        await client.track_metric(
            metric_name="validation.failures",
            value=1.0,
            tags={
                "endpoint": request_path,
                "error_count": str(len(errors)),
            },
        )

    # Track additional info if provided
    if additional_info:
        await client.track_event(
            event_type="validation.additional_info",
            event_data=additional_info,
            metadata={"request_id": request_id},
        )


async def track_validation_metrics(
    endpoint: str,
    total_requests: int,
    successful_validations: int,
    failed_validations: int,
) -> None:
    """Track aggregated validation metrics.

    Args:
        endpoint: API endpoint path
        total_requests: Total number of requests
        successful_validations: Number of successful validations
        failed_validations: Number of failed validations
    """
    client = get_observability_client()

    # Calculate pass rate
    pass_rate = (
        successful_validations / total_requests if total_requests > 0 else 0.0
    )

    await client.track_metric(
        metric_name="validation.pass_rate",
        value=pass_rate,
        tags={"endpoint": endpoint},
    )

    await client.track_metric(
        metric_name="validation.total_requests",
        value=float(total_requests),
        tags={"endpoint": endpoint},
    )

    await client.track_metric(
        metric_name="validation.successful",
        value=float(successful_validations),
        tags={"endpoint": endpoint},
    )

    await client.track_metric(
        metric_name="validation.failed",
        value=float(failed_validations),
        tags={"endpoint": endpoint},
    )


async def get_validation_statistics(
    endpoint: Optional[str] = None,
    time_window_minutes: int = 60,
) -> Dict[str, Any]:
    """Get validation statistics for monitoring.

    Args:
        endpoint: Optional endpoint filter
        time_window_minutes: Time window for statistics

    Returns:
        Dictionary with validation statistics
    """
    # This is a placeholder - implement with actual metrics collection
    return {
        "time_window_minutes": time_window_minutes,
        "endpoint": endpoint or "all",
        "total_requests": 0,
        "successful_validations": 0,
        "failed_validations": 0,
        "pass_rate": 0.0,
        "common_errors": [],
        "avg_processing_time_ms": 0.0,
    }
