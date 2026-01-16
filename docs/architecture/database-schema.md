# Kwanzaa Database Schema

## Overview

The Kwanzaa RAG system uses a hybrid architecture combining:
- **PostgreSQL** for structured relational data (documents, chunks metadata, sources, etc.)
- **ZeroDB** for vector embeddings and semantic search

This document describes the PostgreSQL schema comprising 6 core tables that support provenance tracking, ingestion auditing, and evaluation metrics.

## Design Principles

1. **Provenance-First (Imani - Faith)**: All content includes complete source attribution
2. **Namespace Strategy**: Content organized into 6 namespaces (founding, core_texts, speeches, letters, multimedia, supplemental)
3. **Audit Trail (Ujima - Collective Work)**: Complete tracking of ingestion runs and evaluation results
4. **Referential Integrity**: Foreign keys enforce relationships between tables
5. **Type Safety**: Check constraints ensure data validity

## Core Tables

### 1. sources

**Purpose**: Source manifest registry tracking all data sources with licensing and access information.

**Schema**:
```sql
CREATE TABLE sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(255) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('government', 'press', 'archive', 'academic', 'museum', 'community', 'other')),
    canonical_url VARCHAR(500) NOT NULL,
    license VARCHAR(255) NOT NULL,
    access_method VARCHAR(50) NOT NULL CHECK (access_method IN ('api', 'scrape', 'manual', 'download')),
    priority INTEGER CHECK (priority >= 0 AND priority <= 5),
    tags TEXT[],
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_sources_source_name ON sources(source_name);
CREATE INDEX ix_sources_source_type ON sources(source_type);
CREATE INDEX ix_sources_created_at ON sources(created_at);
```

**Key Fields**:
- `source_id`: Auto-generated UUID primary key
- `source_name`: Human-readable source name (unique)
- `source_type`: Categorization of source organization
- `canonical_url`: Primary URL for the source
- `license`: License governing the source content
- `access_method`: How data is accessed (api, scrape, manual, download)
- `priority`: Priority level for ingestion (0=lowest, 5=highest)
- `tags`: Array of categorization tags

**Relationships**:
- One-to-many with `documents` (one source has many documents)

---

### 2. documents

**Purpose**: Document-level records with complete provenance metadata.

**Schema**:
```sql
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES sources(source_id) ON DELETE CASCADE,
    canonical_url VARCHAR(500) NOT NULL UNIQUE,
    source_org VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1600 AND year <= 2100),
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('speech', 'letter', 'document', 'article', 'book', 'interview', 'multimedia', 'other')),
    license VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    full_text TEXT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_documents_source_id ON documents(source_id);
CREATE INDEX ix_documents_canonical_url ON documents(canonical_url);
CREATE INDEX ix_documents_source_org ON documents(source_org);
CREATE INDEX ix_documents_year ON documents(year);
CREATE INDEX ix_documents_content_type ON documents(content_type);
CREATE INDEX ix_documents_created_at ON documents(created_at);
CREATE INDEX idx_document_year_content ON documents(year, content_type);
```

**Key Fields**:
- `document_id`: Auto-generated UUID primary key
- `source_id`: Foreign key to sources table
- `canonical_url`: Unique URL for this document (provenance required)
- `source_org`: Organization that published the document (provenance required)
- `year`: Year of publication (provenance required)
- `content_type`: Type of content (provenance required)
- `license`: License governing this document (provenance required)
- `title`: Document title
- `full_text`: Complete document text
- `metadata`: Additional metadata fields (JSONB)

**Provenance Requirements**:
All documents MUST have: `canonical_url`, `source_org`, `year`, `content_type`, `license`

**Relationships**:
- Many-to-one with `sources` (many documents belong to one source)
- One-to-many with `chunks` (one document has many chunks)

---

### 3. chunks

**Purpose**: Chunk-level records linked to vector embeddings in ZeroDB.

**Schema**:
```sql
CREATE TABLE chunks (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    chunk_text TEXT NOT NULL,
    citation_label VARCHAR(500) NOT NULL,
    namespace VARCHAR(100) NOT NULL CHECK (namespace IN ('founding', 'core_texts', 'speeches', 'letters', 'multimedia', 'supplemental')),
    vector_id VARCHAR(255),
    retrieved_at TIMESTAMP,
    metadata JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX ix_chunks_document_id ON chunks(document_id);
CREATE INDEX ix_chunks_namespace ON chunks(namespace);
CREATE INDEX ix_chunks_vector_id ON chunks(vector_id);
CREATE INDEX ix_chunks_created_at ON chunks(created_at);
CREATE INDEX idx_chunk_document_index ON chunks(document_id, chunk_index);
CREATE INDEX idx_chunk_namespace_vector ON chunks(namespace, vector_id);
```

**Key Fields**:
- `chunk_id`: Auto-generated UUID primary key
- `document_id`: Foreign key to documents table
- `chunk_index`: Sequential index of chunk within document
- `chunk_text`: The actual text content of the chunk
- `citation_label`: Human-readable citation (provenance required)
- `namespace`: Namespace categorization (one of 6 namespaces)
- `vector_id`: Reference to vector embedding in ZeroDB vector store
- `retrieved_at`: Timestamp when chunk was last retrieved/accessed
- `metadata`: Complete provenance metadata (JSONB)

**6-Namespace Strategy**:
- `founding`: Founding documents (Declaration, Constitution, etc.)
- `core_texts`: Core texts and manifestos
- `speeches`: Speeches and public addresses
- `letters`: Letters and correspondence
- `multimedia`: Multimedia content
- `supplemental`: Supplemental materials

**Relationships**:
- Many-to-one with `documents` (many chunks belong to one document)
- Logical link to ZeroDB vectors via `vector_id`

---

### 4. collections

**Purpose**: Collections and namespace groupings with configuration.

**Schema**:
```sql
CREATE TABLE collections (
    collection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    default_threshold FLOAT CHECK (default_threshold IS NULL OR (default_threshold >= 0.0 AND default_threshold <= 1.0)),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_collections_collection_name ON collections(collection_name);
CREATE INDEX ix_collections_created_at ON collections(created_at);
```

**Key Fields**:
- `collection_id`: Auto-generated UUID primary key
- `collection_name`: Namespace name (unique)
- `description`: Detailed description of the collection
- `default_threshold`: Default similarity threshold for semantic search (0.0 to 1.0)

**Purpose**: Configure the 6-namespace strategy with default search thresholds.

---

### 5. ingestion_logs

**Purpose**: Track ingestion jobs with run metrics, error tracking, and status monitoring.

**Schema**:
```sql
CREATE TABLE ingestion_logs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(255) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(50) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'partial')),
    completed_at TIMESTAMP,
    documents_processed INTEGER CHECK (documents_processed IS NULL OR documents_processed >= 0),
    chunks_created INTEGER CHECK (chunks_created IS NULL OR chunks_created >= 0),
    errors JSONB,
    metadata JSONB,
);

CREATE INDEX ix_ingestion_logs_source_name ON ingestion_logs(source_name);
CREATE INDEX ix_ingestion_logs_started_at ON ingestion_logs(started_at);
CREATE INDEX ix_ingestion_logs_status ON ingestion_logs(status);
CREATE INDEX idx_ingestion_source_status ON ingestion_logs(source_name, status);
CREATE INDEX idx_ingestion_started ON ingestion_logs(started_at DESC);
```

**Key Fields**:
- `run_id`: Auto-generated UUID primary key
- `source_name`: Name of the source being ingested
- `started_at`: Timestamp when ingestion started
- `status`: Current status (running, completed, failed, partial)
- `completed_at`: Timestamp when ingestion completed
- `documents_processed`: Count of documents successfully processed
- `chunks_created`: Count of chunks created from documents
- `errors`: Array of error objects (JSONB)
- `metadata`: Additional run metadata and configuration (JSONB)

**Purpose**: Provide complete audit trail for ingestion operations (Ujima principle).

---

### 6. evaluations

**Purpose**: Evaluation results and metrics for testing RAG quality.

**Schema**:
```sql
CREATE TABLE evaluations (
    eval_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    eval_type VARCHAR(100) NOT NULL CHECK (eval_type IN ('citation_coverage', 'refusal_accuracy', 'hallucination', 'retrieval_quality', 'answer_quality', 'other')),
    run_date TIMESTAMP NOT NULL DEFAULT NOW(),
    metrics JSONB NOT NULL,
    test_cases INTEGER NOT NULL CHECK (test_cases >= 0),
    passed INTEGER NOT NULL CHECK (passed >= 0),
    failed INTEGER NOT NULL CHECK (failed >= 0),
    model_name VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (passed + failed <= test_cases)
);

CREATE INDEX ix_evaluations_eval_type ON evaluations(eval_type);
CREATE INDEX ix_evaluations_run_date ON evaluations(run_date);
CREATE INDEX idx_evaluation_type_date ON evaluations(eval_type, run_date);
```

**Key Fields**:
- `eval_id`: Auto-generated UUID primary key
- `eval_type`: Type of evaluation (citation_coverage, refusal_accuracy, hallucination, etc.)
- `run_date`: Timestamp when evaluation was run
- `metrics`: Evaluation metrics (accuracy, precision, recall, F1, etc.) stored as JSONB
- `test_cases`: Total number of test cases
- `passed`: Number of test cases that passed
- `failed`: Number of test cases that failed
- `model_name`: Model being evaluated (optional)
- `notes`: Additional notes or observations

**Evaluation Types**:
- `citation_coverage`: Are citations being provided when required?
- `refusal_accuracy`: Is the model refusing appropriately when no sources exist?
- `hallucination`: Is the model generating unsupported claims?
- `retrieval_quality`: Are the right chunks being retrieved?
- `answer_quality`: Overall answer quality assessment
- `other`: Custom evaluation types

---

## Entity Relationship Diagram

```
┌──────────────┐
│   sources    │
└──────┬───────┘
       │ 1
       │
       │ N
┌──────▼───────┐
│  documents   │
└──────┬───────┘
       │ 1
       │
       │ N
┌──────▼───────┐        ┌─────────────────┐
│    chunks    │◄──────►│ ZeroDB Vectors  │
└──────────────┘        └─────────────────┘
                         (via vector_id)

┌────────────────┐
│  collections   │  (namespace configuration)
└────────────────┘

┌─────────────────┐
│ ingestion_logs  │  (audit trail)
└─────────────────┘

┌──────────────┐
│ evaluations  │  (metrics)
└──────────────┘
```

## Data Flow

### Ingestion Flow
1. **Register Source**: Create entry in `sources` table
2. **Ingest Document**: Create entry in `documents` table with full provenance
3. **Chunk Document**: Split into chunks, create entries in `chunks` table
4. **Generate Embeddings**: Create vector embeddings and store in ZeroDB
5. **Link Vectors**: Update `chunks.vector_id` with ZeroDB vector ID
6. **Log Run**: Record ingestion metrics in `ingestion_logs`

### Retrieval Flow
1. **Query**: User submits natural language query
2. **Embed**: Generate query embedding
3. **Search ZeroDB**: Semantic search in ZeroDB vector store
4. **Fetch Metadata**: Retrieve chunk metadata from PostgreSQL using `vector_id`
5. **Return Results**: Combine vector search results with provenance metadata
6. **Log Retrieval**: Update `chunks.retrieved_at` timestamp

### Evaluation Flow
1. **Run Tests**: Execute evaluation test cases
2. **Collect Metrics**: Calculate accuracy, precision, recall, etc.
3. **Store Results**: Save to `evaluations` table with metrics as JSONB

## Indexes

### Performance-Critical Indexes
- `documents(source_id)`: Fast lookup of documents by source
- `documents(year, content_type)`: Composite index for filtered queries
- `chunks(document_id, chunk_index)`: Fast chunk lookup and ordering
- `chunks(namespace, vector_id)`: Fast namespace-filtered retrieval
- `ingestion_logs(source_name, status)`: Fast audit queries

### Unique Constraints
- `sources.source_name`: Ensure unique source names
- `documents.canonical_url`: Ensure unique document URLs
- `chunks(document_id, chunk_index)`: Ensure no duplicate chunks
- `collections.collection_name`: Ensure unique collection names

## Database Management

### Migrations
Managed via Alembic:
```bash
# Apply migrations
cd backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# View history
alembic history
```

### Backup Strategy
1. **Regular Backups**: Automated daily backups of PostgreSQL
2. **Point-in-Time Recovery**: Enable WAL archiving
3. **ZeroDB Sync**: Vector embeddings backed up separately via ZeroDB

### Monitoring
- **Table Sizes**: Monitor growth of `documents` and `chunks` tables
- **Index Usage**: Track index hit rates for optimization
- **Query Performance**: Log slow queries > 1000ms
- **Constraint Violations**: Alert on failed inserts due to constraints

## Implementation Files

- **Models**: `/Users/aideveloper/kwanzaa/backend/app/db/models.py`
- **Base**: `/Users/aideveloper/kwanzaa/backend/app/db/base.py`
- **Migration**: `/Users/aideveloper/kwanzaa/backend/alembic/versions/2026_01_16_1500-001_initial_schema.py`
- **Alembic Config**: `/Users/aideveloper/kwanzaa/backend/alembic.ini`

## Next Steps

1. **Apply Migration**: Run `alembic upgrade head` to create tables
2. **Seed Collections**: Insert 6 namespace entries into `collections`
3. **Register Sources**: Add initial sources to `sources` table
4. **Implement Services**: Create service layer for CRUD operations
5. **Add Tests**: Write tests for models and database operations
