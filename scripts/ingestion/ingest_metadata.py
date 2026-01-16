#!/usr/bin/env python3
"""Metadata ingestion script (E4-US2) - Discover and store metadata first."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


def load_manifest(manifest_path: str) -> Dict:
    """Load ingestion manifest."""
    try:
        with open(manifest_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading manifest: {e}", file=sys.stderr)
        sys.exit(1)


def filter_sources_for_processing(
    sources: List[Dict],
    incremental: bool = True,
    specific_source: Optional[str] = None,
) -> List[Dict]:
    """Filter sources based on processing criteria."""
    filtered = []

    for source in sources:
        # Skip if specific source requested and doesn't match
        if specific_source and source.get("source_name") != specific_source:
            continue

        # Skip disabled sources
        if not source.get("enabled", True):
            print(f"Skipping disabled source: {source.get('source_name')}")
            continue

        # For incremental, check if source needs processing
        if incremental:
            # Check if source has been processed recently
            last_processed = source.get("last_processed_at")
            if last_processed:
                # Add logic to skip if processed recently
                # For now, always process
                pass

        filtered.append(source)

    return filtered


def discover_records_from_source(
    source: Dict,
    run_id: str,
) -> Dict:
    """Discover records from a source."""
    source_name = source.get("source_name")
    source_type = source.get("source_type")
    access_method = source.get("access_method")

    print(f"Discovering records from: {source_name}")
    print(f"  Type: {source_type}")
    print(f"  Access: {access_method}")

    result = {
        "source_name": source_name,
        "status": "completed",
        "discovered": 0,
        "processed": 0,
        "failed": 0,
        "errors": [],
    }

    try:
        # This is where actual source-specific ingestion would happen
        # For now, simulate discovery
        if access_method == "api":
            # Use API client to fetch records
            print(f"  Using API endpoint: {source.get('base_url')}")
            result["discovered"] = 0  # Placeholder

        elif access_method == "bulk":
            # Download and process bulk data
            print(f"  Processing bulk data from: {source.get('base_url')}")
            result["discovered"] = 0  # Placeholder

        elif access_method == "allowed_scrape":
            # Respectful scraping with rate limits
            print(f"  Scraping with rate limit: {source.get('rate_limit_per_second', 1.0)}/s")
            result["discovered"] = 0  # Placeholder

        # Store metadata in ZeroDB
        # For MVP, we log the operation
        print(f"  Discovered {result['discovered']} records")

    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(str(e))
        print(f"  Error: {e}", file=sys.stderr)

    return result


def update_run_progress(
    run_id: str,
    source_results: List[Dict],
) -> None:
    """Update run metadata with progress."""
    total_discovered = sum(r["discovered"] for r in source_results)
    total_processed = sum(r["processed"] for r in source_results)
    total_failed = sum(r["failed"] for r in source_results)

    print(f"\nProgress for run {run_id}:")
    print(f"  Sources processed: {len(source_results)}")
    print(f"  Records discovered: {total_discovered}")
    print(f"  Records processed: {total_processed}")
    print(f"  Records failed: {total_failed}")

    # Update run metadata in ZeroDB
    # For now, write to log file
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    log_file = log_dir / f"{run_id}_progress.json"

    progress_data = {
        "run_id": run_id,
        "phase": "metadata_ingestion",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_discovered": total_discovered,
        "total_processed": total_processed,
        "total_failed": total_failed,
        "source_results": source_results,
    }

    with open(log_file, "w") as f:
        json.dump(progress_data, f, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest metadata from sources (E4-US2)"
    )
    parser.add_argument("--run-id", required=True, help="Run identifier")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "staging", "prod"],
        help="Environment",
    )
    parser.add_argument(
        "--manifest",
        default="data/manifests/first_fruits_manifest.json",
        help="Manifest path",
    )
    parser.add_argument(
        "--incremental",
        default="true",
        choices=["true", "false"],
        help="Use incremental processing",
    )
    parser.add_argument(
        "--source",
        help="Process only specific source",
    )

    args = parser.parse_args()

    incremental = args.incremental == "true"

    print("=" * 60)
    print("Metadata Ingestion (E4-US2)")
    print("=" * 60)
    print(f"Run ID: {args.run_id}")
    print(f"Environment: {args.environment}")
    print(f"Incremental: {incremental}")
    if args.source:
        print(f"Source filter: {args.source}")
    print("=" * 60)

    # Load manifest
    manifest_path = Path(__file__).parent.parent.parent / args.manifest
    manifest = load_manifest(str(manifest_path))

    sources = manifest.get("sources", [])
    print(f"\nLoaded {len(sources)} sources from manifest")

    # Filter sources for processing
    sources_to_process = filter_sources_for_processing(
        sources,
        incremental=incremental,
        specific_source=args.source,
    )
    print(f"Processing {len(sources_to_process)} sources")

    # Process each source
    source_results = []
    for source in sources_to_process:
        result = discover_records_from_source(source, args.run_id)
        source_results.append(result)

    # Update run progress
    update_run_progress(args.run_id, source_results)

    # Check for failures
    failed_sources = [r for r in source_results if r["status"] == "failed"]
    if failed_sources:
        print(f"\nWarning: {len(failed_sources)} sources failed")
        for result in failed_sources:
            print(f"  - {result['source_name']}: {result['errors']}")
        return 1

    print("\nMetadata ingestion completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
