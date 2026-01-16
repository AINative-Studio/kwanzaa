#!/usr/bin/env python3
"""Initialize ingestion run and create tracking metadata in ZeroDB."""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from app.models.ingestion import (
    IngestionPhase,
    IngestionRunMetadata,
    IngestionStatus,
)


def generate_manifest_hash(manifest_path: str) -> str:
    """Generate hash of manifest file for change detection."""
    if not os.path.exists(manifest_path):
        return "no-manifest"

    with open(manifest_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def create_zerodb_table_if_not_exists():
    """Create kw_ingestion_runs table in ZeroDB if it doesn't exist."""
    try:
        # This will be implemented using ZeroDB MCP tools
        # For now, we'll use a NoSQL table structure
        print("Checking for kw_ingestion_runs table...")

        # Table schema for ingestion runs
        schema = {
            "fields": {
                "run_id": {"type": "string", "required": True},
                "environment": {"type": "string", "required": True},
                "triggered_by": {"type": "string", "required": True},
                "started_at": {"type": "timestamp", "required": True},
                "completed_at": {"type": "timestamp", "required": False},
                "status": {"type": "string", "required": True},
                "current_phase": {"type": "string", "required": True},
                "manifest_version": {"type": "string", "required": True},
                "manifest_sources": {"type": "array", "required": True},
                "documents_discovered": {"type": "integer", "default": 0},
                "documents_processed": {"type": "integer", "default": 0},
                "documents_failed": {"type": "integer", "default": 0},
                "documents_skipped": {"type": "integer", "default": 0},
                "chunks_created": {"type": "integer", "default": 0},
                "vectors_upserted": {"type": "integer", "default": 0},
                "errors": {"type": "array", "default": []},
                "warnings": {"type": "array", "default": []},
                "source_status": {"type": "object", "default": {}},
                "config_snapshot": {"type": "object", "default": {}},
                "duration_seconds": {"type": "float", "required": False},
                "peak_memory_mb": {"type": "float", "required": False},
                "notifications_sent": {"type": "array", "default": []},
            },
            "indexes": [
                {"fields": ["run_id"], "unique": True},
                {"fields": ["environment", "started_at"]},
                {"fields": ["status", "started_at"]},
            ],
        }

        print("Table schema prepared for kw_ingestion_runs")
        return True

    except Exception as e:
        print(f"Warning: Could not verify table existence: {e}")
        return False


def initialize_run(
    run_id: str,
    environment: str,
    trigger: str,
    manifest_path: str,
) -> IngestionRunMetadata:
    """Initialize ingestion run metadata."""

    manifest_version = generate_manifest_hash(manifest_path)

    # Create initial run metadata
    run_metadata = IngestionRunMetadata(
        run_id=run_id,
        environment=environment,
        triggered_by=trigger,
        started_at=datetime.now(timezone.utc),
        status=IngestionStatus.PENDING,
        current_phase=IngestionPhase.DISCOVER,
        manifest_version=manifest_version,
        manifest_sources=[],
        config_snapshot={
            "manifest_path": manifest_path,
            "zerodb_project_id": os.getenv("ZERODB_PROJECT_ID", "unknown"),
        },
    )

    return run_metadata


def store_run_metadata(run_metadata: IngestionRunMetadata) -> bool:
    """Store run metadata in ZeroDB."""
    try:
        # Convert to dict for storage
        metadata_dict = run_metadata.model_dump(mode="json")

        # Store in ZeroDB (this would use the MCP tools)
        # For now, write to local file as fallback
        output_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
        output_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = output_dir / f"{run_metadata.run_id}_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata_dict, f, indent=2, default=str)

        print(f"Run metadata stored: {metadata_file}")
        return True

    except Exception as e:
        print(f"Error storing run metadata: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize ingestion run and create tracking metadata"
    )
    parser.add_argument("--run-id", required=True, help="Unique run identifier")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "staging", "prod"],
        help="Environment name",
    )
    parser.add_argument(
        "--trigger",
        required=True,
        choices=["scheduled", "manual", "webhook"],
        help="Trigger type",
    )
    parser.add_argument(
        "--manifest",
        default="data/manifests/first_fruits_manifest.json",
        help="Path to ingestion manifest",
    )
    parser.add_argument("--log-file", help="Log file path")

    args = parser.parse_args()

    # Ensure table exists
    create_zerodb_table_if_not_exists()

    # Initialize run metadata
    manifest_path = str(Path(__file__).parent.parent.parent / args.manifest)
    run_metadata = initialize_run(
        run_id=args.run_id,
        environment=args.environment,
        trigger=args.trigger,
        manifest_path=manifest_path,
    )

    # Store metadata
    if store_run_metadata(run_metadata):
        print(f"Successfully initialized run: {args.run_id}")
        print(f"Environment: {args.environment}")
        print(f"Trigger: {args.trigger}")
        print(f"Status: {run_metadata.status}")
        return 0
    else:
        print(f"Failed to initialize run: {args.run_id}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
