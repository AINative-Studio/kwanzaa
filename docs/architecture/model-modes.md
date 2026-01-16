# Model Mode System Architecture

## Overview

The Kwanzaa model mode system provides flexible configuration of the question-answering pipeline, allowing users to choose between different levels of capability, performance, and resource usage based on their specific needs.

## Modes

### 1. Base Mode (`base`)

**Description**: Just the base language model without any Kwanzaa-specific training or retrieval augmentation.

**Components**:
- Base LLM (AI2, LLaMA, or DeepSeek)
- No adapter loaded
- No RAG/semantic search

**Performance Characteristics**:
- **Speed**: 3x faster than full mode
- **Memory**: ~2000 MB
- **Accuracy**: Low for Kwanzaa-specific queries

**When to Use**:
- Testing model functionality
- General purpose queries not specific to Kwanzaa
- Resource-constrained environments
- Quick prototyping

**Limitations**:
- No Kwanzaa-specific training or knowledge
- Cannot access document corpus via RAG
- May hallucinate Kwanzaa-related facts
- No provenance or citation capabilities

### 2. Base + Adapter Mode (`base_adapter`)

**Description**: Base model with the Kwanzaa adapter loaded, providing specialized knowledge without retrieval.

**Components**:
- Base LLM (AI2, LLaMA, or DeepSeek)
- Kwanzaa QLora adapter (trained on Kwanzaa corpus)
- No RAG/semantic search

**Performance Characteristics**:
- **Speed**: 2x faster than full mode
- **Memory**: ~2500 MB
- **Accuracy**: Medium for Kwanzaa-specific queries

**When to Use**:
- Kwanzaa-specific question answering without citations
- Contexts where RAG/search is not needed
- Faster response times with Kwanzaa knowledge
- Offline or disconnected environments

**Limitations**:
- Cannot access document corpus for grounding
- No citation or provenance tracking
- Knowledge limited to training data
- May still hallucinate for edge cases

### 3. Full Mode (`full`) - DEFAULT

**Description**: Complete system with base model, adapter, and retrieval-augmented generation.

**Components**:
- Base LLM (AI2, LLaMA, or DeepSeek)
- Kwanzaa QLora adapter
- RAG with semantic search over document corpus
- Provenance tracking and citation

**Performance Characteristics**:
- **Speed**: 1x (baseline)
- **Memory**: ~3000 MB
- **Accuracy**: High for Kwanzaa-specific queries

**When to Use**:
- Production use cases requiring accuracy
- Research and educational applications
- Queries requiring citations and provenance
- Any use case where accuracy is critical

**Limitations**:
- Slower due to RAG retrieval step
- Requires vector database connectivity
- Higher memory and compute requirements
- Network latency for remote vector DB

## Architecture Components

### Mode Manager

The `ModeManager` class is the central component that coordinates mode selection and session management.

**Key Responsibilities**:
- Validate mode selections
- Manage session lifecycle
- Track session state and expiration
- Provide capability information

**Location**: `/Users/aideveloper/kwanzaa/backend/app/core/modes.py`

### Session Store

The `ModeSessionStore` class manages per-session mode preferences.

**Features**:
- In-memory session storage
- Configurable TTL (time-to-live)
- Automatic expiration and cleanup
- Session metadata support

**Storage Strategy**:
- Current: In-memory dictionary (single-process)
- Future: Redis or distributed cache for multi-worker deployments

### Session Model

Each session tracks:
- **session_id**: Unique identifier
- **mode**: Selected ModelMode
- **created_at**: Session creation timestamp
- **updated_at**: Last modification timestamp
- **expires_at**: Expiration timestamp
- **metadata**: Arbitrary key-value data

## API Design

### Endpoints

The mode system exposes RESTful API endpoints under `/api/v1/modes`:

```
GET    /capabilities           - List all mode capabilities
GET    /capabilities/{mode}    - Get specific mode capabilities
POST   /sessions               - Create new session
GET    /sessions/{session_id}  - Get session information
PATCH  /sessions/{session_id}  - Update session mode
DELETE /sessions/{session_id}  - Delete session
GET    /stats                  - Get system statistics
POST   /cleanup                - Cleanup expired sessions
```

### Request/Response Models

All API models are defined using Pydantic for validation:
- `SessionCreateRequest`: Create new session
- `SessionResponse`: Session information
- `ModeUpdateRequest`: Update session mode
- `ModeCapabilitiesResponse`: Mode capabilities
- `AllCapabilitiesResponse`: All modes' capabilities
- `ModeStatsResponse`: System statistics

**Location**: `/Users/aideveloper/kwanzaa/backend/app/models/modes.py`

## Configuration

### Environment Variables

Mode system configuration is part of the main application settings:

```bash
# Default mode for new sessions (base, base_adapter, full)
DEFAULT_MODEL_MODE=full

# Session TTL in minutes (1-1440)
SESSION_TTL_MINUTES=60
```

### Settings Class

Configuration is loaded via the `Settings` class:

```python
from app.core.config import settings

default_mode = settings.DEFAULT_MODEL_MODE
session_ttl = settings.SESSION_TTL_MINUTES
```

## Session Lifecycle

### 1. Creation

Sessions can be created explicitly via API or implicitly:

```python
# Explicit creation
POST /api/v1/modes/sessions
{
  "mode": "base_adapter",
  "session_id": "optional-custom-id",
  "ttl_minutes": 120,
  "metadata": {"user_id": "user-123"}
}

# Implicit creation (on first use)
# Session created with default mode if not exists
```

### 2. Active Use

During the session lifetime:
- Mode can be changed via PATCH
- Session is automatically extended on updates (configurable)
- Metadata can be added or updated

### 3. Expiration

Sessions expire after TTL:
- Expired sessions return 404 on retrieval
- Automatic cleanup removes expired sessions
- Manual cleanup available via `/cleanup` endpoint

### 4. Deletion

Explicit session deletion:
- Removes session immediately
- Idempotent operation (safe to call multiple times)
- Returns success status

## Integration with Application

### Dependency Injection

The mode manager is injected into API endpoints:

```python
from app.core.modes import ModeManager, get_mode_manager

def get_manager() -> ModeManager:
    default_mode = ModelMode(settings.DEFAULT_MODEL_MODE)
    return get_mode_manager(default_mode=default_mode)

@router.get("/example")
async def example(manager: ModeManager = Depends(get_manager)):
    session = manager.get_session(session_id)
    mode = session.mode if session else manager.default_mode
    # Use mode to configure model behavior
```

### Using Mode in Model Selection

```python
from app.core.modes import ModelMode

# Get session mode
mode = manager.get_session_mode(session_id)

# Configure model based on mode
if mode == ModelMode.BASE:
    # Load base model only
    model = load_base_model()
elif mode == ModelMode.BASE_ADAPTER:
    # Load base + adapter
    model = load_base_model()
    model.load_adapter(adapter_path)
elif mode == ModelMode.FULL:
    # Load base + adapter + enable RAG
    model = load_base_model()
    model.load_adapter(adapter_path)
    enable_rag = True
```

## Testing

### Unit Tests

Comprehensive unit tests cover:
- Mode enum values and validation
- Capability definitions
- Session creation and lifecycle
- Session store operations
- Mode manager functionality

**Location**: `/Users/aideveloper/kwanzaa/backend/tests/test_modes.py`

**Coverage**: 99% of `app/core/modes.py`

### Integration Tests

API endpoint tests cover:
- All CRUD operations on sessions
- Capability retrieval
- Error handling
- End-to-end workflows

**Location**: `/Users/aideveloper/kwanzaa/backend/tests/test_api_modes.py`

## Performance Considerations

### Memory Usage

Mode selection directly impacts memory:
- **Base**: ~2000 MB (base model only)
- **Base+Adapter**: ~2500 MB (+ adapter weights)
- **Full**: ~3000 MB (+ RAG infrastructure)

### Response Time

Relative performance (Full mode = 1.0x baseline):
- **Base**: 3.0x faster
- **Base+Adapter**: 2.0x faster
- **Full**: 1.0x (baseline)

RAG retrieval adds latency:
- Embedding generation: ~10-50ms
- Vector search: ~20-100ms
- Total overhead: ~30-150ms

### Scalability

**Current Implementation**:
- In-memory session store
- Suitable for single-process deployments
- Session data lost on restart

**Recommended for Production**:
- Redis-backed session store
- Distributed across multiple workers
- Persistent session data
- Horizontal scaling support

## Security Considerations

### Session Security

- Session IDs are UUIDs (difficult to guess)
- No authentication required for mode selection (application-level auth separate)
- Sessions automatically expire (configurable TTL)
- Session metadata should not contain sensitive data

### Input Validation

- All mode strings validated against enum
- TTL limited to 1-1440 minutes (max 24 hours)
- Session IDs length-limited
- Metadata validated as JSON

## Future Enhancements

### Planned Improvements

1. **Redis Backend**
   - Distributed session storage
   - Cross-worker session sharing
   - Persistent sessions

2. **Mode Analytics**
   - Track mode usage patterns
   - Performance metrics by mode
   - Usage recommendations

3. **Dynamic Mode Switching**
   - Automatic mode degradation on errors
   - Smart mode selection based on query
   - A/B testing support

4. **Advanced Features**
   - Mode presets (personas)
   - Custom mode configurations
   - Mode-specific rate limiting
   - Cost tracking by mode

## References

- **Core Implementation**: `/Users/aideveloper/kwanzaa/backend/app/core/modes.py`
- **API Models**: `/Users/aideveloper/kwanzaa/backend/app/models/modes.py`
- **API Endpoints**: `/Users/aideveloper/kwanzaa/backend/app/api/v1/endpoints/modes.py`
- **Unit Tests**: `/Users/aideveloper/kwanzaa/backend/tests/test_modes.py`
- **Integration Tests**: `/Users/aideveloper/kwanzaa/backend/tests/test_api_modes.py`
- **API Usage Guide**: [Model Modes API Guide](../api/model-modes-api.md)
