# Kwanzaa Namespace Architecture - Visual Diagrams

**Purpose**: Visual representations of namespace architecture, data flow, and persona mappings
**Created**: 2026-01-16

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KWANZAA NAMESPACE ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   USER QUERY    │
│  (with persona) │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────────────────────────────────────────┐
│                      PERSONA PRESET LAYER                                │
├─────────────────┬─────────────────┬─────────────────┬──────────────────┤
│   EDUCATOR      │   RESEARCHER    │    CREATOR      │     BUILDER      │
│                 │                 │                 │                  │
│ • primary_      │ • ALL           │ • speeches_     │ • dev_patterns   │
│   sources       │   namespaces    │   letters       │ • primary_       │
│ • speeches_     │                 │ • teaching_kits │   sources        │
│   letters       │                 │ • black_press   │                  │
│ • teaching_kits │                 │                 │                  │
│                 │                 │                 │                  │
│ Threshold: 0.80 │ Threshold: 0.75 │ Threshold: 0.65 │ Threshold: 0.70  │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬─────────┘
         │                 │                 │                 │
         └─────────────────┴─────────────────┴─────────────────┘
                                   │
                                   v
┌─────────────────────────────────────────────────────────────────────────┐
│                         NAMESPACE ROUTER                                 │
│  (Selects appropriate namespaces based on persona + explicit filters)   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         v                         v                         v
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  kwanzaa_        │    │  kwanzaa_        │    │  kwanzaa_        │
│  primary_        │    │  black_press     │    │  speeches_       │
│  sources         │    │                  │    │  letters         │
│                  │    │                  │    │                  │
│ • Gov docs       │    │ • Newspapers     │    │ • Speeches       │
│ • Archives       │    │ • Periodicals    │    │ • Letters        │
│ • Laws           │    │ • Editorials     │    │ • Sermons        │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  kwanzaa_        │    │  kwanzaa_        │    │  kwanzaa_        │
│  black_stem      │    │  teaching_kits   │    │  dev_patterns    │
│                  │    │                  │    │                  │
│ • Biographies    │    │ • Lesson plans   │    │ • RAG patterns   │
│ • Patents        │    │ • Curriculum     │    │ • Schemas        │
│ • Research       │    │ • Activities     │    │ • Code examples  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   v
┌─────────────────────────────────────────────────────────────────────────┐
│                      ZERODB VECTOR STORE                                 │
│  (1536-dim embeddings with provenance metadata)                         │
│                                                                          │
│  Each chunk has:                                                         │
│  • embedding: [0.123, -0.456, ...]                                      │
│  • metadata: {canonical_url, source_org, license, year, content_type,   │
│               citation_label, tags, ...}                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   v
┌─────────────────────────────────────────────────────────────────────────┐
│                      RETRIEVAL RESULTS                                   │
│  • Ranked chunks with scores                                             │
│  • Complete provenance for each result                                   │
│  • Citation labels ready for rendering                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   v
┌─────────────────────────────────────────────────────────────────────────┐
│                      ANSWER JSON CONTRACT                                │
│  {                                                                       │
│    "answer": "...",                                                      │
│    "sources": [...],           ← Citations from retrieval                │
│    "retrieval_summary": {...}, ← Namespace, scores, counts              │
│    "unknowns": {...}           ← Gaps in corpus                         │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Ingestion Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│  FIRST FRUITS MANIFEST  │
│                         │
│ {                       │
│   "job_id": "...",      │
│   "source_name": "...", │
│   "default_namespace":  │
│     "kwanzaa_...",      │  ← NAMESPACE ASSIGNMENT
│   "priority": "P0",     │
│   "license": "...",     │
│   ...                   │
│ }                       │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────────────────────────────────────────────────────┐
│                    INGESTION VALIDATOR                                   │
│                                                                          │
│  1. Validate namespace (must be one of 6)                               │
│  2. Check priority (P0/P1/P2)                                           │
│  3. Verify access credentials                                            │
│  4. Create kw_ingestion_runs record                                     │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
            v
┌─────────────────────────────────────────────────────────────────────────┐
│                    SOURCE FETCHER                                        │
│                                                                          │
│  • API calls (NARA, LOC, etc.)                                          │
│  • Bulk downloads (newspaper archives)                                  │
│  • Manual curation (high-priority items)                                │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
            v
┌─────────────────────────────────────────────────────────────────────────┐
│                 PROVENANCE VALIDATOR (100% ENFORCEMENT)                  │
│                                                                          │
│  FOR EACH DOCUMENT:                                                      │
│  ✓ canonical_url exists?                                                │
│  ✓ source_org exists?                                                   │
│  ✓ license exists?                                                      │
│  ✓ year exists and valid (1600-2100)?                                  │
│  ✓ content_type exists?                                                 │
│  ✓ citation_label exists?                                               │
│                                                                          │
│  If ANY field missing → REJECT DOCUMENT                                 │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
            v
┌─────────────────────────────────────────────────────────────────────────┐
│                         CHUNKER                                          │
│                                                                          │
│  • Split document into chunks (512 tokens, 50 overlap)                  │
│  • Preserve provenance metadata for EACH chunk                          │
│  • Generate chunk_id: {doc_id}::chunk::{index}                         │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
            v
┌─────────────────────────────────────────────────────────────────────────┐
│                      EMBEDDING GENERATOR                                 │
│                                                                          │
│  • Model: BAAI/bge-small-en-v1.5                                        │
│  • Dimensions: 1536                                                      │
│  • Generate embedding for chunk.content                                  │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
            v
┌─────────────────────────────────────────────────────────────────────────┐
│              ZERODB STORAGE (with namespace)                             │
│                                                                          │
│  POST /database/vectors/upsert                                           │
│  {                                                                       │
│    "vector_id": "chunk_id",                                             │
│    "vector_embedding": [...],                                           │
│    "namespace": "kwanzaa_primary_sources",  ← NAMESPACE TAG             │
│    "metadata": {                                                        │
│      "doc_id": "...",                                                   │
│      "chunk_index": 1,                                                  │
│      "canonical_url": "...",                                            │
│      "source_org": "...",                                               │
│      "license": "...",                                                  │
│      "year": 1964,                                                      │
│      "content_type": "...",                                             │
│      "citation_label": "...",                                           │
│      ...                                                                │
│    }                                                                     │
│  }                                                                       │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
            v
┌─────────────────────────────────────────────────────────────────────────┐
│                   UPDATE INGESTION RUN STATUS                            │
│                                                                          │
│  kw_ingestion_runs:                                                      │
│  • status = "success"                                                    │
│  • docs_ingested = 150                                                   │
│  • chunks_ingested = 1500                                                │
│  • namespace = "kwanzaa_primary_sources"                                │
│  • ended_at = NOW()                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Persona-Namespace Mapping Heatmap

```
PERSONA-NAMESPACE PRIORITY MATRIX
(■ = Primary, ▓ = Secondary, ░ = Tertiary, · = Not typically used)

                       │ primary_ │ black_  │ speeches_ │ black_ │ teaching_ │ dev_     │
                       │ sources  │ press   │ letters   │ stem   │ kits      │ patterns │
───────────────────────┼──────────┼─────────┼───────────┼────────┼───────────┼──────────┤
EDUCATOR               │    ■     │    ·    │     ■     │   ▓    │     ■     │    ·     │
(Citation-first)       │          │         │           │        │           │          │
───────────────────────┼──────────┼─────────┼───────────┼────────┼───────────┼──────────┤
RESEARCHER             │    ■     │    ■    │     ■     │   ■    │     ■     │    ■     │
(Comprehensive)        │          │         │           │        │           │          │
───────────────────────┼──────────┼─────────┼───────────┼────────┼───────────┼──────────┤
CREATOR                │    ▓     │    ░    │     ■     │   ·    │     ■     │    ·     │
(Creative synthesis)   │          │         │           │        │           │          │
───────────────────────┼──────────┼─────────┼───────────┼────────┼───────────┼──────────┤
BUILDER                │    ▓     │    ·    │     ·     │   ·    │     ·     │    ■     │
(Technical patterns)   │          │         │           │        │           │          │
───────────────────────┴──────────┴─────────┴───────────┴────────┴───────────┴──────────┘

QUERY THRESHOLD BY PERSONA:
Educator:   ████████░░ 0.80 (stricter)
Researcher: ███████░░░ 0.75 (balanced)
Creator:    ██████░░░░ 0.65 (exploratory)
Builder:    ███████░░░ 0.70 (technical)
```

---

## Database Schema Integration

```
┌────────────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA RELATIONSHIPS                        │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│  kw_source_manifest     │
│─────────────────────────│
│  id                     │
│  job_id                 │
│  source_name            │
│  default_namespace  ◄───┼─── NAMESPACE ASSIGNED HERE
│  priority               │
│  license                │
│  ...                    │
└──────────┬──────────────┘
           │
           │ (used by)
           │
           v
┌─────────────────────────┐
│  kw_ingestion_runs      │
│─────────────────────────│
│  id                     │
│  job_id                 │
│  namespace          ◄───┼─── TRACKS WHICH NAMESPACE POPULATED
│  status                 │
│  docs_ingested          │
│  chunks_ingested        │
│  ...                    │
└─────────────────────────┘


┌─────────────────────────┐
│  kw_persona_presets     │
│─────────────────────────│
│  key (educator, ...)    │
│  default_namespaces ◄───┼─── JSONB ARRAY OF NAMESPACES
│  threshold_default      │
│  require_citations      │
│  ...                    │
└──────────┬──────────────┘
           │
           │ (used in)
           │
           v
┌─────────────────────────┐
│  kw_chat_sessions       │
│─────────────────────────│
│  id                     │
│  persona_key            │
│  toggles (JSONB)        │
│  ...                    │
└──────────┬──────────────┘
           │
           │
           v
┌─────────────────────────┐
│  kw_retrieval_runs      │
│─────────────────────────│
│  id                     │
│  session_id             │
│  query                  │
│  namespaces (JSONB) ◄───┼─── WHICH NAMESPACES WERE QUERIED
│  filters                │
│  ...                    │
└──────────┬──────────────┘
           │
           │
           v
┌─────────────────────────┐
│  kw_retrieval_results   │
│─────────────────────────│
│  id                     │
│  retrieval_run_id       │
│  namespace          ◄───┼─── WHICH NAMESPACE RESULT CAME FROM
│  chunk_id               │
│  doc_id                 │
│  score                  │
│  metadata (JSONB)       │
│  ...                    │
└──────────┬──────────────┘
           │
           │ (subset of)
           │
           v
┌─────────────────────────┐
│  kw_citations_used      │
│─────────────────────────│
│  id                     │
│  assistant_message_id   │
│  retrieval_run_id       │
│  chunk_id               │
│  canonical_url          │
│  citation_label         │
│  ...                    │
└─────────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│                    ZERODB VECTORS                            │
│──────────────────────────────────────────────────────────────│
│  vector_id: "chunk_id"                                       │
│  embedding: [1536 floats]                                    │
│  metadata: {                                                 │
│    "namespace": "kwanzaa_primary_sources", ◄─── NAMESPACE    │
│    "doc_id": "...",                                          │
│    "canonical_url": "...",                                   │
│    "source_org": "...",                                      │
│    "license": "...",                                         │
│    "year": 1964,                                             │
│    "content_type": "...",                                    │
│    "citation_label": "...",                                  │
│    ...                                                       │
│  }                                                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Search Query Flow

```
USER QUERY: "What did the Civil Rights Act of 1964 prohibit?"
PERSONA: educator
NAMESPACE: (not specified, use persona default)

┌─────────────────────────────────────────────────────────────┐
│  1. RECEIVE QUERY                                           │
│     • query: "What did the Civil Rights Act..."            │
│     • persona_key: "educator"                               │
│     • namespace: null (will use persona default)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  2. LOAD PERSONA PRESET                                     │
│     SELECT * FROM kw_persona_presets                        │
│     WHERE key = 'educator'                                  │
│                                                             │
│     Result:                                                 │
│     • default_namespaces: ["kwanzaa_primary_sources",      │
│                            "kwanzaa_speeches_letters",      │
│                            "kwanzaa_teaching_kits"]         │
│     • threshold_default: 0.80                               │
│     • require_citations_default: true                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  3. APPLY DEFAULTS                                          │
│     • namespace = "kwanzaa_primary_sources" (first in list) │
│     • threshold = 0.80                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  4. GENERATE QUERY EMBEDDING                                │
│     • model: BAAI/bge-small-en-v1.5                         │
│     • input: "What did the Civil Rights Act..."            │
│     • output: [1536 floats]                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  5. VECTOR SEARCH (ZeroDB)                                  │
│     POST /database/vectors/search                           │
│     {                                                       │
│       "query_vector": [...],                                │
│       "namespace": "kwanzaa_primary_sources",               │
│       "metadata_filter": {},                                │
│       "limit": 10,                                          │
│       "threshold": 0.80                                     │
│     }                                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  6. RETRIEVE RESULTS                                        │
│     Results (ranked by score):                              │
│     1. [0.93] nara_cra_1964::chunk::3                       │
│        "An Act to enforce the constitutional right..."      │
│        Metadata: {                                          │
│          namespace: "kwanzaa_primary_sources",              │
│          citation_label: "National Archives (1964) - ...",  │
│          canonical_url: "https://archives.gov/...",         │
│          ...                                                │
│        }                                                    │
│     2. [0.89] nara_cra_1964::chunk::5                       │
│     ...                                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  7. LOG RETRIEVAL RUN                                       │
│     INSERT INTO kw_retrieval_runs                           │
│     (query, namespaces, top_k, ...)                         │
│     VALUES                                                  │
│     ('What did...', '["kwanzaa_primary_sources"]', 10, ...) │
│                                                             │
│     INSERT INTO kw_retrieval_results                        │
│     (retrieval_run_id, namespace, chunk_id, score, rank)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  8. GENERATE RESPONSE                                       │
│     • Use top chunks as context                             │
│     • Generate answer with citations                        │
│     • Format as answer_json                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│  9. RETURN TO USER                                          │
│     {                                                       │
│       "answer": "The Civil Rights Act of 1964...",          │
│       "sources": [                                          │
│         {                                                   │
│           "citation_label": "National Archives (1964)...",  │
│           "canonical_url": "https://archives.gov/...",      │
│           "year": 1964,                                     │
│           "namespace": "kwanzaa_primary_sources"            │
│         }                                                   │
│       ],                                                    │
│       "retrieval_summary": {                                │
│         "total_results": 5,                                 │
│         "top_score": 0.93,                                  │
│         "namespaces_searched": ["kwanzaa_primary_sources"]  │
│       },                                                    │
│       "unknowns": null                                      │
│     }                                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Namespace Content Type Distribution

```
PRIMARY_SOURCES                BLACK_PRESS
┌──────────────────┐          ┌──────────────────┐
│ proclamation     │ 30%      │ newspaper_       │ 60%
│ legal_document   │ 40%      │ article          │
│ government_      │ 20%      │ editorial        │ 25%
│ report           │          │ column           │ 10%
│ treaty           │  5%      │ obituary         │  3%
│ executive_order  │  5%      │ announcement     │  2%
└──────────────────┘          └──────────────────┘

SPEECHES_LETTERS             BLACK_STEM
┌──────────────────┐          ┌──────────────────┐
│ speech           │ 50%      │ biography        │ 50%
│ letter           │ 30%      │ patent           │ 20%
│ sermon           │ 10%      │ research_paper   │ 15%
│ testimony        │  5%      │ technical_doc    │ 10%
│ radio_address    │  3%      │ oral_history     │  5%
│ interview        │  2%      │                  │
└──────────────────┘          └──────────────────┘

TEACHING_KITS                DEV_PATTERNS
┌──────────────────┐          ┌──────────────────┐
│ lesson_plan      │ 40%      │ architecture_    │ 30%
│ curriculum_guide │ 30%      │ pattern          │
│ discussion_guide │ 15%      │ prompt_template  │ 25%
│ activity         │ 10%      │ schema           │ 20%
│ assessment       │  5%      │ code_example     │ 15%
│                  │          │ best_practice    │ 10%
└──────────────────┘          └──────────────────┘
```

---

## Provenance Validation Gate

```
                      ┌─────────────────────────┐
                      │   DOCUMENT ARRIVES      │
                      │   AT INGESTION          │
                      └───────────┬─────────────┘
                                  │
                                  v
                    ╔═════════════════════════════╗
                    ║  PROVENANCE VALIDATION GATE ║
                    ║    (100% ENFORCEMENT)       ║
                    ╚═════════════════════════════╝
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                v                 v                 v
       ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
       │ canonical_url? │ │   source_org?  │ │    license?    │
       └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
                │                  │                  │
                v                  v                  v
              ✓/✗                ✓/✗                ✓/✗
                │                  │                  │
                └──────────────────┴──────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                v                 v                 v
       ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
       │     year?      │ │ content_type?  │ │citation_label? │
       │  (1600-2100)   │ │                │ │                │
       └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
                │                  │                  │
                v                  v                  v
              ✓/✗                ✓/✗                ✓/✗
                │                  │                  │
                └──────────────────┴──────────────────┘
                                  │
                                  v
                          ┌───────────────┐
                          │  ALL FIELDS   │
                          │   PRESENT?    │
                          └───────┬───────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    v                           v
               ┌─────────┐                 ┌─────────┐
               │   YES   │                 │   NO    │
               │  ✓✓✓✓✓✓ │                 │  ✗✗✗✗✗✗ │
               └────┬────┘                 └────┬────┘
                    │                           │
                    v                           v
            ┌───────────────┐          ┌────────────────┐
            │   PROCEED TO  │          │     REJECT     │
            │   CHUNKING    │          │    DOCUMENT    │
            └───────────────┘          └────────────────┘
                                              │
                                              v
                                       ┌──────────────┐
                                       │ LOG ERROR IN │
                                       │ kw_ingestion │
                                       │    _runs     │
                                       └──────────────┘
```

---

## Cross-Namespace Collection Example

```
┌──────────────────────────────────────────────────────────────────┐
│         COLLECTION: "Civil Rights Movement (1954-1968)"          │
└──────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        v                       v                       v
┌───────────────┐      ┌────────────────┐     ┌────────────────┐
│ kwanzaa_      │      │  kwanzaa_      │     │  kwanzaa_      │
│ primary_      │      │  black_press   │     │  speeches_     │
│ sources       │      │                │     │  letters       │
├───────────────┤      ├────────────────┤     ├────────────────┤
│               │      │                │     │                │
│ • Brown v.    │      │ • Chicago      │     │ • MLK I Have   │
│   Board       │      │   Defender     │     │   a Dream      │
│   (1954)      │      │   coverage     │     │ • Malcolm X    │
│               │      │   of Brown     │     │   speeches     │
│ • Civil       │      │                │     │                │
│   Rights Act  │      │ • Pittsburgh   │     │ • Letter from  │
│   (1964)      │      │   Courier      │     │   Birmingham   │
│               │      │   on March     │     │   Jail         │
│ • Voting      │      │                │     │                │
│   Rights Act  │      │ • Amsterdam    │     │ • Freedom      │
│   (1965)      │      │   News         │     │   Summer       │
│               │      │   editorials   │     │   testimony    │
└───────────────┘      └────────────────┘     └────────────────┘

QUERY THIS COLLECTION:
  → Searches across all 3 namespaces
  → Unified results ranked by relevance
  → Citations maintain namespace provenance
```

---

## API Request/Response Example

```
REQUEST:
────────
POST /api/v1/search/semantic

{
  "query": "civil rights legislation",
  "namespace": "kwanzaa_primary_sources",
  "filters": {
    "year_gte": 1960,
    "year_lte": 1970
  },
  "limit": 5,
  "threshold": 0.75,
  "persona_key": "educator"
}


RESPONSE:
─────────
{
  "status": "success",
  "query": {
    "text": "civil rights legislation",
    "namespace": "kwanzaa_primary_sources",    ← NAMESPACE APPLIED
    "filters_applied": {
      "year_gte": 1960,
      "year_lte": 1970
    },
    "limit": 5,
    "threshold": 0.80    ← PERSONA DEFAULT APPLIED (educator = 0.80)
  },
  "results": [
    {
      "rank": 1,
      "score": 0.93,
      "chunk_id": "nara_cra_1964::chunk::3",
      "doc_id": "nara_cra_1964",
      "namespace": "kwanzaa_primary_sources",   ← RESULT NAMESPACE
      "content": "An Act to enforce the constitutional right...",
      "metadata": {
        "citation_label": "National Archives (1964) - Civil Rights Act",
        "canonical_url": "https://www.archives.gov/...",
        "source_org": "National Archives",
        "year": 1964,
        "content_type": "legal_document",
        "license": "Public Domain",
        "tags": ["civil_rights", "legislation"]
      }
    },
    ...
  ],
  "total_results": 5,
  "search_metadata": {
    "execution_time_ms": 45,
    "embedding_model": "BAAI/bge-small-en-v1.5",
    "query_embedding_time_ms": 12,
    "search_time_ms": 33
  }
}
```

---

**Version**: 1.0
**Last Updated**: 2026-01-16
**Purpose**: Visual reference for architecture diagrams and data flows
