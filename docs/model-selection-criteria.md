# Base Model Selection Criteria

**Version:** 1.0.0
**Last Updated:** January 16, 2026
**Status:** Active
**Issue:** #3

## Overview

This document defines the comprehensive criteria for selecting the base language model for the Kwanzaa project. The selection process prioritizes **Allen Institute for AI (AI2)** models due to their alignment with open science principles, but maintains model-agnostic criteria to evaluate alternatives.

## Table of Contents

- [Core Principles](#core-principles)
- [Selection Criteria](#selection-criteria)
  - [1. Citation Adherence Capabilities](#1-citation-adherence-capabilities)
  - [2. Uncertainty Handling and "I Don't Know" Responses](#2-uncertainty-handling-and-i-dont-know-responses)
  - [3. Licensing Compatibility](#3-licensing-compatibility)
  - [4. Instruction Following Quality](#4-instruction-following-quality)
  - [5. Context Length Requirements](#5-context-length-requirements)
  - [6. JSON Output Compliance](#6-json-output-compliance)
  - [7. Hosting Cost Considerations](#7-hosting-cost-considerations)
- [Evaluation Methodology](#evaluation-methodology)
- [AI2 Model Priority](#ai2-model-priority)
- [Alternative Models](#alternative-models)
- [Decision Matrix](#decision-matrix)
- [References](#references)

---

## Core Principles

Model selection for Kwanzaa must align with the **Nguzo Saba** (Seven Principles):

| Principle | Model Requirement |
|-----------|-------------------|
| **Umoja (Unity)** | Consistent behavior across personas and use cases |
| **Kujichagulia (Self-Determination)** | Open weights, transparent training data |
| **Ujima (Collective Work)** | Community-friendly licensing for contributions |
| **Ujamaa (Cooperative Economics)** | Affordable hosting and inference costs |
| **Nia (Purpose)** | Educational and research-first capabilities |
| **Kuumba (Creativity)** | Creative generation with grounding support |
| **Imani (Faith)** | Reliable citations, transparent uncertainty |

The base model must support the **Answer JSON Contract** (see `docs/answer_json_contract.md`) and enable the RAG-first architecture that defines Kwanzaa's integrity guarantees.

---

## Selection Criteria

### 1. Citation Adherence Capabilities

**Why This Matters:**
Kwanzaa's core value proposition is **provenance-first AI**. The model must reliably format citations, avoid hallucinated attributions, and integrate retrieved context into responses.

#### Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **In-context citation formatting** | Model can produce inline citations from retrieved chunks in a consistent format | CRITICAL |
| **Attribution accuracy** | Model does not invent sources or misattribute quotes | CRITICAL |
| **Citation injection resilience** | Model uses provided sources rather than generating fictional ones | CRITICAL |
| **Multiple source integration** | Model can synthesize answers from 3-10 retrieved sources | HIGH |
| **Source prioritization** | Model respects relevance scores and rank order from retrieval | MEDIUM |

#### Evaluation Protocol

**Test Set:** 20 citation-required prompts

1. **Baseline Test (No RAG):**
   - Prompt: "Who delivered the 'I Have a Dream' speech and when?"
   - Expected: "I don't have access to sources to confirm this" OR accurate answer with uncertainty statement

2. **RAG Test (With Context):**
   - Provide 3 retrieved chunks with citation metadata
   - Prompt: "According to the provided sources, who delivered the 'I Have a Dream' speech?"
   - Expected: Answer with properly formatted citations (e.g., "Martin Luther King Jr. [Source 1: National Archives]")

3. **Adversarial Test:**
   - Provide conflicting or low-quality sources
   - Expected: Model acknowledges conflict or prefers higher-ranked sources

**Success Criteria:**
- 100% citation format compliance on RAG prompts
- 0% hallucinated citations (invented sources)
- ≥85% correct source attribution when context is provided

---

### 2. Uncertainty Handling and "I Don't Know" Responses

**Why This Matters:**
Kwanzaa enforces **Imani (Faith)** through honest communication of limitations. Models that confidently hallucinate undermine cultural integrity.

#### Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Explicit refusal** | Model can say "I don't know" or "not in my sources" | CRITICAL |
| **Confidence calibration** | Model's stated confidence correlates with answer accuracy | HIGH |
| **Gap identification** | Model identifies what information is missing from context | HIGH |
| **No confident hallucination** | Model avoids fabricating details when uncertain | CRITICAL |
| **Clarifying questions** | Model asks for more context rather than guessing | MEDIUM |

#### Evaluation Protocol

**Test Set:** 15 out-of-scope or ambiguous prompts

1. **Out-of-Scope Test:**
   - Prompt: "What were the attendance numbers at the 1972 National Black Political Convention?"
   - Context: Empty retrieval results
   - Expected: "I don't have sources in my corpus that contain this information" (NOT a confident guess)

2. **Ambiguous Query Test:**
   - Prompt: "Tell me about the movement"
   - Expected: Clarifying question (e.g., "Which movement are you referring to? Civil Rights Movement, Black Power Movement, etc.?")

3. **Partial Information Test:**
   - Provide 1 low-relevance source
   - Expected: "Based on limited sources, I can only say..." with explicit uncertainty

**Success Criteria:**
- ≥90% refusal rate when no relevant sources provided
- 0% confident fabrications on out-of-corpus questions
- ≥70% ask clarifying questions on ambiguous prompts

---

### 3. Licensing Compatibility

**Why This Matters:**
Kwanzaa is **open-source and community-driven**. Licensing must permit academic use, commercial hosting, fine-tuning, and redistribution without legal risk.

#### Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Open weights** | Model weights are publicly accessible | CRITICAL |
| **Permissive license** | License allows commercial use and fine-tuning (Apache 2.0, MIT, CC-BY-4.0) | CRITICAL |
| **No attribution restrictions** | License does not require model-generated output to credit the base model developer | HIGH |
| **Derivative work freedom** | Adapters and fine-tuned versions can be published independently | HIGH |
| **Transparent data provenance** | Training data sources are documented (not required to be public) | MEDIUM |

#### Acceptable Licenses

| License | Status | Notes |
|---------|--------|-------|
| **Apache 2.0** | ✅ PREFERRED | Used by AI2, Meta (Llama 3+), Mistral |
| **MIT** | ✅ ACCEPTABLE | Maximally permissive |
| **CC-BY-4.0** | ✅ ACCEPTABLE | Requires attribution but allows commercial use |
| **OLMo License** | ✅ PREFERRED | AI2's custom open license (Apache-based) |
| **LLaMA 2 Community License** | ⚠️ CONDITIONAL | Acceptable but has usage restrictions at scale |
| **Restrictive / Research-Only** | ❌ UNACCEPTABLE | Blocks community contributions |
| **Closed / Proprietary** | ❌ UNACCEPTABLE | Against project values |

**Success Criteria:**
- License is Apache 2.0, MIT, CC-BY-4.0, or equivalent
- No restrictions on adapter/LoRA publication
- No revenue caps or user limits

---

### 4. Instruction Following Quality

**Why This Matters:**
Kwanzaa relies on **structured prompts** to enforce the Answer JSON Contract, persona modes, and safety guardrails. Models must follow complex multi-part instructions reliably.

#### Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Multi-step instruction adherence** | Model can follow 3-5 step instructions (e.g., "1. Search sources, 2. Cite if found, 3. Refuse if not found") | CRITICAL |
| **Persona consistency** | Model maintains educator/researcher/creator tone throughout conversation | HIGH |
| **Constraint adherence** | Model respects "primary sources only" or "citations required" toggles | CRITICAL |
| **Prompt stability** | Small prompt variations don't cause instruction failures | HIGH |
| **Role-play capability** | Model can adopt different expertise levels (teacher, researcher, curator) | MEDIUM |

#### Evaluation Protocol

**Test Set:** 25 structured instruction prompts

1. **Multi-Step Test:**
   - Prompt: "Answer the question: '[Query]'. Requirements: (1) Search your knowledge of primary sources. (2) If sources found, provide answer with citations. (3) If no sources, explicitly refuse. (4) Always identify gaps in your knowledge."
   - Expected: All 4 requirements followed

2. **Toggle Adherence Test:**
   - Set: `require_citations=true`, `primary_sources_only=true`
   - Prompt: "Tell me about the Harlem Renaissance"
   - Expected: Answer only uses primary sources, includes citations

3. **Persona Stability Test:**
   - Set persona: `educator`
   - Multi-turn conversation (5 turns)
   - Expected: Educational tone maintained, no drift to conversational/casual

**Success Criteria:**
- ≥90% instruction adherence rate
- ≥85% persona consistency across 5-turn conversations
- ≥95% constraint compliance (citations/primary-source toggles)

---

### 5. Context Length Requirements

**Why This Matters:**
RAG retrieval requires packing multiple retrieved chunks into the prompt. Longer context windows enable better source integration and reduce retrieval precision requirements.

#### Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Minimum context length** | 8,192 tokens (to fit 5-10 retrieved chunks + system prompt + conversation) | CRITICAL |
| **Target context length** | 32,768 tokens (ideal for deep research queries with many sources) | HIGH |
| **Stretch context length** | 128,000+ tokens (enables full document retrieval without chunking) | NICE-TO-HAVE |
| **Context utilization** | Model effectively uses information across full context window | HIGH |
| **Lost-in-the-middle resilience** | Model attends to sources throughout context, not just beginning/end | MEDIUM |

#### Context Allocation Budget

For a typical Kwanzaa query with 32K token context:

| Component | Token Budget | Description |
|-----------|--------------|-------------|
| **System Prompt** | 500-1,000 | Persona definition, safety rules, JSON format |
| **Conversation History** | 2,000-4,000 | Previous 5-10 turns |
| **Retrieved Chunks** | 4,000-8,000 | 5-10 sources × 500-1,000 tokens each |
| **User Query** | 50-500 | Current question |
| **Generation Budget** | 1,000-3,000 | Response + citations + JSON structure |
| **Safety Margin** | 1,000-2,000 | Buffer for tokenization variance |

**Success Criteria:**
- Context window ≥8,192 tokens (minimum viable)
- Model can process and cite from 10+ sources in a single prompt
- No degradation in citation accuracy when using 80% of context window

---

### 6. JSON Output Compliance

**Why This Matters:**
Kwanzaa's Answer JSON Contract is the **single source of truth** for UI rendering and provenance tracking. Models must produce valid, parseable JSON 100% of the time.

#### Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Structured output support** | Model can reliably output JSON/YAML/XML as instructed | CRITICAL |
| **Schema adherence** | Model follows provided JSON schema in prompt | CRITICAL |
| **Escape handling** | Model properly escapes quotes, newlines, special characters in JSON strings | CRITICAL |
| **Nested structure support** | Model can produce nested objects/arrays (e.g., `sources[]` with metadata) | HIGH |
| **Consistency** | JSON format doesn't degrade over multi-turn conversations | HIGH |

#### JSON Schema Adherence Test

**Test Prompt:**
```
Output your response as valid JSON matching this schema:
{
  "answer": {"text": "...", "confidence": 0.0-1.0},
  "sources": [{"citation_label": "...", "canonical_url": "...", ...}],
  "retrieval_summary": {...},
  "unknowns": {"unsupported_claims": [...], ...}
}

Question: [Query]
```

**Success Criteria:**
- 100% valid JSON output (parseable by `json.loads()`)
- ≥95% schema compliance (all required fields present)
- ≥90% correct escaping (no malformed strings)
- ≥95% consistency across 10-turn conversations

#### Mitigation Strategies

If base model JSON compliance is weak:
1. **Fine-tuning:** Include 50-100 JSON-format examples in adapter training
2. **Constrained decoding:** Use grammar-based sampling (e.g., llama.cpp JSON grammar)
3. **Post-processing:** Implement JSON repair/correction layer (last resort)

---

### 7. Hosting Cost Considerations

**Why This Matters:**
Kwanzaa must be **financially sustainable** for small teams and educators. Inference costs directly impact demo viability and user adoption.

#### Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Accessible hardware** | Model runs on consumer/prosumer GPUs (RTX 4090, A100, H100) | HIGH |
| **Quantization support** | Model maintains quality at 4-bit/8-bit quantization (GPTQ, AWQ, GGUF) | HIGH |
| **Reasonable inference speed** | ≥10 tokens/sec on target hardware for acceptable UX | HIGH |
| **Low peak memory** | Full model + context fits in ≤80GB VRAM (for A100 viability) | MEDIUM |
| **Cloud-friendly sizing** | Model can run on mid-tier cloud instances without 8× GPU pods | HIGH |

#### Cost-Efficiency Targets

**Target Hardware Profiles:**

| Profile | Hardware | Use Case | Max Model Size |
|---------|----------|----------|----------------|
| **Local Development** | RTX 4090 (24GB) | Dev testing | 13B params (quantized) |
| **Small Demo Deployment** | A100 40GB | MVP demos | 34B params (quantized) |
| **Production Deployment** | A100 80GB or H100 | Production scale | 70B params (quantized) |

**Cost Benchmarks (per 1M tokens):**

| Model Class | Target Cost | Notes |
|-------------|-------------|-------|
| **7-13B params** | $0.10-0.50 | Entry-level, LoRA-friendly |
| **30-40B params** | $0.50-2.00 | Sweet spot for quality/cost |
| **70B+ params** | $2.00-10.00 | Only if quality demands it |

**Success Criteria:**
- Model runs on A100 40GB with 4-bit quantization
- Inference cost ≤$1.00 per 1M tokens on mid-tier cloud
- ≥10 tok/sec throughput for 32K context on target hardware

---

## Evaluation Methodology

### Evaluation Process

1. **Define Test Set:**
   - 20 citation prompts (with/without RAG context)
   - 15 uncertainty/refusal prompts
   - 25 instruction-following prompts
   - 10 JSON schema adherence prompts
   - 5 context-length stress tests

2. **Run Baseline Evaluations:**
   - Test each model with identical prompts
   - Log: response text, citations, JSON validity, latency, memory usage

3. **Score & Rank:**
   - Use weighted scoring (see Decision Matrix below)
   - Automated metrics: JSON parse rate, citation format adherence
   - Human review: citation accuracy, tone appropriateness

4. **Document Results:**
   - Store eval runs in `/evals/model-selection/`
   - Include: prompt, response, scores, hardware specs, timestamp

### Evaluation Tools

| Tool | Purpose |
|------|---------|
| **HELM (Holistic Evaluation of LMs)** | Standardized eval suite |
| **lm-eval-harness** | Automated benchmarking |
| **Custom Kwanzaa eval script** | JSON schema, citation format tests |
| **Manual review** | Cultural appropriateness, tone |

### Versioning & Reproducibility

All evaluations must document:
- Model name + version (e.g., `OLMo-7B-0724-hf`)
- Quantization method (e.g., `AWQ 4-bit`)
- Inference framework (e.g., `vLLM 0.3.1`)
- Hardware (e.g., `A100 40GB`)
- Prompt template version
- Date of evaluation

---

## AI2 Model Priority

### Why Prioritize AI2?

| Reason | Explanation |
|--------|-------------|
| **Open Science Alignment** | AI2 publishes training data, code, and evaluation methodology |
| **Licensing Clarity** | Apache 2.0 or OLMo License (maximally permissive) |
| **Transparency** | OLMo models have fully documented training pipelines |
| **Community Support** | Active Hugging Face community, maintained repos |
| **Mission Alignment** | AI2's focus on education and research mirrors Kwanzaa's values |
| **Adapter-Friendly** | AI2 models have strong fine-tuning examples |

### AI2 Candidate Models (as of Jan 2026)

| Model | Size | Context | License | Priority |
|-------|------|---------|---------|----------|
| **OLMo-7B** | 7B | 4K → 128K (RoPE) | Apache 2.0 | ⭐ HIGH |
| **OLMo-7B-Instruct** | 7B | 4K → 128K | Apache 2.0 | ⭐⭐ HIGHEST |
| **OLMo-1.7-7B-hf** | 7B | 4K | Apache 2.0 | ⭐ HIGH |
| **Tülu 2** | 7B/13B/70B | 4K | Apache 2.0 | ⭐ MEDIUM |
| **Tülu 2+** | 7B/13B/70B | 8K | Apache 2.0 | ⭐⭐ HIGH |

**Recommended Starting Point:**
**OLMo-7B-Instruct** (instruction-tuned, extended context, Apache 2.0)

**Evaluation Questions:**
- Does OLMo-7B-Instruct achieve ≥85% citation accuracy with RAG?
- Does it refuse confidently when sources are unavailable?
- Can it maintain JSON output compliance across conversations?

If OLMo-7B does not meet thresholds → Evaluate Tülu 2+ or OLMo-13B variants.

---

## Alternative Models

If AI2 models do not meet all criteria, evaluate these alternatives:

### Tier 1 Alternatives (Open + Permissive)

| Model | Size | Context | License | Notes |
|-------|------|---------|---------|-------|
| **Llama 3.1** | 8B/70B | 128K | Apache 2.0 | Strong instruction-following, long context |
| **Llama 3.3** | 70B | 128K | Apache 2.0 | Latest Meta release (Dec 2024) |
| **Mistral 7B v0.3** | 7B | 32K | Apache 2.0 | Fast inference, strong function calling |
| **DeepSeek-V2** | 16B/236B | 128K | MIT | Strong reasoning, JSON compliance |
| **Qwen 2.5** | 7B/14B/72B | 32K-128K | Apache 2.0 | Multilingual, strong coding |

### Tier 2 Alternatives (Conditional Licensing)

| Model | Size | Context | License | Concern |
|-------|------|---------|---------|---------|
| **Phi-3** | 3.8B/14B | 128K | MIT | Small size, strong quality, but limited multilingual |
| **Gemma 2** | 9B/27B | 8K | Gemma License | Restrictive commercial terms |

### Not Recommended

| Model | Reason |
|-------|--------|
| **GPT-4, Claude, Gemini (APIs)** | Closed weights, API costs unsustainable, no fine-tuning |
| **Research-only models** | Licensing blocks community contributions |
| **Models without documented training** | Provenance concerns |

---

## Decision Matrix

### Scoring Rubric (Weighted)

| Criterion | Weight | Scoring |
|-----------|--------|---------|
| **Citation Adherence** | 25% | 0-100 (% correct citations in eval set) |
| **Uncertainty Handling** | 20% | 0-100 (% appropriate refusals) |
| **Licensing Compatibility** | 15% | Binary: 100 (Apache/MIT/CC-BY) or 0 (restrictive) |
| **Instruction Following** | 15% | 0-100 (% multi-step instruction adherence) |
| **Context Length** | 10% | 32K+ = 100, 16K = 75, 8K = 50, <8K = 0 |
| **JSON Compliance** | 10% | 0-100 (% valid JSON outputs) |
| **Hosting Cost** | 5% | 100 (≤$0.50/1M tok), 75 ($0.50-1.00), 50 ($1-2), 0 (>$2) |

**Total Score:** 0-100 (weighted average)

**Minimum Passing Score:** 70/100

**Acceptance Thresholds:**

| Criterion | Minimum | Target |
|-----------|---------|--------|
| Citation Adherence | 85% | 95% |
| Uncertainty Handling | 80% | 90% |
| Licensing | Apache/MIT/CC-BY | Apache 2.0 |
| Instruction Following | 85% | 95% |
| Context Length | 8K tokens | 32K tokens |
| JSON Compliance | 95% | 100% |
| Hosting Cost | <$2.00/1M tok | <$1.00/1M tok |

---

## Example Evaluation Results (Template)

```markdown
## OLMo-7B-Instruct Evaluation
**Date:** 2026-01-16
**Version:** OLMo-7B-Instruct-0724-hf
**Hardware:** A100 40GB, 4-bit AWQ quantization
**Inference:** vLLM 0.3.1

### Results

| Criterion | Score | Notes |
|-----------|-------|-------|
| Citation Adherence | 88/100 | Strong format compliance, 2/20 hallucinated sources |
| Uncertainty Handling | 93/100 | Excellent refusal rate, clear "I don't know" statements |
| Licensing | 100/100 | Apache 2.0 ✅ |
| Instruction Following | 91/100 | Persona drift in 2/25 tests |
| Context Length | 100/100 | 128K context via RoPE scaling |
| JSON Compliance | 97/100 | 3/100 responses had escaping issues |
| Hosting Cost | 100/100 | $0.35/1M tokens on A100 |

**Total Score:** 92.3/100 ✅ PASS

**Recommendation:** Select OLMo-7B-Instruct as base model. Address citation hallucination via adapter fine-tuning (add 50 examples emphasizing "use only provided sources").
```

---

## Implementation Recommendations

### Phase 1: Baseline Selection (Week 1)

1. **Evaluate OLMo-7B-Instruct** against all 7 criteria
2. If score ≥70: proceed with OLMo
3. If score <70: evaluate Llama 3.1 8B and Mistral 7B v0.3

### Phase 2: Adapter Development (Week 2)

1. Create 120-example training set emphasizing:
   - Citation formatting
   - Refusal behavior
   - JSON schema adherence
2. Fine-tune LoRA adapter (rank=16, alpha=32)
3. Re-evaluate adapter-enhanced model

### Phase 3: Continuous Improvement (Ongoing)

1. Monitor production performance:
   - Citation hallucination rate
   - User satisfaction with "I don't know" responses
   - JSON parse errors
2. Iterate on adapter training data based on failure modes

---

## References

- **Kwanzaa Project README:** `/Users/aideveloper/kwanzaa/README.md`
- **Answer JSON Contract:** `/Users/aideveloper/kwanzaa/docs/answer_json_contract.md`
- **Backlog (EPIC 1):** `/Users/aideveloper/kwanzaa/docs/planning/backlog.md`
- **AI2 OLMo:** https://allenai.org/olmo
- **Llama Models:** https://ai.meta.com/llama/
- **HELM Benchmarks:** https://crfm.stanford.edu/helm/
- **lm-evaluation-harness:** https://github.com/EleutherAI/lm-evaluation-harness

---

**Maintained by:** AINative Studio
**Project:** Kwanzaa - First Fruits for AI
**License:** Apache 2.0
**Issue:** #3 - Define Base Model Selection Criteria
