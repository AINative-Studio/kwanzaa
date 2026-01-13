# Data Ingestion Plan: Kwanzaa “First Fruits” Corpus

**Goal:** Ingest a small, high-signal, provenance-rich public corpus quickly to demonstrate credibility, trust, and cultural integrity.

This plan is optimized for **speed, automation, and auditability** while remaining aligned with the **Nguzo Saba** and the 15-day MVP constraint.

---

## Guiding Principles (Nguzo Saba → System Rules)

### Umoja (Unity)
- One **unified schema**
- Consistent **namespace conventions**
- Single ingestion manifest as the source of truth

### Kujichagulia (Self-Determination)
- Explicit disclosures of:
  - What is included
  - What is excluded
  - What is incomplete
- Users can see corpus boundaries clearly

### Ujima (Collective Work & Responsibility)
- Repeatable ingestion workflows
- Logged runs with timestamps and counts
- Deterministic behavior (same input → same output)

### Nia (Purpose)
- Educational and research value prioritized over volume
- Preference for primary or historically grounded sources

### Imani (Faith)
- Provenance is mandatory
- Licenses are recorded and surfaced
- No anonymous or unverifiable content

---

## A) Data Scope (MVP)

### Target Volume
- **Documents:** 500–5,000
- **Chunks:** 5,000–50,000

This scope is:
- Small enough to ingest and validate quickly
- Large enough to demonstrate:
  - citation reliability
  - cross-source retrieval
  - semantic depth

---

## B) Ingestion Workflow (MVP)

### Step 1 — Source List (“First Fruits Manifest”)

Create a **single manifest file** that defines *all* ingestable sources.

**Manifest Fields**
- `source_name`
- `source_type` (archive, press, academic, curriculum, code, etc.)
- `access_method` (API / bulk download / allowed scrape)
- `license`
- `canonical_url`
- `priority` (P0 / P1 / P2)
- `tags` (era, theme, geography, persona)

> This manifest is the **single source of truth** for ingestion decisions.

---

### Step 2 — Metadata-First Import

- Ingest **metadata + short text/snippets first**
- Store immediately as ZeroDB documents
- Enables:
  - search
  - filtering
  - provenance UI
  - early demo value

**Outcome**
- The system becomes usable *before* full text ingestion completes.

---

### Step 3 — Full-Text Expansion (Selective)

- Only **P0 sources** are expanded to full text during MVP
- Process:
  - fetch full text
  - normalize
  - chunk
  - embed
  - store in ZeroDB

This keeps the corpus **high-signal and manageable**.

---

### Step 4 — Daily Incremental Updates

- Re-run ingestion from the manifest daily
- Behavior:
  - append new records
  - update metadata if changed
  - do not silently overwrite historical records

This supports:
- reproducibility
- auditability
- future community contributions

---

## C) Namespace Design (ZeroDB)

Namespaces are **persona-aligned** and intentional.

| Namespace | Primary Persona | Purpose |
|---------|-----------------|---------|
| `kwanzaa_primary_sources` | Educators / Students | Foundational texts with attribution |
| `kwanzaa_black_press` | Researchers / Educators | Context, timelines, reportage |
| `kwanzaa_speeches_letters` | Creators / Educators | Rhetorical and historical documents |
| `kwanzaa_black_stem` | Researchers / Education | STEM history and contributions |
| `kwanzaa_teaching_kits` | Creators / Educators | Curriculum-ready chunks |
| `kwanzaa_dev_patterns` | Builders / Developers | RAG recipes, prompts, schemas |

Namespaces drive:
- retrieval filtering
- persona presets
- citation enforcement rules

---

## D) Required Metadata Schema (Provenance)

**Every chunk must include the following fields:**

- `source_org`
- `collection`
- `record_id`
- `canonical_url`
- `license`
- `year`
- `content_type`
- `retrieved_at`
- `chunk_index`

> **Rule:**  
> If provenance is missing or incomplete → **do not ingest**.

This is non-negotiable and enforced at ingestion time.

---

## E) Persona-Based Ingestion Priorities

### Builders / Developers
- **Namespace:** `kwanzaa_dev_patterns`
- **Content Focus:**
  - RAG recipes
  - example prompts
  - schema docs
- **Goal:** Demonstrate reusable cultural RAG patterns

---

### Educators / Students
- **Namespaces:**  
  - `kwanzaa_primary_sources`  
  - `kwanzaa_speeches_letters`
- **Content Focus:**
  - primary texts
  - dates
  - authorship
- **Goal:** Citation-first, classroom-safe answers

---

### Creators / Community
- **Namespaces:**  
  - `kwanzaa_speeches_letters`  
  - `kwanzaa_teaching_kits`
- **Content Focus:**
  - rhetorical structure
  - explainable historical context
- **Goal:** Creative synthesis without hallucination

---

### Researchers
- **Namespaces:** All
- **Requirements:**
  - strict metadata completeness
  - full filter support
- **Content Focus:**
  - metadata-first discovery
  - provenance verification
- **Goal:** Trustworthy semantic research

---

## F) Quality Gates (Fast, Automated)

### Minimum Acceptance Criteria for Launch

- **Citation Integrity**
  - ≥90% of responses in educator/research modes:
    - include citations **or**
    - explicitly state “not in corpus”

- **Provenance Completeness**
  - 100% of chunks include all required metadata fields

- **Demo Reliability**
  - At least **10 demo-ready questions per persona**
  - E
