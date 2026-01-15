## EPIC 0 — Project Bootstrap + Repo Readiness (Umoja)

**Goal:** Open repo is usable Day 1; contributors can participate safely.

* **US-0.1** Create repo structure (`/docs`, `/data`, `/app`, `/scripts`, `/infra`, `/examples`)
* **US-0.2** Add `README.md` scaffold (overview, personas, quickstart placeholder)
* **US-0.3** Add `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`
* **US-0.4** Add GitHub issue templates (bug, data source request, ingestion bug, model training bug)
* **US-0.5** Add PR template with provenance checklist (canonical_url, license, year required)
* **US-0.6** Add “Security + Responsible Use” policy page

**Acceptance Criteria**

* New contributor can clone repo and understand purpose + how to contribute sources/issues.

---

## EPIC 1 — Kwanzaa Branding + Product Contracts (Nguzo Saba as requirements)

**Goal:** Brand and product behaviors are encoded as rules and contracts.

* **US-1.1** Define Kwanzaa brand constants (name origin, Nguzo Saba mapping, tagline)
* **US-1.2** Define persona presets (builder/educator/creator/researcher) as config
* **US-1.3** Define mode toggles contract (`citations_required`, `primary_sources_only`, `creative_mode`)
* **US-1.4** Define system prompt policy (no invented quotes, no stereotyping, refusal rules)
* **US-1.5** Define `answer_json` response contract for AIKit rendering

**Acceptance Criteria**

* Every interaction uses the same contract; persona presets are reproducible.

---

## EPIC 2 — ZeroDB Data Model for Kwanzaa RAG (Provenance-first)

**Goal:** A clean data model aligned to ingestion + RAG + eval.

### Tables (minimum set)

* **US-2.1** Create `kw_sources` table (source manifest registry)
* **US-2.2** Create `kw_documents` table (doc-level records + canonical URL + license)
* **US-2.3** Create `kw_chunks` table (chunk metadata + provenance fields)
* **US-2.4** Create `kw_ingestion_runs` table (job runs, counts, errors, timestamps)
* **US-2.5** Create `kw_citations` table (answer → sources used; for analytics + audits)
* **US-2.6** Create `kw_queries` table (persona queries + presets + outcomes)
* **US-2.7** Create `kw_evals` table (golden questions, expected behavior, results)
* **US-2.8** Create `kw_collections` table (curated bundles metadata)
* **US-2.9** Create `kw_collection_items` table (collection ↔ document mapping)

**Acceptance Criteria**

* All records have license + canonical URL captured at creation time.
* Schema supports provenance filters (year, org, collection, type).

---

## EPIC 3 — First Fruits Manifest + Corpus Acquisition (Fast + Public + Licensed)

**Goal:** Build a small, credible corpus quickly without partnerships.

* **US-3.1** Define `FirstFruitsManifest` format (fields: name, type, access, license, canonical, priority, tags)
* **US-3.2** Create initial P0 manifest (10–25 sources) focused on primary sources
* **US-3.3** Add manifest validation rules (license required, canonical URL required)
* **US-3.4** Implement “metadata-first import” pipeline (store doc records immediately)
* **US-3.5** Implement “selective full-text expansion” for P0 sources only
* **US-3.6** Add daily incremental ingestion mode (append-only + change detection)
* **US-3.7** Add de-dupe rules (canonical_url + checksum)
* **US-3.8** Add canonical URL normalization rules
* **US-3.9** Create ingestion logging spec (counts, errors, run status)

**Acceptance Criteria**

* Manifest is the single source of truth; ingestion is repeatable and logged.

---

## EPIC 4 — Namespace Strategy + Embeddings/Vector Layer (ZeroDB)

**Goal:** Corpus is queryable by persona with consistent namespaces.

* **US-4.1** Finalize exact namespaces:

  * `kwanzaa_primary_sources`
  * `kwanzaa_black_press`
  * `kwanzaa_speeches_letters`
  * `kwanzaa_black_stem`
  * `kwanzaa_teaching_kits`
  * `kwanzaa_dev_patterns`
* **US-4.2** Implement namespace routing rules by persona preset
* **US-4.3** Implement chunking spec (size, overlap, metadata per chunk)
* **US-4.4** Implement embed-and-store flows per namespace
* **US-4.5** Implement semantic search queries with filters (year, org, type, tags)
* **US-4.6** Add similarity thresholds by persona preset (educator/research stricter)
* **US-4.7** Create “retrieval summary” builder (top results, scores, chunk ids)

**Acceptance Criteria**

* Search returns provenance-rich results; no namespace mixing without explicit selection.

---

## EPIC 5 — Ingestion Job Specs (API-by-API / Source-by-Source)

**Goal:** Each manifest entry has a deterministic ingestion job spec.

* **US-5.1** Write ingestion spec template per source (inputs, outputs, license handling, errors)
* **US-5.2** Implement ingestion job runner interface (run P0 only, run all, run daily)
* **US-5.3** Implement rate-limit + backoff behaviors
* **US-5.4** Implement content extraction normalization (text clean-up, metadata mapping)
* **US-5.5** Implement chunk embedding pipeline (post-extraction)
* **US-5.6** Store all ingestion run results in `kw_ingestion_runs`
* **US-5.7** Store document/chunk lineage (doc_id → chunk_ids)
* **US-5.8** Add ingestion error triage reports (top failing sources)

**Acceptance Criteria**

* For any source, you can point to: manifest entry → ingestion run → doc ids → chunk ids.

---

## EPIC 6 — Kwanzaa Chat + RAG Orchestration (AIKit Contract)

**Goal:** The chat experience enforces citations/refusals and always returns `answer_json`.

* **US-6.1** Implement persona preset selection (builder/educator/creator/researcher)
* **US-6.2** Implement mode toggles (citations_required, primary_only, creative_mode)
* **US-6.3** Implement RAG retrieval pipeline (search → context pack → generate)
* **US-6.4** Implement `answer_json` renderer in UI (Answer/Sources/Retrieval/Unknowns)
* **US-6.5** Implement citation enforcement:

  * if required and no sources → refuse
* **US-6.6** Implement “show your work” UI panel (retrieved chunks + scores + metadata)
* **US-6.7** Implement “what I don’t know” behavior when retrieval confidence is weak
* **US-6.8** Store per-chat citation usage into `kw_citations`

**Acceptance Criteria**

* Educator/Research modes: ≥90% responses include citations OR explicit “not in corpus”.
* Output is valid JSON 100% of the time.

---

## EPIC 7 — RAGBot Ingest UI + Curator Flow (AIKit)

**Goal:** Demo “upload → ingest → search → answer” and support internal curation.

* **US-7.1** Build RAGBot upload flow (doc upload with metadata)
* **US-7.2** Add namespace selection in ingest UI
* **US-7.3** Preview chunking output before storing (sample chunks + metadata)
* **US-7.4** “Add to corpus” curator action (internal)
* **US-7.5** Show ingestion status (queued/running/success/fail)
* **US-7.6** Add basic contributor safety checks (license required, canonical URL required)

**Acceptance Criteria**

* A curator can add a doc and immediately query it with citations.

---

## EPIC 8 — Semantic Search Explorer + Filters (ZeroDB)

**Goal:** Provenance-first search for researchers.

* **US-8.1** Build Search Explorer UI with filters:

  * year range
  * source_org
  * content_type
  * tags
  * namespace
* **US-8.2** Display results with:

  * snippet
  * score
  * canonical URL
  * license
  * year
* **US-8.3** Add “open source” linkouts per result
* **US-8.4** Add “save query” (store in `kw_queries`)
* **US-8.5** Add “export results” (JSON)

**Acceptance Criteria**

* Researcher can locate sources without chatting; provenance is always visible.

---

## EPIC 9 — Collections (Curated “First Fruits” Bundles)

**Goal:** Guided experience with small, high-signal sets.

* **US-9.1** Define Collections schema + UI
* **US-9.2** Create initial Collections:

  * Reconstruction
  * Civil Rights
  * Black Press
  * Black STEM
  * Speeches + Letters
* **US-9.3** Map documents into collections (collection_items)
* **US-9.4** Add “search within collection”
* **US-9.5** Add “collection overview” page (what’s included + why)

**Acceptance Criteria**

* Demo can run from collections alone and still look credible.

---

## EPIC 10 — Model Selection + Serving Strategy (AI2-first, others optional)

**Goal:** Choose base model and integrate adapter + RAG.

* **US-10.1** Define base model selection criteria:

  * licensing
  * context length
  * instruction-following
  * tool/json compliance
  * hosting cost
* **US-10.2** Evaluate Allen Institute candidates (AI2-first) against criteria
* **US-10.3** Define optional alternatives (Llama/DeepSeek as fallback options)
* **US-10.4** Define serving contract:

  * base only
  * base + adapter
  * base + adapter + RAG
* **US-10.5** Implement model mode switching in app config

**Acceptance Criteria**

* Can toggle between base-only and adapter-enhanced without breaking answer_json.

---

## EPIC 11 — Fine-Tuning Execution (First-Time Friendly)

**Goal:** Train and publish the Kwanzaa adapter successfully.

### Dataset Preparation (must-have)

* **US-11.1** Write training data schema doc (`SCHEMA.md`)
* **US-11.2** Create training set (≥120 examples):

  * citation-following
  * refusal
  * strict JSON
* **US-11.3** Create eval set (25–40 examples)
* **US-11.4** Build dataset validator (JSON parse + required keys)
* **US-11.5** Add dataset versioning (v0.1, manifest hash, changelog)

### Training Run (HF AutoTrain recommended)

* **US-11.6** Create HF training project and upload train/eval
* **US-11.7** Configure QLoRA/LoRA training parameters (safe defaults)
* **US-11.8** Run pilot training (small run)
* **US-11.9** Run production training (target run)
* **US-11.10** Publish adapter artifact + training config + dataset manifest

### Evaluation + Iteration

* **US-11.11** Evaluate JSON validity rate
* **US-11.12** Evaluate citation coverage rate (educator/research presets)
* **US-11.13** Evaluate refusal correctness (no corpus ⇒ refuse)
* **US-11.14** Decide if Run #2 needed; if yes, run focused training

**Acceptance Criteria**

* Adapter improves citation + refusal + JSON compliance measurably.
* Published artifact is reproducible (config + data versions recorded).

---

## EPIC 12 — Minimal Eval Harness (Citations + Retrieval Hit Rate)

**Goal:** You can prove the system works.

* **US-12.1** Define golden questions (10 per persona)
* **US-12.2** Implement “citation coverage” metric
* **US-12.3** Implement “retrieval hit rate” metric (top-k contains relevant chunk)
* **US-12.4** Implement regression runner (re-run after corpus or model changes)
* **US-12.5** Store eval runs in `kw_evals` table with timestamp + versions

**Acceptance Criteria**

* One command/run produces a metrics summary suitable for launch.

---

## EPIC 13 — Safety + Integrity (Imani) Guardrails

**Goal:** Prevent “culture cosplay,” stereotypes, and fake citations.

* **US-13.1** Implement refusal policy for unsupported specifics
* **US-13.2** Implement “no invented quotes/attributions” checks (prompt + QA)
* **US-13.3** Implement “performative dialect” avoidance policy
* **US-13.4** Add UI disclosures: “In-corpus vs out-of-corpus”
* **US-13.5** Add provenance completeness gate: no ingest without license + canonical URL

**Acceptance Criteria**

* If citations required and none retrieved: explicit refusal.
* Provenance completeness is enforced at ingestion time.

---

## EPIC 14 — Analytics + Growth Telemetry (Ujamaa)

**Goal:** Prove the campaign drives product usage.

* **US-14.1** Track funnel events:

  * signup → project created → vectors stored → chats run
* **US-14.2** Track corpus growth per day (docs/chunks)
* **US-14.3** Track persona usage distribution
* **US-14.4** Track citation coverage trend over time
* **US-14.5** Build minimal dashboard view (internal)

**Acceptance Criteria**

* You can publish a campaign post with real numbers.

---

## EPIC 15 — Open-Source Contribution Loop (Ujima)

**Goal:** Make it easy for others to contribute data + improvements.

* **US-15.1** Write “How to contribute sources” guide (manifest PR flow)
* **US-15.2** Add “Source request” issue template + labels
* **US-15.3** Add “Good first issue” list for contributors
* **US-15.4** Add review checklist for maintainers (license + canonical + metadata)
* **US-15.5** Add contributor recognition section (hall of fame)

**Acceptance Criteria**

* External contributors can add sources without breaking provenance guarantees.

---

## EPIC 16 — Launch Package + Demo Scripts (15-day sprint deliverable)

**Goal:** Polished demo that sells AINative power.

* **US-16.1** Write demo scripts (4 persona walkthroughs)
* **US-16.2** Create “10 demo-ready questions” per persona
* **US-16.3** Add “Known limitations” page (transparent boundaries)
* **US-16.4** Publish dataset manifest + adapter artifact links
* **US-16.5** Add “Build log” daily updates template + final sprint recap

**Acceptance Criteria**

* Anyone can run the demo and reproduce the key flows.

---

# Mandatory “First-Time Training” Subtasks (these trip people up)

Add these as child tasks under EPIC 11:

* Validate JSONL lines (no trailing commas, one JSON object per line)
* Ensure assistant outputs are **JSON only**
* Ensure refusal examples exist (at least 20–30)
* Cap sequence length (avoid huge contexts)
* Start with small pilot run before full training
* Record versions (base model id, dataset hash, adapter id)

---

…and I’ll output it in that structure immediately.
