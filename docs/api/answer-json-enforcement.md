# Answer JSON Output Compliance Enforcement

**Epic 8 - Issue #26**
**Version:** 1.0.0
**Last Updated:** 2026-01-16

## Overview

This document describes the output compliance enforcement system for the `answer_json` contract. The enforcement layer ensures that **100% of AI responses conform to the schema**, preventing raw text blobs from reaching the UI and ensuring complete provenance transparency.

## Core Principles

### Zero Tolerance for Non-Compliance

- **No raw text blobs:** All responses must be structured JSON conforming to the schema
- **No UI rendering of unstructured data:** The UI never receives unvalidated responses
- **100% provenance transparency:** Every response includes complete source tracking
- **Explicit uncertainty:** All unknowns and limitations are declared

### Enforcement at Multiple Layers

1. **Response Model Layer:** Pydantic models enforce type safety
2. **Decorator Layer:** Function decorators validate before returning
3. **Middleware Layer:** FastAPI middleware validates all responses
4. **Observability Layer:** AIKit tracks all validation events

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Request                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Endpoint Handler                    │
│  @enforce_answer_json_response()                        │
│  async def query(...) -> AnswerJsonContract             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           Response Model Validation                      │
│  - Pydantic validation                                  │
│  - Type checking                                        │
│  - Field constraints                                    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│       AnswerJsonValidationMiddleware                    │
│  - Schema validation                                    │
│  - Error handling                                       │
│  - 422 responses for violations                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│         AIKit Observability Tracking                    │
│  - Log validation success/failure                       │
│  - Track metrics                                        │
│  - Monitor compliance rates                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Validated Response to Client                │
│  (or 422 Validation Error)                              │
└─────────────────────────────────────────────────────────┘
```

## Implementation Components

### 1. Validation Middleware

**Location:** `backend/app/middleware/answer_validation.py`

The `AnswerJsonValidationMiddleware` intercepts all responses and validates them against the schema.

**Features:**
- Automatic validation for endpoints returning `answer_json`
- Detailed error messages with field-level validation failures
- Development vs production error handling modes
- Integration with AIKit observability

**Configuration:**

```python
from app.middleware.answer_validation import AnswerJsonValidationMiddleware

app.add_middleware(
    AnswerJsonValidationMiddleware,
    enabled=True,              # Enable/disable validation
    log_all_validations=True,  # Log all attempts (not just failures)
    strict_mode=True,          # Raise errors in production
)
```

**Behavior:**

- **Strict Mode (Production):** Returns 422 for invalid responses
- **Non-Strict Mode (Development):** Logs warnings but allows responses
- **Disabled:** Bypasses validation (not recommended)

### 2. Response Model Enforcement

**Location:** `backend/app/utils/response_enforcement.py`

Provides decorators and utilities for route-level validation.

#### Decorator Usage

```python
from fastapi import APIRouter
from app.models.answer_json import AnswerJsonContract
from app.utils.response_enforcement import enforce_answer_json_response

router = APIRouter()

@router.post("/rag/query", response_model=AnswerJsonContract)
@enforce_answer_json_response(strict=True, log_failures=True)
async def query_rag(request: QueryRequest) -> dict:
    # Generate response
    response = await rag_service.query(request)

    # Decorator validates before returning
    return response
```

#### Validation Utility

```python
from app.utils.response_enforcement import validate_and_convert_response

# Validate and convert to Pydantic model
try:
    validated = validate_and_convert_response(response_dict)
    return validated
except AnswerValidationError as e:
    # Handle validation error
    logger.error(f"Validation failed: {e.message}")
    for error in e.errors:
        logger.error(f"  {error.field}: {error.message}")
```

#### Batch Validation

```python
from app.utils.response_enforcement import AnswerJsonResponseValidator

validator = AnswerJsonResponseValidator()

# Validate multiple responses
valid_responses, errors = validator.validate_batch(
    responses=[response1, response2, response3],
    fail_fast=False,  # Continue on errors
)

print(f"Valid: {len(valid_responses)}, Invalid: {len(errors)}")
```

#### Error Recovery

```python
# Attempt to fix common validation issues
recovered = validator.attempt_error_recovery(invalid_response)

if recovered:
    # Successfully recovered
    return recovered
else:
    # Recovery failed - return error
    raise AnswerValidationError(...)
```

### 3. AIKit Observability Integration

**Location:** `backend/app/middleware/observability.py`

Tracks validation events and metrics for monitoring compliance.

**Tracked Events:**

- `validation.success` - Successful validation
- `validation.failed` - Validation failure with error details
- `validation.additional_info` - Additional context

**Tracked Metrics:**

- `validation.pass_rate` - Percentage of successful validations
- `validation.processing_time_ms` - Validation processing time
- `validation.failures` - Count of validation failures

**Usage:**

```python
from app.middleware.observability import track_validation_event

await track_validation_event(
    request=request,
    success=False,
    errors=validation_errors,
    processing_time_ms=45,
)
```

## Validation Error Response Format

When validation fails, the API returns a **422 Unprocessable Entity** response:

```json
{
  "status": "error",
  "error_code": "ANSWER_JSON_VALIDATION_FAILED",
  "message": "Response does not conform to answer_json contract",
  "details": {
    "validation_errors": [
      {
        "field": "answer.text",
        "message": "Field required",
        "error_type": "missing",
        "location": ["answer", "text"]
      },
      {
        "field": "sources",
        "message": "Expected array",
        "error_type": "type_error",
        "location": ["sources"]
      }
    ],
    "error_count": 2,
    "suggestion": "Ensure the response includes all required fields: version, answer, sources, retrieval_summary, unknowns"
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Response Fields

- `status`: Always "error"
- `error_code`: Machine-readable error code
- `message`: Human-readable error message
- `details.validation_errors`: Array of specific validation failures
  - `field`: Dot-notation path to the failed field
  - `message`: Error message for this field
  - `error_type`: Type of validation error
  - `location`: Array path to the error location
- `details.error_count`: Total number of errors
- `details.suggestion`: Helpful suggestion for fixing the issue
- `request_id`: Request correlation ID (if provided)

## Common Validation Errors and Solutions

### 1. Missing Required Fields

**Error:**
```json
{
  "field": "retrieval_summary",
  "message": "Field required",
  "error_type": "missing"
}
```

**Solution:**
```python
# Ensure all required top-level fields are present
response = {
    "version": "kwanzaa.answer.v1",
    "answer": {...},
    "sources": [...],
    "retrieval_summary": {...},  # Required!
    "unknowns": {...},            # Required!
}
```

### 2. Invalid Version Pattern

**Error:**
```json
{
  "field": "version",
  "message": "String should match pattern '^kwanzaa\\.answer\\.v[0-9]+$'",
  "error_type": "string_pattern_mismatch"
}
```

**Solution:**
```python
response = {
    "version": "kwanzaa.answer.v1",  # Must follow pattern
    # ...
}
```

### 3. Empty Answer Text

**Error:**
```json
{
  "field": "answer.text",
  "message": "String should have at least 1 character",
  "error_type": "string_too_short"
}
```

**Solution:**
```python
response = {
    "answer": {
        "text": "This is a valid answer with content.",  # Not empty!
        "confidence": 0.9,
        "tone": "neutral",
        "completeness": "complete",
    }
}
```

### 4. Invalid Confidence Range

**Error:**
```json
{
  "field": "answer.confidence",
  "message": "Input should be less than or equal to 1",
  "error_type": "less_than_equal"
}
```

**Solution:**
```python
response = {
    "answer": {
        "confidence": 0.95,  # Must be 0.0 to 1.0
        # ...
    }
}
```

### 5. Missing Source Fields

**Error:**
```json
{
  "field": "sources.0.canonical_url",
  "message": "Field required",
  "error_type": "missing"
}
```

**Solution:**
```python
# All source fields are required
source = {
    "citation_label": "National Archives (1964) — Civil Rights Act",
    "canonical_url": "https://www.archives.gov/...",  # Required
    "source_org": "National Archives",                # Required
    "year": 1964,                                     # Required
    "content_type": "proclamation",                   # Required
    "license": "Public Domain",                       # Required
    "namespace": "kwanzaa_primary_sources",          # Required
    "doc_id": "nara_cra_1964",                       # Required
    "chunk_id": "nara_cra_1964::chunk::3",           # Required
}
```

### 6. Invalid URL Format

**Error:**
```json
{
  "field": "sources.0.canonical_url",
  "message": "Input should be a valid URL",
  "error_type": "url_parsing"
}
```

**Solution:**
```python
source = {
    "canonical_url": "https://www.archives.gov/doc",  # Must be valid URL
    # Not: "not-a-valid-url"
}
```

### 7. Empty Unknowns Arrays

**Not an Error!** The `unknowns` section can have empty arrays:

```python
# This is valid
response = {
    "unknowns": {
        "unsupported_claims": [],          # Can be empty
        "missing_context": [],             # Can be empty
        "clarifying_questions": [],        # Can be empty
    }
}
```

## Preventing Raw Text Blobs

### Problem: Raw Text Responses

**Bad - This will be rejected:**

```python
@router.post("/query")
async def query_endpoint(request: QueryRequest):
    # Generate answer
    answer_text = await model.generate(request.query)

    # Returning raw text blob - NO!
    return {"response": answer_text}
```

### Solution: Structured answer_json Response

**Good - This will pass validation:**

```python
@router.post("/query", response_model=AnswerJsonContract)
@enforce_answer_json_response()
async def query_endpoint(request: QueryRequest):
    # Generate answer with full provenance
    answer_text = await model.generate(request.query)

    # Retrieve sources
    sources = await retrieval_service.get_sources(request.query)

    # Build complete answer_json response
    return {
        "version": "kwanzaa.answer.v1",
        "persona": "educator",
        "model_mode": "base_adapter_rag",
        "toggles": {
            "require_citations": True,
            "primary_sources_only": False,
            "creative_mode": False,
        },
        "answer": {
            "text": answer_text,
            "confidence": 0.92,
            "tone": "neutral",
            "completeness": "complete",
        },
        "sources": sources,
        "retrieval_summary": {
            "query": request.query,
            "top_k": 10,
            "namespaces": ["kwanzaa_primary_sources"],
            "results": retrieval_results,
        },
        "unknowns": {
            "unsupported_claims": [],
            "missing_context": [],
            "clarifying_questions": [],
        },
        "integrity": {
            "citation_required": True,
            "citations_provided": len(sources) > 0,
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

## Streaming Response Validation

For streaming responses, validation is performed on chunks:

```python
from app.utils.response_enforcement import AnswerJsonResponseValidator

validator = AnswerJsonResponseValidator()

async def stream_response(request: QueryRequest):
    # Stream intermediate chunks
    for chunk in generate_stream():
        # Validate intermediate chunk (relaxed validation)
        if not validator.validate_streaming_chunk(chunk, is_final_chunk=False):
            logger.warning("Invalid intermediate chunk")

        yield chunk

    # Final chunk must pass full validation
    final_chunk = build_final_response()
    if not validator.validate_streaming_chunk(final_chunk, is_final_chunk=True):
        raise AnswerValidationError("Final chunk validation failed")

    yield final_chunk
```

## Testing

### Running Validation Tests

```bash
# Run all validation tests
pytest backend/tests/unit/test_answer_validation.py -v

# Run response enforcement tests
pytest backend/tests/unit/test_response_enforcement.py -v

# Run middleware integration tests
pytest backend/tests/integration/test_answer_validation_middleware.py -v

# Run with coverage
pytest --cov=app.utils.answer_validation \
       --cov=app.utils.response_enforcement \
       --cov=app.middleware.answer_validation \
       --cov-report=html
```

### Test Coverage Goals

- **Target:** 100% coverage for validation utilities
- **Minimum:** 80% coverage for all enforcement components

## Monitoring and Observability

### Validation Metrics Dashboard

Track these metrics in your observability platform:

```python
# Pass rate by endpoint
validation.pass_rate{endpoint="/api/v1/rag/query"}

# Total validation attempts
validation.total_requests{endpoint="/api/v1/rag/query"}

# Failed validations
validation.failed{endpoint="/api/v1/rag/query"}

# Processing time
validation.processing_time_ms{endpoint="/api/v1/rag/query"}
```

### Alerts

Set up alerts for validation issues:

```yaml
alerts:
  - name: LowValidationPassRate
    condition: validation.pass_rate < 0.95
    severity: warning
    message: "Validation pass rate below 95%"

  - name: HighValidationFailureRate
    condition: validation.failed > 10/minute
    severity: critical
    message: "High validation failure rate detected"
```

## Best Practices

### 1. Always Use Response Models

```python
# Good
@router.post("/query", response_model=AnswerJsonContract)
async def query(...) -> AnswerJsonContract:
    ...

# Bad - No type safety
@router.post("/query")
async def query(...) -> dict:
    ...
```

### 2. Use the Decorator

```python
# Good - Validation enforced
@router.post("/query", response_model=AnswerJsonContract)
@enforce_answer_json_response()
async def query(...):
    ...

# Less safe - Relies only on middleware
@router.post("/query", response_model=AnswerJsonContract)
async def query(...):
    ...
```

### 3. Handle Validation Errors Gracefully

```python
from app.utils.answer_validation import AnswerValidationError

try:
    validated = validate_answer_json(response_data)
    return validated
except AnswerValidationError as e:
    # Log detailed errors
    logger.error(f"Validation failed: {e.message}")
    for error in e.errors:
        logger.error(f"  {error.field}: {error.message}")

    # Return proper error response
    raise HTTPException(
        status_code=422,
        detail=create_validation_error_response(e),
    )
```

### 4. Use Helper Functions

```python
from app.models.answer_json import create_answer_json_contract

# Use helper to build valid responses
response = create_answer_json_contract(
    answer="The answer text",
    query="The query",
    sources=sources,
    retrieval_results=results,
)
```

### 5. Test with Valid and Invalid Data

```python
def test_endpoint_validates_response():
    """Test that endpoint validates response."""
    # Test with valid data
    valid_response = {...}
    result = client.post("/query", json=valid_response)
    assert result.status_code == 200

    # Test with invalid data
    invalid_response = {"invalid": "data"}
    result = client.post("/query", json=invalid_response)
    assert result.status_code == 422
```

## Troubleshooting

### Issue: Validation Passes Locally but Fails in Production

**Cause:** Different settings between environments

**Solution:**
- Ensure same validation settings in all environments
- Check middleware configuration
- Verify schema version consistency

### Issue: Too Many Validation Errors

**Cause:** Response generation not following schema

**Solution:**
- Use helper functions to build responses
- Add validation to response generation layer
- Review error logs for common patterns

### Issue: Performance Impact from Validation

**Cause:** Validation overhead on every request

**Solution:**
- Enable validation caching for identical responses
- Use async validation where possible
- Monitor validation processing time metrics

## Related Documentation

- [Answer JSON Contract Schema](./answer-json-contract.md)
- [RAG Orchestration Integration](./rag-orchestration.md)
- [AIKit Observability Guide](../observability/aikit-integration.md)
- [Testing Guidelines](../development/testing-guidelines.md)

## Changelog

### Version 1.0.0 (2026-01-16)

- Initial implementation of validation middleware
- Response model enforcement utilities
- AIKit observability integration
- Comprehensive test suite
- Documentation

## Support

For questions or issues:

- **GitHub Issues:** [kwanzaa/issues](https://github.com/AINative-Studio/kwanzaa/issues)
- **Documentation:** [docs/api/](https://github.com/AINative-Studio/kwanzaa/tree/main/docs/api)
- **Slack:** #kwanzaa-dev
