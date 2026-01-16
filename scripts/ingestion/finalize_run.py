#!/usr/bin/env python3
"""Finalize ingestion run and update final status."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


def load_run_metadata(run_id: str) -> dict:
    """Load initial run metadata."""
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    metadata_file = log_dir / f"{run_id}_metadata.json"

    if not metadata_file.exists():
        return {}

    with open(metadata_file, "r") as f:
        return json.load(f)


def load_progress_data(run_id: str) -> dict:
    """Load progress data from metadata phase."""
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    progress_file = log_dir / f"{run_id}_progress.json"

    if not progress_file.exists():
        return {}

    with open(progress_file, "r") as f:
        return json.load(f)


def load_expansion_data(run_id: str) -> dict:
    """Load expansion data from fulltext phase."""
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    expansion_file = log_dir / f"{run_id}_expansion.json"

    if not expansion_file.exists():
        return {}

    with open(expansion_file, "r") as f:
        return json.load(f)


def calculate_final_stats(
    metadata: dict,
    progress: dict,
    expansion: dict,
) -> dict:
    """Calculate final statistics."""
    stats = {
        "documents_discovered": progress.get("total_discovered", 0),
        "documents_processed": progress.get("total_processed", 0),
        "documents_failed": progress.get("total_failed", 0),
        "chunks_created": expansion.get("total_chunks", 0),
        "vectors_upserted": expansion.get("total_vectors", 0),
    }

    # Calculate duration
    if metadata.get("started_at"):
        started_at = datetime.fromisoformat(metadata["started_at"].replace("Z", "+00:00"))
        completed_at = datetime.now(timezone.utc)
        duration = (completed_at - started_at).total_seconds()
        stats["duration_seconds"] = duration
        stats["completed_at"] = completed_at.isoformat()

    return stats


def determine_final_status(
    progress: dict,
    expansion: dict,
) -> str:
    """Determine final run status."""
    # Check for failures
    progress_results = progress.get("source_results", [])
    expansion_results = expansion.get("expansion_results", [])

    failed_metadata = any(r.get("status") == "failed" for r in progress_results)
    failed_expansion = any(r.get("status") == "failed" for r in expansion_results)

    if failed_metadata and failed_expansion:
        return "failed"
    elif failed_metadata or failed_expansion:
        return "partial"
    else:
        return "completed"


def finalize_run(run_id: str) -> dict:
    """Finalize the ingestion run."""
    print(f"Finalizing run: {run_id}")

    # Load all run data
    metadata = load_run_metadata(run_id)
    progress = load_progress_data(run_id)
    expansion = load_expansion_data(run_id)

    # Calculate final stats
    stats = calculate_final_stats(metadata, progress, expansion)

    # Determine final status
    final_status = determine_final_status(progress, expansion)

    # Update metadata
    metadata.update(stats)
    metadata["status"] = final_status
    metadata["current_phase"] = "complete"

    # Save final metadata
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    final_file = log_dir / f"{run_id}_final.json"

    with open(final_file, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"\nFinal Status: {final_status}")
    print(f"Duration: {stats.get('duration_seconds', 0):.2f}s")
    print(f"Documents discovered: {stats['documents_discovered']}")
    print(f"Documents processed: {stats['documents_processed']}")
    print(f"Chunks created: {stats['chunks_created']}")
    print(f"Vectors upserted: {stats['vectors_upserted']}")

    if stats["documents_failed"] > 0:
        print(f"Documents failed: {stats['documents_failed']}")

    return metadata


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Finalize ingestion run")
    parser.add_argument("--run-id", required=True, help="Run identifier")
    parser.add_argument("--log-file", help="Log file path")

    args = parser.parse_args()

    try:
        final_metadata = finalize_run(args.run_id)

        if final_metadata.get("status") == "failed":
            return 1

        return 0

    except Exception as e:
        print(f"Error finalizing run: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
