# ZeroDB `/database/tables` Creation Payloads — Kwanzaa RAG Data Model (MVP)

**Endpoint:** `POST /v1/public/{project_id}/database/tables`  
**Body Contract:** `{ name, description, schema }`

> Notes
- These are **table creation payloads only** (no rows).  
- Foreign keys are represented as UUID columns (FK constraints can be added later via SQL migrations if you want strict enforcement).
- Timestamps use `TIMESTAMP DEFAULT NOW()` to stay consistent with your docs.

---

## 1) `kw_projects`

```json
{
  "name": "kw_projects",
  "description": "Maps an AINative project to a Kwanzaa corpus + app settings.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "ainative_project_id": "UUID UNIQUE NOT NULL",
    "name": "TEXT NOT NULL",
    "created_at": "TIMESTAMP DEFAULT NOW()",
    "updated_at": "TIMESTAMP DEFAULT NOW()"
  }
}
````

---

## 2) `kw_users`

```json
{
  "name": "kw_users",
  "description": "Minimal user records for analytics + personalization (avoid sensitive PII).",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "external_user_id": "TEXT",
    "role": "TEXT",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 3) `kw_persona_presets`

```json
{
  "name": "kw_persona_presets",
  "description": "Persona defaults: namespaces, filters, and citation/creative toggles.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "key": "TEXT UNIQUE NOT NULL",
    "display_name": "TEXT NOT NULL",
    "description": "TEXT",
    "default_namespaces": "JSONB NOT NULL",
    "default_filters": "JSONB",
    "require_citations_default": "BOOLEAN DEFAULT TRUE",
    "primary_sources_only_default": "BOOLEAN DEFAULT FALSE",
    "creative_mode_default": "BOOLEAN DEFAULT FALSE",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 4) `kw_chat_sessions`

```json
{
  "name": "kw_chat_sessions",
  "description": "Conversation threads with persona + model mode + toggle state.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "ainative_project_id": "UUID NOT NULL",
    "user_id": "UUID",
    "persona_key": "TEXT NOT NULL",
    "title": "TEXT",
    "model_mode": "TEXT NOT NULL",
    "toggles": "JSONB NOT NULL",
    "created_at": "TIMESTAMP DEFAULT NOW()",
    "updated_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 5) `kw_chat_messages`

```json
{
  "name": "kw_chat_messages",
  "description": "Chat messages (user/assistant/system) plus structured assistant payload + confidence.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "session_id": "UUID NOT NULL",
    "role": "TEXT NOT NULL",
    "content": "TEXT NOT NULL",
    "answer_json": "JSONB",
    "refusal_reason": "TEXT",
    "confidence": "NUMERIC",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 6) `kw_retrieval_runs`

```json
{
  "name": "kw_retrieval_runs",
  "description": "One retrieval execution for a user query (namespaces, filters, latency).",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "session_id": "UUID NOT NULL",
    "user_message_id": "UUID NOT NULL",
    "assistant_message_id": "UUID",
    "query": "TEXT NOT NULL",
    "top_k": "INT DEFAULT 8",
    "namespaces": "JSONB NOT NULL",
    "filters": "JSONB",
    "embedding_model": "TEXT NOT NULL DEFAULT 'BAAI/bge-small-en-v1.5'",
    "retrieval_latency_ms": "INT",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 7) `kw_retrieval_results`

```json
{
  "name": "kw_retrieval_results",
  "description": "Top retrieved chunks with score/rank + metadata snapshot (provenance, citation_label, canonical_url).",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "retrieval_run_id": "UUID NOT NULL",
    "namespace": "TEXT NOT NULL",
    "chunk_id": "TEXT NOT NULL",
    "doc_id": "TEXT NOT NULL",
    "score": "NUMERIC NOT NULL",
    "rank": "INT NOT NULL",
    "snippet": "TEXT",
    "metadata": "JSONB NOT NULL",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 8) `kw_citations_used`

```json
{
  "name": "kw_citations_used",
  "description": "Citations actually used in the assistant answer (subset of retrieval results).",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "assistant_message_id": "UUID NOT NULL",
    "retrieval_run_id": "UUID NOT NULL",
    "chunk_id": "TEXT NOT NULL",
    "canonical_url": "TEXT NOT NULL",
    "citation_label": "TEXT NOT NULL",
    "year": "INT",
    "source_org": "TEXT NOT NULL",
    "content_type": "TEXT NOT NULL",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 9) `kw_source_manifest`

```json
{
  "name": "kw_source_manifest",
  "description": "Row-wise representation of FIRST_FRUITS_MANIFEST.json for queryability + governance.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "job_id": "TEXT UNIQUE NOT NULL",
    "source_name": "TEXT NOT NULL",
    "source_type": "TEXT NOT NULL",
    "base_url": "TEXT NOT NULL",
    "access_method": "TEXT NOT NULL",
    "license": "TEXT NOT NULL",
    "priority": "TEXT NOT NULL",
    "default_namespace": "TEXT NOT NULL",
    "tags": "JSONB NOT NULL",
    "schedule": "TEXT NOT NULL",
    "query_templates": "JSONB NOT NULL",
    "created_at": "TIMESTAMP DEFAULT NOW()",
    "updated_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 10) `kw_ingestion_runs`

```json
{
  "name": "kw_ingestion_runs",
  "description": "Audit log for ingestion runs (discover, metadata_import, fulltext_expand, incremental).",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "job_id": "TEXT NOT NULL",
    "run_type": "TEXT NOT NULL",
    "status": "TEXT NOT NULL",
    "started_at": "TIMESTAMP DEFAULT NOW()",
    "ended_at": "TIMESTAMP",
    "docs_attempted": "INT DEFAULT 0",
    "docs_ingested": "INT DEFAULT 0",
    "chunks_ingested": "INT DEFAULT 0",
    "errors": "JSONB",
    "run_notes": "TEXT"
  }
}
```

---

## 11) `kw_corpus_collections`

```json
{
  "name": "kw_corpus_collections",
  "description": "Curated bundles (Civil Rights, Reconstruction, Black STEM, Black Press, Speeches+Letters).",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "key": "TEXT UNIQUE NOT NULL",
    "display_name": "TEXT NOT NULL",
    "description": "TEXT",
    "default_namespaces": "JSONB NOT NULL",
    "default_filters": "JSONB",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 12) `kw_collection_items`

```json
{
  "name": "kw_collection_items",
  "description": "Maps collections to docs/chunks with curation notes and priority ordering.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "collection_id": "UUID NOT NULL",
    "namespace": "TEXT NOT NULL",
    "doc_id": "TEXT NOT NULL",
    "chunk_id": "TEXT",
    "curation_notes": "TEXT",
    "priority": "INT DEFAULT 0",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 13) `kw_eval_questions`

```json
{
  "name": "kw_eval_questions",
  "description": "Evaluation question bank (per persona) with optional expected doc hints.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "persona_key": "TEXT NOT NULL",
    "question": "TEXT NOT NULL",
    "expected_namespace_hints": "JSONB",
    "expected_doc_ids": "JSONB",
    "require_citations": "BOOLEAN DEFAULT TRUE",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## 14) `kw_eval_runs`

```json
{
  "name": "kw_eval_runs",
  "description": "Evaluation run metadata (run name, optional commit SHA, model mode, summary).",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "run_name": "TEXT NOT NULL",
    "commit_sha": "TEXT",
    "model_mode": "TEXT NOT NULL",
    "created_at": "TIMESTAMP DEFAULT NOW()",
    "summary": "JSONB"
  }
}
```

---

## 15) `kw_eval_results`

```json
{
  "name": "kw_eval_results",
  "description": "Per-question eval results for citation coverage + retrieval hit rate.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "eval_run_id": "UUID NOT NULL",
    "eval_question_id": "UUID NOT NULL",
    "retrieval_run_id": "UUID",
    "citation_ok": "BOOLEAN NOT NULL",
    "retrieval_hit": "BOOLEAN NOT NULL",
    "notes": "TEXT",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

---

## (Optional) 16) `kw_answer_artifacts` (if you want structured creator outputs)

If you want to store generated speeches/curricula as first-class objects.

```json
{
  "name": "kw_answer_artifacts",
  "description": "Optional: stores structured generated outputs (speech, explainer, curriculum) with citations.",
  "schema": {
    "id": "UUID PRIMARY KEY",
    "session_id": "UUID NOT NULL",
    "assistant_message_id": "UUID",
    "artifact_type": "TEXT NOT NULL",
    "title": "TEXT",
    "content": "TEXT NOT NULL",
    "citations": "JSONB",
    "created_at": "TIMESTAMP DEFAULT NOW()"
  }
}
```

```
::contentReference[oaicite:0]{index=0}
```
