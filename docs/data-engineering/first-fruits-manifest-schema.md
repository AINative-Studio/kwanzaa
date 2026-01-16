# First Fruits Manifest Schema Documentation

## Overview

The First Fruits Manifest Schema is a comprehensive, standardized specification for documenting data sources in the Kwanzaa First Fruits Corpus. It serves as the single source of truth for all data ingestion, ensuring consistency, traceability, and provenance tracking across the entire data pipeline.

This schema embodies three core Nguzo Saba principles:

- **Umoja (Unity)**: Standardized schema creates unity across diverse data sources
- **Ujima (Collective Work)**: Transparent sourcing enables collective responsibility and shared understanding
- **Imani (Faith)**: Verifiable attribution builds trust through complete provenance tracking

## Schema Version

**Current Version**: 1.0.0

**Schema Location**: `/data/schemas/first_fruits_manifest.schema.json`

**Pydantic Models**: `/backend/app/models/manifest/first_fruits_manifest.py`

## Core Concepts

### Single Source of Truth

Every data source in the Kwanzaa corpus MUST have a corresponding manifest file. The manifest is the authoritative reference for:

- Source identification and classification
- Access methods and authentication
- Licensing and usage rights
- Ingestion configuration and schedules
- Data quality metrics and known issues
- Provenance and change history

### Versioning Strategy

Manifests use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to schema structure
- **MINOR**: Backwards-compatible additions
- **PATCH**: Backwards-compatible fixes

The `manifest_version` field tracks the schema version used to create the manifest.

### Provenance Tracking

All manifests include comprehensive provenance information:

- Who created the manifest
- Who reviewed it
- Complete change history with timestamps
- Last verification date

## Required Fields

The following fields are REQUIRED for all manifests:

| Field | Type | Description |
|-------|------|-------------|
| `manifest_version` | string | Semantic version (e.g., "1.0.0") |
| `source_id` | string | Unique identifier (lowercase, alphanumeric, `-`, `_`) |
| `source_name` | string | Human-readable name |
| `source_type` | enum | Classification of source type |
| `access_method` | object | How to access the data |
| `license` | object | License information |
| `canonical_url` | URL | Primary URL for the source |
| `priority` | enum | Priority level (P0-P4) |
| `tags` | array[string] | Categorization tags |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `updated_at` | datetime | ISO 8601 update timestamp |

## Field Reference

### Source Identification

#### `source_id`

- **Type**: string
- **Pattern**: `^[a-z0-9_-]+$`
- **Length**: 3-100 characters
- **Required**: Yes
- **Description**: Unique identifier for the source. Must be lowercase alphanumeric with underscores or hyphens only.
- **Example**: `"nara_civil_rights"`, `"loc_oral_histories"`

#### `source_name`

- **Type**: string
- **Length**: 1-500 characters
- **Required**: Yes
- **Description**: Human-readable name of the source
- **Example**: `"National Archives - Civil Rights Era Documents"`

#### `source_type`

- **Type**: enum
- **Required**: Yes
- **Values**:
  - `archive`: Traditional archives
  - `database`: Structured databases
  - `api`: API-based sources
  - `file_collection`: File collections
  - `web_scrape`: Web scraping targets
  - `repository`: Code/data repositories
  - `dataset`: Published datasets
  - `library_catalog`: Library catalogs
  - `museum_collection`: Museum collections
  - `oral_history`: Oral history collections
  - `digitized_documents`: Digitized document collections

### Access Configuration

#### `access_method`

An object defining how to access the data source.

**Required Fields**:
- `type`: Access method type (enum)
-
**Optional Fields**:
- `endpoint`: API endpoint or base URL
- `authentication`: Authentication configuration
- `rate_limits`: Rate limiting parameters
- `protocol_details`: Protocol-specific details

**Access Method Types**:
- `direct_download`: Direct HTTP download
- `api_key_required`: Requires API key
- `oauth_required`: Requires OAuth
- `web_scraping`: Web scraping
- `manual_download`: Manual download required
- `bulk_export`: Bulk export available
- `streaming`: Streaming access
- `ftp`: FTP access
- `s3_bucket`: S3 bucket access
- `rsync`: rsync access

**Authentication Object**:
```json
{
  "required": true,
  "method": "api_key",
  "env_var": "NARA_API_KEY"
}
```

**Rate Limits Object**:
```json
{
  "requests_per_second": 2.0,
  "requests_per_day": 1000,
  "concurrent_connections": 3
}
```

### License Information

#### `license`

A comprehensive object defining license terms.

**Required Fields**:
- `type`: License type identifier
- `commercial_use_allowed`: Boolean
- `attribution_required`: Boolean

**Optional Fields**:
- `url`: URL to full license text
- `share_alike_required`: Boolean
- `restrictions`: Array of restriction strings
- `notes`: Additional clarifications

**Common License Types**:
- `"Public Domain"`
- `"CC0"`
- `"CC BY 4.0"`
- `"CC BY-SA 4.0"`
- `"CC BY-NC 4.0"`
- `"Fair Use"`
- `"All Rights Reserved"`
- `"Mixed - Varies by Collection"`

### Priority Levels

#### `priority`

- **Type**: enum
- **Required**: Yes
- **Values**:
  - `P0`: Critical/Immediate - Core primary sources
  - `P1`: High - Important primary sources
  - `P2`: Medium - Secondary sources and supplements
  - `P3`: Low - Nice-to-have materials
  - `P4`: Backlog - Future consideration

### Content Metadata

#### `content_metadata`

Optional but highly recommended object describing the content.

**Fields**:

- `content_types`: Array of content type enums
  - `text`, `speech`, `letter`, `proclamation`, `legal_document`, `article`, `book`, `photograph`, `audio`, `video`, `oral_history`, `manuscript`, `newspaper`, `periodical`, `government_record`

- `time_period`: Object with `start_year` and `end_year` (integers, 1600-2100)

- `languages`: Array of ISO 639-1 language codes (e.g., `["en", "es", "fr-CA"]`)

- `geographic_coverage`: Array of geographic locations

- `estimated_size`: Object with:
  - `document_count`: Estimated number of documents
  - `total_size_bytes`: Estimated size in bytes
  - `total_size_human`: Human-readable size (e.g., "48.8 GB")

### Ingestion Configuration

#### `ingestion_config`

Optional object defining ingestion pipeline parameters.

**Pipeline Types**:
- `batch`: Batch processing
- `streaming`: Streaming ingestion
- `incremental`: Incremental updates
- `one_time`: One-time import

**Schedule Object**:
```json
{
  "frequency": "monthly",
  "cron_expression": "0 2 1 * *"
}
```

**Frequencies**: `once`, `hourly`, `daily`, `weekly`, `monthly`, `on_demand`

**Chunk Strategy Object**:
```json
{
  "method": "semantic",
  "chunk_size": 1000,
  "overlap": 200
}
```

**Chunking Methods**:
- `fixed_size`: Fixed character/token count
- `semantic`: Semantic boundaries
- `paragraph`: Paragraph boundaries
- `sentence`: Sentence boundaries
- `document`: Whole documents

**Quality Checks**:
- `content_validation`: Validate content structure
- `deduplication`: Remove duplicates
- `language_detection`: Detect languages
- `encoding_validation`: Validate encoding
- `metadata_completeness`: Check metadata
- `link_validation`: Validate URLs

### Data Quality Tracking

#### `data_quality`

Optional object for tracking data quality metrics.

**Fields**:

- `completeness_score`: Float 0.0-1.0 (0.0 = incomplete, 1.0 = complete)
- `accuracy_score`: Float 0.0-1.0
- `last_verified`: ISO 8601 timestamp
- `known_issues`: Array of known issue strings
- `data_lineage`: Array of lineage strings

### Nguzo Saba Alignment

#### `nguzo_saba_alignment`

Optional object mapping source to the Seven Principles.

**Fields** (all boolean):
- `umoja`: Unity - Promotes collective Black history and culture
- `kujichagulia`: Self-Determination - Centers Black voices and agency
- `ujima`: Collective Work - Shared community resources
- `ujamaa`: Cooperative Economics - Supports community-owned knowledge
- `nia`: Purpose - Serves educational and cultural preservation goals
- `kuumba`: Creativity - Enables creative expression and interpretation
- `imani`: Faith - Verifiable, trustworthy primary sources

### Ingestion Status

#### `ingestion_status`

Optional object tracking actual ingestion progress.

**Fields**:

- `status`: Enum - `not_started`, `in_progress`, `completed`, `failed`, `paused`, `archived`
- `last_ingestion_date`: ISO 8601 timestamp
- `documents_ingested`: Integer count
- `vectors_created`: Integer count
- `errors`: Array of error objects with `timestamp`, `error_type`, `message`

## Example Manifests

Three complete example manifests are provided in `/data/manifests/examples/`:

1. **nara_civil_rights.json**: National Archives civil rights documents (P0 priority, API access)
2. **loc_oral_histories.json**: Library of Congress oral histories (P1 priority, direct download)
3. **schomburg_digital_collections.json**: Schomburg Center collections (P1 priority, web scraping)

Each example demonstrates different:
- Source types
- Access methods
- License configurations
- Content metadata patterns
- Ingestion strategies

## Validation

### JSON Schema Validation

All manifests MUST validate against `/data/schemas/first_fruits_manifest.schema.json`.

Use a JSON Schema validator:

```bash
# Using ajv-cli
ajv validate -s data/schemas/first_fruits_manifest.schema.json \
    -d data/manifests/examples/nara_civil_rights.json
```

### Pydantic Validation

Python code should use the Pydantic models for validation:

```python
from backend.app.models.manifest import FirstFruitsManifest
import json

# Load and validate manifest
with open("data/manifests/examples/nara_civil_rights.json") as f:
    data = json.load(f)

manifest = FirstFruitsManifest(**data)
print(f"Valid manifest: {manifest.source_name}")
```

## Creating New Manifests

### Step 1: Source Research

Before creating a manifest:

1. Identify the canonical source
2. Research access methods and authentication
3. Verify license terms
4. Document content scope and metadata
5. Estimate size and complexity

### Step 2: Create Manifest File

1. Copy an example manifest as a template
2. Choose appropriate `source_id` (lowercase, descriptive)
3. Fill in all required fields
4. Add optional fields as applicable
5. Document provenance (who created it, when)

### Step 3: Validate

1. Validate against JSON Schema
2. Validate with Pydantic models
3. Review with subject matter experts
4. Add reviewers to `provenance.reviewed_by`

### Step 4: Version Control

1. Commit manifest to git
2. Include review approvals
3. Link to relevant issue/story
4. Update manifest registry (if applicable)

## Best Practices

### Naming Conventions

**Source IDs**:
- Use lowercase only
- Use underscores for word separation
- Include organization abbreviation
- Be descriptive but concise
- Examples: `nara_civil_rights`, `loc_oral_histories`, `schomburg_digital`

**Tags**:
- Use lowercase only
- Use hyphens for word separation
- Be specific and consistent
- Examples: `civil-rights`, `primary-sources`, `oral-history`

### Documentation

- Always provide a detailed `description` field
- Document `known_issues` honestly
- Include `notes` for special considerations
- Keep `change_history` up to date

### License Compliance

- Never assume public domain
- Document restrictions explicitly
- Include license URLs
- Note when licenses vary within a collection
- Err on the side of caution for commercial use

### Data Quality

- Verify sources before creating manifests
- Update `last_verified` regularly
- Document `known_issues` as discovered
- Track `data_lineage` for provenance

### Rate Limiting

- Always respect rate limits
- Set conservative defaults
- Use exponential backoff for retries
- Consider bulk download options

## Maintenance

### Regular Updates

Manifests should be reviewed and updated:

- **Monthly**: Verify `last_verified` dates
- **Quarterly**: Check for source changes
- **Annually**: Comprehensive review and revalidation
- **As Needed**: When issues are discovered

### Change Management

When updating manifests:

1. Update `updated_at` timestamp
2. Add entry to `provenance.change_history`
3. Increment `manifest_version` if schema changes
4. Re-validate against schema
5. Commit with descriptive message

## Troubleshooting

### Common Validation Errors

**Invalid source_id format**:
```
Error: source_id must match pattern ^[a-z0-9_-]+$
Solution: Use only lowercase letters, numbers, underscores, hyphens
```

**Missing required fields**:
```
Error: Field 'license' is required
Solution: Add all required fields listed in schema
```

**Invalid date format**:
```
Error: created_at must be ISO 8601 format
Solution: Use format: 2026-01-16T14:00:00Z
```

**Invalid URL**:
```
Error: canonical_url must be valid URI
Solution: Include protocol: https://example.com
```

### Getting Help

- Review example manifests in `/data/manifests/examples/`
- Check schema documentation in `/data/schemas/`
- Consult Pydantic models for type hints
- Ask data engineering team for guidance

## Related Documentation

- [Data Ingestion Pipeline](./data-ingestion-pipeline.md)
- [Vector Database Schema](./vector-database-schema.md)
- [Answer JSON Contract](../schemas/answer-json-contract.md)
- [Source Attribution Guidelines](./source-attribution.md)

## Schema Evolution

### Version History

- **1.0.0** (2026-01-16): Initial schema release

### Future Enhancements

Planned additions for future versions:

- Support for streaming data sources
- Real-time quality metrics
- Automated verification workflows
- Integration with catalog APIs
- Machine-readable SLAs

### Deprecation Policy

Breaking changes will:

1. Be announced 90 days in advance
2. Include migration guide
3. Provide backward compatibility tools
4. Increment MAJOR version number

## Contributing

To propose schema changes:

1. Open an issue describing the need
2. Provide examples of affected manifests
3. Submit PR with schema updates
4. Update documentation
5. Add/update validation tests
6. Get approval from data engineering team

## License

This schema and documentation are part of the Kwanzaa project and licensed under the Apache 2.0 License.

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-16
**Maintained By**: AINative Data Engineering Team
