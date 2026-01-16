# Kwanzaa Adapter Training Objectives

**Version:** 1.0.0
**Last Updated:** January 16, 2026
**Status:** Active
**Epic:** EPIC 11 — Fine-Tuning Execution

## Overview

This document defines the **four core objectives** for the Kwanzaa model adapter training. These objectives ensure the adapter produces responses that embody **Imani (Faith)** through verifiable sources, honest communication of limitations, and strict adherence to the Answer JSON contract.

The Kwanzaa adapter is not about general instruction-following or style transfer. It is a **specialized behavioral layer** that enforces:

1. **Citation-following** - Always cite sources when answering factual questions
2. **Retrieval usage** - Effectively leverage retrieved context from the corpus
3. **Refusal correctness** - Refuse gracefully when information is not in corpus
4. **Answer JSON compliance** - Output strictly valid `answer_json` format every time

---

## Table of Contents

- [Why These Objectives Matter](#why-these-objectives-matter)
- [Objective 1: Citation-Following](#objective-1-citation-following)
- [Objective 2: Retrieval Usage](#objective-2-retrieval-usage)
- [Objective 3: Refusal Correctness](#objective-3-refusal-correctness)
- [Objective 4: Answer JSON Compliance](#objective-4-answer-json-compliance)
- [Training Data Requirements Summary](#training-data-requirements-summary)
- [Evaluation Framework](#evaluation-framework)
- [Success Criteria](#success-criteria)
- [Nguzo Saba Alignment](#nguzo-saba-alignment)
- [References](#references)

---

## Why These Objectives Matter

### The Problem with Base Models

Pre-trained language models, even highly capable ones, have behaviors that conflict with the Kwanzaa mission:

- They **generate plausible-sounding answers** without evidence
- They **rarely cite sources** even when provided with retrieved context
- They **hallucinate confidently** rather than acknowledge gaps
- They **produce varied JSON structures** that break downstream rendering

### The Adapter Solution

A task-specific adapter (LoRA/QLoRA) teaches the model **new behavioral patterns**:

- Prioritize retrieved documents over parametric knowledge
- Format every response as valid `answer_json`
- Cite sources with full provenance metadata
- Refuse when corpus doesn't support the claim

This is not about changing what the model "knows" — it's about changing **how it responds** when integrated into the Kwanzaa RAG pipeline.

### Alignment with Project Mission

| Project Principle | How Objectives Support It |
|------------------|---------------------------|
| **Imani (Faith)** | Trust through citations, transparency about unknowns |
| **Kujichagulia (Self-Determination)** | User controls citation requirements via toggles |
| **Nia (Purpose)** | Education and research modes require citation discipline |
| **Kuumba (Creativity)** | Creative mode still respects retrieval and grounding |

---

## Objective 1: Citation-Following

### Definition

**The model must cite sources when answering factual questions, using retrieved documents from the corpus.**

When the system provides retrieved context (from semantic search), the adapter must:
- Identify relevant passages in the context
- Generate a response grounded in those passages
- Populate the `sources` array with proper citation metadata
- Reference sources naturally in the answer text when appropriate

### What Success Looks Like

**Positive Example:**

```json
{
  "version": "kwanzaa.answer.v1",
  "persona": "educator",
  "answer": {
    "text": "The Voting Rights Act of 1965 prohibited discriminatory voting practices that had been used to disenfranchise Black Americans, particularly in Southern states.",
    "confidence": 0.91,
    "tone": "educational",
    "completeness": "complete"
  },
  "sources": [
    {
      "citation_label": "National Archives (1965) — Voting Rights Act",
      "canonical_url": "https://www.archives.gov/milestone-documents/voting-rights-act",
      "source_org": "National Archives",
      "year": 1965,
      "content_type": "legal_document",
      "license": "Public Domain",
      "namespace": "kwanzaa_primary_sources",
      "doc_id": "nara_vra_1965",
      "chunk_id": "nara_vra_1965::chunk::2",
      "relevance_score": 0.94
    }
  ],
  "retrieval_summary": {
    "query": "What did the Voting Rights Act do?",
    "top_k": 5,
    "namespaces": ["kwanzaa_primary_sources"],
    "results": [...]
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [],
    "clarifying_questions": []
  }
}
```

**Negative Example (Base Model Behavior):**

```json
{
  "answer": {
    "text": "The Voting Rights Act was passed to protect voting rights."
  },
  "sources": [],
  "unknowns": {
    "unsupported_claims": ["Response not grounded in provided context"]
  }
}
```

### Measurable Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Citation Coverage Rate** | % of factual questions that include ≥1 citation | ≥90% for educator/researcher modes |
| **Citation Accuracy** | % of citations that correctly reference provided context | ≥95% |
| **Provenance Completeness** | % of sources with all required fields populated | 100% |
| **Grounding Score** | % of answer claims supported by cited sources | ≥85% |

### Evaluation Criteria

**Pass Conditions:**
- When retrieved context is relevant (score ≥0.7), model cites it in `sources`
- Citation metadata is complete (all required fields present)
- Answer text aligns with the content of cited sources
- Multiple relevant sources are cited when available

**Fail Conditions:**
- Model ignores retrieved context and generates from parametric knowledge
- Sources array is empty when relevant context is provided
- Citation metadata is incomplete or malformed
- Answer contradicts the cited sources

### Why This Objective Is Critical

**For Users:**
- Enables verification of claims
- Builds trust through transparency
- Supports academic/educational use cases

**For Kwanzaa:**
- Differentiates from "black box" AI systems
- Demonstrates respect for source material
- Fulfills Imani (Faith) principle

**For AINative Platform:**
- Showcases RAG effectiveness
- Proves adapter training can modify behavior
- Creates reusable pattern for other domains

### Training Data Requirements

**Volume:** 40-50 examples (33% of training set)

**Structure:**

```python
{
  "messages": [
    {
      "role": "system",
      "content": "You are Kwanzaa, an AI assistant that provides answers grounded in retrieved sources. You must cite sources using the answer_json format."
    },
    {
      "role": "user",
      "content": """Question: What was the purpose of the Civil Rights Act of 1964?

Retrieved Context:
[1] National Archives (1964) — Civil Rights Act
URL: https://www.archives.gov/milestone-documents/civil-rights-act
Content: "An Act to enforce the constitutional right to vote, to confer jurisdiction upon the district courts of the United States to provide injunctive relief against discrimination in public accommodations, to authorize the Attorney General to institute suits to protect constitutional rights in public facilities and public education..."
Score: 0.93

[2] Library of Congress — Civil Rights Timeline
URL: https://www.loc.gov/exhibits/civil-rights-act/
Content: "The Civil Rights Act of 1964 was the most comprehensive civil rights legislation since Reconstruction. It prohibited discrimination in public places, provided for the integration of schools and other public facilities..."
Score: 0.88"""
    },
    {
      "role": "assistant",
      "content": """{
  "version": "kwanzaa.answer.v1",
  "persona": "educator",
  "model_mode": "base_adapter_rag",
  "answer": {
    "text": "The Civil Rights Act of 1964 was landmark federal legislation that prohibited discrimination based on race, color, religion, sex, or national origin. It addressed discrimination in public accommodations, employment, and federally funded programs, and provided legal mechanisms for enforcement.",
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
      "relevance_score": 0.93
    }
  ],
  "retrieval_summary": {
    "query": "What was the purpose of the Civil Rights Act of 1964?",
    "top_k": 5,
    "namespaces": ["kwanzaa_primary_sources"],
    "results": [...]
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [],
    "clarifying_questions": []
  }
}"""
    }
  ]
}
```

**Key Variations Needed:**

1. **Single high-quality source** (score >0.9)
2. **Multiple complementary sources** (2-3 sources)
3. **Lower-quality retrieval** (score 0.7-0.8, still usable)
4. **Different content types** (legal documents, speeches, articles, letters)
5. **Different namespaces** (primary sources, Black press, speeches, STEM)
6. **Partial information** (corpus has some but not all details)

**Persona Coverage:**
- Educator mode: Detailed citations with educational framing
- Researcher mode: Multiple sources, acknowledgment of scholarly gaps
- Creator mode: Citations with creative synthesis
- Builder mode: Technical sources with implementation details

---

## Objective 2: Retrieval Usage

### Definition

**The model must effectively use retrieved context to generate answers, rather than relying on parametric knowledge.**

This objective ensures the adapter learns to:
- Prioritize retrieved content over pre-training knowledge
- Extract relevant information from provided passages
- Synthesize across multiple retrieved chunks when appropriate
- Acknowledge retrieval quality in the response

### What Success Looks Like

**Positive Example:**

```json
{
  "answer": {
    "text": "Based on the retrieved documents, Frederick Douglass delivered his famous 'What to the Slave is the Fourth of July?' speech on July 5, 1852, in Rochester, New York. The speech was a powerful critique of American independence celebrations while slavery persisted.",
    "confidence": 0.89,
    "tone": "educational",
    "completeness": "complete"
  },
  "sources": [
    {
      "citation_label": "Douglass, Frederick (1852) — Fourth of July Speech",
      "canonical_url": "https://teachingamericanhistory.org/document/what-to-the-slave-is-the-fourth-of-july/",
      "source_org": "Teaching American History",
      "year": 1852,
      "content_type": "speech_transcript",
      "namespace": "kwanzaa_speeches_letters",
      "doc_id": "douglass_july4_1852",
      "chunk_id": "douglass_july4_1852::chunk::1"
    }
  ],
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": ["Detailed audience reactions not included in corpus"],
    "clarifying_questions": []
  }
}
```

**Negative Example (Ignoring Retrieval):**

```json
{
  "answer": {
    "text": "Frederick Douglass was a prominent abolitionist who gave many speeches about slavery and freedom.",
    "confidence": 0.70,
    "completeness": "partial"
  },
  "sources": [],
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": ["Specific speech details from query not addressed"],
    "clarifying_questions": ["Which Frederick Douglass speech are you asking about?"]
  }
}
```

### Measurable Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Retrieval Utilization Rate** | % of responses that reference provided context | ≥95% when context score ≥0.7 |
| **Context Alignment Score** | Semantic similarity between answer and retrieved chunks | ≥0.80 |
| **Hallucination Rate** | % of factual claims NOT supported by context | ≤5% |
| **Multi-Source Synthesis** | % of answers using 2+ sources when multiple are relevant | ≥60% |

### Evaluation Criteria

**Pass Conditions:**
- Answer content closely matches retrieved context
- Specific facts (dates, names, quotes) come from context
- When multiple chunks are relevant, answer synthesizes them
- Answer doesn't introduce facts not present in context

**Fail Conditions:**
- Answer ignores high-quality retrieved context (score >0.85)
- Factual details contradict provided context
- Generic answer when specific context is available
- Hallucinates details not present in any retrieved chunk

### Why This Objective Is Critical

**For Users:**
- Ensures answers are grounded in the actual corpus
- Prevents contamination from model's pre-training biases
- Guarantees corpus quality directly impacts answer quality

**For Kwanzaa:**
- Validates the RAG architecture's value
- Ensures corpus curation directly improves outputs
- Prevents model from "going rogue" with parametric knowledge

**For AINative Platform:**
- Demonstrates RAG systems can override base model behavior
- Shows adapter training can enforce retrieval prioritization
- Proves semantic search integration effectiveness

### Training Data Requirements

**Volume:** 35-45 examples (29% of training set)

**Structure:**

```python
{
  "messages": [
    {
      "role": "system",
      "content": "You are Kwanzaa, an AI assistant. You must ground your answers in the retrieved context provided. If the context contains the answer, use it. Do not rely on your pre-training knowledge for factual claims."
    },
    {
      "role": "user",
      "content": """Question: When was Kwanzaa first celebrated?

Retrieved Context:
[1] Karenga, Maulana — Kwanzaa: Origins and Concepts
URL: https://www.officialkwanzaawebsite.org/origins.html
Content: "Kwanzaa was first celebrated in 1966. Dr. Maulana Karenga created Kwanzaa as a cultural holiday for African Americans in response to the Watts Rebellion and the broader Black Power movement."
Score: 0.96

[2] National Museum of African American History — Kwanzaa Timeline
Content: "The first Kwanzaa celebration took place from December 26, 1966, to January 1, 1967, in Los Angeles, California."
Score: 0.91"""
    },
    {
      "role": "assistant",
      "content": """{
  "version": "kwanzaa.answer.v1",
  "answer": {
    "text": "Kwanzaa was first celebrated in 1966, created by Dr. Maulana Karenga. The inaugural celebration took place from December 26, 1966, to January 1, 1967, in Los Angeles, California, during a period of cultural awakening in the African American community.",
    "confidence": 0.95,
    "tone": "educational",
    "completeness": "complete"
  },
  "sources": [
    {
      "citation_label": "Karenga, Maulana — Kwanzaa: Origins and Concepts",
      "canonical_url": "https://www.officialkwanzaawebsite.org/origins.html",
      "source_org": "Official Kwanzaa Website",
      "year": 1966,
      "content_type": "primary_source",
      "namespace": "kwanzaa_primary_sources",
      "doc_id": "karenga_origins",
      "chunk_id": "karenga_origins::chunk::1",
      "relevance_score": 0.96
    }
  ],
  "retrieval_summary": {
    "query": "When was Kwanzaa first celebrated?",
    "top_k": 5,
    "namespaces": ["kwanzaa_primary_sources"],
    "results": [...]
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [],
    "clarifying_questions": []
  }
}"""
    }
  ]
}
```

**Key Variations Needed:**

1. **Specific factual details** (dates, locations, numbers)
2. **Multi-document synthesis** (combining 2-3 sources)
3. **Context with direct quotes** (model should preserve them)
4. **Temporal information** (ensuring chronology from context)
5. **Contradictory signals** (context vs. likely pre-training knowledge)
6. **Dense technical content** (STEM, legal language)
7. **Narrative content** (speeches, letters, personal accounts)

---

## Objective 3: Refusal Correctness

### Definition

**The model must refuse gracefully when the corpus lacks sufficient information to answer a query, rather than hallucinating or providing generic responses.**

This is the **Imani (Faith)** objective — building trust through honest acknowledgment of limitations.

### What Success Looks Like

**Positive Example (Insufficient Context):**

```json
{
  "version": "kwanzaa.answer.v1",
  "persona": "educator",
  "toggles": {
    "require_citations": true,
    "primary_sources_only": true,
    "creative_mode": false
  },
  "answer": {
    "text": "I cannot provide a detailed answer about the specific economic impact of the Harlem Renaissance on Black-owned businesses because the current corpus does not contain sufficient primary source data on this topic. The retrieved documents focus on cultural and artistic contributions rather than economic analysis.",
    "confidence": 0.45,
    "tone": "educational",
    "completeness": "insufficient_data"
  },
  "sources": [],
  "retrieval_summary": {
    "query": "What was the economic impact of the Harlem Renaissance?",
    "top_k": 10,
    "namespaces": ["kwanzaa_primary_sources", "kwanzaa_black_press"],
    "results": [
      {
        "rank": 1,
        "score": 0.62,
        "snippet": "The Harlem Renaissance was a cultural movement...",
        "citation_label": "Poetry Foundation — Harlem Renaissance Overview"
      }
    ]
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [
      "Primary economic data on Black-owned businesses during 1920s-1930s",
      "Financial impact studies or contemporary business records",
      "Quantitative analysis of wealth creation during this period"
    ],
    "clarifying_questions": [
      "Are you interested in cultural influence instead?",
      "Would information about specific artists or venues be helpful?"
    ]
  },
  "integrity": {
    "citation_required": true,
    "citations_provided": false,
    "retrieval_confidence": "low",
    "fallback_behavior": "refusal"
  }
}
```

**Negative Example (Hallucination):**

```json
{
  "answer": {
    "text": "The Harlem Renaissance significantly boosted Black-owned businesses, with over 200 new establishments opening between 1920 and 1930. The economic impact was estimated at $50 million in today's dollars.",
    "confidence": 0.80,
    "completeness": "complete"
  },
  "sources": [],
  "unknowns": {
    "unsupported_claims": [
      "Specific numbers (200 establishments, $50M) not from corpus"
    ]
  }
}
```

### Measurable Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Refusal Precision** | % of refusals that are appropriate (low retrieval scores) | ≥90% |
| **Refusal Recall** | % of low-confidence retrievals that trigger refusal | ≥85% when score <0.6 |
| **False Confidence Rate** | % of answers with high confidence but no supporting sources | ≤5% |
| **Unknowns Completeness** | % of refusals that populate `missing_context` field | 100% |

### Evaluation Criteria

**Pass Conditions:**
- When retrieval score <0.6, model explicitly states information not available
- `unknowns.missing_context` is populated with specific gaps
- `integrity.fallback_behavior` = "refusal"
- Answer doesn't fabricate specific facts (dates, numbers, quotes)

**Fail Conditions:**
- Model provides confident answer with no supporting context
- Generic platitudes instead of specific refusal
- `sources` is empty but answer contains specific factual claims
- No acknowledgment of corpus limitations

### Why This Objective Is Critical

**For Users:**
- Prevents misinformation and hallucination
- Builds trust through transparency
- Enables users to identify corpus gaps and contribute sources

**For Kwanzaa:**
- Embodies Imani (Faith) principle operationally
- Differentiates from AI systems that "always have an answer"
- Creates feedback loop for corpus improvement

**For AINative Platform:**
- Demonstrates responsible AI behavior
- Shows RAG systems can acknowledge limitations
- Proves adapters can learn complex conditional behaviors

### Training Data Requirements

**Volume:** 25-35 examples (21% of training set)

**Structure:**

```python
{
  "messages": [
    {
      "role": "system",
      "content": "You are Kwanzaa, an AI assistant. When the retrieved context does not contain sufficient information to answer a question, you must explicitly refuse and explain what information is missing. Do not fabricate details."
    },
    {
      "role": "user",
      "content": """Question: What was Malcolm X's stance on the Vietnam War in 1965?

Retrieved Context:
[1] Malcolm X — Speech on Civil Rights (1964)
Content: "We need to fight for our rights here at home before we fight abroad..."
Score: 0.58

[2] Timeline of Malcolm X's Life
Content: "Malcolm X was assassinated on February 21, 1965, in New York City."
Score: 0.52

Note: Low relevance scores, context is tangential."""
    },
    {
      "role": "assistant",
      "content": """{
  "version": "kwanzaa.answer.v1",
  "persona": "educator",
  "toggles": {
    "require_citations": true,
    "primary_sources_only": true,
    "creative_mode": false
  },
  "answer": {
    "text": "I cannot provide a specific answer about Malcolm X's stance on the Vietnam War in 1965 because the corpus does not contain primary source material addressing this topic. Malcolm X was assassinated in February 1965, and the available documents focus on his civil rights work rather than his positions on foreign policy.",
    "confidence": 0.40,
    "tone": "educational",
    "completeness": "insufficient_data"
  },
  "sources": [],
  "retrieval_summary": {
    "query": "What was Malcolm X's stance on the Vietnam War in 1965?",
    "top_k": 10,
    "namespaces": ["kwanzaa_primary_sources", "kwanzaa_speeches_letters"],
    "results": [
      {
        "rank": 1,
        "score": 0.58,
        "citation_label": "Malcolm X — Speech on Civil Rights (1964)"
      }
    ]
  },
  "unknowns": {
    "unsupported_claims": [],
    "missing_context": [
      "Speeches or writings by Malcolm X specifically about Vietnam War",
      "Interviews or statements from 1964-1965 on foreign policy",
      "Contemporary news coverage of Malcolm X's position on Vietnam"
    ],
    "clarifying_questions": [
      "Would you like information about Malcolm X's general anti-imperialist views?",
      "Are you interested in Black leaders' responses to Vietnam War more broadly?"
    ]
  },
  "integrity": {
    "citation_required": true,
    "citations_provided": false,
    "retrieval_confidence": "low",
    "fallback_behavior": "refusal"
  }
}"""
    }
  ]
}
```

**Key Variations Needed:**

1. **Zero relevant results** (all scores <0.5)
2. **Low relevance** (scores 0.5-0.65, tangentially related)
3. **Partial information** (context has some details but not enough for complete answer)
4. **Out-of-scope temporal** (asking about events outside corpus time range)
5. **Out-of-scope topical** (asking about topics not in corpus at all)
6. **Requires creative mode** (user wants creative output but citations required)
7. **Toggle conflicts** (require_citations=true + creative_mode=true but no context)

**Refusal Variations:**
- Polite educational refusal
- Researcher-mode refusal with alternatives
- Creator-mode refusal offering creative alternative
- Builder-mode refusal with technical gap explanation

---

## Objective 4: Answer JSON Compliance

### Definition

**The model must output strictly valid `answer_json` format 100% of the time, with no deviations, malformations, or wrapper text.**

This objective ensures:
- Every response is valid JSON parseable
- All required fields are present
- Field types and constraints are respected
- No extraneous text before/after JSON
- Enum values match specification exactly

### What Success Looks Like

**Positive Example:**

```json
{
  "version": "kwanzaa.answer.v1",
  "persona": "researcher",
  "model_mode": "base_adapter_rag",
  "toggles": {
    "require_citations": true,
    "primary_sources_only": true,
    "creative_mode": false
  },
  "answer": {
    "text": "The 13th Amendment, ratified in 1865, abolished slavery and involuntary servitude in the United States, except as punishment for a crime.",
    "confidence": 0.94,
    "tone": "formal",
    "completeness": "complete"
  },
  "sources": [
    {
      "citation_label": "U.S. Constitution — 13th Amendment (1865)",
      "canonical_url": "https://www.archives.gov/milestone-documents/13th-amendment",
      "source_org": "National Archives",
      "year": 1865,
      "content_type": "legal_document",
      "license": "Public Domain",
      "namespace": "kwanzaa_primary_sources",
      "doc_id": "constitution_13th_amendment",
      "chunk_id": "constitution_13th_amendment::chunk::1",
      "relevance_score": 0.97
    }
  ],
  "retrieval_summary": {
    "query": "What did the 13th Amendment do?",
    "top_k": 5,
    "namespaces": ["kwanzaa_primary_sources"],
    "results": [
      {
        "rank": 1,
        "score": 0.97,
        "snippet": "Neither slavery nor involuntary servitude...",
        "citation_label": "U.S. Constitution — 13th Amendment (1865)",
        "canonical_url": "https://www.archives.gov/milestone-documents/13th-amendment",
        "doc_id": "constitution_13th_amendment",
        "chunk_id": "constitution_13th_amendment::chunk::1",
        "namespace": "kwanzaa_primary_sources"
      }
    ]
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
  },
  "provenance": {
    "generated_at": "2026-01-16T19:30:00Z",
    "model_version": "ai2-olmo-7b",
    "adapter_version": "kwanzaa-v1.0"
  }
}
```

**Negative Examples:**

```text
# Wrapper text (INVALID)
Here is the answer:
{"version": "kwanzaa.answer.v1", ...}

# Missing required field (INVALID)
{"version": "kwanzaa.answer.v1", "answer": {...}}
# Missing: sources, retrieval_summary, unknowns

# Invalid enum value (INVALID)
{"answer": {"tone": "casual"}}  # "casual" not in enum

# Malformed JSON (INVALID)
{"answer": {"text": "Something,}}  # Trailing comma, unclosed quote

# Type mismatch (INVALID)
{"answer": {"confidence": "high"}}  # Should be number 0.0-1.0
```

### Measurable Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **JSON Parse Rate** | % of responses that are valid JSON | 100% |
| **Schema Compliance Rate** | % of valid JSONs that pass schema validation | 100% |
| **Required Fields Rate** | % of responses with all required fields present | 100% |
| **Type Correctness Rate** | % of fields with correct data types | 100% |
| **Enum Compliance Rate** | % of enum fields with valid values | 100% |

### Evaluation Criteria

**Pass Conditions:**
- Response is valid JSON (no parse errors)
- All required fields present: `version`, `answer`, `sources`, `retrieval_summary`, `unknowns`
- Field types match schema (strings, numbers, arrays, objects)
- Enum values match specification (`tone`, `completeness`, `persona`, etc.)
- No wrapper text before or after JSON
- Array fields have correct structure (sources, results, etc.)

**Fail Conditions:**
- JSON parse error (syntax issue)
- Missing required field
- Type mismatch (string instead of number, etc.)
- Invalid enum value
- Wrapper text ("Here is the answer:", etc.)
- Malformed nested objects

### Why This Objective Is Critical

**For Users:**
- Enables reliable programmatic access to answers
- Powers AIKit rendering components
- Ensures consistent UX across all personas

**For Kwanzaa:**
- Foundational to "contract-driven" architecture
- Enables automated quality checks
- Required for analytics and citation tracking

**For AINative Platform:**
- Demonstrates structured output training effectiveness
- Shows adapters can enforce strict formatting
- Creates reusable pattern for contract-based AI

### Training Data Requirements

**Volume:** 20-30 examples (17% of training set, but ALL examples must be valid JSON)

**CRITICAL:** Every training example's assistant response must be valid `answer_json`. If a single example has invalid JSON, the adapter will learn incorrect formatting.

**Structure:**

All examples follow the same pattern — the assistant response is ONLY valid JSON, nothing else:

```python
{
  "messages": [
    {
      "role": "system",
      "content": "You are Kwanzaa. You must respond ONLY with valid JSON in the answer_json format. Do not include any text before or after the JSON."
    },
    {
      "role": "user",
      "content": "Question: What is Kwanzaa?\n\nRetrieved Context: [...]"
    },
    {
      "role": "assistant",
      "content": "{\"version\": \"kwanzaa.answer.v1\", ...}"  # ONLY JSON
    }
  ]
}
```

**Key Variations Needed:**

1. **Minimal response** (only required fields)
2. **Full response** (all optional fields included)
3. **Empty arrays** (`sources: []`, `unknowns.unsupported_claims: []`)
4. **Multiple sources** (2-5 items in sources array)
5. **Multiple retrieval results** (full results array)
6. **All personas** (educator, researcher, creator, builder)
7. **All tones** (neutral, educational, conversational, formal, creative)
8. **All completeness values** (complete, partial, insufficient_data)
9. **All retrieval confidence values** (high, medium, low, none)
10. **All fallback behaviors** (not_needed, creative_generation, refusal, clarification_requested)

**Special Cases:**
- Very long answer text (test escape handling)
- Sources with special characters in URLs
- Nested quotes in answer text
- Unicode characters (non-ASCII names, quotes)

**Validation Pipeline:**

Before including ANY example in training set:

1. Parse with `json.loads()` — must succeed
2. Validate with JSON Schema — must pass
3. Validate with Pydantic model — must pass
4. Check required fields manually
5. Check enum values manually

---

## Training Data Requirements Summary

### Total Training Set: 120-160 Examples

| Objective | Examples | % of Set | Priority |
|-----------|----------|----------|----------|
| Citation-Following | 40-50 | 33% | P0 |
| Retrieval Usage | 35-45 | 29% | P0 |
| Refusal Correctness | 25-35 | 21% | P0 |
| Answer JSON Compliance | 20-30 | 17% | P0 |

**Note:** These categories overlap. A single example can train multiple objectives simultaneously. For instance, a citation-following example also trains JSON compliance if the response is valid JSON.

### Distribution Requirements

#### By Persona

- **Educator**: 35% of examples (citation-heavy, educational tone)
- **Researcher**: 30% of examples (multiple sources, formal tone, acknowledgment of gaps)
- **Creator**: 20% of examples (creative synthesis, grounded generation)
- **Builder**: 15% of examples (technical content, implementation-focused)

#### By Namespace

- **kwanzaa_primary_sources**: 40% (legal documents, proclamations, archives)
- **kwanzaa_speeches_letters**: 25% (personal correspondence, public addresses)
- **kwanzaa_black_press**: 20% (news articles, editorials, journalism)
- **kwanzaa_black_stem**: 10% (scientific papers, technical documentation)
- **kwanzaa_teaching_kits**: 5% (educational materials, curricula)

#### By Difficulty

- **Easy**: 40% (single high-quality source, clear answer, score >0.85)
- **Medium**: 40% (multiple sources, synthesis needed, score 0.7-0.85)
- **Hard**: 20% (low relevance, refusal needed, complex multi-doc synthesis, score <0.7)

#### By Behavior Type

- **Positive examples** (good retrieval, cite sources): 60%
- **Refusal examples** (insufficient data, low scores): 25%
- **Partial examples** (some information available, acknowledge gaps): 15%

### Eval Set: 25-40 Examples

- **Coverage**: At least 5 examples per objective
- **Persona balance**: Representative of training distribution
- **Held-out content**: Different documents than training set
- **Edge cases**: Boundary conditions (score exactly 0.7, empty results, etc.)

### Data Quality Checklist

Every example must pass:

- [ ] Valid JSON (parseable)
- [ ] Schema compliant (all required fields)
- [ ] Realistic retrieved context (actual corpus content preferred)
- [ ] Proper citation metadata (complete provenance)
- [ ] Realistic relevance scores (0.0-1.0, calibrated)
- [ ] Appropriate refusal when needed (no hallucination)
- [ ] Diverse vocabulary (avoid repetitive phrasing)
- [ ] Correct enum values (check against spec)
- [ ] Aligned with Nguzo Saba principles (respect, accuracy)

---

## Evaluation Framework

### Automated Metrics (CI Pipeline)

**JSON Validity Check:**
```python
def evaluate_json_validity(responses: List[str]) -> float:
    """Returns percentage of responses that are valid JSON."""
    valid_count = 0
    for response in responses:
        try:
            json.loads(response)
            valid_count += 1
        except json.JSONDecodeError:
            pass
    return valid_count / len(responses)
```

**Schema Compliance Check:**
```python
def evaluate_schema_compliance(responses: List[str]) -> float:
    """Returns percentage passing JSON Schema validation."""
    from jsonschema import validate, ValidationError

    schema = load_answer_json_schema()
    compliant_count = 0

    for response in responses:
        try:
            data = json.loads(response)
            validate(instance=data, schema=schema)
            compliant_count += 1
        except (json.JSONDecodeError, ValidationError):
            pass

    return compliant_count / len(responses)
```

**Citation Coverage:**
```python
def evaluate_citation_coverage(eval_results: List[Dict]) -> Dict:
    """Evaluate citation behavior across personas."""
    by_persona = {}

    for result in eval_results:
        persona = result['persona']
        has_citations = len(result['response']['sources']) > 0
        retrieval_score = result['retrieval_summary']['results'][0]['score'] if result['retrieval_summary']['results'] else 0

        if persona not in by_persona:
            by_persona[persona] = {'total': 0, 'cited': 0, 'should_cite': 0}

        by_persona[persona]['total'] += 1

        if retrieval_score >= 0.7:
            by_persona[persona]['should_cite'] += 1
            if has_citations:
                by_persona[persona]['cited'] += 1

    # Calculate coverage rate per persona
    for persona in by_persona:
        if by_persona[persona]['should_cite'] > 0:
            by_persona[persona]['coverage_rate'] = (
                by_persona[persona]['cited'] / by_persona[persona]['should_cite']
            )

    return by_persona
```

**Refusal Correctness:**
```python
def evaluate_refusal_correctness(eval_results: List[Dict]) -> Dict:
    """Evaluate refusal behavior."""
    metrics = {
        'true_refusals': 0,  # Low score + refused
        'false_refusals': 0,  # High score + refused
        'missed_refusals': 0,  # Low score + didn't refuse
        'correct_answers': 0  # High score + answered
    }

    for result in eval_results:
        top_score = result['retrieval_summary']['results'][0]['score'] if result['retrieval_summary']['results'] else 0
        refused = result['response']['answer']['completeness'] == 'insufficient_data'

        if top_score < 0.6:
            if refused:
                metrics['true_refusals'] += 1
            else:
                metrics['missed_refusals'] += 1
        else:
            if refused:
                metrics['false_refusals'] += 1
            else:
                metrics['correct_answers'] += 1

    total = sum(metrics.values())
    metrics['refusal_precision'] = metrics['true_refusals'] / (metrics['true_refusals'] + metrics['false_refusals']) if (metrics['true_refusals'] + metrics['false_refusals']) > 0 else 0
    metrics['refusal_recall'] = metrics['true_refusals'] / (metrics['true_refusals'] + metrics['missed_refusals']) if (metrics['true_refusals'] + metrics['missed_refusals']) > 0 else 0

    return metrics
```

### Human Evaluation (Pre-Launch)

**Sample Size:** 20 responses per persona (80 total)

**Evaluation Dimensions:**

1. **Answer Quality** (1-5 scale)
   - Is the answer accurate based on sources?
   - Is the answer complete and helpful?
   - Is the tone appropriate for persona?

2. **Citation Quality** (1-5 scale)
   - Are sources relevant to the answer?
   - Is citation metadata complete and correct?
   - Would a user trust these citations?

3. **Refusal Appropriateness** (binary)
   - When refused, was refusal justified?
   - When didn't refuse, was answer grounded?

4. **Integrity & Trust** (1-5 scale)
   - Does response embody Imani (Faith)?
   - Would you use this in an educational setting?
   - Are limitations honestly communicated?

**Evaluator Instructions:**
- Assume role of persona user (educator, researcher, etc.)
- Check citations against actual sources when possible
- Flag any hallucinations, stereotypes, or cultural missteps
- Note any JSON formatting issues

### Regression Testing

**Trigger:** After any adapter retraining or base model update

**Test Suite:**
- 40 golden questions (10 per persona)
- Expected behavior defined (cite/refuse/answer)
- Automated comparison to baseline

**Pass Criteria:**
- JSON validity: 100%
- Schema compliance: 100%
- Citation coverage: ≥90% (educator/researcher)
- Refusal precision: ≥90%
- No behavioral regressions on golden set

---

## Success Criteria

### Minimum Viable Adapter (Launch Criteria)

The adapter is ready for production when:

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **JSON Parse Rate** | 100% | Automated eval on 40-question test set |
| **Schema Compliance** | 100% | JSON Schema validation + Pydantic validation |
| **Citation Coverage (Educator)** | ≥90% | Automated citation counter on high-confidence retrievals |
| **Citation Coverage (Researcher)** | ≥90% | Automated citation counter on high-confidence retrievals |
| **Refusal Precision** | ≥85% | Automated refusal evaluator on low-confidence test cases |
| **Refusal Recall** | ≥80% | Automated refusal evaluator on low-confidence test cases |
| **Human Quality Score** | ≥4.0/5.0 | Human eval on 80 sampled responses |
| **Zero Hallucinations** | 0 critical | Human review flags no fabricated quotes/facts |

### Stretch Goals (Post-Launch Iteration)

- **Citation coverage** ≥95% for all personas
- **Multi-source synthesis** ≥70% when 3+ sources available
- **Creative mode grounding** ≥80% of creative responses reference sources
- **User feedback** ≥4.5/5.0 trust rating from beta testers

---

## Nguzo Saba Alignment

Each objective directly implements one or more of the Seven Principles:

### Umoja (Unity)
- **Objective 4** ensures unified response format across all personas and modes
- Single `answer_json` contract creates consistency

### Kujichagulia (Self-Determination)
- User `toggles` control citation requirements and creative mode
- System respects user's choice of strictness level

### Ujima (Collective Work and Responsibility)
- **Objective 1** makes retrieval work visible through citations
- `retrieval_summary` shows what the system searched and found

### Ujamaa (Cooperative Economics)
- **Objective 1** ensures proper credit through provenance metadata
- Every source includes `source_org`, `year`, `license` for attribution

### Nia (Purpose)
- Education and research personas prioritize accuracy over creativity
- System is designed for learning, not entertainment

### Kuumba (Creativity)
- Creator persona can generate creative content while remaining grounded
- **Objective 2** ensures even creative mode leverages retrieved context

### Imani (Faith)
- **Objective 3** builds trust through honest refusal when data is lacking
- `unknowns` field transparently communicates limitations
- Citations enable verification and build user faith in the system

---

## References

- [Answer JSON Contract Documentation](/Users/aideveloper/kwanzaa/docs/answer_json_contract.md)
- [Kwanzaa Project README](/Users/aideveloper/kwanzaa/README.md)
- [PRD - EPIC 11: Fine-Tuning Execution](/Users/aideveloper/kwanzaa/docs/planning/prd.md#epic-11--fine-tuning-execution-first-time-friendly)
- [Namespace Strategy](/Users/aideveloper/kwanzaa/docs/architecture/namespace-strategy.md)
- JSON Schema: `/Users/aideveloper/kwanzaa/backend/app/schemas/answer_json.schema.json`
- Pydantic Models: `/Users/aideveloper/kwanzaa/backend/app/models/answer_json.py`

---

**Document Status:** Active
**Next Steps:**
1. Generate training examples following this specification (US-11.2)
2. Build dataset validator (US-11.4)
3. Run pilot training (US-11.8)
4. Evaluate against these metrics (US-11.11-11.13)

---

**Maintained by:** AINative Studio
**Project:** Kwanzaa - First Fruits for AI
**License:** Apache 2.0
