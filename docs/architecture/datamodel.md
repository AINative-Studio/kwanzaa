# Kwanzaa RAG Chatbot — ZeroDB Data Model (MVP)

## Design Goals
- **Provenance-first** storage (Imani)
- **Persona presets + toggles** (Kujichagulia)
- **Collections & bundles** (Umoja)
- **Auditable ingestion runs** (Ujima)
- **Citation and retrieval logging** for eval + growth

---

## 1) Core Entities (Tables)

### 1.1 `kw_projects`
Maps an AINative project to a Kwanzaa corpus + app settings.

**Fields**
- `id` UUID PK
- `ainative_project_id` UUID UNIQUE NOT NULL
- `name` TEXT NOT NULL
- `created_at` TIMESTAMP DEFAULT NOW()
- `updated_at` TIMESTAMP DEFAULT NOW()

---

### 1.2 `kw_users`
Minimal user record for analytics + personalization (do not store sensitive PII).

**Fields**
- `id` UUID PK
- `external_user_id` TEXT NULL (auth provider id)
- `role` TEXT NULL (admin, curator, user)
- `created_at` TIMESTAMP DEFAULT NOW()

---

### 1.3 `kw_persona_presets`
Defines persona defaults and what namespaces/filters they use.

**Fields**
- `id` UUID PK
- `key` TEXT UNIQUE NOT NULL  
  - `builder`
  - `educator`
  - `creator`
  - `researcher`
- `display_name` TEXT NOT NULL
- `description` TEXT
- `default_namespaces` JSONB NOT NULL  
  - e.g. `["kwanzaa_primary_sources","kwanzaa_speeches_letters"]`
- `default_filters` JSONB NULL  
  - e.g. `{ "content_type": ["speech","letter"], "year_gte": 1950 }`
- `require_citations_default` BOOLEAN DEFAULT TRUE
- `primary_sources_only_default` BOOLEAN DEFAULT FALSE
- `creative_mode_default` BOOLEAN DEFAULT FALSE
- `created_at` TIMESTAMP DEFAULT NOW()

---

### 1.4 `kw_chat_sessions`
One conversation thread.

**Fields**
- `id` UUID PK
- `ainative_project_id` UUID NOT NULL
- `user_id` UUID NULL FK → `kw_users.id`
- `persona_key` TEXT NOT NULL (FK-ish to `kw_persona_presets.key`)
- `title` TEXT NULL
- `model_mode` TEXT NOT NULL  
  - `base`
  - `base_adapter`
  - `base_adapter_rag`
- `toggles` JSONB NOT NULL  
  - `{ "require_citations": true, "primary_sources_only": false, "creative_mode": false }`
- `created_at` TIMESTAMP DEFAULT NOW()
- `updated_at` TIMESTAMP DEFAULT NOW()

**Indexes**
- `(ainative_project_id, created_at DESC)`
- `(user_id, created_at DESC)`

---

### 1.5 `kw_chat_messages`
Stores user + assistant turns, plus the “show your work” structure.

**Fields**
- `id` UUID PK
- `session_id` UUID NOT NULL FK → `kw_chat_sessions.id`
- `role` TEXT NOT NULL (`user` | `assistant` | `system`)
- `content` TEXT NOT NULL
- `created_at` TIMESTAMP DEFAULT NOW()

**Assistant-only structured fields**
- `answer_json` JSONB NULL  
  (normalized response payload used by AIKit UI)
- `refusal_reason` TEXT NULL
- `confidence` NUMERIC NULL (0–1)

**Indexes**
- `(session_id, created_at ASC)`

---

## 2) Retrieval + Citation “Show Your Work” Entities

### 2.1 `kw_retrieval_runs`
One retrieval execution for a user query (per assistant response).

**Fields**
- `id` UUID PK
- `session_id` UUID NOT NULL
- `user_message_id` UUID NOT NULL (FK → `kw_chat_messages.id`)
- `assistant_message_id` UUID NULL (FK → `kw_chat_messages.id`)
- `query` TEXT NOT NULL
- `top_k` INT DEFAULT 8
- `namespaces` JSONB NOT NULL (list)
- `filters` JSONB NULL
- `embedding_model` TEXT NOT NULL DEFAULT `BAAI/bge-small-en-v1.5`
- `retrieval_latency_ms` INT NULL
- `created_at` TIMESTAMP DEFAULT NOW()

---

### 2.2 `kw_retrieval_results`
Top retrieved chunks + scores, stored for replay + audit.

**Fields**
- `id` UUID PK
- `retrieval_run_id` UUID NOT NULL FK → `kw_retrieval_runs.id`
- `namespace` TEXT NOT NULL
- `chunk_id` TEXT NOT NULL  (matches ZeroDB vector/doc id)
- `doc_id` TEXT NOT NULL
- `score` NUMERIC NOT NULL
- `rank` INT NOT NULL
- `snippet` TEXT NULL
- `metadata` JSONB NOT NULL  (includes provenance + citation_label + canonical_url)
- `created_at` TIMESTAMP DEFAULT NOW()

**Indexes**
- `(retrieval_run_id, rank ASC)`
- `(namespace, doc_id)`

---

### 2.3 `kw_citations_used`
What the assistant actually cited (subset of retrieval results).

**Fields**
- `id` UUID PK
- `assistant_message_id` UUID NOT NULL FK → `kw_chat_messages.id`
- `retrieval_run_id` UUID NOT NULL FK → `kw_retrieval_runs.id`
- `chunk_id` TEXT NOT NULL
- `canonical_url` TEXT NOT NULL
- `citation_label` TEXT NOT NULL
- `year` INT NULL
- `source_org` TEXT NOT NULL
- `content_type` TEXT NOT NULL
- `created_at` TIMESTAMP DEFAULT NOW()

**Rule**
- If `require_citations=true`, then:
  - must have ≥1 row in `kw_citations_used`
  - OR assistant_message has `refusal_reason = "no_supporting_sources_in_corpus"`

---

## 3) Corpus Management Entities (Ingestion + Collections)

### 3.1 `kw_source_manifest`
Stores your `FIRST_FRUITS_MANIFEST.json` *as rows* for queryability.

**Fields**
- `id` UUID PK
- `job_id` TEXT UNIQUE NOT NULL
- `source_name` TEXT NOT NULL
- `source_type` TEXT NOT NULL
- `base_url` TEXT NOT NULL
- `access_method` TEXT NOT NULL
- `license` TEXT NOT NULL
- `priority` TEXT NOT NULL (`P0`|`P1`|`P2`)
- `default_namespace` TEXT NOT NULL
- `tags` JSONB NOT NULL
- `schedule` TEXT NOT NULL
- `query_templates` JSONB NOT NULL
- `created_at` TIMESTAMP DEFAULT NOW()
- `updated_at` TIMESTAMP DEFAULT NOW()

---

### 3.2 `kw_ingestion_runs`
Tracks each run for audit + Ujima.

**Fields**
- `id` UUID PK
- `job_id` TEXT NOT NULL (FK-ish to manifest)
- `run_type` TEXT NOT NULL (`discover`|`metadata_import`|`fulltext_expand`|`incremental`)
- `status` TEXT NOT NULL (`running`|`success`|`failed`)
- `started_at` TIMESTAMP DEFAULT NOW()
- `ended_at` TIMESTAMP NULL
- `docs_attempted` INT DEFAULT 0
- `docs_ingested` INT DEFAULT 0
- `chunks_ingested` INT DEFAULT 0
- `errors` JSONB NULL
- `run_notes` TEXT NULL

---

### 3.3 `kw_corpus_collections`
Your “First Fruits” bundles: Civil Rights, Black STEM, etc.

**Fields**
- `id` UUID PK
- `key` TEXT UNIQUE NOT NULL  
  - `civil_rights`
  - `reconstruction`
  - `black_stem`
  - `black_press`
  - `speeches_letters`
- `display_name` TEXT NOT NULL
- `description` TEXT
- `default_namespaces` JSONB NOT NULL
- `default_filters` JSONB NULL
- `created_at` TIMESTAMP DEFAULT NOW()

---

### 3.4 `kw_collection_items`
Map collections to docs/chunks.

**Fields**
- `id` UUID PK
- `collection_id` UUID NOT NULL FK → `kw_corpus_collections.id`
- `namespace` TEXT NOT NULL
- `doc_id` TEXT NOT NULL
- `chunk_id` TEXT NULL (optional; can point at whole doc)
- `curation_notes` TEXT NULL
- `priority` INT DEFAULT 0
- `created_at` TIMESTAMP DEFAULT NOW()

---

## 4) Evaluation Entities (Minimal but Real)

### 4.1 `kw_eval_questions`
Stores your 20-per-persona test set.

**Fields**
- `id` UUID PK
- `persona_key` TEXT NOT NULL
- `question` TEXT NOT NULL
- `expected_namespace_hints` JSONB NULL
- `expected_doc_ids` JSONB NULL
- `require_citations` BOOLEAN DEFAULT TRUE
- `created_at` TIMESTAMP DEFAULT NOW()

---

### 4.2 `kw_eval_runs`
One eval run execution.

**Fields**
- `id` UUID PK
- `run_name` TEXT NOT NULL
- `commit_sha` TEXT NULL
- `model_mode` TEXT NOT NULL
- `created_at` TIMESTAMP DEFAULT NOW()
- `summary` JSONB NULL

---

### 4.3 `kw_eval_results`
Per-question results for citation coverage + retrieval hit rate.

**Fields**
- `id` UUID PK
- `eval_run_id` UUID NOT NULL
- `eval_question_id` UUID NOT NULL
- `retrieval_run_id` UUID NULL
- `citation_ok` BOOLEAN NOT NULL
- `retrieval_hit` BOOLEAN NOT NULL
- `notes` TEXT NULL
- `created_at` TIMESTAMP DEFAULT NOW()

---

## 5) How This Maps to the PRD Features

### Kwanzaa Chat (AIKit)
- `kw_chat_sessions` + `kw_chat_messages`
- `kw_retrieval_runs` + `kw_retrieval_results`
- `kw_citations_used` enforces Imani

### RAGBot (AIKit)
- Ingestion actions create `kw_ingestion_runs`
- Added docs map into ZeroDB embeddings namespaces
- Curators can attach `kw_collection_items`

### Search Explorer (ZeroDB)
- Uses embeddings search + filters
- UI can also query:
  - `kw_source_manifest`
  - `kw_corpus_collections`

### “Show Your Work” UX
- Retrieval and citation tables power:
  - top chunks
  - scores
  - metadata
  - citations used

---

## 6) Minimal Index Recommendations
- `kw_chat_messages(session_id, created_at)`
- `kw_retrieval_results(retrieval_run_id, rank)`
- `kw_citations_used(assistant_message_id)`
- `kw_ingestion_runs(job_id, started_at DESC)`
- `kw_collection_items(collection_id, priority DESC)`

---

## 7) Implementation Notes (ZeroDB Alignment)
- Chunks are stored in **ZeroDB embeddings** using:
  - `id = chunk_id`
  - `metadata = canonical chunk schema`
- Tables store:
  - session state
  - run logs
  - citations used
  - eval results
- This avoids duplicating the full corpus in SQL tables while still enabling UX + auditability.

---


