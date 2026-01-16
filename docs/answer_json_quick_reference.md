# Answer JSON Contract - Quick Reference

**Version:** 1.0.0

## Minimal Valid Example

```json
{
  "version": "kwanzaa.answer.v1",
  "answer": {
    "text": "Your answer text here"
  },
  "sources": [],
  "retrieval_summary": {
    "query": "Original query",
    "top_k": 10,
    "namespaces": ["kwanzaa_primary_sources"],
    "results": []
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [],
    "clarifying_questions": []
  }
}
```

## Required Fields Quick Checklist

- ✅ `version` - Must match pattern `kwanzaa.answer.v[N]`
- ✅ `answer.text` - 1-10,000 characters
- ✅ `sources` - Array (can be empty)
- ✅ `retrieval_summary.query` - Original query text
- ✅ `retrieval_summary.top_k` - 1-100
- ✅ `retrieval_summary.namespaces` - Array, 1-20 items
- ✅ `retrieval_summary.results` - Array (can be empty)
- ✅ `unknowns.unsupported_claims` - Array (can be empty)
- ✅ `unknowns.missing_context` - Array (can be empty)
- ✅ `unknowns.clarifying_questions` - Array (can be empty)

## Source Object Required Fields

```json
{
  "citation_label": "Organization (Year) — Title",
  "canonical_url": "https://example.org/source",
  "source_org": "Organization Name",
  "year": 2024,
  "content_type": "article",
  "license": "Public Domain",
  "namespace": "kwanzaa_primary_sources",
  "doc_id": "doc_identifier",
  "chunk_id": "doc_identifier::chunk::1"
}
```

## Enum Values

### Persona
- `educator`
- `researcher`
- `creator`
- `builder`

### Model Mode
- `base_adapter_rag`
- `base_only`
- `adapter_only`
- `creative`

### Tone
- `neutral`
- `educational`
- `conversational`
- `formal`
- `creative`

### Completeness
- `complete`
- `partial`
- `insufficient_data`

### Retrieval Confidence
- `high`
- `medium`
- `low`
- `none`

### Fallback Behavior
- `not_needed`
- `creative_generation`
- `refusal`
- `clarification_requested`

## Common Validation Errors

### 1. Invalid Version Format
```json
// ❌ Wrong
{"version": "v1.0.0"}

// ✅ Correct
{"version": "kwanzaa.answer.v1"}
```

### 2. Missing Required Field
```json
// ❌ Wrong - missing retrieval_summary
{
  "version": "kwanzaa.answer.v1",
  "answer": {"text": "Answer"},
  "sources": [],
  "unknowns": {...}
}

// ✅ Correct - all required fields present
{
  "version": "kwanzaa.answer.v1",
  "answer": {"text": "Answer"},
  "sources": [],
  "retrieval_summary": {...},
  "unknowns": {...}
}
```

### 3. Invalid Year Range
```json
// ❌ Wrong - year_lte < year_gte
{
  "filters": {
    "year_gte": 1970,
    "year_lte": 1960
  }
}

// ✅ Correct
{
  "filters": {
    "year_gte": 1960,
    "year_lte": 1970
  }
}
```

### 4. Citation Integrity Violation
```json
// ❌ Wrong - requires citations but none provided
{
  "sources": [],
  "integrity": {
    "citation_required": true,
    "citations_provided": false
  }
}

// ✅ Correct - citations provided when required
{
  "sources": [{...}],
  "integrity": {
    "citation_required": true,
    "citations_provided": true
  }
}
```

## Python Quick Start

```python
from app.models.answer_json import create_answer_json_contract

# Create minimal contract
contract = create_answer_json_contract(
    answer="Your answer",
    query="Your query"
)

# Validate JSON
from app.models.answer_json import AnswerJsonContract
validated = AnswerJsonContract.model_validate_json(json_string)

# Serialize to JSON
json_output = contract.model_dump_json(indent=2)
```

## TypeScript Quick Start

```typescript
import { createAnswerJsonContract } from './schemas/answer_json.types';

// Create contract
const contract = createAnswerJsonContract(
  'Your answer',
  'Your query'
);

// Type guard
if (isAnswerJsonContract(data)) {
  console.log(data.answer.text);
}
```

## Field Length Limits

| Field | Min | Max |
|-------|-----|-----|
| `answer.text` | 1 | 10,000 chars |
| `citation_label` | 1 | 500 chars |
| `source_org` | 1 | 200 chars |
| `content_type` | 1 | 100 chars |
| `license` | 1 | 200 chars |
| `namespace` | 1 | 100 chars |
| `query` | 1 | 1,000 chars |
| `snippet` | - | 2,000 chars |

## Numeric Ranges

| Field | Min | Max |
|-------|-----|-----|
| `confidence` | 0.0 | 1.0 |
| `score` | 0.0 | 1.0 |
| `relevance_score` | 0.0 | 1.0 |
| `year` | 1600 | 2100 |
| `top_k` | 1 | 100 |
| `rank` | 1 | - |

## Array Limits

| Field | Min Items | Max Items |
|-------|-----------|-----------|
| `sources` | 0 | 100 |
| `namespaces` | 1 | 20 |
| `results` | 0 | 100 |
| `tags` | 0 | 50 |

## Files Reference

| Purpose | Location |
|---------|----------|
| JSON Schema | `/backend/app/schemas/answer_json.schema.json` |
| TypeScript | `/backend/app/schemas/answer_json.types.ts` |
| Python Models | `/backend/app/models/answer_json.py` |
| Full Docs | `/docs/answer_json_contract.md` |
| Examples | `/backend/app/schemas/examples/` |
| Tests | `/backend/tests/test_answer_json_contract.py` |

## Common Use Cases

### 1. Success with Citations
See: `/backend/app/schemas/examples/valid_complete.json`

### 2. Partial Answer with Unknowns
See: `/backend/app/schemas/examples/valid_with_unknowns.json`

### 3. Refusal (Out of Scope)
See: `/backend/app/schemas/examples/valid_refusal.json`

```json
{
  "answer": {
    "text": "I cannot answer this question because it falls outside the scope...",
    "completeness": "insufficient_data"
  },
  "sources": [],
  "integrity": {
    "citation_required": false,
    "citations_provided": false,
    "retrieval_confidence": "none",
    "fallback_behavior": "refusal"
  }
}
```

## AIKit Component Mapping

| Contract Section | AIKit Component |
|------------------|-----------------|
| `answer` | `<AgentResponse>` |
| `sources` | `<CitationList>` |
| `retrieval_summary` | `<ToolResult>` (collapsible) |
| `unknowns` | `<UnknownsCard>` |
| `integrity` | `<IntegrityBadges>` |
| `provenance` | `<ProvenanceFooter>` |

See [AIKit Integration Guide](/Users/aideveloper/kwanzaa/docs/aikit-integration.md) for complete implementation examples.

## Links

- [Full Documentation](/Users/aideveloper/kwanzaa/docs/answer_json_contract.md)
- [AIKit Integration Guide](/Users/aideveloper/kwanzaa/docs/aikit-integration.md)
- [Implementation Summary](/Users/aideveloper/kwanzaa/docs/implementation-summary-issue-23.md)
- [Schema Directory README](/Users/aideveloper/kwanzaa/backend/app/schemas/README.md)
