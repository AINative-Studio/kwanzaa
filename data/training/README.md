# Kwanzaa Adapter Training Dataset

**Version:** 1.0.0
**Epic:** 3B - Adapter Training Dataset Preparation
**Issue:** #55 (E3B-US1)

## Overview

This directory contains training samples that teach the Kwanzaa adapter three critical behaviors:

1. **Citation-following**: Properly citing sources when good retrieval context is available
2. **Refusal**: Gracefully declining when information is not in the corpus
3. **answer_json compliance**: Strictly adhering to the Epic 8 contract format

## Quick Start

### Validate Datasets

```bash
# Validate all example files
python3 data/training/scripts/validate_dataset.py data/training/examples/*.json

# Generate detailed report
python3 data/training/scripts/validate_dataset.py \
  data/training/examples/*.json \
  --report data/training/validation_report.txt
```

## Files

- `dataset-schema.json` - JSON Schema specification
- `models.py` - Pydantic validation models  
- `examples/` - Training sample files (4 categories)
- `scripts/validate_dataset.py` - Validation utility
- `docs/training-dataset-schema.md` - Complete documentation

## References

- Schema Documentation: `docs/training-dataset-schema.md`
- Answer Contract: `backend/app/schemas/answer_json.schema.json`
- Issue Tracker: GitHub Issue #55
