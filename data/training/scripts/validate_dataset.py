#!/usr/bin/env python3
"""Validation script for Kwanzaa adapter training datasets.

Usage:
    python validate_dataset.py <dataset_file.json> [--report <output.txt>] [--verbose]
    python validate_dataset.py data/training/examples/*.json --report report.txt

Validates training datasets against the schema defined in data/training/models.py
and provides detailed error reporting and statistics.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from data.training.models import TrainingDataset
from pydantic import ValidationError


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colorize(text: str, color: str) -> str:
    """Add color to text for terminal output."""
    return f"{color}{text}{Colors.ENDC}"


def validate_dataset_file(file_path: Path, verbose: bool = False) -> Tuple[bool, Dict, List[str]]:
    """Validate a single dataset file.

    Args:
        file_path: Path to JSON dataset file
        verbose: Whether to print verbose validation details

    Returns:
        Tuple of (success: bool, dataset_dict: dict, errors: list)
    """
    errors = []

    try:
        # Load JSON
        with open(file_path) as f:
            data = json.load(f)

        if verbose:
            print(f"  Loaded JSON successfully ({len(json.dumps(data))} bytes)")

        # Validate with Pydantic
        dataset = TrainingDataset(**data)

        if verbose:
            print(f"  Schema validation passed")
            print(f"  Dataset version: {dataset.dataset_version}")
            print(f"  Total samples: {dataset.statistics.total_samples}")

        # Additional semantic validations
        semantic_errors = perform_semantic_validation(dataset, verbose)
        if semantic_errors:
            errors.extend(semantic_errors)

        return len(errors) == 0, data, errors

    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
        return False, {}, errors

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return False, {}, errors

    except ValidationError as e:
        errors.append(f"Schema validation failed:")
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            errors.append(f"  {loc}: {error['msg']}")
        return False, {}, errors

    except Exception as e:
        errors.append(f"Unexpected error: {type(e).__name__}: {e}")
        return False, {}, errors


def perform_semantic_validation(dataset: TrainingDataset, verbose: bool = False) -> List[str]:
    """Perform additional semantic validation beyond schema checks.

    Args:
        dataset: Validated TrainingDataset instance
        verbose: Whether to print verbose details

    Returns:
        List of error messages (empty if no errors)
    """
    errors = []

    # Check for balanced distribution
    if dataset.statistics:
        stats = dataset.statistics

        # Warn if any category has very few samples
        for category, count in stats.by_category.items():
            if count < 3:
                errors.append(
                    f"WARNING: Category '{category}' has only {count} samples. "
                    f"Recommend at least 5 per category."
                )

        # Warn if any persona is missing
        expected_personas = {"educator", "researcher", "creator", "builder"}
        missing_personas = expected_personas - set(stats.by_persona.keys())
        if missing_personas:
            errors.append(
                f"WARNING: Missing personas: {missing_personas}. "
                f"All four personas should be represented."
            )

    # Check quality score distribution
    quality_scores = [s.metadata.quality_score for s in dataset.samples]
    avg_quality = sum(quality_scores) / len(quality_scores)

    if avg_quality < 0.8:
        errors.append(
            f"WARNING: Average quality score is {avg_quality:.2f}. "
            f"Recommend targeting >= 0.85 for production datasets."
        )

    low_quality_samples = [
        s.sample_id for s in dataset.samples if s.metadata.quality_score < 0.7
    ]
    if low_quality_samples:
        errors.append(
            f"WARNING: {len(low_quality_samples)} samples have quality < 0.7: "
            f"{', '.join(low_quality_samples[:5])}"
            f"{'...' if len(low_quality_samples) > 5 else ''}"
        )

    if verbose:
        print(f"  Semantic validation: {len(errors)} warnings")

    return errors


def generate_report(
    results: Dict[Path, Tuple[bool, Dict, List[str]]],
    output_file: Path = None
) -> str:
    """Generate a comprehensive validation report.

    Args:
        results: Dictionary mapping file paths to validation results
        output_file: Optional file to write report to

    Returns:
        Report text
    """
    lines = []
    lines.append("=" * 80)
    lines.append("KWANZAA ADAPTER TRAINING DATASET VALIDATION REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")

    # Summary statistics
    total_files = len(results)
    successful = sum(1 for success, _, _ in results.values() if success)
    failed = total_files - successful

    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total files validated: {total_files}")
    lines.append(f"Successful: {successful}")
    lines.append(f"Failed: {failed}")
    lines.append("")

    # Aggregate statistics
    total_samples = 0
    all_categories = {}
    all_personas = {}
    all_difficulties = {}

    for file_path, (success, data, _) in results.items():
        if success and data:
            stats = data.get("statistics", {})
            total_samples += stats.get("total_samples", 0)

            for cat, count in stats.get("by_category", {}).items():
                all_categories[cat] = all_categories.get(cat, 0) + count

            for persona, count in stats.get("by_persona", {}).items():
                all_personas[persona] = all_personas.get(persona, 0) + count

            for diff, count in stats.get("by_difficulty", {}).items():
                all_difficulties[diff] = all_difficulties.get(diff, 0) + count

    if total_samples > 0:
        lines.append("AGGREGATE STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Total samples across all files: {total_samples}")
        lines.append("")

        lines.append("By Category:")
        for cat, count in sorted(all_categories.items()):
            pct = (count / total_samples) * 100
            lines.append(f"  {cat:20s}: {count:3d} ({pct:5.1f}%)")
        lines.append("")

        lines.append("By Persona:")
        for persona, count in sorted(all_personas.items()):
            pct = (count / total_samples) * 100
            lines.append(f"  {persona:20s}: {count:3d} ({pct:5.1f}%)")
        lines.append("")

        lines.append("By Difficulty:")
        for diff, count in sorted(all_difficulties.items()):
            pct = (count / total_samples) * 100
            lines.append(f"  {diff:20s}: {count:3d} ({pct:5.1f}%)")
        lines.append("")

    # Individual file results
    lines.append("FILE VALIDATION RESULTS")
    lines.append("-" * 80)

    for file_path, (success, data, errors) in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        lines.append(f"\n{status}: {file_path.name}")

        if data:
            lines.append(f"  Version: {data.get('dataset_version', 'unknown')}")
            stats = data.get("statistics", {})
            lines.append(f"  Samples: {stats.get('total_samples', 0)}")

        if errors:
            lines.append("  Errors:")
            for error in errors:
                lines.append(f"    - {error}")

    lines.append("")
    lines.append("=" * 80)

    report_text = "\n".join(lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(report_text)
        print(f"\nReport written to: {output_file}")

    return report_text


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate Kwanzaa adapter training datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/training/examples/citation-examples.json
  %(prog)s data/training/examples/*.json --report report.txt
  %(prog)s --verbose data/training/examples/refusal-examples.json
        """,
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Dataset JSON files to validate",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Output file for validation report",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose validation details",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    args = parser.parse_args()

    # Disable colors if requested or not in TTY
    if args.no_color or not sys.stdout.isatty():
        for attr in dir(Colors):
            if not attr.startswith("_"):
                setattr(Colors, attr, "")

    print(colorize("Kwanzaa Adapter Training Dataset Validator", Colors.HEADER + Colors.BOLD))
    print(colorize("=" * 60, Colors.HEADER))
    print()

    results = {}
    all_success = True

    for file_path in args.files:
        print(colorize(f"Validating: {file_path}", Colors.BOLD))

        success, data, errors = validate_dataset_file(file_path, args.verbose)
        results[file_path] = (success, data, errors)

        if success:
            if errors:  # Has warnings
                print(colorize("  ⚠ PASS (with warnings)", Colors.WARNING))
                for error in errors:
                    print(colorize(f"    {error}", Colors.WARNING))
            else:
                print(colorize("  ✓ PASS", Colors.OKGREEN))
        else:
            print(colorize("  ✗ FAIL", Colors.FAIL))
            for error in errors:
                print(colorize(f"    {error}", Colors.FAIL))
            all_success = False

        print()

    # Generate report
    if args.report or len(results) > 1:
        report = generate_report(results, args.report)
        if not args.report:
            print("\n" + report)

    # Exit with appropriate code
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
