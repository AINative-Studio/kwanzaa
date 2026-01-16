# Answer JSON Enforcement - Integration Guide

**Epic 8 - Issue #26**
**For:** Development Team
**Date:** 2026-01-16

## Quick Start Integration

This guide shows how to integrate the answer_json enforcement system into your FastAPI application.

## Step 1: Add Middleware to main.py

Update `/backend/app/main.py` to include the validation middleware:

```python
"""Kwanzaa FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.v1.endpoints import modes, search
from app.core.config import settings
from app.core.errors import (
    APIError,
    api_error_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_error_handler,
)
# ADD THIS IMPORT
from app.middleware.answer_validation import AnswerJsonValidationMiddleware

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    Kwanzaa Semantic Search API
    ...
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ADD THIS: Answer JSON Validation Middleware
app.add_middleware(
    AnswerJsonValidationMiddleware,
    enabled=True,              # Enable validation
    log_all_validations=True,  # Log all validation attempts
    strict_mode=True,          # Strict mode for production
)

# Register error handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ... rest of the file
```

## Step 2: Create RAG Query Endpoint

Create a new file `/backend/app/api/v1/endpoints/rag.py`:

```python
"""RAG query endpoints with answer_json enforcement."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.models.answer_json import AnswerJsonContract, Persona, ModelMode
from app.utils.response_enforcement import enforce_answer_json_response

router = APIRouter()


class QueryRequest(BaseModel):
    """RAG query request."""

    query: str = Field(..., min_length=1, max_length=1000)
    persona: Persona = Field(default=Persona.EDUCATOR)
    model_mode: ModelMode = Field(default=ModelMode.BASE_ADAPTER_RAG)
    require_citations: bool = Field(default=True)
    primary_sources_only: bool = Field(default=False)
    creative_mode: bool = Field(default=False)


@router.post(
    "/query",
    response_model=AnswerJsonContract,
    status_code=status.HTTP_200_OK,
    summary="Query RAG system",
    description="""
    Query the RAG system with automatic answer_json validation.

    All responses are guaranteed to conform to the answer_json contract,
    ensuring complete provenance transparency and explicit handling of unknowns.
    """,
    responses={
        200: {
            "description": "Valid answer_json response",
            "model": AnswerJsonContract,
        },
        400: {"description": "Invalid request"},
        422: {"description": "Response validation failed"},
        500: {"description": "Internal server error"},
    },
    tags=["rag"],
)
@enforce_answer_json_response(strict=True, log_failures=True)
async def query_rag(request: QueryRequest) -> dict:
    """Query RAG system with validation enforcement.

    This endpoint demonstrates the answer_json enforcement:
    - Returns only valid answer_json responses
    - Middleware validates before sending to client
    - 422 error if response doesn't conform to schema

    Args:
        request: Query request with persona and toggles

    Returns:
        Validated answer_json response

    Raises:
        HTTPException: If validation fails or query fails
    """
    # TODO: Implement actual RAG query logic
    # For now, return a valid mock response

    from datetime import datetime, timezone
    from uuid import uuid4

    return {
        "version": "kwanzaa.answer.v1",
        "persona": request.persona,
        "model_mode": request.model_mode,
        "toggles": {
            "require_citations": request.require_citations,
            "primary_sources_only": request.primary_sources_only,
            "creative_mode": request.creative_mode,
        },
        "answer": {
            "text": f"This is a response to: {request.query}",
            "confidence": 0.92,
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": [],  # TODO: Add actual sources from retrieval
        "retrieval_summary": {
            "query": request.query,
            "top_k": 10,
            "namespaces": ["kwanzaa_primary_sources"],
            "results": [],  # TODO: Add actual retrieval results
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        },
        "integrity": {
            "citation_required": request.require_citations,
            "citations_provided": False,  # TODO: Update based on actual sources
            "retrieval_confidence": "high",
            "fallback_behavior": "not_needed",
        },
        "provenance": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "retrieval_run_id": str(uuid4()),
            "assistant_message_id": str(uuid4()),
        },
    }
```

## Step 3: Register RAG Router

Update `/backend/app/main.py` to include the RAG router:

```python
# Import the RAG router
from app.api.v1.endpoints import modes, rag, search

# ... (middleware setup)

# Include routers
app.include_router(
    search.router,
    prefix=f"{settings.API_V1_PREFIX}/search",
    tags=["search"],
)
app.include_router(
    modes.router,
    prefix=f"{settings.API_V1_PREFIX}/modes",
    tags=["modes"],
)
# ADD THIS
app.include_router(
    rag.router,
    prefix=f"{settings.API_V1_PREFIX}/rag",
    tags=["rag"],
)
```

## Step 4: Test the Integration

### 4.1 Start the Application

```bash
cd /Users/aideveloper/kwanzaa/backend
uvicorn app.main:app --reload --port 8000
```

### 4.2 Test Valid Request

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Kwanzaa?",
    "persona": "educator",
    "model_mode": "base_adapter_rag",
    "require_citations": true
  }'
```

**Expected:** 200 OK with valid answer_json response

### 4.3 Test Invalid Response (Internal)

Temporarily modify the endpoint to return invalid data:

```python
@router.post("/query")
async def query_rag(request: QueryRequest) -> dict:
    # This will be rejected by middleware
    return {"invalid": "response"}
```

**Expected:** 422 Unprocessable Entity with validation errors

## Step 5: Monitor Validation

### Check Logs

```bash
# View validation events
tail -f logs/app.log | grep "validation"

# View only failures
tail -f logs/app.log | grep "validation.failed"
```

### Access Metrics (when AIKit SDK is integrated)

```python
from app.middleware.observability import get_validation_statistics

# Get recent validation stats
stats = await get_validation_statistics(
    endpoint="/api/v1/rag/query",
    time_window_minutes=60,
)

print(f"Pass rate: {stats['pass_rate']:.1%}")
print(f"Total requests: {stats['total_requests']}")
print(f"Failures: {stats['failed_validations']}")
```

## Configuration Options

### Environment Variables

Add to `.env`:

```bash
# Answer JSON Validation
ANSWER_JSON_VALIDATION_ENABLED=true
ANSWER_JSON_STRICT_MODE=true
ANSWER_JSON_LOG_ALL_VALIDATIONS=true

# Observability
AIKIT_OBSERVABILITY_ENABLED=true
AIKIT_API_KEY=your_api_key_here
```

### Settings

Update `/backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings

    # Answer JSON Validation Settings
    ANSWER_JSON_VALIDATION_ENABLED: bool = Field(
        default=True,
        description="Enable answer_json validation middleware",
    )
    ANSWER_JSON_STRICT_MODE: bool = Field(
        default=True,
        description="Strict mode returns 422 for invalid responses",
    )
    ANSWER_JSON_LOG_ALL_VALIDATIONS: bool = Field(
        default=False,
        description="Log all validation attempts (not just failures)",
    )

    # Observability Settings
    AIKIT_OBSERVABILITY_ENABLED: bool = Field(
        default=True,
        description="Enable AIKit observability tracking",
    )
    AIKIT_API_KEY: str = Field(
        default="",
        description="AIKit API key for observability",
    )
```

Then update middleware initialization:

```python
from app.core.config import settings

app.add_middleware(
    AnswerJsonValidationMiddleware,
    enabled=settings.ANSWER_JSON_VALIDATION_ENABLED,
    log_all_validations=settings.ANSWER_JSON_LOG_ALL_VALIDATIONS,
    strict_mode=settings.ANSWER_JSON_STRICT_MODE,
)
```

## Troubleshooting

### Issue: Middleware Not Validating

**Symptom:** Invalid responses pass through without validation

**Solution:**
1. Check middleware is added to app: `app.middleware_stack`
2. Verify middleware is enabled: `enabled=True`
3. Check endpoint path matches validation patterns

### Issue: All Responses Return 422

**Symptom:** Every response fails validation

**Solution:**
1. Review response structure matches answer_json schema
2. Check all required fields are present
3. Run validation demo: `python -m backend.examples.answer_json_enforcement_demo`
4. Enable debug logging to see specific errors

### Issue: Performance Degradation

**Symptom:** Slow response times after adding middleware

**Solution:**
1. Disable `log_all_validations` (only log failures)
2. Implement response caching
3. Monitor validation processing time metrics

## Best Practices

### 1. Always Use Response Model

```python
# Good
@router.post("/query", response_model=AnswerJsonContract)
async def query(...) -> dict:
    ...

# Bad
@router.post("/query")
async def query(...) -> dict:
    ...
```

### 2. Use the Decorator

```python
# Good - Double validation
@router.post("/query", response_model=AnswerJsonContract)
@enforce_answer_json_response()
async def query(...) -> dict:
    ...

# Less safe - Only middleware validation
@router.post("/query", response_model=AnswerJsonContract)
async def query(...) -> dict:
    ...
```

### 3. Handle Errors Gracefully

```python
from app.utils.answer_validation import AnswerValidationError

try:
    response = build_answer_json(...)
    validated = validate_answer_json(response)
    return validated
except AnswerValidationError as e:
    logger.error(f"Validation failed: {e.message}")
    # Fix the response or return error
    raise HTTPException(status_code=422, detail=e.to_dict())
```

### 4. Test Both Valid and Invalid Cases

```python
def test_query_endpoint():
    # Test valid response
    valid_request = {...}
    response = client.post("/rag/query", json=valid_request)
    assert response.status_code == 200

    # Test would-be invalid response
    # (Middleware catches internal validation failures)
    # Mock the endpoint to return invalid data
    with mock_invalid_response():
        response = client.post("/rag/query", json=valid_request)
        assert response.status_code == 422
```

## Deployment Checklist

Before deploying to production:

- [ ] Middleware added to main.py
- [ ] All RAG endpoints use `response_model=AnswerJsonContract`
- [ ] Decorator applied to RAG endpoints
- [ ] Environment variables configured
- [ ] Tests passing (66+ tests)
- [ ] Documentation reviewed
- [ ] Observability configured
- [ ] Monitoring alerts set up
- [ ] Team trained on validation errors

## Next Steps

1. **Integrate with RAG Orchestration**
   - Implement actual RAG query logic
   - Add real source retrieval
   - Connect to semantic search

2. **Enable Observability**
   - Integrate AIKit SDK
   - Set up dashboards
   - Configure alerts

3. **Optimize Performance**
   - Add response caching
   - Implement validation caching
   - Monitor processing times

## Resources

- **Full Documentation:** `/docs/api/answer-json-enforcement.md`
- **Examples:** `/backend/examples/answer_json_enforcement_demo.py`
- **Tests:** `/backend/tests/unit/` and `/backend/tests/integration/`
- **Schema:** `/backend/app/schemas/answer_json.schema.json`
- **Models:** `/backend/app/models/answer_json.py`

## Support

For questions or issues:
- **GitHub:** [Issue #26](https://github.com/AINative-Studio/kwanzaa/issues/26)
- **Slack:** #kwanzaa-dev
- **Docs:** See above resources

---

**Status:** Ready for Integration
**Estimated Integration Time:** 30-60 minutes
**Risk Level:** Low (comprehensive tests, extensive documentation)
