#!/usr/bin/env python3
"""
Validate Kwanzaa adapter training dataset.

This script validates training samples against the JSON schema and checks
quality criteria, distribution targets, and data integrity.

Usage:
    python scripts/validate_training_data.py \
        --schema data/training/dataset-schema.json \
        --examples data/training/examples/ \
        --output data/training/validation/

Requirements:
    pip install jsonschema pydantic
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

try:
    from jsonschema import validate, ValidationError as SchemaValidationError
except ImportError:
    print("Error: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


class DatasetValidator:
    """Validates training dataset samples."""

    def __init__(self, schema_path: str, examples_path: str):
        self.schema = self._load_schema(schema_path)
        self.samples = self._load_samples(examples_path)
        self.errors = []
        self.warnings = []
        self.stats = {}

    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load JSON schema."""
        with open(schema_path) as f:
            return json.load(f)

    def _load_samples(self, examples_path: str) -> List[Dict[str, Any]]:
        """Load all training samples from example files."""
        samples = []
        examples_dir = Path(examples_path)

        if examples_dir.is_file():
            # Single file
            with open(examples_dir) as f:
                data = json.load(f)
                samples.extend(data.get('samples', []))
        else:
            # Directory of files
            for file_path in examples_dir.glob("*.json"):
                with open(file_path) as f:
                    data = json.load(f)
                    samples.extend(data.get('samples', []))

        return samples

    def validate_schema(self) -> bool:
        """Validate all samples against JSON schema."""
        print("🔍 Validating schema compliance...")
        schema_valid = True
        sample_schema = self.schema['definitions']['training_sample']

        for idx, sample in enumerate(self.samples):
            try:
                validate(instance=sample, schema=sample_schema)
            except SchemaValidationError as e:
                schema_valid = False
                sample_id = sample.get('sample_id', f'sample_{idx}')
                self.errors.append(f"Schema error in {sample_id}: {e.message}")

        if schema_valid:
            print(f"  ✅ All {len(self.samples)} samples pass schema validation")
        else:
            print(f"  ❌ Found {len(self.errors)} schema validation errors")

        return schema_valid

    def analyze_distribution(self) -> Dict[str, Any]:
        """Analyze dataset distribution."""
        print("\n📊 Analyzing distribution...")

        categories = Counter(s['category'] for s in self.samples)
        personas = Counter(s['persona'] for s in self.samples)
        difficulties = Counter(s['metadata']['difficulty'] for s in self.samples)

        total = len(self.samples)

        # Calculate percentages
        category_pct = {k: (v / total * 100) for k, v in categories.items()}
        persona_pct = {k: (v / total * 100) for k, v in personas.items()}
        difficulty_pct = {k: (v / total * 100) for k, v in difficulties.items()}

        self.stats['distribution'] = {
            'total_samples': total,
            'by_category': dict(categories),
            'by_persona': dict(personas),
            'by_difficulty': dict(difficulties),
            'category_percentages': category_pct,
            'persona_percentages': persona_pct,
            'difficulty_percentages': difficulty_pct,
        }

        # Print distribution
        print(f"\n  Total samples: {total}")
        print(f"\n  Categories:")
        for cat, count in categories.items():
            pct = category_pct[cat]
            print(f"    {cat:20} {count:3d} ({pct:5.1f}%)")

        print(f"\n  Personas:")
        for persona, count in personas.items():
            pct = persona_pct[persona]
            print(f"    {persona:20} {count:3d} ({pct:5.1f}%)")

        print(f"\n  Difficulty:")
        for diff, count in difficulties.items():
            pct = difficulty_pct[diff]
            print(f"    {diff:20} {count:3d} ({pct:5.1f}%)")

        return self.stats['distribution']

    def check_distribution_targets(self) -> bool:
        """Check if distribution meets target percentages."""
        print("\n🎯 Checking distribution targets...")

        targets_met = True

        # Category targets (for 160 sample dataset)
        category_targets = {
            'citation': (30, 40),  # 30-40%
            'refusal': (20, 30),
            'grounded_answer': (25, 35),
            'format_compliance': (5, 15),
        }

        # Persona targets
        persona_targets = {
            'educator': (30, 40),
            'researcher': (20, 30),
            'creator': (20, 30),
            'builder': (10, 20),
        }

        dist = self.stats.get('distribution', {})
        cat_pct = dist.get('category_percentages', {})
        pers_pct = dist.get('persona_percentages', {})

        # Check categories
        print("\n  Category targets:")
        for cat, (min_pct, max_pct) in category_targets.items():
            actual = cat_pct.get(cat, 0)
            status = "✅" if min_pct <= actual <= max_pct else "⚠️"
            print(f"    {status} {cat:20} {actual:5.1f}% (target: {min_pct}-{max_pct}%)")
            if not (min_pct <= actual <= max_pct):
                self.warnings.append(
                    f"{cat} at {actual:.1f}% (target: {min_pct}-{max_pct}%)"
                )
                if len(self.samples) >= 120:  # Only fail if dataset is large enough
                    targets_met = False

        # Check personas
        print("\n  Persona targets:")
        for persona, (min_pct, max_pct) in persona_targets.items():
            actual = pers_pct.get(persona, 0)
            status = "✅" if min_pct <= actual <= max_pct else "⚠️"
            print(f"    {status} {persona:20} {actual:5.1f}% (target: {min_pct}-{max_pct}%)")
            if not (min_pct <= actual <= max_pct):
                self.warnings.append(
                    f"{persona} at {actual:.1f}% (target: {min_pct}-{max_pct}%)"
                )
                if len(self.samples) >= 120:
                    targets_met = False

        return targets_met

    def analyze_quality(self) -> Dict[str, Any]:
        """Analyze quality metrics."""
        print("\n⭐ Analyzing quality metrics...")

        quality_scores = [s['metadata']['quality_score'] for s in self.samples]
        avg_quality = sum(quality_scores) / len(quality_scores)
        min_quality = min(quality_scores)
        max_quality = max(quality_scores)
        below_threshold = sum(1 for q in quality_scores if q < 0.85)

        self.stats['quality'] = {
            'average_score': avg_quality,
            'min_score': min_quality,
            'max_score': max_quality,
            'below_threshold_count': below_threshold,
            'threshold': 0.85,
        }

        print(f"  Average quality score: {avg_quality:.3f}")
        print(f"  Min quality score:     {min_quality:.3f}")
        print(f"  Max quality score:     {max_quality:.3f}")
        print(f"  Samples below 0.85:    {below_threshold}")

        if avg_quality < 0.90:
            self.warnings.append(
                f"Average quality ({avg_quality:.3f}) below target (0.90)"
            )

        if below_threshold > 0:
            self.errors.append(
                f"{below_threshold} samples have quality score below 0.85"
            )

        return self.stats['quality']

    def check_duplicates(self) -> bool:
        """Check for duplicate sample IDs."""
        print("\n🔍 Checking for duplicates...")

        sample_ids = [s['sample_id'] for s in self.samples]
        id_counts = Counter(sample_ids)
        duplicates = [sid for sid, count in id_counts.items() if count > 1]

        if duplicates:
            print(f"  ❌ Found {len(duplicates)} duplicate sample IDs:")
            for dup_id in duplicates[:10]:
                count = id_counts[dup_id]
                print(f"    - {dup_id} (appears {count} times)")
                self.errors.append(f"Duplicate sample_id: {dup_id}")
            return False
        else:
            print(f"  ✅ All {len(sample_ids)} sample IDs are unique")
            return True

    def check_principle_coverage(self) -> Dict[str, int]:
        """Check coverage of Nguzo Saba principles."""
        print("\n🕯️  Checking principle coverage...")

        all_principles = set()
        principle_counts = Counter()

        for sample in self.samples:
            principles = sample['metadata'].get('principle_focus', [])
            all_principles.update(principles)
            principle_counts.update(principles)

        expected_principles = {
            'Umoja', 'Kujichagulia', 'Ujima', 'Ujamaa',
            'Nia', 'Kuumba', 'Imani'
        }

        print(f"  Principle coverage:")
        for principle in expected_principles:
            count = principle_counts.get(principle, 0)
            pct = (count / len(self.samples) * 100) if self.samples else 0
            status = "✅" if count > 0 else "⚠️"
            print(f"    {status} {principle:15} {count:3d} samples ({pct:5.1f}%)")

        # Imani should be in 100% (or close)
        imani_pct = (principle_counts.get('Imani', 0) / len(self.samples) * 100)
        if imani_pct < 90:
            self.warnings.append(
                f"Imani (Faith) only in {imani_pct:.1f}% of samples (target: 100%)"
            )

        self.stats['principles'] = dict(principle_counts)
        return self.stats['principles']

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        return {
            'valid': len(self.errors) == 0,
            'total_samples': len(self.samples),
            'errors': self.errors,
            'warnings': self.warnings,
            'statistics': self.stats,
        }

    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        print("=" * 60)
        print("Kwanzaa Training Dataset Validation")
        print("=" * 60)

        # 1. Schema validation
        schema_valid = self.validate_schema()

        # 2. Distribution analysis
        self.analyze_distribution()

        # 3. Distribution targets
        targets_met = self.check_distribution_targets()

        # 4. Quality analysis
        self.analyze_quality()

        # 5. Duplicate check
        no_duplicates = self.check_duplicates()

        # 6. Principle coverage
        self.check_principle_coverage()

        # Final verdict
        print("\n" + "=" * 60)
        all_valid = (
            schema_valid
            and no_duplicates
            and len(self.errors) == 0
        )

        if all_valid:
            print("✅ DATASET VALIDATION PASSED")
            if self.warnings:
                print(f"\n⚠️  {len(self.warnings)} warnings (non-blocking):")
                for warning in self.warnings[:5]:
                    print(f"  - {warning}")
        else:
            print("❌ DATASET VALIDATION FAILED")
            print(f"\nErrors found: {len(self.errors)}")
            for error in self.errors[:10]:
                print(f"  - {error}")

        print("=" * 60)

        return all_valid


def main():
    parser = argparse.ArgumentParser(
        description='Validate Kwanzaa training dataset'
    )
    parser.add_argument(
        '--schema',
        required=True,
        help='Path to dataset-schema.json'
    )
    parser.add_argument(
        '--examples',
        required=True,
        help='Path to examples directory or file'
    )
    parser.add_argument(
        '--output',
        help='Output directory for validation report (optional)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with error code if validation fails'
    )

    args = parser.parse_args()

    # Run validation
    validator = DatasetValidator(args.schema, args.examples)
    success = validator.run_all_checks()

    # Save report if output specified
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / 'validation-report.json'

        report = validator.generate_report()
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Validation report saved to: {report_path}")

    # Exit with appropriate code
    if args.strict and not success:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
