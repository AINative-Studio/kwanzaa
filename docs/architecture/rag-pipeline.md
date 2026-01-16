# RAG Pipeline Architecture

**Version:** 1.0.0
**Last Updated:** January 16, 2026
**Status:** Active

## Overview

The RAG (Retrieval-Augmented Generation) Pipeline is a comprehensive system for retrieving, ranking, and formatting contextual information for LLM-based question answering. It implements the complete flow from user query to formatted context, with transparent execution tracking and persona-driven configuration.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Pipeline Stages](#pipeline-stages)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Persona Configuration](#persona-configuration)
- [Integration Points](#integration-points)
- [Performance Considerations](#performance-considerations)
- [Usage Examples](#usage-examples)
- [Testing Strategy](#testing-strategy)
- [Future Enhancements](#future-enhancements)

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           RAG Pipeline                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐      ┌──────────────────┐                    │
│  │  Query Processing │ ───> │    Retrieval     │                    │
│  └──────────────────┘      └──────────────────┘                    │
│           │                          │                               │
│           │                          ▼                               │
│           │                 ┌──────────────────┐                    │
│           │                 │  Ranking/Rerank  │                    │
│           │                 └──────────────────┘                    │
│           │                          │                               │
│           ▼                          ▼                               │
│  ┌──────────────────┐      ┌──────────────────┐                    │
│  │ Context Injection │ <─── │   Statistics     │                    │
│  └──────────────────┘      └──────────────────┘                    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Stack

```
┌────────────────────────────────────────────────────────────────┐
│                    Application Layer                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              FastAPI Endpoints                            │ │
│  │  /api/v1/rag/query, /api/v1/rag/retrieve, etc.          │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    Service Layer                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │  RAGPipeline     │  │ EmbeddingService │  │ RerankService││
│  │  (Orchestration) │  │ (BAAI/bge-small) │  │ (CrossEncoder)││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    Data Layer                                  │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │  ZeroDBClient    │  │  PostgreSQL      │                  │
│  │  (Vector Store)  │  │  (Metadata)      │                  │
│  └──────────────────┘  └──────────────────┘                  │
└────────────────────────────────────────────────────────────────┘
```

## Pipeline Stages

### Stage 1: Query Processing

**Purpose:** Parse user query and apply persona-specific configuration

**Inputs:**
- User query text
- Persona key (educator, researcher, creator, builder)
- Optional: custom thresholds, namespaces, filters

**Processing:**
1. Validate and sanitize query text
2. Load persona configuration from settings
3. Apply persona-specific thresholds and settings
4. Override with request-specific parameters if provided
5. Determine target namespaces
6. Prepare metadata filters

**Outputs:**
- Cleaned query text
- Persona configuration dict
- Namespace list
- Metadata filters

**Code Location:** `backend/app/services/rag_pipeline.py::_process_query()`

### Stage 2: Retrieval

**Purpose:** Perform semantic search across ZeroDB vector namespaces

**Inputs:**
- Query text
- Namespaces to search
- Metadata filters
- Top-k results
- Similarity threshold

**Processing:**
1. Generate query embedding using EmbeddingService
2. For each namespace:
   - Execute vector similarity search
   - Apply metadata filters
   - Collect results with scores
3. Merge results from all namespaces
4. Sort by similarity score (descending)
5. Apply top-k limit
6. Assign ranks (1-indexed)

**Outputs:**
- List of RetrievalChunk objects
- Embedding generation time (ms)
- Search execution time (ms)

**Code Location:** `backend/app/services/rag_pipeline.py::_retrieve_chunks()`

### Stage 3: Ranking/Reranking

**Purpose:** Optionally improve ranking precision using cross-encoder

**Inputs:**
- Query text
- Retrieved chunks
- Top-n for final results
- Reranking enabled flag

**Processing:**
1. Check if reranking is enabled (persona default or override)
2. If enabled:
   - Prepare query-document pairs
   - Compute cross-encoder scores
   - Normalize scores to [0, 1] range
   - Combine semantic + rerank scores
   - Re-sort by final score
   - Update ranks
3. If disabled:
   - Return original chunks unchanged

**Outputs:**
- Reranked list of RetrievalChunk objects
- Reranking time (ms)

**Code Location:** `backend/app/services/rag_pipeline.py::_rerank_chunks()`
**Reranking Implementation:** `backend/app/services/reranker.py`

### Stage 4: Context Injection

**Purpose:** Format chunks into structured context string for LLM prompt

**Inputs:**
- Final ranked list of chunks
- Include context string flag

**Processing:**
1. Create markdown-formatted context header
2. For each chunk:
   - Format rank and citation label
   - Include relevance score
   - Add metadata (year, source_org, content_type, URL)
   - Include tags if present
   - Add content text
   - Add separator
3. Calculate approximate token count
4. Capture max chunk score

**Outputs:**
- ContextString object with:
  - Formatted context text
  - Number of chunks
  - Estimated token count
  - Max chunk score

**Code Location:** `backend/app/services/rag_pipeline.py::_format_context_string()`

### Stage 5: Retrieval Summary Capture

**Purpose:** Collect metrics and statistics for transparency

**Inputs:**
- All pipeline execution data
- Chunks, timings, configurations

**Processing:**
1. Count total retrieved/reranked/returned
2. Calculate score statistics (top, average)
3. Record namespaces searched
4. Capture filters applied
5. Aggregate timing metrics
6. Build statistics object

**Outputs:**
- RetrievalStatistics object with comprehensive metrics

**Code Location:** `backend/app/services/rag_pipeline.py::_build_statistics()`

## Component Details

### RAGPipeline Service

**File:** `backend/app/services/rag_pipeline.py`

**Responsibilities:**
- Orchestrate all pipeline stages
- Manage service dependencies
- Apply persona configurations
- Collect execution statistics
- Provide async context manager

**Key Methods:**
- `process(request)` - Main entry point for pipeline execution
- `_process_query()` - Query parsing and persona application
- `_retrieve_chunks()` - Vector search orchestration
- `_rerank_chunks()` - Optional reranking
- `_format_context_string()` - Context formatting
- `_build_statistics()` - Statistics collection

**Dependencies:**
- `EmbeddingService` - Query embedding generation
- `RerankingService` - Cross-encoder reranking
- `ZeroDBClient` - Vector database operations

### EmbeddingService

**File:** `backend/app/services/embedding.py`

**Model:** BAAI/bge-small-en-v1.5 (default)
**Dimensions:** 1536

**Capabilities:**
- Single text embedding generation
- Batch embedding generation
- Lazy model loading
- Dimension normalization

### RerankingService

**File:** `backend/app/services/reranker.py`

**Model:** cross-encoder/ms-marco-MiniLM-L-6-v2 (default)

**Capabilities:**
- Cross-encoder scoring
- Score normalization (sigmoid)
- Semantic + rerank score combination
- Configurable weights
- Top-n selection

### ZeroDBClient

**File:** `backend/app/db/zerodb.py`

**Capabilities:**
- Vector similarity search
- Metadata filtering
- Multi-namespace support
- Connection management
- Error handling

## Data Flow

### Request Flow Diagram

```
┌─────────────┐
│   Client    │
│   Request   │
└──────┬──────┘
       │
       │ RAGQueryRequest
       │ {query, persona, filters, ...}
       ▼
┌─────────────────────────────────────┐
│        RAGPipeline.process()        │
├─────────────────────────────────────┤
│                                     │
│  1. Query Processing                │
│     ├─ Parse query                  │
│     ├─ Load persona config          │
│     ├─ Apply defaults               │
│     └─ Prepare filters              │
│                                     │
│  2. Embedding Generation            │
│     └─ EmbeddingService             │
│        └─ [0.1, 0.2, ..., 0.9]     │
│                                     │
│  3. Vector Search                   │
│     └─ ZeroDBClient                 │
│        ├─ Namespace 1               │
│        ├─ Namespace 2               │
│        └─ Merge & Rank              │
│                                     │
│  4. Reranking (Optional)            │
│     └─ RerankingService             │
│        ├─ Cross-encoder scores      │
│        ├─ Combine scores            │
│        └─ Re-sort chunks            │
│                                     │
│  5. Context Formatting              │
│     └─ Format chunks as markdown    │
│                                     │
│  6. Statistics Collection           │
│     └─ Build RetrievalStatistics    │
│                                     │
└──────────────┬──────────────────────┘
               │
               │ RAGPipelineResponse
               │ {chunks, context, stats, ...}
               ▼
        ┌─────────────┐
        │   Client    │
        │   Response  │
        └─────────────┘
```

### Data Models

**RAGQueryRequest:**
```python
{
  "query": str,
  "persona_key": str,
  "namespaces": List[str],
  "filters": Dict[str, Any],
  "top_k": int,
  "similarity_threshold": float,
  "enable_reranking": bool,
  "rerank_top_n": int,
  "include_context_string": bool
}
```

**RAGPipelineResponse:**
```python
{
  "status": str,
  "query": str,
  "persona": str,
  "chunks": List[RetrievalChunk],
  "context_string": ContextString,
  "statistics": RetrievalStatistics,
  "persona_thresholds": PersonaThresholds,
  "reranking_enabled": bool,
  "embedding_model": str,
  "rerank_model": str
}
```

**RetrievalChunk:**
```python
{
  "chunk_id": str,
  "doc_id": str,
  "namespace": str,
  "content": str,
  "score": float,
  "rank": int,
  "citation_label": str,
  "canonical_url": str,
  "source_org": str,
  "year": int,
  "content_type": str,
  "license": str,
  "tags": List[str],
  "rerank_score": float,
  "final_score": float
}
```

## Persona Configuration

### Persona Settings

| Persona    | Similarity Threshold | Max Results | Min Results | Rerank | Namespaces |
|------------|---------------------|-------------|-------------|--------|------------|
| Educator   | 0.80                | 10          | 3           | Yes    | kwanzaa_primary_sources |
| Researcher | 0.75                | 20          | 5           | Yes    | kwanzaa_primary_sources, kwanzaa_black_press, kwanzaa_speeches_letters, kwanzaa_black_stem |
| Creator    | 0.65                | 15          | 2           | No     | kwanzaa_primary_sources, kwanzaa_speeches_letters, kwanzaa_teaching_kits |
| Builder    | 0.70                | 10          | 1           | No     | kwanzaa_dev_patterns |

### Persona Philosophy

**Educator:**
- High precision required (0.80 threshold)
- Primary sources only by default
- Reranking for best accuracy
- Moderate result count for focused responses

**Researcher:**
- Comprehensive coverage across multiple sources
- Lower threshold for broader recall
- Reranking for precision
- Highest result count for thorough analysis

**Creator:**
- Balance between precision and inspiration
- Lower threshold for creative connections
- No reranking (faster, more diverse)
- Multiple content types for inspiration

**Builder:**
- Technical focus on development patterns
- Moderate threshold for relevant code examples
- No reranking (faster iteration)
- Single specialized namespace

## Integration Points

### With Answer JSON Contract

The RAG pipeline output directly feeds into the `answer_json` contract:

**Mapping:**
- `RetrievalChunk` → `SourceReference` (answer_json.sources)
- `RetrievalStatistics` → `RetrievalSummarySection` (answer_json.retrieval_summary)
- `ContextString` → Injected into LLM prompt for generation

**Example Integration:**
```python
from app.services.rag_pipeline import RAGPipeline
from app.models.answer_json import AnswerJson, SourceReference, RetrievalResult

# Execute RAG pipeline
rag_response = await pipeline.process(rag_request)

# Convert chunks to sources for answer_json
sources = [
    SourceReference(
        citation_label=chunk.citation_label,
        canonical_url=chunk.canonical_url,
        source_org=chunk.source_org,
        year=chunk.year,
        content_type=chunk.content_type,
        license=chunk.license,
        namespace=chunk.namespace,
        doc_id=chunk.doc_id,
        chunk_id=chunk.chunk_id,
        relevance_score=chunk.final_score or chunk.score,
    )
    for chunk in rag_response.chunks
]

# Convert statistics to retrieval summary
retrieval_results = [
    RetrievalResult(
        rank=chunk.rank,
        score=chunk.final_score or chunk.score,
        snippet=chunk.content[:500],
        citation_label=chunk.citation_label,
        canonical_url=chunk.canonical_url,
        doc_id=chunk.doc_id,
        chunk_id=chunk.chunk_id,
        namespace=chunk.namespace,
    )
    for chunk in rag_response.chunks
]

# Build answer_json contract
answer_json = AnswerJson(
    version="kwanzaa.answer.v1",
    persona=rag_response.persona,
    sources=sources,
    retrieval_summary=RetrievalSummarySection(
        query=rag_response.query,
        top_k=len(rag_response.chunks),
        namespaces=rag_response.statistics.namespaces_searched,
        filters=rag_response.statistics.filters_applied or {},
        results=retrieval_results,
    ),
    # ... other fields
)
```

### With LLM Generation

The context string is injected into the LLM prompt:

```python
# Get formatted context
context = rag_response.context_string.formatted_context

# Build LLM prompt
system_prompt = f"""You are an AI assistant specializing in historical knowledge.
Use the following retrieved context to answer the user's question.
Always cite sources using the provided citation labels.

{context}
"""

# Generate response using LLM
llm_response = await llm_service.generate(
    system_prompt=system_prompt,
    user_prompt=rag_response.query,
)
```

## Performance Considerations

### Timing Breakdown

Typical latency for a complete pipeline execution:

| Stage              | Typical Time | Notes |
|-------------------|--------------|-------|
| Query Processing  | <5ms         | In-memory configuration lookup |
| Embedding Generation | 50-100ms  | CPU-bound, depends on model |
| Vector Search     | 100-300ms    | Network + ZeroDB processing |
| Reranking         | 50-150ms     | CPU-bound, depends on chunk count |
| Context Formatting | <10ms       | String manipulation |
| **Total**         | **250-600ms** | Varies by configuration |

### Optimization Strategies

**1. Caching:**
- Cache query embeddings (same query)
- Cache persona configurations
- Cache frequent search results

**2. Parallel Execution:**
- Search multiple namespaces in parallel
- Batch embedding generation when possible

**3. Resource Management:**
- Lazy load embedding models
- Lazy load cross-encoder models
- Connection pooling for ZeroDB

**4. Adaptive Reranking:**
- Only rerank for high-precision personas
- Skip reranking if few results
- Use lightweight rerankers for speed

### Scalability

**Horizontal Scaling:**
- Stateless pipeline design
- No shared mutable state
- Can run multiple instances behind load balancer

**Resource Requirements:**
- Embedding Model: ~500MB RAM
- Rerank Model: ~300MB RAM
- Per-request memory: ~100MB peak

## Usage Examples

### Basic Query

```python
from app.services.rag_pipeline import RAGPipeline
from app.models.retrieval import RAGQueryRequest

# Initialize pipeline
pipeline = RAGPipeline()

# Create request
request = RAGQueryRequest(
    query="What were the key principles of Kwanzaa?",
    persona_key="educator",
)

# Execute pipeline
response = await pipeline.process(request)

# Access results
print(f"Found {len(response.chunks)} relevant chunks")
print(f"Top score: {response.statistics.top_score:.3f}")
print(f"Total time: {response.statistics.total_time_ms}ms")

# Use context for LLM
context = response.context_string.formatted_context
```

### Advanced Query with Filters

```python
request = RAGQueryRequest(
    query="Civil rights legislation in the 1960s",
    persona_key="researcher",
    filters={
        "year_gte": 1960,
        "year_lte": 1969,
        "content_type": ["legal_document", "speech"],
    },
    top_k=20,
    enable_reranking=True,
    rerank_top_n=10,
)

response = await pipeline.process(request)
```

### Custom Namespaces

```python
request = RAGQueryRequest(
    query="Technical implementation of RAG",
    persona_key="builder",
    namespaces=["kwanzaa_dev_patterns", "kwanzaa_technical_docs"],
    similarity_threshold=0.75,
)

response = await pipeline.process(request)
```

### Using Context Manager

```python
async with RAGPipeline() as pipeline:
    response = await pipeline.process(request)
    # ZeroDB client automatically closed on exit
```

## Testing Strategy

### Test Coverage

The test suite (`backend/tests/test_rag_pipeline.py`) covers:

1. **Query Processing:**
   - Persona configuration application
   - Custom override handling
   - Query sanitization

2. **Retrieval:**
   - Successful retrieval
   - Multi-namespace search
   - Metadata filtering
   - Empty results handling

3. **Reranking:**
   - Score combination
   - Rank updates
   - Empty list handling

4. **Context Formatting:**
   - Metadata inclusion
   - Token estimation
   - Empty context handling

5. **Integration:**
   - End-to-end pipeline execution
   - Statistics collection
   - Error handling
   - Context manager behavior

### Running Tests

```bash
# Run all RAG pipeline tests
pytest backend/tests/test_rag_pipeline.py -v

# Run with coverage
pytest backend/tests/test_rag_pipeline.py --cov=app.services.rag_pipeline --cov-report=html

# Run specific test class
pytest backend/tests/test_rag_pipeline.py::TestPipelineIntegration -v
```

### Test Fixtures

The test suite uses mocked services to enable fast, isolated testing:
- `mock_embedding_service` - Returns fixed embeddings
- `mock_reranking_service` - Simulates reranking behavior
- `mock_zerodb_client` - Returns synthetic search results

## Future Enhancements

### Planned Features

1. **Hybrid Search:**
   - Combine semantic + keyword (BM25) search
   - Configurable weighting

2. **Query Expansion:**
   - Automatic query reformulation
   - Synonym expansion
   - Multi-query retrieval

3. **Result Caching:**
   - Redis-based result cache
   - Configurable TTL by persona
   - Cache invalidation strategy

4. **Advanced Reranking:**
   - Multiple reranking models
   - Model selection by persona
   - Ensemble reranking

5. **Retrieval Metrics:**
   - Precision/Recall tracking
   - Relevance feedback loop
   - A/B testing framework

6. **Context Window Management:**
   - Automatic chunking for large results
   - Token budget management
   - Intelligent truncation

### Research Directions

- **Adaptive Retrieval:** Dynamically adjust thresholds based on query complexity
- **Multi-hop Retrieval:** Follow citation chains for deeper context
- **Temporal Awareness:** Weight results by temporal relevance
- **Cross-lingual Retrieval:** Support multiple languages

## References

- [Semantic Search API Documentation](/Users/aideveloper/kwanzaa/docs/api/semantic-search-api.md)
- [Answer JSON Contract](/Users/aideveloper/kwanzaa/docs/answer_json_contract.md)
- [Persona Configuration](/Users/aideveloper/kwanzaa/backend/config/rag/personas.yaml)
- [Retrieval Configuration](/Users/aideveloper/kwanzaa/backend/config/rag/retrieval.yaml)

---

**Maintained by:** AINative Studio
**Project:** Kwanzaa - First Fruits for AI
**License:** Apache 2.0
