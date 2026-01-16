# Epic 8 Implementation: answer_json Contract & Rendering

## Overview

Epic 8 focuses on defining and enforcing the answer_json contract for AI responses, ensuring Safety & Integrity (Nguzo: Imani).

## Issues Implemented

- **Issue #65 (E8-US1)**: Define answer_json Contract
- **Issue #66 (E8-US2)**: Enforce Output Compliance

## Deliverables

### 1. Schema Definitions

**JSON Schema** (`backend/app/schemas/answer_json.schema.json`)
- Complete JSON Schema Draft 7 specification
- Versioned contract pattern: `kwanzaa.answer.v1`
- Defines required fields: answer, sources, retrieval_summary, unknowns

**TypeScript Types** (`backend/app/schemas/answer_json.types.ts`)
- TypeScript type definitions with helper functions
- Ensures type safety across frontend and backend

**Python Models** (`backend/app/models/answer_json.py`)
- Pydantic models with comprehensive validation
- Type checking, range validation, format validation
- Business logic enforcement

### 2. Validation Utilities

**Validation Module** (`backend/app/utils/answer_validation.py`)
- Primary validation functions
- Error handling and reporting
- Batch validation support

### 3. Tests

**Test Suite** (`backend/tests/test_answer_json_contract.py`)
- Comprehensive validation tests
- Schema compliance verification
- Edge case coverage

### 4. Example Files

Located in `backend/app/schemas/examples/`:
- `valid_minimal.json` - Minimal valid response
- `valid_complete.json` - Complete response with all fields
- `valid_with_unknowns.json` - Response acknowledging gaps
- `invalid_missing_required.json` - Missing required fields
- `invalid_bad_version.json` - Invalid version format
- `invalid_citation_integrity.json` - Citation inconsistencies

## Contract Structure

```typescript
{
  contract_version: "kwanzaa.answer.v1",
  answer: {
    text: string,
    confidence: number,  // 0.0-1.0
    tone: enum,
    completeness: enum
  },
  sources: [
    {
      citation_id: string,
      title: string,
      canonical_url: string,
      year: number,
      source_org: string,
      license: string
    }
  ],
  retrieval_summary: {
    query_rewrite: string,
    chunks_retrieved: number,
    confidence: number,
    fallback_triggered: boolean
  },
  unknowns: [
    {
      question: string,
      reason: string
    }
  ],
  generation_metadata: {
    persona: enum,
    model_mode: enum,
    toggles: object,
    timestamp: ISO8601
  }
}
```

## Nguzo Saba Integration

The contract embodies all Seven Principles:
- **Umoja (Unity)** - Unified schema across platforms
- **Kujichagulia (Self-Determination)** - User-controlled settings
- **Ujima (Collective Work)** - Transparent retrieval process
- **Ujamaa (Cooperative Economics)** - Shared credit through provenance
- **Nia (Purpose)** - Education-first design
- **Kuumba (Creativity)** - Creative mode support
- **Imani (Faith)** - Citation integrity and honesty

## Acceptance Criteria

### E8-US1: Define answer_json Contract
- ✅ Contract versioned
- ✅ JSON schema defined and documented
- ✅ Schema includes all required fields
- ✅ Schema is renderable by AIKit

### E8-US2: Enforce Output Compliance
- ✅ Validation utilities implemented
- ✅ Pydantic models with field validation
- ✅ Test coverage for compliance
- ✅ Example files for validation

## Usage

### Python Validation

```python
from app.models.answer_json import AnswerJson
from app.utils.answer_validation import validate_answer_json

# Validate response
try:
    validated = validate_answer_json(ai_response)
    return validated.model_dump()
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
```

### TypeScript Usage

```typescript
import { AnswerJson, validateAnswerJson } from './schemas/answer_json.types';

const response: AnswerJson = {
  contract_version: "kwanzaa.answer.v1",
  answer: { /* ... */ },
  sources: [ /* ... */ ],
  // ...
};
```

## Next Steps

1. Integrate validation into all AI response endpoints
2. Create FastAPI middleware for automatic validation
3. Update AI service to generate compliant responses
4. Add monitoring for validation failures
5. Implement UI rendering components

## References

- Issue #65: https://github.com/AINative-Studio/kwanzaa/issues/65
- Issue #66: https://github.com/AINative-Studio/kwanzaa/issues/66
- PRD Section: Safety + Integrity
- Nguzo: Imani (Faith)
