# Model Modes API Guide

## Overview

The Model Modes API allows you to configure the Kwanzaa question-answering system with three different modes, each offering different trade-offs between speed, accuracy, and resource usage.

**Base URL**: `/api/v1/modes`

## Quick Start

### 1. Check Available Modes

First, review the available modes and their capabilities:

```bash
curl -X GET http://localhost:8000/api/v1/modes/capabilities
```

**Response**:
```json
{
  "modes": {
    "base": {
      "mode": "base",
      "performance": {
        "relative_speed": 3.0,
        "memory_usage_mb": 2000
      },
      "features": {
        "has_adapter": false,
        "has_rag": false
      },
      "quality": {
        "kwanzaa_accuracy": "Low - No specialized knowledge",
        "general_capability": "Good - Standard LLM capabilities"
      },
      "usage": {
        "recommended_for": [
          "Testing model functionality",
          "General purpose queries",
          "Resource-constrained environments"
        ],
        "limitations": [
          "No Kwanzaa-specific training",
          "Cannot access document corpus",
          "May hallucinate facts"
        ]
      }
    },
    "base_adapter": { ... },
    "full": { ... }
  },
  "default_mode": "full"
}
```

### 2. Create a Session

Create a new session with your chosen mode:

```bash
curl -X POST http://localhost:8000/api/v1/modes/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "base_adapter",
    "metadata": {
      "user_id": "user-123"
    }
  }'
```

**Response**:
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "mode": "base_adapter",
  "created_at": "2025-01-16T10:30:00Z",
  "updated_at": "2025-01-16T10:30:00Z",
  "expires_at": "2025-01-16T11:30:00Z",
  "is_expired": false,
  "metadata": {
    "user_id": "user-123"
  }
}
```

### 3. Use Your Session

Include the session ID in your application requests to use the configured mode.

### 4. Change Mode (Optional)

Switch to a different mode during your session:

```bash
curl -X PATCH http://localhost:8000/api/v1/modes/sessions/f47ac10b-58cc-4372-a567-0e02b2c3d479 \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "full"
  }'
```

## API Endpoints

### Get All Mode Capabilities

Retrieve capabilities for all available modes.

**Endpoint**: `GET /api/v1/modes/capabilities`

**Response**: `200 OK`
```json
{
  "modes": {
    "base": { ... },
    "base_adapter": { ... },
    "full": { ... }
  },
  "default_mode": "full"
}
```

**Use Case**: Display mode options to users, help them make informed decisions.

---

### Get Specific Mode Capabilities

Get detailed information about a single mode.

**Endpoint**: `GET /api/v1/modes/capabilities/{mode}`

**Parameters**:
- `mode` (path): Mode identifier - `base`, `base_adapter`, or `full`

**Response**: `200 OK`
```json
{
  "mode": "base_adapter",
  "performance": {
    "relative_speed": 2.0,
    "memory_usage_mb": 2500
  },
  "features": {
    "has_adapter": true,
    "has_rag": false
  },
  "quality": {
    "kwanzaa_accuracy": "Medium - Trained on Kwanzaa corpus",
    "general_capability": "Good - Maintains base model capabilities"
  },
  "usage": {
    "recommended_for": [
      "Kwanzaa-specific question answering without citations",
      "Faster response times with Kwanzaa knowledge"
    ],
    "limitations": [
      "Cannot access document corpus",
      "No citation tracking"
    ]
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid mode identifier

---

### Create Session

Create a new session with a specific mode configuration.

**Endpoint**: `POST /api/v1/modes/sessions`

**Request Body**:
```json
{
  "mode": "base_adapter",           // Optional: defaults to "full"
  "session_id": "my-custom-id",     // Optional: auto-generated if not provided
  "ttl_minutes": 120,               // Optional: defaults to 60
  "metadata": {                     // Optional: arbitrary key-value data
    "user_id": "user-123",
    "app_version": "1.2.3"
  }
}
```

**Response**: `201 Created`
```json
{
  "session_id": "my-custom-id",
  "mode": "base_adapter",
  "created_at": "2025-01-16T10:30:00Z",
  "updated_at": "2025-01-16T10:30:00Z",
  "expires_at": "2025-01-16T12:30:00Z",
  "is_expired": false,
  "metadata": {
    "user_id": "user-123",
    "app_version": "1.2.3"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid mode or parameters

**Examples**:

**Minimal (use defaults)**:
```bash
curl -X POST http://localhost:8000/api/v1/modes/sessions \
  -H "Content-Type: application/json" \
  -d '{}'
```

**With custom mode**:
```bash
curl -X POST http://localhost:8000/api/v1/modes/sessions \
  -H "Content-Type: application/json" \
  -d '{"mode": "base"}'
```

**With custom session ID**:
```bash
curl -X POST http://localhost:8000/api/v1/modes/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123-session",
    "mode": "full"
  }'
```

**With extended TTL**:
```bash
curl -X POST http://localhost:8000/api/v1/modes/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "full",
    "ttl_minutes": 240
  }'
```

---

### Get Session

Retrieve information about an existing session.

**Endpoint**: `GET /api/v1/modes/sessions/{session_id}`

**Parameters**:
- `session_id` (path): Session identifier

**Response**: `200 OK`
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "mode": "base_adapter",
  "created_at": "2025-01-16T10:30:00Z",
  "updated_at": "2025-01-16T10:35:00Z",
  "expires_at": "2025-01-16T11:35:00Z",
  "is_expired": false,
  "metadata": {
    "user_id": "user-123"
  }
}
```

**Error Responses**:
- `404 Not Found`: Session does not exist or has expired

**Example**:
```bash
curl -X GET http://localhost:8000/api/v1/modes/sessions/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

---

### Update Session Mode

Change the mode for an existing session.

**Endpoint**: `PATCH /api/v1/modes/sessions/{session_id}`

**Parameters**:
- `session_id` (path): Session identifier

**Request Body**:
```json
{
  "mode": "full",              // Required: new mode
  "extend_ttl": true,          // Optional: extend expiration (default: true)
  "metadata": {                // Optional: merge with existing metadata
    "changed_at": "2025-01-16T10:40:00Z"
  }
}
```

**Response**: `200 OK`
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "mode": "full",
  "created_at": "2025-01-16T10:30:00Z",
  "updated_at": "2025-01-16T10:40:00Z",
  "expires_at": "2025-01-16T11:40:00Z",
  "is_expired": false,
  "metadata": {
    "user_id": "user-123",
    "changed_at": "2025-01-16T10:40:00Z"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid mode
- `404 Not Found`: Session does not exist or has expired

**Examples**:

**Change mode with TTL extension**:
```bash
curl -X PATCH http://localhost:8000/api/v1/modes/sessions/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"mode": "full"}'
```

**Change mode without extending TTL**:
```bash
curl -X PATCH http://localhost:8000/api/v1/modes/sessions/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "base_adapter",
    "extend_ttl": false
  }'
```

---

### Delete Session

Remove a session and free its resources.

**Endpoint**: `DELETE /api/v1/modes/sessions/{session_id}`

**Parameters**:
- `session_id` (path): Session identifier

**Response**: `200 OK`
```json
{
  "success": true,
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message": "Session deleted successfully"
}
```

**Note**: This operation is idempotent - returns success even if session doesn't exist.

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/modes/sessions/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

---

### Get System Statistics

Retrieve statistics about the mode management system.

**Endpoint**: `GET /api/v1/modes/stats`

**Response**: `200 OK`
```json
{
  "default_mode": "full",
  "active_sessions": 42,
  "available_modes": ["base", "base_adapter", "full"]
}
```

**Example**:
```bash
curl -X GET http://localhost:8000/api/v1/modes/stats
```

---

### Cleanup Expired Sessions

Manually trigger cleanup of expired sessions.

**Endpoint**: `POST /api/v1/modes/cleanup`

**Response**: `200 OK`
```json
{
  "success": true,
  "sessions_removed": 5,
  "message": "Cleaned up 5 expired session(s)"
}
```

**Note**: Sessions are automatically cleaned up when accessed, but this endpoint allows manual maintenance.

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/modes/cleanup
```

## Usage Patterns

### Pattern 1: Simple Mode Selection

Best for: Single-user applications, testing

```python
import requests

# Select mode once at startup
response = requests.post(
    "http://localhost:8000/api/v1/modes/sessions",
    json={"mode": "base_adapter"}
)
session = response.json()
SESSION_ID = session["session_id"]

# Use session ID throughout application lifecycle
# ... make requests with SESSION_ID ...
```

### Pattern 2: User Preference Storage

Best for: Multi-user applications with preferences

```python
import requests

def create_user_session(user_id: str, preferred_mode: str):
    """Create session with user preferences."""
    response = requests.post(
        "http://localhost:8000/api/v1/modes/sessions",
        json={
            "mode": preferred_mode,
            "metadata": {
                "user_id": user_id,
                "created_from": "web_app"
            }
        }
    )
    return response.json()

def get_user_mode(session_id: str):
    """Retrieve current mode for user."""
    response = requests.get(
        f"http://localhost:8000/api/v1/modes/sessions/{session_id}"
    )
    session = response.json()
    return session["mode"]
```

### Pattern 3: Dynamic Mode Switching

Best for: Interactive applications with mode selection UI

```python
import requests

class ModeManager:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = None

    def initialize(self, mode: str = "full"):
        """Initialize with a mode."""
        response = requests.post(
            f"{self.base_url}/api/v1/modes/sessions",
            json={"mode": mode}
        )
        session = response.json()
        self.session_id = session["session_id"]
        return session

    def switch_mode(self, new_mode: str):
        """Switch to different mode."""
        response = requests.patch(
            f"{self.base_url}/api/v1/modes/sessions/{self.session_id}",
            json={"mode": new_mode}
        )
        return response.json()

    def get_current_mode(self):
        """Get current session mode."""
        response = requests.get(
            f"{self.base_url}/api/v1/modes/sessions/{self.session_id}"
        )
        return response.json()["mode"]

# Usage
manager = ModeManager("http://localhost:8000")
manager.initialize(mode="base")
print(f"Current mode: {manager.get_current_mode()}")

# User decides to switch
manager.switch_mode("full")
print(f"New mode: {manager.get_current_mode()}")
```

### Pattern 4: Capability-Driven Selection

Best for: Applications that need to show trade-offs to users

```python
import requests

def get_modes_with_rag():
    """Get list of modes that support RAG."""
    response = requests.get("http://localhost:8000/api/v1/modes/capabilities")
    data = response.json()

    rag_modes = [
        mode_name
        for mode_name, mode_data in data["modes"].items()
        if mode_data["features"]["has_rag"]
    ]
    return rag_modes

def recommend_mode_for_query(query_requires_citations: bool):
    """Recommend mode based on query requirements."""
    if query_requires_citations:
        return "full"  # Only mode with RAG/citations
    else:
        return "base_adapter"  # Faster, still has Kwanzaa knowledge

# Usage
if user_needs_citations:
    mode = recommend_mode_for_query(True)
else:
    mode = recommend_mode_for_query(False)

# Create session with recommended mode
response = requests.post(
    "http://localhost:8000/api/v1/modes/sessions",
    json={"mode": mode}
)
```

## Mode Selection Decision Tree

```
Do you need citations and provenance?
├─ YES → Use "full" mode
└─ NO
   └─ Is query Kwanzaa-specific?
      ├─ YES → Use "base_adapter" mode (faster)
      └─ NO → Use "base" mode (fastest)
```

## Client Examples

### Python with Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/modes"

# Get capabilities
capabilities = requests.get(f"{BASE_URL}/capabilities").json()
print(f"Available modes: {capabilities['available_modes']}")

# Create session
session = requests.post(
    f"{BASE_URL}/sessions",
    json={"mode": "base_adapter"}
).json()
print(f"Session ID: {session['session_id']}")

# Update session
updated = requests.patch(
    f"{BASE_URL}/sessions/{session['session_id']}",
    json={"mode": "full"}
).json()
print(f"New mode: {updated['mode']}")

# Delete session
deleted = requests.delete(
    f"{BASE_URL}/sessions/{session['session_id']}"
).json()
print(f"Deleted: {deleted['success']}")
```

### JavaScript with Fetch

```javascript
const BASE_URL = 'http://localhost:8000/api/v1/modes';

// Get capabilities
async function getCapabilities() {
  const response = await fetch(`${BASE_URL}/capabilities`);
  return await response.json();
}

// Create session
async function createSession(mode = 'full') {
  const response = await fetch(`${BASE_URL}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode })
  });
  return await response.json();
}

// Update session
async function updateSession(sessionId, newMode) {
  const response = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: newMode })
  });
  return await response.json();
}

// Usage
const session = await createSession('base_adapter');
console.log('Session:', session.session_id);

const updated = await updateSession(session.session_id, 'full');
console.log('New mode:', updated.mode);
```

### cURL Examples

```bash
# Create session with full mode
curl -X POST http://localhost:8000/api/v1/modes/sessions \
  -H "Content-Type: application/json" \
  -d '{"mode": "full"}'

# Get session info
curl http://localhost:8000/api/v1/modes/sessions/SESSION_ID

# Update to base mode
curl -X PATCH http://localhost:8000/api/v1/modes/sessions/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"mode": "base"}'

# Get stats
curl http://localhost:8000/api/v1/modes/stats

# Delete session
curl -X DELETE http://localhost:8000/api/v1/modes/sessions/SESSION_ID
```

## Error Handling

### Common Error Responses

**400 Bad Request** - Invalid input
```json
{
  "detail": "Invalid mode: invalid_mode. Valid options: ['base', 'base_adapter', 'full']"
}
```

**404 Not Found** - Session not found
```json
{
  "detail": "Session not found or expired: nonexistent-id"
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Failed to create session: [error details]"
}
```

### Error Handling Example

```python
import requests

def safe_create_session(mode: str):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/modes/sessions",
            json={"mode": mode}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(f"Invalid mode: {mode}")
        elif e.response.status_code == 500:
            print("Server error, please try again")
        return None
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server")
        return None
```

## Best Practices

1. **Cache Capabilities**: Fetch mode capabilities once at startup, not per request
2. **Reuse Sessions**: Create sessions once and reuse them, don't create new sessions per request
3. **Handle Expiration**: Implement logic to recreate expired sessions gracefully
4. **Use Appropriate TTL**: Set TTL based on expected session duration (default 60 minutes)
5. **Store Session IDs**: Persist session IDs in user sessions, local storage, or cookies
6. **Monitor Mode Performance**: Track response times and accuracy by mode for your use case
7. **Provide Mode Selection UI**: Let users choose based on their speed/accuracy preferences
8. **Document Trade-offs**: Clearly communicate mode differences to end users

## Troubleshooting

### Session Not Found

**Problem**: `404 Not Found` when accessing session

**Solutions**:
- Check if session has expired (default 60 minutes)
- Verify session ID is correct
- Check if session was deleted
- Create new session if needed

### Invalid Mode Error

**Problem**: `400 Bad Request` with "Invalid mode" message

**Solutions**:
- Use only: `base`, `base_adapter`, or `full`
- Check for typos in mode name
- Verify mode string is lowercase

### High Memory Usage

**Problem**: Application using too much memory

**Solutions**:
- Switch to `base` or `base_adapter` mode (lower memory)
- Review number of active sessions
- Run cleanup to remove expired sessions
- Consider session TTL reduction

## Related Documentation

- [Model Modes Architecture](../architecture/model-modes.md)
- [Semantic Search API](./semantic-search-api.md)
- [Configuration Guide](../development/configuration.md)

## Support

For issues or questions:
- GitHub Issues: https://github.com/AINative-Studio/kwanzaa/issues
- Documentation: https://github.com/AINative-Studio/kwanzaa/docs
