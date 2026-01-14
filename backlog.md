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
Perfect request — this is exactly where teams get burned if it’s hand-waved.

Below is an **explicit, no-assumptions expansion** of the backlog that adds **every Hugging Face fine-tuning step** as first-class work. This is written so **someone who has never trained a model** can execute it, and **someone experienced will see nothing missing**.

This **extends EPIC 3 and EPIC 10** from the master backlog and can be dropped straight into your tracker.

---

# 🧠 Kwanzaa Model — Hugging Face Fine-Tuning Backlog (Expanded & Explicit)

> **Scope:** Adapter-based fine-tuning (LoRA / QLoRA)
> **Budget:** $500–$5,000
> **Base Model (Default):** Allen Institute (AI2)
> **Alternatives:** LLaMA, DeepSeek (optional path)
> **Non-Goal:** Training a model from scratch

---

## EPIC 3A — Hugging Face Environment & Prerequisites

**Nguzo:** Umoja
**Why this exists:** Most failures happen before training starts.

---

### E3A-US1 — Select Fine-Tuning Strategy

* Decide:

  * LoRA vs QLoRA
  * Full precision vs quantized
* **Acceptance Criteria**

  * Decision recorded with rationale
  * Budget implications noted

---

### E3A-US2 — Create Hugging Face Account & Org

* Create HF account
* Create or select HF organization
* Generate access token with:

  * read
  * write
* **Acceptance Criteria**

  * Token stored securely (env var)
  * Org name documented

---

### E3A-US3 — Verify Model License Compatibility

* Review base model license:

  * redistribution
  * adapter publishing
* **Acceptance Criteria**

  * License allows adapter release
  * Notes committed to repo

---

### E3A-US4 — Provision Training Environment

* Choose:

  * Hugging Face AutoTrain
  * Custom notebook (HF + RunPod)
* Validate:

  * GPU type
  * VRAM availability
* **Acceptance Criteria**

  * Environment selected and documented
  * Cost estimate recorded

---

### E3A-US5 — Install Training Dependencies

* Install:

  * transformers
  * peft
  * accelerate
  * datasets
  * bitsandbytes (if QLoRA)
* **Acceptance Criteria**

  * `pip freeze` saved
  * Versions pinned

---

## EPIC 3B — Adapter Training Dataset Preparation

**Nguzo:** Nia, Imani
**Key principle:** We train **behavior**, not facts.

---

### E3B-US1 — Define Training Sample Schema

Each sample must include:

* system prompt
* user prompt
* assistant response
* optional citations block
* refusal examples
* **Acceptance Criteria**

  * JSON schema defined
  * Schema reviewed by engineering + product

---

### E3B-US2 — Create Citation-Following Examples

* Examples where:

  * RAG context exists
  * Model must cite retrieved sources
* **Acceptance Criteria**

  * ≥50 high-quality samples
  * Citations reference realistic metadata

---

### E3B-US3 — Create “Not in Corpus” Refusal Examples

* Explicit refusal patterns:

  * “No supporting sources found”
  * Ask clarifying question
* **Acceptance Criteria**

  * ≥30 refusal examples
  * Language matches PRD tone rules

---

### E3B-US4 — Create answer_json Compliance Examples

* Model output must follow:

  * answer
  * sources
  * retrieval_summary
  * unknowns
* **Acceptance Criteria**

  * ≥40 structured-output samples
  * Strict JSON validity

---

### E3B-US5 — Validate Dataset Quality

* Run:

  * JSON validation
  * schema checks
  * duplication scan
* **Acceptance Criteria**

  * 0 invalid samples
  * Dataset versioned

---

## EPIC 3C — Adapter Training Execution (Hugging Face)

**Nguzo:** Kuumba
**This is the “actual training” phase.**

---

### E3C-US1 — Configure Training Script

* Define:

  * base model ID
  * adapter type (LoRA/QLoRA)
  * target modules
* **Acceptance Criteria**

  * Config file checked into repo
  * No hard-coded secrets

---

### E3C-US2 — Set Hyperparameters

Explicitly define:

* learning rate
* batch size
* gradient accumulation
* epochs
* max sequence length
* **Acceptance Criteria**

  * Hyperparameters documented
  * Budget impact estimated

---

### E3C-US3 — Run Dry Test (Single Batch)

* Validate:

  * model loads
  * adapter attaches
  * loss computes
* **Acceptance Criteria**

  * Dry run completes without error

---

### E3C-US4 — Execute Full Training Run

* Monitor:

  * loss curve
  * GPU usage
  * cost
* **Acceptance Criteria**

  * Training completes successfully
  * Logs saved

---

### E3C-US5 — Save & Version Adapter Artifact

* Save:

  * adapter weights
  * config
* Version with:

  * base model hash
  * dataset version
* **Acceptance Criteria**

  * Artifact reproducible
  * Checksum recorded

---

## EPIC 3D — Adapter Evaluation & Safety Verification

**Nguzo:** Imani
**Why this exists:** Training ≠ correctness.

---

### E3D-US1 — Load Adapter Into Inference Pipeline

* Attach adapter to base model
* Enable inference mode
* **Acceptance Criteria**

  * Adapter loads without warnings

---

### E3D-US2 — Run Citation Coverage Evaluation

* Test educator/research prompts
* Measure:

  * citation presence
  * refusal correctness
* **Acceptance Criteria**

  * ≥90% citation coverage OR explicit refusal

---

### E3D-US3 — Run Hallucination Stress Tests

* Prompts with:

  * missing corpus data
  * ambiguous facts
* **Acceptance Criteria**

  * Model refuses instead of guessing

---

### E3D-US4 — Run Cultural Integrity Red-Team

* Prompts targeting:

  * stereotypes
  * performative tone
* **Acceptance Criteria**

  * No policy violations
  * Issues logged if failures occur

---

## EPIC 3E — Publishing & Integration

**Nguzo:** Ujamaa
**Goal:** Make this reusable and transparent.

---

### E3E-US1 — Publish Adapter to Hugging Face

* Upload adapter
* Add:

  * README
  * training notes
* **Acceptance Criteria**

  * Adapter publicly accessible
  * License clearly stated

---

### E3E-US2 — Integrate Adapter Into AINative Config

* Add adapter toggle:

  * base
  * base + adapter
* **Acceptance Criteria**

  * No code changes needed to enable

---

### E3E-US3 — Update Documentation

* Explain:

  * what adapter does
  * what it does NOT do
* **Acceptance Criteria**

  * README updated
  * No misleading claims

---

## EPIC 10A — Ongoing Model Iteration (Post-MVP Ready)

**Nguzo:** Ujima
**Optional but future-proofed**

---

### E10A-US1 — Adapter Retraining Playbook

* When to retrain
* What signals trigger retrain
* **Acceptance Criteria**

  * Playbook written

---

### E10A-US2 — Dataset Expansion Workflow

* How new examples get added
* Review + validation steps
* **Acceptance Criteria**

  * Contribution guide updated

---

## 🔑 Critical Reality Check (Read This)

If you **skip any of the following**, you will likely fail:

* License verification
* Refusal training
* Structured output examples
* Dry run before full training
* Adapter evaluation *before* demo

This backlog prevents that.

---

