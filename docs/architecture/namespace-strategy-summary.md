# Namespace Strategy - Executive Summary

**Document**: Epic 6 (Issue #14) - Namespace Strategy Finalization
**Status**: Complete
**Created**: 2026-01-16
**Full Documentation**: `/Users/aideveloper/kwanzaa/docs/architecture/namespace-strategy.md`

---

## Quick Overview

The Kwanzaa namespace strategy defines **6 core namespaces** that organize the corpus into persona-aligned collections. Each namespace enforces 100% provenance completeness and supports cited, transparent responses.

---

## The Six Namespaces

| Namespace | Purpose | Primary Persona | Priority | Target (MVP) |
|-----------|---------|----------------|----------|--------------|
| **kwanzaa_primary_sources** | Government documents, official records | Educator | P0 | 500-1,500 docs |
| **kwanzaa_black_press** | Historical Black newspapers, periodicals | Researcher | P0 | 1,000-3,000 docs |
| **kwanzaa_speeches_letters** | Speeches, letters, correspondence | Creator | P0 | 200-500 docs |
| **kwanzaa_black_stem** | STEM biographies, patents, contributions | Educator | P1 | 300-800 docs |
| **kwanzaa_teaching_kits** | Lesson plans, curriculum materials | Educator | P1 | 100-300 docs |
| **kwanzaa_dev_patterns** | Technical docs, RAG patterns, schemas | Builder | P0 | 50-150 docs |

**Total MVP Target**: 2,150-6,150 documents, 21,500+ chunks

---

## Key Architectural Decisions

### 1. Domain-First Organization
- Namespaces organized by knowledge domain and use case, not technical characteristics
- Enables natural persona-to-namespace mappings
- Clear contribution pathways for domain experts

### 2. Provenance as Foundation
Every chunk MUST include:
- `canonical_url` - Source URL
- `source_org` - Issuing organization
- `license` - Legal status
- `year` - Publication year
- `content_type` - Document type
- `citation_label` - Human-readable citation

**Enforcement**: Ingestion pipeline rejects incomplete metadata (100% requirement)

### 3. Namespace Independence
- Logically isolated but technically unified
- Same embedding model across all (BAAI/bge-small-en-v1.5, 1536 dims)
- Shared metadata schema
- Independent ingestion tracking
- Cross-namespace queries supported

### 4. Persona-Centric Design

| Persona | Primary Goal | Default Namespaces | Threshold |
|---------|-------------|-------------------|-----------|
| **Educator** | Citation-first answers | primary_sources, speeches_letters, teaching_kits | 0.80 |
| **Researcher** | Metadata-first discovery | All namespaces | 0.75 |
| **Creator** | Creative synthesis | speeches_letters, teaching_kits, black_press | 0.65 |
| **Builder** | Reusable RAG patterns | dev_patterns, primary_sources | 0.70 |

---

## Integration Points

### Database Schema Integration

**kw_source_manifest** - Sources declare their namespace:
```sql
default_namespace TEXT NOT NULL -- One of 6 namespaces
```

**kw_retrieval_runs** - Every search logs namespaces queried:
```sql
namespaces JSONB NOT NULL -- ["kwanzaa_primary_sources"]
```

**kw_retrieval_results** - Results include namespace:
```sql
namespace TEXT NOT NULL -- For provenance tracking
```

**kw_persona_presets** - Personas specify default namespaces:
```sql
default_namespaces JSONB NOT NULL -- ["kwanzaa_primary_sources", ...]
```

### API Integration

Search API supports namespace filtering:
```json
{
  "query": "civil rights legislation",
  "namespace": "kwanzaa_primary_sources",
  "filters": {"year_gte": 1960},
  "persona_key": "educator"
}
```

### Pydantic Models

**Action Required**: Add namespace validation to `SearchRequest`:
```python
@field_validator("namespace")
@classmethod
def validate_namespace(cls, v: Optional[str]) -> Optional[str]:
    allowed = [
        "kwanzaa_primary_sources",
        "kwanzaa_black_press",
        "kwanzaa_speeches_letters",
        "kwanzaa_black_stem",
        "kwanzaa_teaching_kits",
        "kwanzaa_dev_patterns",
    ]
    if v is not None and v not in allowed:
        raise ValueError(f"Invalid namespace. Must be one of: {allowed}")
    return v
```

---

## Namespace Selection Guide

**Quick Decision Tree**:

1. Government document or official record? → **kwanzaa_primary_sources**
2. Black newspaper or periodical? → **kwanzaa_black_press**
3. Speech, letter, or direct communication? → **kwanzaa_speeches_letters**
4. STEM biography or patent? → **kwanzaa_black_stem**
5. Curriculum or teaching material? → **kwanzaa_teaching_kits**
6. Technical docs or code? → **kwanzaa_dev_patterns**
7. None of the above? → Escalate for review

---

## Governance Process

### Adding a New Namespace

1. **Proposal**: Submit GitHub issue with label `namespace:proposal`
   - Include: purpose, scope, content types, source orgs, persona mapping, rationale
2. **Review**: Team review (1 week) + community feedback (2 weeks)
3. **Approval**: Project maintainers decide
4. **Implementation**: Update docs, schema, ingestion, persona presets

### Namespace Lifecycle

- **Proposal** → **Implementation** → **Maintenance** → **Deprecation** (if needed)
- Quality metrics tracked: provenance completeness, citation success, query recall
- Deprecation only if: low usage (<5% queries for 6 months), redundancy, quality issues

---

## Implementation Roadmap

### Phase 1: MVP Foundation (Week 1-2)
- Create all 6 namespaces in ZeroDB
- Update data model with namespace fields
- Implement namespace validation in API
- Update persona presets

**Deliverable**: All namespaces queryable via API

### Phase 2: Initial Corpus (Week 2-3)
- Populate P0 sources (2,150 docs, 21,500 chunks)
- Run metadata-first ingestion
- Selectively expand full-text
- Validate provenance completeness

**Deliverable**: 100% provenance complete corpus

### Phase 3: Persona Integration (Week 3)
- Configure persona presets with namespace mappings
- Implement threshold adjustments
- Add namespace recommendations to UI
- Create demo scripts

**Deliverable**: 4 persona presets fully functional

### Phase 4: Quality Assurance (Week 4)
- Run evaluation questions per namespace
- Measure citation coverage
- Test cross-namespace collections
- Gather user feedback

**Deliverable**: >90% citation coverage for educator/researcher

### Phase 5: Documentation (Ongoing)
- Publish namespace strategy
- Create contributor guides
- Establish governance process
- Monitor quality metrics

**Deliverable**: Community can contribute to correct namespaces

---

## Success Metrics

### Quantitative

| Metric | Target | Measurement |
|--------|--------|-------------|
| Provenance Completeness | 100% | % chunks with all required metadata |
| Ingestion Success Rate | >95% | % successful ingestion runs |
| Citation Generation Success | >95% | % results producing valid citations |
| Retrieval Hit Rate | >80% | % eval questions with relevant results |
| Citation Coverage (Educator) | >90% | % educator queries with citations or refusal |

### Qualitative

- User satisfaction with namespace clarity: >4.0/5.0
- Time for contributor to understand strategy: <30 minutes
- Namespace selection error rate: <10%

---

## Nguzo Saba Alignment

| Principle | Implementation |
|-----------|---------------|
| **Umoja (Unity)** | Consistent structure and naming across all namespaces |
| **Kujichagulia (Self-Determination)** | Users select specific namespaces for queries |
| **Ujima (Collective Work)** | Namespace decisions documented and auditable |
| **Ujamaa (Cooperative Economics)** | Open corpus enables community contributions |
| **Nia (Purpose)** | Education and research prioritized in design |
| **Kuumba (Creativity)** | Creator tools access rich rhetorical content |
| **Imani (Faith)** | Trust through complete provenance in every namespace |

---

## Action Items for Team

### For Backend Developers
1. Add namespace validation to `SearchRequest` model
2. Update `kw_source_manifest` with CHECK constraint for namespace
3. Implement namespace filtering in vector search
4. Add namespace tracking to `kw_retrieval_runs`

**Files to Update**:
- `/Users/aideveloper/kwanzaa/backend/app/models/search.py`
- Database migration scripts for new constraints

### For Data Curators
1. Review namespace definitions (full doc)
2. Use decision tree for source classification
3. Ensure all manifest entries have `default_namespace` field
4. Validate provenance completeness before ingestion

**Reference**: Section "Namespace Definitions" in full strategy doc

### For Frontend Developers
1. Add namespace selector to search UI
2. Display namespace badges on search results
3. Show persona-specific namespace recommendations
4. Add namespace filtering to Search Explorer

### For Documentation Team
1. Update API documentation with namespace examples
2. Create contributor guide referencing namespace strategy
3. Add namespace section to README
4. Create video walkthrough of namespace selection

---

## Example Queries by Namespace

### kwanzaa_primary_sources
```python
client.search.semantic(
    query="What did the Civil Rights Act of 1964 prohibit?",
    namespace="kwanzaa_primary_sources",
    persona_key="educator"
)
```

### kwanzaa_black_press
```python
client.search.semantic(
    query="Chicago Defender coverage of Emmett Till",
    namespace="kwanzaa_black_press",
    filters={"year": 1955}
)
```

### kwanzaa_speeches_letters
```python
client.search.semantic(
    query="rhetorical devices in I Have a Dream",
    namespace="kwanzaa_speeches_letters",
    persona_key="creator"
)
```

### kwanzaa_black_stem
```python
client.search.semantic(
    query="Katherine Johnson NASA contributions",
    namespace="kwanzaa_black_stem"
)
```

### kwanzaa_teaching_kits
```python
client.search.semantic(
    query="civil rights movement lesson plan",
    namespace="kwanzaa_teaching_kits",
    filters={"grade_level": "9-12"}
)
```

### kwanzaa_dev_patterns
```python
client.search.semantic(
    query="answer_json contract structure",
    namespace="kwanzaa_dev_patterns",
    persona_key="builder"
)
```

---

## Frequently Asked Questions

### Q: Can a source belong to multiple namespaces?
**A**: Sources have a single `default_namespace`, but cross-namespace **collections** can group content from multiple namespaces (e.g., a "Civil Rights Movement" collection spanning primary_sources, black_press, and speeches_letters).

### Q: What if a source doesn't fit any namespace?
**A**: Escalate for review. May indicate need for a new namespace (rare) or need to refine source type/scope.

### Q: Can users search across multiple namespaces?
**A**: Yes. Queries without a namespace filter search the persona's default namespaces. Multi-namespace queries are supported (future enhancement for explicit multi-namespace array).

### Q: How do we handle sources with incomplete metadata?
**A**: Ingestion pipeline REJECTS chunks with missing required provenance fields. This is enforced at 100% to maintain Imani (Faith).

### Q: Can we rename a namespace?
**A**: No - breaking change. If needed, create new namespace and migrate content with versioned plan.

### Q: How do private organizations add custom namespaces?
**A**: Future feature. Format would be `{org_prefix}_kwanzaa_{domain}` (e.g., `acme_kwanzaa_internal_curriculum`).

---

## Resources

- **Full Strategy Document**: `/Users/aideveloper/kwanzaa/docs/architecture/namespace-strategy.md` (48KB, comprehensive)
- **Data Model**: `/Users/aideveloper/kwanzaa/docs/architecture/datamodel.md`
- **Search API Spec**: `/Users/aideveloper/kwanzaa/docs/api/semantic-search-api.md`
- **Persona Definitions**: `/Users/aideveloper/kwanzaa/docs/planning/agents.md`
- **Ingestion Plan**: `/Users/aideveloper/kwanzaa/docs/planning/Data-Ingestion.md`

---

## Next Steps

1. **Team Review**: Schedule review meeting for full namespace strategy
2. **Backend Implementation**: Week 1-2 (Phase 1)
3. **Corpus Ingestion**: Week 2-3 (Phase 2)
4. **Persona Integration**: Week 3 (Phase 3)
5. **Launch QA**: Week 4 (Phase 4)

**Status Tracking**: Issue #14 (Epic 6: Namespaces)

---

**Questions or Feedback**: File issues at https://github.com/AINative-Studio/kwanzaa/issues with label `namespace:feedback`

**Document Owner**: Architecture Team
**Last Updated**: 2026-01-16
