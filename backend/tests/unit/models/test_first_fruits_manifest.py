"""
Unit tests for First Fruits Manifest models.

Tests the Pydantic models and JSON schema validation for manifest files.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.manifest import (
    AccessMethod,
    AccessMethodType,
    AuthenticationMethod,
    ChunkingMethod,
    ContentMetadata,
    ContentType,
    DataQuality,
    FirstFruitsManifest,
    IngestionConfig,
    IngestionFrequency,
    IngestionStatus,
    IngestionStatusType,
    LicenseInfo,
    NguzoSabaAlignment,
    PipelineType,
    PriorityLevel,
    SourceType,
)


class TestPriorityLevel:
    """Test PriorityLevel enum."""

    def test_all_priority_levels(self):
        """Test all priority level values."""
        assert PriorityLevel.P0 == "P0"
        assert PriorityLevel.P1 == "P1"
        assert PriorityLevel.P2 == "P2"
        assert PriorityLevel.P3 == "P3"
        assert PriorityLevel.P4 == "P4"


class TestSourceType:
    """Test SourceType enum."""

    def test_source_types(self):
        """Test source type values."""
        assert SourceType.ARCHIVE == "archive"
        assert SourceType.API == "api"
        assert SourceType.ORAL_HISTORY == "oral_history"


class TestAccessMethod:
    """Test AccessMethod model."""

    def test_minimal_access_method(self):
        """Test creating minimal access method."""
        access = AccessMethod(type=AccessMethodType.DIRECT_DOWNLOAD)
        assert access.type == AccessMethodType.DIRECT_DOWNLOAD
        assert access.endpoint is None
        assert access.authentication is None

    def test_full_access_method(self):
        """Test creating full access method with all fields."""
        access = AccessMethod(
            type=AccessMethodType.API_KEY_REQUIRED,
            endpoint="https://api.example.com",
            authentication={
                "required": True,
                "method": AuthenticationMethod.API_KEY,
                "env_var": "API_KEY",
            },
            rate_limits={
                "requests_per_second": 2.0,
                "requests_per_day": 1000,
                "concurrent_connections": 3,
            },
            protocol_details={"version": "v1"},
        )
        assert access.type == AccessMethodType.API_KEY_REQUIRED
        assert str(access.endpoint) == "https://api.example.com/"
        assert access.authentication.required is True
        assert access.rate_limits.requests_per_second == 2.0


class TestLicenseInfo:
    """Test LicenseInfo model."""

    def test_minimal_license(self):
        """Test creating minimal license info."""
        license_info = LicenseInfo(
            type="Public Domain",
            commercial_use_allowed=True,
            attribution_required=False,
        )
        assert license_info.type == "Public Domain"
        assert license_info.commercial_use_allowed is True

    def test_full_license(self):
        """Test creating full license info."""
        license_info = LicenseInfo(
            type="CC BY 4.0",
            url="https://creativecommons.org/licenses/by/4.0/",
            commercial_use_allowed=True,
            attribution_required=True,
            share_alike_required=False,
            restrictions=["Must attribute"],
            notes="Standard CC BY license",
        )
        assert license_info.type == "CC BY 4.0"
        assert license_info.attribution_required is True
        assert len(license_info.restrictions) == 1


class TestContentMetadata:
    """Test ContentMetadata model."""

    def test_with_time_period(self):
        """Test content metadata with time period."""
        metadata = ContentMetadata(
            content_types=[ContentType.TEXT, ContentType.SPEECH],
            time_period={"start_year": 1960, "end_year": 1970},
            languages=["en"],
        )
        assert ContentType.TEXT in metadata.content_types
        assert metadata.time_period.start_year == 1960

    def test_invalid_time_period(self):
        """Test that invalid time period raises error."""
        with pytest.raises(ValidationError) as exc_info:
            ContentMetadata(
                time_period={"start_year": 1970, "end_year": 1960}
            )
        assert "start_year must be less than or equal to end_year" in str(exc_info.value)

    def test_language_code_validation(self):
        """Test language code validation."""
        # Valid codes
        metadata = ContentMetadata(languages=["en", "es", "fr-CA"])
        assert "en" in metadata.languages

        # Invalid code
        with pytest.raises(ValidationError) as exc_info:
            ContentMetadata(languages=["english"])
        assert "Invalid language code" in str(exc_info.value)


class TestIngestionConfig:
    """Test IngestionConfig model."""

    def test_batch_pipeline(self):
        """Test batch pipeline configuration."""
        config = IngestionConfig(
            pipeline_type=PipelineType.BATCH,
            schedule={
                "frequency": IngestionFrequency.DAILY,
                "cron_expression": "0 2 * * *",
            },
            chunk_strategy={
                "method": ChunkingMethod.SEMANTIC,
                "chunk_size": 1000,
                "overlap": 200,
            },
            embedding_model="text-embedding-3-small",
            target_namespace="kwanzaa_primary_sources",
        )
        assert config.pipeline_type == PipelineType.BATCH
        assert config.schedule.frequency == IngestionFrequency.DAILY
        assert config.chunk_strategy.chunk_size == 1000


class TestDataQuality:
    """Test DataQuality model."""

    def test_quality_scores(self):
        """Test quality score validation."""
        quality = DataQuality(
            completeness_score=0.95,
            accuracy_score=0.98,
            last_verified=datetime.now(timezone.utc),
            known_issues=["Some OCR errors"],
        )
        assert quality.completeness_score == 0.95
        assert len(quality.known_issues) == 1

    def test_invalid_score(self):
        """Test that invalid scores raise errors."""
        with pytest.raises(ValidationError):
            DataQuality(completeness_score=1.5)  # > 1.0


class TestNguzoSabaAlignment:
    """Test NguzoSabaAlignment model."""

    def test_all_principles(self):
        """Test all seven principles."""
        alignment = NguzoSabaAlignment(
            umoja=True,
            kujichagulia=True,
            ujima=True,
            ujamaa=True,
            nia=True,
            kuumba=True,
            imani=True,
        )
        assert alignment.umoja is True
        assert alignment.imani is True


class TestIngestionStatus:
    """Test IngestionStatus model."""

    def test_not_started_status(self):
        """Test not started status."""
        status = IngestionStatus(
            status=IngestionStatusType.NOT_STARTED,
            documents_ingested=0,
            vectors_created=0,
        )
        assert status.status == IngestionStatusType.NOT_STARTED
        assert status.documents_ingested == 0

    def test_completed_status(self):
        """Test completed status with data."""
        status = IngestionStatus(
            status=IngestionStatusType.COMPLETED,
            last_ingestion_date=datetime.now(timezone.utc),
            documents_ingested=1000,
            vectors_created=5000,
        )
        assert status.status == IngestionStatusType.COMPLETED
        assert status.documents_ingested == 1000


class TestFirstFruitsManifest:
    """Test FirstFruitsManifest model."""

    def test_minimal_manifest(self):
        """Test creating minimal valid manifest."""
        now = datetime.now(timezone.utc)
        manifest = FirstFruitsManifest(
            manifest_version="1.0.0",
            source_id="test_source",
            source_name="Test Source",
            source_type=SourceType.ARCHIVE,
            access_method=AccessMethod(type=AccessMethodType.DIRECT_DOWNLOAD),
            license=LicenseInfo(
                type="Public Domain",
                commercial_use_allowed=True,
                attribution_required=False,
            ),
            canonical_url="https://example.com",
            priority=PriorityLevel.P2,
            tags=["test", "example"],
            created_at=now,
            updated_at=now,
        )
        assert manifest.source_id == "test_source"
        assert manifest.priority == PriorityLevel.P2
        assert len(manifest.tags) == 2

    def test_invalid_source_id(self):
        """Test that invalid source_id raises error."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            FirstFruitsManifest(
                manifest_version="1.0.0",
                source_id="Invalid Source!",  # Has space and special char
                source_name="Test Source",
                source_type=SourceType.ARCHIVE,
                access_method=AccessMethod(type=AccessMethodType.DIRECT_DOWNLOAD),
                license=LicenseInfo(
                    type="Public Domain",
                    commercial_use_allowed=True,
                    attribution_required=False,
                ),
                canonical_url="https://example.com",
                priority=PriorityLevel.P2,
                tags=["test"],
                created_at=now,
                updated_at=now,
            )
        assert "source_id" in str(exc_info.value)

    def test_invalid_tag_format(self):
        """Test that invalid tags raise errors."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            FirstFruitsManifest(
                manifest_version="1.0.0",
                source_id="test_source",
                source_name="Test Source",
                source_type=SourceType.ARCHIVE,
                access_method=AccessMethod(type=AccessMethodType.DIRECT_DOWNLOAD),
                license=LicenseInfo(
                    type="Public Domain",
                    commercial_use_allowed=True,
                    attribution_required=False,
                ),
                canonical_url="https://example.com",
                priority=PriorityLevel.P2,
                tags=["Valid Tag"],  # Has uppercase and space
                created_at=now,
                updated_at=now,
            )
        assert "Invalid tag" in str(exc_info.value)

    def test_updated_before_created_validation(self):
        """Test that updated_at must be >= created_at."""
        created = datetime(2026, 1, 16, 12, 0, 0, tzinfo=timezone.utc)
        updated = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)  # Before created

        with pytest.raises(ValidationError) as exc_info:
            FirstFruitsManifest(
                manifest_version="1.0.0",
                source_id="test_source",
                source_name="Test Source",
                source_type=SourceType.ARCHIVE,
                access_method=AccessMethod(type=AccessMethodType.DIRECT_DOWNLOAD),
                license=LicenseInfo(
                    type="Public Domain",
                    commercial_use_allowed=True,
                    attribution_required=False,
                ),
                canonical_url="https://example.com",
                priority=PriorityLevel.P2,
                tags=["test"],
                created_at=created,
                updated_at=updated,
            )
        assert "updated_at must be greater than or equal to created_at" in str(
            exc_info.value
        )


class TestExampleManifests:
    """Test example manifest files."""

    @pytest.fixture
    def examples_dir(self):
        """Get examples directory path."""
        return Path(__file__).parent.parent.parent.parent.parent / "data" / "manifests" / "examples"

    def test_nara_civil_rights_example(self, examples_dir):
        """Test NARA civil rights example manifest."""
        manifest_path = examples_dir / "nara_civil_rights.json"
        if not manifest_path.exists():
            pytest.skip(f"Example manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = json.load(f)

        manifest = FirstFruitsManifest(**data)
        assert manifest.source_id == "nara_civil_rights"
        assert manifest.priority == PriorityLevel.P0
        assert manifest.source_type == SourceType.ARCHIVE
        assert "civil-rights" in manifest.tags

    def test_loc_oral_histories_example(self, examples_dir):
        """Test LOC oral histories example manifest."""
        manifest_path = examples_dir / "loc_oral_histories.json"
        if not manifest_path.exists():
            pytest.skip(f"Example manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = json.load(f)

        manifest = FirstFruitsManifest(**data)
        assert manifest.source_id == "loc_oral_histories"
        assert manifest.priority == PriorityLevel.P1
        assert manifest.source_type == SourceType.ORAL_HISTORY
        assert "oral-history" in manifest.tags

    def test_schomburg_digital_example(self, examples_dir):
        """Test Schomburg digital collections example manifest."""
        manifest_path = examples_dir / "schomburg_digital_collections.json"
        if not manifest_path.exists():
            pytest.skip(f"Example manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = json.load(f)

        manifest = FirstFruitsManifest(**data)
        assert manifest.source_id == "schomburg_digital"
        assert manifest.priority == PriorityLevel.P1
        assert manifest.source_type == SourceType.LIBRARY_CATALOG
        assert "harlem-renaissance" in manifest.tags


class TestJSONSchemaValidation:
    """Test JSON Schema validation."""

    @pytest.fixture
    def schema_path(self):
        """Get schema file path."""
        return Path(__file__).parent.parent.parent.parent.parent / "data" / "schemas" / "first_fruits_manifest.schema.json"

    @pytest.fixture
    def json_schema(self, schema_path):
        """Load JSON schema."""
        if not schema_path.exists():
            pytest.skip(f"Schema not found: {schema_path}")

        with open(schema_path) as f:
            return json.load(f)

    def test_schema_has_required_fields(self, json_schema):
        """Test that schema defines required fields."""
        assert "$schema" in json_schema
        assert "title" in json_schema
        assert "version" in json_schema
        assert "required" in json_schema

        required_fields = json_schema["required"]
        assert "manifest_version" in required_fields
        assert "source_id" in required_fields
        assert "source_name" in required_fields
        assert "source_type" in required_fields
        assert "priority" in required_fields

    def test_schema_has_definitions(self, json_schema):
        """Test that schema has type definitions."""
        assert "definitions" in json_schema
        definitions = json_schema["definitions"]
        assert "priority_level" in definitions
        assert "source_type" in definitions
        assert "access_method" in definitions
        assert "license_info" in definitions


class TestManifestSerialization:
    """Test manifest serialization and deserialization."""

    def test_roundtrip_serialization(self):
        """Test that manifest can be serialized and deserialized."""
        now = datetime.now(timezone.utc)
        original = FirstFruitsManifest(
            manifest_version="1.0.0",
            source_id="test_source",
            source_name="Test Source",
            source_type=SourceType.ARCHIVE,
            description="A test source for validation",
            access_method=AccessMethod(
                type=AccessMethodType.API_KEY_REQUIRED,
                endpoint="https://api.example.com",
            ),
            license=LicenseInfo(
                type="CC BY 4.0",
                commercial_use_allowed=True,
                attribution_required=True,
            ),
            canonical_url="https://example.com",
            priority=PriorityLevel.P1,
            tags=["test", "example"],
            created_at=now,
            updated_at=now,
        )

        # Serialize to JSON
        json_str = original.model_dump_json()
        data = json.loads(json_str)

        # Deserialize back
        restored = FirstFruitsManifest(**data)

        assert restored.source_id == original.source_id
        assert restored.priority == original.priority
        assert restored.tags == original.tags
