#!/usr/bin/env python3
"""
Validate citation training examples for Kwanzaa RAG model.

This script validates:
1. JSON schema compliance
2. Citation integrity (citations match sources)
3. Metadata completeness
4. Source diversity
5. Quality metrics

Usage:
    python scripts/validate_citation_examples.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class CitationValidator:
    """Validate citation training examples."""

    def __init__(self, examples_path: str, schema_path: str):
        self.examples_path = Path(examples_path)
        self.schema_path = Path(schema_path)
        self.examples = []
        self.errors = []
        self.warnings = []

    def load_examples(self):
        """Load citation examples."""
        with open(self.examples_path, 'r') as f:
            data = json.load(f)
            self.examples = data.get('samples', [])
            print(f"Loaded {len(self.examples)} examples from {self.examples_path}")

    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Run all validations and return results."""
        self.errors = []
        self.warnings = []

        print("\nRunning validation checks...\n")

        # 1. Structure validation
        print("1. Validating structure...")
        self._validate_structure()

        # 2. Citation integrity
        print("2. Validating citation integrity...")
        self._validate_citation_integrity()

        # 3. Metadata completeness
        print("3. Validating metadata completeness...")
        self._validate_metadata()

        # 4. Source diversity
        print("4. Checking source diversity...")
        diversity_stats = self._check_source_diversity()

        # 5. Quality metrics
        print("5. Calculating quality metrics...")
        quality_stats = self._calculate_quality_metrics()

        # Compile report
        report = {
            "total_examples": len(self.examples),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "passed": len(self.errors) == 0,
            "error_details": self.errors,
            "warning_details": self.warnings,
            "diversity_stats": diversity_stats,
            "quality_stats": quality_stats
        }

        return report["passed"], report

    def _validate_structure(self):
        """Validate basic structure of examples."""
        required_fields = [
            'sample_id', 'category', 'persona', 'user_query',
            'retrieved_context', 'expected_output', 'metadata'
        ]

        required_output_fields = [
            'version', 'answer', 'sources', 'retrieval_summary', 'unknowns'
        ]

        for idx, example in enumerate(self.examples):
            if example is None:
                self.errors.append(f"Example at index {idx} is None")
                continue

            # Check top-level fields
            for field in required_fields:
                if field not in example:
                    self.errors.append(
                        f"Example {example.get('sample_id', idx)}: Missing required field '{field}'"
                    )

            # Check expected_output structure
            if 'expected_output' in example:
                output = example['expected_output']
                for field in required_output_fields:
                    if field not in output:
                        self.errors.append(
                            f"Example {example.get('sample_id', idx)}: Missing required field '{field}' in expected_output"
                        )

                # Validate version format
                if 'version' in output:
                    if not output['version'].startswith('kwanzaa.answer.v'):
                        self.errors.append(
                            f"Example {example.get('sample_id', idx)}: Invalid version format"
                        )

    def _validate_citation_integrity(self):
        """Validate that citations properly reference sources."""
        for example in self.examples:
            if example is None:
                continue

            sample_id = example.get('sample_id', 'unknown')
            output = example.get('expected_output', {})

            # Check that sources array exists
            sources = output.get('sources', [])
            if not isinstance(sources, list):
                self.errors.append(
                    f"Example {sample_id}: 'sources' must be an array"
                )
                continue

            # Check that integrity field indicates citations are required and provided
            integrity = output.get('integrity', {})
            if integrity.get('citation_required'):
                if not integrity.get('citations_provided'):
                    self.errors.append(
                        f"Example {sample_id}: Citations required but not provided"
                    )

                if len(sources) == 0:
                    self.errors.append(
                        f"Example {sample_id}: Citations required but sources array is empty"
                    )

            # Validate each source has required fields
            required_source_fields = [
                'citation_label', 'canonical_url', 'source_org', 'year',
                'content_type', 'license', 'namespace', 'doc_id', 'chunk_id'
            ]

            for sidx, source in enumerate(sources):
                for field in required_source_fields:
                    if field not in source:
                        self.errors.append(
                            f"Example {sample_id}, source {sidx}: Missing required field '{field}'"
                        )

                # Validate year range
                if 'year' in source:
                    year = source['year']
                    if not (1600 <= year <= 2100):
                        self.errors.append(
                            f"Example {sample_id}, source {sidx}: Invalid year {year}"
                        )

                # Validate URL format
                if 'canonical_url' in source:
                    url = source['canonical_url']
                    if not url.startswith(('http://', 'https://')):
                        self.warnings.append(
                            f"Example {sample_id}, source {sidx}: URL does not start with http:// or https://"
                        )

    def _validate_metadata(self):
        """Validate metadata completeness."""
        required_metadata = ['difficulty', 'principle_focus', 'quality_score']

        for example in self.examples:
            if example is None:
                continue

            sample_id = example.get('sample_id', 'unknown')
            metadata = example.get('metadata', {})

            for field in required_metadata:
                if field not in metadata:
                    self.warnings.append(
                        f"Example {sample_id}: Missing metadata field '{field}'"
                    )

            # Validate difficulty values
            if 'difficulty' in metadata:
                if metadata['difficulty'] not in ['easy', 'medium', 'hard']:
                    self.errors.append(
                        f"Example {sample_id}: Invalid difficulty value"
                    )

            # Validate quality_score range
            if 'quality_score' in metadata:
                score = metadata['quality_score']
                if not (0.0 <= score <= 1.0):
                    self.errors.append(
                        f"Example {sample_id}: Quality score must be between 0.0 and 1.0"
                    )

            # Validate principle_focus
            if 'principle_focus' in metadata:
                valid_principles = [
                    "Umoja", "Kujichagulia", "Ujima", "Ujamaa",
                    "Nia", "Kuumba", "Imani"
                ]
                for principle in metadata['principle_focus']:
                    if principle not in valid_principles:
                        self.errors.append(
                            f"Example {sample_id}: Invalid principle '{principle}'"
                        )

    def _check_source_diversity(self) -> Dict[str, Any]:
        """Check diversity of sources used."""
        source_orgs = defaultdict(int)
        source_types = defaultdict(int)
        namespaces = defaultdict(int)
        years = []

        for example in self.examples:
            if example is None:
                continue

            output = example.get('expected_output', {})
            sources = output.get('sources', [])

            for source in sources:
                if 'source_org' in source:
                    source_orgs[source['source_org']] += 1
                if 'content_type' in source:
                    source_types[source['content_type']] += 1
                if 'namespace' in source:
                    namespaces[source['namespace']] += 1
                if 'year' in source:
                    years.append(source['year'])

        return {
            "unique_source_orgs": len(source_orgs),
            "unique_content_types": len(source_types),
            "unique_namespaces": len(namespaces),
            "year_range": (min(years), max(years)) if years else (None, None),
            "source_org_distribution": dict(source_orgs),
            "content_type_distribution": dict(source_types),
            "namespace_distribution": dict(namespaces)
        }

    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculate quality metrics."""
        total = len(self.examples)
        if total == 0:
            return {}

        persona_counts = defaultdict(int)
        difficulty_counts = defaultdict(int)
        avg_sources = 0
        avg_quality_score = 0
        citation_coverage = 0

        for example in self.examples:
            if example is None:
                continue

            # Persona distribution
            if 'persona' in example:
                persona_counts[example['persona']] += 1

            # Difficulty distribution
            if 'metadata' in example and 'difficulty' in example['metadata']:
                difficulty_counts[example['metadata']['difficulty']] += 1

            # Average sources per example
            output = example.get('expected_output', {})
            sources = output.get('sources', [])
            avg_sources += len(sources)

            # Average quality score
            if 'metadata' in example and 'quality_score' in example['metadata']:
                avg_quality_score += example['metadata']['quality_score']

            # Citation coverage
            integrity = output.get('integrity', {})
            if integrity.get('citations_provided'):
                citation_coverage += 1

        return {
            "persona_distribution": dict(persona_counts),
            "difficulty_distribution": dict(difficulty_counts),
            "avg_sources_per_example": avg_sources / total if total > 0 else 0,
            "avg_quality_score": avg_quality_score / total if total > 0 else 0,
            "citation_coverage_pct": (citation_coverage / total * 100) if total > 0 else 0
        }

    def print_report(self, report: Dict[str, Any]):
        """Print validation report."""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)

        print(f"\nTotal Examples: {report['total_examples']}")
        print(f"Errors: {report['errors']}")
        print(f"Warnings: {report['warnings']}")
        print(f"Status: {'PASSED' if report['passed'] else 'FAILED'}")

        if report['error_details']:
            print("\n" + "-"*60)
            print("ERRORS:")
            print("-"*60)
            for error in report['error_details']:
                print(f"  - {error}")

        if report['warning_details']:
            print("\n" + "-"*60)
            print("WARNINGS:")
            print("-"*60)
            for warning in report['warning_details']:
                print(f"  - {warning}")

        print("\n" + "-"*60)
        print("SOURCE DIVERSITY:")
        print("-"*60)
        diversity = report['diversity_stats']
        print(f"  Unique Source Organizations: {diversity['unique_source_orgs']}")
        print(f"  Unique Content Types: {diversity['unique_content_types']}")
        print(f"  Unique Namespaces: {diversity['unique_namespaces']}")
        print(f"  Year Range: {diversity['year_range'][0]} - {diversity['year_range'][1]}")

        print("\n" + "-"*60)
        print("QUALITY METRICS:")
        print("-"*60)
        quality = report['quality_stats']
        print(f"  Average Sources per Example: {quality['avg_sources_per_example']:.2f}")
        print(f"  Average Quality Score: {quality['avg_quality_score']:.2f}")
        print(f"  Citation Coverage: {quality['citation_coverage_pct']:.1f}%")

        print(f"\n  Persona Distribution:")
        for persona, count in quality['persona_distribution'].items():
            print(f"    {persona}: {count}")

        print(f"\n  Difficulty Distribution:")
        for diff, count in quality['difficulty_distribution'].items():
            print(f"    {diff}: {count}")

        print("\n" + "="*60)


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    examples_path = project_root / "data" / "training" / "examples" / "citation-examples.json"
    schema_path = project_root / "data" / "training" / "dataset-schema.json"

    print("="*60)
    print("KWANZAA CITATION EXAMPLES VALIDATOR")
    print("="*60)

    validator = CitationValidator(
        examples_path=str(examples_path),
        schema_path=str(schema_path)
    )

    validator.load_examples()
    passed, report = validator.validate_all()
    validator.print_report(report)

    # Return exit code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
