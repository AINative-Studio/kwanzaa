# Kwanzaa Semantic Search - Implementation Guide

## Overview

This document provides a comprehensive guide to the Kwanzaa semantic search implementation, including setup, usage, testing, and integration patterns.

## Architecture

The semantic search system follows a clean, layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Endpoints                     │
│                 (app/api/v1/endpoints)                   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                   Service Layer                          │
│          (SearchService, EmbeddingService)               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                   Data Layer                             │
│          (ZeroDBClient, PostgreSQL)                      │
└──────────────────────────────────────────────────────────┘
```

### Key Components

1. **API Layer** (`app/api/v1/endpoints/search.py`)
   - FastAPI endpoints for search operations
   - Request validation and error handling
   - Dependency injection for services

2. **Service Layer**
   - `SearchService`: Core search logic with persona defaults
   - `EmbeddingService`: Text-to-vector embedding generation

3. **Data Layer**
   - `ZeroDBClient`: Vector database operations
   - Metadata filtering and result processing

4. **Models** (`app/models/search.py`)
   - Pydantic models for request/response validation
   - Type-safe data structures

## Installation & Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+ (for metadata storage)
- ZeroDB account and API key

### 2. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# ZeroDB Settings (REQUIRED)
ZERODB_PROJECT_ID=your-project-id
ZERODB_API_KEY=your-api-key

# Optional: Customize search behavior
DEFAULT_SIMILARITY_THRESHOLD=0.7
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

### 4. Start the Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Usage

### Basic Semantic Search

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/search/semantic",
        json={
            "query": "What did the Civil Rights Act of 1964 prohibit?",
            "limit": 5,
            "threshold": 0.7
        }
    )
    results = response.json()
```

### Search with Provenance Filters

```python
response = await client.post(
    "http://localhost:8000/api/v1/search/semantic",
    json={
        "query": "civil rights legislation",
        "namespace": "kwanzaa_primary_sources",
        "filters": {
            "year_gte": 1960,
            "year_lte": 1970,
            "content_type": ["proclamation", "legal_document"],
            "source_org": ["National Archives", "Library of Congress"]
        },
        "limit": 10,
        "threshold": 0.75
    }
)
```

### Persona-Driven Search

```python
# Educator persona: Higher threshold, primary sources only
response = await client.post(
    "http://localhost:8000/api/v1/search/semantic",
    json={
        "query": "explain the voting rights act to students",
        "persona_key": "educator"
        # Automatically applies: threshold=0.80, namespace=kwanzaa_primary_sources
    }
)
```

### Working with Results

```python
results = response.json()

# Iterate through ranked results
for result in results["results"]:
    print(f"Rank {result['rank']}: {result['metadata']['citation_label']}")
    print(f"Score: {result['score']:.2f}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Source: {result['metadata']['canonical_url']}")
    print(f"Year: {result['metadata']['year']}")
    print("---")

# Access search metadata
print(f"Total results: {results['total_results']}")
print(f"Execution time: {results['search_metadata']['execution_time_ms']}ms")
```

## Testing

The implementation includes comprehensive tests following TDD principles.

### Run All Tests

```bash
cd backend
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/test_search_service.py
```

### Test Coverage Requirements

The project enforces a minimum of 80% test coverage:

```bash
pytest --cov=app --cov-fail-under=80
```

### Key Test Files

- `tests/test_models.py`: Model validation tests
- `tests/test_search_service.py`: Search service logic tests
- `tests/test_api_search.py`: API endpoint integration tests

## Integration Patterns

### 1. Direct Service Integration

For applications that want to embed search functionality:

```python
from app.services.search import SearchService
from app.services.embedding import EmbeddingService
from app.models.search import SearchRequest, ProvenanceFilters

# Initialize services
embedding_service = EmbeddingService()
search_service = SearchService(embedding_service)

# Create search request
request = SearchRequest(
    query="black scientists and inventors",
    namespace="kwanzaa_black_stem",
    filters=ProvenanceFilters(
        year_gte=1900,
        tags=["science", "biography"]
    ),
    limit=20
)

# Perform search (requires ZeroDB client)
from app.db.zerodb import ZeroDBClient

async with ZeroDBClient() as zerodb:
    response = await search_service.search(
        request=request,
        zerodb_search_func=zerodb.search_vectors
    )
```

### 2. RAG Pipeline Integration

The search service is designed to integrate with RAG orchestration:

```python
class RAGOrchestrator:
    def __init__(self):
        self.search_service = SearchService()
        self.zerodb_client = ZeroDBClient()

    async def retrieve_context(
        self,
        user_query: str,
        persona: str
    ) -> List[Dict]:
        """Retrieve relevant context for RAG."""
        request = SearchRequest(
            query=user_query,
            persona_key=persona,
            limit=8  # Top-K for context
        )

        response = await self.search_service.search(
            request=request,
            zerodb_search_func=self.zerodb_client.search_vectors
        )

        # Return formatted context
        return [
            {
                "content": result.content,
                "citation": result.metadata.citation_label,
                "url": result.metadata.canonical_url,
                "score": result.score
            }
            for result in response.results
        ]
```

### 3. Custom Persona Configuration

Extend persona configurations for your use case:

```python
from app.core.config import settings

# Add custom persona
settings.PERSONA_THRESHOLDS["historian"] = 0.78
settings.PERSONA_NAMESPACES["historian"] = [
    "kwanzaa_primary_sources",
    "kwanzaa_black_press",
    "kwanzaa_reconstruction"
]

# Use custom persona
request = SearchRequest(
    query="reconstruction era policies",
    persona_key="historian"
)
```

## Performance Considerations

### 1. Embedding Generation

- First request per query: ~12-50ms (depends on model)
- Subsequent requests: Cached (if implemented)
- Batch processing: Use `EmbeddingService.generate_batch_embeddings()`

### 2. Vector Search

- Typical latency: 20-100ms
- Depends on:
  - Namespace size
  - Filter complexity
  - Result limit

### 3. Optimization Tips

```python
# 1. Use appropriate limits
request = SearchRequest(
    query="...",
    limit=10  # Start small, only increase if needed
)

# 2. Pre-filter with metadata
request = SearchRequest(
    query="...",
    filters=ProvenanceFilters(
        year_gte=1960,  # Narrows search space
        content_type=["speech"]
    )
)

# 3. Adjust threshold based on use case
# Higher threshold = fewer, more relevant results
request = SearchRequest(
    query="...",
    threshold=0.80  # Stricter for education/research
)
```

## Error Handling

The API uses standardized error responses:

```python
try:
    response = await client.post("/api/v1/search/semantic", json={...})
    response.raise_for_status()
    results = response.json()
except httpx.HTTPStatusError as e:
    error = e.response.json()
    print(f"Error: {error['error_code']}")
    print(f"Message: {error['message']}")

    if 'details' in error:
        print(f"Details: {error['details']}")
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | ZeroDB unavailable |

## Monitoring & Logging

### Search Metadata

Every response includes execution metadata:

```python
metadata = results["search_metadata"]
print(f"Total time: {metadata['execution_time_ms']}ms")
print(f"Embedding time: {metadata['query_embedding_time_ms']}ms")
print(f"Search time: {metadata['search_time_ms']}ms")
print(f"Model: {metadata['embedding_model']}")
```

### Logging (Production)

In production, implement structured logging:

```python
import structlog

logger = structlog.get_logger()

# Log search operations
logger.info(
    "search_executed",
    query=request.query,
    namespace=request.namespace,
    results_count=len(response.results),
    execution_time_ms=response.search_metadata.execution_time_ms
)
```

## Security Considerations

### 1. Input Validation

All inputs are validated via Pydantic models:
- Query length: 1-1000 characters
- Limit: 1-100
- Threshold: 0.0-1.0
- Persona: Predefined enum

### 2. Rate Limiting

Configure rate limits in `.env`:

```env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

### 3. Authentication (Production)

Add authentication middleware:

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Security(security)):
    # Implement JWT verification
    token = credentials.credentials
    # Verify token and return user
    pass

# Apply to endpoints
@router.post("/semantic", dependencies=[Depends(verify_token)])
async def semantic_search(...):
    ...
```

## Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t kwanzaa-api .
docker run -p 8000:8000 --env-file .env kwanzaa-api
```

### Environment Variables (Production)

```env
# Production settings
DEBUG=False
LOG_LEVEL=INFO

# Security
SECRET_KEY=<strong-random-key>

# Performance
QUERY_CACHE_TTL_SECONDS=300
EMBEDDING_CACHE_TTL_SECONDS=3600

# Database connection pooling
DATABASE_MAX_CONNECTIONS=20
DATABASE_MIN_CONNECTIONS=5
```

## Troubleshooting

### Issue: Slow embedding generation

**Solution**: Model loads on first use. Consider:
- Pre-warming the service
- Using a smaller model for dev
- Implementing embedding caching

### Issue: ZeroDB connection errors

**Solution**: Verify:
- `ZERODB_API_KEY` is correct
- `ZERODB_PROJECT_ID` exists
- Network connectivity to ZeroDB API

### Issue: Low quality results

**Solution**: Adjust:
- Increase `threshold` for precision
- Add `filters` to narrow scope
- Use appropriate `persona_key`

### Issue: Tests failing

**Solution**:
- Ensure test dependencies installed: `pip install -r requirements.txt`
- Check environment variables set in tests
- Run with `-v` flag for details: `pytest -v`

## Next Steps

1. **Implement Authentication**: Add JWT-based auth for production
2. **Add Caching**: Implement Redis caching for embeddings and results
3. **Metrics Collection**: Add Prometheus metrics for monitoring
4. **Batch Operations**: Support batch search requests
5. **Advanced Filtering**: Add full-text search integration
6. **Result Ranking**: Implement custom ranking algorithms

## Support

- GitHub Issues: https://github.com/AINative-Studio/kwanzaa/issues
- Documentation: https://docs.kwanzaa.ainative.io
- API Status: https://status.kwanzaa.ainative.io
