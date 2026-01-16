# Schemas Directory

This directory contains schema definitions and type contracts for the Kwanzaa API.

## Contents

### Answer JSON Contract

**Version:** 1.0.0

The Answer JSON Contract defines the structure for AI responses with citations, provenance tracking, and transparent uncertainty.

#### Files

- `answer_json.schema.json` - JSON Schema (Draft 7) definition
- `answer_json.types.ts` - TypeScript type definitions
- `../models/answer_json.py` - Pydantic models (Python)

#### Documentation

See [`/docs/answer_json_contract.md`](/Users/aideveloper/kwanzaa/docs/answer_json_contract.md) for comprehensive documentation.

#### Example Files

The `examples/` directory contains validation examples:

**Valid Examples:**
- `valid_minimal.json` - Minimal valid contract
- `valid_complete.json` - Complete contract with all fields
- `valid_with_unknowns.json` - Contract demonstrating unknowns/gaps

**Invalid Examples (for testing):**
- `invalid_missing_required.json` - Missing required fields
- `invalid_bad_version.json` - Invalid version format
- `invalid_citation_integrity.json` - Violates citation integrity rule

## Usage

### Python (Backend)

```python
from app.models.answer_json import (
    AnswerJsonContract,
    create_answer_json_contract,
)

# Create a contract
contract = create_answer_json_contract(
    answer="Your answer text",
    query="Original query",
)

# Validate JSON
raw_json = '{"version": "kwanzaa.answer.v1", ...}'
validated = AnswerJsonContract.model_validate_json(raw_json)
```

### TypeScript (Frontend)

```typescript
import {
  AnswerJsonContract,
  createAnswerJsonContract,
} from './schemas/answer_json.types';

// Create a contract
const contract = createAnswerJsonContract(
  'Your answer text',
  'Original query'
);
```

### JSON Schema Validation

Use the JSON Schema file for validation in any language:

```bash
# Using ajv-cli
ajv validate -s answer_json.schema.json -d examples/valid_minimal.json
```

## Testing

Run the test suite:

```bash
cd /Users/aideveloper/kwanzaa/backend
python3 -m pytest tests/test_answer_json_contract.py -v
```

## Design Principles

The Answer JSON Contract embodies the **Nguzo Saba** (Seven Principles):

1. **Umoja (Unity)** - Unified schema across all personas
2. **Kujichagulia (Self-Determination)** - User-controlled toggles
3. **Ujima (Collective Work)** - Transparent retrieval summary
4. **Ujamaa (Cooperative Economics)** - Provenance metadata
5. **Nia (Purpose)** - Education and research first
6. **Kuumba (Creativity)** - Creative mode with grounding
7. **Imani (Faith)** - Trust through citations and honesty

## Adding New Schemas

When adding new schema definitions:

1. Create JSON Schema file in this directory
2. Create TypeScript types file
3. Create Pydantic models in `/app/models/`
4. Add validation examples in `examples/`
5. Add tests in `/tests/`
6. Document in `/docs/`
