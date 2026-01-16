# Metadata Ingestion Pipeline - Quick Start Guide

## Overview

This guide walks you through running the metadata-first ingestion pipeline for the Kwanzaa First Fruits corpus in under 5 minutes.

## Prerequisites

- Python 3.10+
- Required packages installed (see `backend/requirements.txt`)
- Access to ZeroDB (or use mock client for testing)

## Quick Start

### 1. Run the Pipeline

```bash
cd /Users/aideveloper/kwanzaa/backend

# Basic run with mock client (for testing)
python3 scripts/run_metadata_ingestion.py \
  --manifest /Users/aideveloper/kwanzaa/data/manifests/first_fruits_manifest.json

# With custom output directory
python3 scripts/run_metadata_ingestion.py \
  --manifest /Users/aideveloper/kwanzaa/data/manifests/first_fruits_manifest.json \
  --output-dir /Users/aideveloper/kwanzaa/data/ingestion_runs \
  --batch-size 50
```

### 2. Check the Results

```bash
# View ingestion stats
cat /Users/aideveloper/kwanzaa/data/ingestion_runs/*_stats.json | python3 -m json.tool

# View logs (if log file specified)
tail -f /Users/aideveloper/kwanzaa/data/ingestion_runs/ingestion.log
```

### 3. Run Tests

```bash
cd /Users/aideveloper/kwanzaa/backend

# Run all ingestion tests
python3 -m pytest tests/test_metadata_ingestion.py -v

# Run with coverage
python3 -m pytest tests/test_metadata_ingestion.py --cov=app.services.metadata_ingestion
```

## Example Output

### Successful Run

```
2026-01-16 14:28:08 - INFO - Starting metadata ingestion run: ingestion_run_20260116_222808
2026-01-16 14:28:08 - INFO - Loading manifest from: data/manifests/first_fruits_manifest.json
2026-01-16 14:28:08 - INFO - Manifest loaded successfully: 4 sources
2026-01-16 14:28:08 - INFO - Processing source: loc_douglass_papers
2026-01-16 14:28:08 - INFO - Extracted 1 documents from loc_douglass_papers
2026-01-16 14:28:08 - INFO - Storing batch of 4 documents to kw_documents
2026-01-16 14:28:08 - INFO - Successfully stored 4 documents
2026-01-16 14:28:08 - INFO - Ingestion run completed: ingestion_run_20260116_222808
============================================================
INGESTION SUMMARY
============================================================
Run ID: ingestion_run_20260116_222808
Started: 2026-01-16T22:28:08.788397+00:00
Completed: 2026-01-16T22:28:08.789062+00:00
Sources Processed: 4/4
Sources Failed: 0
Documents Inserted: 4
Documents Failed: 0
Total Errors: 0
============================================================
```

### Stats JSON

```json
{
    "run_id": "ingestion_run_20260116_222808",
    "started_at": "2026-01-16T22:28:08.788397+00:00",
    "completed_at": "2026-01-16T22:28:08.789062+00:00",
    "total_sources": 4,
    "sources_processed": 4,
    "sources_failed": 0,
    "total_documents": 4,
    "documents_inserted": 4,
    "documents_updated": 0,
    "documents_failed": 0,
    "errors": []
}
```

## Command Line Options

```
usage: run_metadata_ingestion.py [-h] --manifest MANIFEST
                                 [--batch-size BATCH_SIZE]
                                 [--max-retries MAX_RETRIES]
                                 [--output-dir OUTPUT_DIR]
                                 [--log-level {DEBUG,INFO,WARNING,ERROR}]
                                 [--log-file LOG_FILE]
                                 [--use-real-client]

Options:
  --manifest MANIFEST           Path to First Fruits manifest JSON file (required)
  --batch-size BATCH_SIZE       Batch size for bulk operations (default: 100)
  --max-retries MAX_RETRIES     Maximum retry attempts (default: 3)
  --output-dir OUTPUT_DIR       Directory for output files
  --log-level LEVEL             Logging level (default: INFO)
  --log-file LOG_FILE           Optional log file path
  --use-real-client             Use real ZeroDB client (requires config)
```

## Programmatic Usage

```python
import asyncio
from pathlib import Path
from app.services.metadata_ingestion import MetadataIngestionPipeline

async def run_ingestion():
    # Mock client for testing
    from scripts.run_metadata_ingestion import MockZeroDBClient
    client = MockZeroDBClient()

    # Initialize pipeline
    pipeline = MetadataIngestionPipeline(
        manifest_path=Path("data/manifests/first_fruits_manifest.json"),
        zerodb_client=client,
        batch_size=100,
        max_retries=3,
    )

    # Run pipeline
    stats = await pipeline.run()

    # Export stats
    pipeline.export_stats(Path("data/ingestion_runs/my_run_stats.json"))

    print(f"Processed {stats.sources_processed}/{stats.total_sources} sources")
    print(f"Inserted {stats.documents_inserted} documents")

# Run
asyncio.run(run_ingestion())
```

## Test Coverage

The pipeline includes comprehensive tests covering:

- ✅ Metadata validation (9 tests)
- ✅ Document processing (11 tests)
- ✅ Error handling (3 tests)
- ✅ Idempotency (1 test)
- ✅ Statistics tracking (2 tests)
- ✅ Enum definitions (3 tests)

**Total: 29 tests with 86%+ coverage**

## Troubleshooting

### Issue: "Manifest file not found"

**Solution**: Verify the manifest path is correct:
```bash
ls -la /Users/aideveloper/kwanzaa/data/manifests/first_fruits_manifest.json
```

### Issue: "Invalid source_type"

**Solution**: Ensure source types in manifest match supported values:
- `primary_source`, `speech`, `black_press` → mapped to `archive` or `press`
- Or use direct values: `government`, `university`, `library`, `museum`, `archive`, `press`, `nonprofit`, `publisher`

### Issue: "Module not found"

**Solution**: Install dependencies:
```bash
cd /Users/aideveloper/kwanzaa/backend
pip install -r requirements.txt
```

## Next Steps

1. **Extend the Pipeline**: Add real API connectors for sources
2. **Enable Full Text**: Implement chunking and embedding generation
3. **Add Monitoring**: Set up Prometheus metrics and Grafana dashboards
4. **Deploy to Production**: Configure real ZeroDB client and credentials
5. **Schedule Jobs**: Set up cron or Airflow for daily ingestion runs

## Further Reading

- [Complete Documentation](metadata-first-pipeline.md)
- [Data Ingestion Plan](/Users/aideveloper/kwanzaa/docs/planning/Data-Ingestion.md)
- [Technical PRD](/Users/aideveloper/kwanzaa/docs/planning/technical-ingestion.md)
- [First Fruits Manifest](/Users/aideveloper/kwanzaa/data/manifests/first_fruits_manifest.json)

## Support

For issues or questions:
1. Check the [full documentation](metadata-first-pipeline.md)
2. Review test examples in `backend/tests/test_metadata_ingestion.py`
3. Open an issue on the project repository
