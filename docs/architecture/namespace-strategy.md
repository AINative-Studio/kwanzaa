# Kwanzaa Namespace Strategy

**Version:** 1.0
**Status:** Finalized
**Epic:** Epic 6 (epic:namespaces) - Issue #14
**Last Updated:** 2026-01-16

---

## Executive Summary

This document defines the complete namespace architecture for the Kwanzaa MVP, a provenance-first AI system for Black history and culture. Namespaces organize the corpus into persona-aligned collections that support cited, transparent, culturally grounded responses.

The six namespaces are:
1. **kwanzaa_primary_sources** - Foundational historical documents
2. **kwanzaa_black_press** - Historical Black newspapers and periodicals
3. **kwanzaa_speeches_letters** - Rhetorical and correspondence documents
4. **kwanzaa_black_stem** - STEM contributions and biographies
5. **kwanzaa_teaching_kits** - Curriculum-ready educational materials
6. **kwanzaa_dev_patterns** - RAG patterns and technical documentation

These namespaces integrate seamlessly with the existing data model (kw_sources, kw_documents, kw_chunks) and enable persona-driven search (educator, researcher, creator, builder).

---

## Table of Contents

1. [Requirements Analysis](#requirements-analysis)
2. [Architecture Principles](#architecture-principles)
3. [Namespace Definitions](#namespace-definitions)
4. [Integration with Data Model](#integration-with-data-model)
5. [Persona-Namespace Mappings](#persona-namespace-mappings)
6. [Usage Guidelines](#usage-guidelines)
7. [Governance and Extension](#governance-and-extension)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Success Metrics](#success-metrics)

---

## Requirements Analysis

### Functional Requirements

1. **Provenance-First Organization**: Every namespace must enforce complete provenance metadata (canonical_url, license, year, source_org)
2. **Persona Alignment**: Namespaces must map to the four personas (educator, researcher, creator, builder)
3. **Search Isolation**: Queries can target specific namespaces without cross-contamination
4. **Filter Compatibility**: Namespace filtering must work alongside year, source_org, content_type, and tag filters
5. **Citation Support**: All content must support citation generation for answer_json contract
6. **Extensibility**: New namespaces can be added without breaking existing functionality

### Non-Functional Requirements

1. **Performance**: Namespace filtering must not degrade search latency (target <100ms overhead)
2. **Scalability**: Architecture must support 10,000+ documents and 100,000+ chunks per namespace
3. **Data Quality**: 100% provenance completeness enforced at ingestion time
4. **Maintainability**: Clear naming conventions and documentation for future contributors
5. **Nguzo Saba Alignment**: Architecture must reflect the Seven Principles

### Quality Attributes

- **Umoja (Unity)**: Consistent structure and naming across all namespaces
- **Kujichagulia (Self-Determination)**: Users can select specific namespaces for their queries
- **Ujima (Collective Work)**: Namespace decisions are documented and auditable
- **Ujamaa (Cooperative Economics)**: Open corpus design enables community contributions
- **Nia (Purpose)**: Education and research prioritized in namespace design
- **Kuumba (Creativity)**: Creator tools have access to rich rhetorical content
- **Imani (Faith)**: Trust through complete provenance in every namespace

---

## Architecture Principles

### 1. Domain-First Organization

Namespaces are organized by **knowledge domain and use case**, not by technical characteristics. This enables:
- Natural persona-to-namespace mappings
- Intuitive curator workflows
- Clear contribution pathways for domain experts

### 2. Provenance as Foundation

Every chunk in every namespace MUST include:
```json
{
  "canonical_url": "https://...",
  "source_org": "Library of Congress",
  "license": "Public Domain",
  "year": 1964,
  "content_type": "speech",
  "citation_label": "Library of Congress (1964) - Title"
}
```

**Enforcement**: Ingestion pipeline rejects any chunk missing required fields.

### 3. Namespace Independence

Namespaces are **logically isolated** but **technically unified**:
- Each namespace uses the same embedding model (BAAI/bge-small-en-v1.5, 1536 dimensions)
- Shared metadata schema across all namespaces
- Independent ingestion runs tracked per namespace
- Cross-namespace queries supported via multi-namespace search

### 4. Persona-Centric Design

Namespaces map to user journeys:

| Persona | Primary Goal | Primary Namespaces |
|---------|-------------|-------------------|
| Educator | Citation-first answers for students | primary_sources, speeches_letters |
| Researcher | Metadata-first discovery | All namespaces, especially black_press |
| Creator | Creative synthesis with grounding | speeches_letters, teaching_kits |
| Builder | Reusable RAG patterns | dev_patterns, primary_sources |

### 5. First Fruits Philosophy

MVP focuses on **small, high-signal, P0 sources**:
- Quality > quantity
- Public domain and government archives prioritized
- Selective full-text expansion (P0 only in MVP)
- Metadata-first import for all sources

---

## Namespace Definitions

### 1. kwanzaa_primary_sources

**Purpose**: Foundational historical documents with the highest provenance requirements. This is the "ground truth" namespace for historical facts.

**Scope**:
- Government documents (legislation, court rulings, executive orders)
- National Archives records
- Library of Congress collections
- Historical treaties and proclamations
- Official government reports on civil rights, reconstruction, etc.

**Content Types**:
- `proclamation` - Official declarations
- `legal_document` - Laws, court rulings, legislation
- `government_report` - Official reports and studies
- `treaty` - Formal agreements
- `executive_order` - Presidential directives

**Source Organizations** (Examples):
- National Archives and Records Administration (NARA)
- Library of Congress
- U.S. Supreme Court
- National Park Service
- Federal government agencies

**Quality Gates**:
- **Provenance Completeness**: 100% required (canonical_url, license, year, source_org)
- **License**: Must be Public Domain or U.S. Government work
- **Verification**: Two-source verification for historical claims
- **Citation Format**: APA-style with institutional authority

**Target Volume** (MVP):
- Documents: 500-1,500
- Chunks: 5,000-15,000

**Persona Priority**: Educator (primary), Researcher (primary), Creator (secondary)

**Ingestion Priority**: P0 (highest)

**Example Entry**:
```json
{
  "chunk_id": "nara_cra_1964::chunk::3",
  "doc_id": "nara_cra_1964",
  "namespace": "kwanzaa_primary_sources",
  "content": "An Act to enforce the constitutional right to vote...",
  "metadata": {
    "citation_label": "National Archives (1964) - Civil Rights Act",
    "canonical_url": "https://www.archives.gov/milestone-documents/civil-rights-act",
    "source_org": "National Archives",
    "year": 1964,
    "content_type": "legal_document",
    "license": "Public Domain",
    "tags": ["civil_rights", "legislation", "voting_rights"]
  }
}
```

**Use Cases**:
- Student research papers requiring primary source citations
- Fact-checking historical claims
- Legal and policy analysis
- Timeline construction for history education

---

### 2. kwanzaa_black_press

**Purpose**: Historical context, community perspectives, and reportage from Black-owned newspapers and periodicals. Provides cultural context and contemporary accounts.

**Scope**:
- Historical Black newspapers (Chicago Defender, Amsterdam News, Pittsburgh Courier, etc.)
- Black periodicals and magazines
- Community newsletters and publications
- Historical archives from university collections

**Content Types**:
- `newspaper_article` - News reporting
- `editorial` - Opinion pieces
- `column` - Regular columnist writing
- `advertisement` - Historical advertisements (cultural context)
- `obituary` - Community records
- `announcement` - Event and community news

**Source Organizations** (Examples):
- Library of Congress (Chronicling America)
- University digital archives (Howard, Spelman, Morehouse)
- Internet Archive newspaper collections
- State historical societies
- Black Press Archives

**Quality Gates**:
- **Provenance Completeness**: 100% required
- **Date Range**: Focus on 1863-1975 for MVP (expandable)
- **License**: Public Domain or explicit permission
- **Digitization Quality**: OCR accuracy >95%

**Target Volume** (MVP):
- Documents: 1,000-3,000
- Chunks: 10,000-30,000

**Persona Priority**: Researcher (primary), Educator (secondary), Creator (secondary)

**Ingestion Priority**: P0 (high)

**Example Entry**:
```json
{
  "chunk_id": "chicagodefender_1955_08_28::chunk::5",
  "doc_id": "chicagodefender_1955_08_28",
  "namespace": "kwanzaa_black_press",
  "content": "The murder of 14-year-old Emmett Till in Mississippi...",
  "metadata": {
    "citation_label": "Chicago Defender (August 28, 1955)",
    "canonical_url": "https://www.loc.gov/item/sn84026847/1955-08-28/",
    "source_org": "Chicago Defender / Library of Congress",
    "year": 1955,
    "content_type": "newspaper_article",
    "license": "Public Domain",
    "tags": ["civil_rights", "emmett_till", "mississippi", "violence"]
  }
}
```

**Use Cases**:
- Cultural context for historical events
- Contemporary perspectives on historical moments
- Timeline analysis of community responses
- Primary source material for social history

---

### 3. kwanzaa_speeches_letters

**Purpose**: Rhetorical and correspondence documents for analyzing language, persuasion, and historical communication. Essential for creators and educators teaching rhetoric.

**Scope**:
- Historical speeches by Black leaders and activists
- Personal and public correspondence
- Sermons and religious addresses
- Testimony before Congress
- Radio addresses and broadcasts

**Content Types**:
- `speech` - Public addresses
- `letter` - Personal and public correspondence
- `sermon` - Religious addresses
- `testimony` - Congressional or legal testimony
- `radio_address` - Broadcast speeches
- `interview` - Recorded conversations

**Source Organizations** (Examples):
- Library of Congress
- National Archives
- University special collections
- Presidential libraries
- Civil rights organization archives

**Quality Gates**:
- **Provenance Completeness**: 100% required
- **Attribution**: Speaker/author clearly identified
- **Context**: Date, location, and occasion documented
- **Transcription Quality**: Human-verified preferred

**Target Volume** (MVP):
- Documents: 200-500
- Chunks: 2,000-5,000

**Persona Priority**: Creator (primary), Educator (primary), Researcher (secondary)

**Ingestion Priority**: P0 (high)

**Example Entry**:
```json
{
  "chunk_id": "mlk_ihaveadream_1963::chunk::12",
  "doc_id": "mlk_ihaveadream_1963",
  "namespace": "kwanzaa_speeches_letters",
  "content": "I have a dream that one day this nation will rise up...",
  "metadata": {
    "citation_label": "Martin Luther King Jr. (August 28, 1963) - I Have a Dream",
    "canonical_url": "https://www.archives.gov/files/press/exhibits/dream-speech.pdf",
    "source_org": "National Archives",
    "year": 1963,
    "content_type": "speech",
    "license": "Public Domain",
    "speaker": "Martin Luther King Jr.",
    "location": "Washington, D.C.",
    "event": "March on Washington",
    "tags": ["civil_rights", "march_on_washington", "rhetoric", "equality"]
  }
}
```

**Use Cases**:
- Teaching rhetorical analysis
- Creative writing prompts grounded in historical language
- Speech structure for content creators
- Historical context for quotes and attributions

---

### 4. kwanzaa_black_stem

**Purpose**: Document contributions to science, technology, engineering, and mathematics. Counter erasure narratives and provide role models for STEM education.

**Scope**:
- Biographies of Black scientists, inventors, engineers, mathematicians
- Patent records and technical documents
- University archives and academic papers
- NASA and government STEM archives
- Historical society records

**Content Types**:
- `biography` - Life stories and career histories
- `patent` - Patent records and technical specifications
- `research_paper` - Academic publications
- `technical_document` - Engineering and scientific documentation
- `oral_history` - First-person accounts
- `obituary` - Professional records

**Source Organizations** (Examples):
- Smithsonian National Museum of African American History and Culture
- NASA archives
- U.S. Patent and Trademark Office
- National Society of Black Engineers archives
- University STEM diversity initiatives

**Quality Gates**:
- **Provenance Completeness**: 100% required
- **Subject Identification**: Name, field, and contributions clearly documented
- **Technical Accuracy**: Peer-reviewed or institutionally verified
- **Image Rights**: Patent diagrams and photos properly licensed

**Target Volume** (MVP):
- Documents: 300-800
- Chunks: 3,000-8,000

**Persona Priority**: Educator (primary), Researcher (secondary), Creator (secondary)

**Ingestion Priority**: P1 (medium-high)

**Example Entry**:
```json
{
  "chunk_id": "nasa_katherine_johnson_bio::chunk::7",
  "doc_id": "nasa_katherine_johnson_bio",
  "namespace": "kwanzaa_black_stem",
  "content": "Katherine Johnson calculated the trajectory for Alan Shepard's 1961 mission...",
  "metadata": {
    "citation_label": "NASA (2020) - Katherine Johnson Biography",
    "canonical_url": "https://www.nasa.gov/content/katherine-johnson-biography",
    "source_org": "NASA",
    "year": 2020,
    "content_type": "biography",
    "license": "Public Domain",
    "subject_name": "Katherine Johnson",
    "field": "Mathematics",
    "tags": ["nasa", "space_program", "mathematics", "women_in_stem"]
  }
}
```

**Use Cases**:
- STEM curriculum development
- Role model identification for students
- Historical STEM timeline construction
- Countering erasure narratives

---

### 5. kwanzaa_teaching_kits

**Purpose**: Curriculum-ready materials for educators. Structured, classroom-safe content with learning objectives and discussion prompts.

**Scope**:
- Lesson plans from trusted educational organizations
- Curriculum guides from museums and historical societies
- Educational resources from civil rights organizations
- Discussion guides and reflection prompts
- Assessment rubrics and learning objectives

**Content Types**:
- `lesson_plan` - Structured teaching materials
- `curriculum_guide` - Multi-lesson sequences
- `discussion_guide` - Facilitation materials
- `activity` - Hands-on learning activities
- `assessment` - Evaluation tools
- `resource_list` - Curated reading lists

**Source Organizations** (Examples):
- Smithsonian museums
- National Park Service education programs
- Teaching Tolerance / Learning for Justice
- National Council for the Social Studies
- State education departments

**Quality Gates**:
- **Provenance Completeness**: 100% required
- **Grade Level**: Clearly specified
- **Learning Objectives**: Explicitly stated
- **Safety Review**: Classroom-appropriate language and content
- **Standards Alignment**: Connected to educational standards (when applicable)

**Target Volume** (MVP):
- Documents: 100-300
- Chunks: 1,000-3,000

**Persona Priority**: Educator (primary), Creator (secondary)

**Ingestion Priority**: P1 (medium)

**Example Entry**:
```json
{
  "chunk_id": "nps_selma_lesson_plan::chunk::3",
  "doc_id": "nps_selma_lesson_plan",
  "namespace": "kwanzaa_teaching_kits",
  "content": "Learning Objective: Students will analyze the events of Bloody Sunday...",
  "metadata": {
    "citation_label": "National Park Service - Selma to Montgomery Teaching Guide",
    "canonical_url": "https://www.nps.gov/subjects/teachingwithhistoricplaces/selma.htm",
    "source_org": "National Park Service",
    "year": 2019,
    "content_type": "lesson_plan",
    "license": "Public Domain",
    "grade_level": "9-12",
    "duration": "2 class periods",
    "tags": ["voting_rights", "civil_rights", "lesson_plan", "high_school"]
  }
}
```

**Use Cases**:
- Direct classroom implementation
- Curriculum planning for Kwanzaa celebrations
- Parent education resources
- Homeschool lesson planning

---

### 6. kwanzaa_dev_patterns

**Purpose**: Technical documentation for builders implementing culturally grounded RAG systems. Reusable patterns, schemas, and best practices.

**Scope**:
- RAG architecture patterns
- Prompt engineering examples
- Schema definitions and contracts
- Evaluation frameworks
- API documentation
- Best practices guides

**Content Types**:
- `architecture_pattern` - System design patterns
- `prompt_template` - Reusable prompts
- `schema` - Data structure definitions
- `code_example` - Implementation snippets
- `best_practice` - Guidelines and recommendations
- `evaluation_framework` - Testing and quality assurance

**Source Organizations** (Examples):
- AINative platform documentation
- Kwanzaa project internal documentation
- Open-source RAG frameworks
- AI ethics organizations
- Academic research on culturally grounded AI

**Quality Gates**:
- **Provenance Completeness**: 100% required
- **Technical Accuracy**: Code tested and validated
- **Documentation Quality**: Clear explanations and examples
- **License Clarity**: MIT or Apache 2.0 preferred
- **Version Tracking**: Software versions specified

**Target Volume** (MVP):
- Documents: 50-150
- Chunks: 500-1,500

**Persona Priority**: Builder (primary)

**Ingestion Priority**: P0 (documentation for MVP)

**Example Entry**:
```json
{
  "chunk_id": "kwanzaa_answer_json_contract::chunk::1",
  "doc_id": "kwanzaa_answer_json_contract",
  "namespace": "kwanzaa_dev_patterns",
  "content": "The answer_json contract enforces 'show your work' transparency...",
  "metadata": {
    "citation_label": "Kwanzaa Project - Answer JSON Contract v1.0",
    "canonical_url": "https://github.com/ainative-studio/kwanzaa/docs/answer_json_contract.md",
    "source_org": "AINative Studio",
    "year": 2026,
    "content_type": "schema",
    "license": "Apache 2.0",
    "version": "1.0",
    "tags": ["rag", "contract", "citation", "transparency"]
  }
}
```

**Use Cases**:
- Building culturally grounded RAG systems
- Implementing citation enforcement
- Replicating Kwanzaa architecture patterns
- Contributing to the open-source project

---

## Integration with Data Model

### Database Schema Integration

The namespace strategy integrates seamlessly with the existing ZeroDB data model defined in `/Users/aideveloper/kwanzaa/docs/architecture/datamodel.md`.

#### kw_source_manifest

The `default_namespace` field in `kw_source_manifest` specifies which namespace each ingestion job targets:

```sql
CREATE TABLE kw_source_manifest (
  id UUID PRIMARY KEY,
  job_id TEXT UNIQUE NOT NULL,
  source_name TEXT NOT NULL,
  source_type TEXT NOT NULL,
  base_url TEXT NOT NULL,
  access_method TEXT NOT NULL,
  license TEXT NOT NULL,
  priority TEXT NOT NULL, -- P0 | P1 | P2
  default_namespace TEXT NOT NULL, -- One of the 6 namespaces
  tags JSONB NOT NULL,
  schedule TEXT NOT NULL,
  query_templates JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Validation Rules**:
- `default_namespace` MUST be one of: `kwanzaa_primary_sources`, `kwanzaa_black_press`, `kwanzaa_speeches_letters`, `kwanzaa_black_stem`, `kwanzaa_teaching_kits`, `kwanzaa_dev_patterns`
- Enforced via CHECK constraint or application-level validation

#### kw_documents

Documents are not directly tagged with namespaces (they're source-level), but the lineage is:
```
kw_source_manifest.default_namespace
  -> kw_documents (via job_id)
  -> kw_chunks (embedded in namespace)
```

#### kw_chunks (ZeroDB Embeddings)

Chunks are stored in ZeroDB embeddings with namespace as a metadata field:

```json
{
  "id": "nara_cra_1964::chunk::3",
  "namespace": "kwanzaa_primary_sources",
  "embedding": [0.123, -0.456, ...],
  "metadata": {
    "doc_id": "nara_cra_1964",
    "chunk_index": 3,
    "canonical_url": "https://...",
    "source_org": "National Archives",
    "year": 1964,
    "content_type": "legal_document",
    "license": "Public Domain",
    "citation_label": "National Archives (1964) - Civil Rights Act",
    "tags": ["civil_rights", "legislation"]
  }
}
```

**Key Integration Points**:
1. **Ingestion**: `kw_ingestion_runs` tracks which namespace was populated
2. **Retrieval**: `kw_retrieval_runs.namespaces` stores which namespaces were queried
3. **Citations**: `kw_citations_used` references chunks by namespace and chunk_id
4. **Collections**: `kw_collection_items.namespace` enables cross-namespace curation

#### kw_persona_presets

Persona presets specify default namespaces for each user journey:

```sql
CREATE TABLE kw_persona_presets (
  id UUID PRIMARY KEY,
  key TEXT UNIQUE NOT NULL, -- educator | researcher | creator | builder
  display_name TEXT NOT NULL,
  description TEXT,
  default_namespaces JSONB NOT NULL,
  -- e.g., ["kwanzaa_primary_sources", "kwanzaa_speeches_letters"]
  default_filters JSONB NULL,
  require_citations_default BOOLEAN DEFAULT TRUE,
  primary_sources_only_default BOOLEAN DEFAULT FALSE,
  creative_mode_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### kw_retrieval_runs

Every search logs which namespaces were queried:

```sql
CREATE TABLE kw_retrieval_runs (
  id UUID PRIMARY KEY,
  session_id UUID NOT NULL,
  user_message_id UUID NOT NULL,
  assistant_message_id UUID NULL,
  query TEXT NOT NULL,
  top_k INT DEFAULT 8,
  namespaces JSONB NOT NULL, -- ["kwanzaa_primary_sources"]
  filters JSONB NULL,
  embedding_model TEXT NOT NULL DEFAULT 'BAAI/bge-small-en-v1.5',
  retrieval_latency_ms INT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### kw_retrieval_results

Results include namespace for provenance tracking:

```sql
CREATE TABLE kw_retrieval_results (
  id UUID PRIMARY KEY,
  retrieval_run_id UUID NOT NULL,
  namespace TEXT NOT NULL, -- Namespace where chunk was found
  chunk_id TEXT NOT NULL,
  doc_id TEXT NOT NULL,
  score NUMERIC NOT NULL,
  rank INT NOT NULL,
  snippet TEXT NULL,
  metadata JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Search API Integration

The semantic search API (`/api/v1/search/semantic`) supports namespace filtering:

```json
{
  "query": "What did the Civil Rights Act of 1964 prohibit?",
  "namespace": "kwanzaa_primary_sources",
  "filters": {
    "year_gte": 1960,
    "year_lte": 1970
  },
  "limit": 10,
  "threshold": 0.7,
  "persona_key": "educator"
}
```

**Multi-Namespace Search** (Future Enhancement):
```json
{
  "query": "civil rights legislation",
  "namespaces": ["kwanzaa_primary_sources", "kwanzaa_black_press"],
  "filters": {...}
}
```

### Pydantic Models Integration

The existing `SearchRequest` model in `/Users/aideveloper/kwanzaa/backend/app/models/search.py` supports namespace filtering:

```python
class SearchRequest(BaseModel):
    query: str
    namespace: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Vector namespace to search within",
    )
    filters: Optional[ProvenanceFilters] = None
    limit: Optional[int] = Field(default=10, ge=1, le=100)
    threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    persona_key: Optional[str] = Field(
        default=None,
        pattern="^(educator|researcher|creator|builder)$",
    )
```

**Enhancement Needed**: Add namespace validation:
```python
@field_validator("namespace")
@classmethod
def validate_namespace(cls, v: Optional[str]) -> Optional[str]:
    """Validate namespace against allowed values."""
    if v is None:
        return v

    allowed_namespaces = [
        "kwanzaa_primary_sources",
        "kwanzaa_black_press",
        "kwanzaa_speeches_letters",
        "kwanzaa_black_stem",
        "kwanzaa_teaching_kits",
        "kwanzaa_dev_patterns",
    ]

    if v not in allowed_namespaces:
        raise ValueError(f"Invalid namespace. Must be one of: {allowed_namespaces}")

    return v
```

---

## Persona-Namespace Mappings

### Educator Persona

**Primary Goal**: Citation-first, classroom-safe answers for students

**Default Namespaces**:
1. `kwanzaa_primary_sources` (primary)
2. `kwanzaa_speeches_letters` (secondary)
3. `kwanzaa_teaching_kits` (secondary)

**Default Settings**:
- `require_citations`: `true`
- `primary_sources_only`: `true`
- `creative_mode`: `false`
- `threshold`: `0.80` (stricter for accuracy)

**Typical Queries**:
- "What did the Voting Rights Act of 1965 accomplish?"
- "When was the Emancipation Proclamation signed?"
- "Who spoke at the March on Washington?"

**Answer Behavior**:
- Always cite primary sources when available
- Refuse if no supporting corpus evidence
- Include educational context in unknowns section
- Suggest teaching_kits resources when relevant

**Namespace Priority Order**:
1. kwanzaa_primary_sources (ground truth)
2. kwanzaa_speeches_letters (historical context)
3. kwanzaa_teaching_kits (pedagogical support)

---

### Researcher Persona

**Primary Goal**: Metadata-first discovery across comprehensive corpus

**Default Namespaces**: All namespaces
1. `kwanzaa_primary_sources`
2. `kwanzaa_black_press`
3. `kwanzaa_speeches_letters`
4. `kwanzaa_black_stem`
5. `kwanzaa_teaching_kits`
6. `kwanzaa_dev_patterns`

**Default Settings**:
- `require_citations`: `true`
- `primary_sources_only`: `false`
- `creative_mode`: `false`
- `threshold`: `0.75` (balanced precision/recall)

**Typical Queries**:
- "Timeline of Black Press coverage of Brown v. Board of Education"
- "Cross-reference civil rights legislation with newspaper coverage"
- "STEM contributions during the Space Race era"

**Answer Behavior**:
- Provide multi-source citations
- Highlight gaps and inconsistencies
- Surface metadata for further investigation
- Enable cross-namespace comparison

**Namespace Priority Order**: Context-dependent, but typically:
1. kwanzaa_black_press (contemporary perspectives)
2. kwanzaa_primary_sources (official records)
3. kwanzaa_speeches_letters (firsthand accounts)
4. kwanzaa_black_stem (technical contributions)

---

### Creator Persona

**Primary Goal**: Creative synthesis with grounding (but allow exploration)

**Default Namespaces**:
1. `kwanzaa_speeches_letters` (primary - rhetorical models)
2. `kwanzaa_teaching_kits` (secondary - structured content)
3. `kwanzaa_black_press` (tertiary - cultural context)

**Default Settings**:
- `require_citations`: `false` (but encouraged)
- `primary_sources_only`: `false`
- `creative_mode`: `true`
- `threshold`: `0.65` (more exploratory)

**Typical Queries**:
- "What rhetorical devices did MLK use in the I Have a Dream speech?"
- "Help me write a speech about unity using historical language patterns"
- "Generate discussion prompts for a Kwanzaa celebration"

**Answer Behavior**:
- Provide creative suggestions grounded in retrieved content
- Cite rhetorical patterns and language structures
- Offer optional citations (not required)
- Warn about out-of-corpus creative extrapolation

**Namespace Priority Order**:
1. kwanzaa_speeches_letters (language models)
2. kwanzaa_teaching_kits (structured guidance)
3. kwanzaa_black_press (cultural context)

---

### Builder Persona

**Primary Goal**: Reusable RAG patterns and technical implementation

**Default Namespaces**:
1. `kwanzaa_dev_patterns` (primary)
2. `kwanzaa_primary_sources` (secondary - for testing)

**Default Settings**:
- `require_citations`: `true`
- `primary_sources_only`: `false`
- `creative_mode`: `false`
- `threshold`: `0.70` (balanced)

**Typical Queries**:
- "Show me the answer_json contract structure"
- "How does the citation enforcement logic work?"
- "What's the best practice for chunking historical documents?"
- "Sample prompt for refusal behavior"

**Answer Behavior**:
- Provide code examples and schemas
- Link to technical documentation
- Include implementation notes
- Reference related patterns

**Namespace Priority Order**:
1. kwanzaa_dev_patterns (technical docs)
2. kwanzaa_primary_sources (test corpus)

---

## Usage Guidelines

### For Data Curators

#### Adding Sources to Namespaces

1. **Identify Namespace**: Determine which namespace best fits the source
   - Primary source documents → `kwanzaa_primary_sources`
   - Newspaper archives → `kwanzaa_black_press`
   - Speeches/letters → `kwanzaa_speeches_letters`
   - STEM biographies → `kwanzaa_black_stem`
   - Lesson plans → `kwanzaa_teaching_kits`
   - Technical docs → `kwanzaa_dev_patterns`

2. **Validate Provenance**: Ensure all required metadata exists:
   - canonical_url
   - source_org
   - license
   - year
   - content_type

3. **Add to Manifest**: Update `kw_source_manifest` with:
   ```json
   {
     "job_id": "nara_civil_rights_collection",
     "source_name": "NARA Civil Rights Collection",
     "source_type": "archive",
     "base_url": "https://www.archives.gov/...",
     "access_method": "api",
     "license": "Public Domain",
     "priority": "P0",
     "default_namespace": "kwanzaa_primary_sources",
     "tags": ["civil_rights", "government", "legislation"]
   }
   ```

4. **Run Ingestion**: Execute ingestion job for the namespace
5. **Validate Results**: Check `kw_ingestion_runs` for success/errors

#### Namespace Selection Decision Tree

```
Is it a government document or official record?
  YES → kwanzaa_primary_sources
  NO → Continue

Is it from a Black newspaper or periodical?
  YES → kwanzaa_black_press
  NO → Continue

Is it a speech, letter, or direct communication?
  YES → kwanzaa_speeches_letters
  NO → Continue

Is it about STEM contributions or scientists?
  YES → kwanzaa_black_stem
  NO → Continue

Is it curriculum or teaching material?
  YES → kwanzaa_teaching_kits
  NO → Continue

Is it technical documentation or code?
  YES → kwanzaa_dev_patterns
  NO → Escalate for review (may need new namespace)
```

---

### For Application Developers

#### Querying Specific Namespaces

```python
from kwanzaa_client import KwanzaaClient

client = KwanzaaClient(api_key=API_KEY)

# Single namespace query
results = client.search.semantic(
    query="civil rights legislation",
    namespace="kwanzaa_primary_sources",
    filters={"year_gte": 1960, "year_lte": 1970},
    limit=10
)

# Persona-driven query (uses preset namespaces)
results = client.search.semantic(
    query="voting rights history",
    persona_key="educator"
)
```

#### Handling Multi-Namespace Results

```python
# Group results by namespace
from collections import defaultdict

namespace_results = defaultdict(list)
for result in results:
    namespace_results[result.namespace].append(result)

# Process by priority
for namespace in ["kwanzaa_primary_sources", "kwanzaa_black_press"]:
    if namespace in namespace_results:
        print(f"\n{namespace}:")
        for result in namespace_results[namespace]:
            print(f"  - {result.metadata.citation_label}")
```

#### Citation Generation

```python
def generate_citation(result: SearchResult) -> str:
    """Generate APA-style citation from search result."""
    meta = result.metadata

    if result.namespace == "kwanzaa_primary_sources":
        return f"{meta.source_org}. ({meta.year}). {meta.citation_label}. {meta.canonical_url}"

    elif result.namespace == "kwanzaa_black_press":
        return f"{meta.source_org}. ({meta.year}). {meta.citation_label}. Retrieved from {meta.canonical_url}"

    # Add more namespace-specific citation formats...
```

---

### For Educators

#### Restricting to Safe Namespaces

Educators working with K-12 students should restrict queries to vetted namespaces:

```python
SAFE_NAMESPACES = [
    "kwanzaa_primary_sources",
    "kwanzaa_teaching_kits",
    "kwanzaa_black_stem"  # Biography content pre-vetted
]

# Classroom-safe query
results = client.search.semantic(
    query=student_question,
    namespace="kwanzaa_primary_sources",  # Or any SAFE_NAMESPACE
    persona_key="educator"
)
```

#### Suggested Namespace by Grade Level

| Grade Level | Primary Namespace | Secondary Namespaces |
|-------------|------------------|---------------------|
| K-5 | kwanzaa_teaching_kits | kwanzaa_black_stem (biographies) |
| 6-8 | kwanzaa_primary_sources, kwanzaa_teaching_kits | kwanzaa_speeches_letters |
| 9-12 | kwanzaa_primary_sources, kwanzaa_speeches_letters | kwanzaa_black_press |
| College | All namespaces | All namespaces |

---

## Governance and Extension

### Namespace Lifecycle

#### 1. Proposal Phase

**When to Propose a New Namespace**:
- Existing namespaces don't fit the source domain
- Volume of content justifies separate organization (>500 documents)
- Distinct persona need not met by current namespaces
- Clear use case differentiation

**Proposal Requirements**:
1. **Namespace Name**: Follow convention `kwanzaa_{domain}`
2. **Purpose Statement**: 1-2 sentences
3. **Scope Definition**: What's included/excluded
4. **Content Types**: List of expected content_type values
5. **Source Organizations**: Example sources
6. **Persona Mapping**: Which personas benefit
7. **Target Volume**: Estimated doc/chunk counts
8. **Rationale**: Why existing namespaces are insufficient

**Proposal Template**:
```markdown
## Namespace Proposal: kwanzaa_[domain]

**Purpose**: [One sentence]

**Scope**: [What's included]

**Content Types**: [List]

**Source Organizations**: [Examples]

**Persona Priority**: [Ordered list]

**Target Volume**: [Estimates]

**Rationale**: [Why needed]

**Success Metrics**: [How we'll measure value]
```

**Review Process**:
1. Submit proposal as GitHub issue with label `namespace:proposal`
2. Team review within 1 week
3. Community feedback period (2 weeks for major namespaces)
4. Approval by project maintainers
5. Implementation plan created

---

#### 2. Implementation Phase

**Steps to Add a New Namespace**:

1. **Update Documentation**:
   - Add namespace definition to this document
   - Update API documentation
   - Add to persona preset mappings

2. **Update Schema Validation**:
   - Add namespace to allowed values in `SearchRequest` validator
   - Update `kw_source_manifest` CHECK constraint
   - Add to frontend dropdown options

3. **Create Initial Manifest Entries**:
   - Add at least 3 P0 sources to `kw_source_manifest`
   - Ensure complete provenance for all sources

4. **Configure Ingestion**:
   - Set up ingestion jobs for new namespace
   - Configure chunking parameters (if different from defaults)
   - Test with small batch first

5. **Validate Results**:
   - Run test queries against new namespace
   - Verify metadata completeness
   - Check citation generation

6. **Update Persona Presets**:
   - Add namespace to relevant `kw_persona_presets.default_namespaces`
   - Adjust thresholds if needed

7. **Document and Communicate**:
   - Update README and contributor guides
   - Announce new namespace to community
   - Provide usage examples

---

#### 3. Maintenance Phase

**Ongoing Responsibilities**:
- Monitor ingestion success rates
- Review quality metrics (provenance completeness)
- Address curator questions and edge cases
- Prune or merge if namespace proves redundant

**Quality Metrics** (per namespace):
- Provenance completeness: 100% (enforced)
- Citation generation success rate: >95%
- Query recall (eval set): >80%
- User satisfaction: Qualitative feedback

**Deprecation Criteria**:
- Low usage (<5% of queries) for 6 months
- Better served by existing namespace
- Source quality issues unresolvable
- Community consensus for removal

---

### Naming Conventions

#### Namespace Names

**Format**: `kwanzaa_{domain}`

**Rules**:
- All lowercase
- Use underscores (not hyphens or camelCase)
- Descriptive but concise (2-3 words max)
- Domain-focused (not technical characteristics)

**Good Examples**:
- `kwanzaa_primary_sources`
- `kwanzaa_black_press`
- `kwanzaa_oral_histories`

**Bad Examples**:
- `kwanzaa_HighPrioritySources` (use lowercase)
- `kwanzaa-speeches` (use underscores)
- `kwanzaa_1536_dim_vectors` (avoid technical details)
- `kwanzaa_misc` (too vague)

#### Content Types

**Format**: `lowercase_underscore`

**Rules**:
- Descriptive and specific
- Consistent within namespace
- Maximum 3 words
- No technical jargon

**Examples**:
- `speech`, `letter`, `newspaper_article`
- `biography`, `patent`, `research_paper`
- `lesson_plan`, `discussion_guide`

#### Source Organization Names

**Format**: Official institutional name

**Rules**:
- Use full official name
- Include disambiguators when needed
- Consistent capitalization

**Examples**:
- "National Archives and Records Administration (NARA)"
- "Library of Congress"
- "Chicago Defender / Library of Congress" (for collections)

---

### Extension Guidelines

#### Cross-Namespace Collections

Collections can span multiple namespaces:

```sql
-- Example: Civil Rights Movement collection
INSERT INTO kw_corpus_collections (key, display_name, default_namespaces) VALUES (
  'civil_rights_movement',
  'Civil Rights Movement (1954-1968)',
  '["kwanzaa_primary_sources", "kwanzaa_black_press", "kwanzaa_speeches_letters"]'
);

-- Add items from different namespaces
INSERT INTO kw_collection_items (collection_id, namespace, doc_id) VALUES
  ('civil_rights_collection_id', 'kwanzaa_primary_sources', 'brown_v_board'),
  ('civil_rights_collection_id', 'kwanzaa_black_press', 'montgomery_bus_boycott_coverage'),
  ('civil_rights_collection_id', 'kwanzaa_speeches_letters', 'mlk_letter_birmingham_jail');
```

#### Namespace Hierarchies (Future)

Not implemented in MVP, but future versions could support sub-namespaces:
- `kwanzaa_primary_sources::legislation`
- `kwanzaa_primary_sources::court_rulings`

This would enable finer-grained filtering while maintaining logical grouping.

#### Private/Custom Namespaces (Future)

Organizations deploying Kwanzaa could create private namespaces:
- Format: `{org_prefix}_kwanzaa_{domain}`
- Example: `acme_kwanzaa_internal_curriculum`
- Isolated from public namespaces

---

### Version Control

This namespace strategy document is versioned:

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-16 | Initial namespace strategy | Architecture Team |

**Update Protocol**:
1. Major changes (new namespaces, restructuring): Increment major version (2.0)
2. Minor changes (clarifications, examples): Increment minor version (1.1)
3. Typos and formatting: No version change, document in commit

**Backward Compatibility**:
- Existing namespaces cannot be renamed (breaking change)
- New namespaces are additive (non-breaking)
- Content migration between namespaces requires versioned plan

---

## Implementation Roadmap

### Phase 1: MVP Foundation (Week 1-2)

**Goal**: Establish core namespaces and ingestion pipeline

**Tasks**:
1. Create all 6 namespaces in ZeroDB
2. Update `kw_source_manifest` table with namespace field
3. Implement namespace validation in API
4. Add namespace filtering to search endpoint
5. Update persona presets with default namespaces

**Deliverables**:
- All 6 namespaces created and documented
- Namespace validation in place
- API supports namespace filtering

**Success Criteria**:
- All namespaces queryable via API
- Namespace filter works in semantic search
- Provenance completeness enforced at 100%

---

### Phase 2: Initial Corpus (Week 2-3)

**Goal**: Populate P0 sources across namespaces

**Target Volumes**:
- `kwanzaa_primary_sources`: 500 docs, 5,000 chunks
- `kwanzaa_black_press`: 1,000 docs, 10,000 chunks
- `kwanzaa_speeches_letters`: 200 docs, 2,000 chunks
- `kwanzaa_black_stem`: 300 docs, 3,000 chunks
- `kwanzaa_teaching_kits`: 100 docs, 1,000 chunks
- `kwanzaa_dev_patterns`: 50 docs, 500 chunks

**Tasks**:
1. Create manifest entries for P0 sources
2. Run metadata-first ingestion for all namespaces
3. Selectively expand full-text for P0 sources
4. Validate provenance completeness
5. Run test queries per namespace

**Deliverables**:
- 2,150 documents ingested
- 21,500+ chunks embedded
- All with complete provenance

**Success Criteria**:
- 100% provenance completeness
- <5% ingestion error rate
- Test queries return relevant results per namespace

---

### Phase 3: Persona Integration (Week 3)

**Goal**: Connect namespaces to persona-driven workflows

**Tasks**:
1. Populate `kw_persona_presets` table with namespace mappings
2. Implement persona-specific threshold adjustments
3. Add namespace recommendations to UI
4. Create demo scripts per persona showing namespace usage
5. Test citation coverage per persona/namespace combination

**Deliverables**:
- 4 persona presets fully configured
- UI displays namespace recommendations
- Demo scripts for each persona

**Success Criteria**:
- Educator queries default to primary_sources
- Researcher queries span all namespaces
- Creator queries prioritize speeches_letters
- Builder queries use dev_patterns

---

### Phase 4: Quality Assurance (Week 4)

**Goal**: Validate namespace strategy effectiveness

**Tasks**:
1. Run evaluation questions per namespace
2. Measure citation coverage by namespace
3. Test cross-namespace collections
4. Validate metadata consistency
5. Gather user feedback on namespace clarity

**Deliverables**:
- Evaluation report per namespace
- Citation coverage metrics
- User feedback summary

**Success Criteria**:
- Citation coverage >90% for educator/researcher modes
- Retrieval hit rate >80% per namespace
- Zero provenance gaps in production corpus

---

### Phase 5: Documentation and Governance (Ongoing)

**Goal**: Enable community contributions and extensions

**Tasks**:
1. Publish namespace strategy (this document)
2. Create contributor guide for namespace selection
3. Establish namespace proposal process
4. Set up monitoring and quality dashboards
5. Document lessons learned and best practices

**Deliverables**:
- Published namespace documentation
- Contributor guidelines
- Governance process
- Quality monitoring dashboard

**Success Criteria**:
- External contributors successfully add sources to correct namespaces
- Namespace proposal process operational
- Quality metrics tracked and visible

---

## Success Metrics

### Quantitative Metrics

#### Namespace Health

| Metric | Target | Measurement |
|--------|--------|-------------|
| Provenance Completeness | 100% | % chunks with all required metadata |
| Ingestion Success Rate | >95% | % successful ingestion runs per namespace |
| Query Latency | <100ms | p95 search latency with namespace filter |
| Citation Generation Success | >95% | % results that produce valid citations |

#### Usage Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Namespace Query Distribution | Balanced | % queries per namespace |
| Multi-Namespace Queries | <30% | % queries spanning >1 namespace |
| Namespace Coverage in Results | >80% | % queries returning results from intended namespace |
| Persona-Namespace Alignment | >90% | % persona queries using expected namespaces |

#### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Retrieval Hit Rate | >80% | % eval questions with relevant results per namespace |
| Citation Coverage (Educator) | >90% | % educator queries with citations or refusal |
| Citation Coverage (Researcher) | >90% | % researcher queries with citations |
| False Positive Rate | <5% | % results from wrong namespace in filtered queries |

---

### Qualitative Metrics

#### User Satisfaction

- Survey question: "Did the namespace filtering help you find relevant sources?"
  - Target: >4.0/5.0 average rating

- Survey question: "Are the namespace names clear and intuitive?"
  - Target: >4.0/5.0 average rating

#### Community Engagement

- Number of namespace proposals submitted
  - Target: >3 proposals in first 6 months

- Number of sources contributed per namespace
  - Target: >20 sources per namespace from external contributors in year 1

#### Documentation Quality

- Time for new contributor to understand namespace strategy
  - Target: <30 minutes to read and comprehend this document

- Number of namespace selection errors by curators
  - Target: <10% error rate

---

### Evaluation Questions by Namespace

#### kwanzaa_primary_sources

1. What did the Civil Rights Act of 1964 prohibit?
2. When was the Emancipation Proclamation signed?
3. What were the key provisions of the Voting Rights Act of 1965?
4. Summarize Brown v. Board of Education.
5. What did Executive Order 8802 establish?

**Expected Behavior**:
- 100% should return primary source citations
- 0% should refuse (corpus should cover these)

---

#### kwanzaa_black_press

1. How did the Chicago Defender cover the Emmett Till murder?
2. What was the Black Press reaction to Brown v. Board?
3. Timeline of Pittsburgh Courier coverage of the Montgomery Bus Boycott.
4. How did Black newspapers cover WWII?
5. What advertisements appeared in the Amsterdam News in the 1950s?

**Expected Behavior**:
- >80% should return Black Press citations
- Some may supplement with primary_sources for context
- May refuse if specific dates not in corpus

---

#### kwanzaa_speeches_letters

1. What rhetorical devices did MLK use in "I Have a Dream"?
2. Analyze the structure of Malcolm X's "Ballot or the Bullet" speech.
3. What did Frederick Douglass argue in his 4th of July speech?
4. Summarize James Baldwin's letter to his nephew.
5. What metaphors appear in Sojourner Truth's speeches?

**Expected Behavior**:
- 100% should cite speech/letter texts
- May include rhetorical analysis
- Should highlight specific language patterns

---

#### kwanzaa_black_stem

1. Who was Katherine Johnson and what did she contribute to NASA?
2. What did George Washington Carver invent?
3. Who was the first Black astronaut?
4. What patents did Garrett Morgan hold?
5. Tell me about Mae Jemison's career.

**Expected Behavior**:
- >80% should return biographical citations
- May include patent records where applicable
- May refuse if specific details not in corpus

---

#### kwanzaa_teaching_kits

1. Show me a lesson plan about the Civil Rights Movement.
2. What discussion questions work for teaching about Reconstruction?
3. How do I teach about Kwanzaa principles in elementary school?
4. What activities help students understand the Great Migration?
5. Provide an assessment rubric for a civil rights research project.

**Expected Behavior**:
- >80% should return lesson plan or curriculum citations
- Should include grade-level guidance
- May suggest adaptations

---

#### kwanzaa_dev_patterns

1. Show me the answer_json contract structure.
2. How does citation enforcement work in Kwanzaa?
3. What's the best practice for chunking historical documents?
4. How do I implement persona-driven search?
5. What embedding model does Kwanzaa use?

**Expected Behavior**:
- 100% should cite technical documentation
- Should include code examples where applicable
- Should link to related patterns

---

## Appendices

### Appendix A: Namespace Comparison Table

| Feature | primary_sources | black_press | speeches_letters | black_stem | teaching_kits | dev_patterns |
|---------|----------------|-------------|------------------|------------|---------------|-------------|
| Primary Persona | Educator | Researcher | Creator | Educator | Educator | Builder |
| Priority | P0 | P0 | P0 | P1 | P1 | P0 |
| Target Docs (MVP) | 500-1,500 | 1,000-3,000 | 200-500 | 300-800 | 100-300 | 50-150 |
| Target Chunks (MVP) | 5K-15K | 10K-30K | 2K-5K | 3K-8K | 1K-3K | 500-1.5K |
| License Types | Public Domain, Gov | Public Domain, Permitted | Public Domain, Permitted | Public Domain, Permitted | Public Domain, Educational | MIT, Apache 2.0 |
| Citation Required | Yes | Yes | Yes | Yes | Yes | Yes |
| Creative Mode | No | No | Allowed | No | Allowed | No |
| Threshold (Default) | 0.80 | 0.75 | 0.65 | 0.75 | 0.70 | 0.70 |

---

### Appendix B: Migration Path from Unstructured Corpus

If you have an existing corpus without namespaces:

**Step 1: Audit Existing Sources**
```sql
SELECT source_org, content_type, COUNT(*)
FROM kw_chunks
GROUP BY source_org, content_type
ORDER BY COUNT(*) DESC;
```

**Step 2: Map Sources to Namespaces**
Create mapping:
```json
{
  "National Archives": "kwanzaa_primary_sources",
  "Library of Congress": "kwanzaa_primary_sources",
  "Chicago Defender": "kwanzaa_black_press",
  ...
}
```

**Step 3: Backfill Namespace Metadata**
```python
def assign_namespace(chunk):
    source_org = chunk["metadata"]["source_org"]
    content_type = chunk["metadata"]["content_type"]

    if source_org in ["National Archives", "NARA"]:
        return "kwanzaa_primary_sources"
    elif "Defender" in source_org or "Press" in source_org:
        return "kwanzaa_black_press"
    # Add more logic...

    return None  # Flag for manual review

# Update all chunks
for chunk in existing_chunks:
    namespace = assign_namespace(chunk)
    if namespace:
        update_chunk_namespace(chunk.id, namespace)
    else:
        flag_for_manual_review(chunk.id)
```

**Step 4: Validate Migration**
- Check 100% chunks have namespace
- Verify persona queries work as expected
- Run evaluation questions per namespace

---

### Appendix C: Namespace Decision Flowchart

```
START
  |
  v
Is it government-issued or official?
  |
  +--YES--> kwanzaa_primary_sources
  |
  +--NO--> Is it from Black Press?
             |
             +--YES--> kwanzaa_black_press
             |
             +--NO--> Is it a speech/letter?
                        |
                        +--YES--> kwanzaa_speeches_letters
                        |
                        +--NO--> Is it STEM-related?
                                   |
                                   +--YES--> kwanzaa_black_stem
                                   |
                                   +--NO--> Is it curriculum/teaching?
                                              |
                                              +--YES--> kwanzaa_teaching_kits
                                              |
                                              +--NO--> Is it technical docs?
                                                         |
                                                         +--YES--> kwanzaa_dev_patterns
                                                         |
                                                         +--NO--> NEEDS REVIEW
```

---

### Appendix D: Sample Ingestion Run

Example `kw_ingestion_runs` entry showing namespace tracking:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "job_id": "nara_civil_rights_1964",
  "run_type": "fulltext_expand",
  "status": "success",
  "started_at": "2026-01-16T10:00:00Z",
  "ended_at": "2026-01-16T10:15:32Z",
  "docs_attempted": 150,
  "docs_ingested": 148,
  "chunks_ingested": 1480,
  "namespace": "kwanzaa_primary_sources",
  "errors": [
    {
      "doc_id": "nara_missing_license",
      "error": "Missing required field: license"
    },
    {
      "doc_id": "nara_invalid_year",
      "error": "Year out of valid range: 2100"
    }
  ],
  "run_notes": "P0 ingestion for Civil Rights Act documents"
}
```

---

### Appendix E: Namespace Stats Dashboard (Proposed)

Recommended metrics dashboard per namespace:

```
Namespace: kwanzaa_primary_sources
├── Document Count: 1,250
├── Chunk Count: 8,940
├── Provenance Completeness: 100%
├── Source Organizations: 12
│   ├── National Archives: 45%
│   ├── Library of Congress: 30%
│   └── Others: 25%
├── Content Types:
│   ├── legal_document: 40%
│   ├── proclamation: 30%
│   ├── government_report: 20%
│   └── Others: 10%
├── Year Range: 1863-2025
├── Query Volume (Last 30d): 2,340 queries
├── Average Query Latency: 45ms
├── Citation Success Rate: 96%
└── Last Ingestion: 2026-01-15
```

---

## Conclusion

The Kwanzaa namespace strategy provides a robust, extensible architecture for organizing culturally grounded knowledge. By aligning namespaces with personas, enforcing provenance at every level, and following the Nguzo Saba principles, this system delivers trustworthy, cited, transparent AI responses.

The six namespaces—primary_sources, black_press, speeches_letters, black_stem, teaching_kits, and dev_patterns—cover the MVP scope while enabling future growth. Clear governance processes ensure quality and community participation.

**Next Steps**:
1. Review this strategy with the team
2. Implement Phase 1 (Foundation) - Week 1-2
3. Begin Phase 2 (Initial Corpus) - Week 2-3
4. Monitor metrics and iterate based on feedback

**Questions or Feedback**: File issues at https://github.com/AINative-Studio/kwanzaa/issues with label `namespace:feedback`

---

**Document Approval**:
- Architecture Team: [Pending]
- Product Team: [Pending]
- Community Review: [Pending]

**Implementation Tracking**: Issue #14 (Epic 6: Namespaces)
