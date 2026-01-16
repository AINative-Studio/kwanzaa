"""API models for model mode operations."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ModeCapabilitiesResponse(BaseModel):
    """Response model for mode capabilities.

    Provides detailed information about what a mode can and cannot do,
    helping users make informed decisions about mode selection.
    """

    mode: str = Field(
        ...,
        description="Mode identifier",
    )
    performance: Dict[str, Any] = Field(
        ...,
        description="Performance characteristics",
    )
    features: Dict[str, bool] = Field(
        ...,
        description="Available features",
    )
    quality: Dict[str, str] = Field(
        ...,
        description="Quality characteristics",
    )
    usage: Dict[str, List[str]] = Field(
        ...,
        description="Recommended usage and limitations",
    )


class SessionCreateRequest(BaseModel):
    """Request to create a new session with specific mode.

    This allows clients to explicitly create a session with a chosen mode.
    """

    mode: Optional[str] = Field(
        default=None,
        pattern="^(base|base_adapter|full)$",
        description="Model mode (base, base_adapter, full). Uses default if not provided.",
    )
    session_id: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Optional custom session ID",
    )
    ttl_minutes: Optional[int] = Field(
        default=None,
        ge=1,
        le=1440,
        description="Session TTL in minutes (1-1440)",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional session metadata",
    )


class SessionResponse(BaseModel):
    """Response model for session information.

    Returns the current state of a session including mode and expiration.
    """

    session_id: str = Field(
        ...,
        description="Session identifier",
    )
    mode: str = Field(
        ...,
        description="Current model mode",
    )
    created_at: str = Field(
        ...,
        description="Session creation timestamp (ISO 8601)",
    )
    updated_at: str = Field(
        ...,
        description="Last update timestamp (ISO 8601)",
    )
    expires_at: str = Field(
        ...,
        description="Expiration timestamp (ISO 8601)",
    )
    is_expired: bool = Field(
        ...,
        description="Whether session has expired",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Session metadata",
    )


class ModeUpdateRequest(BaseModel):
    """Request to update session mode.

    Allows changing the mode for an existing session.
    """

    mode: str = Field(
        ...,
        pattern="^(base|base_adapter|full)$",
        description="New model mode (base, base_adapter, full)",
    )
    extend_ttl: bool = Field(
        default=True,
        description="Whether to extend session expiration",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata to merge",
    )


class ModeStatsResponse(BaseModel):
    """Response model for mode system statistics.

    Provides overview of mode system state.
    """

    default_mode: str = Field(
        ...,
        description="Default mode for new sessions",
    )
    active_sessions: int = Field(
        ...,
        ge=0,
        description="Number of active sessions",
    )
    available_modes: List[str] = Field(
        ...,
        description="List of available modes",
    )


class AllCapabilitiesResponse(BaseModel):
    """Response model for all mode capabilities.

    Returns capabilities information for all available modes.
    """

    modes: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Capabilities by mode",
    )
    default_mode: str = Field(
        ...,
        description="Default mode",
    )


class ErrorResponse(BaseModel):
    """Standard error response model.

    Provides consistent error information across all endpoints.
    """

    error: str = Field(
        ...,
        description="Error type or category",
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details",
    )


class SessionDeleteResponse(BaseModel):
    """Response model for session deletion.

    Confirms whether session was successfully deleted.
    """

    success: bool = Field(
        ...,
        description="Whether deletion was successful",
    )
    session_id: str = Field(
        ...,
        description="Session ID that was deleted (or attempted)",
    )
    message: str = Field(
        ...,
        description="Descriptive message about the operation",
    )
