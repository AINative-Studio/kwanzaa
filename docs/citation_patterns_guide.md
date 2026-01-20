# Citation Patterns Guide for Kwanzaa RAG Model

**Version:** 1.0.0
**Last Updated:** January 16, 2026
**Purpose:** Training guide for proper citation patterns in RAG responses

---

## Table of Contents

- [Overview](#overview)
- [Core Citation Principles](#core-citation-principles)
- [Citation Pattern Types](#citation-pattern-types)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Anti-Patterns](#anti-patterns)
- [Quality Criteria](#quality-criteria)
- [Examples](#examples)

---

## Overview

The Kwanzaa RAG model enforces **Imani (Faith)** through transparent, accurate citations. Every claim must be grounded in retrieved sources, with proper attribution following the `answer_json` contract.

### Why Citations Matter

1. **Trust**: Users can verify claims against original sources
2. **Transparency**: "Show your work" builds confidence
3. **Accountability**: Prevents hallucination and misinformation
4. **Cultural Integrity**: Respects the voices and perspectives of source creators
5. **Educational Value**: Teaches proper research practices

---

## Core Citation Principles

### 1. Citation-First Mindset

**Always ask:** "What source supports this claim?"

If no source supports it:
- Don't make the claim
- Acknowledge the gap in `unknowns.missing_context`
- Offer to search for additional sources

### 2. Primary Sources Priority

When available, privilege:
- **Primary sources** (firsthand accounts, original documents)
- **Contemporary sources** (from the time period)
- **Authoritative institutions** (National Archives, Library of Congress)

Over:
- Secondary scholarly analysis
- Tertiary summaries or encyclopedias
- Undated or poorly sourced materials

### 3. Accurate Attribution

Citations must:
- Match the retrieved context exactly
- Include complete metadata (org, year, URL, license)
- Use correct chunk_id and doc_id
- Reflect relevance scores honestly

### 4. Transparent Limitations

Always acknowledge:
- Gaps in knowledge (`unknowns.missing_context`)
- Conflicting sources (`unknowns.unsupported_claims`)
- Partial answers (`answer.completeness: "partial"`)

---

## Citation Pattern Types

### Pattern 1: Single Source Citation

**Use when:** One authoritative source fully answers the query.

**Format:**
```
The Civil Rights Act of 1964 prohibited discrimination in public accommodations, employment, and federally funded programs [1].
```

**Requirements:**
- Clear attribution with [1] notation
- Source listed in `sources` array
- High confidence (0.9+) in retrieval

**Example Use Cases:**
- Factual historical dates
- Direct quotes from speeches
- Legal text from legislation

---

### Pattern 2: Multiple Source Synthesis

**Use when:** Multiple sources provide complementary information.

**Format:**
```
The Montgomery Bus Boycott had significant economic impact. The bus company lost over 65% of revenue [1], while daily ridership dropped from 30,000 to fewer than 8,000 passengers [2].
```

**Requirements:**
- Each claim cites its specific source
- Sources appear in relevance order
- Synthesize without contradicting sources

**Example Use Cases:**
- Comprehensive topic coverage
- Corroborating evidence
- Multiple perspectives

---

### Pattern 3: Conflicting Sources

**Use when:** Sources disagree on facts or interpretations.

**Format:**
```
Attendance estimates vary by source. The National Park Service reported 250,000 [1], while organizers claimed over 300,000 [2]. The most reliable figure appears to be the official estimate of 250,000 [1].
```

**Requirements:**
- Present all perspectives fairly
- Explain the conflict
- Indicate which source is most authoritative
- Document reasoning in answer text

**Example Use Cases:**
- Crowd size estimates
- Historical controversies
- Disputed dates or facts

---

### Pattern 4: Primary vs Secondary Sources

**Use when:** Combining firsthand accounts with scholarly analysis.

**Format:**
```
John Lewis described the Freedom Rides' purpose as testing federal enforcement of Boynton v. Virginia [1 - primary]. Historian Raymond Arsenault contextualizes this as strategic nonviolent direct action [2 - secondary].
```

**Requirements:**
- Clearly label source types
- Privilege primary source voice
- Use secondary for context only
- Maintain source hierarchy

**Example Use Cases:**
- Historical events with participant accounts
- Scholarly contextualization
- Research questions requiring both

---

### Pattern 5: Direct Quotation

**Use when:** Exact wording matters (famous quotes, legal language, precise statements).

**Format:**
```
Dr. King stated: "I have a dream that my four little children will one day live in a nation where they will not be judged by the color of their skin but by the content of their character" [1].
```

**Requirements:**
- Use quotation marks
- Preserve exact wording
- Include citation immediately after
- Note context if needed

**Example Use Cases:**
- Famous speeches
- Legal definitions
- Precise technical language

---

### Pattern 6: Paraphrasing

**Use when:** Restating source material for clarity or synthesis.

**Format:**
```
Rosa Parks explained that her refusal to give up her seat was not due to physical fatigue but rather moral exhaustion with injustice [1].
```

**Requirements:**
- Maintain meaning accurately
- Cite the source
- Don't misrepresent intent
- Preserve key phrases if meaningful

**Example Use Cases:**
- Complex technical content
- Synthesizing multiple points
- Improving readability

---

## Best Practices

### DO:

✓ **Cite every claim**
✓ **Use inline citations [1][2]**
✓ **Provide complete source metadata**
✓ **Acknowledge gaps in knowledge**
✓ **Prioritize primary sources**
✓ **Present conflicting sources fairly**
✓ **Use direct quotes when words matter**
✓ **Maintain cultural respect in framing**
✓ **Check citation integrity before responding**
✓ **Update `unknowns` when appropriate**

### DON'T:

✗ Make unsupported claims
✗ Cite sources not in retrieved context
✗ Fabricate metadata
✗ Ignore conflicting sources
✗ Misattribute quotes
✗ Use secondary sources when primary available
✗ Overstate confidence
✗ Hide limitations
✗ Cherry-pick sources to support bias
✗ Omit relevant counter-evidence

---

## Common Patterns

### Pattern: Multi-Source Historical Event

```
The March on Washington for Jobs and Freedom on August 28, 1963, drew approximately 250,000 people according to official National Park Service estimates [1]. Contemporary news coverage reported similar figures [2], and participant John Lewis recalled "more than 250,000" in his memoir [3]. This convergence of official records, news accounts, and participant memories provides high confidence in the attendance figure.
```

**Why this works:**
- Cites multiple source types
- Shows convergence of evidence
- Explains confidence level
- Maintains source diversity

---

### Pattern: Acknowledging Knowledge Gaps

```
The Civil Rights Act of 1964 prohibited discrimination in several key areas [1]. However, specific enforcement case law from 1965-1967 is not included in the corpus [unknowns.missing_context]. Would you like me to note areas where additional research would be valuable?
```

**Why this works:**
- Answers what can be answered
- Transparently notes gaps
- Offers to help further
- Maintains user trust

---

### Pattern: Primary Source Quote with Context

```
In her 1964 testimony before the Democratic National Convention, Fannie Lou Hamer described voting rights violations in Mississippi: "[exact quote]" [1]. This testimony galvanized national attention on voter suppression in the South and contributed to passage of the Voting Rights Act of 1965.
```

**Why this works:**
- Preserves powerful firsthand voice
- Provides historical context
- Proper attribution
- Explains significance

---

## Anti-Patterns

### Anti-Pattern 1: Vague Attribution

❌ **Bad:**
```
According to sources, the Montgomery Bus Boycott was effective.
```

✓ **Good:**
```
The Montgomery Bus Boycott achieved significant economic impact, with the bus company losing over 65% of revenue [1 - King, M.L. 1958].
```

**Why:** Vague "sources" provides no verifiability or trust.

---

### Anti-Pattern 2: Citation Without Retrieval

❌ **Bad:**
```
The Emancipation Proclamation freed all enslaved people [no source in retrieved_context].
```

✓ **Good:**
```
[If no source retrieved, acknowledge gap]
"I don't have sources in my corpus that directly address the Emancipation Proclamation. Let me search again with different keywords..."
```

**Why:** Never cite what you haven't retrieved. This violates Imani (Faith).

---

### Anti-Pattern 3: Ignoring Conflicting Sources

❌ **Bad:**
```
300,000 people attended the March on Washington [cherry-picking highest estimate].
```

✓ **Good:**
```
Attendance estimates range from 200,000 to over 300,000 [1][2]. The official National Park Service figure of 250,000 [1] is most commonly cited.
```

**Why:** Presenting only one side when sources disagree misleads users.

---

### Anti-Pattern 4: Misattributed Quotes

❌ **Bad:**
```
Martin Luther King Jr. said "I have a dream" [citing secondary source about the speech].
```

✓ **Good:**
```
Martin Luther King Jr. said "I have a dream..." [1 - King, M.L. Jr. (1963) — I Have a Dream Speech, National Archives].
```

**Why:** Quotes must cite original source, not secondary descriptions.

---

## Quality Criteria

### Citation Quality Checklist

For each response, verify:

- [ ] Every claim has a citation
- [ ] All citations reference retrieved_context
- [ ] Metadata is complete and accurate
- [ ] Relevance scores are realistic (0.7-0.99)
- [ ] Years match historical facts
- [ ] URLs are valid and permanent when possible
- [ ] Content_type accurately describes source
- [ ] License information is correct
- [ ] Namespace indicates corpus section
- [ ] Tags aid discoverability

### Answer Quality Checklist

- [ ] `answer.text` directly addresses user_query
- [ ] `answer.confidence` reflects retrieval quality
- [ ] `answer.tone` matches persona
- [ ] `answer.completeness` is honest
- [ ] `sources` array matches inline citations
- [ ] `retrieval_summary` shows the work
- [ ] `unknowns` acknowledges gaps
- [ ] `integrity.citations_provided` is true when required

---

## Examples

### Example 1: Educator Persona, Single Source

**Query:** "When was Kwanzaa first celebrated?"

**Answer:**
```
Kwanzaa was first celebrated in 1966 [1]. Dr. Maulana Karenga created this cultural and spiritual holiday to reaffirm and restore African culture and celebrate its value to Black American lives. The inaugural celebration took place from December 26, 1966 to January 1, 1967, with members of the US Organization in Los Angeles [1].
```

**Why this works:**
- Direct, factual answer
- Multiple facts from same source
- Educational tone
- Complete metadata in sources array

---

### Example 2: Researcher Persona, Multiple Sources

**Query:** "What evidence exists about the Montgomery Bus Boycott's economic impact?"

**Answer:**
```
Primary sources document significant economic impact from the Montgomery Bus Boycott:

Direct Impact on Bus Company:
- The bus company publicly acknowledged losing over 65% of its normal revenue during the boycott [1]
- Daily ridership dropped from approximately 30,000 to fewer than 8,000 passengers [2]
- The bus line operated at a deficit throughout 1956 [2]

Community Organization:
- The Black community, which comprised approximately 75% of pre-boycott bus riders, organized alternative transportation including carpools [2]

These figures come from contemporary sources: Dr. King's firsthand account published in 1958 [1] and newspaper financial reports from 1956 [2].
```

**Why this works:**
- Synthesis of multiple sources
- Clear attribution per claim
- Notes source types and dates
- Research-appropriate depth

---

### Example 3: Handling Conflicting Sources

**Query:** "What was the death toll during the Tulsa Race Massacre?"

**Answer:**
```
The death toll from the 1921 Tulsa Race Massacre remains a matter of historical controversy due to deliberate suppression of evidence:

Official Historical Estimate:
- The 2001 Oklahoma Commission concluded that between 100 and 300 people were killed [1]

Contemporary Reports:
- Initial 1921 newspaper reports cited official figures of only 36 deaths [2]
- However, Black residents and witnesses reported seeing many more bodies removed [2]

Recent Forensic Evidence:
- Forensic analysis (2019-2022) supports estimates of 100-300 casualties [3]
- Many victims were buried in unmarked graves and death certificates were destroyed [3]

The most reliable current estimate is 100-300 deaths [1][3], representing a significant historical correction from the long-understated official figure.
```

**Why this works:**
- Presents all perspectives
- Explains the controversy
- Indicates most reliable sources
- Acknowledges ongoing research
- Documents historical injustice

---

## Appendix: Answer JSON Citation Requirements

### Required Fields

Every citation-enabled response must include:

```json
{
  "version": "kwanzaa.answer.v1",
  "answer": {
    "text": "Answer with inline citations [1][2]",
    "confidence": 0.9,
    "tone": "educational",
    "completeness": "complete"
  },
  "sources": [
    {
      "citation_label": "Author (Year) — Title",
      "canonical_url": "https://...",
      "source_org": "Organization",
      "year": 1963,
      "content_type": "speech",
      "license": "Public Domain",
      "namespace": "kwanzaa_primary_sources",
      "doc_id": "unique_doc_id",
      "chunk_id": "unique_chunk_id",
      "tags": ["tag1", "tag2"],
      "relevance_score": 0.93
    }
  ],
  "retrieval_summary": {
    "query": "Original user query",
    "top_k": 10,
    "namespaces": ["kwanzaa_primary_sources"],
    "results": [...]
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [],
    "clarifying_questions": []
  },
  "integrity": {
    "citation_required": true,
    "citations_provided": true,
    "retrieval_confidence": "high",
    "fallback_behavior": "not_needed"
  }
}
```

### Citation Numbering

- Use `[1]` for first source, `[2]` for second, etc.
- Number in order of first appearance in answer text
- List sources in same order in `sources` array
- Match `relevance_score` to retrieval rank when appropriate

---

## Additional Resources

- [Answer JSON Contract Documentation](/Users/aideveloper/kwanzaa/docs/answer_json_contract.md)
- [Source Metadata Library](/Users/aideveloper/kwanzaa/data/training/source-metadata-library.json)
- [Citation Examples Dataset](/Users/aideveloper/kwanzaa/data/training/examples/citation-examples.json)
- [Validation Script](/Users/aideveloper/kwanzaa/scripts/validate_citation_examples.py)

---

**Maintained by:** AINative Studio
**Project:** Kwanzaa - First Fruits for AI
**License:** Apache 2.0
