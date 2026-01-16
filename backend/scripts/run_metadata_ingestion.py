#!/usr/bin/env python3
"""Run metadata-first ingestion pipeline.

This script executes the metadata ingestion pipeline for the Kwanzaa First Fruits corpus.
It supports both CLI and programmatic execution.

Usage:
    python scripts/run_metadata_ingestion.py --manifest data/manifests/first_fruits_manifest.json
    python scripts/run_metadata_ingestion.py --manifest data/manifests/first_fruits_manifest.json --batch-size 50
    python scripts/run_metadata_ingestion.py --help
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.metadata_ingestion import (
    MetadataIngestionPipeline,
    IngestionError,
)


# Mock ZeroDB client for demonstration
class MockZeroDBClient:
    """Mock ZeroDB client for testing and demonstration."""

    async def insert_rows(self, table_id: str, rows: list, return_ids: bool = True):
        """Mock insert_rows method."""
        logging.info(f"[MOCK] Inserting {len(rows)} rows into {table_id}")
        return {"inserted_ids": [f"mock_id_{i}" for i in range(len(rows))]}

    async def get_table(self, table_id: str):
        """Mock get_table method."""
        logging.info(f"[MOCK] Checking if table {table_id} exists")
        return None  # Simulate table doesn't exist

    async def create_table(self, table_name: str, schema: dict, description: str = ""):
        """Mock create_table method."""
        logging.info(f"[MOCK] Creating table {table_name}")
        return {"table_name": table_name}


def setup_logging(log_level: str = "INFO", log_file: Path = None):
    """Configure logging for the ingestion pipeline.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers,
    )


async def run_ingestion(
    manifest_path: Path,
    batch_size: int = 100,
    max_retries: int = 3,
    output_dir: Path = None,
    use_mock_client: bool = True,
):
    """Run the metadata ingestion pipeline.

    Args:
        manifest_path: Path to First Fruits manifest
        batch_size: Batch size for bulk operations
        max_retries: Maximum retry attempts
        output_dir: Directory for output files
        use_mock_client: Use mock ZeroDB client (for testing)

    Returns:
        IngestionStats with results
    """
    logger = logging.getLogger(__name__)

    try:
        # Initialize ZeroDB client
        if use_mock_client:
            logger.warning("Using MOCK ZeroDB client - data will not be persisted")
            zerodb_client = MockZeroDBClient()
        else:
            # In production, initialize real ZeroDB client
            # from app.db.zerodb import ZeroDBClient
            # zerodb_client = ZeroDBClient()
            raise NotImplementedError("Real ZeroDB client not yet integrated")

        # Initialize pipeline
        logger.info("Initializing metadata ingestion pipeline")
        pipeline = MetadataIngestionPipeline(
            manifest_path=manifest_path,
            zerodb_client=zerodb_client,
            batch_size=batch_size,
            max_retries=max_retries,
        )

        # Run pipeline
        logger.info(f"Starting ingestion from manifest: {manifest_path}")
        stats = await pipeline.run()

        # Export stats
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            stats_file = output_dir / f"{stats.run_id}_stats.json"
            pipeline.export_stats(stats_file)
            logger.info(f"Stats exported to: {stats_file}")

        # Print summary
        logger.info("=" * 60)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Run ID: {stats.run_id}")
        logger.info(f"Started: {stats.started_at}")
        logger.info(f"Completed: {stats.completed_at}")
        logger.info(f"Sources Processed: {stats.sources_processed}/{stats.total_sources}")
        logger.info(f"Sources Failed: {stats.sources_failed}")
        logger.info(f"Documents Inserted: {stats.documents_inserted}")
        logger.info(f"Documents Failed: {stats.documents_failed}")
        logger.info(f"Total Errors: {len(stats.errors)}")

        if stats.errors:
            logger.warning("Errors encountered during ingestion:")
            for error in stats.errors[:5]:  # Show first 5 errors
                logger.warning(f"  - {error['source_id']}: {error['error_message']}")
            if len(stats.errors) > 5:
                logger.warning(f"  ... and {len(stats.errors) - 5} more errors")

        logger.info("=" * 60)

        return stats

    except IngestionError as e:
        logger.error(f"Ingestion pipeline failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Run metadata-first ingestion pipeline for Kwanzaa First Fruits corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python scripts/run_metadata_ingestion.py --manifest data/manifests/first_fruits_manifest.json

  # Run with custom batch size and output directory
  python scripts/run_metadata_ingestion.py \\
    --manifest data/manifests/first_fruits_manifest.json \\
    --batch-size 50 \\
    --output-dir data/ingestion_runs

  # Run with debug logging
  python scripts/run_metadata_ingestion.py \\
    --manifest data/manifests/first_fruits_manifest.json \\
    --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to First Fruits manifest JSON file",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for bulk operations (default: 100)",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for failed operations (default: 3)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/ingestion_runs"),
        help="Directory for output files (default: data/ingestion_runs)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        help="Optional log file path (default: stdout only)",
    )

    parser.add_argument(
        "--use-real-client",
        action="store_true",
        help="Use real ZeroDB client instead of mock (requires configuration)",
    )

    args = parser.parse_args()

    # Validate manifest path
    if not args.manifest.exists():
        print(f"Error: Manifest file not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    # Setup logging
    setup_logging(log_level=args.log_level, log_file=args.log_file)

    # Run ingestion
    try:
        stats = asyncio.run(
            run_ingestion(
                manifest_path=args.manifest,
                batch_size=args.batch_size,
                max_retries=args.max_retries,
                output_dir=args.output_dir,
                use_mock_client=not args.use_real_client,
            )
        )

        # Exit with success
        sys.exit(0)

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
