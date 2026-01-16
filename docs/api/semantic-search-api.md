# Kwanzaa Semantic Search API Contract

## Overview

The Semantic Search API enables vector-based semantic search across the Kwanzaa corpus with comprehensive provenance filtering. This API is designed to support persona-driven queries and integrate with the RAG orchestration pipeline.

## Base URL

```
/api/v1/search
```

## Authentication

All requests require a valid API key or JWT token in the Authorization header:

```
Authorization: Bearer {token}
```

## Endpoints

### 1. POST /api/v1/search/semantic

Perform semantic search with provenance filters.

#### Request

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer {token}`

**Body:**

```json
{
  "query": "string (required, 1-1000 chars)",
  "namespace": "string (optional, default: 'default')",
  "filters": {
    "year": "integer (optional, single year)",
    "year_gte": "integer (optional, year greater than or equal)",
    "year_lte": "integer (optional, year less than or equal)",
    "source_org": "array[string] (optional, filter by source organizations)",
    "content_type": "array[string] (optional, filter by content types)",
    "tags": "array[string] (optional, filter by tags)"
  },
  "limit": "integer (optional, default: 10, max: 100)",
  "threshold": "float (optional, default: 0.7, range: 0.0-1.0)",
  "include_embeddings": "boolean (optional, default: false)",
  "persona_key": "string (optional, one of: builder, educator, creator, researcher)"
}
```

**Field Descriptions:**

- `query`: The search query text (natural language)
- `namespace`: Vector namespace to search within (e.g., "kwanzaa_primary_sources")
- `filters`: Metadata filters for provenance-based filtering
  - `year`: Exact year match (e.g., 1964)
  - `year_gte`: Minimum year (inclusive)
  - `year_lte`: Maximum year (inclusive)
  - `source_org`: List of source organizations (e.g., ["National Archives", "Library of Congress"])
  - `content_type`: List of content types (e.g., ["speech", "letter", "proclamation"])
  - `tags`: List of tags for additional filtering
- `limit`: Maximum number of results to return
- `threshold`: Minimum similarity score (0.0 to 1.0)
- `include_embeddings`: Whether to include vector embeddings in response
- `persona_key`: Apply persona-specific defaults and thresholds

**Persona-Specific Behavior:**

When `persona_key` is specified, the following defaults apply:

| Persona | Default Threshold | Default Namespaces | Notes |
|---------|------------------|-------------------|-------|
| educator | 0.80 | kwanzaa_primary_sources | Stricter threshold, citation-focused |
| researcher | 0.75 | kwanzaa_primary_sources, kwanzaa_black_press | Balanced precision/recall |
| creator | 0.65 | All namespaces | More creative, exploratory |
| builder | 0.70 | kwanzaa_dev_patterns | Technical focus |

#### Response

**Success (200 OK):**

```json
{
  "status": "success",
  "query": {
    "text": "What did the Civil Rights Act of 1964 prohibit?",
    "namespace": "kwanzaa_primary_sources",
    "filters_applied": {
      "year_gte": 1960,
      "year_lte": 1970,
      "content_type": ["proclamation"]
    },
    "limit": 10,
    "threshold": 0.7
  },
  "results": [
    {
      "rank": 1,
      "score": 0.93,
      "chunk_id": "nara_cra_1964::chunk::3",
      "doc_id": "nara_cra_1964",
      "namespace": "kwanzaa_primary_sources",
      "content": "An Act to enforce the constitutional right to vote...",
      "metadata": {
        "citation_label": "National Archives (1964) — Civil Rights Act",
        "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
        "source_org": "National Archives",
        "year": 1964,
        "content_type": "proclamation",
        "license": "Public Domain",
        "tags": ["civil_rights", "legislation"]
      }
    }
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

**Error Responses:**

**400 Bad Request:**
```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "message": "Query text is required and must be between 1 and 1000 characters",
  "details": {
    "field": "query",
    "constraint": "length"
  }
}
```

**401 Unauthorized:**
```json
{
  "status": "error",
  "error_code": "UNAUTHORIZED",
  "message": "Invalid or missing authentication token"
}
```

**429 Too Many Requests:**
```json
{
  "status": "error",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Please try again in 60 seconds.",
  "details": {
    "retry_after_seconds": 60
  }
}
```

**500 Internal Server Error:**
```json
{
  "status": "error",
  "error_code": "INTERNAL_ERROR",
  "message": "An internal error occurred while processing your request",
  "request_id": "uuid-here"
}
```

**503 Service Unavailable:**
```json
{
  "status": "error",
  "error_code": "SERVICE_UNAVAILABLE",
  "message": "ZeroDB service is temporarily unavailable"
}
```

### 2. POST /api/v1/search/embed

Generate embeddings for text (utility endpoint for testing/debugging).

#### Request

```json
{
  "text": "string (required, 1-10000 chars)",
  "model": "string (optional, default: BAAI/bge-small-en-v1.5)"
}
```

#### Response

**Success (200 OK):**

```json
{
  "status": "success",
  "text": "What did the Civil Rights Act of 1964 prohibit?",
  "embedding": [0.123, -0.456, ...],
  "dimensions": 1536,
  "model": "BAAI/bge-small-en-v1.5"
}
```

### 3. GET /api/v1/search/namespaces

List available namespaces and their metadata.

#### Response

**Success (200 OK):**

```json
{
  "status": "success",
  "namespaces": [
    {
      "name": "kwanzaa_primary_sources",
      "display_name": "Primary Sources",
      "description": "Primary historical documents and government archives",
      "document_count": 1250,
      "chunk_count": 8940,
      "content_types": ["speech", "letter", "proclamation", "legal_document"],
      "year_range": [1863, 2025],
      "source_orgs": ["National Archives", "Library of Congress"]
    }
  ]
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_REQUEST | 400 | Request validation failed |
| MISSING_FIELD | 400 | Required field is missing |
| INVALID_FIELD_VALUE | 400 | Field value is invalid |
| UNAUTHORIZED | 401 | Authentication failed |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Internal server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |

## Rate Limiting

- **Rate Limit:** 60 requests per minute per API key
- **Burst Limit:** 10 requests per second
- Rate limit headers are included in all responses:
  - `X-RateLimit-Limit`: Total requests allowed per minute
  - `X-RateLimit-Remaining`: Requests remaining in current window
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## Data Models

### SearchRequest

```typescript
interface SearchRequest {
  query: string;
  namespace?: string;
  filters?: ProvenanceFilters;
  limit?: number;
  threshold?: number;
  include_embeddings?: boolean;
  persona_key?: PersonaKey;
}
```

### ProvenanceFilters

```typescript
interface ProvenanceFilters {
  year?: number;
  year_gte?: number;
  year_lte?: number;
  source_org?: string[];
  content_type?: string[];
  tags?: string[];
}
```

### SearchResult

```typescript
interface SearchResult {
  rank: number;
  score: number;
  chunk_id: string;
  doc_id: string;
  namespace: string;
  content: string;
  metadata: ChunkMetadata;
  embedding?: number[];
}
```

### ChunkMetadata

```typescript
interface ChunkMetadata {
  citation_label: string;
  canonical_url: string;
  source_org: string;
  year: number;
  content_type: string;
  license: string;
  tags: string[];
  [key: string]: any;
}
```

## Usage Examples

### Example 1: Basic Semantic Search

```bash
curl -X POST https://api.kwanzaa.ainative.io/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "query": "What did the Civil Rights Act of 1964 prohibit?",
    "namespace": "kwanzaa_primary_sources",
    "limit": 5,
    "threshold": 0.7
  }'
```

### Example 2: Search with Year Range Filter

```bash
curl -X POST https://api.kwanzaa.ainative.io/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "query": "civil rights legislation",
    "namespace": "kwanzaa_primary_sources",
    "filters": {
      "year_gte": 1960,
      "year_lte": 1970,
      "content_type": ["proclamation", "legal_document"]
    },
    "limit": 10,
    "threshold": 0.75
  }'
```

### Example 3: Persona-Specific Search

```bash
curl -X POST https://api.kwanzaa.ainative.io/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "query": "explain the voting rights act to students",
    "persona_key": "educator",
    "filters": {
      "source_org": ["National Archives", "Library of Congress"]
    }
  }'
```

### Example 4: Multi-Tag Filter Search

```bash
curl -X POST https://api.kwanzaa.ainative.io/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "query": "black scientists and inventors",
    "namespace": "kwanzaa_black_stem",
    "filters": {
      "tags": ["science", "biography"],
      "year_gte": 1900
    },
    "limit": 20,
    "threshold": 0.65
  }'
```

## Python SDK Example

```python
from kwanzaa_client import KwanzaaClient

client = KwanzaaClient(api_key="YOUR_API_KEY")

# Basic search
results = client.search.semantic(
    query="What did the Civil Rights Act of 1964 prohibit?",
    namespace="kwanzaa_primary_sources",
    limit=5
)

# Search with filters
results = client.search.semantic(
    query="civil rights legislation",
    namespace="kwanzaa_primary_sources",
    filters={
        "year_gte": 1960,
        "year_lte": 1970,
        "content_type": ["proclamation", "legal_document"]
    },
    threshold=0.75
)

# Persona-specific search
results = client.search.semantic(
    query="explain the voting rights act to students",
    persona_key="educator"
)

for result in results:
    print(f"{result.rank}. [{result.score:.2f}] {result.metadata.citation_label}")
    print(f"   {result.content[:200]}...")
```

## Performance Considerations

1. **Query Optimization:**
   - Keep queries focused and specific (1-50 words optimal)
   - Use filters to narrow search space before vector search
   - Consider caching for frequently used queries

2. **Batch Operations:**
   - For multiple searches, use batch endpoints when available
   - Implement client-side connection pooling

3. **Result Set Size:**
   - Default limit of 10 results balances performance and utility
   - Larger result sets (50+) may have increased latency
   - Use pagination for exploring large result sets

4. **Embedding Generation:**
   - Embeddings are cached server-side for common queries
   - Custom embedding models may have higher latency

## Security Considerations

1. **Input Validation:**
   - All inputs are sanitized and validated
   - Maximum query length prevents abuse
   - Filters are validated against schema

2. **Authorization:**
   - Row-level security based on project access
   - Namespace permissions enforced
   - Audit logging for all searches

3. **Rate Limiting:**
   - Per-key rate limiting prevents abuse
   - Adaptive rate limiting during high load
   - DDoS protection at infrastructure layer

4. **Data Privacy:**
   - No PII stored in embeddings or metadata
   - Search queries are not retained beyond audit logs
   - Results filtered by user permissions

## Versioning

This API follows semantic versioning. The current version is `v1`.

Breaking changes will be announced 90 days in advance and will result in a new API version (e.g., `v2`).

## Support

For API support, please:
- Check the documentation at https://docs.kwanzaa.ainative.io
- File issues at https://github.com/AINative-Studio/kwanzaa/issues
- Contact support at support@ainative.io
