# Data Ingest Plan

**Leveraging the OnSide Personal Data Lakehouse + Agent Pipelines**

## Strategic Reframe (Critical)

We are **not building a new ingestion system**.

We are **repurposing OnSide’s proven strengths**:

* Multi-source data aggregation
* Automated scraping & API ingestion
* Normalization pipelines
* Historical retention
* AI-ready structuring
* Agent-driven analysis loops

**New framing:**

> **OnSide = AINative’s Internal Data Acquisition + Scraping Engine**
> ZeroDB = Long-term semantic memory + RAG layer

OnSide gathers, cleans, and structures data.
ZeroDB indexes, embeds, and serves it for reasoning.

---

## How OnSide Fits the Cultural MVP (At a Systems Level)

### Existing OnSide Capabilities We Reuse

From the doc you shared, OnSide already supports:

* Automated **web + content ingestion**
* **Competitor content scraping**
* **News monitoring**
* **Content inventory creation**
* **Topic clustering & semantic analysis**
* **Historical backfill**
* **Daily automated pipelines**
* **Agent-first interaction model**

These map *directly* to what we need for cultural data.

---

## Revised Ingest Architecture (AINative + OnSide)

```
┌───────────────────────────────────────────┐
│          PUBLIC / OPEN WEB SOURCES        │
│  (archives, news, speeches, essays, etc.)│
└─────────────────────┬─────────────────────┘
                      ▼
┌───────────────────────────────────────────┐
│     ONSIDE INGEST & SCRAPE PIPELINES      │
│                                           │
│  • Source discovery                       │
│  • Scheduled scraping                    │
│  • Content extraction                    │
│  • Normalization                          │
│  • Metadata enrichment                   │
│  • Historical backfill                   │
└─────────────────────┬─────────────────────┘
                      ▼
┌───────────────────────────────────────────┐
│        ONSIDE PERSONAL DATA LAKEHOUSE     │
│  (internal AINative tenant / project)    │
│                                           │
│  • Raw → Clean → AI-ready layers          │
│  • Full provenance                        │
│  • Time-indexed                           │
└─────────────────────┬─────────────────────┘
                      ▼
┌───────────────────────────────────────────┐
│              ZeroDB                       │
│                                           │
│  • Chunking                               │
│  • Embeddings                             │
│  • Semantic search                        │
│  • RAG                                   │
│  • Citation surfacing                     │
└───────────────────────────────────────────┘
```

---

## Persona-Driven Ingest Strategy (Using OnSide)

### Persona 1: Builders / Developers

**“Give me a culturally aware agent + RAG patterns”**

#### How OnSide Helps

* OnSide already:

  * Crawls competitor content
  * Tracks topic coverage
  * Builds content inventories
* We repurpose this to:

  * Crawl *public cultural sources*
  * Treat each source like a “competitor domain”
  * Track topic clusters across sources

#### Ingest Pattern

* OnSide:

  * Scrapes content pages
  * Extracts text + metadata
  * Groups by topic / theme
* ZeroDB:

  * Embeds cleaned content
  * Enables RAG examples

#### What This Proves

* Developers see:

  * A real, automated RAG pipeline
  * How topic clustering feeds retrieval
  * How agents reason over structured corpora

---

### Persona 2: Educators / Students

**“Answer w/ citations and primary sources”**

#### How OnSide Helps

* OnSide already:

  * Monitors news sources
  * Stores historical content
  * Preserves timestamps
* We adapt this to:

  * Monitor trusted public archives
  * Backfill historical content
  * Preserve source URLs + publish dates

#### Ingest Pattern

* OnSide:

  * Pulls content on a schedule
  * Captures original URLs, authors, dates
* ZeroDB:

  * Stores chunks with provenance
  * Enforces citation-first RAG

#### What This Proves

* The system behaves like:

  * An academic assistant
  * A citation engine
  * A trustworthy knowledge base

---

### Persona 3: Creators / Community

**“Generate prompts, speeches, explainers, curricula”**

#### How OnSide Helps

* OnSide already:

  * Analyzes content tone
  * Identifies content gaps
  * Generates content briefs
* We reuse this to:

  * Classify narrative content
  * Preserve rhetorical structure
  * Enable style-aware generation

#### Ingest Pattern

* OnSide:

  * Extracts long-form content
  * Tags themes, tone, audience
* ZeroDB:

  * Supports generative RAG prompts
  * Optionally surfaces sources

#### What This Proves

* Culture is:

  * Retrieved, not hallucinated
  * Transformable, not distorted
* Same data powers both facts *and* creativity

---

### Persona 4: Researchers

**“Search across a curated corpus with provenance”**

#### How OnSide Helps

* OnSide already:

  * Maintains a **lakehouse**
  * Tracks historical changes
  * Correlates across sources
* We adapt this to:

  * Maintain a metadata-first index
  * Preserve long-term historical timelines

#### Ingest Pattern

* OnSide:

  * Acts as the canonical record store
  * Maintains clean, queryable metadata
* ZeroDB:

  * Provides semantic search + filters
  * Exposes why results matched

#### What This Proves

* AINative + OnSide can function as:

  * A discovery engine
  * A research index
  * A provenance-first AI system

---

## How OnSide Pipelines Map to Cultural Ingest

| OnSide Concept      | Cultural MVP Equivalent        |
| ------------------- | ------------------------------ |
| Competitor Domains  | Public archives / sites        |
| Content Inventory   | Cultural corpus                |
| News Monitoring     | Historical + current discourse |
| Topic Clusters      | Themes / movements / eras      |
| Historical Backfill | Archive ingestion              |
| Daily Pipelines     | Incremental corpus growth      |
| Agent Insights      | RAG + explanation layer        |

This is reuse, not reinvention.

---

## Minimal Changes Required (Realistic)

We **do not** need to rebuild OnSide.

We only need:

* A new internal “AINative Cultural Project” tenant
* Source definitions pointed at public/open content
* Slight schema extension for:

  * license
  * content_type
  * canonical_source

Everything else already exists conceptually.

---

## What Agents Should Validate in the Codebase

Have agents confirm:

1. Existing scraping & crawling logic
2. Content extraction & cleaning steps
3. Topic clustering / semantic analysis
4. Historical backfill support
5. Scheduled ingestion workflows
6. Data handoff points where ZeroDB can ingest
7. Where provenance metadata already exists

The question becomes:

> **How fast can we point OnSide at cultural sources instead of SMB competitors?**

---

## Why This Is a Strong Move Strategically

* You showcase **two internal products working together**
* You avoid one-off MVP hacks
* You prove AINative can:

  * ingest
  * reason
  * cite
  * generate
  * scale
* You turn Black History Month into:

  * a real platform demo
  * not a marketing stunt

---

