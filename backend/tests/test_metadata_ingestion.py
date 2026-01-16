"""Tests for metadata ingestion pipeline.

Following TDD best practices with BDD-style tests.
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.metadata_ingestion import (
    AccessMethod,
    ContentType,
    IngestionError,
    IngestionStats,
    MetadataIngestionPipeline,
    MetadataValidator,
    Priority,
    ProvenanceMetadata,
    SourceType,
    ValidationError,
)


class TestMetadataValidator:
    """Test suite for metadata validation."""

    def test_validate_document_metadata_success(self):
        """Given valid document metadata, validation should pass."""
        # Arrange
        valid_doc = {
            "doc_id": "test_001",
            "title": "Test Document",
            "source_org": "Test Org",
            "collection": "Test Collection",
            "canonical_url": "https://example.com/test_001",
            "license": "Public Domain",
            "content_type": ContentType.DEV_DOC.value,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "access_method": AccessMethod.API.value,
            "priority": Priority.P0.value,
            "year": 2020,
        }

        # Act & Assert
        MetadataValidator.validate_document_metadata(valid_doc)  # Should not raise

    def test_validate_document_metadata_missing_required_field(self):
        """Given document missing required fields, validation should fail."""
        # Arrange
        invalid_doc = {
            "doc_id": "test_001",
            # Missing title
            "source_org": "Test Org",
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Missing required fields"):
            MetadataValidator.validate_document_metadata(invalid_doc)

    def test_validate_document_metadata_empty_title(self):
        """Given document with empty title, validation should fail."""
        # Arrange
        invalid_doc = {
            "doc_id": "test_001",
            "title": "   ",  # Empty/whitespace title
            "source_org": "Test Org",
            "collection": "Test Collection",
            "canonical_url": "https://example.com/test_001",
            "license": "Public Domain",
            "content_type": ContentType.DEV_DOC.value,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "access_method": AccessMethod.API.value,
            "priority": Priority.P0.value,
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            MetadataValidator.validate_document_metadata(invalid_doc)

    def test_validate_document_metadata_invalid_url(self):
        """Given document with invalid URL, validation should fail."""
        # Arrange
        invalid_doc = {
            "doc_id": "test_001",
            "title": "Test Document",
            "source_org": "Test Org",
            "collection": "Test Collection",
            "canonical_url": "not-a-url",  # Invalid URL
            "license": "Public Domain",
            "content_type": ContentType.DEV_DOC.value,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "access_method": AccessMethod.API.value,
            "priority": Priority.P0.value,
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid canonical_url"):
            MetadataValidator.validate_document_metadata(invalid_doc)

    def test_validate_document_metadata_invalid_content_type(self):
        """Given document with invalid content_type, validation should fail."""
        # Arrange
        invalid_doc = {
            "doc_id": "test_001",
            "title": "Test Document",
            "source_org": "Test Org",
            "collection": "Test Collection",
            "canonical_url": "https://example.com/test_001",
            "license": "Public Domain",
            "content_type": "invalid_type",  # Invalid content type
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "access_method": AccessMethod.API.value,
            "priority": Priority.P0.value,
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid content_type"):
            MetadataValidator.validate_document_metadata(invalid_doc)

    def test_validate_document_metadata_invalid_year(self):
        """Given document with invalid year, validation should fail."""
        # Arrange
        invalid_doc = {
            "doc_id": "test_001",
            "title": "Test Document",
            "source_org": "Test Org",
            "collection": "Test Collection",
            "canonical_url": "https://example.com/test_001",
            "license": "Public Domain",
            "content_type": ContentType.DEV_DOC.value,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "access_method": AccessMethod.API.value,
            "priority": Priority.P0.value,
            "year": 3000,  # Future year
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Year .* is out of valid range"):
            MetadataValidator.validate_document_metadata(invalid_doc)

    def test_validate_provenance_success(self):
        """Given valid provenance metadata, validation should pass."""
        # Arrange
        valid_provenance = {
            "source_type": SourceType.ARCHIVE.value,
            "access_method": AccessMethod.API.value,
            "source_id": "test_source_001",
            "source_url": "https://example.com",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "license": "Public Domain",
            "hash": "abc123",
        }

        # Act & Assert
        MetadataValidator.validate_provenance(valid_provenance)  # Should not raise

    def test_validate_provenance_missing_required_field(self):
        """Given provenance missing required fields, validation should fail."""
        # Arrange
        invalid_provenance = {
            "source_type": SourceType.ARCHIVE.value,
            # Missing other required fields
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Missing required provenance fields"):
            MetadataValidator.validate_provenance(invalid_provenance)

    def test_validate_provenance_invalid_source_type(self):
        """Given provenance with invalid source_type, validation should fail."""
        # Arrange
        invalid_provenance = {
            "source_type": "invalid_type",
            "access_method": AccessMethod.API.value,
            "source_id": "test_source_001",
            "source_url": "https://example.com",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "license": "Public Domain",
            "hash": "abc123",
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid source_type"):
            MetadataValidator.validate_provenance(invalid_provenance)


class TestMetadataIngestionPipeline:
    """Test suite for metadata ingestion pipeline."""

    @pytest.fixture
    def mock_zerodb_client(self):
        """Create mock ZeroDB client."""
        client = AsyncMock()
        client.insert_rows = AsyncMock(return_value={"inserted_ids": ["id1", "id2"]})
        client.get_table = AsyncMock(return_value={"table_name": "test_table"})
        client.create_table = AsyncMock()
        return client

    @pytest.fixture
    def sample_manifest(self, tmp_path):
        """Create sample manifest file."""
        manifest_data = {
            "manifest_version": "1.0.0",
            "manifest_id": "test_manifest",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "Test manifest",
            "sources": [
                {
                    "source_id": "test_source_001",
                    "source_name": "Test Source",
                    "source_type": SourceType.ARCHIVE.value,
                    "source_org": "Test Organization",
                    "base_url": "https://example.com",
                    "access_method": AccessMethod.API.value,
                    "license": "Public Domain",
                    "priority": Priority.P0.value,
                    "default_namespace": "test_namespace",
                    "tags": ["test", "example"],
                    "job_id": "test_job",
                    "schedule": "daily",
                }
            ],
        }

        manifest_path = tmp_path / "test_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)

        return manifest_path

    @pytest.mark.asyncio
    async def test_pipeline_initialization(self, sample_manifest, mock_zerodb_client):
        """Given valid inputs, pipeline should initialize successfully."""
        # Act
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
            batch_size=50,
        )

        # Assert
        assert pipeline.manifest_path == sample_manifest
        assert pipeline.batch_size == 50
        assert pipeline.run_id.startswith("ingestion_run_")
        assert isinstance(pipeline.stats, IngestionStats)

    def test_load_manifest_success(self, sample_manifest, mock_zerodb_client):
        """Given valid manifest file, loading should succeed."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )

        # Act
        manifest = pipeline.load_manifest()

        # Assert
        assert "sources" in manifest
        assert len(manifest["sources"]) == 1
        assert manifest["sources"][0]["source_id"] == "test_source_001"

    def test_load_manifest_file_not_found(self, mock_zerodb_client):
        """Given non-existent manifest file, loading should fail."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=Path("/nonexistent/manifest.json"),
            zerodb_client=mock_zerodb_client,
        )

        # Act & Assert
        with pytest.raises(IngestionError, match="Manifest file not found"):
            pipeline.load_manifest()

    def test_load_manifest_invalid_json(self, tmp_path, mock_zerodb_client):
        """Given invalid JSON in manifest, loading should fail."""
        # Arrange
        invalid_manifest = tmp_path / "invalid.json"
        with open(invalid_manifest, "w") as f:
            f.write("{invalid json}")

        pipeline = MetadataIngestionPipeline(
            manifest_path=invalid_manifest,
            zerodb_client=mock_zerodb_client,
        )

        # Act & Assert
        with pytest.raises(IngestionError, match="Invalid JSON"):
            pipeline.load_manifest()

    def test_generate_doc_id(self, sample_manifest, mock_zerodb_client):
        """Given source and record IDs, doc_id should be stable."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )

        # Act
        doc_id_1 = pipeline._generate_doc_id("source_001", "record_123")
        doc_id_2 = pipeline._generate_doc_id("source_001", "record_123")

        # Assert
        assert doc_id_1 == doc_id_2
        assert doc_id_1 == "source_001::record_123"

    def test_generate_citation_label(self, sample_manifest, mock_zerodb_client):
        """Given document metadata, citation label should be formatted correctly."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )

        # Act
        citation = pipeline._generate_citation_label(
            source_org="Test Org",
            year=2020,
            title="Test Document Title",
        )

        # Assert
        assert "Test Org" in citation
        assert "2020" in citation
        assert "Test Document Title" in citation

    def test_generate_citation_label_no_year(self, sample_manifest, mock_zerodb_client):
        """Given document without year, citation should use 'n.d.'"""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )

        # Act
        citation = pipeline._generate_citation_label(
            source_org="Test Org",
            year=None,
            title="Test Document Title",
        )

        # Assert
        assert "n.d." in citation

    def test_generate_citation_label_long_title(self, sample_manifest, mock_zerodb_client):
        """Given long title, citation should truncate."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )
        long_title = "A" * 100

        # Act
        citation = pipeline._generate_citation_label(
            source_org="Test Org",
            year=2020,
            title=long_title,
        )

        # Assert
        assert len(citation) < len(long_title) + 20
        assert "..." in citation

    def test_compute_hash_deterministic(self, sample_manifest, mock_zerodb_client):
        """Given same content, hash should be deterministic."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )
        content = "test content"

        # Act
        hash1 = pipeline._compute_hash(content)
        hash2 = pipeline._compute_hash(content)

        # Assert
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters

    @pytest.mark.asyncio
    async def test_store_document_batch_success(self, sample_manifest, mock_zerodb_client):
        """Given valid documents, batch storage should succeed."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )
        documents = [
            {"doc_id": "doc1", "title": "Doc 1"},
            {"doc_id": "doc2", "title": "Doc 2"},
        ]

        # Act
        count = await pipeline._store_document_batch(documents)

        # Assert
        assert count == 2
        mock_zerodb_client.insert_rows.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_document_batch_retry_on_failure(
        self, sample_manifest, mock_zerodb_client
    ):
        """Given transient failure, storage should retry."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )
        documents = [{"doc_id": "doc1", "title": "Doc 1"}]

        # Simulate failure then success
        mock_zerodb_client.insert_rows.side_effect = [
            Exception("Transient error"),
            {"inserted_ids": ["id1"]},
        ]

        # Act
        count = await pipeline._store_document_batch(documents)

        # Assert
        assert count == 1
        assert mock_zerodb_client.insert_rows.call_count == 2

    @pytest.mark.asyncio
    async def test_process_source_generates_documents(
        self, sample_manifest, mock_zerodb_client
    ):
        """Given valid source, processing should generate documents."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )
        manifest = pipeline.load_manifest()
        source = manifest["sources"][0]

        # Act
        documents = await pipeline.process_source(source)

        # Assert
        assert len(documents) > 0
        assert all("doc_id" in doc for doc in documents)
        assert all("provenance" in doc for doc in documents)

    @pytest.mark.asyncio
    async def test_run_pipeline_end_to_end(self, sample_manifest, mock_zerodb_client):
        """Given valid manifest, pipeline should run end-to-end successfully."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
            batch_size=10,
        )

        # Act
        stats = await pipeline.run()

        # Assert
        assert stats.run_id == pipeline.run_id
        assert stats.completed_at is not None
        assert stats.sources_processed > 0
        assert stats.documents_inserted >= 0

    @pytest.mark.asyncio
    async def test_run_pipeline_idempotency(self, sample_manifest, mock_zerodb_client):
        """Given same documents, pipeline should not insert duplicates."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )

        # Process first time
        manifest = pipeline.load_manifest()
        source = manifest["sources"][0]
        docs1 = await pipeline.process_source(source)

        # Add to processed set
        for doc in docs1:
            pipeline.processed_doc_ids.add(doc["doc_id"])

        # Process again
        docs2 = await pipeline.process_source(source)

        # Act - filter out processed docs
        new_docs = [
            doc for doc in docs2
            if doc["doc_id"] not in pipeline.processed_doc_ids
        ]

        # Assert
        assert len(new_docs) == 0  # No new docs should be added

    def test_export_stats_creates_file(self, sample_manifest, mock_zerodb_client, tmp_path):
        """Given stats, export should create JSON file."""
        # Arrange
        pipeline = MetadataIngestionPipeline(
            manifest_path=sample_manifest,
            zerodb_client=mock_zerodb_client,
        )
        pipeline.stats.sources_processed = 1
        pipeline.stats.documents_inserted = 5
        pipeline.stats.completed_at = datetime.now(timezone.utc).isoformat()

        output_path = tmp_path / "stats" / "run_stats.json"

        # Act
        pipeline.export_stats(output_path)

        # Assert
        assert output_path.exists()
        with open(output_path, "r") as f:
            stats_data = json.load(f)
        assert stats_data["sources_processed"] == 1
        assert stats_data["documents_inserted"] == 5


class TestIngestionStats:
    """Test suite for ingestion statistics tracking."""

    def test_ingestion_stats_initialization(self):
        """Given run_id, stats should initialize with default values."""
        # Act
        stats = IngestionStats(
            run_id="test_run_123",
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        # Assert
        assert stats.run_id == "test_run_123"
        assert stats.total_sources == 0
        assert stats.sources_processed == 0
        assert len(stats.errors) == 0

    def test_add_error(self):
        """Given error details, stats should track error."""
        # Arrange
        stats = IngestionStats(
            run_id="test_run_123",
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        # Act
        stats.add_error(
            source_id="test_source",
            error_type="validation_error",
            error_message="Test error message",
        )

        # Assert
        assert len(stats.errors) == 1
        assert stats.errors[0]["source_id"] == "test_source"
        assert stats.errors[0]["error_type"] == "validation_error"
        assert stats.errors[0]["error_message"] == "Test error message"
        assert "timestamp" in stats.errors[0]


class TestEnums:
    """Test suite for enum definitions."""

    def test_priority_enum_values(self):
        """Priority enum should have correct values."""
        assert Priority.P0.value == "P0"
        assert Priority.P1.value == "P1"
        assert Priority.P2.value == "P2"

    def test_access_method_enum_values(self):
        """AccessMethod enum should have correct values."""
        assert AccessMethod.API.value == "api"
        assert AccessMethod.BULK.value == "bulk"
        assert AccessMethod.ALLOWED_SCRAPE.value == "allowed_scrape"

    def test_content_type_enum_comprehensive(self):
        """ContentType enum should cover all required types."""
        expected_types = {
            "speech",
            "letter",
            "proclamation",
            "newspaper_article",
            "journal_article",
            "book_excerpt",
            "biography",
            "timeline_entry",
            "curriculum",
            "dataset_doc",
            "dev_doc",
        }
        actual_types = {ct.value for ct in ContentType}
        assert actual_types == expected_types
