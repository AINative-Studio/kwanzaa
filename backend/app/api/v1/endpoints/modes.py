"""Model mode management API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.modes import (
    ModeManager,
    ModelMode,
    get_mode_manager,
)
from app.models.modes import (
    AllCapabilitiesResponse,
    ErrorResponse,
    ModeCapabilitiesResponse,
    ModeStatsResponse,
    ModeUpdateRequest,
    SessionCreateRequest,
    SessionDeleteResponse,
    SessionResponse,
)

router = APIRouter()


def get_manager() -> ModeManager:
    """Get mode manager instance.

    Returns:
        ModeManager dependency
    """
    try:
        default_mode = ModelMode(settings.DEFAULT_MODEL_MODE)
    except ValueError:
        default_mode = ModelMode.FULL

    return get_mode_manager(default_mode=default_mode)


@router.get(
    "/capabilities",
    response_model=AllCapabilitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all mode capabilities",
    description="""
    Retrieve detailed information about all available model modes.

    This endpoint returns performance characteristics, feature availability,
    quality expectations, and usage recommendations for each mode to help
    users make informed decisions about mode selection.

    Modes:
    - **base**: Just the base model (fastest, least accurate)
    - **base_adapter**: Base + trained adapter (balanced)
    - **full**: Base + adapter + RAG (most accurate, default)
    """,
    responses={
        200: {"description": "Capabilities retrieved successfully"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def get_all_capabilities(
    manager: ModeManager = Depends(get_manager),
) -> AllCapabilitiesResponse:
    """Get capabilities for all modes.

    Args:
        manager: Mode manager dependency

    Returns:
        AllCapabilitiesResponse with all mode capabilities
    """
    try:
        capabilities = manager.get_all_capabilities()

        return AllCapabilitiesResponse(
            modes=capabilities,
            default_mode=manager.default_mode.value,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve capabilities: {str(e)}",
        ) from e


@router.get(
    "/capabilities/{mode}",
    response_model=ModeCapabilitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get capabilities for specific mode",
    description="""
    Retrieve detailed information about a specific model mode.

    Returns performance characteristics, features, quality metrics,
    and usage recommendations for the requested mode.
    """,
    responses={
        200: {"description": "Capabilities retrieved successfully"},
        400: {"description": "Invalid mode"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def get_mode_capabilities(
    mode: str,
    manager: ModeManager = Depends(get_manager),
) -> ModeCapabilitiesResponse:
    """Get capabilities for a specific mode.

    Args:
        mode: Mode identifier (base, base_adapter, full)
        manager: Mode manager dependency

    Returns:
        ModeCapabilitiesResponse for the specified mode

    Raises:
        HTTPException: If mode is invalid
    """
    try:
        mode_enum = manager.validate_mode(mode)
        capabilities = manager.get_mode_capabilities(mode_enum)

        return ModeCapabilitiesResponse(**capabilities.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve capabilities: {str(e)}",
        ) from e


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new session",
    description="""
    Create a new session with a specific model mode.

    Sessions are used to track user preferences for model mode across
    multiple requests. Each session has a TTL and will be automatically
    cleaned up after expiration.

    If no mode is specified, the default mode (full) is used.
    If no session_id is provided, one will be generated automatically.
    """,
    responses={
        201: {"description": "Session created successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def create_session(
    request: SessionCreateRequest,
    manager: ModeManager = Depends(get_manager),
) -> SessionResponse:
    """Create a new session.

    Args:
        request: Session creation request
        manager: Mode manager dependency

    Returns:
        SessionResponse with created session information

    Raises:
        HTTPException: If session creation fails
    """
    try:
        # Validate mode if provided
        mode_enum = None
        if request.mode:
            mode_enum = manager.validate_mode(request.mode)

        # Create session
        session = manager.create_session(
            mode=mode_enum,
            session_id=request.session_id,
            ttl_minutes=request.ttl_minutes,
            metadata=request.metadata,
        )

        return SessionResponse(**session.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        ) from e


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get session information",
    description="""
    Retrieve information about an existing session.

    Returns the current mode, timestamps, and expiration status for
    the specified session.
    """,
    responses={
        200: {"description": "Session retrieved successfully"},
        404: {"description": "Session not found or expired"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def get_session(
    session_id: str,
    manager: ModeManager = Depends(get_manager),
) -> SessionResponse:
    """Get session information.

    Args:
        session_id: Session identifier
        manager: Mode manager dependency

    Returns:
        SessionResponse with session information

    Raises:
        HTTPException: If session not found or retrieval fails
    """
    try:
        session = manager.get_session(session_id)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found or expired: {session_id}",
            )

        return SessionResponse(**session.to_dict())

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}",
        ) from e


@router.patch(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update session mode",
    description="""
    Update the model mode for an existing session.

    This allows users to switch between modes during their session.
    By default, updating the mode extends the session TTL.
    """,
    responses={
        200: {"description": "Session updated successfully"},
        400: {"description": "Invalid mode or request"},
        404: {"description": "Session not found or expired"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def update_session(
    session_id: str,
    request: ModeUpdateRequest,
    manager: ModeManager = Depends(get_manager),
) -> SessionResponse:
    """Update session mode.

    Args:
        session_id: Session identifier
        request: Mode update request
        manager: Mode manager dependency

    Returns:
        SessionResponse with updated session information

    Raises:
        HTTPException: If session not found or update fails
    """
    try:
        # Validate mode
        mode_enum = manager.validate_mode(request.mode)

        # Update session
        session = manager.update_session_mode(
            session_id=session_id,
            mode=mode_enum,
            metadata=request.metadata,
            extend_ttl=request.extend_ttl,
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found or expired: {session_id}",
            )

        return SessionResponse(**session.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}",
        ) from e


@router.delete(
    "/sessions/{session_id}",
    response_model=SessionDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete session",
    description="""
    Delete an existing session.

    This immediately removes the session and frees associated resources.
    """,
    responses={
        200: {"description": "Session deleted or not found"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def delete_session(
    session_id: str,
    manager: ModeManager = Depends(get_manager),
) -> SessionDeleteResponse:
    """Delete a session.

    Args:
        session_id: Session identifier
        manager: Mode manager dependency

    Returns:
        SessionDeleteResponse confirming deletion

    Note:
        Returns success even if session doesn't exist (idempotent)
    """
    try:
        deleted = manager.delete_session(session_id)

        return SessionDeleteResponse(
            success=deleted,
            session_id=session_id,
            message=(
                "Session deleted successfully"
                if deleted
                else "Session not found (may already be deleted)"
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}",
        ) from e


@router.get(
    "/stats",
    response_model=ModeStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get mode system statistics",
    description="""
    Retrieve statistics about the mode management system.

    Returns information about active sessions, default mode, and
    available modes.
    """,
    responses={
        200: {"description": "Statistics retrieved successfully"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def get_stats(
    manager: ModeManager = Depends(get_manager),
) -> ModeStatsResponse:
    """Get mode system statistics.

    Args:
        manager: Mode manager dependency

    Returns:
        ModeStatsResponse with system statistics
    """
    try:
        stats = manager.get_stats()
        return ModeStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}",
        ) from e


@router.post(
    "/cleanup",
    status_code=status.HTTP_200_OK,
    summary="Cleanup expired sessions",
    description="""
    Manually trigger cleanup of expired sessions.

    This is normally done automatically, but can be triggered manually
    for maintenance purposes.
    """,
    responses={
        200: {"description": "Cleanup completed"},
        500: {"description": "Internal server error"},
    },
    tags=["modes"],
)
async def cleanup_expired_sessions(
    manager: ModeManager = Depends(get_manager),
) -> dict:
    """Cleanup expired sessions.

    Args:
        manager: Mode manager dependency

    Returns:
        Dict with cleanup statistics
    """
    try:
        removed_count = manager.cleanup_expired_sessions()

        return {
            "success": True,
            "sessions_removed": removed_count,
            "message": f"Cleaned up {removed_count} expired session(s)",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup sessions: {str(e)}",
        ) from e
