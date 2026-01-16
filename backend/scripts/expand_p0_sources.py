#!/usr/bin/env python3
"""Script to expand P0 sources from manifest to full text.

This script demonstrates the complete workflow for selective full-text expansion:
1. Load manifest
2. Filter P0 sources
3. Extract full text (from files or API)
4. Chunk and embed
5. Store in ZeroDB

Usage:
    python scripts/expand_p0_sources.py --manifest data/manifests/first_fruits_manifest.json
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.zerodb import ZeroDBClient
from app.services.embedding import EmbeddingService
from app.services.manifest_loader import ManifestLoader, SourceManifest, AccessMethod
from app.services.text_expansion import TextExpansionService


async def extract_text_from_source(source: SourceManifest) -> str:
    """Extract full text from a source based on access method.
    
    Args:
        source: Source manifest entry
        
    Returns:
        Full text of the source
        
    Note:
        This is a stub implementation. Real implementation would:
        - Read from local files
        - Download from URLs
        - Call APIs
        - Handle various formats (PDF, HTML, TXT, etc.)
    """
    if source.access_method == AccessMethod.LOCAL_FILE and source.location:
        # Read from local file
        file_path = Path(source.location)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise FileNotFoundError(f"Source file not found: {file_path}")
    
    elif source.access_method == AccessMethod.HTTP_DOWNLOAD:
        # TODO: Implement HTTP download
        raise NotImplementedError("HTTP download not yet implemented")
    
    elif source.access_method == AccessMethod.API:
        # TODO: Implement API extraction
        raise NotImplementedError("API extraction not yet implemented")
    
    else:
        raise ValueError(f"Unsupported access method: {source.access_method}")


def create_document_metadata(source: SourceManifest) -> Dict:
    """Create document metadata from source manifest.
    
    Args:
        source: Source manifest entry
        
    Returns:
        Metadata dictionary for document
    """
    return {
        "source_id": source.source_id,
        "document_id": f"{source.source_id}_001",  # TODO: Handle multiple docs per source
        "source_org": source.source_org,
        "canonical_url": source.canonical_url,
        "license_info": source.license_info,
        "year": source.year,
        "content_type": source.content_type,
        "tags": source.tags or [],
        "priority": source.priority,
    }


async def expand_p0_sources(
    manifest_path: Path,
    namespace: str = "kwanzaa_primary_sources",
    skip_existing: bool = True,
    dry_run: bool = False,
) -> None:
    """Main function to expand P0 sources.
    
    Args:
        manifest_path: Path to FirstFruitsManifest JSON file
        namespace: ZeroDB namespace for storage
        skip_existing: Skip sources that are already expanded
        dry_run: Run without actually storing data
    """
    print(f"\n{'='*60}")
    print("P0 Source Expansion Pipeline")
    print(f"{'='*60}\n")
    
    # Load manifest
    print(f"Loading manifest from: {manifest_path}")
    loader = ManifestLoader(manifest_path=manifest_path)
    loader.load_manifest()
    
    # Get statistics
    stats = loader.get_statistics()
    print(f"\nManifest Statistics:")
    print(f"  Total sources: {stats['total_sources']}")
    print(f"  P0 sources: {stats['p0_sources']}")
    print(f"  Priority distribution: {stats['priority_distribution']}")
    
    # Validate manifest
    print("\nValidating manifest...")
    issues = loader.validate_manifest()
    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return
    print("Manifest validation passed!")
    
    # Get P0 sources
    p0_sources = loader.get_p0_sources()
    print(f"\nFound {len(p0_sources)} P0 sources to expand:")
    for source in p0_sources:
        print(f"  - {source.source_name} ({source.source_id})")
    
    if dry_run:
        print("\nDry run mode - skipping expansion")
        return
    
    # Initialize services
    print("\nInitializing services...")
    embedding_service = EmbeddingService()
    zerodb_client = ZeroDBClient() if not dry_run else None
    expansion_service = TextExpansionService(
        embedding_service=embedding_service,
        zerodb_client=zerodb_client,
    )
    
    # Get service stats
    service_stats = expansion_service.get_stats()
    print(f"  Chunk size: {service_stats['chunk_size']} tokens")
    print(f"  Chunk overlap: {service_stats['chunk_overlap']} tokens")
    print(f"  Embedding model: {service_stats['embedding_model']}")
    print(f"  Embedding dimensions: {service_stats['embedding_dimensions']}")
    
    # Process each P0 source
    print(f"\n{'='*60}")
    print("Processing P0 Sources")
    print(f"{'='*60}\n")
    
    total_sources = len(p0_sources)
    successful = 0
    skipped = 0
    failed = 0
    
    for i, source in enumerate(p0_sources, 1):
        print(f"\n[{i}/{total_sources}] Processing: {source.source_name}")
        print(f"  Source ID: {source.source_id}")
        print(f"  Type: {source.source_type.value}")
        print(f"  Access method: {source.access_method.value}")
        
        try:
            # Extract text
            print(f"  Extracting text...")
            text = await extract_text_from_source(source)
            print(f"  Text length: {len(text)} characters")
            
            # Create metadata
            metadata = create_document_metadata(source)
            
            # Expand document
            print(f"  Expanding to chunks...")
            result = await expansion_service.expand_document(
                document_text=text,
                metadata=metadata,
                namespace=namespace,
                skip_if_exists=skip_existing,
            )
            
            # Report results
            if result['status'] == 'success':
                print(f"  ✓ Success!")
                print(f"    Chunks created: {result['chunks_created']}")
                print(f"    Chunks stored: {result['chunks_stored']}")
                print(f"    Embedding time: {result['embedding_time_ms']}ms")
                successful += 1
            
            elif result['status'] == 'skipped':
                print(f"  ⊘ Skipped: {result['reason']}")
                skipped += 1
            
            else:
                print(f"  ⚠ Partial success or error:")
                print(f"    Status: {result['status']}")
                print(f"    Chunks stored: {result['chunks_stored']}/{result['chunks_created']}")
                if result.get('errors'):
                    print(f"    Errors: {len(result['errors'])}")
                failed += 1
        
        except FileNotFoundError as e:
            print(f"  ✗ Error: {e}")
            print(f"    Skipping source (file not found)")
            failed += 1
        
        except NotImplementedError as e:
            print(f"  ⊘ Skipped: {e}")
            skipped += 1
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print("Expansion Summary")
    print(f"{'='*60}")
    print(f"\nTotal sources: {total_sources}")
    print(f"  Successful: {successful}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")
    print(f"\nNamespace: {namespace}")
    print()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Expand P0 sources from manifest to full text with embeddings"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/first_fruits_manifest.json"),
        help="Path to FirstFruitsManifest JSON file",
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default="kwanzaa_primary_sources",
        help="ZeroDB namespace for storage",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-expansion of existing sources",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without storing data (validation only)",
    )
    
    args = parser.parse_args()
    
    # Run async main
    asyncio.run(
        expand_p0_sources(
            manifest_path=args.manifest,
            namespace=args.namespace,
            skip_existing=not args.force,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
