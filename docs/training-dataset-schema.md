# Kwanzaa Adapter Training Dataset Schema

**Version:** 1.0.0
**Epic:** 3B - Adapter Training Dataset Preparation
**Issue:** #55 (E3B-US1)

## Overview

This document defines the schema for training samples that teach the Kwanzaa adapter three critical behaviors:

1. **Citation-following**: Properly citing sources when good retrieval context is available
2. **Refusal**: Gracefully declining when information is not in the corpus
3. **answer_json compliance**: Strictly adhering to the Epic 8 contract format

## Schema Architecture

### High-Level Structure

```
TrainingDataset
├── dataset_version (string, semver)
├── created_at (ISO 8601 timestamp)
├── description (string, optional)
├── statistics (computed automatically)
│   ├── total_samples
│   ├── by_category {}
│   ├── by_persona {}
│   └── by_difficulty {}
└── samples []
    └── TrainingSample (see below)
```

### TrainingSample Structure

Each training sample represents a complete input-output pair for supervised fine-tuning:

```python
{
  "sample_id": "citation_educator_001",           # Unique identifier
  "category": "citation",                         # Training objective
  "persona": "educator",                          # Target persona
  "user_query": "What did the Civil Rights...",  # User input
  "retrieved_context": [...],                     # Simulated RAG results
  "expected_output": {...},                       # answer_json contract
  "metadata": {...}                               # Quality metrics
}
```

## Field Specifications

### 1. Core Identifiers

#### `sample_id` (required)
- **Type:** string
- **Pattern:** `^[a-z0-9_]+$`
- **Description:** Unique identifier following convention: `{category}_{persona}_{number}`
- **Example:** `"citation_educator_001"`, `"refusal_researcher_002"`

#### `category` (required)
- **Type:** enum
- **Values:**
  - `citation` - Teaches proper source citation with good retrieval
  - `refusal` - Teaches graceful refusal when data is unavailable
  - `grounded_answer` - Teaches synthesis from multiple sources
  - `format_compliance` - Teaches strict answer_json format adherence
- **Description:** Primary training objective for this sample

#### `persona` (required)
- **Type:** enum
- **Values:** `educator`, `researcher`, `creator`, `builder`
- **Description:** Target persona that should respond to this query
- **Validation:** Must match `expected_output.persona` if present

### 2. Input Components

#### `user_query` (required)
- **Type:** string
- **Length:** 10-500 characters
- **Description:** The user's question or prompt
- **Guidelines:**
  - Should be realistic and representative of actual user queries
  - Clear and unambiguous for training purposes
  - Appropriate for the target persona

#### `retrieved_context` (required, can be empty array)
- **Type:** array of `RetrievalResult`
- **Description:** Simulated RAG retrieval results providing context
- **When empty:** Used for refusal training (no good sources found)
- **When populated:** Used for citation and grounded answer training

##### RetrievalResult Structure

```python
{
  "rank": 1,                    # Result position (1-indexed)
  "score": 0.93,                # Similarity score (0.0-1.0)
  "chunk_id": "doc_123::chunk::5",
  "doc_id": "doc_123",
  "namespace": "kwanzaa_primary_sources",
  "content": "The actual text content...",  # Max 2000 chars
  "metadata": {
    "citation_label": "King, M.L. (1963) — Letter from Birmingham Jail",
    "canonical_url": "https://...",
    "source_org": "National Archives",
    "year": 1963,
    "content_type": "letter",
    "license": "Public Domain",
    "tags": ["civil_rights", "1960s"]
  }
}
```

### 3. Output Contract

#### `expected_output` (required)
- **Type:** `AnswerJsonContract` (Epic 8 schema)
- **Description:** The complete, valid answer_json response the model should generate
- **Validation:** Must conform to `backend/app/schemas/answer_json.schema.json`

**Required Fields in expected_output:**
- `version`: Contract version (e.g., `"kwanzaa.answer.v1"`)
- `answer.text`: Main response text
- `sources[]`: Array of source citations (empty for refusals)
- `retrieval_summary`: Full retrieval metadata
- `unknowns`: Limitations, gaps, and clarifying questions

**Key Integrity Checks:**
- If `toggles.require_citations = true`, sources must be provided (unless refusal)
- `retrieval_summary.results` should align with `retrieved_context` input
- `unknowns` fields should accurately reflect information gaps

### 4. Training Metadata

#### `metadata` (required)
Quality and annotation metadata for the sample:

```python
{
  "difficulty": "medium",              # easy | medium | hard
  "principle_focus": ["Imani"],        # Nguzo Saba principles
  "quality_score": 0.95,               # 0.0-1.0 rating
  "reviewer": "human_annotator_001",   # Optional reviewer ID
  "notes": "Excellent example...",     # Optional notes
  "edge_case": false,                  # Is this an edge case?
  "failure_mode": "..."                # What failure does this address?
}
```

##### `difficulty` (required)
- **easy**: Simple, straightforward query with clear answer
- **medium**: Requires synthesis or nuanced handling
- **hard**: Complex, ambiguous, or edge case scenario

##### `principle_focus` (required)
Array of Nguzo Saba principles this sample emphasizes:
- `Umoja` (Unity)
- `Kujichagulia` (Self-Determination)
- `Ujima` (Collective Work)
- `Ujamaa` (Cooperative Economics)
- `Nia` (Purpose)
- `Kuumba` (Creativity)
- `Imani` (Faith)

##### `quality_score` (required)
- **Type:** float, 0.0-1.0
- **Description:** Human-assigned quality rating
- **Guidelines:**
  - 0.9-1.0: Exemplary sample, perfect for training
  - 0.8-0.89: High quality, good training value
  - 0.7-0.79: Acceptable quality
  - Below 0.7: Should be revised or removed

## Sample Type Guidelines

### Citation Samples

**Purpose:** Teach the model to properly cite sources when good retrieval context is available.

**Requirements:**
- `category`: `"citation"`
- `retrieved_context`: MUST have at least one result with score > 0.8
- `expected_output.sources`: MUST contain properly formatted citations
- `expected_output.integrity.citations_provided`: `true`
- `expected_output.integrity.retrieval_confidence`: `"high"` or `"medium"`

**Example Use Cases:**
- Straightforward factual questions with clear sources
- Multi-source synthesis requiring multiple citations
- Demonstrating proper citation format and inline references

### Refusal Samples

**Purpose:** Teach the model to gracefully refuse when information is not in the corpus.

**Requirements:**
- `category`: `"refusal"`
- `retrieved_context`: Empty OR all results with score < 0.7
- `expected_output.sources`: Empty array `[]`
- `expected_output.integrity.citations_provided`: `false`
- `expected_output.integrity.fallback_behavior`: `"refusal"` or `"clarification_requested"`
- `expected_output.unknowns`: MUST be populated with specific gaps

**Example Use Cases:**
- Questions about data not in the corpus (current events, specific statistics)
- Queries requiring data types the corpus doesn't contain
- Overly specific questions without matching sources

### Grounded Answer Samples

**Purpose:** Teach the model to synthesize information from multiple sources while maintaining grounding.

**Requirements:**
- `category`: `"grounded_answer"`
- `retrieved_context`: Multiple results (2+) with varying relevance
- `expected_output.sources`: Multiple citations used in synthesis
- `expected_output.answer.text`: Clear synthesis with inline citations
- `expected_output.integrity.retrieval_confidence`: Usually `"high"`

**Example Use Cases:**
- Complex questions requiring multi-source synthesis
- Historical context building from multiple documents
- Technical explanations grounded in reference materials

### Format Compliance Samples

**Purpose:** Teach the model to strictly follow answer_json contract across edge cases.

**Requirements:**
- `category`: `"format_compliance"`
- Tests specific contract requirements or edge cases
- All required fields properly populated
- Demonstrates correct handling of optional fields

**Example Use Cases:**
- Minimal input edge cases (e.g., single-word queries)
- Complex queries with many unknowns
- Demonstrating all confidence and completeness levels
- Partial completeness scenarios

## Validation Rules

### Automatic Validation

The Pydantic models in `data/training/models.py` enforce:

1. **Schema Compliance**
   - All required fields present
   - Field types and formats correct
   - String lengths within bounds
   - Enums use valid values

2. **Cross-Field Consistency**
   - `persona` matches between sample and expected_output
   - Citation samples have high-quality context
   - Refusal samples have no/low-quality context
   - Unique sample IDs across dataset

3. **Answer Contract Validation**
   - `expected_output` conforms to Epic 8 schema
   - Required answer_json fields present
   - Citation integrity checks pass

### Manual Quality Checks

Human reviewers should verify:

1. **Accuracy**: Expected output is factually correct given the context
2. **Realism**: User query is representative of actual usage
3. **Pedagogy**: Sample effectively teaches the target behavior
4. **Diversity**: Sample adds unique value (not redundant)
5. **Cultural Sensitivity**: Content respects Nguzo Saba principles

## Usage Examples

### Loading and Validating a Dataset

```python
from data.training.models import TrainingDataset
import json

# Load dataset
with open("data/training/examples/citation-examples.json") as f:
    data = json.load(f)

# Validate with Pydantic
dataset = TrainingDataset(**data)

# Statistics are computed automatically
print(f"Total samples: {dataset.statistics.total_samples}")
print(f"By category: {dataset.statistics.by_category}")
```

### Creating a New Sample

```python
from data.training.models import (
    TrainingSample, TrainingCategory, Persona,
    RetrievalResult, AnswerJsonContract, TrainingMetadata
)

sample = TrainingSample(
    sample_id="citation_researcher_010",
    category=TrainingCategory.CITATION,
    persona=Persona.RESEARCHER,
    user_query="What was the significance of the March on Washington?",
    retrieved_context=[
        RetrievalResult(
            rank=1,
            score=0.95,
            chunk_id="mlk_speech::chunk::1",
            doc_id="mlk_speech",
            namespace="kwanzaa_primary_sources",
            content="I have a dream that one day...",
            metadata={...}
        )
    ],
    expected_output=AnswerJsonContract(...),
    metadata=TrainingMetadata(
        difficulty="medium",
        principle_focus=["Imani", "Nia"],
        quality_score=0.93
    )
)
```

## File Organization

```
data/training/
├── dataset-schema.json          # JSON Schema specification
├── models.py                    # Pydantic validation models
├── examples/
│   ├── citation-examples.json       # 5-10 citation samples
│   ├── refusal-examples.json        # 5-10 refusal samples
│   ├── grounded-answer-examples.json # 5-10 synthesis samples
│   └── format-compliance-examples.json # 5-10 edge cases
└── scripts/
    └── validate_dataset.py      # Validation utility
```

## Best Practices

### Sample Design

1. **One Clear Objective**: Each sample should teach one primary behavior
2. **Realistic Context**: Retrieval context should match production scenarios
3. **Complete Outputs**: Expected outputs should be exemplary, not minimal
4. **Edge Case Coverage**: Include samples for common failure modes
5. **Persona Alignment**: Query and response should fit the persona

### Quality Assurance

1. **Peer Review**: Have another annotator review high-value samples
2. **Production Testing**: Test samples against actual model outputs
3. **Iterative Refinement**: Update samples based on model performance
4. **Version Control**: Track changes to samples over time
5. **Metrics Tracking**: Monitor quality scores and difficulty distribution

### Corpus Management

1. **Balanced Distribution**:
   - All four categories represented
   - All four personas covered
   - Mix of difficulty levels
   - Coverage of Nguzo Saba principles

2. **Diversity Requirements**:
   - Different query types and phrasings
   - Various source types (speeches, documents, articles)
   - Multiple historical periods
   - Range of complexity levels

3. **Growth Strategy**:
   - Start with 5-10 samples per category (40 total minimum)
   - Expand to 20-50 per category for production (160-320 total)
   - Continuously add samples targeting observed failure modes

## Validation Script Usage

```bash
# Validate a single file
python data/training/scripts/validate_dataset.py \
  data/training/examples/citation-examples.json

# Validate all examples
python data/training/scripts/validate_dataset.py \
  data/training/examples/*.json

# Generate validation report
python data/training/scripts/validate_dataset.py \
  --report validation_report.txt \
  data/training/examples/*.json
```

## References

- **JSON Schema**: `data/training/dataset-schema.json`
- **Pydantic Models**: `data/training/models.py`
- **Answer Contract**: `backend/app/schemas/answer_json.schema.json`
- **Epic 8 Documentation**: `docs/epic8-implementation.md`
- **Issue Tracker**: GitHub Issue #55

## Changelog

### Version 1.0.0 (2026-01-16)
- Initial schema definition
- Four sample categories defined
- Pydantic validation models created
- Example samples provided (5-10 per category)
- Documentation completed
