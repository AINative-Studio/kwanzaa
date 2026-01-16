# Citation Enforcement Architecture

**Version:** 1.0.0
**Last Updated:** January 16, 2026
**Status:** Active

## Overview

The Citation Enforcement system implements honest refusal logic when citations are required but retrieval results are insufficient. This enforces **Imani (Faith)** by refusing to answer rather than providing uncited or poorly-supported responses.

## Purpose

The citation enforcement system serves several critical purposes:

1. **Trust Through Honesty**: Refuse to answer when we cannot provide proper citations
2. **Quality Control**: Ensure all cited answers meet minimum quality thresholds
3. **Persona-Specific Standards**: Apply different citation requirements based on use case
4. **Transparent Limitations**: Communicate clearly what information is missing
5. **Prevention of Hallucinations**: Never generate uncited factual claims when citations are required

## Architecture Components

### 1. Refusal Models (`backend/app/models/refusal.py`)

Core data models for refusal decisions:

- **RefusalReason**: Enum of reasons for refusing to answer
- **RefusalContext**: Context information about why refusal occurred
- **RefusalSuggestion**: Actionable suggestions for improving queries
- **RefusalDecision**: Complete refusal decision with context and suggestions
- **PersonaThresholds**: Citation thresholds for different personas

### 2. Citation Validator (`backend/app/utils/citation_validator.py`)

Utilities for validating citation quality:

- `validate_similarity_scores()`: Check if retrieval scores meet threshold
- `count_sources()`: Count unique sources in results
- `validate_min_sources()`: Ensure minimum source count is met
- `count_primary_sources()`: Count primary sources
- `has_citeable_content()`: Verify results have complete citation metadata
- `detect_query_type()`: Classify queries as factual/creative/analytical
- `generate_gap_descriptions()`: Generate specific gap descriptions

### 3. Citation Enforcer (`backend/app/services/citation_enforcer.py`)

Main service implementing enforcement logic:

- `evaluate_retrieval()`: Main entry point for evaluation
- `evaluate_search_results()`: Evaluate search results
- Refusal event logging for analysis
- Integration with persona thresholds and toggles

## Refusal Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│ START: Citation Enforcement Evaluation                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Check: Citations     │
                  │ Required?            │
                  └──────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
               NO                        YES
                │                         │
                ▼                         ▼
      ┌─────────────────┐    ┌──────────────────────┐
      │ Check: Query     │    │ Check: Any Results   │
      │ Type Creative?   │    │ Returned?            │
      └────────┬─────────┘    └──────────┬───────────┘
               │                          │
          ┌────┴────┐              ┌──────┴──────┐
         YES       NO              NO            YES
          │         │               │             │
          ▼         │               ▼             ▼
    ┌─────────┐    │    ┌────────────────┐  ┌─────────────────────┐
    │ ALLOW   │    │    │ REFUSE:        │  │ Check: Citeable     │
    │         │    │    │ INSUFFICIENT   │  │ Content Present?    │
    └─────────┘    │    │ RETRIEVAL      │  └──────────┬──────────┘
                   │    └────────────────┘             │
                   │                           ┌────────┴────────┐
                   │                          NO               YES
                   │                           │                 │
                   │                           ▼                 ▼
                   │              ┌────────────────────┐  ┌─────────────────┐
                   │              │ REFUSE:            │  │ Check: Scores   │
                   │              │ NO_CITEABLE_       │  │ Meet Threshold? │
                   │              │ CONTENT            │  └──────┬──────────┘
                   │              └────────────────────┘         │
                   │                                   ┌─────────┴──────────┐
                   │                                  NO                   YES
                   │                                   │                    │
                   │                                   ▼                    ▼
                   │                      ┌────────────────────┐  ┌────────────────────┐
                   │                      │ REFUSE:            │  │ Check: Enough      │
                   │                      │ LOW_SIMILARITY_    │  │ Unique Sources?    │
                   │                      │ SCORE              │  └─────────┬──────────┘
                   │                      └────────────────────┘            │
                   │                                             ┌──────────┴──────────┐
                   │                                            NO                    YES
                   │                                             │                      │
                   │                                             ▼                      ▼
                   │                                ┌────────────────────┐  ┌───────────────────┐
                   │                                │ REFUSE:            │  │ Check: Primary    │
                   │                                │ BELOW_MIN_         │  │ Sources Required? │
                   │                                │ SOURCES            │  └─────────┬─────────┘
                   │                                └────────────────────┘            │
                   │                                                       ┌──────────┴──────────┐
                   │                                                      NO                    YES
                   │                                                       │                      │
                   │                                                       ▼                      ▼
                   │                                                 ┌──────────┐    ┌────────────────────┐
                   │                                                 │ ALLOW    │    │ Check: Primary     │
                   │                                                 │          │    │ Sources Found?     │
                   │                                                 └──────────┘    └──────────┬─────────┘
                   │                                                                            │
                   │                                                                 ┌──────────┴──────────┐
                   │                                                                NO                    YES
                   │                                                                 │                      │
                   │                                                                 ▼                      ▼
                   │                                                    ┌────────────────────┐  ┌──────────┐
                   │                                                    │ REFUSE:            │  │ ALLOW    │
                   │                                                    │ NO_PRIMARY_        │  │          │
                   │                                                    │ SOURCES            │  └──────────┘
                   │                                                    └────────────────────┘
                   │
                   └──────────────────────────────────────────────────────────────────────────────────────┐
                                                                                                            │
                                                                                                            ▼
                                                                                                  ┌──────────────────┐
                                                                                                  │ Apply Persona    │
                                                                                                  │ Defaults         │
                                                                                                  └──────────────────┘
```

## Persona Thresholds

Different personas have different citation requirements:

### Educator Persona

```python
PersonaThresholds(
    persona="educator",
    citations_required=True,
    similarity_threshold=0.80,
    min_sources=2,
    primary_sources_only=False,
    strict_mode=True,
)
```

**Use Case**: Educational contexts where accuracy is critical but flexibility is needed.

**Behavior**:
- Requires citations for all factual queries
- Requires 80% similarity minimum
- Needs at least 2 unique sources
- Accepts secondary sources
- Strict validation of citation metadata

### Researcher Persona

```python
PersonaThresholds(
    persona="researcher",
    citations_required=True,
    similarity_threshold=0.75,
    min_sources=3,
    primary_sources_only=True,
    strict_mode=True,
)
```

**Use Case**: Research applications requiring rigorous source verification.

**Behavior**:
- Always requires citations
- Requires 75% similarity (slightly lower to find more sources)
- Needs at least 3 unique sources
- **Only accepts primary sources**
- Strict validation

### Creator Persona

```python
PersonaThresholds(
    persona="creator",
    citations_required=False,
    similarity_threshold=0.60,
    min_sources=1,
    primary_sources_only=False,
    strict_mode=False,
)
```

**Use Case**: Creative generation with optional grounding.

**Behavior**:
- Citations optional (unless toggled on)
- Lower similarity threshold (60%)
- Only needs 1 source when citations used
- Accepts all source types
- Lenient validation

### Builder Persona

```python
PersonaThresholds(
    persona="builder",
    citations_required=False,
    similarity_threshold=0.65,
    min_sources=1,
    primary_sources_only=False,
    strict_mode=False,
)
```

**Use Case**: Technical/implementation contexts.

**Behavior**:
- Citations optional
- Moderate similarity threshold (65%)
- Lenient source requirements
- Accepts all source types

## Refusal Response Format

When refusing to answer, the system returns an `AnswerJsonContract` with:

```json
{
  "version": "kwanzaa.answer.v1",
  "persona": "educator",
  "answer": {
    "text": "I cannot provide a cited answer to this query because...",
    "completeness": "insufficient_data"
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
    "missing_context": [
      "No relevant documents found in the corpus",
      "Retrieved documents have low relevance (best: 0.65, required: 0.80)"
    ],
    "clarifying_questions": [
      "Could you rephrase your query with different keywords?",
      "Are you looking for information from a specific time period?"
    ]
  },
  "integrity": {
    "citation_required": true,
    "citations_provided": false,
    "retrieval_confidence": "none",
    "fallback_behavior": "refusal"
  }
}
```

## Example Refusal Messages

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

## Integration Points

### 1. RAG Pipeline Integration

The citation enforcer should be called **after retrieval** but **before generation**:

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
    # Return refusal response
    return create_refusal_response(decision)
else:
    # Proceed with generation
    return generate_answer(query, retrieval_results)
```

### 2. Answer Validation Integration

After generation, validate that the answer contract reflects refusal correctly:

```python
def validate_refusal_response(
    answer_contract: AnswerJsonContract,
    decision: RefusalDecision,
) -> bool:
    """Validate that refusal is properly reflected in answer contract."""
    if not decision.should_refuse:
        return True

    # Check answer completeness
    if answer_contract.answer.completeness != Completeness.INSUFFICIENT_DATA:
        return False

    # Check sources are empty
    if len(answer_contract.sources) > 0:
        return False

    # Check unknowns are populated
    if len(answer_contract.unknowns.missing_context) == 0:
        return False

    # Check integrity metadata
    if answer_contract.integrity:
        if answer_contract.integrity.fallback_behavior != FallbackBehavior.REFUSAL:
            return False

    return True
```

### 3. Logging Integration

All refusal events should be logged for analysis:

```python
# Enable logging in enforcer
enforcer = CitationEnforcer(enable_logging=True)

# Evaluate
decision = enforcer.evaluate_retrieval(...)

# Get logged events
events = enforcer.get_refusal_events()

# Log to analytics system
for event in events:
    analytics.log_refusal(
        query=event["query"],
        persona=event["persona"],
        reason=event["reason"],
        threshold=event["similarity_threshold"],
        actual=event["actual_similarity"],
    )
```

## Testing Strategy

### Unit Tests

- Test each validation function independently
- Test persona threshold configurations
- Test refusal message generation
- Test suggestion generation

### Integration Tests

- Test complete refusal workflow
- Test boundary cases (exact threshold match)
- Test all persona behaviors
- Test toggle overrides
- Test custom thresholds

### Acceptance Tests

- Verify no silent hallucinations occur
- Verify refusal messages are clear and helpful
- Verify all refusal events are logged
- Verify answer contract format is correct

## Performance Considerations

1. **Validation Speed**: All validation operations are O(n) where n is number of results
2. **Logging Overhead**: Logging is optional and can be disabled for performance
3. **Memory Usage**: Refusal events are stored in-memory; clear periodically
4. **Caching**: Persona thresholds can be cached to avoid repeated instantiation

## Security Considerations

1. **No PII in Logs**: Ensure queries don't contain PII before logging
2. **Rate Limiting**: Consider rate limiting to prevent abuse of refusal logging
3. **Input Validation**: All inputs are validated through Pydantic models
4. **Error Messages**: Refusal messages don't leak sensitive system information

## Future Enhancements

1. **Adaptive Thresholds**: Learn optimal thresholds from user feedback
2. **Query Refinement**: Automatically suggest refined queries
3. **Corpus Gap Analysis**: Identify systematic gaps in corpus coverage
4. **Multi-language Support**: Extend to non-English queries
5. **Confidence Calibration**: Calibrate similarity thresholds based on corpus characteristics

## Monitoring and Metrics

### Key Metrics to Track

1. **Refusal Rate by Persona**: Percentage of queries refused per persona
2. **Refusal Reasons Distribution**: Breakdown of refusal reasons
3. **Average Similarity Scores**: Track how close queries get to thresholds
4. **Source Count Distribution**: How many sources are typically found
5. **Query Types Distribution**: Factual vs creative vs analytical

### Alerting Thresholds

- Alert if refusal rate exceeds 50% for any persona
- Alert if NO_CITEABLE_CONTENT refusals spike (indicates ingestion issues)
- Alert if average similarity scores drop below 0.5 (indicates corpus drift)

## References

- [Answer JSON Contract](/Users/aideveloper/kwanzaa/docs/answer_json_contract.md)
- [Search Models](/Users/aideveloper/kwanzaa/backend/app/models/search.py)
- [Citation Validator](/Users/aideveloper/kwanzaa/backend/app/utils/citation_validator.py)
- [Citation Enforcer](/Users/aideveloper/kwanzaa/backend/app/services/citation_enforcer.py)
- [Issue #25: Citation Enforcement Logic](https://github.com/AINative-Studio/kwanzaa/issues/25)

---

**Maintained by:** AINative Studio
**Project:** Kwanzaa - First Fruits for AI
**License:** Apache 2.0
