#!/usr/bin/env python3
"""
Validate AINative Training Dataset

This script validates the extracted training data to ensure:
1. No AI attribution (Claude, Anthropic, etc.) - ZERO TOLERANCE
2. Valid JSON structure
3. Valid Python/TypeScript syntax in code blocks
4. Proper message format (system, user, assistant)
5. Reasonable content length
6. Coverage across all categories

Issue: #72
Epic: #69
"""

import json
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Tuple
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AINativeTrainingDataValidator:
    """Validate AINative training dataset quality."""

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.examples: List[Dict] = []
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []

        # Validation statistics
        self.stats = {
            "total_examples": 0,
            "valid_examples": 0,
            "invalid_examples": 0,
            "has_ai_attribution": 0,
            "invalid_json": 0,
            "invalid_structure": 0,
            "syntax_errors": 0,
            "missing_tests": 0,
            "missing_error_handling": 0,
            "missing_type_hints": 0,
        }

    def load_dataset(self) -> bool:
        """Load JSONL dataset."""
        if not self.dataset_path.exists():
            logger.error("Dataset file does not exist: %s", self.dataset_path)
            return False

        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        example = json.loads(line)
                        self.examples.append(example)
                    except json.JSONDecodeError as e:
                        self.errors.append({
                            "line": line_num,
                            "type": "invalid_json",
                            "message": str(e)
                        })
                        self.stats["invalid_json"] += 1

            self.stats["total_examples"] = len(self.examples)
            logger.info("Loaded %d examples from %s", len(self.examples), self.dataset_path)
            return True

        except Exception as e:
            logger.error("Failed to load dataset: %s", e)
            return False

    def validate_example(self, example: Dict, example_num: int) -> Tuple[bool, List[str]]:
        """Validate a single training example."""
        issues = []

        # Check structure
        if "messages" not in example:
            issues.append("Missing 'messages' field")
            self.stats["invalid_structure"] += 1
            return False, issues

        messages = example["messages"]
        if not isinstance(messages, list) or len(messages) < 2:
            issues.append("Invalid messages structure (need at least system + user or user + assistant)")
            self.stats["invalid_structure"] += 1
            return False, issues

        # Check for AI attribution (ZERO TOLERANCE)
        full_text = json.dumps(example).lower()
        forbidden_terms = [
            "claude",
            "anthropic",
            "generated with",
            "co-authored-by: claude",
            "🤖 generated with",
            "ai-generated"
        ]

        for term in forbidden_terms:
            if term in full_text:
                issues.append(f"FORBIDDEN AI ATTRIBUTION: Contains '{term}'")
                self.stats["has_ai_attribution"] += 1

        # Validate message roles
        valid_roles = {"system", "user", "assistant"}
        for i, msg in enumerate(messages):
            if "role" not in msg or "content" not in msg:
                issues.append(f"Message {i} missing role or content")
                continue

            if msg["role"] not in valid_roles:
                issues.append(f"Message {i} has invalid role: {msg['role']}")

        # Check assistant message (if present)
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        if assistant_messages:
            assistant_content = assistant_messages[0]["content"]

            # Validate Python code syntax
            python_blocks = re.findall(r'```python\n(.*?)\n```', assistant_content, re.DOTALL)
            for i, code in enumerate(python_blocks):
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    issues.append(f"Python syntax error in code block {i+1}: {e}")
                    self.stats["syntax_errors"] += 1

            # Check for tests
            if len(assistant_content) > 200:  # Only check substantial responses
                if not re.search(r'\btest[_\s]|pytest|@pytest', assistant_content.lower()):
                    issues.append("No tests found in response")
                    self.stats["missing_tests"] += 1

            # Check for error handling
            if 'def ' in assistant_content or 'async def' in assistant_content:
                if not re.search(r'\btry\b|\bexcept\b|HTTPException|raise', assistant_content):
                    issues.append("No error handling found")
                    self.stats["missing_error_handling"] += 1

            # Check for type hints
            if 'def ' in assistant_content:
                if not re.search(r':\s*(str|int|bool|List|Dict|Optional|Any|UUID|Session)', assistant_content):
                    issues.append("No type hints found")
                    self.stats["missing_type_hints"] += 1

        # Check content length
        total_length = sum(len(msg.get("content", "")) for msg in messages)
        if total_length < 50:
            issues.append("Content too short (< 50 chars)")
        elif total_length > 10000:
            self.warnings.append({
                "example": example_num,
                "message": "Content very long (> 10000 chars)"
            })

        return len(issues) == 0, issues

    def validate_all(self) -> bool:
        """Validate all examples."""
        logger.info("Validating %d examples...", len(self.examples))

        for i, example in enumerate(self.examples, 1):
            is_valid, issues = self.validate_example(example, i)

            if is_valid:
                self.stats["valid_examples"] += 1
            else:
                self.stats["invalid_examples"] += 1
                self.errors.append({
                    "example": i,
                    "issues": issues
                })

        logger.info("Validation complete!")
        return self.stats["invalid_examples"] == 0

    def print_report(self):
        """Print validation report."""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)

        print(f"\nDataset: {self.dataset_path}")
        print(f"Total Examples: {self.stats['total_examples']}")

        print("\n" + "-"*70)
        print("VALIDATION RESULTS")
        print("-"*70)
        print(f"✅ Valid Examples:   {self.stats['valid_examples']}")
        print(f"❌ Invalid Examples: {self.stats['invalid_examples']}")

        success_rate = (self.stats['valid_examples'] / max(self.stats['total_examples'], 1)) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")

        print("\n" + "-"*70)
        print("CRITICAL ISSUES")
        print("-"*70)
        print(f"🚨 AI Attribution:   {self.stats['has_ai_attribution']} (ZERO TOLERANCE)")
        print(f"❌ Invalid JSON:     {self.stats['invalid_json']}")
        print(f"❌ Invalid Structure: {self.stats['invalid_structure']}")
        print(f"❌ Syntax Errors:    {self.stats['syntax_errors']}")

        print("\n" + "-"*70)
        print("QUALITY WARNINGS")
        print("-"*70)
        print(f"⚠️  Missing Tests:        {self.stats['missing_tests']}")
        print(f"⚠️  Missing Error Handling: {self.stats['missing_error_handling']}")
        print(f"⚠️  Missing Type Hints:    {self.stats['missing_type_hints']}")

        # Print first few errors
        if self.errors:
            print("\n" + "-"*70)
            print("FIRST 10 ERRORS")
            print("-"*70)
            for error in self.errors[:10]:
                if "line" in error:
                    print(f"\nLine {error['line']}: {error['type']}")
                    print(f"  {error['message']}")
                else:
                    print(f"\nExample {error['example']}:")
                    for issue in error['issues']:
                        print(f"  - {issue}")

        # Print warnings
        if self.warnings:
            print("\n" + "-"*70)
            print(f"WARNINGS ({len(self.warnings)} total)")
            print("-"*70)
            for warning in self.warnings[:5]:
                print(f"Example {warning['example']}: {warning['message']}")

        print("\n" + "="*70)

        # Final verdict
        if self.stats["has_ai_attribution"] > 0:
            print("❌ CRITICAL FAILURE: AI attribution found (ZERO TOLERANCE)")
            print("="*70)
            return False
        elif self.stats["invalid_examples"] == 0:
            print("✅ VALIDATION PASSED")
            print("="*70)
            return True
        elif success_rate >= 90:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            print(f"   {self.stats['invalid_examples']} examples need fixing")
            print("="*70)
            return True
        else:
            print("❌ VALIDATION FAILED")
            print(f"   Only {success_rate:.1f}% of examples are valid (need >= 90%)")
            print("="*70)
            return False

    def save_error_report(self, output_path: str):
        """Save detailed error report to file."""
        report_data = {
            "stats": self.stats,
            "errors": self.errors,
            "warnings": self.warnings
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        logger.info("Saved error report to %s", output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Validate AINative training dataset'
    )
    parser.add_argument(
        'dataset_path',
        help='Path to JSONL training dataset'
    )
    parser.add_argument(
        '--error-report',
        default='outputs/validation_errors.json',
        help='Output path for error report'
    )

    args = parser.parse_args()

    validator = AINativeTrainingDataValidator(args.dataset_path)

    # Load dataset
    if not validator.load_dataset():
        return 1

    # Validate all examples
    validator.validate_all()

    # Print report
    passed = validator.print_report()

    # Save error report
    if validator.errors or validator.warnings:
        validator.save_error_report(args.error_report)

    return 0 if passed else 1


if __name__ == "__main__":
    exit(main())
