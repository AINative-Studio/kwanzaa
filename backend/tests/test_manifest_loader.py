"""Tests for manifest loader.

This module tests the manifest loading and filtering functionality.
"""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.services.manifest_loader import (
    AccessMethod,
    ManifestLoader,
    SourceManifest,
    SourceType,
)


class TestSourceManifest:
    """Test suite for SourceManifest dataclass."""

    def test_source_manifest_creation(self):
        """Test creating source manifest with required fields."""
        manifest = SourceManifest(
            source_name="Test Source",
            source_id="test_source_001",
            source_type=SourceType.PRIMARY_SOURCE,
            access_method=AccessMethod.LOCAL_FILE,
            canonical_url="https://example.com",
            license_info="Public Domain",
            priority=0,
        )

        assert manifest.source_name == "Test Source"
        assert manifest.source_id == "test_source_001"
        assert manifest.source_type == SourceType.PRIMARY_SOURCE
        assert manifest.priority == 0

    def test_source_manifest_with_optional_fields(self):
        """Test creating source manifest with all fields."""
        manifest = SourceManifest(
            source_name="Test Source",
            source_id="test_source_001",
            source_type=SourceType.PRIMARY_SOURCE,
            access_method=AccessMethod.LOCAL_FILE,
            canonical_url="https://example.com",
            license_info="Public Domain",
            priority=0,
            source_org="Test Org",
            year=1903,
            content_type="essay",
            tags=["test", "primary_source"],
            location="/data/test.txt",
            metadata={"key": "value"},
        )

        assert manifest.source_org == "Test Org"
        assert manifest.year == 1903
        assert manifest.content_type == "essay"
        assert "test" in manifest.tags
        assert manifest.location == "/data/test.txt"
        assert manifest.metadata["key"] == "value"

    def test_source_manifest_from_dict(self):
        """Test creating manifest from dictionary."""
        data = {
            "source_name": "Test Source",
            "source_id": "test_001",
            "source_type": "primary_source",
            "access_method": "local_file",
            "canonical_url": "https://example.com",
            "license_info": "Public Domain",
            "priority": 0,
            "tags": ["test"],
        }

        manifest = SourceManifest.from_dict(data)

        assert manifest.source_name == "Test Source"
        assert manifest.source_id == "test_001"
        assert manifest.source_type == SourceType.PRIMARY_SOURCE
        assert manifest.access_method == AccessMethod.LOCAL_FILE

    def test_source_manifest_from_dict_missing_field(self):
        """Test error handling for missing required field."""
        data = {
            "source_name": "Test Source",
            # Missing source_id
            "source_type": "primary_source",
            "access_method": "local_file",
            "license_info": "Public Domain",
            "priority": 0,
        }

        with pytest.raises(ValueError, match="Missing required field"):
            SourceManifest.from_dict(data)

    def test_source_manifest_from_dict_invalid_enum(self):
        """Test error handling for invalid enum value."""
        data = {
            "source_name": "Test Source",
            "source_id": "test_001",
            "source_type": "invalid_type",
            "access_method": "local_file",
            "canonical_url": "https://example.com",
            "license_info": "Public Domain",
            "priority": 0,
        }

        with pytest.raises(ValueError, match="Invalid manifest data"):
            SourceManifest.from_dict(data)

    def test_source_manifest_to_dict(self):
        """Test converting manifest to dictionary."""
        manifest = SourceManifest(
            source_name="Test Source",
            source_id="test_001",
            source_type=SourceType.PRIMARY_SOURCE,
            access_method=AccessMethod.LOCAL_FILE,
            canonical_url="https://example.com",
            license_info="Public Domain",
            priority=0,
            tags=["test"],
        )

        result = manifest.to_dict()

        assert isinstance(result, dict)
        assert result["source_name"] == "Test Source"
        assert result["source_type"] == "primary_source"
        assert result["access_method"] == "local_file"
        assert result["priority"] == 0

    def test_is_p0(self):
        """Test P0 source identification."""
        p0_manifest = SourceManifest(
            source_name="P0 Source",
            source_id="p0_001",
            source_type=SourceType.PRIMARY_SOURCE,
            access_method=AccessMethod.LOCAL_FILE,
            canonical_url="https://example.com",
            license_info="Public Domain",
            priority=0,
        )

        p1_manifest = SourceManifest(
            source_name="P1 Source",
            source_id="p1_001",
            source_type=SourceType.PRIMARY_SOURCE,
            access_method=AccessMethod.LOCAL_FILE,
            canonical_url="https://example.com",
            license_info="Public Domain",
            priority=1,
        )

        assert p0_manifest.is_p0() is True
        assert p1_manifest.is_p0() is False


class TestManifestLoader:
    """Test suite for ManifestLoader."""

    @pytest.fixture
    def sample_manifest_data(self):
        """Create sample manifest data."""
        return {
            "manifest_version": "1.0",
            "sources": [
                {
                    "source_name": "P0 Source 1",
                    "source_id": "p0_001",
                    "source_type": "primary_source",
                    "access_method": "local_file",
                    "canonical_url": "https://example.com/1",
                    "license_info": "Public Domain",
                    "priority": 0,
                    "tags": ["test", "p0"],
                },
                {
                    "source_name": "P0 Source 2",
                    "source_id": "p0_002",
                    "source_type": "book",
                    "access_method": "local_file",
                    "canonical_url": "https://example.com/2",
                    "license_info": "Public Domain",
                    "priority": 0,
                    "tags": ["test", "p0"],
                },
                {
                    "source_name": "P1 Source",
                    "source_id": "p1_001",
                    "source_type": "black_press",
                    "access_method": "api",
                    "canonical_url": "https://example.com/3",
                    "license_info": "Subscription Required",
                    "priority": 1,
                    "tags": ["test", "p1"],
                },
            ],
        }

    @pytest.fixture
    def manifest_file(self, sample_manifest_data, tmp_path):
        """Create temporary manifest file."""
        manifest_path = tmp_path / "test_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(sample_manifest_data, f)
        return manifest_path

    def test_loader_initialization(self):
        """Test loader initialization."""
        loader = ManifestLoader()
        assert loader._loaded is False

    def test_load_manifest_from_file(self, manifest_file):
        """Test loading manifest from file."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        assert loader._loaded is True
        sources = loader.get_all_sources()
        assert len(sources) == 3

    def test_load_manifest_file_not_found(self):
        """Test error handling for missing file."""
        loader = ManifestLoader(manifest_path=Path("/nonexistent/manifest.json"))

        with pytest.raises(FileNotFoundError):
            loader.load_manifest()

    def test_load_manifest_no_path(self):
        """Test error handling when no path provided."""
        loader = ManifestLoader()

        with pytest.raises(ValueError, match="Manifest path not provided"):
            loader.load_manifest()

    def test_load_manifest_invalid_json(self, tmp_path):
        """Test error handling for invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{invalid json")

        loader = ManifestLoader(manifest_path=invalid_file)

        with pytest.raises(ValueError, match="Invalid JSON"):
            loader.load_manifest()

    def test_load_from_dict(self, sample_manifest_data):
        """Test loading manifest from dictionary."""
        loader = ManifestLoader()
        loader.load_from_dict(sample_manifest_data)

        assert loader._loaded is True
        sources = loader.get_all_sources()
        assert len(sources) == 3

    def test_load_from_dict_list_format(self):
        """Test loading manifest from list format."""
        manifest_list = [
            {
                "source_name": "Test Source",
                "source_id": "test_001",
                "source_type": "primary_source",
                "access_method": "local_file",
                "canonical_url": "https://example.com",
                "license_info": "Public Domain",
                "priority": 0,
            }
        ]

        loader = ManifestLoader()
        loader.load_from_dict(manifest_list)

        assert loader._loaded is True
        sources = loader.get_all_sources()
        assert len(sources) == 1

    def test_get_all_sources(self, manifest_file):
        """Test getting all sources."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        sources = loader.get_all_sources()

        assert len(sources) == 3
        assert all(isinstance(s, SourceManifest) for s in sources)

    def test_get_all_sources_not_loaded(self):
        """Test error when getting sources before loading."""
        loader = ManifestLoader()

        with pytest.raises(RuntimeError, match="Manifest not loaded"):
            loader.get_all_sources()

    def test_get_p0_sources(self, manifest_file):
        """Test filtering P0 sources."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        p0_sources = loader.get_p0_sources()

        assert len(p0_sources) == 2
        assert all(s.priority == 0 for s in p0_sources)
        assert all(s.is_p0() for s in p0_sources)

    def test_get_sources_by_priority(self, manifest_file):
        """Test filtering sources by priority."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        p0_sources = loader.get_sources_by_priority(0)
        p1_sources = loader.get_sources_by_priority(1)

        assert len(p0_sources) == 2
        assert len(p1_sources) == 1
        assert all(s.priority == 0 for s in p0_sources)
        assert all(s.priority == 1 for s in p1_sources)

    def test_get_sources_by_type(self, manifest_file):
        """Test filtering sources by type."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        primary_sources = loader.get_sources_by_type(SourceType.PRIMARY_SOURCE)
        book_sources = loader.get_sources_by_type(SourceType.BOOK)
        press_sources = loader.get_sources_by_type(SourceType.BLACK_PRESS)

        assert len(primary_sources) == 1
        assert len(book_sources) == 1
        assert len(press_sources) == 1

    def test_get_sources_by_tags_any(self, manifest_file):
        """Test filtering sources by tags (any match)."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        sources = loader.get_sources_by_tags(["p0"], match_all=False)

        assert len(sources) == 2

    def test_get_sources_by_tags_all(self, manifest_file):
        """Test filtering sources by tags (all match)."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        sources = loader.get_sources_by_tags(["test", "p0"], match_all=True)

        assert len(sources) == 2
        assert all("test" in s.tags and "p0" in s.tags for s in sources)

    def test_get_source_by_id(self, manifest_file):
        """Test getting source by ID."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        source = loader.get_source_by_id("p0_001")

        assert source is not None
        assert source.source_id == "p0_001"
        assert source.source_name == "P0 Source 1"

    def test_get_source_by_id_not_found(self, manifest_file):
        """Test getting non-existent source by ID."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        source = loader.get_source_by_id("nonexistent")

        assert source is None

    def test_get_statistics(self, manifest_file):
        """Test getting manifest statistics."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        stats = loader.get_statistics()

        assert stats["total_sources"] == 3
        assert stats["p0_sources"] == 2
        assert stats["priority_distribution"][0] == 2
        assert stats["priority_distribution"][1] == 1
        assert "type_distribution" in stats
        assert "access_method_distribution" in stats

    def test_validate_manifest_valid(self, manifest_file):
        """Test validating valid manifest."""
        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        issues = loader.validate_manifest()

        assert len(issues) == 0

    def test_validate_manifest_duplicate_ids(self, tmp_path):
        """Test validation catches duplicate IDs."""
        manifest_data = {
            "sources": [
                {
                    "source_name": "Source 1",
                    "source_id": "duplicate_id",
                    "source_type": "primary_source",
                    "access_method": "local_file",
                    "canonical_url": "https://example.com",
                    "license_info": "Public Domain",
                    "priority": 0,
                },
                {
                    "source_name": "Source 2",
                    "source_id": "duplicate_id",  # Duplicate
                    "source_type": "primary_source",
                    "access_method": "local_file",
                    "canonical_url": "https://example.com",
                    "license_info": "Public Domain",
                    "priority": 0,
                },
            ]
        }

        manifest_file = tmp_path / "duplicate.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        issues = loader.validate_manifest()

        assert len(issues) > 0
        assert any("Duplicate source IDs" in issue for issue in issues)

    def test_validate_manifest_negative_priority(self, tmp_path):
        """Test validation catches negative priorities."""
        manifest_data = {
            "sources": [
                {
                    "source_name": "Test Source",
                    "source_id": "test_001",
                    "source_type": "primary_source",
                    "access_method": "local_file",
                    "canonical_url": "https://example.com",
                    "license_info": "Public Domain",
                    "priority": -1,  # Invalid
                }
            ]
        }

        manifest_file = tmp_path / "invalid_priority.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        loader = ManifestLoader(manifest_path=manifest_file)
        loader.load_manifest()

        issues = loader.validate_manifest()

        assert len(issues) > 0
        assert any("negative priority" in issue for issue in issues)
