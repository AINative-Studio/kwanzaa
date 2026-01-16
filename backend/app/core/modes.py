"""Model mode management system.

This module provides a flexible mode system that allows users to choose between
different model configurations:

1. base - Just the base model (no adapter, no RAG)
2. base + kwanzaa_adapter - Base model with trained adapter (no RAG)
3. base + adapter + RAG - Full system with base, adapter, and RAG (default)

The mode system supports per-session configuration and provides clear capability
trade-offs for each mode.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ModelMode(str, Enum):
    """Available model modes.

    Each mode represents a different configuration of the Kwanzaa system:
    - BASE: Just the base model (fastest, least accurate)
    - BASE_ADAPTER: Base + trained adapter (balanced)
    - FULL: Base + adapter + RAG (most accurate, default)
    """

    BASE = "base"
    BASE_ADAPTER = "base_adapter"
    FULL = "full"


@dataclass
class ModeCapabilities:
    """Capabilities and characteristics of a model mode.

    This class documents the trade-offs between different modes to help
    users make informed decisions about which mode to use.
    """

    mode: ModelMode

    # Performance characteristics
    relative_speed: float  # 1.0 = baseline, higher is faster
    memory_usage_mb: int  # Approximate memory usage

    # Feature availability
    has_adapter: bool  # Is the Kwanzaa adapter loaded?
    has_rag: bool  # Is RAG (semantic search) available?

    # Quality characteristics
    kwanzaa_accuracy: str  # Expected accuracy for Kwanzaa-specific queries
    general_capability: str  # Capability for general queries

    # Recommended use cases
    recommended_for: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dict with all capabilities and characteristics
        """
        return {
            "mode": self.mode.value,
            "performance": {
                "relative_speed": self.relative_speed,
                "memory_usage_mb": self.memory_usage_mb,
            },
            "features": {
                "has_adapter": self.has_adapter,
                "has_rag": self.has_rag,
            },
            "quality": {
                "kwanzaa_accuracy": self.kwanzaa_accuracy,
                "general_capability": self.general_capability,
            },
            "usage": {
                "recommended_for": self.recommended_for,
                "limitations": self.limitations,
            },
        }


# Mode capability definitions
MODE_CAPABILITIES: Dict[ModelMode, ModeCapabilities] = {
    ModelMode.BASE: ModeCapabilities(
        mode=ModelMode.BASE,
        relative_speed=3.0,
        memory_usage_mb=2000,
        has_adapter=False,
        has_rag=False,
        kwanzaa_accuracy="Low - No specialized knowledge",
        general_capability="Good - Standard LLM capabilities",
        recommended_for=[
            "Testing model functionality",
            "General purpose queries not specific to Kwanzaa",
            "Resource-constrained environments",
            "Quick prototyping",
        ],
        limitations=[
            "No Kwanzaa-specific training or knowledge",
            "Cannot access document corpus via RAG",
            "May hallucinate Kwanzaa-related facts",
            "No provenance or citation capabilities",
        ],
    ),
    ModelMode.BASE_ADAPTER: ModeCapabilities(
        mode=ModelMode.BASE_ADAPTER,
        relative_speed=2.0,
        memory_usage_mb=2500,
        has_adapter=True,
        has_rag=False,
        kwanzaa_accuracy="Medium - Trained on Kwanzaa corpus",
        general_capability="Good - Maintains base model capabilities",
        recommended_for=[
            "Kwanzaa-specific question answering without citations",
            "Contexts where RAG/search is not needed",
            "Faster response times with Kwanzaa knowledge",
            "Offline or disconnected environments",
        ],
        limitations=[
            "Cannot access document corpus for grounding",
            "No citation or provenance tracking",
            "Knowledge limited to training data",
            "May still hallucinate for edge cases",
        ],
    ),
    ModelMode.FULL: ModeCapabilities(
        mode=ModelMode.FULL,
        relative_speed=1.0,
        memory_usage_mb=3000,
        has_adapter=True,
        has_rag=True,
        kwanzaa_accuracy="High - Adapter + grounded retrieval",
        general_capability="Excellent - Full system capabilities",
        recommended_for=[
            "Production use cases requiring accuracy",
            "Research and educational applications",
            "Queries requiring citations and provenance",
            "Any use case where accuracy is critical",
        ],
        limitations=[
            "Slower due to RAG retrieval step",
            "Requires vector database connectivity",
            "Higher memory and compute requirements",
            "Network latency for remote vector DB",
        ],
    ),
}


@dataclass
class SessionMode:
    """Session-specific mode configuration.

    Tracks the active mode for a user session along with metadata
    about when it was set and when it expires.
    """

    session_id: str
    mode: ModelMode
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if session has expired.

        Returns:
            True if session is expired
        """
        return datetime.utcnow() >= self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dict with session information
        """
        return {
            "session_id": self.session_id,
            "mode": self.mode.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_expired": self.is_expired(),
            "metadata": self.metadata,
        }


class ModeSessionStore:
    """In-memory session store for model modes.

    This implementation uses an in-memory dictionary for session storage.
    For production deployments with multiple workers, consider using Redis
    or another distributed cache.
    """

    def __init__(self, default_ttl_minutes: int = 60):
        """Initialize session store.

        Args:
            default_ttl_minutes: Default session TTL in minutes
        """
        self._sessions: Dict[str, SessionMode] = {}
        self._default_ttl_minutes = default_ttl_minutes

    def create_session(
        self,
        mode: ModelMode,
        session_id: Optional[str] = None,
        ttl_minutes: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionMode:
        """Create a new session with specified mode.

        Args:
            mode: Model mode for this session
            session_id: Optional session ID (generated if not provided)
            ttl_minutes: Session TTL in minutes (uses default if not provided)
            metadata: Optional session metadata

        Returns:
            Created SessionMode instance
        """
        if session_id is None:
            session_id = str(uuid4())

        ttl = ttl_minutes if ttl_minutes is not None else self._default_ttl_minutes
        now = datetime.utcnow()

        session = SessionMode(
            session_id=session_id,
            mode=mode,
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(minutes=ttl),
            metadata=metadata or {},
        )

        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionMode]:
        """Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            SessionMode if found and not expired, None otherwise
        """
        session = self._sessions.get(session_id)

        if session is None:
            return None

        if session.is_expired():
            # Clean up expired session
            del self._sessions[session_id]
            return None

        return session

    def update_session(
        self,
        session_id: str,
        mode: Optional[ModelMode] = None,
        metadata: Optional[Dict[str, Any]] = None,
        extend_ttl: bool = True,
    ) -> Optional[SessionMode]:
        """Update an existing session.

        Args:
            session_id: Session identifier
            mode: New mode (keeps current if None)
            metadata: New metadata to merge with existing
            extend_ttl: Whether to extend expiration time

        Returns:
            Updated SessionMode if session exists, None otherwise
        """
        session = self.get_session(session_id)

        if session is None:
            return None

        now = datetime.utcnow()

        if mode is not None:
            session.mode = mode

        if metadata is not None:
            session.metadata.update(metadata)

        session.updated_at = now

        if extend_ttl:
            session.expires_at = now + timedelta(minutes=self._default_ttl_minutes)

        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove all expired sessions.

        Returns:
            Number of sessions removed
        """
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]

        for sid in expired_ids:
            del self._sessions[sid]

        return len(expired_ids)

    def get_active_session_count(self) -> int:
        """Get count of active (non-expired) sessions.

        Returns:
            Number of active sessions
        """
        self.cleanup_expired()
        return len(self._sessions)


class ModeManager:
    """Manager for model mode operations.

    This class provides the main interface for mode management, including
    validation, session management, and capability lookup.
    """

    def __init__(
        self,
        default_mode: ModelMode = ModelMode.FULL,
        session_store: Optional[ModeSessionStore] = None,
    ):
        """Initialize mode manager.

        Args:
            default_mode: Default mode for new sessions
            session_store: Session store instance (created if not provided)
        """
        self._default_mode = default_mode
        self._session_store = session_store or ModeSessionStore()

    @property
    def default_mode(self) -> ModelMode:
        """Get the default mode.

        Returns:
            Default ModelMode
        """
        return self._default_mode

    def get_mode_capabilities(self, mode: ModelMode) -> ModeCapabilities:
        """Get capabilities for a specific mode.

        Args:
            mode: Model mode

        Returns:
            ModeCapabilities for the specified mode

        Raises:
            ValueError: If mode is invalid
        """
        if mode not in MODE_CAPABILITIES:
            raise ValueError(f"Invalid mode: {mode}")

        return MODE_CAPABILITIES[mode]

    def get_all_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities for all modes.

        Returns:
            Dict mapping mode names to capability dictionaries
        """
        return {
            mode.value: capabilities.to_dict()
            for mode, capabilities in MODE_CAPABILITIES.items()
        }

    def validate_mode(self, mode_str: str) -> ModelMode:
        """Validate and convert mode string to enum.

        Args:
            mode_str: Mode string (base, base_adapter, full)

        Returns:
            ModelMode enum value

        Raises:
            ValueError: If mode string is invalid
        """
        try:
            return ModelMode(mode_str)
        except ValueError as e:
            valid_modes = [m.value for m in ModelMode]
            raise ValueError(
                f"Invalid mode: {mode_str}. Valid options: {valid_modes}"
            ) from e

    def create_session(
        self,
        mode: Optional[ModelMode] = None,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> SessionMode:
        """Create a new session.

        Args:
            mode: Model mode (uses default if not provided)
            session_id: Optional session ID
            **kwargs: Additional arguments passed to session store

        Returns:
            Created SessionMode instance
        """
        mode = mode or self._default_mode
        return self._session_store.create_session(
            mode=mode,
            session_id=session_id,
            **kwargs,
        )

    def get_session(self, session_id: str) -> Optional[SessionMode]:
        """Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            SessionMode if found, None otherwise
        """
        return self._session_store.get_session(session_id)

    def get_session_mode(self, session_id: str) -> ModelMode:
        """Get mode for a session, falling back to default.

        Args:
            session_id: Session identifier

        Returns:
            ModelMode for the session or default mode
        """
        session = self.get_session(session_id)
        return session.mode if session else self._default_mode

    def update_session_mode(
        self,
        session_id: str,
        mode: ModelMode,
        **kwargs,
    ) -> Optional[SessionMode]:
        """Update mode for an existing session.

        Args:
            session_id: Session identifier
            mode: New model mode
            **kwargs: Additional arguments passed to session store

        Returns:
            Updated SessionMode if session exists, None otherwise
        """
        return self._session_store.update_session(
            session_id=session_id,
            mode=mode,
            **kwargs,
        )

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        return self._session_store.delete_session(session_id)

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.

        Returns:
            Number of sessions removed
        """
        return self._session_store.cleanup_expired()

    def get_stats(self) -> Dict[str, Any]:
        """Get mode manager statistics.

        Returns:
            Dict with statistics about sessions and modes
        """
        return {
            "default_mode": self._default_mode.value,
            "active_sessions": self._session_store.get_active_session_count(),
            "available_modes": [mode.value for mode in ModelMode],
        }


# Global mode manager instance
_mode_manager: Optional[ModeManager] = None


def get_mode_manager(
    default_mode: ModelMode = ModelMode.FULL,
    reset: bool = False,
) -> ModeManager:
    """Get or create global mode manager instance.

    Args:
        default_mode: Default mode for new sessions
        reset: Force creation of new instance

    Returns:
        ModeManager instance
    """
    global _mode_manager

    if _mode_manager is None or reset:
        _mode_manager = ModeManager(default_mode=default_mode)

    return _mode_manager
