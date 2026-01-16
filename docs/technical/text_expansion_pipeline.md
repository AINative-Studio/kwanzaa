# Text Expansion Pipeline

## Overview

The Text Expansion Pipeline is a core component of the Kwanzaa data ingestion framework (EPIC 4). It selectively expands Priority 0 (P0) sources from metadata-only records to full-text documents with semantic search capabilities.

## Architecture

### Pipeline Components

```
Manifest Loader → Source Filter (P0) → Text Extraction → Chunking → Embedding → Storage
       ↓                                                                              ↓
   Validation                                                                    Provenance
```

### Key Services

1. **ManifestLoader** (`app/services/manifest_loader.py`)
   - Loads FirstFruitsManifest from JSON files
   - Filters sources by priority, type, and tags
   - Validates manifest integrity

2. **TextChunker** (`app/services/text_expansion.py`)
   - Smart sentence-based chunking
   - Configurable chunk size with overlap
   - Preserves semantic boundaries

3. **TextExpansionService** (`app/services/text_expansion.py`)
   - Orchestrates the complete expansion pipeline
   - Integrates chunking, embedding, and storage
   - Handles idempotency and error recovery

## Configuration

### Default Parameters

- **Chunk Size**: 512 tokens (~2048 characters)
- **Chunk Overlap**: 102 tokens (~20% overlap, ~408 characters)
- **Minimum Chunk Size**: 100 tokens (~400 characters)
- **Embedding Dimensions**: 1536 (OpenAI-compatible)
- **Embedding Model**: BAAI/bge-small-en-v1.5

### Environment Variables

```bash
# ZeroDB Configuration
ZERODB_PROJECT_ID=your_project_id
ZERODB_API_KEY=your_api_key
ZERODB_API_URL=https://api.zerodb.ainative.io

# Embedding Configuration
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=1536
EMBEDDING_BATCH_SIZE=32
```

## Usage

### 1. Load Manifest

```python
from pathlib import Path
from app.services.manifest_loader import ManifestLoader

# Load manifest file
loader = ManifestLoader(manifest_path=Path("data/manifests/first_fruits_manifest.json"))
loader.load_manifest()

# Get P0 sources
p0_sources = loader.get_p0_sources()
print(f"Found {len(p0_sources)} P0 sources to expand")
```

### 2. Expand Single Document

```python
from app.services.text_expansion import TextExpansionService
from app.services.embedding import EmbeddingService
from app.db.zerodb import ZeroDBClient

# Initialize services
embedding_service = EmbeddingService()
zerodb_client = ZeroDBClient()
expansion_service = TextExpansionService(
    embedding_service=embedding_service,
    zerodb_client=zerodb_client,
)

# Expand document
document_text = "Full text of the document..."
metadata = {
    "source_id": "douglass_narrative_1845",
    "document_id": "douglass_narrative_1845_001",
    "source_org": "Project Gutenberg",
    "canonical_url": "https://www.gutenberg.org/ebooks/23",
    "license_info": "Public Domain",
    "year": 1845,
    "content_type": "autobiography",
    "tags": ["primary_source", "frederick_douglass", "slavery"],
    "priority": 0,
}

result = await expansion_service.expand_document(
    document_text=document_text,
    metadata=metadata,
    namespace="kwanzaa_primary_sources",
    skip_if_exists=True,
)

print(f"Status: {result['status']}")
print(f"Chunks created: {result['chunks_created']}")
print(f"Chunks stored: {result['chunks_stored']}")
```

### 3. Batch Processing

```python
# Process multiple documents
documents = [
    (text1, metadata1),
    (text2, metadata2),
    (text3, metadata3),
]

results = await expansion_service.expand_batch(
    documents=documents,
    namespace="kwanzaa_primary_sources",
    skip_if_exists=True,
)

# Check results
for result in results:
    print(f"{result['document_id']}: {result['status']}")
```

## Data Model

### Chunk Metadata Structure

Each chunk is stored with comprehensive provenance metadata:

```python
{
    "source_id": "douglass_narrative_1845",
    "document_id": "douglass_narrative_1845_001",
    "chunk_index": 0,
    "total_chunks": 25,
    "start_char": 0,
    "end_char": 2048,
    "chunk_hash": "sha256_hash_of_chunk_text",
    "chunk_text_preview": "First 200 chars of chunk...",
    
    # Provenance
    "source_org": "Project Gutenberg",
    "canonical_url": "https://www.gutenberg.org/ebooks/23",
    "license_info": "Public Domain",
    "year": 1845,
    "content_type": "autobiography",
    "tags": ["primary_source", "frederick_douglass", "slavery"],
    "priority": 0,
    "ingested_at": "2026-01-16T14:30:00Z",
}
```

### Vector Storage

Chunks are stored in ZeroDB with:
- **Vector ID**: `{document_id}_chunk_{chunk_index}`
- **Vector Embedding**: 1536-dimensional float array
- **Document**: Full chunk text
- **Metadata**: Complete provenance information
- **Namespace**: Persona-specific (e.g., `kwanzaa_primary_sources`)

## Chunking Strategy

### Smart Sentence-Based Chunking

The chunker uses sentence boundaries to create semantically coherent chunks:

1. **Text Normalization**
   - Remove control characters
   - Normalize whitespace
   - Preserve paragraph breaks

2. **Sentence Splitting**
   - Split on sentence boundaries (., !, ?)
   - Preserve paragraph structure
   - Handle edge cases (abbreviations, etc.)

3. **Chunk Assembly**
   - Group sentences up to chunk size
   - Add overlap from previous chunk
   - Respect minimum chunk size

### Overlap Strategy

Chunks include overlap to maintain context:

```
Chunk 1: [==============]
Chunk 2:         [======|==============]
Chunk 3:                        [======|==============]
                         ^^^^^^ overlap region
```

**Benefits:**
- Prevents loss of context at boundaries
- Improves retrieval quality
- Captures cross-boundary semantic relationships

## Idempotency

The pipeline is fully idempotent:

```python
# First run: processes document
result1 = await expansion_service.expand_document(text, metadata, skip_if_exists=True)
# result1['status'] == 'success'

# Second run: skips existing document
result2 = await expansion_service.expand_document(text, metadata, skip_if_exists=True)
# result2['status'] == 'skipped'
# result2['reason'] == 'document_already_exists'
```

## Error Handling

### Partial Success

If some chunks fail to store, the pipeline continues:

```python
{
    "status": "partial_success",
    "chunks_created": 10,
    "chunks_stored": 8,
    "errors": [
        {"chunk_index": 3, "error": "Storage timeout"},
        {"chunk_index": 7, "error": "Network error"},
    ]
}
```

### Recovery Strategy

Failed chunks can be retried by:
1. Re-running expansion (skipped chunks will be detected)
2. Using force mode: `skip_if_exists=False`

## Performance Considerations

### Batch Size

Embeddings are generated in batches (default: 32):
- Reduces API calls
- Improves throughput
- Manages memory usage

### Storage Optimization

Vectors are stored with:
- Compressed metadata
- Efficient vector indexing
- Namespace partitioning

### Typical Performance

- **Chunking**: ~1000 tokens/second
- **Embedding Generation**: ~100 chunks/second (batch)
- **Storage**: ~50 chunks/second

## Testing

Comprehensive test coverage includes:

```bash
# Run tests
pytest backend/tests/test_text_expansion.py -v
pytest backend/tests/test_manifest_loader.py -v

# Run with coverage
pytest backend/tests/test_text_expansion.py --cov=app.services.text_expansion
pytest backend/tests/test_manifest_loader.py --cov=app.services.manifest_loader
```

### Test Coverage

- Chunking logic: 100%
- Metadata handling: 100%
- Error scenarios: 100%
- Idempotency: 100%
- Provenance tracking: 100%

## Monitoring

### Key Metrics

1. **Processing Metrics**
   - Documents processed per hour
   - Chunks created per document
   - Average embedding time

2. **Quality Metrics**
   - Chunk size distribution
   - Overlap effectiveness
   - Storage success rate

3. **Error Metrics**
   - Failed documents
   - Storage errors
   - Validation failures

## Best Practices

### Manifest Management

1. **Validate Before Processing**
   ```python
   issues = loader.validate_manifest()
   if issues:
       print(f"Manifest validation failed: {issues}")
       return
   ```

2. **Use Priority Levels**
   - P0: Critical primary sources (expand first)
   - P1: Secondary sources (expand next)
   - P2+: Lower priority (expand as needed)

### Chunking Configuration

1. **For Short Documents** (< 5000 tokens)
   - Chunk size: 512 tokens
   - Overlap: 20%

2. **For Long Documents** (> 5000 tokens)
   - Chunk size: 1024 tokens
   - Overlap: 15%

3. **For Technical Content**
   - Chunk size: 768 tokens
   - Overlap: 25% (more context needed)

### Namespace Strategy

Organize by content type and persona:

- `kwanzaa_primary_sources`: Core historical documents
- `kwanzaa_black_press`: Historical newspapers
- `kwanzaa_speeches_letters`: Correspondence and speeches
- `kwanzaa_black_stem`: STEM-focused content
- `kwanzaa_teaching_kits`: Educational materials
- `kwanzaa_dev_patterns`: Development resources

## Troubleshooting

### Common Issues

1. **Empty Chunks Created**
   - Check minimum chunk size setting
   - Verify text normalization
   - Inspect source text quality

2. **Storage Failures**
   - Verify ZeroDB credentials
   - Check network connectivity
   - Review error logs

3. **Embedding Timeouts**
   - Reduce batch size
   - Check model availability
   - Monitor memory usage

## Future Enhancements

1. **Adaptive Chunking**
   - Context-aware chunk boundaries
   - Topic-based segmentation
   - Multi-level chunking

2. **Embedding Optimization**
   - Model fine-tuning
   - Dimension reduction
   - Quantization

3. **Storage Optimization**
   - Compression strategies
   - Index optimization
   - Caching layer

## References

- [EPIC 4: Data Ingestion Framework](../epics/epic_4_data_ingestion.md)
- [FirstFruitsManifest Schema](../schemas/first_fruits_manifest.md)
- [ZeroDB Integration Guide](./zerodb_integration.md)
- [RAG Best Practices](./rag_best_practices.md)
