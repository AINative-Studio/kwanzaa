# 🧱 Kwanzaa Model — **Master Backlog (Single Source of Truth)**

**Sprint Scope:** 15 Days
**Product Type:** Cultural Model + RAG MVP
**Platform:** AINative (ZeroDB + AIKit)
**Guiding Framework:** Nguzo Saba (Umoja, Kujichagulia, Ujima, Ujamaa, Nia, Kuumba, Imani)

---

## EPIC 0 — Foundations & Repo Setup

**Nguzo:** Umoja
**PRD Sections:** System Architecture, Deliverables

### User Stories

**E0-US1 — Initialize Open GitHub Repository**

* Set repo structure (docs/, data/, adapters/, evals/, ui/)
* Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE
* Acceptance:

  * Repo is public
  * Contribution pathways documented

**E0-US2 — Define Environment & Config Conventions**

* Config-driven setup (models, adapters, namespaces)
* No hard-coded assumptions
* Acceptance:

  * One config file controls model + adapter + RAG modes

---

## EPIC 1 — Base Model Selection & Evaluation

**Nguzo:** Nia, Imani
**PRD Sections:** System Architecture, Safety + Integrity

### User Stories

**E1-US1 — Define Base Model Selection Criteria**

* Criteria include:

  * Citation adherence
  * Uncertainty handling
  * Licensing compatibility
  * Instruction following
* Acceptance:

  * Criteria documented in repo

**E1-US2 — Evaluate Allen Institute (AI2) Models (Default Path)**

* Run eval prompts for:

  * Citation-required answers
  * Refusal behavior
  * Historical QA
* Acceptance:

  * Results logged and versioned

**E1-US3 — Evaluate Optional Models (LLaMA, DeepSeek)**

* Same eval harness
* Compare deltas
* Acceptance:

  * No lock-in to one base model

---

## EPIC 2 — Base Model Serving & Configuration

**Nguzo:** Umoja
**PRD Sections:** Core MVP Features, System Architecture

### User Stories

**E2-US1 — Implement Model Abstraction Layer**

* Base model defined via config
* Supports AI2, LLaMA, DeepSeek
* Acceptance:

  * Swapping base models requires no code changes

**E2-US2 — Define Model Modes**

* `base`
* `base + kwanzaa_adapter`
* `base + adapter + RAG` (default)
* Acceptance:

  * Mode stored per session

**E2-US3 — Persona-Based Generation Defaults**

* Educator/Researcher = deterministic
* Creator = expressive but grounded
* Acceptance:

  * Defaults documented + enforced

---

## EPIC 3 — Kwanzaa Adapter Training (LoRA / QLoRA)

**Nguzo:** Nia, Kuumba, Imani
**PRD Sections:** System Architecture, Safety

### User Stories

**E3-US1 — Define Adapter Objectives**

* Adapter teaches:

  * Citation-following
  * Retrieval usage
  * Refusal correctness
  * answer_json compliance
* Acceptance:

  * Objectives documented

**E3-US2 — Prepare Adapter Training Dataset**

* High-signal, small dataset
* Includes:

  * “Answer with citation”
  * “Not in corpus” refusals
  * Retrieval-grounded answers
* Acceptance:

  * Dataset fits $500–$5k budget

**E3-US3 — Train Adapter on Default Base Model**

* Reproducible run
* Save adapter artifact + checksum
* Acceptance:

  * No base weights modified

**E3-US4 — Adapter Compatibility Testing**

* Test adapter with alternative bases
* Acceptance:

  * Failures documented, not hidden

---

## EPIC 4 — Data Ingestion Framework (First Fruits Corpus)

**Nguzo:** Umoja, Ujima, Imani
**PRD Sections:** Data Ingestion Plan

### User Stories

**E4-US1 — Define “First Fruits Manifest” Schema**

* source_name
* source_type
* access_method
* license
* canonical_url
* priority
* tags
* Acceptance:

  * Manifest is single source of truth

**E4-US2 — Metadata-First Ingestion Pipeline**

* Ingest metadata + snippets first
* Store immediately in ZeroDB
* Acceptance:

  * Search + provenance UI works before full text

**E4-US3 — Selective Full-Text Expansion**

* Only P0 sources expanded
* Chunk + embed + store
* Acceptance:

  * Expansion is idempotent

**E4-US4 — Daily Incremental Ingestion Jobs**

* Re-run manifest daily
* Append-only behavior
* Acceptance:

  * Ingestion logs persisted

---

## EPIC 5 — ZeroDB Schema & Namespaces

**Nguzo:** Umoja, Imani
**PRD Sections:** Namespace Design, Provenance

### User Stories

**E5-US1 — Create ZeroDB Tables**

* documents
* chunks
* sources
* collections
* ingestion_logs
* evaluations
* Acceptance:

  * All tables created via `/database/tables`

**E5-US2 — Implement Required Provenance Schema**

* Enforce:

  * canonical_url
  * license
  * year
  * source_org
* Acceptance:

  * No provenance → no ingest

**E5-US3 — Namespace Enforcement**

* Persona-aligned namespaces:

  * primary_sources
  * speeches_letters
  * black_press
  * black_stem
  * teaching_kits
  * dev_patterns
* Acceptance:

  * Filters respected in queries

---

## EPIC 6 — RAG Orchestration & Query Logic

**Nguzo:** Nia, Imani
**PRD Sections:** Core MVP Features

### User Stories

**E6-US1 — Retrieval Pipeline**

* Query → retrieve → rank → inject context
* Acceptance:

  * Retrieval summary captured

**E6-US2 — Persona-Specific Query Templates**

* Builders: patterns + schemas
* Educators: primary sources only
* Creators: rhetorical structures
* Researchers: metadata-first
* Acceptance:

  * Templates documented + selectable

**E6-US3 — Citation Enforcement Logic**

* If required and missing → refuse
* Acceptance:

  * No silent hallucinations

---

## EPIC 7 — AIKit UI (Chat, RAGBot, Search)

**Nguzo:** Umoja, Kuumba
**PRD Sections:** Core MVP Features

### User Stories

**E7-US1 — Kwanzaa Chat UI**

* Mode toggles
* Persona presets
* Acceptance:

  * answer_json rendered correctly

**E7-US2 — RAGBot Upload + Preview**

* Upload → ingest → preview chunks
* Acceptance:

  * Curators can validate before publish

**E7-US3 — Semantic Search Explorer**

* Filters:

  * year
  * source
  * tags
* Acceptance:

  * Provenance visible in results

---

## EPIC 8 — answer_json Contract & Rendering

**Nguzo:** Imani
**PRD Sections:** Safety + Integrity

### User Stories

**E8-US1 — Define answer_json Contract**

* answer
* sources
* retrieval_summary
* unknowns
* Acceptance:

  * Contract versioned

**E8-US2 — Enforce Output Compliance**

* All responses conform
* Acceptance:

  * UI never renders raw text blobs

---

## EPIC 9 — Safety, Integrity & Cultural Guardrails

**Nguzo:** Imani
**PRD Sections:** Safety + Integrity

### User Stories

**E9-US1 — Refusal & Uncertainty Training**

* Clear refusals when unsupported
* Acceptance:

  * No evasive language

**E9-US2 — Anti-Stereotype Guardrails**

* Prevent performative dialect
* Acceptance:

  * Red-team prompts tracked

---

## EPIC 10 — Evaluation & Metrics

**Nguzo:** Ujima, Imani
**PRD Sections:** Success Metrics

### User Stories

**E10-US1 — Citation Coverage Eval**

* Educator/Research modes
* Acceptance:

  * ≥90% coverage or explicit refusal

**E10-US2 — Retrieval Hit-Rate Eval**

* Top-k relevance tracking
* Acceptance:

  * Scores logged per version

**E10-US3 — Persona Demo Questions**

* 10+ reliable questions per persona
* Acceptance:

  * Demo-ready

---

## EPIC 11 — Documentation & Community Enablement

**Nguzo:** Ujamaa
**PRD Sections:** Deliverables

### User Stories

**E11-US1 — README & Architecture Docs**

* Clear onboarding
* Acceptance:

  * New contributor can run demo in <30 min

**E11-US2 — Dataset Manifest Publication**

* Sources + licenses
* Acceptance:

  * Fully transparent corpus

**E11-US3 — Contribution Workflow**

* Data contributions
* Issues + backlog
* Acceptance:

  * PR template + review guidelines

---

## EPIC 12 — Launch & Demo Readiness

**Nguzo:** Nia, Umoja
**PRD Sections:** 15-Day Execution Plan

### User Stories

**E12-US1 — Demo Script & Scenarios**

* Persona-based demos
* Acceptance:

  * Repeatable live demo

**E12-US2 — Publish Artifacts**

* Adapter
* Dataset manifest
* Eval summary
* Acceptance:

  * Public links available

---
