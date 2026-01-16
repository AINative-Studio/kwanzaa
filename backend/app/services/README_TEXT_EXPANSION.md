# Text Expansion Service

## Overview

The Text Expansion Service provides selective full-text expansion capabilities for the Kwanzaa data ingestion pipeline. It processes P0 (priority 0) sources by chunking documents, generating embeddings, and storing them in ZeroDB with complete provenance metadata.

## Quick Start

```python
from pathlib import Path
from app.services.manifest_loader import ManifestLoader
from app.services.text_expansion import TextExpansionService
from app.services.embedding import EmbeddingService
from app.db.zerodb import ZeroDBClient

# Load P0 sources from manifest
loader = ManifestLoader(manifest_path=Path("data/manifests/first_fruits_manifest.json"))
loader.load_manifest()
p0_sources = loader.get_p0_sources()

# Initialize expansion service
service = TextExpansionService(
    embedding_service=EmbeddingService(),
    zerodb_client=ZeroDBClient(),
)

# Expand a document
result = await service.expand_document(
    document_text="Full document text...",
    metadata={
        "source_id": "douglass_narrative",
        "document_id": "douglass_narrative_001",
        "source_org": "Project Gutenberg",
        "canonical_url": "https://example.com",
        "license_info": "Public Domain",
        "year": 1845,
        "content_type": "autobiography",
        "tags": ["primary_source"],
        "priority": 0,
    },
    namespace="kwanzaa_primary_sources",
)
```

## Components

### 1. ManifestLoader

Loads and filters FirstFruitsManifest files.

```python
loader = ManifestLoader(manifest_path=Path("manifest.json"))
loader.load_manifest()

# Get P0 sources only
p0_sources = loader.get_p0_sources()

# Get sources by type
books = loader.get_sources_by_type(SourceType.BOOK)

# Get sources by tags
primary = loader.get_sources_by_tags(["primary_source"])

# Validate manifest
issues = loader.validate_manifest()
```

### 2. TextChunker

Smart sentence-based text chunking with overlap.

```python
chunker = TextChunker(
    chunk_size=512,      # tokens
    chunk_overlap=102,   # ~20%
    min_chunk_size=100,  # tokens
)

chunks = chunker.chunk_text(
    text="Document text...",
    metadata={"source_id": "test", "document_id": "doc_001"}
)
```

### 3. TextExpansionService

Main orchestration service.

```python
service = TextExpansionService(
    embedding_service=EmbeddingService(),
    zerodb_client=ZeroDBClient(),
)

# Single document
result = await service.expand_document(text, metadata)

# Batch processing
results = await service.expand_batch([
    (text1, metadata1),
    (text2, metadata2),
])
```

## Configuration

### Environment Variables

```bash
# ZeroDB
ZERODB_PROJECT_ID=your_project_id
ZERODB_API_KEY=your_api_key
ZERODB_API_URL=https://api.zerodb.ainative.io

# Embeddings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=1536
EMBEDDING_BATCH_SIZE=32
```

### Chunk Configuration

```python
# Default (recommended for most documents)
TextChunker(chunk_size=512, chunk_overlap=102)

# Large documents
TextChunker(chunk_size=1024, chunk_overlap=153)

# Technical content (needs more context)
TextChunker(chunk_size=768, chunk_overlap=192)
```

## Data Model

### Chunk Metadata

```python
@dataclass
class ChunkMetadata:
    source_id: str              # Source identifier
    document_id: str            # Document identifier
    chunk_index: int            # 0-based chunk position
    total_chunks: int           # Total chunks in document
    start_char: int             # Start position in source
    end_char: int               # End position in source
    
    # Provenance (optional)
    source_org: Optional[str]
    canonical_url: Optional[str]
    license_info: Optional[str]
    year: Optional[int]
    content_type: Optional[str]
    tags: List[str]
    priority: int
```

### Storage Format

Vectors are stored in ZeroDB with:
- **Vector ID**: `{document_id}_chunk_{chunk_index}`
- **Namespace**: Persona-specific (e.g., `kwanzaa_primary_sources`)
- **Document**: Full chunk text
- **Metadata**: Complete ChunkMetadata + chunk_hash + ingested_at

## Features

### Idempotent Processing

The service automatically skips documents that have already been processed:

```python
# First run: processes document
result1 = await service.expand_document(text, metadata, skip_if_exists=True)
# Returns: {'status': 'success', 'chunks_stored': 25}

# Second run: skips automatically
result2 = await service.expand_document(text, metadata, skip_if_exists=True)
# Returns: {'status': 'skipped', 'reason': 'document_already_exists'}

# Force reprocessing
result3 = await service.expand_document(text, metadata, skip_if_exists=False)
# Returns: {'status': 'success', 'chunks_stored': 25}
```

### Error Handling

The service provides detailed error information:

```python
result = await service.expand_document(text, metadata)

if result['status'] == 'success':
    print(f"Stored {result['chunks_stored']} chunks")
    
elif result['status'] == 'partial_success':
    print(f"Stored {result['chunks_stored']}/{result['chunks_created']} chunks")
    for error in result['errors']:
        print(f"Chunk {error['chunk_index']}: {error['error']}")
        
elif result['status'] == 'error':
    print(f"Error: {result['reason']}")
```

### Batch Processing

Process multiple documents efficiently:

```python
documents = [
    (text1, metadata1),
    (text2, metadata2),
    (text3, metadata3),
]

results = await service.expand_batch(documents)

for result in results:
    print(f"{result['document_id']}: {result['status']}")
```

## Usage Examples

### Example 1: Process Local File

```python
from pathlib import Path

# Read document
text = Path("data/texts/document.txt").read_text()

# Create metadata
metadata = {
    "source_id": "test_source",
    "document_id": "test_doc_001",
    "source_org": "Test Organization",
    "canonical_url": "https://example.com/doc",
    "license_info": "Public Domain",
    "year": 1903,
    "content_type": "essay",
    "tags": ["test", "primary_source"],
    "priority": 0,
}

# Expand
result = await service.expand_document(
    document_text=text,
    metadata=metadata,
    namespace="kwanzaa_primary_sources",
)
```

### Example 2: Process All P0 Sources

```python
from app.services.manifest_loader import ManifestLoader

# Load manifest
loader = ManifestLoader(manifest_path=Path("manifest.json"))
loader.load_manifest()

# Process all P0 sources
for source in loader.get_p0_sources():
    # Extract text (implementation depends on access_method)
    text = extract_text(source)
    
    # Create metadata
    metadata = {
        "source_id": source.source_id,
        "document_id": f"{source.source_id}_001",
        "source_org": source.source_org,
        "canonical_url": source.canonical_url,
        "license_info": source.license_info,
        "year": source.year,
        "content_type": source.content_type,
        "tags": source.tags,
        "priority": source.priority,
    }
    
    # Expand
    result = await service.expand_document(text, metadata)
    print(f"{source.source_name}: {result['status']}")
```

### Example 3: Custom Chunking

```python
# Create custom chunker
custom_chunker = TextChunker(
    chunk_size=1024,     # Larger chunks
    chunk_overlap=256,   # 25% overlap
    min_chunk_size=200,  # Higher minimum
)

# Use with service
service = TextExpansionService(
    embedding_service=EmbeddingService(),
    zerodb_client=ZeroDBClient(),
    chunker=custom_chunker,
)
```

## Command Line Usage

```bash
# Process P0 sources from manifest
python scripts/expand_p0_sources.py \
    --manifest data/manifests/first_fruits_manifest.json \
    --namespace kwanzaa_primary_sources

# Dry run (validation only)
python scripts/expand_p0_sources.py \
    --manifest manifest.json \
    --dry-run

# Force reprocessing
python scripts/expand_p0_sources.py \
    --manifest manifest.json \
    --force
```

## Testing

```bash
# Run all tests
pytest tests/test_text_expansion.py -v
pytest tests/test_manifest_loader.py -v

# Run with coverage
pytest tests/test_text_expansion.py --cov=app.services.text_expansion
pytest tests/test_manifest_loader.py --cov=app.services.manifest_loader

# Run specific test
pytest tests/test_text_expansion.py::TestTextChunker::test_chunk_long_text -v
```

## Performance

### Typical Performance Metrics

| Operation | Throughput |
|-----------|-----------|
| Text chunking | ~1000 tokens/sec |
| Embedding generation | ~100 chunks/sec (batch) |
| Vector storage | ~50 chunks/sec |
| End-to-end | 2-3 min per 100KB document |

### Optimization Tips

1. **Use batch processing** for multiple documents
2. **Adjust batch size** based on memory constraints
3. **Use appropriate chunk size** for content type
4. **Enable skip_if_exists** for idempotent operations
5. **Monitor ZeroDB performance** and adjust timeouts

## Best Practices

### 1. Chunk Size Selection

- **Short documents** (< 5000 tokens): 512 tokens, 20% overlap
- **Long documents** (> 5000 tokens): 1024 tokens, 15% overlap
- **Technical content**: 768 tokens, 25% overlap (needs more context)

### 2. Namespace Organization

Organize by content type and persona:
- `kwanzaa_primary_sources`: Core historical documents
- `kwanzaa_black_press`: Historical newspapers
- `kwanzaa_speeches_letters`: Correspondence
- `kwanzaa_black_stem`: STEM content
- `kwanzaa_teaching_kits`: Educational materials

### 3. Manifest Management

```python
# Always validate before processing
issues = loader.validate_manifest()
if issues:
    print(f"Validation failed: {issues}")
    return

# Check statistics
stats = loader.get_statistics()
print(f"Total P0 sources: {stats['p0_sources']}")
```

### 4. Error Recovery

```python
# Collect results
results = await service.expand_batch(documents)

# Retry failed documents
failed_docs = [
    (text, meta) 
    for (text, meta), result in zip(documents, results)
    if result['status'] == 'error'
]

if failed_docs:
    print(f"Retrying {len(failed_docs)} failed documents...")
    retry_results = await service.expand_batch(failed_docs)
```

## Troubleshooting

### Issue: Empty chunks created

**Cause**: Minimum chunk size too high or text too short

**Solution**: 
```python
chunker = TextChunker(min_chunk_size=50)  # Lower minimum
```

### Issue: Storage failures

**Cause**: ZeroDB connection or authentication issues

**Solution**:
```python
# Check credentials
print(f"Project ID: {settings.ZERODB_PROJECT_ID}")
print(f"API URL: {settings.ZERODB_API_URL}")

# Test connection
client = ZeroDBClient()
result = await client.search_vectors(
    query_vector=[0.0] * 1536,
    limit=1,
)
```

### Issue: Embedding timeouts

**Cause**: Batch size too large or model unavailable

**Solution**:
```python
# Reduce batch size
settings.EMBEDDING_BATCH_SIZE = 16
```

## References

- [Text Expansion Pipeline Documentation](../../../docs/technical/text_expansion_pipeline.md)
- [Implementation Summary](../../../docs/technical/issue_15_implementation_summary.md)
- [EPIC 4: Data Ingestion Framework](../../../docs/epics/epic_4_data_ingestion.md)
- [FirstFruitsManifest Schema](../../../docs/schemas/first_fruits_manifest.md)

## Support

For issues or questions:
1. Check the [troubleshooting guide](#troubleshooting)
2. Review the [comprehensive documentation](../../../docs/technical/text_expansion_pipeline.md)
3. Open an issue on GitHub with the `epic:data-ingestion` label
