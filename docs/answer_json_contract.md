# Answer JSON Contract Documentation

**Version:** 1.0.0
**Last Updated:** January 16, 2026
**Status:** Active

## Overview

The Answer JSON Contract is a strict JSON schema for AI responses in the Kwanzaa project. It enforces **Imani (Faith)** through verifiable sources and honest communication of limitations, ensuring that every AI response is grounded, cited, and transparent.

## Table of Contents

- [Purpose](#purpose)
- [Schema Location](#schema-location)
- [Core Principles](#core-principles)
- [Contract Structure](#contract-structure)
- [Field Definitions](#field-definitions)
- [Validation Rules](#validation-rules)
- [Usage Examples](#usage-examples)
- [AIKit Rendering Guidelines](#aikit-rendering-guidelines)
- [Version History](#version-history)
- [References](#references)

## Purpose

The Answer JSON Contract serves multiple critical purposes:

1. **Trust and Transparency**: Every answer includes sources, retrieval information, and honest acknowledgment of limitations
2. **Provenance Tracking**: Full citation metadata ensures attribution to original sources
3. **Cultural Integrity**: Enforces the Seven Principles (Nguzo Saba) at the data contract level
4. **AIKit Compatibility**: Structured for optimal rendering in AI interfaces
5. **Cross-Language Consistency**: Uniform contract across TypeScript, Python, and JSON Schema

## Schema Location

The contract is defined in three complementary formats:

| Format | Location | Purpose |
|--------|----------|---------|
| JSON Schema | `/backend/app/schemas/answer_json.schema.json` | Formal schema definition for validation |
| TypeScript | `/backend/app/schemas/answer_json.types.ts` | Type definitions for frontend/TypeScript consumers |
| Python (Pydantic) | `/backend/app/models/answer_json.py` | Backend models with validation logic |

## Core Principles

The contract embodies the **Nguzo Saba** (Seven Principles):

| Principle | Implementation |
|-----------|----------------|
| **Umoja (Unity)** | Unified schema across all personas and interfaces |
| **Kujichagulia (Self-Determination)** | User-controlled `toggles` for citation and creativity |
| **Ujima (Collective Work)** | Transparent `retrieval_summary` showing the work |
| **Ujamaa (Cooperative Economics)** | `provenance` metadata giving proper credit |
| **Nia (Purpose)** | Education and research-first design |
| **Kuumba (Creativity)** | Support for creative mode with grounding |
| **Imani (Faith)** | `sources` and `unknowns` build trust through honesty |

## Contract Structure

### High-Level Overview

```
AnswerJsonContract
├── version (required)          # Contract version identifier
├── persona (optional)          # Persona mode (educator, researcher, etc.)
├── model_mode (optional)       # Model mode (RAG, creative, etc.)
├── toggles (optional)          # User behavior controls
├── answer (required)           # Main AI response
│   ├── text
│   ├── confidence
│   ├── tone
│   └── completeness
├── sources (required)          # Citation array
│   └── [Source...]
├── retrieval_summary (required) # Retrieval transparency
│   ├── query
│   ├── top_k
│   ├── namespaces
│   ├── filters
│   └── results
├── unknowns (required)         # Honest acknowledgment of gaps
│   ├── unsupported_claims
│   ├── missing_context
│   ├── clarifying_questions
│   └── out_of_scope
├── integrity (optional)        # Trust and safety metadata
└── provenance (optional)       # Generation tracking
```

## Field Definitions

### Required Fields

#### `version` (string, required)

- **Pattern:** `^kwanzaa\.answer\.v[0-9]+$`
- **Description:** Contract version identifier
- **Example:** `"kwanzaa.answer.v1"`

#### `answer` (object, required)

Main AI response with metadata.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `text` | string | Yes | 1-10,000 chars | The main response text |
| `confidence` | number | No | 0.0-1.0 | Model confidence score |
| `tone` | enum | No | See [Tone](#tone-enum) | Response tone |
| `completeness` | enum | No | See [Completeness](#completeness-enum) | Answer completeness |

##### Tone Enum

- `neutral`
- `educational`
- `conversational`
- `formal`
- `creative`

##### Completeness Enum

- `complete` - All aspects of the query are fully addressed
- `partial` - Some aspects addressed, but gaps remain
- `insufficient_data` - Corpus lacks sufficient data for a complete answer

#### `sources` (array, required)

Array of source citations with full provenance metadata.

Each source object must include:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `citation_label` | string | Yes | 1-500 chars | Human-readable citation |
| `canonical_url` | string (URI) | Yes | Valid URI | URL to source document |
| `source_org` | string | Yes | 1-200 chars | Source organization |
| `year` | integer | Yes | 1600-2100 | Document year |
| `content_type` | string | Yes | 1-100 chars | Content classification |
| `license` | string | Yes | 1-200 chars | License information |
| `namespace` | string | Yes | 1-100 chars | Vector namespace |
| `doc_id` | string | Yes | 1-200 chars | Document identifier |
| `chunk_id` | string | Yes | 1-200 chars | Chunk identifier |
| `tags` | array[string] | No | Max 50 items | Content tags |
| `relevance_score` | number | No | 0.0-1.0 | Relevance score |

**Additional properties are allowed** for source-specific metadata.

#### `retrieval_summary` (object, required)

Summary of the retrieval process for transparency.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `query` | string | Yes | 1-1,000 chars | Original query text |
| `top_k` | integer | Yes | 1-100 | Number of results requested |
| `namespaces` | array[string] | Yes | 1-20 items | Namespaces searched |
| `filters` | object | No | - | Filters applied |
| `results` | array | Yes | 0-100 items | Retrieval results |
| `execution_time_ms` | integer | No | >= 0 | Execution time |
| `embedding_model` | string | No | - | Embedding model used |

##### Retrieval Result Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rank` | integer | Yes | Result rank (1-indexed) |
| `score` | number | Yes | Similarity score (0.0-1.0) |
| `snippet` | string | No | Text snippet (max 2,000 chars) |
| `citation_label` | string | Yes | Citation label |
| `canonical_url` | string | Yes | Source URL |
| `doc_id` | string | Yes | Document ID |
| `chunk_id` | string | Yes | Chunk ID |
| `namespace` | string | Yes | Namespace |

#### `unknowns` (object, required)

Transparent communication of limitations and gaps.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `unsupported_claims` | array[string] | Yes | Claims not supported by corpus |
| `missing_context` | array[string] | Yes | Context gaps in corpus |
| `clarifying_questions` | array[string] | Yes | Questions that would help |
| `out_of_scope` | array[string] | No | Out-of-scope topics |

### Optional Fields

#### `persona` (enum, optional)

Persona mode that generated the response.

- `educator` - Educational context, citations required
- `researcher` - Research mode, deep sourcing
- `creator` - Creative generation with grounding
- `builder` - Technical/implementation focus

#### `model_mode` (enum, optional)

Model mode used for generation.

- `base_adapter_rag` - Base model + adapter + RAG retrieval
- `base_only` - Base model without adapter or RAG
- `adapter_only` - Adapter without RAG
- `creative` - Creative generation mode

#### `toggles` (object, optional)

User-controlled behavior toggles.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `require_citations` | boolean | Yes | Citations mandatory |
| `primary_sources_only` | boolean | Yes | Primary sources only |
| `creative_mode` | boolean | Yes | Creative generation enabled |

#### `integrity` (object, optional)

Integrity metadata for trust and safety.

| Field | Type | Description |
|-------|------|-------------|
| `citation_required` | boolean | Whether citations were required |
| `citations_provided` | boolean | Whether citations were provided |
| `retrieval_confidence` | enum | `high`, `medium`, `low`, `none` |
| `fallback_behavior` | enum | `not_needed`, `creative_generation`, `refusal`, `clarification_requested` |
| `safety_flags` | array[string] | Safety or policy flags |

#### `provenance` (object, optional)

Generation provenance for tracking and credit.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `generated_at` | string (ISO 8601) | Yes | Generation timestamp |
| `retrieval_run_id` | string (UUID) | No | Retrieval run identifier |
| `assistant_message_id` | string (UUID) | No | Assistant message ID |
| `session_id` | string (UUID) | No | Session identifier |
| `model_version` | string | No | Model version |
| `adapter_version` | string | No | Adapter version |

## Validation Rules

### Schema-Level Validation

1. **Required Fields**: `version`, `answer`, `sources`, `retrieval_summary`, `unknowns` must be present
2. **No Additional Properties**: The root contract object forbids additional properties
3. **Version Format**: Must match pattern `kwanzaa.answer.v[digit]`
4. **Text Length**: `answer.text` must be 1-10,000 characters

### Business Logic Validation

1. **Citation Integrity**: If `integrity.citation_required = true`, then `sources` array must not be empty
2. **Year Range**: If `retrieval_summary.filters` includes both `year_gte` and `year_lte`, then `year_gte <= year_lte`
3. **Confidence Bounds**: All confidence and score values must be in range [0.0, 1.0]
4. **Rank Ordering**: `retrieval_summary.results` should be ordered by `rank` (1-indexed)

### Python-Specific Validation

The Pydantic model includes a `@model_validator` that enforces:

```python
@model_validator(mode="after")
def validate_citation_integrity(self) -> "AnswerJsonContract":
    """Validate citation integrity requirements."""
    if self.integrity:
        if self.integrity.citation_required and not self.integrity.citations_provided:
            if len(self.sources) == 0:
                raise ValueError(
                    "Citations are required but none were provided. "
                    "This violates Imani (Faith) principle."
                )
    return self
```

## Usage Examples

### Minimal Valid Contract

```json
{
  "version": "kwanzaa.answer.v1",
  "answer": {
    "text": "Kwanzaa was created in 1966 by Dr. Maulana Karenga."
  },
  "sources": [],
  "retrieval_summary": {
    "query": "When was Kwanzaa created?",
    "top_k": 10,
    "namespaces": ["kwanzaa_primary_sources"],
    "results": []
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": ["No primary sources available in corpus"],
    "clarifying_questions": []
  }
}
```

### Complete Example with Sources

```json
{
  "version": "kwanzaa.answer.v1",
  "persona": "educator",
  "model_mode": "base_adapter_rag",
  "toggles": {
    "require_citations": true,
    "primary_sources_only": true,
    "creative_mode": false
  },
  "answer": {
    "text": "The Civil Rights Act of 1964 was landmark federal legislation that prohibited discrimination based on race, color, religion, sex, or national origin in public accommodations, employment, and federally funded programs.",
    "confidence": 0.92,
    "tone": "educational",
    "completeness": "complete"
  },
  "sources": [
    {
      "citation_label": "National Archives (1964) — Civil Rights Act",
      "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
      "source_org": "National Archives",
      "year": 1964,
      "content_type": "legal_document",
      "license": "Public Domain",
      "namespace": "kwanzaa_primary_sources",
      "doc_id": "nara_cra_1964",
      "chunk_id": "nara_cra_1964::chunk::3",
      "tags": ["civil_rights", "legislation", "1960s"],
      "relevance_score": 0.93
    }
  ],
  "retrieval_summary": {
    "query": "What did the Civil Rights Act of 1964 prohibit?",
    "top_k": 5,
    "namespaces": ["kwanzaa_primary_sources"],
    "filters": {
      "content_type": ["legal_document", "proclamation"],
      "year_gte": 1960,
      "year_lte": 1970
    },
    "results": [
      {
        "rank": 1,
        "score": 0.93,
        "snippet": "An Act to enforce the constitutional right to vote, to confer jurisdiction upon the district courts of the United States to provide injunctive relief against discrimination in public accommodations...",
        "citation_label": "National Archives (1964) — Civil Rights Act",
        "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
        "doc_id": "nara_cra_1964",
        "chunk_id": "nara_cra_1964::chunk::3",
        "namespace": "kwanzaa_primary_sources"
      }
    ],
    "execution_time_ms": 245,
    "embedding_model": "text-embedding-3-small"
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [
      "Detailed enforcement case law from 1965-1967 not included in corpus"
    ],
    "clarifying_questions": []
  },
  "integrity": {
    "citation_required": true,
    "citations_provided": true,
    "retrieval_confidence": "high",
    "fallback_behavior": "not_needed"
  },
  "provenance": {
    "generated_at": "2026-01-16T18:42:11Z",
    "retrieval_run_id": "9b2d7cfa-cc5e-4a2b-9a6e-6c77f47a9c21",
    "assistant_message_id": "c5f0a75e-4e5c-4a11-9f55-1b5b0a31d77e"
  }
}
```

### Python Usage

```python
from backend.app.models.answer_json import (
    Answer,
    AnswerJsonContract,
    Persona,
    Source,
    Unknowns,
    create_answer_json_contract,
)

# Create a contract using the helper function
contract = create_answer_json_contract(
    answer="Kwanzaa was created in 1966.",
    query="When was Kwanzaa created?",
    persona=Persona.EDUCATOR,
)

# Access fields
print(contract.answer.text)
print(contract.version)

# Serialize to JSON
json_output = contract.model_dump_json(indent=2)

# Validate incoming JSON
raw_json = '{"version": "kwanzaa.answer.v1", ...}'
validated = AnswerJsonContract.model_validate_json(raw_json)
```

### TypeScript Usage

```typescript
import {
  AnswerJsonContract,
  createAnswerJsonContract,
  isAnswerJsonContract,
} from './schemas/answer_json.types';

// Create a contract
const contract: AnswerJsonContract = createAnswerJsonContract(
  'Kwanzaa was created in 1966.',
  'When was Kwanzaa created?',
  {
    persona: 'educator',
    modelMode: 'base_adapter_rag',
  }
);

// Type guard
if (isAnswerJsonContract(data)) {
  console.log(data.answer.text);
}

// Access with type safety
const answerText: string = contract.answer.text;
const sources: Source[] = contract.sources;
```

## AIKit Rendering Guidelines

### Visual Hierarchy

1. **Primary**: `answer.text` - Display prominently as the main response
2. **Secondary**: `sources` - Render as clickable citations below answer
3. **Tertiary**: `retrieval_summary` - Collapsible "Show Your Work" section
4. **Quaternary**: `unknowns` - Only show if non-empty, as trust indicator

### Recommended UI Components

#### Answer Section

```jsx
<Answer>
  <AnswerText>{contract.answer.text}</AnswerText>
  {contract.answer.confidence && (
    <ConfidenceBadge value={contract.answer.confidence} />
  )}
  {contract.answer.completeness && (
    <CompletenessIndicator status={contract.answer.completeness} />
  )}
</Answer>
```

#### Sources Section

```jsx
<Sources>
  <SectionHeader>Sources ({contract.sources.length})</SectionHeader>
  {contract.sources.map((source, idx) => (
    <Citation key={idx}>
      <CitationNumber>{idx + 1}</CitationNumber>
      <CitationLink href={source.canonical_url}>
        {source.citation_label}
      </CitationLink>
      <CitationMeta>
        {source.source_org} • {source.year} • {source.content_type}
      </CitationMeta>
    </Citation>
  ))}
</Sources>
```

#### Retrieval Summary (Collapsible)

```jsx
<Collapsible title="Show Your Work" defaultOpen={false}>
  <RetrievalInfo>
    <Field label="Query">{contract.retrieval_summary.query}</Field>
    <Field label="Namespaces">
      {contract.retrieval_summary.namespaces.join(', ')}
    </Field>
    <Field label="Filters">
      {JSON.stringify(contract.retrieval_summary.filters)}
    </Field>
  </RetrievalInfo>
  <RetrievalResults>
    {contract.retrieval_summary.results.map((result) => (
      <ResultCard key={result.rank}>
        <ResultRank>#{result.rank}</ResultRank>
        <ResultScore>{(result.score * 100).toFixed(1)}%</ResultScore>
        <ResultSnippet>{result.snippet}</ResultSnippet>
        <ResultLink href={result.canonical_url}>
          {result.citation_label}
        </ResultLink>
      </ResultCard>
    ))}
  </RetrievalResults>
</Collapsible>
```

#### Unknowns Section

```jsx
{(contract.unknowns.unsupported_claims.length > 0 ||
  contract.unknowns.missing_context.length > 0 ||
  contract.unknowns.clarifying_questions.length > 0) && (
  <UnknownsSection>
    <SectionHeader>What's Missing or Unclear</SectionHeader>

    {contract.unknowns.unsupported_claims.length > 0 && (
      <UnknownsList title="Unsupported Claims">
        {contract.unknowns.unsupported_claims.map((claim, idx) => (
          <UnknownItem key={idx}>{claim}</UnknownItem>
        ))}
      </UnknownsList>
    )}

    {contract.unknowns.missing_context.length > 0 && (
      <UnknownsList title="Missing Context">
        {contract.unknowns.missing_context.map((context, idx) => (
          <UnknownItem key={idx}>{context}</UnknownItem>
        ))}
      </UnknownsList>
    )}

    {contract.unknowns.clarifying_questions.length > 0 && (
      <UnknownsList title="Clarifying Questions">
        {contract.unknowns.clarifying_questions.map((question, idx) => (
          <UnknownItem key={idx}>{question}</UnknownItem>
        ))}
      </UnknownsList>
    )}
  </UnknownsSection>
)}
```

#### Integrity Badges

```jsx
<IntegrityIndicators>
  {contract.integrity?.citation_required && (
    <Badge variant={contract.integrity.citations_provided ? 'success' : 'warning'}>
      Citations: {contract.integrity.citations_provided ? '✓' : '✗'}
    </Badge>
  )}
  {contract.integrity?.retrieval_confidence && (
    <Badge variant={getConfidenceVariant(contract.integrity.retrieval_confidence)}>
      Confidence: {contract.integrity.retrieval_confidence}
    </Badge>
  )}
</IntegrityIndicators>
```

### Accessibility Considerations

1. **Semantic HTML**: Use `<article>`, `<section>`, `<cite>` appropriately
2. **ARIA Labels**: Add `aria-label` to citation links and collapsible sections
3. **Keyboard Navigation**: Ensure all interactive elements are keyboard-accessible
4. **Screen Readers**: Provide `aria-live` regions for dynamic content
5. **Color Independence**: Don't rely solely on color for confidence/completeness indicators

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-16 | Initial release of Answer JSON Contract |

## References

- [Kwanzaa Project README](/Users/aideveloper/kwanzaa/README.md)
- [Search Models](/Users/aideveloper/kwanzaa/backend/app/models/search.py)
- [Original Contract Example](/Users/aideveloper/kwanzaa/contract.json)
- [JSON Schema Draft 7](https://json-schema.org/draft-07/schema)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Maintained by:** AINative Studio
**Project:** Kwanzaa - First Fruits for AI
**License:** Apache 2.0
