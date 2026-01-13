```markdown
# Technical Ingestion PRD: Kwanzaa “First Fruits” Corpus
**Project:** Kwanzaa Model (AINative)  
**Sprint:** 15 days (Black History Month activation)  
**Goal:** Ship a **small, high-signal, provenance-rich** public corpus with **citation-first RAG** and **provenance-first search**.

---

## 0) Outcomes

By the end of the sprint, we will have:

1. A **curated “First Fruits” corpus** ingested into ZeroDB with strict provenance metadata
2. A set of **persona-aligned namespaces** (exact list below)
3. Automated ingestion jobs that run **from a single manifest**
4. Query templates and demo scripts per persona
5. A minimal evaluation harness proving:
   - **Citation coverage**
   - **Retrieval hit rate**

---

## 1) MVP Constraints

### Must-Haves
- Provenance fields present in **100%** of ingested chunks
- Educator + Researcher modes:
  - **≥90%** of answers include citations **OR** explicitly state “not in corpus”
- At least **10 demo-ready questions per persona** that work reliably

### Nice-to-Haves
- Daily incremental updates
- Basic deduplication across sources
- “Corpus boundary disclosure” banner (what’s in/out)

### Non-Goals (MVP)
- Not building a generalized internet crawler
- Not ingesting social media streams at scale
- Not building partner pipelines (those come after relationships)

---

## 2) Exact ZeroDB Namespaces

These are the canonical namespaces for MVP. No ad-hoc namespaces.

| Namespace | Persona | Purpose | Citation Requirement |
|---|---|---|---|
| `kwanzaa_primary_sources` | Educators/Students | Primary texts and archival records | **Required** |
| `kwanzaa_black_press` | Researchers/Educators | Newspaper & periodical coverage for context/timelines | Preferred / Required by preset |
| `kwanzaa_speeches_letters` | Creators/Educators | Speeches, letters, essays, proclamations | Preferred / Required by preset |
| `kwanzaa_black_stem` | Researchers/Educators | STEM contributions, patents, biographies, institutional records | Preferred / Required by preset |
| `kwanzaa_teaching_kits` | Creators/Educators | Curriculum-ready chunks, lesson plans, study guides | Optional |
| `kwanzaa_dev_patterns` | Builders/Developers | RAG recipes, prompt patterns, schema docs, “how to build on Kwanzaa” | Optional |
| `kwanzaa_manifests` | Internal | Source manifests, dataset cards, run logs, diffs | N/A |

**Rule:** Every ingested chunk must belong to **exactly one** of the above namespaces.

---

## 3) ZeroDB-Ready Metadata Schema (Canonical)

### 3.1 Document Schema (ingested before chunking)
Store the “document record” first (metadata-first import), then expand full text for P0 sources.

**Required fields (documents):**
- `doc_id` (string, stable)
- `title` (string)
- `source_org` (string)
- `collection` (string)
- `canonical_url` (string)
- `license` (string)
- `year` (int or null if unknown)
- `content_type` (enum; see below)
- `authors` (string[] or empty)
- `retrieved_at` (ISO timestamp)
- `access_method` (enum: `api` | `bulk` | `allowed_scrape`)
- `priority` (enum: `P0` | `P1` | `P2`)
- `tags` (string[])

**Optional fields (documents):**
- `subtitle` (string)
- `publisher` (string)
- `place` (string)
- `language` (string; default `en`)
- `abstract` (string)
- `rights_url` (string)
- `source_query` (string; what query produced this record)
- `source_id` (string; external system identifier)
- `checksum` (string; for change detection)

### 3.2 Chunk Schema (used for embeddings + retrieval)
Every chunk inherits from the document and adds chunk-level controls.

**Required fields (chunks):**
- `chunk_id` (string; `${doc_id}::chunk::${chunk_index}`)
- `doc_id` (string; stable parent)
- `chunk_index` (int)
- `text` (string; the actual chunk text)
- `source_org` (string)
- `collection` (string)
- `record_id` (string; external record id or derived stable id)
- `canonical_url` (string)
- `license` (string)
- `year` (int or null)
- `content_type` (enum)
- `retrieved_at` (ISO timestamp)
- `namespace` (string; one of the canonical namespaces)
- `citation_label` (string; short citation: org + year + title)
- `provenance` (object; see below)

**Required `provenance` object:**
- `source_type` (enum: `government` | `university` | `library` | `museum` | `archive` | `press` | `nonprofit` | `publisher`)
- `access_method` (`api` | `bulk` | `allowed_scrape`)
- `source_id` (string)
- `source_url` (string; canonical)
- `retrieved_at` (ISO timestamp)
- `license` (string)
- `hash` (string; hash of chunk text)

**Content type enum (MVP):**
- `speech`
- `letter`
- `proclamation`
- `newspaper_article`
- `journal_article`
- `book_excerpt`
- `biography`
- `timeline_entry`
- `curriculum`
- `dataset_doc`
- `dev_doc`

**Rule:** If any required provenance field is missing → **do not ingest**.

---

## 4) “First Fruits Manifest” (Single Source of Truth)

### 4.1 Manifest File Format
A single manifest (stored under `kwanzaa_manifests`) defines all sources + jobs.

**Manifest entry fields (required):**
- `source_name`
- `source_type`
- `base_url`
- `access_method` (`api` | `bulk` | `allowed_scrape`)
- `license`
- `priority` (`P0` | `P1` | `P2`)
- `default_namespace` (one of canonical namespaces)
- `tags` (string[])
- `job_id` (string; stable)
- `schedule` (e.g., daily, weekly, one-shot)
- `query_templates` (array of named templates)

**Manifest entry fields (optional):**
- `rate_limits`
- `pagination_strategy`
- `fields_mapping` (source → canonical schema)
- `robots_policy_notes` (if scrape)
- `topic_seeds` (for persona queries)

### 4.2 Manifest Governance (MVP)
- Only P0 sources get full-text expansion during MVP
- P1/P2 get metadata-first import only (unless needed for demos)

---

## 5) Ingestion Pipeline (End-to-End)

### Phase 1 — Discover
- Use manifest query templates to pull candidate records
- Store record metadata immediately

### Phase 2 — Normalize
- Map source fields to canonical doc schema
- Enforce license + provenance presence
- Generate stable `doc_id`

### Phase 3 — Store (Metadata-First)
- Write docs into ZeroDB:
  - Table-like storage (optional) AND/OR
  - Document store via `embeddings/embed-and-store` with short snippets
- Emit ingestion event: counts, failures, run id

### Phase 4 — Expand (P0 Only)
- Fetch full text
- Chunk to retrieval-friendly sizes
- Embed and store chunks in target namespace

### Phase 5 — Incremental Update
- Diff by `source_id` and/or `checksum`
- Append new docs, update metadata, preserve history

---

## 6) Ingestion Job Specs (API-by-API / Source-by-Source)

> **Note:** These specs define “what” must happen per source. Implementation can use any internal approach.

### 6.1 Chronicling America (Library of Congress) — Black Press / Context
**Priority:** P0  
**Namespace:** `kwanzaa_black_press`  
**Access Method:** API  
**Records:** newspaper pages, articles, metadata

**Job:**
- Pull records by:
  - date ranges (era-based)
  - keywords/topics (persona templates below)
  - publication titles (where available)
- Store:
  - article/page metadata (title, date, publication)
  - canonical URL
  - OCR text if available (or snippet if not)
- Expand:
  - full OCR text chunks for P0 topics

**Canonical mapping:**
- `record_id` = LOC item id (or derived stable id)
- `year` = from publication date
- `content_type` = `newspaper_article`

---

### 6.2 National Archives / Founders Online / Government Text Repositories — Primary Sources
**Priority:** P0  
**Namespace:** `kwanzaa_primary_sources`  
**Access Method:** API or bulk (depending on source availability)

**Job:**
- Pull documents by:
  - era buckets (Reconstruction, Civil Rights, etc.)
  - topic seeds (voting rights, education, labor, housing)
- Store metadata first
- Expand full text for P0 subsets

**Canonical mapping:**
- `content_type` = `proclamation` / `letter` / `speech` depending on record

---

### 6.3 University Digital Collections / Institutional Repositories — Speeches, Letters, Scholarship
**Priority:** P1 (metadata-first), selectively elevate to P0 for demos  
**Namespace:** `kwanzaa_speeches_letters` or `kwanzaa_primary_sources`  
**Access Method:** API (if available) or bulk

**Job:**
- Pull:
  - collections with public access rights
  - structured metadata and stable identifiers
- Store metadata + abstracts/snippets
- Expand only demo-critical items

**Canonical mapping:**
- `content_type` = `speech`, `letter`, `journal_article`, `biography`

---

### 6.4 Smithsonian / Museums / Public Domain Archives — Cultural Context
**Priority:** P1  
**Namespace:** `kwanzaa_primary_sources` or `kwanzaa_black_stem` (as relevant)  
**Access Method:** API or bulk

**Job:**
- Pull object records, exhibit text, interpretive write-ups
- Store metadata-first
- Expand only if license permits and text is substantial

**Canonical mapping:**
- `content_type` = `timeline_entry` / `biography` / `dataset_doc`

---

### 6.5 USPTO / Patents Open Data — Black STEM
**Priority:** P0 (for STEM demos)  
**Namespace:** `kwanzaa_black_stem`  
**Access Method:** API or bulk

**Job:**
- Pull patent records and summaries
- Store:
  - patent id, inventor names, year, abstract
- Expand:
  - abstract + claims excerpts (where allowed) for retrieval

**Canonical mapping:**
- `content_type` = `dataset_doc` or `biography` (if inventor bio linked)

---

### 6.6 Curriculum Open Repositories (public licenses) — Teaching Kits
**Priority:** P0 for creator/educator demos  
**Namespace:** `kwanzaa_teaching_kits`  
**Access Method:** bulk or allowed scrape (license must be explicit)

**Job:**
- Pull lesson plans, unit outlines, worksheets
- Normalize into chunk-friendly sections:
  - objectives, activities, assessment, reading list
- Embed per section

**Canonical mapping:**
- `content_type` = `curriculum`

---

### 6.7 Kwanzaa Dev Docs Pack — Builders
**Priority:** P0  
**Namespace:** `kwanzaa_dev_patterns`  
**Access Method:** internal docs + public docs you author/publish

**Job:**
- Store:
  - RAG patterns
  - schema + namespaces
  - sample prompts
  - evaluation recipes
- This becomes the “developer quickstart corpus” for demos

**Canonical mapping:**
- `content_type` = `dev_doc`

---

## 7) ZeroDB Storage Contract (Exact Calls)

### 7.1 Embed + Store (chunks) — Default Path
**Endpoint:**
- `POST /v1/public/{project_id}/embeddings/embed-and-store`

**Payload shape (chunk-level):**
- `documents[]` where each document is:
  - `id`: `chunk_id`
  - `text`: chunk text
  - `metadata`: all canonical chunk metadata (including provenance)

**Namespace:**
- Use the target namespace from the manifest entry.

### 7.2 Search (for eval + demos)
**Endpoint:**
- `POST /v1/public/{project_id}/embeddings/search`

**Payload shape:**
- `query`: user question
- `top_k`: 5–10
- `namespace`: persona default namespaces
- optional `filter`: metadata filters

---

## 8) Persona Query Templates (Source-Specific Examples)

These templates are used in two places:
1) Ingestion discovery (to pull records)
2) Demo scripts (to validate retrieval + citations)

### 8.1 Builders / Developers (RAG patterns)
**Namespaces:** `kwanzaa_dev_patterns` (+ any for examples)

**Query templates:**
- “Show me a citation-first RAG prompt template.”
- “How should I design namespaces for cultural corpora?”
- “Give me an ingestion manifest example and explain the fields.”
- “How do I enforce ‘not in corpus’ responses?”

---

### 8.2 Educators / Students (primary-source citations)
**Namespaces:** `kwanzaa_primary_sources`, `kwanzaa_speeches_letters`

**Query templates (general):**
- “What did [historical figure] argue about [topic]? Provide primary-source citations.”
- “What primary sources support claims about [event] in [year range]?”
- “Summarize [topic] using only primary sources from the corpus.”

**Chronicling America topic pulls (discovery queries):**
- Topic seed list examples:
  - “Reconstruction”
  - “Voting rights”
  - “Education”
  - “Great Migration”
  - “Civil Rights”
  - “Housing”
  - “Labor”
- Execution pattern:
  - `topic_seed + date_range + publication filter (optional)`

---

### 8.3 Creators / Community (speeches, explainers, curricula)
**Namespaces:** `kwanzaa_speeches_letters`, `kwanzaa_teaching_kits`

**Query templates:**
- “Draft a 3-minute speech on [topic] grounded in cited sources (optional citations toggle).”
- “Create a 1-page explainer for students on [topic], with a source list.”
- “Generate a lesson plan outline for grades [X–Y] on [topic], referencing corpus sources.”

---

### 8.4 Researchers (provenance-first search)
**Namespaces:** all, with strict filters

**Query templates (search + filters):**
- “Find sources about [topic] between [year_start] and [year_end].”
- “Show me the top 20 documents about [topic], grouped by source_org.”
- “Return only content_type = newspaper_article, year = 19XX, tag includes [theme].”
- “Explain why each result matched (include score + snippet + provenance).”

---

## 9) Minimal Evaluation Plan (MVP)

### 9.1 Metrics

#### A) Citation Coverage (Educator/Research presets)
**Definition:**
- % of responses that include:
  - ≥1 citation (canonical_url + citation_label)  
  **OR**
  - explicit “not in corpus”

**Target:**
- **≥90%** compliant

**Test set:**
- 20 questions per persona (80 total)
- Educator/Research questions weighted heavier for citation checks

---

#### B) Retrieval Hit Rate
**Definition:**
- For each test query:
  - At least one of top_k retrieved chunks contains the “expected evidence”
- Evidence can be validated by:
  - matching doc_id from a curated expected list
  - keyword overlap threshold
  - metadata filters matching the intended era/type

**Target:**
- **≥70%** for MVP across all personas
- **≥80%** for Educator/Research subsets (P0 corpora)

---

#### C) Demo Reliability
**Definition:**
- For the top 10 demo questions per persona:
  - answers are stable
  - citations appear when required
  - no hallucinated sources

**Target:**
- **≥90%** pass rate on repeated runs

---

### 9.2 Eval Harness Outputs (Required)
- JSON report:
  - per-question: retrieved ids, scores, citation presence, pass/fail
- Aggregated summary:
  - citation coverage %
  - retrieval hit rate %
  - failure clusters by namespace/source

---

## 10) Quality Gates (Ship/No-Ship)

### Ship if:
- Provenance completeness: **100%**
- Citation coverage (educator/research): **≥90%**
- Demo reliability: **≥90%** for curated demo questions
- Corpus size: at least **P0 coverage** for each persona:
  - Educator: primary sources present
  - Creator: speeches/letters + teaching kits present
  - Researcher: metadata filters work
  - Builder: dev patterns corpus present

### Do not ship if:
- Any ingestion path produces chunks without canonical provenance fields
- Citation-required mode fabricates sources or citations

---

## 11) Deliverables (Engineering)

1. **`FIRST_FRUITS_MANIFEST.json`** (canonical)
2. **Namespace + schema docs** stored under `kwanzaa_dev_patterns`
3. **Ingestion run logs** stored under `kwanzaa_manifests`
4. **Corpus dataset card** (sources, licenses, coverage notes)
5. **Eval harness report** + summary
6. **Persona query packs** (demo-ready)

---

## Appendix A — Suggested “Era/Theme” Tag Set (MVP)
Use tags consistently across sources for filtering and demo stability.

**Eras (examples):**
- `reconstruction`
- `jim_crow`
- `great_migration`
- `civil_rights`
- `post_civil_rights`

**Themes (examples):**
- `voting_rights`
- `education`
- `housing`
- `labor`
- `health`
- `entrepreneurship`
- `stem`

---

## Appendix B — Citation Formatting Contract (for UI + Answers)

When citations are required:
- Provide citations as a list with:
  - `citation_label`
  - `canonical_url`
  - `year`
  - `source_org`
  - `content_type`

**If no sources are found:**
- Explicitly state: **“No supporting sources found in this corpus.”**
- Suggest narrowing the query (era/theme) without inventing evidence
```
