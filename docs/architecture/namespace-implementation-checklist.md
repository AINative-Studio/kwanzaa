# Namespace Strategy - Implementation Checklist

**Epic**: Epic 6 (Issue #14) - Namespace Strategy
**Status**: Ready for Implementation
**Created**: 2026-01-16

This checklist provides actionable tasks for implementing the Kwanzaa namespace strategy. Each task includes specific files to modify, code snippets, and acceptance criteria.

---

## Phase 1: MVP Foundation (Week 1-2)

### Backend - Data Model Updates

#### Task 1.1: Add Namespace Validation to SearchRequest Model

**File**: `/Users/aideveloper/kwanzaa/backend/app/models/search.py`

**Action**: Add field validator after line 141 (after persona_key field):

```python
ALLOWED_NAMESPACES = [
    "kwanzaa_primary_sources",
    "kwanzaa_black_press",
    "kwanzaa_speeches_letters",
    "kwanzaa_black_stem",
    "kwanzaa_teaching_kits",
    "kwanzaa_dev_patterns",
]

@field_validator("namespace")
@classmethod
def validate_namespace(cls, v: Optional[str]) -> Optional[str]:
    """Validate namespace against allowed values."""
    if v is None:
        return v

    if v not in ALLOWED_NAMESPACES:
        raise ValueError(
            f"Invalid namespace '{v}'. Must be one of: {ALLOWED_NAMESPACES}"
        )

    return v
```

**Acceptance Criteria**:
- [ ] Validation rejects invalid namespace names
- [ ] All 6 valid namespaces accepted
- [ ] None/null namespace allowed (defaults to persona preset)
- [ ] Tests pass for valid and invalid cases

**Test Cases**:
```python
# Valid
assert SearchRequest(query="test", namespace="kwanzaa_primary_sources")
assert SearchRequest(query="test", namespace=None)

# Invalid - should raise ValueError
with pytest.raises(ValueError):
    SearchRequest(query="test", namespace="invalid_namespace")
```

---

#### Task 1.2: Create Namespace Constants Module

**File**: `/Users/aideveloper/kwanzaa/backend/app/core/namespaces.py` (new file)

**Action**: Create centralized namespace definitions:

```python
"""Namespace constants and utilities for Kwanzaa corpus organization."""

from enum import Enum
from typing import Dict, List


class KwanzaaNamespace(str, Enum):
    """Enumeration of valid Kwanzaa namespaces."""

    PRIMARY_SOURCES = "kwanzaa_primary_sources"
    BLACK_PRESS = "kwanzaa_black_press"
    SPEECHES_LETTERS = "kwanzaa_speeches_letters"
    BLACK_STEM = "kwanzaa_black_stem"
    TEACHING_KITS = "kwanzaa_teaching_kits"
    DEV_PATTERNS = "kwanzaa_dev_patterns"


# Namespace metadata for UI and documentation
NAMESPACE_METADATA: Dict[str, Dict[str, any]] = {
    KwanzaaNamespace.PRIMARY_SOURCES: {
        "display_name": "Primary Sources",
        "description": "Government documents, official records, and archival materials",
        "icon": "file-text",
        "color": "#1E40AF",  # blue-800
        "primary_persona": "educator",
        "priority": "P0",
    },
    KwanzaaNamespace.BLACK_PRESS: {
        "display_name": "Black Press",
        "description": "Historical Black newspapers and periodicals",
        "icon": "newspaper",
        "color": "#7C2D12",  # amber-900
        "primary_persona": "researcher",
        "priority": "P0",
    },
    KwanzaaNamespace.SPEECHES_LETTERS: {
        "display_name": "Speeches & Letters",
        "description": "Rhetorical documents and correspondence",
        "icon": "message-square",
        "color": "#4C1D95",  # purple-900
        "primary_persona": "creator",
        "priority": "P0",
    },
    KwanzaaNamespace.BLACK_STEM: {
        "display_name": "Black STEM",
        "description": "STEM contributions, biographies, and patents",
        "icon": "flask",
        "color": "#064E3B",  # emerald-900
        "primary_persona": "educator",
        "priority": "P1",
    },
    KwanzaaNamespace.TEACHING_KITS: {
        "display_name": "Teaching Kits",
        "description": "Curriculum materials and lesson plans",
        "icon": "book-open",
        "color": "#DC2626",  # red-600
        "primary_persona": "educator",
        "priority": "P1",
    },
    KwanzaaNamespace.DEV_PATTERNS: {
        "display_name": "Dev Patterns",
        "description": "Technical documentation and RAG patterns",
        "icon": "code",
        "color": "#374151",  # gray-700
        "primary_persona": "builder",
        "priority": "P0",
    },
}


def get_namespace_display_name(namespace: str) -> str:
    """Get human-readable display name for namespace."""
    return NAMESPACE_METADATA.get(namespace, {}).get("display_name", namespace)


def get_namespaces_for_persona(persona_key: str) -> List[str]:
    """Get default namespaces for a given persona."""
    persona_namespaces = {
        "educator": [
            KwanzaaNamespace.PRIMARY_SOURCES,
            KwanzaaNamespace.SPEECHES_LETTERS,
            KwanzaaNamespace.TEACHING_KITS,
        ],
        "researcher": list(KwanzaaNamespace),  # All namespaces
        "creator": [
            KwanzaaNamespace.SPEECHES_LETTERS,
            KwanzaaNamespace.TEACHING_KITS,
            KwanzaaNamespace.BLACK_PRESS,
        ],
        "builder": [
            KwanzaaNamespace.DEV_PATTERNS,
            KwanzaaNamespace.PRIMARY_SOURCES,
        ],
    }

    return [ns.value for ns in persona_namespaces.get(persona_key, [])]


def validate_namespace(namespace: str) -> bool:
    """Check if namespace is valid."""
    return namespace in [ns.value for ns in KwanzaaNamespace]
```

**Acceptance Criteria**:
- [ ] All 6 namespaces defined in enum
- [ ] Metadata includes display names, descriptions, personas
- [ ] Helper functions work correctly
- [ ] Module importable throughout backend

---

#### Task 1.3: Add Namespace Endpoint to API

**File**: `/Users/aideveloper/kwanzaa/backend/app/api/v1/endpoints/search.py`

**Action**: Add new endpoint after search endpoint (around line 100):

```python
from app.core.namespaces import NAMESPACE_METADATA, KwanzaaNamespace

@router.get("/namespaces")
async def list_namespaces(
    persona_key: Optional[str] = Query(
        None,
        description="Filter namespaces by persona",
        regex="^(educator|researcher|creator|builder)$",
    )
) -> dict:
    """
    List available namespaces and their metadata.

    If persona_key is provided, highlights namespaces relevant to that persona.
    """
    namespaces = []

    for ns in KwanzaaNamespace:
        metadata = NAMESPACE_METADATA[ns.value].copy()
        metadata["name"] = ns.value

        # Highlight if relevant to persona
        if persona_key:
            metadata["is_recommended"] = (
                metadata.get("primary_persona") == persona_key
            )

        namespaces.append(metadata)

    return {
        "status": "success",
        "namespaces": namespaces,
        "total": len(namespaces),
    }
```

**Acceptance Criteria**:
- [ ] GET `/api/v1/search/namespaces` returns all namespaces
- [ ] Includes display_name, description, icon, color
- [ ] Query param `?persona_key=educator` filters recommendations
- [ ] Response matches API contract format

**Test**:
```bash
curl http://localhost:8000/api/v1/search/namespaces

curl http://localhost:8000/api/v1/search/namespaces?persona_key=educator
```

---

### Database - Schema Updates

#### Task 1.4: Add Namespace to kw_source_manifest Table

**File**: Create `/Users/aideveloper/kwanzaa/backend/migrations/add_namespace_to_manifest.sql`

**Action**: Add namespace column with validation:

```sql
-- Add namespace column to kw_source_manifest
ALTER TABLE kw_source_manifest
ADD COLUMN default_namespace TEXT;

-- Add CHECK constraint for valid namespaces
ALTER TABLE kw_source_manifest
ADD CONSTRAINT valid_namespace CHECK (
    default_namespace IN (
        'kwanzaa_primary_sources',
        'kwanzaa_black_press',
        'kwanzaa_speeches_letters',
        'kwanzaa_black_stem',
        'kwanzaa_teaching_kits',
        'kwanzaa_dev_patterns'
    )
);

-- Make it NOT NULL after backfilling existing data
-- (Run this separately after backfill)
-- ALTER TABLE kw_source_manifest
-- ALTER COLUMN default_namespace SET NOT NULL;

-- Add index for namespace queries
CREATE INDEX idx_source_manifest_namespace
ON kw_source_manifest(default_namespace);

-- Comment for documentation
COMMENT ON COLUMN kw_source_manifest.default_namespace IS
'Namespace for organizing sources by domain (e.g., kwanzaa_primary_sources)';
```

**Acceptance Criteria**:
- [ ] Column added to table
- [ ] CHECK constraint prevents invalid namespaces
- [ ] Index created for performance
- [ ] Existing rows handled (null allowed temporarily)

---

#### Task 1.5: Add Namespace Tracking to kw_ingestion_runs

**File**: Create `/Users/aideveloper/kwanzaa/backend/migrations/add_namespace_to_ingestion_runs.sql`

**Action**:

```sql
-- Add namespace to ingestion runs for tracking
ALTER TABLE kw_ingestion_runs
ADD COLUMN namespace TEXT;

-- Add CHECK constraint
ALTER TABLE kw_ingestion_runs
ADD CONSTRAINT valid_ingestion_namespace CHECK (
    namespace IN (
        'kwanzaa_primary_sources',
        'kwanzaa_black_press',
        'kwanzaa_speeches_letters',
        'kwanzaa_black_stem',
        'kwanzaa_teaching_kits',
        'kwanzaa_dev_patterns'
    )
);

-- Add index
CREATE INDEX idx_ingestion_runs_namespace
ON kw_ingestion_runs(namespace, started_at DESC);

COMMENT ON COLUMN kw_ingestion_runs.namespace IS
'Namespace populated by this ingestion run';
```

**Acceptance Criteria**:
- [ ] Column added to table
- [ ] Constraint enforced
- [ ] Index created
- [ ] Can query ingestion runs by namespace

---

#### Task 1.6: Create Persona Presets Table

**File**: Create `/Users/aideveloper/kwanzaa/backend/migrations/create_persona_presets.sql`

**Action**:

```sql
-- Create persona presets table
CREATE TABLE kw_persona_presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    default_namespaces JSONB NOT NULL DEFAULT '[]'::jsonb,
    default_filters JSONB NULL,
    require_citations_default BOOLEAN DEFAULT TRUE,
    primary_sources_only_default BOOLEAN DEFAULT FALSE,
    creative_mode_default BOOLEAN DEFAULT FALSE,
    threshold_default NUMERIC DEFAULT 0.7,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add CHECK constraint for valid persona keys
ALTER TABLE kw_persona_presets
ADD CONSTRAINT valid_persona_key CHECK (
    key IN ('educator', 'researcher', 'creator', 'builder')
);

-- Create index
CREATE INDEX idx_persona_presets_key ON kw_persona_presets(key);

-- Insert default persona presets
INSERT INTO kw_persona_presets (
    key, display_name, description, default_namespaces,
    require_citations_default, primary_sources_only_default,
    creative_mode_default, threshold_default
) VALUES
(
    'educator',
    'Educator',
    'Citation-first, classroom-safe answers for students',
    '["kwanzaa_primary_sources", "kwanzaa_speeches_letters", "kwanzaa_teaching_kits"]'::jsonb,
    true,
    true,
    false,
    0.80
),
(
    'researcher',
    'Researcher',
    'Metadata-first discovery across comprehensive corpus',
    '["kwanzaa_primary_sources", "kwanzaa_black_press", "kwanzaa_speeches_letters", "kwanzaa_black_stem", "kwanzaa_teaching_kits", "kwanzaa_dev_patterns"]'::jsonb,
    true,
    false,
    false,
    0.75
),
(
    'creator',
    'Creator',
    'Creative synthesis with grounding',
    '["kwanzaa_speeches_letters", "kwanzaa_teaching_kits", "kwanzaa_black_press"]'::jsonb,
    false,
    false,
    true,
    0.65
),
(
    'builder',
    'Builder',
    'Reusable RAG patterns and technical implementation',
    '["kwanzaa_dev_patterns", "kwanzaa_primary_sources"]'::jsonb,
    true,
    false,
    false,
    0.70
);
```

**Acceptance Criteria**:
- [ ] Table created with all fields
- [ ] 4 persona presets inserted
- [ ] Constraints enforced
- [ ] Default namespaces stored as JSONB arrays

---

### Configuration Updates

#### Task 1.7: Add Namespace Config

**File**: `/Users/aideveloper/kwanzaa/backend/app/core/config.py`

**Action**: Add namespace configuration section:

```python
from typing import List

class Settings(BaseSettings):
    # ... existing settings ...

    # Namespace configuration
    ALLOWED_NAMESPACES: List[str] = [
        "kwanzaa_primary_sources",
        "kwanzaa_black_press",
        "kwanzaa_speeches_letters",
        "kwanzaa_black_stem",
        "kwanzaa_teaching_kits",
        "kwanzaa_dev_patterns",
    ]

    DEFAULT_NAMESPACE: str = "kwanzaa_primary_sources"

    # Persona-namespace mappings
    PERSONA_DEFAULT_NAMESPACES: dict = {
        "educator": ["kwanzaa_primary_sources", "kwanzaa_speeches_letters", "kwanzaa_teaching_kits"],
        "researcher": ["kwanzaa_primary_sources", "kwanzaa_black_press", "kwanzaa_speeches_letters", "kwanzaa_black_stem", "kwanzaa_teaching_kits", "kwanzaa_dev_patterns"],
        "creator": ["kwanzaa_speeches_letters", "kwanzaa_teaching_kits", "kwanzaa_black_press"],
        "builder": ["kwanzaa_dev_patterns", "kwanzaa_primary_sources"],
    }

    class Config:
        env_file = ".env"
```

**Acceptance Criteria**:
- [ ] Config values accessible via `settings.ALLOWED_NAMESPACES`
- [ ] Can be overridden via environment variables
- [ ] Used consistently across application

---

## Phase 2: Initial Corpus Population (Week 2-3)

### Ingestion Updates

#### Task 2.1: Update Ingestion Pipeline to Support Namespaces

**File**: Create `/Users/aideveloper/kwanzaa/backend/app/services/ingestion.py` (or update existing)

**Action**: Ensure ingestion respects namespace from manifest:

```python
async def ingest_source(source_manifest: dict) -> dict:
    """
    Ingest a source into its designated namespace.

    Args:
        source_manifest: Dict with keys: job_id, source_name, default_namespace, etc.

    Returns:
        Ingestion run result with stats
    """
    namespace = source_manifest.get("default_namespace")

    if not namespace or namespace not in ALLOWED_NAMESPACES:
        raise ValueError(f"Invalid namespace: {namespace}")

    # Create ingestion run record
    run_id = await create_ingestion_run(
        job_id=source_manifest["job_id"],
        namespace=namespace,
        run_type="metadata_import"
    )

    try:
        # Fetch documents from source
        documents = await fetch_documents(source_manifest)

        # Process each document
        for doc in documents:
            # Validate provenance completeness
            validate_provenance(doc)

            # Chunk document
            chunks = chunk_document(doc)

            # Embed and store in ZeroDB with namespace
            for chunk in chunks:
                await store_chunk_with_namespace(
                    chunk=chunk,
                    namespace=namespace,
                    doc_metadata=doc.metadata
                )

        # Update run status
        await update_ingestion_run(run_id, status="success", stats=...)

    except Exception as e:
        await update_ingestion_run(run_id, status="failed", errors=[str(e)])
        raise

    return {"run_id": run_id, "namespace": namespace, ...}
```

**Acceptance Criteria**:
- [ ] Ingestion reads namespace from source manifest
- [ ] Validates namespace before processing
- [ ] Stores chunks in correct ZeroDB namespace
- [ ] Logs namespace in kw_ingestion_runs
- [ ] Enforces provenance completeness (100%)

---

#### Task 2.2: Create Manifest Entries for P0 Sources

**File**: Create `/Users/aideveloper/kwanzaa/data/manifests/first_fruits_p0.json`

**Action**: Define initial P0 sources:

```json
{
  "manifest_version": "1.0",
  "created_at": "2026-01-16",
  "sources": [
    {
      "job_id": "nara_civil_rights_1964",
      "source_name": "NARA Civil Rights Act Collection",
      "source_type": "archive",
      "base_url": "https://www.archives.gov/...",
      "access_method": "api",
      "license": "Public Domain",
      "priority": "P0",
      "default_namespace": "kwanzaa_primary_sources",
      "tags": ["civil_rights", "legislation", "government"],
      "schedule": "weekly",
      "query_templates": [
        {"type": "api_query", "endpoint": "/search", "params": {...}}
      ],
      "estimated_documents": 150,
      "notes": "High-priority civil rights legislation"
    },
    {
      "job_id": "loc_chicago_defender_1940_1960",
      "source_name": "Chicago Defender Archive (1940-1960)",
      "source_type": "newspaper",
      "base_url": "https://www.loc.gov/collections/chicago-defender/",
      "access_method": "bulk_download",
      "license": "Public Domain",
      "priority": "P0",
      "default_namespace": "kwanzaa_black_press",
      "tags": ["newspaper", "black_press", "civil_rights_era"],
      "schedule": "monthly",
      "estimated_documents": 5000,
      "notes": "Core Black Press coverage of civil rights era"
    },
    {
      "job_id": "nara_mlk_speeches",
      "source_name": "Martin Luther King Jr. Speeches",
      "source_type": "archive",
      "base_url": "https://www.archives.gov/...",
      "access_method": "manual_curated",
      "license": "Public Domain",
      "priority": "P0",
      "default_namespace": "kwanzaa_speeches_letters",
      "tags": ["speech", "mlk", "civil_rights", "rhetoric"],
      "schedule": "one_time",
      "estimated_documents": 50,
      "notes": "Foundational rhetorical texts"
    }
  ]
}
```

**Acceptance Criteria**:
- [ ] At least 3 sources per namespace (P0)
- [ ] All required fields present
- [ ] default_namespace specified for each source
- [ ] Validates against manifest schema

---

#### Task 2.3: Create Provenance Validation Function

**File**: `/Users/aideveloper/kwanzaa/backend/app/utils/provenance.py` (new file)

**Action**:

```python
"""Provenance validation utilities."""

from typing import Dict, List, Optional


REQUIRED_PROVENANCE_FIELDS = [
    "canonical_url",
    "source_org",
    "license",
    "year",
    "content_type",
    "citation_label",
]


class ProvenanceValidationError(Exception):
    """Raised when provenance validation fails."""
    pass


def validate_provenance(metadata: Dict) -> None:
    """
    Validate that all required provenance fields are present and valid.

    Args:
        metadata: Document or chunk metadata dictionary

    Raises:
        ProvenanceValidationError: If any required field is missing or invalid
    """
    missing_fields = []

    for field in REQUIRED_PROVENANCE_FIELDS:
        if field not in metadata or metadata[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise ProvenanceValidationError(
            f"Missing required provenance fields: {missing_fields}. "
            f"Cannot ingest without complete provenance. "
            f"Metadata: {metadata}"
        )

    # Validate year is reasonable
    year = metadata.get("year")
    if not isinstance(year, int) or year < 1600 or year > 2100:
        raise ProvenanceValidationError(
            f"Invalid year: {year}. Must be integer between 1600 and 2100."
        )

    # Validate canonical_url is a valid URL
    canonical_url = metadata.get("canonical_url")
    if not canonical_url.startswith(("http://", "https://")):
        raise ProvenanceValidationError(
            f"Invalid canonical_url: {canonical_url}. Must be a valid HTTP(S) URL."
        )


def generate_citation_label(metadata: Dict) -> str:
    """
    Generate a human-readable citation label from metadata.

    Args:
        metadata: Document metadata with source_org, year, title/content_type

    Returns:
        Formatted citation label (e.g., "National Archives (1964) - Civil Rights Act")
    """
    source_org = metadata.get("source_org", "Unknown")
    year = metadata.get("year", "n.d.")
    title = metadata.get("title") or metadata.get("content_type", "Document")

    return f"{source_org} ({year}) - {title}"
```

**Acceptance Criteria**:
- [ ] Validates all 6 required provenance fields
- [ ] Raises exception with clear error message if invalid
- [ ] Used in ingestion pipeline before storing chunks
- [ ] 100% enforcement (no chunks without provenance)

---

## Phase 3: Persona Integration (Week 3)

#### Task 3.1: Load Persona Presets in Search API

**File**: `/Users/aideveloper/kwanzaa/backend/app/api/v1/endpoints/search.py`

**Action**: Modify search endpoint to use persona presets:

```python
from app.core.namespaces import get_namespaces_for_persona

@router.post("/semantic")
async def semantic_search(request: SearchRequest) -> SearchResponse:
    """
    Perform semantic search with provenance filters.

    If persona_key is provided, applies persona-specific defaults for
    namespaces and thresholds.
    """
    # Apply persona defaults if persona_key provided
    if request.persona_key:
        # Load persona preset from database
        persona = await get_persona_preset(request.persona_key)

        # Use persona's default namespaces if no namespace specified
        if not request.namespace:
            request.namespace = persona.default_namespaces[0]  # Use first

        # Apply persona's default threshold if not specified
        if request.threshold == 0.7:  # Default value
            request.threshold = persona.threshold_default

    # Existing search logic...
    query_embedding = await generate_embedding(request.query)

    # Search with namespace filter
    results = await search_vectors(
        query_embedding=query_embedding,
        namespace=request.namespace,
        filters=request.filters.to_metadata_filter() if request.filters else {},
        limit=request.limit,
        threshold=request.threshold
    )

    return format_search_response(results, request)
```

**Acceptance Criteria**:
- [ ] Persona presets loaded from database
- [ ] Default namespaces applied when persona_key provided
- [ ] Threshold adjusted based on persona
- [ ] Existing search logic still works without persona_key

---

#### Task 3.2: Create Persona Preset Management Endpoint

**File**: `/Users/aideveloper/kwanzaa/backend/app/api/v1/endpoints/personas.py` (new file)

**Action**:

```python
"""Persona preset management endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models.persona import PersonaPreset
from app.db.zerodb import get_persona_preset, list_persona_presets

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/", response_model=List[PersonaPreset])
async def list_personas():
    """List all available persona presets."""
    return await list_persona_presets()


@router.get("/{persona_key}", response_model=PersonaPreset)
async def get_persona(persona_key: str):
    """Get a specific persona preset by key."""
    persona = await get_persona_preset(persona_key)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona
```

**Acceptance Criteria**:
- [ ] GET `/api/v1/personas` returns all 4 presets
- [ ] GET `/api/v1/personas/educator` returns educator preset with namespaces
- [ ] Returns 404 for invalid persona keys

---

## Phase 4: Quality Assurance (Week 4)

#### Task 4.1: Create Namespace Evaluation Test Suite

**File**: `/Users/aideveloper/kwanzaa/backend/tests/test_namespaces.py` (new file)

**Action**:

```python
"""Test suite for namespace functionality."""

import pytest
from app.models.search import SearchRequest
from app.core.namespaces import (
    KwanzaaNamespace,
    get_namespaces_for_persona,
    validate_namespace
)


class TestNamespaceValidation:
    """Test namespace validation logic."""

    def test_valid_namespaces_accepted(self):
        """Test that all valid namespaces are accepted."""
        for ns in KwanzaaNamespace:
            request = SearchRequest(query="test", namespace=ns.value)
            assert request.namespace == ns.value

    def test_invalid_namespace_rejected(self):
        """Test that invalid namespaces raise ValueError."""
        with pytest.raises(ValueError):
            SearchRequest(query="test", namespace="invalid_namespace")

    def test_none_namespace_allowed(self):
        """Test that None namespace is allowed (uses persona default)."""
        request = SearchRequest(query="test", namespace=None)
        assert request.namespace is None


class TestPersonaNamespaceMappings:
    """Test persona-to-namespace mappings."""

    def test_educator_namespaces(self):
        """Educator should default to primary_sources, speeches_letters, teaching_kits."""
        namespaces = get_namespaces_for_persona("educator")
        assert KwanzaaNamespace.PRIMARY_SOURCES.value in namespaces
        assert KwanzaaNamespace.SPEECHES_LETTERS.value in namespaces
        assert KwanzaaNamespace.TEACHING_KITS.value in namespaces

    def test_researcher_all_namespaces(self):
        """Researcher should have access to all namespaces."""
        namespaces = get_namespaces_for_persona("researcher")
        assert len(namespaces) == 6  # All namespaces

    def test_creator_namespaces(self):
        """Creator should default to speeches_letters, teaching_kits, black_press."""
        namespaces = get_namespaces_for_persona("creator")
        assert KwanzaaNamespace.SPEECHES_LETTERS.value in namespaces
        assert KwanzaaNamespace.TEACHING_KITS.value in namespaces
        assert KwanzaaNamespace.BLACK_PRESS.value in namespaces

    def test_builder_namespaces(self):
        """Builder should default to dev_patterns, primary_sources."""
        namespaces = get_namespaces_for_persona("builder")
        assert KwanzaaNamespace.DEV_PATTERNS.value in namespaces
        assert KwanzaaNamespace.PRIMARY_SOURCES.value in namespaces


class TestProvenanceEnforcement:
    """Test provenance validation."""

    def test_complete_provenance_accepted(self):
        """Test that complete provenance passes validation."""
        from app.utils.provenance import validate_provenance

        valid_metadata = {
            "canonical_url": "https://example.com/doc",
            "source_org": "National Archives",
            "license": "Public Domain",
            "year": 1964,
            "content_type": "legal_document",
            "citation_label": "National Archives (1964) - Test",
        }

        # Should not raise
        validate_provenance(valid_metadata)

    def test_missing_provenance_rejected(self):
        """Test that missing provenance raises exception."""
        from app.utils.provenance import (
            validate_provenance,
            ProvenanceValidationError
        )

        incomplete_metadata = {
            "canonical_url": "https://example.com/doc",
            "source_org": "National Archives",
            # Missing: license, year, content_type, citation_label
        }

        with pytest.raises(ProvenanceValidationError):
            validate_provenance(incomplete_metadata)


@pytest.mark.asyncio
class TestNamespaceSearch:
    """Test namespace filtering in search API."""

    async def test_search_with_namespace_filter(self, client):
        """Test that namespace filter is applied in search."""
        response = await client.post("/api/v1/search/semantic", json={
            "query": "civil rights",
            "namespace": "kwanzaa_primary_sources",
            "limit": 5
        })

        assert response.status_code == 200
        data = response.json()

        # All results should be from specified namespace
        for result in data["results"]:
            assert result["namespace"] == "kwanzaa_primary_sources"

    async def test_persona_applies_namespace_defaults(self, client):
        """Test that persona_key applies default namespaces."""
        response = await client.post("/api/v1/search/semantic", json={
            "query": "voting rights",
            "persona_key": "educator",
            "limit": 5
        })

        assert response.status_code == 200
        data = response.json()

        # Results should be from educator's default namespaces
        educator_namespaces = [
            "kwanzaa_primary_sources",
            "kwanzaa_speeches_letters",
            "kwanzaa_teaching_kits"
        ]

        for result in data["results"]:
            assert result["namespace"] in educator_namespaces
```

**Acceptance Criteria**:
- [ ] All tests pass
- [ ] >80% code coverage for namespace-related code
- [ ] Tests included in CI/CD pipeline

---

#### Task 4.2: Create Namespace Evaluation Questions

**File**: `/Users/aideveloper/kwanzaa/data/eval/namespace_eval_questions.json`

**Action**: Create evaluation questions per namespace:

```json
{
  "version": "1.0",
  "created_at": "2026-01-16",
  "evaluation_sets": {
    "kwanzaa_primary_sources": [
      {
        "question": "What did the Civil Rights Act of 1964 prohibit?",
        "expected_behavior": "Should cite primary source from NARA or LOC",
        "require_citation": true,
        "min_score": 0.8
      },
      {
        "question": "When was the Emancipation Proclamation signed?",
        "expected_behavior": "Should cite government document",
        "require_citation": true,
        "min_score": 0.8
      }
    ],
    "kwanzaa_black_press": [
      {
        "question": "How did the Chicago Defender cover the Emmett Till murder?",
        "expected_behavior": "Should cite Chicago Defender articles",
        "require_citation": true,
        "min_score": 0.75
      }
    ],
    "kwanzaa_speeches_letters": [
      {
        "question": "What rhetorical devices did MLK use in I Have a Dream?",
        "expected_behavior": "Should cite speech text and analyze rhetoric",
        "require_citation": true,
        "min_score": 0.8
      }
    ],
    "kwanzaa_black_stem": [
      {
        "question": "Who was Katherine Johnson and what did she contribute to NASA?",
        "expected_behavior": "Should cite NASA biographical sources",
        "require_citation": true,
        "min_score": 0.75
      }
    ],
    "kwanzaa_teaching_kits": [
      {
        "question": "Show me a lesson plan about the Civil Rights Movement",
        "expected_behavior": "Should return lesson plan with grade level",
        "require_citation": true,
        "min_score": 0.7
      }
    ],
    "kwanzaa_dev_patterns": [
      {
        "question": "Show me the answer_json contract structure",
        "expected_behavior": "Should cite technical documentation",
        "require_citation": true,
        "min_score": 0.8
      }
    ]
  }
}
```

**Acceptance Criteria**:
- [ ] At least 5 questions per namespace
- [ ] Expected behavior documented
- [ ] Can be run programmatically
- [ ] Results tracked in kw_eval_results table

---

## Monitoring and Metrics

#### Task 5.1: Create Namespace Metrics Dashboard Query

**File**: `/Users/aideveloper/kwanzaa/backend/scripts/namespace_metrics.sql`

**Action**:

```sql
-- Namespace health metrics

-- Document/chunk counts per namespace
SELECT
    namespace,
    COUNT(DISTINCT doc_id) as document_count,
    COUNT(*) as chunk_count
FROM kw_retrieval_results
GROUP BY namespace
ORDER BY chunk_count DESC;

-- Query distribution by namespace (last 30 days)
SELECT
    namespace,
    COUNT(*) as query_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM kw_retrieval_runs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY namespace
ORDER BY query_count DESC;

-- Citation success rate by namespace
SELECT
    rr.namespace,
    COUNT(DISTINCT rr.retrieval_run_id) as total_retrievals,
    COUNT(DISTINCT cu.retrieval_run_id) as retrievals_with_citations,
    ROUND(
        COUNT(DISTINCT cu.retrieval_run_id) * 100.0 /
        NULLIF(COUNT(DISTINCT rr.retrieval_run_id), 0),
        2
    ) as citation_rate_pct
FROM kw_retrieval_results rr
LEFT JOIN kw_citations_used cu ON cu.retrieval_run_id = rr.retrieval_run_id
GROUP BY rr.namespace
ORDER BY citation_rate_pct DESC;

-- Ingestion success by namespace
SELECT
    namespace,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
    ROUND(
        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(COUNT(*), 0),
        2
    ) as success_rate_pct,
    SUM(docs_ingested) as total_docs_ingested,
    SUM(chunks_ingested) as total_chunks_ingested
FROM kw_ingestion_runs
WHERE namespace IS NOT NULL
GROUP BY namespace
ORDER BY total_chunks_ingested DESC;

-- Provenance completeness audit
-- (This would be a Python script that checks ZeroDB vectors)
```

**Acceptance Criteria**:
- [ ] Queries run successfully
- [ ] Metrics accessible to team
- [ ] Can be scheduled to run daily/weekly

---

## Documentation Updates

#### Task 6.1: Update API Documentation

**File**: `/Users/aideveloper/kwanzaa/docs/api/semantic-search-api.md`

**Action**: Add namespace examples and update schemas

**Changes Needed**:
1. Add namespace parameter documentation
2. Add namespace filter examples
3. Document persona-namespace behavior
4. Add `/namespaces` endpoint documentation

---

#### Task 6.2: Update README

**File**: `/Users/aideveloper/kwanzaa/README.md`

**Action**: Add namespace section:

```markdown
## Namespaces

Kwanzaa organizes its corpus into 6 namespaces aligned with user personas:

- **kwanzaa_primary_sources** - Government documents and official records
- **kwanzaa_black_press** - Historical Black newspapers
- **kwanzaa_speeches_letters** - Rhetorical documents
- **kwanzaa_black_stem** - STEM contributions and biographies
- **kwanzaa_teaching_kits** - Curriculum materials
- **kwanzaa_dev_patterns** - Technical documentation

Each namespace enforces complete provenance (canonical_url, license, year, etc.).

Learn more: [Namespace Strategy](docs/architecture/namespace-strategy.md)
```

---

## Final Checklist

### Backend
- [ ] Namespace validation added to SearchRequest
- [ ] Namespace constants module created
- [ ] /namespaces API endpoint implemented
- [ ] Persona presets table created and populated
- [ ] Database migrations applied
- [ ] Ingestion pipeline updated
- [ ] Provenance validation enforced
- [ ] All tests passing

### Database
- [ ] kw_source_manifest.default_namespace column added
- [ ] kw_ingestion_runs.namespace column added
- [ ] kw_persona_presets table created
- [ ] CHECK constraints enforced
- [ ] Indexes created

### Data
- [ ] P0 manifest entries created
- [ ] At least 3 sources per namespace
- [ ] All sources have default_namespace
- [ ] Provenance complete for all sources

### Testing
- [ ] Unit tests for namespace validation
- [ ] Integration tests for search with namespaces
- [ ] Provenance validation tests
- [ ] Evaluation questions created per namespace

### Documentation
- [ ] Namespace strategy published
- [ ] API docs updated
- [ ] README updated
- [ ] Contributor guide references namespaces

### Monitoring
- [ ] Namespace metrics queries created
- [ ] Can track ingestion success per namespace
- [ ] Can track query distribution
- [ ] Can track citation rates per namespace

---

## Success Criteria

At the end of implementation:

1. All 6 namespaces are queryable via API
2. Search filters correctly by namespace
3. Persona presets apply correct default namespaces
4. 100% provenance completeness enforced
5. At least 2,000 documents ingested across namespaces
6. Citation coverage >90% for educator/researcher personas
7. All tests passing
8. Documentation complete and accessible

---

## Timeline

- **Week 1**: Tasks 1.1-1.7 (Backend foundation)
- **Week 2**: Tasks 2.1-2.3 (Ingestion and corpus)
- **Week 3**: Tasks 3.1-3.2 (Persona integration)
- **Week 4**: Tasks 4.1-4.2, 5.1, 6.1-6.2 (QA and docs)

---

## Support

Questions or blockers? File issues at:
https://github.com/AINative-Studio/kwanzaa/issues

Label: `namespace:implementation`

**Document Owner**: Architecture Team
**Last Updated**: 2026-01-16
