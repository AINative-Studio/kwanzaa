"""Unit tests for model mode system.

Tests cover:
- Mode enum and capabilities
- Session management
- Mode manager operations
- Session store operations
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from app.core.modes import (
    MODE_CAPABILITIES,
    ModeCapabilities,
    ModeManager,
    ModeSessionStore,
    ModelMode,
    SessionMode,
    get_mode_manager,
)


class TestModelMode:
    """Test ModelMode enum."""

    def test_mode_values(self):
        """Test that mode values are correct."""
        assert ModelMode.BASE.value == "base"
        assert ModelMode.BASE_ADAPTER.value == "base_adapter"
        assert ModelMode.FULL.value == "full"

    def test_mode_from_string(self):
        """Test creating mode from string."""
        assert ModelMode("base") == ModelMode.BASE
        assert ModelMode("base_adapter") == ModelMode.BASE_ADAPTER
        assert ModelMode("full") == ModelMode.FULL

    def test_invalid_mode_string(self):
        """Test that invalid mode string raises error."""
        with pytest.raises(ValueError):
            ModelMode("invalid")


class TestModeCapabilities:
    """Test ModeCapabilities dataclass."""

    def test_base_mode_capabilities(self):
        """Test capabilities for BASE mode."""
        caps = MODE_CAPABILITIES[ModelMode.BASE]

        assert caps.mode == ModelMode.BASE
        assert caps.has_adapter is False
        assert caps.has_rag is False
        assert caps.relative_speed > 1.0
        assert len(caps.recommended_for) > 0
        assert len(caps.limitations) > 0

    def test_base_adapter_mode_capabilities(self):
        """Test capabilities for BASE_ADAPTER mode."""
        caps = MODE_CAPABILITIES[ModelMode.BASE_ADAPTER]

        assert caps.mode == ModelMode.BASE_ADAPTER
        assert caps.has_adapter is True
        assert caps.has_rag is False
        assert caps.relative_speed > MODE_CAPABILITIES[ModelMode.FULL].relative_speed

    def test_full_mode_capabilities(self):
        """Test capabilities for FULL mode."""
        caps = MODE_CAPABILITIES[ModelMode.FULL]

        assert caps.mode == ModelMode.FULL
        assert caps.has_adapter is True
        assert caps.has_rag is True
        assert caps.relative_speed == 1.0

    def test_capabilities_to_dict(self):
        """Test converting capabilities to dictionary."""
        caps = MODE_CAPABILITIES[ModelMode.BASE]
        caps_dict = caps.to_dict()

        assert caps_dict["mode"] == "base"
        assert "performance" in caps_dict
        assert "features" in caps_dict
        assert "quality" in caps_dict
        assert "usage" in caps_dict

        assert "relative_speed" in caps_dict["performance"]
        assert "has_adapter" in caps_dict["features"]
        assert "kwanzaa_accuracy" in caps_dict["quality"]
        assert "recommended_for" in caps_dict["usage"]


class TestSessionMode:
    """Test SessionMode dataclass."""

    def test_session_creation(self):
        """Test creating a session."""
        now = datetime.utcnow()
        expires = now + timedelta(minutes=60)

        session = SessionMode(
            session_id="test-123",
            mode=ModelMode.FULL,
            created_at=now,
            updated_at=now,
            expires_at=expires,
            metadata={"user": "test"},
        )

        assert session.session_id == "test-123"
        assert session.mode == ModelMode.FULL
        assert session.metadata["user"] == "test"

    def test_session_not_expired(self):
        """Test that fresh session is not expired."""
        now = datetime.utcnow()
        expires = now + timedelta(minutes=60)

        session = SessionMode(
            session_id="test-123",
            mode=ModelMode.FULL,
            created_at=now,
            updated_at=now,
            expires_at=expires,
        )

        assert session.is_expired() is False

    def test_session_expired(self):
        """Test that old session is expired."""
        now = datetime.utcnow()
        expires = now - timedelta(minutes=1)  # Expired 1 minute ago

        session = SessionMode(
            session_id="test-123",
            mode=ModelMode.FULL,
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=1),
            expires_at=expires,
        )

        assert session.is_expired() is True

    def test_session_to_dict(self):
        """Test converting session to dictionary."""
        now = datetime.utcnow()
        expires = now + timedelta(minutes=60)

        session = SessionMode(
            session_id="test-123",
            mode=ModelMode.BASE,
            created_at=now,
            updated_at=now,
            expires_at=expires,
            metadata={"test": "data"},
        )

        session_dict = session.to_dict()

        assert session_dict["session_id"] == "test-123"
        assert session_dict["mode"] == "base"
        assert "created_at" in session_dict
        assert "expires_at" in session_dict
        assert session_dict["metadata"]["test"] == "data"


class TestModeSessionStore:
    """Test ModeSessionStore."""

    def test_create_session_with_auto_id(self):
        """Test creating session with auto-generated ID."""
        store = ModeSessionStore(default_ttl_minutes=60)

        session = store.create_session(mode=ModelMode.FULL)

        assert session.session_id is not None
        assert session.mode == ModelMode.FULL
        assert not session.is_expired()

    def test_create_session_with_custom_id(self):
        """Test creating session with custom ID."""
        store = ModeSessionStore()

        session = store.create_session(
            mode=ModelMode.BASE,
            session_id="custom-123",
        )

        assert session.session_id == "custom-123"

    def test_create_session_with_custom_ttl(self):
        """Test creating session with custom TTL."""
        store = ModeSessionStore(default_ttl_minutes=30)

        session = store.create_session(
            mode=ModelMode.FULL,
            ttl_minutes=120,
        )

        # Session should expire in ~120 minutes, not 30
        expected_expiry = datetime.utcnow() + timedelta(minutes=120)
        delta = abs((session.expires_at - expected_expiry).total_seconds())
        assert delta < 5  # Within 5 seconds

    def test_create_session_with_metadata(self):
        """Test creating session with metadata."""
        store = ModeSessionStore()

        session = store.create_session(
            mode=ModelMode.BASE,
            metadata={"user_id": "user-123", "ip": "127.0.0.1"},
        )

        assert session.metadata["user_id"] == "user-123"
        assert session.metadata["ip"] == "127.0.0.1"

    def test_get_existing_session(self):
        """Test retrieving existing session."""
        store = ModeSessionStore()

        created = store.create_session(
            mode=ModelMode.FULL,
            session_id="test-456",
        )

        retrieved = store.get_session("test-456")

        assert retrieved is not None
        assert retrieved.session_id == created.session_id
        assert retrieved.mode == created.mode

    def test_get_nonexistent_session(self):
        """Test retrieving non-existent session returns None."""
        store = ModeSessionStore()

        retrieved = store.get_session("nonexistent")

        assert retrieved is None

    def test_get_expired_session(self):
        """Test retrieving expired session returns None and cleans up."""
        store = ModeSessionStore()

        # Create session with very short TTL
        session = store.create_session(
            mode=ModelMode.FULL,
            session_id="expired-123",
            ttl_minutes=0,  # Expires immediately
        )

        # Force expiration
        session.expires_at = datetime.utcnow() - timedelta(seconds=1)

        retrieved = store.get_session("expired-123")

        assert retrieved is None

    def test_update_session_mode(self):
        """Test updating session mode."""
        store = ModeSessionStore()

        session = store.create_session(
            mode=ModelMode.BASE,
            session_id="update-test",
        )

        updated = store.update_session(
            session_id="update-test",
            mode=ModelMode.FULL,
        )

        assert updated is not None
        assert updated.mode == ModelMode.FULL

    def test_update_session_metadata(self):
        """Test updating session metadata."""
        store = ModeSessionStore()

        store.create_session(
            mode=ModelMode.BASE,
            session_id="meta-test",
            metadata={"key1": "value1"},
        )

        updated = store.update_session(
            session_id="meta-test",
            metadata={"key2": "value2"},
        )

        assert updated is not None
        assert updated.metadata["key1"] == "value1"
        assert updated.metadata["key2"] == "value2"

    def test_update_session_extends_ttl(self):
        """Test that updating session extends TTL by default."""
        store = ModeSessionStore(default_ttl_minutes=60)

        session = store.create_session(
            mode=ModelMode.BASE,
            session_id="ttl-test",
        )

        original_expiry = session.expires_at

        # Wait a moment and update
        import time
        time.sleep(0.1)

        updated = store.update_session(
            session_id="ttl-test",
            extend_ttl=True,
        )

        assert updated is not None
        assert updated.expires_at > original_expiry

    def test_update_session_without_extending_ttl(self):
        """Test updating session without extending TTL."""
        store = ModeSessionStore(default_ttl_minutes=60)

        session = store.create_session(
            mode=ModelMode.BASE,
            session_id="no-extend-test",
        )

        original_expiry = session.expires_at

        updated = store.update_session(
            session_id="no-extend-test",
            mode=ModelMode.FULL,
            extend_ttl=False,
        )

        assert updated is not None
        assert updated.expires_at == original_expiry

    def test_update_nonexistent_session(self):
        """Test updating non-existent session returns None."""
        store = ModeSessionStore()

        updated = store.update_session(
            session_id="nonexistent",
            mode=ModelMode.FULL,
        )

        assert updated is None

    def test_delete_existing_session(self):
        """Test deleting existing session."""
        store = ModeSessionStore()

        store.create_session(
            mode=ModelMode.BASE,
            session_id="delete-test",
        )

        deleted = store.delete_session("delete-test")

        assert deleted is True
        assert store.get_session("delete-test") is None

    def test_delete_nonexistent_session(self):
        """Test deleting non-existent session returns False."""
        store = ModeSessionStore()

        deleted = store.delete_session("nonexistent")

        assert deleted is False

    def test_cleanup_expired_sessions(self):
        """Test cleaning up expired sessions."""
        store = ModeSessionStore()

        # Create some sessions
        store.create_session(mode=ModelMode.BASE, session_id="active-1")
        store.create_session(mode=ModelMode.FULL, session_id="active-2")

        expired1 = store.create_session(mode=ModelMode.BASE, session_id="expired-1")
        expired2 = store.create_session(mode=ModelMode.BASE, session_id="expired-2")

        # Force expiration
        expired1.expires_at = datetime.utcnow() - timedelta(seconds=1)
        expired2.expires_at = datetime.utcnow() - timedelta(seconds=1)

        removed = store.cleanup_expired()

        assert removed == 2
        assert store.get_active_session_count() == 2

    def test_get_active_session_count(self):
        """Test getting active session count."""
        store = ModeSessionStore()

        assert store.get_active_session_count() == 0

        store.create_session(mode=ModelMode.BASE)
        store.create_session(mode=ModelMode.FULL)

        assert store.get_active_session_count() == 2


class TestModeManager:
    """Test ModeManager."""

    def test_manager_initialization(self):
        """Test manager initialization with default mode."""
        manager = ModeManager(default_mode=ModelMode.BASE_ADAPTER)

        assert manager.default_mode == ModelMode.BASE_ADAPTER

    def test_manager_default_mode(self):
        """Test manager uses FULL as default when not specified."""
        manager = ModeManager()

        assert manager.default_mode == ModelMode.FULL

    def test_get_mode_capabilities(self):
        """Test getting capabilities for a mode."""
        manager = ModeManager()

        caps = manager.get_mode_capabilities(ModelMode.BASE)

        assert caps.mode == ModelMode.BASE
        assert isinstance(caps, ModeCapabilities)

    def test_get_all_capabilities(self):
        """Test getting all mode capabilities."""
        manager = ModeManager()

        all_caps = manager.get_all_capabilities()

        assert "base" in all_caps
        assert "base_adapter" in all_caps
        assert "full" in all_caps
        assert all_caps["base"]["mode"] == "base"

    def test_validate_mode_valid(self):
        """Test validating valid mode string."""
        manager = ModeManager()

        mode = manager.validate_mode("base")
        assert mode == ModelMode.BASE

        mode = manager.validate_mode("full")
        assert mode == ModelMode.FULL

    def test_validate_mode_invalid(self):
        """Test validating invalid mode string raises error."""
        manager = ModeManager()

        with pytest.raises(ValueError) as exc_info:
            manager.validate_mode("invalid")

        assert "Invalid mode" in str(exc_info.value)
        assert "base" in str(exc_info.value)

    def test_create_session_with_default_mode(self):
        """Test creating session with default mode."""
        manager = ModeManager(default_mode=ModelMode.BASE_ADAPTER)

        session = manager.create_session()

        assert session.mode == ModelMode.BASE_ADAPTER

    def test_create_session_with_custom_mode(self):
        """Test creating session with custom mode."""
        manager = ModeManager()

        session = manager.create_session(mode=ModelMode.BASE)

        assert session.mode == ModelMode.BASE

    def test_get_session(self):
        """Test getting session through manager."""
        manager = ModeManager()

        created = manager.create_session(session_id="manager-test")
        retrieved = manager.get_session("manager-test")

        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    def test_get_session_mode_existing(self):
        """Test getting mode for existing session."""
        manager = ModeManager()

        manager.create_session(
            mode=ModelMode.BASE_ADAPTER,
            session_id="mode-test",
        )

        mode = manager.get_session_mode("mode-test")

        assert mode == ModelMode.BASE_ADAPTER

    def test_get_session_mode_nonexistent(self):
        """Test getting mode for non-existent session returns default."""
        manager = ModeManager(default_mode=ModelMode.BASE)

        mode = manager.get_session_mode("nonexistent")

        assert mode == ModelMode.BASE

    def test_update_session_mode(self):
        """Test updating session mode through manager."""
        manager = ModeManager()

        manager.create_session(
            mode=ModelMode.BASE,
            session_id="update-test",
        )

        updated = manager.update_session_mode(
            session_id="update-test",
            mode=ModelMode.FULL,
        )

        assert updated is not None
        assert updated.mode == ModelMode.FULL

    def test_delete_session(self):
        """Test deleting session through manager."""
        manager = ModeManager()

        manager.create_session(session_id="delete-test")

        deleted = manager.delete_session("delete-test")

        assert deleted is True
        assert manager.get_session("delete-test") is None

    def test_cleanup_expired_sessions(self):
        """Test cleanup through manager."""
        manager = ModeManager()

        session = manager.create_session(session_id="expired-test")
        session.expires_at = datetime.utcnow() - timedelta(seconds=1)

        removed = manager.cleanup_expired_sessions()

        assert removed >= 1

    def test_get_stats(self):
        """Test getting manager statistics."""
        manager = ModeManager(default_mode=ModelMode.BASE_ADAPTER)

        manager.create_session()
        manager.create_session()

        stats = manager.get_stats()

        assert stats["default_mode"] == "base_adapter"
        assert stats["active_sessions"] == 2
        assert len(stats["available_modes"]) == 3


class TestGetModeManager:
    """Test get_mode_manager factory function."""

    def test_get_manager_creates_singleton(self):
        """Test that get_mode_manager returns same instance."""
        manager1 = get_mode_manager()
        manager2 = get_mode_manager()

        assert manager1 is manager2

    def test_get_manager_with_reset(self):
        """Test that reset creates new instance."""
        manager1 = get_mode_manager()
        manager2 = get_mode_manager(reset=True)

        assert manager1 is not manager2

    def test_get_manager_with_default_mode(self):
        """Test creating manager with specific default mode."""
        manager = get_mode_manager(
            default_mode=ModelMode.BASE,
            reset=True,
        )

        assert manager.default_mode == ModelMode.BASE
