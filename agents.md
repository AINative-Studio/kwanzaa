# AGENTS.md — Kwanzaa Project Agent Initialization & Doc Consumption Order

This file is the **single source of truth** for how AINative agents should onboard into the Kwanzaa codebase and how the PRD, ingestion plan, and data model relate.

## 0) Mission (1 paragraph)
Build **Kwanzaa**: a cultural + RAG + fine-tune MVP on AINative that delivers:
- Cited primary-source answers (Educators/Students)
- Provenance-first search (Researchers)
- Prompted creative synthesis (Creators/Community)
- Reusable RAG patterns (Builders/Developers)

Non-negotiable: **provenance + citations + “show your work” UX**.

---

## 1) Canonical Artifacts (Read in this exact order)

### 1.1 Product Contract
1) `PRD_KWANZAA_MODEL.md`
- Defines: personas, modes, toggles, “show your work”, safety/integrity.
- If anything conflicts later, PRD wins.

### 1.2 Data Acquisition & Ingestion Contract
2) `DATA_INGESTION_PRD_KWANZAA_FIRST_FRUITS.md`
- Defines: exact namespaces, provenance schema, ingestion job specs, eval metrics.

### 1.3 Persistence Contract (ZeroDB)
3) `ZERODB_DATA_MODEL_KWANZAA.md`
- Defines: SQL table model for sessions/messages/retrieval/citations/ingestion/eval.

4) `ZERODB_TABLE_PAYLOADS_KWANZAA.json` (or `.md`)
- Defines: `/database/tables` create payloads per table.

### 1.4 Runtime Output Contract (UI Rendering)
5) `ANSWER_JSON_CONTRACT_KWANZAA.json`
- Defines: the `answer_json` payload AIKit must render (Answer / Sources / Retrieval / Unknowns).

### 1.5 API Contract (AINative/ZeroDB)
6) `ZERODB_PLATFORM_DEVELOPER_GUIDE.md` (or link)
- Defines: endpoints, auth, embedding defaults, pitfalls:
  - embeddings default: `BAAI/bge-small-en-v1.5` (384 dims)
  - vector endpoints require `/database/` prefix
  - row insert uses `row_data`

---

## 2) How The Docs Relate (Dependency Graph)

### Product → Ingestion → Storage → UI
- **PRD** defines persona modes + integrity requirements.
- **Ingestion PRD** defines what exists in corpus (namespaces + provenance), and what “citations” mean.
- **ZeroDB Data Model** defines how chat/retrieval/citations/ingestion runs are persisted and audited.
- **Answer JSON contract** defines how the assistant response is rendered and validated.

If your implementation changes any one of these, you must update the downstream contracts.

---

## 3) Invariants (Must Hold Everywhere)

### 3.1 Citations / Provenance (Imani)
If `require_citations=true`:
- assistant must include ≥1 entry in `sources[]`
- OR explicitly refuse with `unknowns.unsupported_claims` + `integrity.citations_provided=false`

### 3.2 Show Your Work UX
Every assistant response must persist:
- `kw_retrieval_runs`
- `kw_retrieval_results` (ranked + scored)
- `kw_citations_used` (subset actually cited)

### 3.3 Namespace Consistency
- Retrieval must query only namespaces allowed by persona preset + toggles.
- “Primary sources only” must filter namespaces to approved “primary” sets.

### 3.4 Embeddings Consistency
- Store + search must use the **same embedding model** in a namespace.
- Default is 384-dim (`BAAI/bge-small-en-v1.5`) unless explicitly changed.

---

## 4) Agent Startup Checklist (Do This First)

Every agent must:
1) Read the docs in the order above.
2) Produce a 1-page “understanding summary”:
   - persona modes
   - namespaces
   - provenance requirements
   - tables it will touch
   - endpoints it will call
3) Identify all code locations where:
   - ingestion happens
   - embeddings are generated/stored
   - search happens
   - chat responses are formatted
4) Return a delta list of what exists vs what must be added.

---

## 5) Agent Roles (Recommended Internal Split)

### A) Corpus & Ingestion Agent
- Owns: manifest, ingestion jobs, provenance schema enforcement
- Outputs: ingestion run logs, chunk metadata correctness

### B) RAG Orchestration Agent
- Owns: retrieval -> prompt assembly -> response formatting
- Must enforce: citations + unknowns logic + answer_json validation

### C) ZeroDB Persistence Agent
- Owns: creating tables, insert/query patterns, indexing, run logging
- Ensures: row_data contract, error handling, auditability

### D) AIKit UI Agent
- Owns: Chat, RAGBot, Search Explorer, Collections
- Must render: answer, sources, retrieval summary, unknowns

### E) Evaluation Agent
- Owns: eval question bank, eval runs, metrics computation
- Produces: citation coverage + retrieval hit-rate reports

---

## 6) “Stop Conditions” (When to Halt & Escalate)
Agents must stop and report if they detect:
- any response in educator/research mode without citations or explicit refusal
- any ingested chunk missing provenance fields
- mismatched embedding dimensions within a namespace
- usage of wrong endpoint prefixes (`/vectors/*` vs `/database/vectors/*`)
- row inserts not using `row_data`

---

## 7) Minimal Deliverables For Day-1 Demo
Must exist by end of Day 1:
- namespaces created + at least 50 “first fruits” docs ingested
- working semantic search explorer UI
- chat UI returns answer_json and renders:
  - Answer
  - Sources
  - Retrieval Summary
  - Unknowns (when needed)
- retrieval + citations persisted in tables

---
```

If you want, I can also give you a **repo file layout** (where each of these docs should live) and a **short “agent prompt” template** you can paste into your agent runner so each agent automatically follows this order and returns deltas.
