"""Integration tests for model mode API endpoints.

Tests cover:
- GET /capabilities - Get all mode capabilities
- GET /capabilities/{mode} - Get specific mode capabilities
- POST /sessions - Create new session
- GET /sessions/{session_id} - Get session info
- PATCH /sessions/{session_id} - Update session mode
- DELETE /sessions/{session_id} - Delete session
- GET /stats - Get system statistics
- POST /cleanup - Cleanup expired sessions
"""

import pytest
from fastapi.testclient import TestClient

from app.core.modes import ModelMode, get_mode_manager
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mode_manager():
    """Reset mode manager before each test."""
    get_mode_manager(reset=True)
    yield
    get_mode_manager(reset=True)


class TestCapabilitiesEndpoints:
    """Test capabilities endpoints."""

    def test_get_all_capabilities(self):
        """Test GET /capabilities returns all mode capabilities."""
        response = client.get("/api/v1/modes/capabilities")

        assert response.status_code == 200

        data = response.json()
        assert "modes" in data
        assert "default_mode" in data
        assert data["default_mode"] == "full"

        # Check all modes present
        assert "base" in data["modes"]
        assert "base_adapter" in data["modes"]
        assert "full" in data["modes"]

        # Check structure of capabilities
        base_caps = data["modes"]["base"]
        assert "performance" in base_caps
        assert "features" in base_caps
        assert "quality" in base_caps
        assert "usage" in base_caps

    def test_get_specific_mode_capabilities_base(self):
        """Test GET /capabilities/base."""
        response = client.get("/api/v1/modes/capabilities/base")

        assert response.status_code == 200

        data = response.json()
        assert data["mode"] == "base"
        assert data["features"]["has_adapter"] is False
        assert data["features"]["has_rag"] is False

    def test_get_specific_mode_capabilities_base_adapter(self):
        """Test GET /capabilities/base_adapter."""
        response = client.get("/api/v1/modes/capabilities/base_adapter")

        assert response.status_code == 200

        data = response.json()
        assert data["mode"] == "base_adapter"
        assert data["features"]["has_adapter"] is True
        assert data["features"]["has_rag"] is False

    def test_get_specific_mode_capabilities_full(self):
        """Test GET /capabilities/full."""
        response = client.get("/api/v1/modes/capabilities/full")

        assert response.status_code == 200

        data = response.json()
        assert data["mode"] == "full"
        assert data["features"]["has_adapter"] is True
        assert data["features"]["has_rag"] is True

    def test_get_invalid_mode_capabilities(self):
        """Test GET /capabilities with invalid mode returns 400."""
        response = client.get("/api/v1/modes/capabilities/invalid")

        assert response.status_code == 400
        assert "Invalid mode" in response.json()["detail"]


class TestSessionEndpoints:
    """Test session management endpoints."""

    def test_create_session_with_defaults(self):
        """Test POST /sessions with default parameters."""
        response = client.post("/api/v1/modes/sessions", json={})

        assert response.status_code == 201

        data = response.json()
        assert "session_id" in data
        assert data["mode"] == "full"  # Default mode
        assert data["is_expired"] is False

    def test_create_session_with_custom_mode(self):
        """Test POST /sessions with custom mode."""
        response = client.post(
            "/api/v1/modes/sessions",
            json={"mode": "base"},
        )

        assert response.status_code == 201

        data = response.json()
        assert data["mode"] == "base"

    def test_create_session_with_custom_id(self):
        """Test POST /sessions with custom session ID."""
        response = client.post(
            "/api/v1/modes/sessions",
            json={
                "mode": "base_adapter",
                "session_id": "custom-session-123",
            },
        )

        assert response.status_code == 201

        data = response.json()
        assert data["session_id"] == "custom-session-123"
        assert data["mode"] == "base_adapter"

    def test_create_session_with_metadata(self):
        """Test POST /sessions with metadata."""
        response = client.post(
            "/api/v1/modes/sessions",
            json={
                "mode": "full",
                "metadata": {
                    "user_id": "user-123",
                    "source": "web",
                },
            },
        )

        assert response.status_code == 201

        data = response.json()
        assert data["metadata"]["user_id"] == "user-123"
        assert data["metadata"]["source"] == "web"

    def test_create_session_with_custom_ttl(self):
        """Test POST /sessions with custom TTL."""
        response = client.post(
            "/api/v1/modes/sessions",
            json={
                "mode": "base",
                "ttl_minutes": 120,
            },
        )

        assert response.status_code == 201

        data = response.json()
        # Verify session was created (detailed TTL validation in unit tests)
        assert "expires_at" in data

    def test_create_session_with_invalid_mode(self):
        """Test POST /sessions with invalid mode returns 400."""
        response = client.post(
            "/api/v1/modes/sessions",
            json={"mode": "invalid"},
        )

        assert response.status_code == 400

    def test_get_existing_session(self):
        """Test GET /sessions/{session_id} for existing session."""
        # Create session first
        create_response = client.post(
            "/api/v1/modes/sessions",
            json={"session_id": "test-get-123"},
        )
        assert create_response.status_code == 201

        # Get session
        response = client.get("/api/v1/modes/sessions/test-get-123")

        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "test-get-123"
        assert data["mode"] == "full"

    def test_get_nonexistent_session(self):
        """Test GET /sessions/{session_id} for non-existent session returns 404."""
        response = client.get("/api/v1/modes/sessions/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_session_mode(self):
        """Test PATCH /sessions/{session_id} to update mode."""
        # Create session
        create_response = client.post(
            "/api/v1/modes/sessions",
            json={
                "session_id": "test-update-123",
                "mode": "base",
            },
        )
        assert create_response.status_code == 201

        # Update mode
        response = client.patch(
            "/api/v1/modes/sessions/test-update-123",
            json={"mode": "full"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "test-update-123"
        assert data["mode"] == "full"

    def test_update_session_with_metadata(self):
        """Test PATCH /sessions/{session_id} with metadata."""
        # Create session
        create_response = client.post(
            "/api/v1/modes/sessions",
            json={
                "session_id": "test-meta-123",
                "metadata": {"key1": "value1"},
            },
        )
        assert create_response.status_code == 201

        # Update with new metadata
        response = client.patch(
            "/api/v1/modes/sessions/test-meta-123",
            json={
                "mode": "base",
                "metadata": {"key2": "value2"},
            },
        )

        assert response.status_code == 200

        data = response.json()
        assert data["metadata"]["key1"] == "value1"
        assert data["metadata"]["key2"] == "value2"

    def test_update_nonexistent_session(self):
        """Test PATCH /sessions/{session_id} for non-existent session returns 404."""
        response = client.patch(
            "/api/v1/modes/sessions/nonexistent",
            json={"mode": "full"},
        )

        assert response.status_code == 404

    def test_update_session_with_invalid_mode(self):
        """Test PATCH /sessions/{session_id} with invalid mode returns 400."""
        # Create session
        create_response = client.post(
            "/api/v1/modes/sessions",
            json={"session_id": "test-invalid-123"},
        )
        assert create_response.status_code == 201

        # Try to update with invalid mode
        response = client.patch(
            "/api/v1/modes/sessions/test-invalid-123",
            json={"mode": "invalid"},
        )

        assert response.status_code == 400

    def test_delete_existing_session(self):
        """Test DELETE /sessions/{session_id} for existing session."""
        # Create session
        create_response = client.post(
            "/api/v1/modes/sessions",
            json={"session_id": "test-delete-123"},
        )
        assert create_response.status_code == 201

        # Delete session
        response = client.delete("/api/v1/modes/sessions/test-delete-123")

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test-delete-123"

        # Verify session is gone
        get_response = client.get("/api/v1/modes/sessions/test-delete-123")
        assert get_response.status_code == 404

    def test_delete_nonexistent_session(self):
        """Test DELETE /sessions/{session_id} for non-existent session is idempotent."""
        response = client.delete("/api/v1/modes/sessions/nonexistent")

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()


class TestStatsEndpoints:
    """Test statistics and management endpoints."""

    def test_get_stats_no_sessions(self):
        """Test GET /stats with no active sessions."""
        response = client.get("/api/v1/modes/stats")

        assert response.status_code == 200

        data = response.json()
        assert data["default_mode"] == "full"
        assert data["active_sessions"] == 0
        assert len(data["available_modes"]) == 3

    def test_get_stats_with_sessions(self):
        """Test GET /stats with active sessions."""
        # Create some sessions
        client.post("/api/v1/modes/sessions", json={})
        client.post("/api/v1/modes/sessions", json={})

        response = client.get("/api/v1/modes/stats")

        assert response.status_code == 200

        data = response.json()
        assert data["active_sessions"] == 2

    def test_cleanup_endpoint(self):
        """Test POST /cleanup endpoint."""
        # Create session
        client.post("/api/v1/modes/sessions", json={})

        response = client.post("/api/v1/modes/cleanup")

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "sessions_removed" in data
        assert "message" in data


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_complete_session_lifecycle(self):
        """Test complete session lifecycle: create, get, update, delete."""
        # 1. Create session
        create_response = client.post(
            "/api/v1/modes/sessions",
            json={
                "session_id": "lifecycle-test",
                "mode": "base",
                "metadata": {"test": "lifecycle"},
            },
        )
        assert create_response.status_code == 201
        create_data = create_response.json()
        assert create_data["mode"] == "base"

        # 2. Get session
        get_response = client.get("/api/v1/modes/sessions/lifecycle-test")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["session_id"] == "lifecycle-test"
        assert get_data["mode"] == "base"

        # 3. Update session
        update_response = client.patch(
            "/api/v1/modes/sessions/lifecycle-test",
            json={"mode": "full"},
        )
        assert update_response.status_code == 200
        update_data = update_response.json()
        assert update_data["mode"] == "full"

        # 4. Verify update
        verify_response = client.get("/api/v1/modes/sessions/lifecycle-test")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["mode"] == "full"

        # 5. Delete session
        delete_response = client.delete("/api/v1/modes/sessions/lifecycle-test")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True

        # 6. Verify deletion
        final_response = client.get("/api/v1/modes/sessions/lifecycle-test")
        assert final_response.status_code == 404

    def test_multiple_sessions_independent(self):
        """Test that multiple sessions are independent."""
        # Create session 1
        response1 = client.post(
            "/api/v1/modes/sessions",
            json={
                "session_id": "session-1",
                "mode": "base",
            },
        )
        assert response1.status_code == 201

        # Create session 2
        response2 = client.post(
            "/api/v1/modes/sessions",
            json={
                "session_id": "session-2",
                "mode": "full",
            },
        )
        assert response2.status_code == 201

        # Verify both exist with correct modes
        get1 = client.get("/api/v1/modes/sessions/session-1")
        assert get1.json()["mode"] == "base"

        get2 = client.get("/api/v1/modes/sessions/session-2")
        assert get2.json()["mode"] == "full"

        # Update session 1
        client.patch(
            "/api/v1/modes/sessions/session-1",
            json={"mode": "base_adapter"},
        )

        # Verify session 2 unchanged
        get2_after = client.get("/api/v1/modes/sessions/session-2")
        assert get2_after.json()["mode"] == "full"

    def test_capability_driven_mode_selection(self):
        """Test workflow of checking capabilities before selecting mode."""
        # 1. Get all capabilities to understand options
        caps_response = client.get("/api/v1/modes/capabilities")
        assert caps_response.status_code == 200
        capabilities = caps_response.json()

        # 2. Check specific mode for details
        full_caps_response = client.get("/api/v1/modes/capabilities/full")
        assert full_caps_response.status_code == 200
        full_caps = full_caps_response.json()
        assert full_caps["features"]["has_rag"] is True

        # 3. Create session with chosen mode
        session_response = client.post(
            "/api/v1/modes/sessions",
            json={"mode": "full"},
        )
        assert session_response.status_code == 201
        assert session_response.json()["mode"] == "full"
