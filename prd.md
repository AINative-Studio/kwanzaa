```markdown
# PRD: Kwanzaa Model

**Brand Codename:** Kwanzaa  
**Tagline:** *First Fruits for AI — grounded knowledge, cultural integrity, and community power.*  
**Name Origin:** “Kwanzaa” comes from the Swahili phrase **matunda ya kwanza** (“first fruits”) — symbolizing harvest and blessings.  
**Guiding Framework:** **Nguzo Saba (Seven Principles)**  
Umoja • Kujichagulia • Ujima • Ujamaa • Nia • Kuumba • Imani

**Project Type:** Cultural + RAG + Fine-tune MVP  
**Duration:** 15-day sprint (Black History Month activation)  
**Budget:** $500–$5,000 (fine-tune/adapters + hosting)  
**Platform:** AINative (ZeroDB + AIKit + RAG + Semantic Search)  
**Status:** New PRD (no references to any other products)

---

## 1) Executive Summary

**Kwanzaa** is a culturally grounded model and retrieval system built on AINative that delivers:

- Cited primary-source answers for **educators/students**
- Provenance-first search for **researchers**
- Prompted creative synthesis for **creators/community**
- Reusable RAG patterns for **builders/developers**

It combines a strong open model (coding-first option) with a **cultural adapter** and a **ZeroDB knowledge plane**.  
The MVP demonstrates that AINative can power trustworthy cultural intelligence with clear provenance, respectful language handling, and repeatable workflows.

---

## 2) Product Vision Anchored to Nguzo Saba

These principles are **product requirements**, not just branding.

### Umoja (Unity)
- One unified experience across personas: **ingest → search → chat → cite → create**
- Shared corpus conventions (schema, namespaces, provenance)

### Kujichagulia (Self-Determination)
- User-controlled toggles:
  - **Require citations**
  - **Primary sources only**
  - **Creative mode**
- Clear disclosures: what’s in the corpus vs. what isn’t

### Ujima (Collective Work & Responsibility)
- Community contribution workflow (post-MVP): submit sources + metadata review queue
- Clear accountability: change logs, ingestion logs, dataset manifests

### Ujamaa (Cooperative Economics)
- Showcase “developer-pays vs user-pays” optionality via AINative credits
- Open artifacts: dataset manifest + adapter published for reuse

### Nia (Purpose)
- Explicit purpose: education, research, responsible cultural computing
- No “culture cosplay” — grounded outputs with provenance

### Kuumba (Creativity)
- Creator tools: speech/explainer/curriculum generators with optional citations
- Style controls grounded in retrieved context

### Imani (Faith)
- Trust layer: citations, provenance, confidence scoring, refusal when unsupported
- “Show your work” UX: retrieval evidence and source links

---

## 3) User Personas (MVP Scope)

### Builders / Developers
> “Give me a culturally aware agent + RAG patterns”

### Educators / Students
> “Answer w/ citations and primary sources”

### Creators / Community
> “Generate prompts, speeches, explainers, curricula”

### Researchers
> “Search across a curated corpus with provenance”

---

## 4) Core MVP Features

### 4.1 Kwanzaa Chat (AIKit)

**Model Modes**
- Base model (coding-first option)
- Base + Kwanzaa Adapter
- Base + Adapter + RAG (default)

**Toggles**
- Require citations (default **ON** for educator/research modes)
- Primary sources only (filters namespaces)
- Creative mode (creator presets)

**Output Contract (always)**
- Answer
- Sources used (if any)
- Retrieval summary (top results + scores)
- “What I don’t know” when retrieval is weak

---

### 4.2 Kwanzaa RAGBot (AIKit)

- Upload → ingest → embed → store workflow
- Namespace selection
- Live preview of retrieved chunks + citations
- “Add to corpus” button for internal curators

---

### 4.3 Kwanzaa Semantic Search Explorer (ZeroDB)

**Search + Filters**
- Year range
- Source type
- Author
- Tags / era / geography

**Results Display**
- Snippet
- Score
- Canonical URL
- License and provenance

---

### 4.4 Kwanzaa Collections (Curated Sets)

Small, high-signal “first fruits” bundles aligned to persona needs:
- Civil Rights era set
- Reconstruction set
- Black STEM set
- Black Press set
- Speeches + Letters set

---

## 5) System Architecture (AINative-Native)

### Components
- **Model Serving:** open model endpoint + optional adapter
- **ZeroDB:** document storage, embeddings, vector search
- **RAG Orchestration:** retrieval → context injection → response formatting
- **AIKit UI:** Chat + RAGBot + Search Explorer + Collections

### ZeroDB Endpoints Used
- Projects
- Embeddings: `embed-and-store`, `search`
- Optional: Events (analytics, build logs)

---

## 6) Safety + Integrity Requirements (Imani)

### Hard Requirements
- If **Require citations** is ON:
  - Answers must include **≥1 citation** or explicitly state  
    “no supporting sources in corpus”
- If retrieval confidence is low:
  - Ask a clarifying question **or** refuse to assert specifics

### Prohibited Behaviors
- Stereotype reinforcement
- Mocking or performative dialect
- Invented quotes or fake attributions

### “Show Your Work” UX
Always display:
- Top retrieved chunks
- Scores
- Metadata
- Source links

---

## 7) 15-Day Execution Plan (High-Level)

**Days 1–3**
- Ship UI (Chat + RAGBot + Search Explorer)
- Implement provenance schema + namespace conventions
- Ingest initial “First Fruits” corpus (small)

**Days 4–7**
- RAG formatting + citation enforcement
- Persona presets (builder / educator / creator / researcher)
- Collections UI

**Days 8–11**
- Adapter fine-tune (QLoRA / LoRA) focused on:
  - Citation-following
  - Retrieval query decomposition
  - Safe uncertainty behavior

**Days 12–15**
- Eval harness (retrieval hit-rate + citation coverage)
- Launch build log + demo scripts
- Publish artifacts (adapter + dataset manifest)

---

## 8) Success Metrics

### Product Metrics
- Citation coverage rate (educator/research modes)
- Retrieval hit-rate above threshold
- Average time-to-first-answer with citations
- Creator satisfaction: “usable output” rate

### Growth Metrics
- New signups → project created → vectors stored → chats run
- Corpus growth per day (documents + chunks)

---

## 9) Deliverables

- Kwanzaa demo app (AIKit-based)
- ZeroDB corpus (namespaces + collections)
- Kwanzaa adapter (published artifact)
- Dataset manifest (sources, licenses, provenance)
```
