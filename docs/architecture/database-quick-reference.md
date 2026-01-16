# Database Schema Quick Reference

## Table Summary

| Table | Purpose | Key Fields | Rows (Est.) |
|-------|---------|------------|-------------|
| **sources** | Source manifest registry | source_name, canonical_url, license | ~50-100 |
| **documents** | Document-level provenance | canonical_url, year, content_type | ~10,000+ |
| **chunks** | Chunk metadata + vector links | chunk_text, namespace, vector_id | ~100,000+ |
| **collections** | Namespace configuration | collection_name, default_threshold | 6 |
| **ingestion_logs** | Ingestion audit trail | source_name, status, started_at | ~1,000+ |
| **evaluations** | Evaluation metrics | eval_type, metrics, run_date | ~500+ |

## Required Provenance Fields

Every document and chunk MUST have:
- `canonical_url`: Source URL
- `license`: License information
- `year`: Year of publication
- `source_org`: Publishing organization
- `content_type`: Type of content
- `citation_label`: Human-readable citation (chunks only)

## 6-Namespace Strategy

| Namespace | Content Type | Example |
|-----------|--------------|---------|
| `founding` | Founding documents | Declaration of Independence, Constitution |
| `core_texts` | Core texts & manifestos | Du Bois essays, manifestos |
| `speeches` | Speeches & addresses | MLK speeches, inaugural addresses |
| `letters` | Letters & correspondence | Baldwin letters, personal correspondence |
| `multimedia` | Multimedia content | Audio/video transcripts, images |
| `supplemental` | Supplemental materials | Context documents, analysis |

## Common Queries

### Get all documents from a source
```python
from app.db import Document

documents = await session.execute(
    select(Document).where(Document.source_id == source_id)
)
```

### Get chunks for a document
```python
from app.db import Chunk

chunks = await session.execute(
    select(Chunk)
    .where(Chunk.document_id == document_id)
    .order_by(Chunk.chunk_index)
)
```

### Get chunks by namespace
```python
chunks = await session.execute(
    select(Chunk).where(Chunk.namespace == "speeches")
)
```

### Track ingestion run
```python
from app.db import IngestionLog

log = IngestionLog(
    source_name="Library of Congress",
    status="running"
)
session.add(log)
await session.commit()
```

### Record evaluation
```python
from app.db import Evaluation

eval_result = Evaluation(
    eval_type="citation_coverage",
    metrics={"accuracy": 0.95, "precision": 0.92},
    test_cases=100,
    passed=95,
    failed=5
)
session.add(eval_result)
await session.commit()
```

## Cascade Delete Behavior

- **Delete Source** → Deletes all documents and chunks
- **Delete Document** → Deletes all chunks
- **Delete Chunk** → Vector in ZeroDB should be deleted separately

## Validation Rules

### sources
- `priority`: 0-5 (0=lowest, 5=highest)
- `source_type`: One of: government, press, archive, academic, museum, community, other
- `access_method`: One of: api, scrape, manual, download

### documents
- `year`: 1600-2100
- `content_type`: One of: speech, letter, document, article, book, interview, multimedia, other
- `canonical_url`: Must be unique

### chunks
- `chunk_index`: >= 0
- `namespace`: One of: founding, core_texts, speeches, letters, multimedia, supplemental
- `(document_id, chunk_index)`: Must be unique

### collections
- `default_threshold`: 0.0-1.0 (if provided)

### ingestion_logs
- `status`: One of: running, completed, failed, partial
- `documents_processed`: >= 0 (if provided)
- `chunks_created`: >= 0 (if provided)

### evaluations
- `eval_type`: One of: citation_coverage, refusal_accuracy, hallucination, retrieval_quality, answer_quality, other
- `test_cases`, `passed`, `failed`: >= 0
- `passed + failed <= test_cases`

## Database Commands

### Apply migrations
```bash
cd backend
alembic upgrade head
```

### Create new migration
```bash
cd backend
alembic revision --autogenerate -m "add new field"
```

### Rollback migration
```bash
cd backend
alembic downgrade -1
```

### Check current version
```bash
cd backend
alembic current
```

### View migration history
```bash
cd backend
alembic history
```

## Connection String Format

PostgreSQL connection via asyncpg:
```
postgresql+asyncpg://user:password@host:port/database
```

Example (local):
```
postgresql+asyncpg://localhost/kwanzaa
```

## Key Relationships

```
sources (1) ←→ (N) documents (1) ←→ (N) chunks
                                          ↓
                                    ZeroDB vectors
                                    (via vector_id)
```

## File Locations

- Models: `backend/app/db/models.py`
- Base: `backend/app/db/base.py`
- Migrations: `backend/alembic/versions/`
- Config: `backend/alembic.ini`
- Docs: `docs/architecture/database-schema.md`
