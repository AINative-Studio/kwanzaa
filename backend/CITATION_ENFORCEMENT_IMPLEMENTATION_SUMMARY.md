# Citation Enforcement Implementation Summary

**Issue:** #25 - Citation Enforcement Logic
**Date:** January 16, 2026
**Status:** Complete
**Tests:** 43/43 Passing

## Overview

Successfully implemented citation enforcement logic that refuses to answer when citations are required but retrieval is insufficient. This enforces **Imani (Faith)** through honest communication and prevents silent hallucinations.

## Files Created

### 1. Models
- `/Users/aideveloper/kwanzaa/backend/app/models/refusal.py`
  - `RefusalReason` enum (6 refusal reasons)
  - `RefusalContext` (context about refusal decision)
  - `RefusalSuggestion` (actionable suggestions)
  - `RefusalDecision` (complete refusal decision)
  - `PersonaThresholds` (persona-specific citation requirements)

### 2. Utilities
- `/Users/aideveloper/kwanzaa/backend/app/utils/citation_validator.py`
  - 16 validation functions for citation quality
  - Support for both `RetrievalResult` and `SearchResult`
  - Query type detection (factual/creative/analytical)
  - Gap description generation

### 3. Services
- `/Users/aideveloper/kwanzaa/backend/app/services/citation_enforcer.py`
  - `CitationEnforcer` service (main enforcement logic)
  - Persona threshold management
  - Refusal event logging
  - Integration with toggles and custom thresholds

### 4. Tests
- `/Users/aideveloper/kwanzaa/backend/tests/test_citation_enforcement.py`
  - 43 comprehensive tests (100% passing)
  - Unit tests for validators
  - Integration tests for enforcer
  - Edge case testing
  - Persona behavior verification

### 5. Documentation
- `/Users/aideveloper/kwanzaa/docs/architecture/citation-enforcement.md`
  - Complete architecture documentation
  - Refusal decision tree diagram
  - Integration points
  - Example refusal messages
  - Monitoring guidelines

## Refusal Decision Tree

```
Query → Citations Required? → Query Type Creative? → Allow
                            ↓
                         Yes: Check Results
                            ↓
                    Any Results? → No → REFUSE: INSUFFICIENT_RETRIEVAL
                            ↓
                          Yes
                            ↓
                    Has Citeable Content? → No → REFUSE: NO_CITEABLE_CONTENT
                            ↓
                          Yes
                            ↓
                    Meets Similarity Threshold? → No → REFUSE: LOW_SIMILARITY_SCORE
                            ↓
                          Yes
                            ↓
                    Enough Unique Sources? → No → REFUSE: BELOW_MIN_SOURCES
                            ↓
                          Yes
                            ↓
                    Primary Sources Required? → No → ALLOW
                            ↓
                          Yes
                            ↓
                    Has Primary Sources? → No → REFUSE: NO_PRIMARY_SOURCES
                            ↓
                          Yes → ALLOW
```

## Persona Thresholds

### Educator
- **Citations Required:** Yes
- **Similarity Threshold:** 0.80
- **Min Sources:** 2
- **Primary Sources Only:** No
- **Strict Mode:** Yes

**Use Case:** Educational contexts where accuracy is critical but flexibility is needed.

### Researcher
- **Citations Required:** Yes
- **Similarity Threshold:** 0.75
- **Min Sources:** 3
- **Primary Sources Only:** Yes
- **Strict Mode:** Yes

**Use Case:** Research applications requiring rigorous source verification.

### Creator
- **Citations Required:** No
- **Similarity Threshold:** 0.60
- **Min Sources:** 1
- **Primary Sources Only:** No
- **Strict Mode:** No

**Use Case:** Creative generation with optional grounding.

### Builder
- **Citations Required:** No
- **Similarity Threshold:** 0.65
- **Min Sources:** 1
- **Primary Sources Only:** No
- **Strict Mode:** No

**Use Case:** Technical/implementation contexts.

## Example Refusal Responses

### Insufficient Retrieval
```
I cannot provide a cited answer to this query because no relevant documents
were found in the current corpus. To maintain accuracy and trust, I must
refuse rather than provide an uncited response.

Suggestions:
- Try rephrasing your query with different keywords
- The corpus may need expansion to cover this topic
```

### Low Similarity Score
```
I cannot provide a cited answer because the retrieved documents have low
relevance (best: 0.65, required: 0.80). To maintain accuracy, I must refuse
rather than cite insufficient sources.

Suggestions:
- Rephrase your query to better match document content
- Use terminology that appears in historical documents
```

### No Primary Sources
```
I cannot provide a cited answer because no primary sources were found in the
retrieval results, and primary sources are required for researcher persona
queries.

Suggestions:
- Consider allowing secondary sources
- Ingest primary source documents on this topic (speeches, letters, official documents)
```

### Below Minimum Sources
```
I cannot provide a cited answer because only 1 source(s) were found, but 3
are required for confident citation.

Suggestions:
- Broaden your query to match more documents
- Use more general terms or remove specific constraints
```

## Test Coverage Summary

### Citation Validator Tests (14 tests)
- Similarity score validation
- Source counting (with duplicate handling)
- Minimum source validation
- Citeable content validation
- Query type detection (factual/creative/analytical)
- Gap description generation

### Search Result Validation Tests (2 tests)
- Primary source counting from search results
- Citeable content validation for search results

### Persona Thresholds Tests (6 tests)
- All persona defaults (educator, researcher, creator, builder)
- Persona lookup by name
- Invalid persona handling

### Citation Enforcer Tests (13 tests)
- Successful evaluation for different personas
- Refusal for insufficient retrieval
- Refusal for low similarity scores
- Refusal for no primary sources
- Refusal for below minimum sources
- Creative queries without citation requirements
- Toggle override behavior
- Search result evaluation
- Refusal event logging

### Integration Tests (5 tests)
- Boundary case (exact threshold match)
- Refusal message quality
- All personas behave correctly
- Custom thresholds override persona defaults
- No silent hallucinations verification

### Edge Cases (4 tests)
- Empty query handling
- Very long query handling
- None persona (fallback behavior)
- Invalid persona graceful handling

## Integration Points

### RAG Pipeline Integration
```python
# 1. Perform retrieval
retrieval_results = search_service.search(query, namespace, filters)

# 2. Enforce citation requirements
enforcer = CitationEnforcer()
decision = enforcer.evaluate_retrieval(
    query=query,
    results=retrieval_results,
    persona=persona,
    toggles=user_toggles,
)

# 3. Check decision
if decision.should_refuse:
    return create_refusal_response(decision)
else:
    return generate_answer(query, retrieval_results)
```

### Answer Contract Integration
When refusing, the system returns an `AnswerJsonContract` with:
- `answer.completeness = "insufficient_data"`
- `sources = []`
- `unknowns.missing_context` populated with specific gaps
- `integrity.fallback_behavior = "refusal"`

### Logging Integration
```python
enforcer = CitationEnforcer(enable_logging=True)
decision = enforcer.evaluate_retrieval(...)

# Get logged events
events = enforcer.get_refusal_events()
for event in events:
    analytics.log_refusal(event)
```

## Acceptance Criteria Verification

### 1. Citation Required and Missing → Model Refuses ✓
```python
# Test: test_evaluate_retrieval_fails_no_results
# Verifies that when citations are required (educator persona) and no
# results are found, the enforcer refuses to answer
decision = enforcer.evaluate_retrieval(
    query="What is Kwanzaa?",
    results=[],
    persona="educator",
)
assert decision.should_refuse is True
assert decision.context.reason == RefusalReason.INSUFFICIENT_RETRIEVAL
```

### 2. No Silent Hallucinations ✓
```python
# Test: test_no_silent_hallucinations
# Verifies that insufficient retrieval ALWAYS refuses when citations required
for persona in ["educator", "researcher"]:
    decision = enforcer.evaluate_retrieval(
        query="Factual query requiring citation",
        results=[],
        persona=persona,
    )
    assert decision.should_refuse is True
    assert decision.refusal_message is not None
```

### 3. Refusal Messages Clear and Helpful ✓
```python
# Test: test_refusal_message_quality
# Verifies refusal messages are substantive and include suggestions
decision = enforcer.evaluate_retrieval(...)
assert len(decision.refusal_message) > 50
assert "cannot" in decision.refusal_message.lower()
assert len(decision.specific_gaps) > 0
assert len(decision.suggestions) > 0
```

### 4. All Refusal Events Logged ✓
```python
# Test: test_refusal_event_logging
enforcer.evaluate_retrieval(
    query="What is Kwanzaa?",
    results=[],
    persona="educator",
)
events = enforcer.get_refusal_events()
assert len(events) == 1
assert events[0]["query"] == "What is Kwanzaa?"
assert events[0]["reason"] == RefusalReason.INSUFFICIENT_RETRIEVAL.value
```

## Key Features Implemented

1. **Citation Requirement Detection**
   - Persona settings (citations_required flag)
   - Query type detection (factual vs creative)
   - Mode settings (primary_sources_only flag)
   - Toggle overrides

2. **Citation Validation After Retrieval**
   - Check if retrieval returned results
   - Validate similarity scores meet threshold
   - Verify retrieved chunks contain citeable content
   - Count available sources

3. **Refusal Logic**
   - If citations_required=true AND insufficient retrieval → REFUSE
   - If primary_sources_only=true AND no primary sources → REFUSE
   - Persona-specific thresholds:
     - Educator: similarity < 0.80 → refuse
     - Researcher: similarity < 0.75 → refuse
     - Fewer than min_sources → refuse

4. **Refusal Response Format**
   - Compatible with answer_json contract
   - completeness="insufficient_data"
   - Populated unknowns[] array with specific gaps
   - Helpful refusal message (not evasive)
   - Actionable suggestions

5. **Logging for Evaluation**
   - Log all refusal events with reason
   - Track: query, persona, retrieval_score, threshold, decision
   - Enable analysis of refusal patterns

6. **Comprehensive Testing**
   - 43 tests covering all scenarios
   - Test prompts requiring citations without corpus support
   - Test boundary cases (score near threshold)
   - Test all personas' refusal behavior
   - Verify no silent hallucinations

## Performance Characteristics

- **Validation Speed:** O(n) where n is number of results
- **Memory Usage:** Minimal - only stores refusal events in-memory
- **Logging Overhead:** Optional, can be disabled
- **Thread-Safe:** Yes (no shared mutable state)

## Future Enhancements

1. **Adaptive Thresholds:** Learn optimal thresholds from user feedback
2. **Query Refinement:** Automatically suggest refined queries
3. **Corpus Gap Analysis:** Identify systematic gaps in corpus coverage
4. **Multi-language Support:** Extend to non-English queries
5. **Confidence Calibration:** Calibrate similarity thresholds based on corpus

## Usage Example

```python
from app.services.citation_enforcer import CitationEnforcer
from app.models.answer_json import Toggles

# Initialize enforcer with logging
enforcer = CitationEnforcer(enable_logging=True)

# Evaluate retrieval results
decision = enforcer.evaluate_retrieval(
    query="What was the Civil Rights Act of 1964?",
    results=retrieval_results,
    persona="educator",
    toggles=Toggles(
        require_citations=True,
        primary_sources_only=False,
        creative_mode=False,
    ),
)

# Check decision
if decision.should_refuse:
    print(f"Refusal Reason: {decision.context.reason}")
    print(f"Message: {decision.refusal_message}")
    print(f"Gaps: {decision.specific_gaps}")
    print(f"Suggestions: {[s.description for s in decision.suggestions]}")
else:
    print("Citation requirements met, can proceed with answer generation")

# Get refusal events for analytics
events = enforcer.get_refusal_events()
```

## Conclusion

The citation enforcement system is fully implemented and tested, providing robust protection against uncited responses while maintaining a helpful user experience through clear refusal messages and actionable suggestions. All acceptance criteria have been verified through comprehensive testing.

The system enforces **Imani (Faith)** by refusing to answer when we cannot provide proper citations, preventing silent hallucinations and building trust through honest communication of limitations.
