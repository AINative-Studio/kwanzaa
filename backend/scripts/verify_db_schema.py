#!/usr/bin/env python3
"""Verify database schema setup and table creation.

This script verifies that:
1. All 6 tables can be imported
2. Table schemas are correctly defined
3. Relationships are properly configured
4. Constraints are in place

Run this before applying migrations to catch any issues.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def verify_models():
    """Verify that all models can be imported and have correct structure."""
    print("=" * 80)
    print("Verifying Database Models")
    print("=" * 80)

    try:
        from app.db.models import (
            Chunk,
            Collection,
            Document,
            Evaluation,
            IngestionLog,
            Source,
        )

        print("✓ All models imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import models: {e}")
        return False

    # Verify table names
    tables = {
        "Source": ("sources", Source),
        "Document": ("documents", Document),
        "Chunk": ("chunks", Chunk),
        "Collection": ("collections", Collection),
        "IngestionLog": ("ingestion_logs", IngestionLog),
        "Evaluation": ("evaluations", Evaluation),
    }

    print("\nTable Names:")
    for model_name, (expected_table, model) in tables.items():
        actual_table = model.__tablename__
        if actual_table == expected_table:
            print(f"  ✓ {model_name}: {actual_table}")
        else:
            print(f"  ✗ {model_name}: expected '{expected_table}', got '{actual_table}'")
            return False

    # Verify relationships
    print("\nRelationships:")

    # Source -> Documents
    if hasattr(Source, "documents"):
        print("  ✓ Source.documents relationship exists")
    else:
        print("  ✗ Source.documents relationship missing")
        return False

    # Document -> Source
    if hasattr(Document, "source"):
        print("  ✓ Document.source relationship exists")
    else:
        print("  ✗ Document.source relationship missing")
        return False

    # Document -> Chunks
    if hasattr(Document, "chunks"):
        print("  ✓ Document.chunks relationship exists")
    else:
        print("  ✗ Document.chunks relationship missing")
        return False

    # Chunk -> Document
    if hasattr(Chunk, "document"):
        print("  ✓ Chunk.document relationship exists")
    else:
        print("  ✗ Chunk.document relationship missing")
        return False

    # Verify key columns
    print("\nKey Columns:")
    required_columns = {
        "Source": ["source_id", "source_name", "canonical_url", "license"],
        "Document": ["document_id", "source_id", "canonical_url", "year", "content_type", "license"],
        "Chunk": ["chunk_id", "document_id", "chunk_index", "chunk_text", "citation_label", "namespace"],
        "Collection": ["collection_id", "collection_name"],
        "IngestionLog": ["run_id", "source_name", "started_at", "status"],
        "Evaluation": ["eval_id", "eval_type", "run_date", "metrics", "test_cases", "passed", "failed"],
    }

    for model_name, (_, model) in tables.items():
        columns = [col.name for col in model.__table__.columns]
        required = required_columns.get(model_name, [])

        missing = [col for col in required if col not in columns]
        if missing:
            print(f"  ✗ {model_name} missing columns: {missing}")
            return False
        else:
            print(f"  ✓ {model_name} has all required columns")

    # Verify constraints
    print("\nConstraints:")

    # Check Source constraints
    source_constraints = [c.name for c in Source.__table__.constraints]
    if "check_priority_range" in source_constraints:
        print("  ✓ Source.check_priority_range exists")
    else:
        print("  ✗ Source.check_priority_range missing")
        return False

    # Check Document constraints
    doc_constraints = [c.name for c in Document.__table__.constraints]
    if "check_year_range" in doc_constraints:
        print("  ✓ Document.check_year_range exists")
    else:
        print("  ✗ Document.check_year_range missing")
        return False

    # Check Chunk constraints
    chunk_constraints = [c.name for c in Chunk.__table__.constraints]
    if "check_namespace" in chunk_constraints:
        print("  ✓ Chunk.check_namespace exists")
    else:
        print("  ✗ Chunk.check_namespace missing")
        return False

    # Check Evaluation constraints
    eval_constraints = [c.name for c in Evaluation.__table__.constraints]
    if "check_passed_failed_sum" in eval_constraints:
        print("  ✓ Evaluation.check_passed_failed_sum exists")
    else:
        print("  ✗ Evaluation.check_passed_failed_sum missing")
        return False

    print("\n" + "=" * 80)
    print("✓ All verification checks passed!")
    print("=" * 80)
    return True


def verify_alembic():
    """Verify Alembic configuration."""
    print("\n" + "=" * 80)
    print("Verifying Alembic Configuration")
    print("=" * 80)

    alembic_ini = backend_dir / "alembic.ini"
    alembic_dir = backend_dir / "alembic"
    env_py = alembic_dir / "env.py"
    versions_dir = alembic_dir / "versions"

    files_to_check = [
        ("alembic.ini", alembic_ini),
        ("alembic/env.py", env_py),
        ("alembic/versions/", versions_dir),
    ]

    for name, path in files_to_check:
        if path.exists():
            print(f"  ✓ {name} exists")
        else:
            print(f"  ✗ {name} missing")
            return False

    # Check for initial migration
    migration_files = list(versions_dir.glob("*.py"))
    if migration_files:
        print(f"  ✓ Found {len(migration_files)} migration(s)")
        for mig in migration_files:
            print(f"    - {mig.name}")
    else:
        print("  ⚠ No migrations found (this is OK if you haven't created them yet)")

    print("\n" + "=" * 80)
    print("✓ Alembic configuration verified!")
    print("=" * 80)
    return True


def verify_base():
    """Verify database base configuration."""
    print("\n" + "=" * 80)
    print("Verifying Database Base Configuration")
    print("=" * 80)

    try:
        from app.db.base import Base, get_db

        print("  ✓ Base class imported")
        print("  ✓ get_db function imported")

        # Verify Base has metadata
        if hasattr(Base, "metadata"):
            print("  ✓ Base.metadata exists")

            # Count registered tables
            table_count = len(Base.metadata.tables)
            print(f"  ✓ {table_count} tables registered in Base.metadata")

            if table_count == 6:
                print("  ✓ Correct number of tables (6)")
            else:
                print(f"  ✗ Expected 6 tables, got {table_count}")
                return False
        else:
            print("  ✗ Base.metadata missing")
            return False

    except ImportError as e:
        print(f"  ✗ Failed to import base: {e}")
        return False

    print("\n" + "=" * 80)
    print("✓ Database base configuration verified!")
    print("=" * 80)
    return True


def main():
    """Run all verification checks."""
    print("\n" + "=" * 80)
    print("KWANZAA DATABASE SCHEMA VERIFICATION")
    print("=" * 80)

    checks = [
        ("Models", verify_models),
        ("Base", verify_base),
        ("Alembic", verify_alembic),
    ]

    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} verification failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n" + "=" * 80)
        print("✓ ALL CHECKS PASSED!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Ensure PostgreSQL is running")
        print("2. Update backend/.env with DATABASE_URL")
        print("3. Run: cd backend && alembic upgrade head")
        print("4. Verify tables created: psql -d kwanzaa -c '\\dt'")
        return 0
    else:
        print("\n" + "=" * 80)
        print("✗ SOME CHECKS FAILED")
        print("=" * 80)
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
