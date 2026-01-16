# Kwanzaa Semantic Search Backend

Backend API implementation for Kwanzaa's semantic search with provenance filters.

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your ZeroDB credentials
```

### 2. Run Server

```bash
# Development mode (with hot reload)
./start.sh --dev

# Production mode
./start.sh

# Run tests
./start.sh --test
```

### 3. Access API

- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── search.py         # Search API endpoints
│   ├── core/
│   │   ├── config.py                 # Configuration
│   │   └── errors.py                 # Error handling
│   ├── db/
│   │   └── zerodb.py                 # ZeroDB client
│   ├── models/
│   │   └── search.py                 # Pydantic models
│   ├── services/
│   │   ├── embedding.py              # Embedding service
│   │   └── search.py                 # Search service
│   └── main.py                       # FastAPI app
├── tests/
│   ├── conftest.py                   # Test fixtures
│   ├── test_models.py                # Model tests
│   ├── test_search_service.py        # Service tests
│   └── test_api_search.py            # API tests
├── requirements.txt                  # Dependencies
├── pyproject.toml                    # Tool configuration
└── .env.example                      # Environment template
```

## API Endpoints

### POST /api/v1/search/semantic

Perform semantic search with provenance filters.

**Request:**
```json
{
  "query": "What did the Civil Rights Act of 1964 prohibit?",
  "namespace": "kwanzaa_primary_sources",
  "filters": {
    "year_gte": 1960,
    "year_lte": 1970,
    "content_type": ["proclamation", "legal_document"]
  },
  "limit": 10,
  "threshold": 0.7
}
```

**Response:**
```json
{
  "status": "success",
  "query": {...},
  "results": [...],
  "total_results": 5,
  "search_metadata": {...}
}
```

### POST /api/v1/search/embed

Generate embedding for text (utility endpoint).

### GET /api/v1/search/namespaces

List available vector namespaces.

## Configuration

Key environment variables in `.env`:

```env
# Required
ZERODB_PROJECT_ID=your-project-id
ZERODB_API_KEY=your-api-key

# Optional
DEFAULT_SIMILARITY_THRESHOLD=0.7
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test markers
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
```

## Development

### Code Quality

```bash
# Format code
black app tests

# Lint
ruff app tests

# Type checking
mypy app
```

### Pre-commit Checks

Before committing:
1. Run tests: `pytest`
2. Check coverage: `pytest --cov=app --cov-fail-under=80`
3. Format code: `black app tests`
4. Lint: `ruff app tests`

## Features

- **Semantic Vector Search**: Natural language queries using sentence-transformers
- **Provenance Filtering**: Filter by year, source organization, content type, and tags
- **Persona-Driven Search**: Preset configurations for educator, researcher, creator, builder
- **Transparent Metadata**: Execution times, scores, and citation information
- **Comprehensive Error Handling**: Standardized error responses
- **Type Safety**: Full Pydantic validation
- **80%+ Test Coverage**: TDD approach with unit and integration tests

## Architecture

The implementation follows clean architecture principles:

1. **API Layer**: FastAPI endpoints with OpenAPI documentation
2. **Service Layer**: Business logic (SearchService, EmbeddingService)
3. **Data Layer**: ZeroDB client for vector operations
4. **Models**: Pydantic models for validation

## Persona Defaults

| Persona | Threshold | Default Namespace | Use Case |
|---------|-----------|-------------------|----------|
| educator | 0.80 | kwanzaa_primary_sources | Teaching, citations required |
| researcher | 0.75 | kwanzaa_primary_sources | Academic research |
| creator | 0.65 | All namespaces | Creative projects |
| builder | 0.70 | kwanzaa_dev_patterns | Technical development |

## Performance

Typical latencies:
- Embedding generation: 12-50ms (first request)
- Vector search: 20-100ms
- Total request: 50-200ms

## Security

- Input validation via Pydantic
- Rate limiting support
- CORS configuration
- JWT authentication ready (add middleware)

## Troubleshooting

**Slow first request**: Embedding model loads on first use (10-30s). Subsequent requests are fast.

**ZeroDB connection errors**: Verify API key and project ID in `.env`.

**Test failures**: Ensure test environment variables are set in `conftest.py`.

## Documentation

- [API Contract](../../docs/api/semantic-search-api.md)
- [Implementation Guide](../../docs/api/semantic-search-implementation.md)
- [Data Model](../../docs/architecture/datamodel.md)

## Support

- GitHub Issues: https://github.com/AINative-Studio/kwanzaa/issues
- Documentation: https://docs.kwanzaa.ainative.io

## License

Apache 2.0 - See [LICENSE](../LICENSE) for details.
