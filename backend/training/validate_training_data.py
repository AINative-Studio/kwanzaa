#!/usr/bin/env python3
"""
Kwanzaa Training Data Validation Script

Comprehensive validation for training dataset quality, consistency, and correctness.
Validates all examples from E3B-US1 through E3B-US4 against quality standards.

Validation Checks:
1. JSON validity
2. Schema compliance
3. Duplication detection
4. Label consistency
5. Answer quality
6. Citation accuracy
7. Refusal appropriateness
8. Format compliance

Quality Metrics:
- 0 invalid samples required
- No duplicates
- Consistent tone and style
- Factual accuracy
- Cultural sensitivity

Author: Kwanzaa Development Team
Date: 2026-01-16
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter, defaultdict

# Optional: jsonschema for enhanced validation
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("WARNING: jsonschema not installed. Schema validation will be basic.")


@dataclass
class ValidationIssue:
    """Represents a validation issue found in the dataset"""
    severity: str  # "error", "warning", "info"
    category: str  # Which validation check found this
    sample_id: str
    file_path: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Complete validation report with statistics and issues"""
    total_samples: int = 0
    valid_samples: int = 0
    invalid_samples: int = 0
    warnings: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    validation_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_issue(self, issue: ValidationIssue):
        """Add an issue to the report"""
        self.issues.append(issue)
        if issue.severity == "error":
            self.invalid_samples += 1
        elif issue.severity == "warning":
            self.warnings += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for JSON serialization"""
        return {
            "validation_timestamp": self.validation_timestamp,
            "summary": {
                "total_samples": self.total_samples,
                "valid_samples": self.valid_samples,
                "invalid_samples": self.invalid_samples,
                "warnings": self.warnings,
                "pass_rate": f"{(self.valid_samples / self.total_samples * 100):.2f}%" if self.total_samples > 0 else "0%"
            },
            "statistics": self.statistics,
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "sample_id": issue.sample_id,
                    "file_path": issue.file_path,
                    "message": issue.message,
                    "details": issue.details
                }
                for issue in self.issues
            ]
        }


class TrainingDataValidator:
    """Comprehensive validator for Kwanzaa training data"""

    def __init__(self, schema_path: Path, training_data_dir: Path):
        self.schema_path = schema_path
        self.training_data_dir = training_data_dir
        self.schema = self._load_schema()
        self.report = ValidationReport()

        # Track for duplication detection
        self.seen_sample_ids: Set[str] = set()
        self.seen_queries: Dict[str, List[str]] = defaultdict(list)
        self.content_hashes: Dict[str, List[str]] = defaultdict(list)

        # Expected values for consistency checking
        self.valid_categories = {"citation", "refusal", "grounded_answer", "format_compliance"}
        self.valid_personas = {"educator", "researcher", "creator", "builder"}
        self.valid_principles = {"Umoja", "Kujichagulia", "Ujima", "Ujamaa", "Nia", "Kuumba", "Imani"}
        self.valid_difficulties = {"easy", "medium", "hard"}
        self.valid_tones = {"neutral", "educational", "conversational", "formal", "creative"}
        self.valid_completeness = {"complete", "partial", "insufficient_data"}

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema for validation"""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_all(self) -> ValidationReport:
        """Run all validation checks on all training examples"""
        print("Starting comprehensive validation...")
        print(f"Schema: {self.schema_path}")
        print(f"Training data directory: {self.training_data_dir}")
        print("-" * 80)

        # Find all JSON files in the examples directory
        example_files = list(self.training_data_dir.glob("examples/*.json"))

        if not example_files:
            print(f"ERROR: No example files found in {self.training_data_dir / 'examples'}")
            return self.report

        print(f"Found {len(example_files)} example files to validate\n")

        # Validate each file
        for file_path in example_files:
            print(f"Validating: {file_path.name}")
            self._validate_file(file_path)

        # Calculate final statistics
        self._calculate_statistics()

        print("\n" + "=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        self._print_summary()

        return self.report

    def _validate_file(self, file_path: Path):
        """Validate a single training data file"""
        try:
            # Check 1: JSON Validity
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="json_validity",
                sample_id="N/A",
                file_path=str(file_path),
                message=f"Invalid JSON: {str(e)}",
                details={"line": e.lineno, "column": e.colno}
            ))
            return
        except Exception as e:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="json_validity",
                sample_id="N/A",
                file_path=str(file_path),
                message=f"Failed to read file: {str(e)}"
            ))
            return

        # Check 2: Schema Compliance
        self._validate_schema_compliance(data, file_path)

        # Validate each sample in the file
        samples = data.get("samples", [])
        for sample in samples:
            self.report.total_samples += 1
            sample_id = sample.get("sample_id", "unknown")

            # Check 3: Duplication Detection
            self._check_duplications(sample, file_path)

            # Check 4: Label Consistency
            self._check_label_consistency(sample, file_path)

            # Check 5: Answer Quality
            self._check_answer_quality(sample, file_path)

            # Check 6: Citation Accuracy
            self._check_citation_accuracy(sample, file_path)

            # Check 7: Refusal Appropriateness
            self._check_refusal_appropriateness(sample, file_path)

            # Check 8: Format Compliance
            self._check_format_compliance(sample, file_path)

    def _validate_schema_compliance(self, data: Dict[str, Any], file_path: Path):
        """Validate data against JSON schema"""
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="schema_compliance",
                sample_id=data.get("samples", [{}])[0].get("sample_id", "unknown") if data.get("samples") else "N/A",
                file_path=str(file_path),
                message=f"Schema validation failed: {e.message}",
                details={"path": list(e.path), "schema_path": list(e.schema_path)}
            ))
        except jsonschema.SchemaError as e:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="schema_compliance",
                sample_id="N/A",
                file_path=str(file_path),
                message=f"Invalid schema: {str(e)}"
            ))

    def _check_duplications(self, sample: Dict[str, Any], file_path: Path):
        """Check for duplicate sample IDs, queries, and content"""
        sample_id = sample.get("sample_id", "")

        # Check duplicate sample IDs
        if sample_id in self.seen_sample_ids:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="duplication",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Duplicate sample_id: {sample_id}"
            ))
        else:
            self.seen_sample_ids.add(sample_id)

        # Check duplicate queries
        query = sample.get("user_query", "").strip().lower()
        if query:
            if query in self.seen_queries:
                self.report.add_issue(ValidationIssue(
                    severity="warning",
                    category="duplication",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Duplicate or very similar user_query",
                    details={"query": sample.get("user_query"), "also_in": self.seen_queries[query]}
                ))
            self.seen_queries[query].append(sample_id)

        # Check duplicate content (using hash of expected output)
        expected_output = sample.get("expected_output", {})
        answer_text = expected_output.get("answer", {}).get("text", "")
        if answer_text:
            content_hash = hashlib.sha256(answer_text.encode()).hexdigest()[:16]
            if content_hash in self.content_hashes:
                self.report.add_issue(ValidationIssue(
                    severity="warning",
                    category="duplication",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message="Duplicate or very similar answer text",
                    details={"also_in": self.content_hashes[content_hash]}
                ))
            self.content_hashes[content_hash].append(sample_id)

    def _check_label_consistency(self, sample: Dict[str, Any], file_path: Path):
        """Verify label consistency across the sample"""
        sample_id = sample.get("sample_id", "unknown")

        # Check category
        category = sample.get("category")
        if category not in self.valid_categories:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="label_consistency",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Invalid category: {category}",
                details={"valid_categories": list(self.valid_categories)}
            ))

        # Check persona consistency
        sample_persona = sample.get("persona")
        expected_persona = sample.get("expected_output", {}).get("persona")

        if sample_persona != expected_persona:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="label_consistency",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Persona mismatch: sample={sample_persona}, expected_output={expected_persona}"
            ))

        # Check difficulty
        difficulty = sample.get("metadata", {}).get("difficulty")
        if difficulty not in self.valid_difficulties:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="label_consistency",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Invalid difficulty: {difficulty}",
                details={"valid_difficulties": list(self.valid_difficulties)}
            ))

        # Check principles
        principles = sample.get("metadata", {}).get("principle_focus", [])
        invalid_principles = [p for p in principles if p not in self.valid_principles]
        if invalid_principles:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="label_consistency",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Invalid principles: {invalid_principles}",
                details={"valid_principles": list(self.valid_principles)}
            ))

        # Check tone
        tone = sample.get("expected_output", {}).get("answer", {}).get("tone")
        if tone and tone not in self.valid_tones:
            self.report.add_issue(ValidationIssue(
                severity="warning",
                category="label_consistency",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Unexpected tone: {tone}",
                details={"valid_tones": list(self.valid_tones)}
            ))

        # Check completeness
        completeness = sample.get("expected_output", {}).get("answer", {}).get("completeness")
        if completeness and completeness not in self.valid_completeness:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="label_consistency",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Invalid completeness: {completeness}",
                details={"valid_completeness": list(self.valid_completeness)}
            ))

    def _check_answer_quality(self, sample: Dict[str, Any], file_path: Path):
        """Validate answer quality and content"""
        sample_id = sample.get("sample_id", "unknown")
        expected_output = sample.get("expected_output", {})
        answer = expected_output.get("answer", {})
        answer_text = answer.get("text", "")

        # Check minimum answer length
        if len(answer_text.strip()) < 50:
            self.report.add_issue(ValidationIssue(
                severity="warning",
                category="answer_quality",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Answer text is very short ({len(answer_text)} chars)",
                details={"answer_length": len(answer_text)}
            ))

        # Check for placeholder text
        placeholders = ["TODO", "FIXME", "XXX", "[placeholder]", "lorem ipsum"]
        for placeholder in placeholders:
            if placeholder.lower() in answer_text.lower():
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="answer_quality",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Answer contains placeholder text: {placeholder}"
                ))

        # Check confidence score
        confidence = answer.get("confidence")
        if confidence is not None:
            if not (0 <= confidence <= 1):
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="answer_quality",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Invalid confidence score: {confidence} (must be 0-1)"
                ))

        # Check quality score
        quality_score = sample.get("metadata", {}).get("quality_score")
        if quality_score is not None:
            if not (0 <= quality_score <= 1):
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="answer_quality",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Invalid quality_score: {quality_score} (must be 0-1)"
                ))
            elif quality_score < 0.8:
                self.report.add_issue(ValidationIssue(
                    severity="warning",
                    category="answer_quality",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Low quality_score: {quality_score} (target >= 0.8)"
                ))

        # Check for culturally insensitive language (basic check)
        sensitive_patterns = [
            r'\brace\b(?! discrimination)',  # "race" without context
            r'\bexotic\b',
            r'\bprimitive\b',
            r'\btribe\b(?! history)',
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, answer_text, re.IGNORECASE):
                self.report.add_issue(ValidationIssue(
                    severity="warning",
                    category="answer_quality",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Potentially insensitive language detected (pattern: {pattern})",
                    details={"recommendation": "Review for cultural sensitivity"}
                ))

    def _check_citation_accuracy(self, sample: Dict[str, Any], file_path: Path):
        """Validate citation accuracy and consistency"""
        sample_id = sample.get("sample_id", "unknown")
        category = sample.get("category")
        expected_output = sample.get("expected_output", {})
        answer_text = expected_output.get("answer", {}).get("text", "")
        sources = expected_output.get("sources", [])
        retrieved_context = sample.get("retrieved_context", [])

        # Find citation markers in text [1], [2], etc.
        citation_markers = set(re.findall(r'\[(\d+)\]', answer_text))

        # For citation and grounded_answer categories, check citation usage
        if category in ["citation", "grounded_answer"]:
            if retrieved_context and not citation_markers:
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="citation_accuracy",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message="Retrieved context exists but no citations used in answer"
                ))

            # Check that all citation markers have corresponding sources
            num_sources = len(sources)
            for marker in citation_markers:
                marker_num = int(marker)
                if marker_num > num_sources:
                    self.report.add_issue(ValidationIssue(
                        severity="error",
                        category="citation_accuracy",
                        sample_id=sample_id,
                        file_path=str(file_path),
                        message=f"Citation [{marker}] used but only {num_sources} sources provided"
                    ))

            # Check that sources list matches retrieved context
            if len(sources) != len(retrieved_context):
                self.report.add_issue(ValidationIssue(
                    severity="warning",
                    category="citation_accuracy",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Mismatch: {len(sources)} sources but {len(retrieved_context)} retrieved contexts"
                ))

        # Validate source structure
        for idx, source in enumerate(sources, 1):
            required_fields = ["citation_label", "canonical_url", "doc_id", "chunk_id"]
            missing_fields = [f for f in required_fields if f not in source]
            if missing_fields:
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="citation_accuracy",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Source [{idx}] missing required fields: {missing_fields}"
                ))

            # Validate URL format
            url = source.get("canonical_url", "")
            if url and not (url.startswith("http://") or url.startswith("https://")):
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="citation_accuracy",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Source [{idx}] has invalid URL format: {url}"
                ))

        # Check integrity section
        integrity = expected_output.get("integrity", {})
        if category in ["citation", "grounded_answer"]:
            citation_required = integrity.get("citation_required")
            citations_provided = integrity.get("citations_provided")

            if citation_required and not citations_provided:
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="citation_accuracy",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message="integrity.citation_required=true but citations_provided=false"
                ))

    def _check_refusal_appropriateness(self, sample: Dict[str, Any], file_path: Path):
        """Validate refusal behavior is appropriate"""
        sample_id = sample.get("sample_id", "unknown")
        category = sample.get("category")
        expected_output = sample.get("expected_output", {})
        answer_text = expected_output.get("answer", {}).get("text", "")
        retrieved_context = sample.get("retrieved_context", [])
        integrity = expected_output.get("integrity", {})
        unknowns = expected_output.get("unknowns", {})

        # Check refusal category samples
        if category == "refusal":
            # Should have insufficient_data completeness
            completeness = expected_output.get("answer", {}).get("completeness")
            if completeness != "insufficient_data":
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="refusal_appropriateness",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Refusal sample should have completeness='insufficient_data', got '{completeness}'"
                ))

            # Should have fallback_behavior indicating refusal
            fallback = integrity.get("fallback_behavior")
            if fallback not in ["refusal", "clarification_requested"]:
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="refusal_appropriateness",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"Refusal sample should have appropriate fallback_behavior, got '{fallback}'"
                ))

            # Should explain what's missing
            refusal_keywords = ["cannot", "don't have", "not available", "unable to", "insufficient"]
            has_refusal_language = any(keyword in answer_text.lower() for keyword in refusal_keywords)

            if not has_refusal_language:
                self.report.add_issue(ValidationIssue(
                    severity="warning",
                    category="refusal_appropriateness",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message="Refusal answer should clearly indicate inability to answer"
                ))

            # Should populate unknowns sections
            if not unknowns.get("missing_context") and not unknowns.get("out_of_scope"):
                self.report.add_issue(ValidationIssue(
                    severity="warning",
                    category="refusal_appropriateness",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message="Refusal sample should explain what's missing in unknowns"
                ))

            # Should offer alternatives or clarifying questions
            if not unknowns.get("clarifying_questions"):
                self.report.add_issue(ValidationIssue(
                    severity="info",
                    category="refusal_appropriateness",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message="Refusal sample could benefit from clarifying_questions"
                ))

        # Check non-refusal samples with good context don't refuse
        elif category in ["citation", "grounded_answer"] and retrieved_context:
            high_score_context = any(ctx.get("score", 0) > 0.8 for ctx in retrieved_context)

            if high_score_context:
                refusal_keywords = ["cannot answer", "don't have information", "not available in my corpus"]
                has_inappropriate_refusal = any(keyword in answer_text.lower() for keyword in refusal_keywords)

                if has_inappropriate_refusal:
                    self.report.add_issue(ValidationIssue(
                        severity="warning",
                        category="refusal_appropriateness",
                        sample_id=sample_id,
                        file_path=str(file_path),
                        message="Sample has high-quality context but appears to refuse answering"
                    ))

    def _check_format_compliance(self, sample: Dict[str, Any], file_path: Path):
        """Validate answer_json contract format compliance"""
        sample_id = sample.get("sample_id", "unknown")
        expected_output = sample.get("expected_output", {})

        # Check required top-level fields
        required_fields = ["version", "answer", "sources", "retrieval_summary", "unknowns"]
        missing_fields = [f for f in required_fields if f not in expected_output]

        if missing_fields:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="format_compliance",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Missing required expected_output fields: {missing_fields}"
            ))

        # Check version format
        version = expected_output.get("version", "")
        if not re.match(r'^kwanzaa\.answer\.v\d+$', version):
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="format_compliance",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"Invalid version format: {version} (expected 'kwanzaa.answer.v1')"
            ))

        # Check answer structure
        answer = expected_output.get("answer", {})
        if "text" not in answer:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="format_compliance",
                sample_id=sample_id,
                file_path=str(file_path),
                message="answer.text is required"
            ))

        # Check sources is array
        sources = expected_output.get("sources")
        if sources is not None and not isinstance(sources, list):
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="format_compliance",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"sources must be an array, got {type(sources)}"
            ))

        # Check retrieval_summary structure
        retrieval_summary = expected_output.get("retrieval_summary", {})
        required_retrieval_fields = ["query", "top_k", "namespaces", "results"]
        missing_retrieval = [f for f in required_retrieval_fields if f not in retrieval_summary]

        if missing_retrieval:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="format_compliance",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"retrieval_summary missing fields: {missing_retrieval}"
            ))

        # Check unknowns structure
        unknowns = expected_output.get("unknowns", {})
        required_unknowns_fields = ["unsupported_claims", "missing_context", "clarifying_questions"]
        missing_unknowns = [f for f in required_unknowns_fields if f not in unknowns]

        if missing_unknowns:
            self.report.add_issue(ValidationIssue(
                severity="error",
                category="format_compliance",
                sample_id=sample_id,
                file_path=str(file_path),
                message=f"unknowns missing fields: {missing_unknowns}"
            ))

        # Check all unknowns fields are arrays
        for field in required_unknowns_fields:
            value = unknowns.get(field)
            if value is not None and not isinstance(value, list):
                self.report.add_issue(ValidationIssue(
                    severity="error",
                    category="format_compliance",
                    sample_id=sample_id,
                    file_path=str(file_path),
                    message=f"unknowns.{field} must be an array, got {type(value)}"
                ))

    def _calculate_statistics(self):
        """Calculate comprehensive dataset statistics"""
        # Collect all samples for statistics
        all_samples = []
        for file_path in self.training_data_dir.glob("examples/*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_samples.extend(data.get("samples", []))
            except Exception:
                continue

        # Calculate valid samples (total - invalid)
        self.report.valid_samples = self.report.total_samples - len([
            issue for issue in self.report.issues if issue.severity == "error"
        ])

        # Category distribution
        categories = Counter(s.get("category") for s in all_samples)

        # Persona distribution
        personas = Counter(s.get("persona") for s in all_samples)

        # Difficulty distribution
        difficulties = Counter(s.get("metadata", {}).get("difficulty") for s in all_samples)

        # Principle coverage
        all_principles = []
        for s in all_samples:
            all_principles.extend(s.get("metadata", {}).get("principle_focus", []))
        principle_counts = Counter(all_principles)

        # Quality scores
        quality_scores = [
            s.get("metadata", {}).get("quality_score")
            for s in all_samples
            if s.get("metadata", {}).get("quality_score") is not None
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        # Edge cases
        edge_cases = sum(1 for s in all_samples if s.get("metadata", {}).get("edge_case", False))

        # Issue distribution
        issues_by_category = Counter(issue.category for issue in self.report.issues)
        issues_by_severity = Counter(issue.severity for issue in self.report.issues)

        self.report.statistics = {
            "by_category": dict(categories),
            "by_persona": dict(personas),
            "by_difficulty": dict(difficulties),
            "principle_coverage": dict(principle_counts),
            "quality_metrics": {
                "average_quality_score": round(avg_quality, 3),
                "min_quality_score": round(min(quality_scores), 3) if quality_scores else 0,
                "max_quality_score": round(max(quality_scores), 3) if quality_scores else 0,
                "edge_cases": edge_cases
            },
            "issues_by_category": dict(issues_by_category),
            "issues_by_severity": dict(issues_by_severity)
        }

    def _print_summary(self):
        """Print validation summary to console"""
        summary = self.report.to_dict()["summary"]
        stats = self.report.statistics

        print(f"\nTotal Samples: {summary['total_samples']}")
        print(f"Valid Samples: {summary['valid_samples']}")
        print(f"Invalid Samples: {summary['invalid_samples']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Pass Rate: {summary['pass_rate']}")

        print("\n" + "-" * 80)
        print("STATISTICS")
        print("-" * 80)

        print("\nBy Category:")
        for cat, count in stats.get("by_category", {}).items():
            print(f"  {cat}: {count}")

        print("\nBy Persona:")
        for persona, count in stats.get("by_persona", {}).items():
            print(f"  {persona}: {count}")

        print("\nBy Difficulty:")
        for diff, count in stats.get("by_difficulty", {}).items():
            print(f"  {diff}: {count}")

        print("\nPrinciple Coverage:")
        for principle, count in stats.get("principle_coverage", {}).items():
            print(f"  {principle}: {count}")

        quality = stats.get("quality_metrics", {})
        print(f"\nQuality Metrics:")
        print(f"  Average Quality Score: {quality.get('average_quality_score')}")
        print(f"  Min Quality Score: {quality.get('min_quality_score')}")
        print(f"  Max Quality Score: {quality.get('max_quality_score')}")
        print(f"  Edge Cases: {quality.get('edge_cases')}")

        if stats.get("issues_by_category"):
            print("\nIssues by Category:")
            for cat, count in stats.get("issues_by_category", {}).items():
                print(f"  {cat}: {count}")

        if stats.get("issues_by_severity"):
            print("\nIssues by Severity:")
            for severity, count in stats.get("issues_by_severity", {}).items():
                print(f"  {severity}: {count}")

        # Print detailed issues if any
        if self.report.issues:
            print("\n" + "=" * 80)
            print("DETAILED ISSUES")
            print("=" * 80)

            # Group by severity
            errors = [i for i in self.report.issues if i.severity == "error"]
            warnings = [i for i in self.report.issues if i.severity == "warning"]
            infos = [i for i in self.report.issues if i.severity == "info"]

            if errors:
                print(f"\nERRORS ({len(errors)}):")
                for issue in errors[:20]:  # Limit to first 20
                    print(f"\n  [{issue.sample_id}] {issue.category}")
                    print(f"  File: {issue.file_path}")
                    print(f"  Message: {issue.message}")
                    if issue.details:
                        print(f"  Details: {issue.details}")

                if len(errors) > 20:
                    print(f"\n  ... and {len(errors) - 20} more errors (see report file)")

            if warnings:
                print(f"\nWARNINGS ({len(warnings)}):")
                for issue in warnings[:10]:  # Limit to first 10
                    print(f"\n  [{issue.sample_id}] {issue.category}")
                    print(f"  Message: {issue.message}")

                if len(warnings) > 10:
                    print(f"\n  ... and {len(warnings) - 10} more warnings (see report file)")


def main():
    """Main entry point for validation script"""
    import sys

    # Define paths
    project_root = Path(__file__).parent.parent.parent
    schema_path = project_root / "data" / "training" / "dataset-schema.json"
    training_data_dir = project_root / "data" / "training"

    # Validate paths exist
    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}")
        sys.exit(1)

    if not training_data_dir.exists():
        print(f"ERROR: Training data directory not found: {training_data_dir}")
        sys.exit(1)

    # Run validation
    validator = TrainingDataValidator(schema_path, training_data_dir)
    report = validator.validate_all()

    # Save report
    report_path = training_data_dir / "validation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, indent=2)

    print(f"\nFull report saved to: {report_path}")

    # Exit with error code if validation failed
    if report.invalid_samples > 0:
        print("\nVALIDATION FAILED: Invalid samples found")
        sys.exit(1)
    else:
        print("\nVALIDATION PASSED: All samples are valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
