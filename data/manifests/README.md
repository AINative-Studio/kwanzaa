# First Fruits Manifest Registry

This directory contains manifest files for all data sources in the Kwanzaa First Fruits Corpus.

## Overview

Each manifest file is a JSON document that serves as the single source of truth for a data source, documenting:

- Source identification and metadata
- Access methods and authentication
- Licensing and usage rights
- Content characteristics
- Ingestion configuration
- Data quality metrics
- Provenance and change history

## Directory Structure

```
manifests/
├── README.md (this file)
├── examples/               # Example manifests
│   ├── nara_civil_rights.json
│   ├── loc_oral_histories.json
│   └── schomburg_digital_collections.json
└── active/                 # Active source manifests (to be created)
```

## Schema

All manifests MUST conform to the First Fruits Manifest Schema:

- **Schema Location**: `/data/schemas/first_fruits_manifest.schema.json`
- **Schema Version**: 1.0.0
- **Documentation**: `/docs/data-engineering/first-fruits-manifest-schema.md`
- **Pydantic Models**: `/backend/app/models/manifest/`

## Example Manifests

Three complete example manifests are provided in the `examples/` directory:

### 1. NARA Civil Rights Documents
**File**: `examples/nara_civil_rights.json`

- **Priority**: P0 (Critical)
- **Source Type**: Archive
- **Access**: API with authentication
- **Content**: Civil Rights era documents (1954-1968)
- **Size**: ~15,000 documents, 48.8 GB

### 2. Library of Congress Oral Histories
**File**: `examples/loc_oral_histories.json`

- **Priority**: P1 (High)
- **Source Type**: Oral History
- **Access**: Direct download (no authentication)
- **Content**: African American oral histories (1920-2020)
- **Size**: ~850 interviews, 200 GB

### 3. Schomburg Center Digital Collections
**File**: `examples/schomburg_digital_collections.json`

- **Priority**: P1 (High)
- **Source Type**: Library Catalog
- **Access**: Web scraping (respectful crawl)
- **Content**: African diaspora materials (1600-2020)
- **Size**: ~250,000 items, 500 GB

## Creating New Manifests

### Step 1: Research the Source

Before creating a manifest:

1. Identify the canonical source URL
2. Research access methods and API documentation
3. Verify license terms and usage rights
4. Document content scope and metadata standards
5. Estimate size and document count

### Step 2: Create Manifest File

1. Copy an example manifest as a template:
   ```bash
   cp examples/nara_civil_rights.json active/your_source_id.json
   ```

2. Update all fields according to your source
3. Choose an appropriate `source_id`:
   - Lowercase only
   - Use underscores for separation
   - Include organization abbreviation
   - Be descriptive but concise
   - Example: `smithsonian_nmaahc`

4. Set appropriate priority level:
   - **P0**: Critical primary sources needed immediately
   - **P1**: Important primary sources
   - **P2**: Secondary sources and supplements
   - **P3**: Nice-to-have materials
   - **P4**: Backlog for future consideration

### Step 3: Validate

Validate your manifest before committing:

```python
from app.models.manifest import FirstFruitsManifest
import json

# Load and validate
with open("active/your_source_id.json") as f:
    data = json.load(f)

manifest = FirstFruitsManifest(**data)
print(f"Valid manifest: {manifest.source_name}")
```

Or use JSON Schema validation:

```bash
# Install ajv-cli if needed: npm install -g ajv-cli
ajv validate \
    -s ../../schemas/first_fruits_manifest.schema.json \
    -d active/your_source_id.json
```

### Step 4: Submit for Review

1. Commit manifest to git
2. Add reviewers to `provenance.reviewed_by`
3. Create pull request
4. Link to relevant issue/story

## Manifest Lifecycle

### Status Values

Manifests track ingestion status:

- `not_started`: Source identified but not yet ingested
- `in_progress`: Ingestion currently running
- `completed`: Successfully ingested
- `failed`: Ingestion failed (see `errors` field)
- `paused`: Temporarily paused
- `archived`: No longer active

### Updates

Manifests should be updated when:

- Source access methods change
- License terms are updated
- Ingestion configuration changes
- Data quality issues are discovered
- New related sources are identified

Always:
1. Update `updated_at` timestamp
2. Add entry to `provenance.change_history`
3. Increment `manifest_version` if schema changes
4. Re-validate against schema

## Best Practices

### Naming Conventions

**Source IDs**:
- `nara_civil_rights` (organization_topic)
- `loc_oral_histories` (organization_collection)
- `schomburg_digital` (name_type)

**Tags**:
- Use hyphens for word separation
- Be specific and consistent
- Examples: `civil-rights`, `oral-history`, `primary-sources`

### License Documentation

- Never assume public domain
- Document restrictions explicitly
- Include license URLs
- Note when licenses vary within collection
- Err on the side of caution

### Rate Limiting

- Always respect API rate limits
- Set conservative defaults
- Use exponential backoff
- Consider bulk download options
- Document in `access_method.rate_limits`

### Data Quality

- Be honest about `known_issues`
- Track `data_lineage` for provenance
- Update `last_verified` regularly
- Document quality scores transparently

## Maintenance

### Regular Reviews

- **Monthly**: Verify `last_verified` dates
- **Quarterly**: Check for source changes
- **Annually**: Comprehensive revalidation

### Change Management

When updating manifests:

1. Update `updated_at` timestamp
2. Add change history entry
3. Re-validate against schema
4. Commit with descriptive message
5. Notify data engineering team

## Resources

- **Schema Documentation**: `/docs/data-engineering/first-fruits-manifest-schema.md`
- **JSON Schema**: `/data/schemas/first_fruits_manifest.schema.json`
- **Pydantic Models**: `/backend/app/models/manifest/`
- **Tests**: `/backend/tests/unit/models/test_first_fruits_manifest.py`

## Support

For questions or assistance:

1. Review example manifests
2. Consult schema documentation
3. Check Pydantic models for type hints
4. Ask data engineering team

## License

This documentation and manifest schema are part of the Kwanzaa project and licensed under Apache 2.0.

---

**Version**: 1.0.0
**Last Updated**: 2026-01-16
**Maintained By**: AINative Data Engineering Team
