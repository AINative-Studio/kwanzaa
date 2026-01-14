## Team Lanes (run in parallel)

**Lane A — Corpus + Ingestion**

* manifests, provenance schema, ingestion jobs, chunk/embed/store, eval questions

**Lane B — Product UI (AIKit)**

* Chat + RAGBot + Search Explorer + Collections + “show your work” rendering

**Lane C — Model + Training**

* dataset build, training run, evaluation, publish adapter artifact

**Lane D — DevRel + Launch**

* README, contribution workflow, issues/backlog, demo scripts, daily build logs

---

## Day-by-Day Plan

### Days 1–2: Foundations (Umoja)

**Goal:** get the skeleton working end-to-end with placeholder content.

**Lane A**

* Create `FirstFruitsManifest` file (P0 list only, 10–25 sources)
* Implement provenance schema + namespaces (exact names)
* Ingest metadata-first records into ZeroDB (docs + metadata, minimal text)

**Lane B**

* Ship UI scaffolding:

  * Kwanzaa Chat (with mode toggles)
  * Search Explorer (basic query + results list)
  * “Show your work” panel placeholder

**Lane C**

* Pick base model candidate list (AI2 first, others optional)
* Stand up training config (Doc #1) in repo
* Create dataset schema doc (SCHEMA.md)

**Lane D**

* Initialize open repo structure
* Add CONTRIBUTING + Code of Conduct + Issue templates

**Definition of Done**

* UI loads
* Search returns *something*
* All outputs render as `answer_json` (even if mocked)

---

### Days 3–4: Corpus MVP + RAG Plumbing (Nia)

**Goal:** RAG works with citations and provenance.

**Lane A**

* Expand P0 sources to full text (selective)
* Chunk + embed + store into persona namespaces:

  * `kwanzaa_primary_sources`
  * `kwanzaa_speeches_letters`
  * `kwanzaa_black_press`
  * `kwanzaa_black_stem`
  * `kwanzaa_teaching_kits`
  * `kwanzaa_dev_patterns`

**Lane B**

* Wire Chat to:

  * retrieve (top_k)
  * inject context
  * render sources + retrieval summary
* Add filters (namespace + year + content_type)

**Lane C**

* Draft eval questions (10 per persona)
* Start building dataset examples (Doc #2)

  * citation-following
  * refusal
  * strict JSON

**Lane D**

* Publish “First Fruits” public roadmap in README
* Add “How to contribute sources” instructions (manifest PR flow)

**Definition of Done**

* Educator mode: answers include citations
* Research mode: provenance fields always shown
* If no results: model says “not in corpus”

---

### Days 5–6: Persona Presets + Collections (Kujichagulia)

**Goal:** the demo feels intentional per persona.

**Lane A**

* Create “First Fruits Collections” (small curated sets) as metadata groupings:

  * Reconstruction
  * Civil Rights
  * Black Press
  * Black STEM
  * Speeches + Letters
* Ensure each collection has license + canonical URLs

**Lane B**

* Persona presets:

  * Builder: dev patterns namespace
  * Educator: citations required + primary sources toggle default
  * Creator: creative mode on but grounded
  * Researcher: provenance-first UI + filters default
* Collections UI (browse + click to search within)

**Lane C**

* Finalize v0 dataset:

  * 50 citation-following
  * 30 refusals
  * 40 strict JSON
  * eval set 25–40 lines
* Add dataset validator (JSON validity)

**Lane D**

* Daily build log format
* “Demo script v0” outline (persona walkthrough)

**Definition of Done**

* “Click persona → ask question → get answer + sources” works reliably
* Collections drive high hit-rate retrieval

---

### Days 7–8: Training Run #1 (Kuumba + Imani)

**Goal:** first adapter trained and published.

**Lane C (focus)**

* Run training using HF AutoTrain (recommended)
* Evaluate:

  * JSON valid rate
  * citation coverage rate
  * refusal correctness
* Publish adapter artifact:

  * adapter weights
  * training config
  * dataset version + manifest hash

**Lane A**

* Patch corpus gaps discovered by eval prompts
* Add 10–20 more P0 docs for weak areas

**Lane B**

* Add “confidence / retrieval strength” indicator
* Add “unknowns” block rendering

**Lane D**

* Post “Model training report” in repo (results + known limitations)

**Definition of Done**

* Adapter improves citation compliance and refusal behavior
* Adapter loads in your serving stack

---

### Days 9–10: RAG Quality + Citation Enforcement (Imani)

**Goal:** fewer hallucinations, better grounding.

**Lane A**

* Add metadata consistency checks (100% required fields)
* Add dedupe rules + canonical URL normalization

**Lane B**

* Enforce: if citations_required and sources empty → refuse template
* Render “retrieved chunks” (top N) with metadata

**Lane C**

* Training Run #2 (optional) if metrics fail thresholds:

  * Focus on refusal/citation examples
  * Limit to 1 epoch

**Lane D**

* Add “Known limitations” + “How to verify sources” section to README

**Definition of Done**

* Educator/Research presets meet:

  * ≥90% citation coverage OR explicit “not in corpus”
  * 100% provenance presence in chunks

---

### Days 11–12: Demo Hardening + Contribution Loop (Ujima)

**Goal:** open repo feels alive and safe to contribute to.

**Lane A**

* “Source contribution pipeline” spec:

  * add to manifest
  * validate license + canonical URL
  * ingestion logs entry

**Lane B**

* Add “Add to corpus” curator action (internal)
* Add ingestion status UI indicator (optional)

**Lane C**

* Freeze adapter version as `v0.1`
* Create regression eval list (golden prompts)

**Lane D**

* Populate backlog with labeled issues:

  * good first issue
  * data contributions
  * evaluation improvements
* Add PR template with provenance checklist

**Definition of Done**

* External contributors can add sources safely
* Maintainers can review quickly

---

### Days 13–15: Launch Package (Ujamaa)

**Goal:** ship the campaign with a polished story.

**Lane B**

* Final UI polish pass
* Add “shareable query links” (optional)
* Ensure answer_json render is stable

**Lane A**

* Final corpus manifest + dataset manifest published
* Freeze namespaces and schema

**Lane C**

* Final metrics snapshot + reproducibility notes

**Lane D**

* Launch assets:

  * README complete
  * Demo scripts
  * 4 persona walkthroughs
  * “Build your own cultural RAG” quickstart

**Definition of Done**

* Public repo: install → run demo → try persona flows
* Artifacts published (adapter + manifests)
* Clear invitation to contribute

---

## Critical Path (Don’t Break This)

1. **Corpus + provenance schema** (Days 1–4)
2. **RAG + UI “show your work”** (Days 3–6)
3. **Dataset + training** (Days 5–8)
4. **Evaluation + enforcement** (Days 9–10)
5. **Launch + contribution loop** (Days 11–15)

---

