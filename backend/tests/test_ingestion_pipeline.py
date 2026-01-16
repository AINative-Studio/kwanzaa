"""Integration tests for ingestion pipeline."""

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import pytest


class TestIngestionPipeline:
    """Test suite for ingestion pipeline components."""

    @pytest.fixture
    def test_manifest(self, tmp_path):
        """Create a test manifest file."""
        manifest = {
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "sources": [
                {
                    "source_name": "Test Source",
                    "source_type": "test",
                    "base_url": "https://example.com",
                    "access_method": "api",
                    "license": "Public Domain",
                    "priority": "P0",
                    "default_namespace": "test_namespace",
                    "enabled": True,
                    "tags": ["test"],
                }
            ],
            "global_config": {
                "max_parallel_sources": 1,
                "default_rate_limit": 1.0,
                "chunk_size": 1000,
                "chunk_overlap": 200,
            },
            "namespaces": {
                "test_namespace": {"description": "Test namespace"}
            },
        }

        manifest_file = tmp_path / "test_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f)

        return str(manifest_file)

    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Set up mock environment variables."""
        monkeypatch.setenv("ZERODB_API_KEY", "test-key")
        monkeypatch.setenv("ZERODB_PROJECT_ID", "test-project")
        monkeypatch.setenv("ENVIRONMENT", "dev")

    def test_init_run_script(self, test_manifest, mock_env, tmp_path):
        """Test run initialization script."""
        run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Run init script
        result = subprocess.run(
            [
                "python3",
                "scripts/ingestion/init_run.py",
                "--run-id",
                run_id,
                "--environment",
                "dev",
                "--trigger",
                "manual",
                "--manifest",
                test_manifest,
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Init script failed: {result.stderr}"
        assert "Successfully initialized run" in result.stdout

        # Check metadata file was created
        log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
        metadata_file = log_dir / f"{run_id}_metadata.json"
        assert metadata_file.exists()

        # Verify metadata contents
        with open(metadata_file) as f:
            metadata = json.load(f)

        assert metadata["run_id"] == run_id
        assert metadata["environment"] == "dev"
        assert metadata["triggered_by"] == "manual"
        assert metadata["status"] == "pending"

    def test_metadata_ingestion_script(self, test_manifest, mock_env):
        """Test metadata ingestion script."""
        run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize run first
        subprocess.run(
            [
                "python3",
                "scripts/ingestion/init_run.py",
                "--run-id",
                run_id,
                "--environment",
                "dev",
                "--trigger",
                "manual",
                "--manifest",
                test_manifest,
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
        )

        # Run metadata ingestion
        result = subprocess.run(
            [
                "python3",
                "scripts/ingestion/ingest_metadata.py",
                "--run-id",
                run_id,
                "--environment",
                "dev",
                "--manifest",
                test_manifest,
                "--incremental",
                "true",
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Metadata ingestion failed: {result.stderr}"
        assert "Metadata ingestion completed" in result.stdout

        # Check progress file was created
        log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
        progress_file = log_dir / f"{run_id}_progress.json"
        assert progress_file.exists()

    def test_finalize_run_script(self, test_manifest, mock_env):
        """Test run finalization script."""
        run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize and run pipeline
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"

        # Init
        subprocess.run(
            [
                "python3",
                str(scripts_dir / "ingestion" / "init_run.py"),
                "--run-id",
                run_id,
                "--environment",
                "dev",
                "--trigger",
                "manual",
                "--manifest",
                test_manifest,
            ],
            capture_output=True,
        )

        # Metadata ingestion
        subprocess.run(
            [
                "python3",
                str(scripts_dir / "ingestion" / "ingest_metadata.py"),
                "--run-id",
                run_id,
                "--environment",
                "dev",
                "--manifest",
                test_manifest,
            ],
            capture_output=True,
        )

        # Finalize
        result = subprocess.run(
            [
                "python3",
                str(scripts_dir / "ingestion" / "finalize_run.py"),
                "--run-id",
                run_id,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Finalize script failed: {result.stderr}"
        assert "Final Status" in result.stdout

        # Check final file was created
        log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
        final_file = log_dir / f"{run_id}_final.json"
        assert final_file.exists()

        # Verify final metadata
        with open(final_file) as f:
            final_metadata = json.load(f)

        assert final_metadata["run_id"] == run_id
        assert "status" in final_metadata
        assert "duration_seconds" in final_metadata

    def test_notification_script(self, test_manifest, mock_env):
        """Test notification sending script."""
        run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Run notification script (without actual webhooks)
        result = subprocess.run(
            [
                "python3",
                "scripts/ingestion/send_notification.py",
                "--run-id",
                run_id,
                "--status",
                "completed",
                "--summary",
                "Test notification",
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
        )

        # Should succeed even without notification channels configured
        assert result.returncode == 0

    def test_update_status_script(self, test_manifest, mock_env):
        """Test status update script."""
        run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize run
        subprocess.run(
            [
                "python3",
                "scripts/ingestion/init_run.py",
                "--run-id",
                run_id,
                "--environment",
                "dev",
                "--trigger",
                "manual",
                "--manifest",
                test_manifest,
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
        )

        # Update status
        result = subprocess.run(
            [
                "python3",
                "scripts/ingestion/update_run_status.py",
                "--run-id",
                run_id,
                "--status",
                "failed",
                "--error",
                "Test error",
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Update status failed: {result.stderr}"
        assert "Updated run" in result.stdout

        # Verify status was updated
        log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
        metadata_file = log_dir / f"{run_id}_metadata.json"

        with open(metadata_file) as f:
            metadata = json.load(f)

        assert metadata["status"] == "failed"
        assert len(metadata.get("errors", [])) > 0


class TestIngestionModels:
    """Test ingestion data models."""

    def test_ingestion_run_metadata_creation(self):
        """Test creating ingestion run metadata."""
        from app.models.ingestion import (
            IngestionPhase,
            IngestionRunMetadata,
            IngestionStatus,
        )

        metadata = IngestionRunMetadata(
            run_id="test_run_001",
            environment="dev",
            triggered_by="manual",
            started_at=datetime.utcnow(),
            status=IngestionStatus.PENDING,
            current_phase=IngestionPhase.DISCOVER,
            manifest_version="abc123",
            manifest_sources=["source1", "source2"],
        )

        assert metadata.run_id == "test_run_001"
        assert metadata.status == IngestionStatus.PENDING
        assert metadata.documents_discovered == 0

        # Test JSON serialization
        metadata_dict = metadata.model_dump(mode="json")
        assert "run_id" in metadata_dict
        assert "started_at" in metadata_dict

    def test_ingestion_manifest_structure(self):
        """Test ingestion manifest structure."""
        from app.models.ingestion import (
            IngestionManifest,
            IngestionSourceMetadata,
        )

        source = IngestionSourceMetadata(
            source_name="Test Source",
            source_type="archive",
            base_url="https://example.com",
            access_method="api",
            license="Public Domain",
            priority="P0",
            default_namespace="test_namespace",
            tags=["test"],
        )

        manifest = IngestionManifest(
            version="1.0.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            sources=[source],
        )

        assert len(manifest.sources) == 1
        assert manifest.sources[0].source_name == "Test Source"

    def test_notification_config(self):
        """Test notification configuration."""
        from app.models.ingestion import NotificationConfig

        config = NotificationConfig(
            enabled=True,
            email_enabled=True,
            email_recipients=["test@example.com"],
            webhook_enabled=True,
            webhook_url="https://example.com/webhook",
            notify_on_success=True,
            notify_on_failure=True,
        )

        assert config.enabled
        assert config.email_enabled
        assert len(config.email_recipients) == 1


class TestManualTriggerCLI:
    """Test manual trigger CLI functionality."""

    def test_manual_trigger_help(self):
        """Test manual trigger help command."""
        result = subprocess.run(
            ["bash", "scripts/manual_trigger.sh", "help"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Manual Ingestion Trigger Script" in result.stdout
        assert "Commands:" in result.stdout

    def test_manual_trigger_status(self):
        """Test status command."""
        result = subprocess.run(
            ["bash", "scripts/manual_trigger.sh", "status"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
        )

        # Should succeed even if no runs found
        assert result.returncode == 0


@pytest.mark.integration
class TestEndToEndIngestion:
    """End-to-end integration tests (requires live credentials)."""

    @pytest.mark.skipif(
        not os.getenv("ZERODB_API_KEY"),
        reason="ZERODB_API_KEY not set",
    )
    def test_full_ingestion_pipeline_dry_run(self, tmp_path):
        """Test full pipeline in dry-run mode."""
        # This test requires actual credentials but runs in dry-run mode
        result = subprocess.run(
            [
                "bash",
                "scripts/daily_ingestion.sh",
                "--environment",
                "dev",
                "--dry-run",
                "--manual",
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Dry run should succeed
        assert result.returncode == 0 or "DRY RUN" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
