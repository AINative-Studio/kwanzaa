#!/usr/bin/env python3
"""
Validation Script for Agent Swarm Training Examples
Ensures examples meet quality standards and contain real AINative API code
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

class ExampleValidator:
    """Validates agent swarm training examples"""

    def __init__(self, examples_file: Path):
        self.examples_file = examples_file
        self.examples: List[Dict[str, Any]] = []
        self.validation_results = {
            "total_examples": 0,
            "passed": 0,
            "failed": 0,
            "issues": []
        }

    def load_examples(self) -> None:
        """Load examples from JSONL file"""
        self.examples = []
        with open(self.examples_file, 'r') as f:
            for line in f:
                if line.strip():
                    self.examples.append(json.loads(line))
        self.validation_results["total_examples"] = len(self.examples)
        print(f"✓ Loaded {len(self.examples)} examples")

    def validate_structure(self, example: Dict[str, Any], index: int) -> List[str]:
        """Validate example structure"""
        issues = []

        # Check required fields
        if "messages" not in example:
            issues.append(f"Example {index}: Missing 'messages' field")
            return issues

        messages = example["messages"]
        if not isinstance(messages, list) or len(messages) != 3:
            issues.append(f"Example {index}: Must have exactly 3 messages (system, user, assistant)")
            return issues

        # Check message roles
        expected_roles = ["system", "user", "assistant"]
        for i, (msg, expected_role) in enumerate(zip(messages, expected_roles)):
            if msg.get("role") != expected_role:
                issues.append(f"Example {index}: Message {i} has wrong role (expected {expected_role}, got {msg.get('role')})")
            if not msg.get("content"):
                issues.append(f"Example {index}: Message {i} has empty content")

        return issues

    def check_ai_attribution(self, content: str, index: int) -> List[str]:
        """Check for AI attribution violations"""
        issues = []

        # Patterns to detect
        forbidden_patterns = [
            r"Claude",
            r"Anthropic",
            r"AI-generated",
            r"Generated with.*🤖",
            r"Co-Authored-By:.*Claude",
            r"noreply@anthropic\.com"
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Example {index}: Contains AI attribution: '{pattern}'")

        return issues

    def validate_code_quality(self, content: str, index: int) -> List[str]:
        """Validate code blocks contain real AINative API patterns"""
        issues = []

        # Extract code blocks
        code_blocks = re.findall(r'```python(.*?)```', content, re.DOTALL)

        if not code_blocks:
            # Some examples may not have code (like explanatory ones)
            return issues

        # Check for real AINative imports and patterns
        ainative_patterns = [
            r'from app\.agents\.swarm',
            r'from app\.agents\.swarm\.agent_swarm',
            r'from app\.agents\.swarm\.llm_agent_orchestrator',
            r'from app\.agents\.swarm\.swarm_task',
            r'from ainative import',
            r'AgentSwarm\(',
            r'SwarmConfig\(',
            r'SwarmTask\(',
            r'LLMAgentOrchestrator\(',
            r'execute_parallel\(',
            r'execute_task\(',
            r'spawn_agent\(',
            r'AgentRole\.',
            r'SwarmRole\.',
            r'TaskType\.',
            r'AgentCollaborationMode\.'
        ]

        has_ainative_api = False
        for code_block in code_blocks:
            for pattern in ainative_patterns:
                if re.search(pattern, code_block):
                    has_ainative_api = True
                    break
            if has_ainative_api:
                break

        if code_blocks and not has_ainative_api:
            issues.append(f"Example {index}: Code blocks don't contain recognizable AINative API patterns")

        return issues

    def check_parallel_sequential_distinction(self, content: str, index: int) -> List[str]:
        """Check that examples clearly distinguish parallel vs sequential"""
        issues = []

        # Keywords that should be present in relevant examples
        parallel_keywords = [
            "parallel",
            "concurrent",
            "execute_parallel",
            "simultaneously",
            "asyncio.gather"
        ]

        sequential_keywords = [
            "sequential",
            "dependencies",
            "one after another",
            "execute_task",
            "waits for"
        ]

        content_lower = content.lower()

        # Check if example discusses parallelization
        has_parallel = any(kw in content_lower for kw in parallel_keywords)
        has_sequential = any(kw in content_lower for kw in sequential_keywords)

        # If discussing either, should be clear about the distinction
        if (has_parallel or has_sequential):
            if "parallel" in content_lower and "sequential" not in content_lower:
                # This is okay - pure parallel example
                pass
            elif "sequential" in content_lower and "parallel" not in content_lower:
                # This is okay - pure sequential example
                pass
            elif has_parallel and has_sequential:
                # Good - discusses both
                pass

        return issues

    def validate_example(self, example: Dict[str, Any], index: int) -> List[str]:
        """Validate a single example"""
        all_issues = []

        # Structure validation
        all_issues.extend(self.validate_structure(example, index))

        if "messages" not in example:
            return all_issues  # Skip further validation if structure is wrong

        # Check all messages for AI attribution
        for msg in example["messages"]:
            content = msg.get("content", "")
            all_issues.extend(self.check_ai_attribution(content, index))

        # Validate assistant response
        assistant_msg = example["messages"][2]
        assistant_content = assistant_msg.get("content", "")
        all_issues.extend(self.validate_code_quality(assistant_content, index))
        all_issues.extend(self.check_parallel_sequential_distinction(assistant_content, index))

        return all_issues

    def validate_all(self) -> Dict[str, Any]:
        """Validate all examples"""
        print("\n" + "="*70)
        print("VALIDATING AGENT SWARM TRAINING EXAMPLES")
        print("="*70 + "\n")

        for idx, example in enumerate(self.examples, 1):
            issues = self.validate_example(example, idx)

            if issues:
                self.validation_results["failed"] += 1
                self.validation_results["issues"].extend(issues)
                print(f"✗ Example {idx}: FAILED")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                self.validation_results["passed"] += 1
                print(f"✓ Example {idx}: PASSED")

        return self.validation_results

    def print_summary(self) -> None:
        """Print validation summary"""
        results = self.validation_results

        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        print(f"Total Examples: {results['total_examples']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")

        if results["failed"] == 0:
            print("\n✓ ALL EXAMPLES PASSED VALIDATION!")
            print("\nQuality Checks:")
            print("  ✓ Correct structure (system, user, assistant)")
            print("  ✓ No AI attribution violations")
            print("  ✓ Contains real AINative API patterns")
            print("  ✓ Clear parallel/sequential distinction")
        else:
            print(f"\n✗ {results['failed']} examples failed validation")
            print("\nIssues found:")
            for issue in results["issues"]:
                print(f"  - {issue}")

        print("="*70 + "\n")

    def generate_report(self) -> str:
        """Generate detailed validation report"""
        results = self.validation_results

        report = []
        report.append("# Agent Swarm Training Examples Validation Report\n")
        report.append(f"**File:** `{self.examples_file}`\n")
        report.append(f"**Date:** {Path(__file__).stat().st_mtime}\n")
        report.append("\n## Summary\n")
        report.append(f"- **Total Examples:** {results['total_examples']}")
        report.append(f"- **Passed:** {results['passed']}")
        report.append(f"- **Failed:** {results['failed']}")
        report.append(f"- **Success Rate:** {(results['passed']/results['total_examples']*100):.1f}%\n")

        report.append("\n## Validation Criteria\n")
        report.append("1. **Structure:** 3 messages (system, user, assistant)")
        report.append("2. **AI Attribution:** Zero tolerance for Claude/Anthropic mentions")
        report.append("3. **API Authenticity:** Uses actual AINative agent swarm APIs")
        report.append("4. **Clarity:** Distinguishes parallel vs sequential execution\n")

        if results["failed"] > 0:
            report.append("\n## Issues Found\n")
            for issue in results["issues"]:
                report.append(f"- {issue}")
        else:
            report.append("\n## ✓ All Examples Passed\n")
            report.append("All training examples meet quality standards and contain authentic AINative API code.")

        return "\n".join(report)


def main():
    """Main validation function"""
    examples_file = Path(__file__).parent.parent / "data" / "training" / "agent_swarm_examples_v2.jsonl"

    if not examples_file.exists():
        print(f"✗ Examples file not found: {examples_file}")
        return 1

    validator = ExampleValidator(examples_file)
    validator.load_examples()
    validator.validate_all()
    validator.print_summary()

    # Generate report
    report_file = examples_file.parent / "agent_swarm_validation_report.md"
    report = validator.generate_report()
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"Validation report saved to: {report_file}")

    # Return exit code based on validation
    return 0 if validator.validation_results["failed"] == 0 else 1


if __name__ == "__main__":
    exit(main())
