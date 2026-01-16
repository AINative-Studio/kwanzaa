#!/usr/bin/env python3
"""Update run status (used for error handling)."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def update_status(run_id: str, status: str, error: str = None) -> bool:
    """Update run status."""
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    metadata_file = log_dir / f"{run_id}_metadata.json"

    if not metadata_file.exists():
        print(f"Error: Metadata file not found for run {run_id}", file=sys.stderr)
        return False

    # Load existing metadata
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    # Update status
    metadata["status"] = status
    metadata["updated_at"] = datetime.now(timezone.utc).isoformat()

    if error:
        if "errors" not in metadata:
            metadata["errors"] = []
        metadata["errors"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error,
        })

    # Save updated metadata
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"Updated run {run_id} status to: {status}")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update ingestion run status")
    parser.add_argument("--run-id", required=True, help="Run identifier")
    parser.add_argument("--status", required=True, help="New status")
    parser.add_argument("--error", help="Error message if failed")

    args = parser.parse_args()

    if update_status(args.run_id, args.status, args.error):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
