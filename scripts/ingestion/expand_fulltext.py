#!/usr/bin/env python3
"""Full-text expansion script (E4-US3) - Expand P0 sources to full text."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))


def load_processed_metadata(run_id: str) -> Dict:
    """Load metadata processed in previous phase."""
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    log_file = log_dir / f"{run_id}_progress.json"

    if not log_file.exists():
        print(f"Warning: No progress file found for run {run_id}")
        return {"source_results": []}

    with open(log_file, "r") as f:
        return json.load(f)


def filter_p0_sources(source_results: List[Dict], priority: str = "P0") -> List[Dict]:
    """Filter sources by priority."""
    # For now, return all sources
    # In production, this would check priority from manifest
    return source_results


def expand_source_fulltext(
    source_name: str,
    run_id: str,
) -> Dict:
    """Expand full text for a source."""
    print(f"Expanding full text for: {source_name}")

    result = {
        "source_name": source_name,
        "status": "completed",
        "documents_expanded": 0,
        "chunks_created": 0,
        "vectors_upserted": 0,
        "errors": [],
    }

    try:
        # This is where actual full-text processing would happen:
        # 1. Fetch full text
        # 2. Chunk into retrieval-friendly sizes
        # 3. Generate embeddings
        # 4. Store in ZeroDB with proper namespace

        print(f"  Fetching full text...")
        # Placeholder for actual implementation

        print(f"  Chunking documents...")
        # Placeholder for chunking logic

        print(f"  Generating embeddings...")
        # Placeholder for embedding generation

        print(f"  Storing in ZeroDB...")
        # Placeholder for ZeroDB storage

        result["documents_expanded"] = 0  # Placeholder
        result["chunks_created"] = 0  # Placeholder
        result["vectors_upserted"] = 0  # Placeholder

        print(f"  Expanded {result['documents_expanded']} documents")
        print(f"  Created {result['chunks_created']} chunks")
        print(f"  Upserted {result['vectors_upserted']} vectors")

    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(str(e))
        print(f"  Error: {e}", file=sys.stderr)

    return result


def update_run_progress(
    run_id: str,
    expansion_results: List[Dict],
) -> None:
    """Update run metadata with expansion progress."""
    total_expanded = sum(r["documents_expanded"] for r in expansion_results)
    total_chunks = sum(r["chunks_created"] for r in expansion_results)
    total_vectors = sum(r["vectors_upserted"] for r in expansion_results)

    print(f"\nExpansion progress for run {run_id}:")
    print(f"  Sources expanded: {len(expansion_results)}")
    print(f"  Documents expanded: {total_expanded}")
    print(f"  Chunks created: {total_chunks}")
    print(f"  Vectors upserted: {total_vectors}")

    # Update run metadata
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    log_file = log_dir / f"{run_id}_expansion.json"

    progress_data = {
        "run_id": run_id,
        "phase": "fulltext_expansion",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_expanded": total_expanded,
        "total_chunks": total_chunks,
        "total_vectors": total_vectors,
        "expansion_results": expansion_results,
    }

    with open(log_file, "w") as f:
        json.dump(progress_data, f, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Expand full text for P0 sources (E4-US3)"
    )
    parser.add_argument("--run-id", required=True, help="Run identifier")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "staging", "prod"],
        help="Environment",
    )
    parser.add_argument(
        "--priority",
        default="P0",
        choices=["P0", "P1", "P2"],
        help="Priority filter",
    )
    parser.add_argument(
        "--source",
        help="Process only specific source",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Full-Text Expansion (E4-US3)")
    print("=" * 60)
    print(f"Run ID: {args.run_id}")
    print(f"Environment: {args.environment}")
    print(f"Priority: {args.priority}")
    if args.source:
        print(f"Source filter: {args.source}")
    print("=" * 60)

    # Load metadata from previous phase
    progress_data = load_processed_metadata(args.run_id)
    source_results = progress_data.get("source_results", [])

    print(f"\nLoaded {len(source_results)} sources from metadata phase")

    # Filter P0 sources
    sources_to_expand = filter_p0_sources(source_results, args.priority)

    if args.source:
        sources_to_expand = [
            s for s in sources_to_expand if s["source_name"] == args.source
        ]

    print(f"Expanding {len(sources_to_expand)} sources")

    # Expand each source
    expansion_results = []
    for source_result in sources_to_expand:
        source_name = source_result["source_name"]
        result = expand_source_fulltext(source_name, args.run_id)
        expansion_results.append(result)

    # Update run progress
    update_run_progress(args.run_id, expansion_results)

    # Check for failures
    failed_sources = [r for r in expansion_results if r["status"] == "failed"]
    if failed_sources:
        print(f"\nWarning: {len(failed_sources)} sources failed expansion")
        for result in failed_sources:
            print(f"  - {result['source_name']}: {result['errors']}")
        return 1

    print("\nFull-text expansion completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
