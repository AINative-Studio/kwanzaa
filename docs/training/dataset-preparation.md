# Kwanzaa Adapter Training Dataset Preparation

**Version:** 1.0.0
**Date:** January 16, 2026
**Budget:** $500 - $5,000
**Status:** Ready for Implementation

## Executive Summary

This document outlines the strategy for creating a high-quality, small adapter training dataset focused on teaching the model four critical behaviors: citation, refusal, retrieval-grounded answers, and answer_json compliance. The approach prioritizes signal quality over quantity, targeting 120-200 training examples and 25-40 evaluation examples within a $500-$5k budget.

## Table of Contents

- [Dataset Objectives](#dataset-objectives)
- [Target Metrics](#target-metrics)
- [Dataset Composition](#dataset-composition)
- [Quality Criteria](#quality-criteria)
- [Data Collection Strategy](#data-collection-strategy)
- [Budget Breakdown](#budget-breakdown)
- [Annotation Guidelines](#annotation-guidelines)
- [Validation Process](#validation-process)
- [Timeline](#timeline)
- [Risk Mitigation](#risk-mitigation)

---

## Dataset Objectives

### Primary Training Goals

1. **Citation Behavior**
   - Model learns to cite sources using bracket notation [1][2]
   - Properly constructs citation_label strings
   - Matches citations to retrieval context
   - Uses multiple sources when appropriate

2. **Refusal Behavior**
   - Gracefully refuses when corpus lacks information
   - Provides helpful alternative directions
   - Populates `unknowns` fields accurately
   - Maintains educational tone during refusal

3. **Retrieval-Grounded Answers**
   - Synthesizes information from multiple sources
   - Stays grounded in retrieved context
   - Balances creativity with accuracy
   - Adapts to persona requirements

4. **answer_json Compliance**
   - Strictly follows contract structure
   - Populates all required fields correctly
   - Handles edge cases (empty sources, partial completeness)
   - Maintains schema validation across all outputs

### Secondary Goals

- Persona differentiation (educator vs. researcher vs. creator vs. builder)
- Appropriate confidence scoring
- Completeness classification accuracy
- Integrity metadata consistency

---

## Target Metrics

### Dataset Size

| Split | Minimum | Target | Maximum |
|-------|---------|--------|---------|
| Training | 120 | 160 | 200 |
| Evaluation | 25 | 32 | 40 |
| **Total** | **145** | **192** | **240** |

### Category Distribution (Training Set)

| Category | Minimum % | Target % | Example Count (160 target) |
|----------|-----------|----------|---------------------------|
| Citation | 30% | 35% | 56 |
| Refusal | 20% | 25% | 40 |
| Grounded Answer | 30% | 30% | 48 |
| Format Compliance | 10% | 10% | 16 |

### Persona Distribution (Training Set)

| Persona | Target % | Example Count (160 target) |
|---------|----------|---------------------------|
| Educator | 35% | 56 |
| Researcher | 25% | 40 |
| Creator | 25% | 40 |
| Builder | 15% | 24 |

### Difficulty Distribution (Training Set)

| Difficulty | Target % | Purpose |
|------------|----------|---------|
| Easy | 30% | Basic patterns, foundational behaviors |
| Medium | 50% | Realistic scenarios, nuanced cases |
| Hard | 20% | Edge cases, complex synthesis, failure modes |

### Principle Coverage

All Seven Principles should be represented, with emphasis on:
- **Imani (Faith)** - 100% of samples (trust through citations/refusal)
- **Nia (Purpose)** - 60% of samples (education-first design)
- **Ujima (Collective Work)** - 40% of samples (transparency, "show your work")
- **Kuumba (Creativity)** - 30% of samples (creator persona emphasis)
- Other principles - 20-30% each

---

## Dataset Composition

### Sample Structure

Each training sample must include:

```json
{
  "sample_id": "category_persona_###",
  "category": "citation|refusal|grounded_answer|format_compliance",
  "persona": "educator|researcher|creator|builder",
  "user_query": "The user's question (10-500 chars)",
  "retrieved_context": [...],
  "expected_output": { /* complete answer_json contract */ },
  "metadata": {
    "difficulty": "easy|medium|hard",
    "principle_focus": ["Imani", "Nia", ...],
    "quality_score": 0.0-1.0,
    "reviewer": "annotator_id",
    "notes": "Why this example matters",
    "edge_case": false,
    "failure_mode": "What this prevents"
  }
}
```

### Category-Specific Requirements

#### 1. Citation Examples (56 samples)

**Distribution:**
- Single source citation: 20 samples
- Multi-source citation (2-3 sources): 25 samples
- Multi-source citation (4+ sources): 11 samples

**Scenarios:**
- Historical fact with primary source support
- Multi-source synthesis for complex questions
- Different content types (legal docs, memoirs, essays, newspaper articles)
- Various citation styles (inline, list format)
- Cross-persona variation

**Quality Indicators:**
- Retrieval scores > 0.75
- Citations match retrieved content exactly
- Proper bracket notation [1][2]
- Complete source metadata in answer_json

#### 2. Refusal Examples (40 samples)

**Distribution:**
- Empty retrieval results: 15 samples
- Low relevance scores (<0.70): 15 samples
- Out-of-scope questions: 10 samples

**Scenarios:**
- Current events not in corpus
- Quantitative data requests without data
- Country-specific information lacking
- Requests requiring real-time knowledge
- Performative or culturally sensitive requests

**Quality Indicators:**
- Clear acknowledgment of limitation
- Helpful alternative suggestions
- Appropriate `unknowns` field population
- `out_of_scope` correctly identified
- Maintains helpful, educational tone

#### 3. Grounded Answer Examples (48 samples)

**Distribution:**
- 2-3 source synthesis: 25 samples
- 4+ source synthesis: 15 samples
- Persona-specific formatting: 8 samples

**Scenarios:**
- Explaining concepts across multiple sources
- Historical context requiring timeline construction
- Comparative analysis from different perspectives
- Technical specifications derived from cultural texts
- Age-appropriate or audience-specific adaptations

**Quality Indicators:**
- Proper source integration without hallucination
- Persona-appropriate tone and structure
- Completeness marked "complete" or "partial" accurately
- All claims traceable to sources
- Balanced confidence scores (0.80-0.95)

#### 4. Format Compliance Examples (16 samples)

**Distribution:**
- Edge case handling: 8 samples
- Minimal/maximal field population: 4 samples
- Completeness variations: 4 samples

**Scenarios:**
- Very short queries ("Hi", "Thanks")
- Overly complex multi-part questions
- Partial completeness with multiple unknowns
- High confidence with perfect retrieval
- Low confidence with poor retrieval

**Quality Indicators:**
- Valid JSON schema in all cases
- Required fields never omitted
- Appropriate use of optional fields
- Correct enum values
- Proper array/object nesting

---

## Quality Criteria

### Individual Sample Quality (Minimum 0.85/1.0)

Each sample must meet these standards:

#### 1. Correctness (0-1 scale)
- Retrieved context is realistic and relevant
- Expected output follows answer_json contract exactly
- Citations match retrieved chunks
- Metadata is accurate

#### 2. Educational Value (0-1 scale)
- Teaches a distinct behavior pattern
- Addresses common failure mode
- Provides clear positive example
- Generalizable to similar queries

#### 3. Diversity (0-1 scale)
- Not redundant with existing samples
- Covers unique persona/category/difficulty combination
- Explores different edge cases
- Varies query patterns and lengths

#### 4. Realism (0-1 scale)
- User query is natural and plausible
- Retrieved context matches actual corpus style
- Expected output is achievable by model
- Metadata reflects real-world uncertainty

### Batch Quality (Entire Dataset)

- **No duplicate scenarios** across samples
- **Balanced distribution** within 5% of target percentages
- **Coverage completeness** - all personas, categories, difficulties represented
- **Inter-annotator agreement** > 0.80 (Cohen's kappa) on sample quality
- **Schema validation** - 100% of samples pass JSON schema validation

---

## Data Collection Strategy

### Phase 1: Seed Dataset Creation (Internal, $0)

**Timeline:** Week 1-2
**Goal:** 40 high-quality seed examples (10 per category)

**Approach:**
1. Use existing project knowledge to create initial examples
2. Cover all four personas in seed set
3. Focus on clearest, most teachable patterns
4. Establish quality baseline

**Deliverables:**
- 10 citation examples
- 10 refusal examples
- 10 grounded answer examples
- 10 format compliance examples
- Annotation guidelines document

### Phase 2: Corpus-Derived Examples (Tool-Assisted, $500-$1,500)

**Timeline:** Week 3-4
**Goal:** 60 examples derived from actual corpus queries

**Approach:**
1. Run semantic search against actual Kwanzaa corpus
2. Capture real retrieval results for training context
3. Manually craft expected outputs based on retrieved content
4. Use LLM assistance to draft initial examples (human validates all)

**Budget Allocation:**
- LLM API calls for drafting: $200-$400
- Human validation/editing (20 hours @ $50/hr): $1,000
- Quality assurance: $300

**Tools:**
- GPT-4 or Claude for example drafting (with strict human oversight)
- ZeroDB semantic search for realistic retrieval
- Custom validation scripts

### Phase 3: Expert Annotation (Human Annotators, $2,000-$3,000)

**Timeline:** Week 5-7
**Goal:** 60-100 additional high-quality examples

**Approach:**
1. Hire 2-3 expert annotators with relevant backgrounds:
   - Educator with African American studies knowledge
   - Technical writer with RAG/AI experience
   - Researcher with primary source experience

2. Provide detailed annotation guidelines (see below)

3. Annotators create examples independently, then cross-validate

4. Project lead reviews all examples for quality

**Budget Allocation:**
- Annotator 1 (Educator): 30 examples @ $30/example = $900
- Annotator 2 (Technical): 30 examples @ $30/example = $900
- Annotator 3 (Researcher): 30 examples @ $30/example = $900
- Lead review/editing (20 hours @ $75/hr): $1,500
- **Total:** $4,200 (adjust based on volume)

**Quality Gates:**
- Initial training session with all annotators
- Weekly check-ins and calibration
- Random sample review (20% of examples)
- Final comprehensive review before release

### Phase 4: Evaluation Set Creation (Internal + Expert, $500-$1,000)

**Timeline:** Week 8
**Goal:** 25-40 evaluation examples (held-out test set)

**Approach:**
1. Create evaluation examples separately from training
2. Focus on harder cases and edge scenarios
3. Include "gotcha" cases that test overfitting
4. Ensure no overlap with training set

**Budget Allocation:**
- Expert evaluation design (10 hours @ $75/hr): $750
- Additional annotation if needed: $250

---

## Budget Breakdown

### Conservative Budget ($500-$1,500)

| Phase | Cost | Deliverable |
|-------|------|-------------|
| Phase 1: Seed | $0 | 40 samples |
| Phase 2: Corpus-Derived | $500-$1,500 | 60 samples |
| Phase 4: Eval Set | $0 (internal) | 25 samples |
| **Total** | **$500-$1,500** | **125 samples** |

**Approach:** Heavy internal contribution, LLM-assisted drafting with human validation, minimal external annotation. Suitable if team has domain expertise and time.

### Moderate Budget ($2,000-$3,500)

| Phase | Cost | Deliverable |
|-------|------|-------------|
| Phase 1: Seed | $0 | 40 samples |
| Phase 2: Corpus-Derived | $1,000-$1,500 | 60 samples |
| Phase 3: Expert Annotation | $1,500-$2,000 | 40 samples |
| Phase 4: Eval Set | $500 | 32 samples |
| **Total** | **$3,000-$4,000** | **172 samples** |

**Approach:** Mix of internal and external expertise, one expert annotator, comprehensive evaluation set. **RECOMMENDED APPROACH.**

### Full Budget ($4,000-$5,000)

| Phase | Cost | Deliverable |
|-------|------|-------------|
| Phase 1: Seed | $0 | 40 samples |
| Phase 2: Corpus-Derived | $1,500 | 60 samples |
| Phase 3: Expert Annotation | $4,200 | 90 samples |
| Phase 4: Eval Set | $1,000 | 40 samples |
| **Total** | **$6,700** | **230 samples** |

*(Adjust Phase 3 to 2 annotators to fit $5k budget: ~$3,300 total)*

**Approach:** Multiple expert annotators, maximum diversity, comprehensive coverage, robust evaluation. Provides highest quality and best coverage.

---

## Annotation Guidelines

### Annotator Instructions

#### 1. Understanding the Task

You are creating training examples that teach a language model to:
- Cite sources accurately using retrieved context
- Refuse gracefully when information is unavailable
- Provide grounded answers based on retrieval
- Follow the answer_json contract structure exactly

Each example has three main components:
1. **User Query** - What the user asks
2. **Retrieved Context** - Simulated search results from the corpus
3. **Expected Output** - The ideal answer_json response

#### 2. Creating User Queries

**Good Query Characteristics:**
- Natural, conversational language
- Realistic for the target persona
- Clear intent
- 10-500 characters
- Avoids ambiguity unless testing edge cases

**Examples:**
- ✅ "What did the Civil Rights Act of 1964 prohibit?"
- ✅ "Explain Umoja to middle school students"
- ✅ "How many people celebrate Kwanzaa in France?"
- ❌ "Tell me about stuff" (too vague)
- ❌ "What is the comprehensive historical analysis of..." (overly complex for simple query)

#### 3. Creating Retrieved Context

**Realistic Retrieval Properties:**
- Score range: 0.55-0.98 (perfect 1.0 is unrealistic)
- High relevance: 0.85-0.98
- Medium relevance: 0.70-0.84
- Low relevance: 0.55-0.69
- For refusals: often empty or <0.70

**Required Metadata Fields:**
- citation_label (human-readable)
- canonical_url (must be valid format)
- source_org (realistic organization)
- year (1600-2100, realistic for content)
- content_type (speech, letter, essay, etc.)
- license (Public Domain, CC BY, etc.)
- tags (relevant to content)

**Content Guidelines:**
- Chunk length: 100-500 words typically
- Mirrors actual corpus style
- Contains information relevant to query
- Realistic for the purported source

#### 4. Creating Expected Output

**answer_json Requirements:**

Always include:
- `version`: Always "kwanzaa.answer.v1"
- `answer.text`: 1-10,000 chars, addresses query
- `sources`: Array (may be empty for refusals)
- `retrieval_summary`: Must match retrieved_context
- `unknowns`: All required sub-fields

For citations:
- Use bracket notation [1][2] in answer.text
- Sources array order matches bracket numbers
- All cited sources must be in retrieved_context

For refusals:
- Empty or low-relevance retrieval
- Acknowledge limitation clearly
- Populate `unknowns.missing_context` and `unknowns.clarifying_questions`
- Consider `unknowns.out_of_scope` when appropriate

Persona-specific tone:
- **Educator**: Educational, accessible, patient
- **Researcher**: Formal, precise, methodological
- **Creator**: Conversational, collaborative, inspirational
- **Builder**: Technical, practical, implementation-focused

#### 5. Metadata Guidelines

**difficulty:**
- Easy: Straightforward query, clear retrieval, single source
- Medium: Multi-source synthesis, nuanced cases, persona adaptation
- Hard: Complex synthesis, edge cases, failure mode testing

**principle_focus:**
- Every sample must include at least ["Imani"]
- Add other principles as relevant to content

**quality_score:**
- Start at 1.0
- Deduct for any issues:
  - -0.05 for minor formatting inconsistencies
  - -0.10 for unrealistic elements
  - -0.15 for educational value concerns
  - -0.20 for correctness issues
- Minimum acceptable: 0.85

**notes:**
- Explain why this example is valuable
- Note any special considerations
- Reference similar examples if clustered

**edge_case:**
- Mark true for unusual scenarios
- Helps identify high-value testing examples

**failure_mode:**
- Document what common error this addresses
- Examples: "Hallucinating citations", "Refusing with good context available"

#### 6. Quality Checklist

Before submitting each example, verify:

- [ ] User query is natural and realistic
- [ ] Retrieved context has proper metadata
- [ ] Retrieval scores are realistic (not all 0.99)
- [ ] Expected output passes JSON schema validation
- [ ] Citations match retrieved_context exactly
- [ ] All required answer_json fields present
- [ ] Persona tone is appropriate
- [ ] Confidence score is realistic (0.80-0.95 for most)
- [ ] Completeness classification is accurate
- [ ] Unknowns are populated when appropriate
- [ ] Metadata is complete and accurate
- [ ] Quality score >= 0.85
- [ ] No obvious spelling/grammar errors
- [ ] Example teaches a distinct pattern

---

## Validation Process

### Automated Validation

**Schema Validation:**
```bash
# Validate all examples against JSON schema
python scripts/validate_training_data.py \
  --schema data/training/dataset-schema.json \
  --examples data/training/examples/*.json \
  --strict
```

**Contract Validation:**
```python
# Validate expected_output against answer_json contract
from backend.app.models.answer_json import AnswerJsonContract

for sample in training_samples:
    try:
        AnswerJsonContract.model_validate(sample['expected_output'])
    except ValidationError as e:
        print(f"Sample {sample['sample_id']} failed: {e}")
```

**Distribution Validation:**
```python
# Check distribution targets
assert category_distribution['citation'] >= 0.30
assert category_distribution['refusal'] >= 0.20
assert persona_distribution['educator'] >= 0.30
# ... etc
```

### Human Review Process

**Stage 1: Self-Review (Annotator)**
- Annotator reviews own work against checklist
- Quality score self-assessment
- Flag uncertain examples for lead review

**Stage 2: Peer Review (Inter-Annotator)**
- 20% random sample reviewed by peer annotator
- Cohen's kappa agreement > 0.80 required
- Discrepancies discussed and resolved

**Stage 3: Lead Review (Project Lead)**
- All edge_case=true examples reviewed
- All quality_score < 0.90 examples reviewed
- Random 10% sample of remaining examples
- Final approval for dataset inclusion

**Stage 4: Dataset Review (Full Team)**
- Review overall distribution
- Test random samples for realism
- Check for unintended biases
- Verify diversity and coverage

### Evaluation Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Schema Validity | 100% | Automated validation |
| Distribution Balance | ±5% of target | Statistical analysis |
| Inter-Annotator Agreement | >0.80 (Kappa) | Peer review sample |
| Average Quality Score | >0.90 | Human ratings |
| Realism Score | >4.0/5.0 | Blind human rating |
| Educational Value | >4.0/5.0 | Expert assessment |
| No Duplicates | 100% unique | Semantic similarity check |

---

## Timeline

### 8-Week Implementation Schedule

**Week 1-2: Phase 1 - Seed Dataset**
- Days 1-3: Create annotation guidelines
- Days 4-10: Create 40 seed examples (internal team)
- Days 11-14: Initial validation and schema testing

**Week 3-4: Phase 2 - Corpus-Derived Examples**
- Days 1-2: Set up corpus query pipeline
- Days 3-10: Generate and validate 60 corpus-derived examples
- Days 11-14: Quality review and refinement

**Week 5-7: Phase 3 - Expert Annotation** *(if budget allows)*
- Week 5 Day 1-2: Annotator training and calibration
- Week 5 Day 3 - Week 6 Day 5: Active annotation period
- Week 6 Day 6 - Week 7: Review, revisions, and finalization

**Week 8: Phase 4 - Evaluation Set**
- Days 1-5: Create evaluation set (25-40 examples)
- Days 6-7: Final validation and dataset release

### Accelerated Timeline (4-6 Weeks)

If needed, compress to:
- Weeks 1-2: Phases 1 & 2 combined (internal + LLM-assisted)
- Weeks 3-4: Phase 3 (expert annotation, if budget allows)
- Weeks 5-6: Phase 4 + validation

---

## Risk Mitigation

### Risk: Low Inter-Annotator Agreement

**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Extensive training session before annotation begins
- Clear examples of good vs. poor samples
- Weekly calibration meetings
- Early detection via 20% peer review
- Adjudication process for disagreements

### Risk: Budget Overrun

**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Phased approach allows stopping at any milestone
- Conservative budget estimate first ($500-$1,500)
- LLM-assisted drafting reduces human time
- Internal team can supplement if needed

### Risk: Insufficient Coverage

**Likelihood:** Low
**Impact:** Medium
**Mitigation:**
- Distribution targets set upfront
- Continuous monitoring during collection
- Gap analysis before final phase
- Flexibility to adjust category mix

### Risk: Quality Below Threshold

**Likelihood:** Low
**Impact:** High
**Mitigation:**
- Multi-stage review process
- Minimum quality score (0.85) enforced
- Lead review of all flagged examples
- Reject-and-replace process for poor samples

### Risk: Schema Changes Required

**Likelihood:** Low
**Impact:** Medium
**Mitigation:**
- Schema designed upfront with flexibility
- Version field allows evolution
- Early validation catches issues
- Automated migration scripts if needed

### Risk: Annotator Availability

**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Budget for 2-3 annotators (redundancy)
- Rolling recruitment (annotator pipeline)
- Internal team can fill gaps
- Extend timeline if needed

---

## Success Metrics

### Dataset Success Criteria

✅ **Completeness:**
- Minimum 145 samples (120 train + 25 eval)
- Target 192 samples (160 train + 32 eval)
- All categories and personas represented

✅ **Quality:**
- Average quality score > 0.90
- 100% schema validity
- Inter-annotator agreement > 0.80

✅ **Balance:**
- All distributions within ±5% of targets
- No persona <15% or >40%
- Difficulty spread: 30% easy / 50% medium / 20% hard

✅ **Diversity:**
- No duplicate scenarios
- All Seven Principles represented
- Mix of content types and years
- Various query patterns and lengths

### Downstream Model Success (Post-Training)

These metrics should be measured after adapter training:

- **Citation Accuracy:** >90% of answers with good retrieval include proper citations
- **Refusal Accuracy:** >85% of answers without good retrieval refuse appropriately
- **Format Compliance:** 100% valid answer_json outputs
- **Persona Consistency:** >80% human raters correctly identify persona from tone
- **Retrieval Grounding:** <5% hallucination rate (claims not in sources)

---

## Appendix A: Example Quality Rubric

### Individual Sample Scoring

**Correctness (Weight: 35%)**
- 1.0: Perfect accuracy, all fields valid, citations match
- 0.9: Minor metadata inconsistencies
- 0.8: Small factual issues or citation mismatches
- 0.7: Notable accuracy problems
- <0.7: Reject sample

**Educational Value (Weight: 30%)**
- 1.0: Teaches critical behavior, high impact
- 0.9: Solid educational example
- 0.8: Useful but not exceptional
- 0.7: Limited teaching value
- <0.7: Reject sample

**Realism (Weight: 20%)**
- 1.0: Completely realistic and natural
- 0.9: Very realistic with minor artifacts
- 0.8: Generally realistic
- 0.7: Somewhat artificial
- <0.7: Reject sample

**Diversity (Weight: 15%)**
- 1.0: Unique scenario, fills gap
- 0.9: Somewhat novel
- 0.8: Moderate overlap with existing
- 0.7: Significant redundancy
- <0.7: Reject sample

**Overall Quality Score = Weighted Average**

Minimum acceptable: 0.85

---

## Appendix B: Annotator Training Materials

### Training Session Agenda (2 hours)

**Part 1: Project Context (30 min)**
- Kwanzaa project overview
- Nguzo Saba principles
- Why this dataset matters
- Target model behaviors

**Part 2: answer_json Contract (30 min)**
- Contract structure walkthrough
- Required vs. optional fields
- Common pitfalls
- Schema validation demo

**Part 3: Annotation Process (30 min)**
- Sample creation workflow
- Quality criteria review
- Tools and resources
- Example review (good vs. poor)

**Part 4: Hands-On Practice (30 min)**
- Create 2 practice samples
- Peer review and feedback
- Q&A and clarification

### Post-Training Support

- Shared annotation document with examples
- Slack channel for quick questions
- Weekly check-in meetings
- Lead available for consultation

---

## Appendix C: Sample Validation Script

```python
#!/usr/bin/env python3
"""
Validate training dataset samples against schema and quality criteria.
"""
import json
from pathlib import Path
from jsonschema import validate, ValidationError
from collections import Counter

def validate_dataset(schema_path: str, examples_path: str):
    """Validate all examples against schema and distribution targets."""

    # Load schema
    with open(schema_path) as f:
        schema = json.load(f)

    # Load all example files
    examples = []
    for file_path in Path(examples_path).glob("*.json"):
        with open(file_path) as f:
            data = json.load(f)
            examples.extend(data['samples'])

    print(f"Loaded {len(examples)} samples")

    # Schema validation
    errors = []
    for sample in examples:
        try:
            validate(instance=sample, schema=schema['definitions']['training_sample'])
        except ValidationError as e:
            errors.append(f"{sample['sample_id']}: {e.message}")

    if errors:
        print(f"\n❌ Schema validation errors: {len(errors)}")
        for error in errors[:10]:  # Show first 10
            print(f"  - {error}")
    else:
        print("\n✅ All samples pass schema validation")

    # Distribution validation
    categories = Counter(s['category'] for s in examples)
    personas = Counter(s['persona'] for s in examples)
    difficulties = Counter(s['metadata']['difficulty'] for s in examples)

    print("\n📊 Distribution Analysis:")
    print(f"  Categories: {dict(categories)}")
    print(f"  Personas: {dict(personas)}")
    print(f"  Difficulties: {dict(difficulties)}")

    # Quality score analysis
    quality_scores = [s['metadata']['quality_score'] for s in examples]
    avg_quality = sum(quality_scores) / len(quality_scores)

    print(f"\n⭐ Quality Metrics:")
    print(f"  Average quality score: {avg_quality:.3f}")
    print(f"  Minimum quality score: {min(quality_scores):.3f}")
    print(f"  Samples below 0.85: {sum(1 for q in quality_scores if q < 0.85)}")

    # Final verdict
    schema_valid = len(errors) == 0
    quality_valid = avg_quality >= 0.90
    size_valid = len(examples) >= 120

    print(f"\n{'='*50}")
    if schema_valid and quality_valid and size_valid:
        print("✅ DATASET VALIDATION PASSED")
    else:
        print("❌ DATASET VALIDATION FAILED")
        if not schema_valid:
            print("  - Schema validation issues detected")
        if not quality_valid:
            print(f"  - Average quality ({avg_quality:.3f}) below 0.90")
        if not size_valid:
            print(f"  - Sample count ({len(examples)}) below 120")

if __name__ == "__main__":
    validate_dataset(
        schema_path="data/training/dataset-schema.json",
        examples_path="data/training/examples/"
    )
```

---

## Appendix D: Recommended Tools

### Data Collection
- **ZeroDB MCP**: Semantic search for realistic retrieval
- **GPT-4 / Claude**: Draft generation (human validates all)
- **Google Sheets**: Annotation tracking and collaboration

### Validation
- **jsonschema** (Python): Schema validation
- **Pydantic**: answer_json contract validation
- **pytest**: Automated test suite

### Quality Assurance
- **Inter-Rater Reliability Calculator**: Cohen's kappa computation
- **Semantic Similarity Tool**: Duplicate detection
- **Custom validation script**: Distribution and quality checks

### Collaboration
- **GitHub**: Version control for dataset
- **Slack**: Annotator communication
- **Notion/Docs**: Living annotation guidelines

---

## Conclusion

This dataset preparation strategy prioritizes quality over quantity, targeting the minimum viable dataset size (145 samples) with flexibility to scale to optimal size (192 samples) within budget constraints. The phased approach allows for early wins and iterative improvement, while rigorous quality criteria ensure every sample contributes meaningfully to adapter training.

The investment of $500-$5,000 produces a high-leverage asset: a carefully curated dataset that teaches critical RAG behaviors (citation, refusal, grounding, compliance) across diverse personas and scenarios. This dataset becomes the foundation for adapter fine-tuning, enabling the Kwanzaa model to embody Imani (Faith) through trustworthy, cited, and transparent responses.

**Next Steps:**
1. Approve budget and timeline
2. Finalize annotation guidelines
3. Begin Phase 1 seed dataset creation
4. Recruit expert annotators (if using Phase 3)
5. Execute collection phases
6. Validate and release dataset
7. Begin adapter training (separate PRD/issue)

---

**Document Prepared By:** AI Research Team
**Review Status:** Ready for Team Review
**Related Documents:**
- `/data/training/dataset-schema.json`
- `/data/training/examples/*.json`
- `/docs/answer_json_contract.md`
- `/docs/api/semantic-search-api.md`
