# Answer JSON Validation Guide

## Overview

This guide explains how to use the answer_json validation system in the Kwanzaa backend. The validation enforces the principle that **UI should never render raw text blobs** and ensures all AI responses conform to the structured answer_json contract.

## Table of Contents

- [Quick Start](#quick-start)
- [Schema Overview](#schema-overview)
- [Validation Functions](#validation-functions)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Testing](#testing)

## Quick Start

### Basic Validation

```python
from app.utils.answer_validation import validate_answer_json, AnswerValidationError

# Validate a response
try:
    validated_response = validate_answer_json(response_data)
    # Use validated_response - it's a fully typed AnswerJson object
    print(validated_response.answer.text)
    print(validated_response.answer.confidence)
except AnswerValidationError as e:
    # Handle validation errors
    print(f"Validation failed: {e.message}")
    for error in e.errors:
        print(f"  {error.field}: {error.message}")
```

### Check Validity Without Exceptions

```python
from app.utils.answer_validation import is_valid_answer_json

if is_valid_answer_json(response_data):
    # Process valid response
    process_response(response_data)
else:
    # Handle invalid response
    handle_error(response_data)
```

## Schema Overview

The answer_json contract consists of several nested sections:

### Top-Level Structure

```python
{
    "version": "kwanzaa.answer.v1",      # Schema version
    "persona": "educator",                # Agent persona
    "model_mode": "base_adapter_rag",    # Model mode
    "toggles": {...},                     # Configuration toggles
    "answer": {...},                      # Main answer content
    "sources": [...],                     # Citation sources
    "retrieval_summary": {...},           # Retrieval details
    "unknowns": {...},                    # Missing context
    "integrity": {...},                   # Trust metadata
    "provenance": {...}                   # Audit information
}
```

### Key Sections

#### Answer Section
Contains the main response with confidence and completeness metadata:

```python
"answer": {
    "text": "The main answer text",
    "confidence": 0.92,           # 0.0 to 1.0
    "tone": "neutral",           # neutral, formal, conversational, academic
    "completeness": "partial"     # complete, partial, incomplete
}
```

#### Sources Section
Provides full provenance for all citations:

```python
"sources": [
    {
        "citation_label": "National Archives (1964)",
        "canonical_url": "https://...",
        "source_org": "National Archives",
        "year": 1964,
        "content_type": "proclamation",
        "license": "Public Domain",
        "namespace": "kwanzaa_primary_sources",
        "doc_id": "nara_cra_1964",
        "chunk_id": "nara_cra_1964::chunk::3"
    }
]
```

#### Retrieval Summary
Shows transparency in the retrieval process ("Show Your Work"):

```python
"retrieval_summary": {
    "query": "What did the Civil Rights Act prohibit?",
    "top_k": 5,
    "namespaces": ["kwanzaa_primary_sources"],
    "filters": {"content_type": ["proclamation"]},
    "results": [...]  # Top retrieval results
}
```

#### Integrity Section
Provides trust signals and citation tracking:

```python
"integrity": {
    "citation_required": true,
    "citations_provided": true,
    "retrieval_confidence": "high",  # high, medium, low
    "fallback_behavior": "not_needed"
}
```

## Validation Functions

### validate_answer_json(data)

Primary validation function. Returns a fully validated `AnswerJson` Pydantic model.

**Parameters:**
- `data` (dict): Response dictionary to validate

**Returns:**
- `AnswerJson`: Validated Pydantic model with full type safety

**Raises:**
- `AnswerValidationError`: If validation fails

**Example:**
```python
validated = validate_answer_json(response_data)
# Access with full type safety
answer_text = validated.answer.text
confidence = validated.answer.confidence
sources = validated.sources
```

### validate_answer_json_dict(data)

Validates and returns as dictionary (useful when Pydantic model not needed).

**Parameters:**
- `data` (dict): Response dictionary to validate

**Returns:**
- `dict`: Validated dictionary (same structure as input if valid)

**Raises:**
- `AnswerValidationError`: If validation fails

### is_valid_answer_json(data)

Check validity without raising exceptions.

**Parameters:**
- `data` (dict): Response dictionary to check

**Returns:**
- `bool`: True if valid, False otherwise

**Example:**
```python
if is_valid_answer_json(response):
    # Process valid response
    pass
else:
    # Log error and use fallback
    logger.error("Invalid response format")
    use_fallback_response()
```

### get_validation_errors(data)

Get validation errors without raising exceptions.

**Parameters:**
- `data` (dict): Response dictionary to validate

**Returns:**
- `List[ValidationErrorDetail]`: List of validation errors (empty if valid)

**Example:**
```python
errors = get_validation_errors(response)
if errors:
    for error in errors:
        logger.error(f"Field {error.field}: {error.message}")
```

### validate_multiple_responses(responses)

Batch validation for multiple responses.

**Parameters:**
- `responses` (List[dict]): List of response dictionaries

**Returns:**
- `Tuple[List[AnswerJson], List[Tuple[int, AnswerValidationError]]]`:
  - First element: List of valid responses
  - Second element: List of (index, error) tuples for failed validations

**Example:**
```python
valid, invalid = validate_multiple_responses(batch_responses)

print(f"Valid: {len(valid)}, Invalid: {len(invalid)}")

# Process valid responses
for response in valid:
    process_response(response)

# Handle invalid responses
for idx, error in invalid:
    logger.error(f"Response {idx} failed: {error.message}")
```

## Error Handling

### AnswerValidationError

Exception raised when validation fails. Contains detailed error information.

**Attributes:**
- `message` (str): High-level error message
- `errors` (List[ValidationErrorDetail]): Detailed error list
- `raw_data` (dict, optional): The data that failed validation

**Methods:**
- `to_dict()`: Convert to dictionary for API responses

**Example:**
```python
try:
    validated = validate_answer_json(data)
except AnswerValidationError as e:
    # Log detailed errors
    logger.error(f"Validation failed: {e.message}")

    # Access individual errors
    for error in e.errors:
        logger.error(f"  Field: {error.field}")
        logger.error(f"  Message: {error.message}")
        logger.error(f"  Type: {error.error_type}")
        logger.error(f"  Location: {error.location}")

    # Return error to API client
    return JSONResponse(
        status_code=422,
        content=e.to_dict()
    )
```

### ValidationErrorDetail

Detailed information about a single validation error.

**Attributes:**
- `field` (str): The field that failed validation
- `message` (str): Human-readable error message
- `error_type` (str): Type of validation error
- `location` (List[str]): Path to the error in the data structure

## Best Practices

### 1. Always Validate at API Boundaries

Validate all AI responses before sending them to clients:

```python
@router.post("/ask")
async def ask_question(request: QuestionRequest):
    # Generate AI response
    raw_response = await ai_service.generate_answer(request.question)

    # ALWAYS validate before returning
    try:
        validated = validate_answer_json(raw_response)
        return validated.model_dump()
    except AnswerValidationError as e:
        logger.error(f"Generated invalid response: {e}")
        # Return error or fallback response
        raise HTTPException(status_code=500, detail="Invalid AI response format")
```

### 2. Use Type-Safe Access

Take advantage of Pydantic's type safety:

```python
# Good - type-safe access
validated = validate_answer_json(data)
text: str = validated.answer.text
confidence: float = validated.answer.confidence
sources: List[SourceReference] = validated.sources

# Avoid - loses type safety
data = validate_answer_json_dict(data)
text = data["answer"]["text"]  # No type checking
```

### 3. Handle Validation Errors Gracefully

```python
def process_ai_response(data: dict) -> Optional[AnswerJson]:
    """Process AI response with graceful error handling."""
    try:
        return validate_answer_json(data)
    except AnswerValidationError as e:
        # Log for debugging
        logger.error(f"Validation failed: {e}")

        # Record metrics
        metrics.increment("validation_errors")

        # Return None to trigger fallback
        return None
```

### 4. Validate in Tests

Always validate test fixtures:

```python
def test_ai_response_generation():
    response = generate_ai_response("test question")

    # Validate the response
    validated = validate_answer_json(response)

    # Now test with confidence
    assert validated.answer.confidence >= 0.7
    assert len(validated.sources) > 0
```

### 5. Batch Validation for Performance

When processing multiple responses:

```python
# Good - batch validation
valid, invalid = validate_multiple_responses(all_responses)

# Process valid responses
for response in valid:
    save_to_database(response)

# Handle invalid responses
if invalid:
    logger.warning(f"{len(invalid)} responses failed validation")
```

## Examples

### Example 1: Basic API Endpoint

```python
from fastapi import APIRouter, HTTPException
from app.utils.answer_validation import validate_answer_json, AnswerValidationError

router = APIRouter()

@router.post("/ask")
async def ask_question(question: str):
    # Generate response from AI
    raw_response = await ai_service.ask(question)

    # Validate response
    try:
        validated = validate_answer_json(raw_response)
    except AnswerValidationError as e:
        logger.error(f"AI generated invalid response: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI response validation failed"
        )

    # Return validated response
    return validated.model_dump()
```

### Example 2: Validation Middleware

```python
from fastapi import Request, Response
from app.utils.answer_validation import validate_answer_json, AnswerValidationError

async def validate_ai_responses(request: Request, call_next):
    """Middleware to validate all AI responses."""
    response = await call_next(request)

    # Check if response is from AI endpoint
    if request.url.path.startswith("/api/ai/"):
        try:
            # Parse and validate response body
            body = await response.json()
            validate_answer_json(body)
        except AnswerValidationError as e:
            logger.error(f"Invalid AI response: {e}")
            return Response(
                content={"error": "Invalid response format"},
                status_code=500
            )

    return response
```

### Example 3: Background Job Validation

```python
from app.utils.answer_validation import validate_multiple_responses

async def process_batch_questions(questions: List[str]):
    """Process multiple questions and validate all responses."""
    # Generate all responses
    responses = await ai_service.batch_ask(questions)

    # Validate all at once
    valid, invalid = validate_multiple_responses(responses)

    # Save valid responses
    for response in valid:
        await save_response(response)

    # Alert on invalid responses
    if invalid:
        for idx, error in invalid:
            logger.error(f"Question {idx} produced invalid response: {error}")
            await send_alert(f"Validation failed for question: {questions[idx]}")

    return {
        "total": len(questions),
        "valid": len(valid),
        "invalid": len(invalid)
    }
```

### Example 4: Testing with Fixtures

```python
import pytest
from tests.fixtures.answer_json_fixtures import VALID_FIXTURES, INVALID_FIXTURES
from app.utils.answer_validation import validate_answer_json, AnswerValidationError

def test_ai_service_returns_valid_format():
    """Test that AI service returns valid answer_json."""
    response = ai_service.generate_answer("test question")

    # Should not raise
    validated = validate_answer_json(response)
    assert validated.version == "kwanzaa.answer.v1"

def test_validation_rejects_invalid_format():
    """Test that validation rejects invalid format."""
    invalid_data = INVALID_FIXTURES["missing_required_field_version"]["data"]

    with pytest.raises(AnswerValidationError) as exc_info:
        validate_answer_json(invalid_data)

    # Check error details
    error = exc_info.value
    assert "version" in str(error)
```

## Testing

### Running Tests

```bash
# Run all validation tests
pytest tests/unit/schemas/test_answer_json_schema.py tests/unit/utils/test_answer_validation.py

# Run with coverage
pytest tests/unit/schemas/ tests/unit/utils/ --cov=app/schemas/answer_json --cov=app/utils/answer_validation --cov-report=html

# Run specific test class
pytest tests/unit/utils/test_answer_validation.py::TestValidateAnswerJson -v
```

### Test Fixtures

Test fixtures are available in `tests/fixtures/answer_json_fixtures.py`:

```python
from tests.fixtures.answer_json_fixtures import get_valid_fixture, get_invalid_fixture

# Get a valid fixture
complete_answer = get_valid_fixture("complete_answer_with_citations")

# Get an invalid fixture
invalid_data = get_invalid_fixture("missing_required_field_version")
```

### Coverage Requirements

The validation logic must maintain >= 80% test coverage. Current coverage:
- `app/schemas/answer_json.py`: **99%**
- `app/utils/answer_validation.py`: **100%**

## Integration Points

### 1. API Endpoints

All AI endpoints should validate responses before returning:

```python
# In app/api/v1/endpoints/ai.py
from app.utils.answer_validation import validate_answer_json

@router.post("/ask")
async def ask(question: str):
    response = await ai_service.ask(question)
    validated = validate_answer_json(response)  # Validate before returning
    return validated.model_dump()
```

### 2. Background Jobs

Validate responses in async processing:

```python
from app.utils.answer_validation import validate_answer_json

async def process_question_job(question_id: str):
    question = await get_question(question_id)
    response = await ai_service.ask(question.text)

    # Validate before saving
    validated = validate_answer_json(response)
    await save_response(question_id, validated)
```

### 3. Testing

Use validation in integration tests:

```python
async def test_end_to_end_question():
    response = await client.post("/api/ask", json={"question": "test"})
    data = response.json()

    # Verify response conforms to contract
    validated = validate_answer_json(data)
    assert validated.answer.text is not None
```

## Troubleshooting

### Common Validation Errors

1. **Missing Required Field**
   ```
   Error: Field 'version' is required
   Fix: Ensure all top-level fields are present
   ```

2. **Invalid URL Format**
   ```
   Error: canonical_url must start with http:// or https://
   Fix: Use full URL with protocol
   ```

3. **Confidence Out of Range**
   ```
   Error: confidence must be between 0.0 and 1.0
   Fix: Clamp confidence values to [0.0, 1.0]
   ```

4. **Citation Consistency**
   ```
   Error: citation_required=True but citations_provided=False
   Fix: Provide sources when citations are required
   ```

5. **Source-Retrieval Mismatch**
   ```
   Error: Sources reference doc_ids not in retrieval results
   Fix: Ensure all cited sources appear in retrieval results
   ```

### Debugging Tips

1. **Enable Detailed Logging**
   ```python
   import logging
   logging.getLogger("app.utils.answer_validation").setLevel(logging.DEBUG)
   ```

2. **Inspect Raw Data**
   ```python
   try:
       validate_answer_json(data)
   except AnswerValidationError as e:
       # Raw data is preserved in exception
       print(e.raw_data)
   ```

3. **Get All Errors at Once**
   ```python
   errors = get_validation_errors(data)
   for error in errors:
       print(f"{error.field}: {error.message}")
   ```

## Additional Resources

- **Contract Specification**: `/contract.json`
- **Schema Models**: `/backend/app/schemas/answer_json.py`
- **Validation Utilities**: `/backend/app/utils/answer_validation.py`
- **Test Fixtures**: `/backend/tests/fixtures/answer_json_fixtures.py`
- **Unit Tests**: `/backend/tests/unit/schemas/` and `/backend/tests/unit/utils/`

## Support

For questions or issues with validation:

1. Check this documentation
2. Review test cases for examples
3. Examine test fixtures for valid/invalid examples
4. Check logs for detailed validation errors
