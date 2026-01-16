# Namespace Quick Reference Card

**For**: Developers, Data Curators, Contributors
**Purpose**: Fast lookup for namespace decisions and usage
**Last Updated**: 2026-01-16

---

## Quick Decision Tree

```
What type of content are you working with?

1. Government doc/official record? → kwanzaa_primary_sources
2. Black newspaper/periodical?     → kwanzaa_black_press
3. Speech/letter?                  → kwanzaa_speeches_letters
4. STEM biography/patent?          → kwanzaa_black_stem
5. Lesson plan/curriculum?         → kwanzaa_teaching_kits
6. Technical doc/code?             → kwanzaa_dev_patterns
7. Not sure?                       → File issue for review
```

---

## The 6 Namespaces (One-Line Summary)

| Namespace | What Goes Here |
|-----------|---------------|
| `kwanzaa_primary_sources` | Government documents, laws, official archives |
| `kwanzaa_black_press` | Black newspapers (Chicago Defender, Amsterdam News, etc.) |
| `kwanzaa_speeches_letters` | Speeches, correspondence, rhetorical documents |
| `kwanzaa_black_stem` | STEM biographies, patents, scientific contributions |
| `kwanzaa_teaching_kits` | Lesson plans, curriculum, educational materials |
| `kwanzaa_dev_patterns` | Technical docs, code, RAG patterns |

---

## Persona Default Namespaces

| Persona | Searches These Namespaces By Default |
|---------|-------------------------------------|
| **Educator** | primary_sources, speeches_letters, teaching_kits |
| **Researcher** | ALL (all 6 namespaces) |
| **Creator** | speeches_letters, teaching_kits, black_press |
| **Builder** | dev_patterns, primary_sources |

---

## Required Provenance Fields (100% Mandatory)

Every chunk MUST have these 6 fields or it will be REJECTED:

1. `canonical_url` - Source URL (must start with http:// or https://)
2. `source_org` - Organization name (e.g., "National Archives")
3. `license` - Legal status (e.g., "Public Domain")
4. `year` - Publication year (integer, 1600-2100)
5. `content_type` - Document type (e.g., "speech", "legal_document")
6. `citation_label` - Human-readable citation

**Example**:
```json
{
  "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
  "source_org": "National Archives",
  "license": "Public Domain",
  "year": 1964,
  "content_type": "legal_document",
  "citation_label": "National Archives (1964) - Civil Rights Act"
}
```

---

## Common Content Types by Namespace

### kwanzaa_primary_sources
- `proclamation`
- `legal_document`
- `government_report`
- `treaty`
- `executive_order`

### kwanzaa_black_press
- `newspaper_article`
- `editorial`
- `column`
- `obituary`
- `announcement`

### kwanzaa_speeches_letters
- `speech`
- `letter`
- `sermon`
- `testimony`
- `radio_address`
- `interview`

### kwanzaa_black_stem
- `biography`
- `patent`
- `research_paper`
- `technical_document`
- `oral_history`

### kwanzaa_teaching_kits
- `lesson_plan`
- `curriculum_guide`
- `discussion_guide`
- `activity`
- `assessment`

### kwanzaa_dev_patterns
- `architecture_pattern`
- `prompt_template`
- `schema`
- `code_example`
- `best_practice`

---

## API Usage Examples

### Search Specific Namespace

```python
# Python SDK
results = client.search.semantic(
    query="civil rights legislation",
    namespace="kwanzaa_primary_sources",
    limit=10
)
```

```bash
# cURL
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "civil rights legislation",
    "namespace": "kwanzaa_primary_sources",
    "limit": 10
  }'
```

### Use Persona Defaults

```python
# Python SDK - uses educator's default namespaces
results = client.search.semantic(
    query="voting rights history",
    persona_key="educator"
)
```

### List All Namespaces

```bash
curl http://localhost:8000/api/v1/search/namespaces
```

---

## Database Queries

### Count Documents Per Namespace

```sql
SELECT
    namespace,
    COUNT(*) as chunk_count
FROM kw_retrieval_results
GROUP BY namespace
ORDER BY chunk_count DESC;
```

### Check Ingestion Status

```sql
SELECT
    namespace,
    status,
    docs_ingested,
    chunks_ingested,
    started_at
FROM kw_ingestion_runs
WHERE namespace = 'kwanzaa_primary_sources'
ORDER BY started_at DESC
LIMIT 10;
```

### Find Sources for Namespace

```sql
SELECT
    source_name,
    priority,
    license,
    default_namespace
FROM kw_source_manifest
WHERE default_namespace = 'kwanzaa_black_press';
```

---

## Validation Checklist (Before Ingestion)

Before ingesting a source, verify:

- [ ] Source has clear default_namespace
- [ ] All 6 provenance fields present for EVERY document
- [ ] canonical_url is valid HTTP(S) URL
- [ ] year is integer between 1600-2100
- [ ] license is specified (preferably Public Domain)
- [ ] source_org is official institutional name
- [ ] content_type matches namespace conventions
- [ ] citation_label is human-readable

**If ANY field is missing → DO NOT INGEST**

---

## Common Errors and Fixes

### Error: "Invalid namespace"

**Problem**: Namespace not one of the 6 allowed values

**Fix**: Use exact namespace name from the list:
- `kwanzaa_primary_sources`
- `kwanzaa_black_press`
- `kwanzaa_speeches_letters`
- `kwanzaa_black_stem`
- `kwanzaa_teaching_kits`
- `kwanzaa_dev_patterns`

### Error: "Missing required provenance fields"

**Problem**: One or more of the 6 required fields missing

**Fix**: Add all 6 fields to metadata:
1. canonical_url
2. source_org
3. license
4. year
5. content_type
6. citation_label

### Error: "Invalid year"

**Problem**: Year is not an integer or out of range

**Fix**: Ensure year is integer between 1600 and 2100

---

## Namespace Selection Examples

### Example 1: Civil Rights Act of 1964

**Source**: National Archives
**Type**: Legal document (federal law)
**Namespace**: `kwanzaa_primary_sources`
**Rationale**: Government-issued official document

---

### Example 2: Chicago Defender Article on March on Washington

**Source**: Chicago Defender (via Library of Congress)
**Type**: Newspaper article
**Namespace**: `kwanzaa_black_press`
**Rationale**: Black-owned newspaper coverage

---

### Example 3: MLK "I Have a Dream" Speech

**Source**: National Archives
**Type**: Speech transcript
**Namespace**: `kwanzaa_speeches_letters`
**Rationale**: Historical speech (rhetorical document)

---

### Example 4: Katherine Johnson NASA Biography

**Source**: NASA
**Type**: Biography
**Namespace**: `kwanzaa_black_stem`
**Rationale**: STEM contribution and biography

---

### Example 5: Smithsonian Civil Rights Lesson Plan

**Source**: Smithsonian
**Type**: Lesson plan
**Namespace**: `kwanzaa_teaching_kits`
**Rationale**: Curriculum-ready educational material

---

### Example 6: Kwanzaa answer_json Contract Documentation

**Source**: Kwanzaa GitHub repo
**Type**: Technical specification
**Namespace**: `kwanzaa_dev_patterns`
**Rationale**: Technical documentation for builders

---

## Threshold Recommendations

Different personas use different similarity thresholds:

| Persona | Threshold | Reasoning |
|---------|-----------|-----------|
| Educator | 0.80 | Stricter for accuracy in education |
| Researcher | 0.75 | Balanced precision/recall |
| Creator | 0.65 | More exploratory, creative freedom |
| Builder | 0.70 | Balanced for technical queries |

**Override in API**:
```json
{
  "query": "...",
  "namespace": "...",
  "threshold": 0.80
}
```

---

## When to Propose a New Namespace

Consider proposing a new namespace if:

1. **Volume**: Have >500 documents that don't fit existing namespaces
2. **Distinct Domain**: Content has clear domain boundaries
3. **Persona Need**: Addresses unmet persona requirement
4. **Clear Differentiation**: Can articulate why existing namespaces insufficient

**How to Propose**:
1. File GitHub issue with label `namespace:proposal`
2. Include: purpose, scope, content types, source orgs, rationale
3. Team reviews within 1 week
4. Community feedback period (2 weeks)

---

## Metrics to Track

### Per Namespace:
- Document count
- Chunk count
- Query volume (last 30 days)
- Citation success rate
- Ingestion success rate
- Provenance completeness (must be 100%)

### Overall:
- Namespace distribution of queries
- Cross-namespace query frequency
- Persona-namespace alignment

---

## Emergency Contacts

- **Architecture Questions**: File issue with label `namespace:architecture`
- **Ingestion Problems**: File issue with label `namespace:ingestion`
- **API Bugs**: File issue with label `namespace:api`
- **Data Curation**: File issue with label `namespace:curation`

GitHub: https://github.com/AINative-Studio/kwanzaa/issues

---

## Additional Resources

- **Full Strategy**: `/Users/aideveloper/kwanzaa/docs/architecture/namespace-strategy.md`
- **Implementation Checklist**: `/Users/aideveloper/kwanzaa/docs/architecture/namespace-implementation-checklist.md`
- **Summary**: `/Users/aideveloper/kwanzaa/docs/architecture/namespace-strategy-summary.md`
- **Data Model**: `/Users/aideveloper/kwanzaa/docs/architecture/datamodel.md`
- **API Spec**: `/Users/aideveloper/kwanzaa/docs/api/semantic-search-api.md`

---

## Print-Friendly Cheat Sheet

```
╔══════════════════════════════════════════════════════════════════╗
║              KWANZAA NAMESPACE QUICK REFERENCE                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  DECISION TREE:                                                  ║
║    Government doc?       → kwanzaa_primary_sources              ║
║    Black newspaper?      → kwanzaa_black_press                  ║
║    Speech/letter?        → kwanzaa_speeches_letters             ║
║    STEM biography?       → kwanzaa_black_stem                   ║
║    Lesson plan?          → kwanzaa_teaching_kits                ║
║    Technical doc?        → kwanzaa_dev_patterns                 ║
║                                                                  ║
║  REQUIRED PROVENANCE (100%):                                     ║
║    1. canonical_url     4. year                                 ║
║    2. source_org        5. content_type                         ║
║    3. license           6. citation_label                       ║
║                                                                  ║
║  PERSONA DEFAULTS:                                               ║
║    Educator    → primary_sources, speeches_letters              ║
║    Researcher  → ALL namespaces                                 ║
║    Creator     → speeches_letters, teaching_kits, black_press   ║
║    Builder     → dev_patterns, primary_sources                  ║
║                                                                  ║
║  VALIDATION RULE:                                                ║
║    Missing provenance = REJECTED (no exceptions)                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

**Version**: 1.0
**Last Updated**: 2026-01-16
**Print This Page**: Keep at your desk for quick reference
