#!/usr/bin/env python3
"""
Automated Adapter Compatibility Checks

This module provides automated pre-flight checks and validation utilities
for adapter compatibility testing. Use these to quickly identify obvious
incompatibilities before running full test suites.

Usage:
    # Quick compatibility check
    python adapter_compatibility_checks.py --adapter kwanzaa-v1-olmo --base llama

    # Pre-flight validation only
    python adapter_compatibility_checks.py --adapter kwanzaa-v1-olmo --base llama --preflight-only

    # CI/CD integration
    python adapter_compatibility_checks.py --adapter $ADAPTER_NAME --base $BASE_MODEL --exit-on-failure
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CheckSeverity(str, Enum):
    """Severity level for compatibility checks."""
    CRITICAL = "critical"  # Blocks deployment
    WARNING = "warning"    # May work with workarounds
    INFO = "info"          # Informational only


@dataclass
class CompatibilityCheck:
    """Result of a single compatibility check."""
    check_name: str
    passed: bool
    severity: CheckSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None


class AdapterCompatibilityChecker:
    """Automated compatibility checker for adapters."""

    def __init__(self):
        """Initialize the compatibility checker."""
        # Known model architectures
        self.model_architectures = {
            "ai2/OLMo-7B-Instruct": {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "num_key_value_heads": 32,  # MHA
                "attention_type": "mha",
                "position_encoding": "rope",
                "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
                "architecture_family": "olmo",
            },
            "meta-llama/Meta-Llama-3.1-8B-Instruct": {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "num_key_value_heads": 8,  # GQA
                "attention_type": "gqa",
                "position_encoding": "rope",
                "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
                "architecture_family": "llama",
            },
            "deepseek-ai/DeepSeek-V2-Lite": {
                "hidden_size": 5120,
                "num_attention_heads": 32,
                "num_key_value_heads": 8,  # GQA
                "attention_type": "gqa",
                "position_encoding": "rope",
                "target_modules": ["q_proj", "kv_proj", "o_proj"],  # Fused KV
                "architecture_family": "deepseek",
                "special_features": ["moe", "fused_kv"],
            },
        }

    def run_all_checks(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> List[CompatibilityCheck]:
        """Run all compatibility checks.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            List of CompatibilityCheck results
        """
        checks = []

        checks.append(self.check_architecture_compatibility(adapter_config, base_model_id))
        checks.append(self.check_dimension_compatibility(adapter_config, base_model_id))
        checks.append(self.check_attention_mechanism(adapter_config, base_model_id))
        checks.append(self.check_target_modules(adapter_config, base_model_id))
        checks.append(self.check_position_encoding(adapter_config, base_model_id))
        checks.append(self.check_tokenizer_compatibility(adapter_config, base_model_id))
        checks.append(self.check_adapter_type_support(adapter_config, base_model_id))

        return checks

    def check_architecture_compatibility(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> CompatibilityCheck:
        """Check if adapter architecture is compatible with base model.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            CompatibilityCheck result
        """
        adapter_base = adapter_config.get("base_model_id")

        if adapter_base not in self.model_architectures:
            return CompatibilityCheck(
                check_name="architecture_compatibility",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Unknown adapter base model: {adapter_base}",
                details={"adapter_base": adapter_base},
                remediation="Manually verify architecture compatibility",
            )

        if base_model_id not in self.model_architectures:
            return CompatibilityCheck(
                check_name="architecture_compatibility",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Unknown target base model: {base_model_id}",
                details={"target_base": base_model_id},
                remediation="Manually verify architecture compatibility",
            )

        adapter_family = self.model_architectures[adapter_base]["architecture_family"]
        target_family = self.model_architectures[base_model_id]["architecture_family"]

        if adapter_family == target_family:
            return CompatibilityCheck(
                check_name="architecture_compatibility",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"Same architecture family: {adapter_family}",
                details={"family": adapter_family},
            )
        else:
            return CompatibilityCheck(
                check_name="architecture_compatibility",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Different architecture families: {adapter_family} -> {target_family}",
                details={
                    "adapter_family": adapter_family,
                    "target_family": target_family,
                },
                remediation="Expect quality degradation. Consider retraining adapter.",
            )

    def check_dimension_compatibility(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> CompatibilityCheck:
        """Check if hidden dimensions match.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            CompatibilityCheck result
        """
        adapter_base = adapter_config.get("base_model_id")

        if adapter_base not in self.model_architectures or base_model_id not in self.model_architectures:
            return CompatibilityCheck(
                check_name="dimension_compatibility",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Cannot verify dimensions - unknown models",
                remediation="Manually check hidden_size configuration",
            )

        adapter_hidden = self.model_architectures[adapter_base]["hidden_size"]
        target_hidden = self.model_architectures[base_model_id]["hidden_size"]

        if adapter_hidden == target_hidden:
            return CompatibilityCheck(
                check_name="dimension_compatibility",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"Hidden dimensions match: {adapter_hidden}",
                details={"hidden_size": adapter_hidden},
            )
        else:
            return CompatibilityCheck(
                check_name="dimension_compatibility",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"Hidden dimension mismatch: {adapter_hidden} != {target_hidden}",
                details={
                    "adapter_hidden_size": adapter_hidden,
                    "target_hidden_size": target_hidden,
                    "difference": target_hidden - adapter_hidden,
                },
                remediation="INCOMPATIBLE - adapter will fail to load. Must retrain.",
            )

    def check_attention_mechanism(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> CompatibilityCheck:
        """Check if attention mechanisms are compatible.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            CompatibilityCheck result
        """
        adapter_base = adapter_config.get("base_model_id")

        if adapter_base not in self.model_architectures or base_model_id not in self.model_architectures:
            return CompatibilityCheck(
                check_name="attention_mechanism",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Cannot verify attention mechanism - unknown models",
                remediation="Manually check attention configuration",
            )

        adapter_attn = self.model_architectures[adapter_base]["attention_type"]
        target_attn = self.model_architectures[base_model_id]["attention_type"]

        adapter_kv_heads = self.model_architectures[adapter_base]["num_key_value_heads"]
        target_kv_heads = self.model_architectures[base_model_id]["num_key_value_heads"]

        if adapter_attn == target_attn and adapter_kv_heads == target_kv_heads:
            return CompatibilityCheck(
                check_name="attention_mechanism",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"Attention mechanisms match: {adapter_attn}",
                details={
                    "attention_type": adapter_attn,
                    "kv_heads": adapter_kv_heads,
                },
            )
        else:
            severity = CheckSeverity.CRITICAL if adapter_attn != target_attn else CheckSeverity.WARNING

            return CompatibilityCheck(
                check_name="attention_mechanism",
                passed=False,
                severity=severity,
                message=f"Attention mismatch: {adapter_attn} -> {target_attn}",
                details={
                    "adapter_attention": adapter_attn,
                    "target_attention": target_attn,
                    "adapter_kv_heads": adapter_kv_heads,
                    "target_kv_heads": target_kv_heads,
                },
                remediation="MHA <-> GQA transitions may fail. Test carefully." if severity == CheckSeverity.WARNING else "INCOMPATIBLE - Different attention mechanisms.",
            )

    def check_target_modules(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> CompatibilityCheck:
        """Check if target modules are compatible.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            CompatibilityCheck result
        """
        adapter_base = adapter_config.get("base_model_id")
        adapter_target_modules = set(adapter_config.get("target_modules", []))

        if base_model_id not in self.model_architectures:
            return CompatibilityCheck(
                check_name="target_modules",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Cannot verify target modules - unknown target base",
                remediation="Manually verify target module names",
            )

        target_modules = set(self.model_architectures[base_model_id]["target_modules"])

        if adapter_target_modules == target_modules:
            return CompatibilityCheck(
                check_name="target_modules",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"Target modules match: {list(adapter_target_modules)}",
                details={"modules": list(adapter_target_modules)},
            )
        else:
            missing = target_modules - adapter_target_modules
            extra = adapter_target_modules - target_modules

            return CompatibilityCheck(
                check_name="target_modules",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"Target module mismatch",
                details={
                    "adapter_modules": list(adapter_target_modules),
                    "target_modules": list(target_modules),
                    "missing_in_adapter": list(missing),
                    "extra_in_adapter": list(extra),
                },
                remediation="Adapter may fail to load or produce errors. Retrain with correct target modules.",
            )

    def check_position_encoding(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> CompatibilityCheck:
        """Check if position encoding schemes are compatible.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            CompatibilityCheck result
        """
        adapter_base = adapter_config.get("base_model_id")

        if adapter_base not in self.model_architectures or base_model_id not in self.model_architectures:
            return CompatibilityCheck(
                check_name="position_encoding",
                passed=False,
                severity=CheckSeverity.INFO,
                message="Cannot verify position encoding - unknown models",
                remediation="Manually check position encoding (RoPE/Absolute/ALiBi)",
            )

        adapter_pos = self.model_architectures[adapter_base]["position_encoding"]
        target_pos = self.model_architectures[base_model_id]["position_encoding"]

        if adapter_pos == target_pos:
            return CompatibilityCheck(
                check_name="position_encoding",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"Position encoding matches: {adapter_pos}",
                details={"encoding": adapter_pos},
            )
        else:
            return CompatibilityCheck(
                check_name="position_encoding",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Position encoding mismatch: {adapter_pos} -> {target_pos}",
                details={
                    "adapter_encoding": adapter_pos,
                    "target_encoding": target_pos,
                },
                remediation="May cause context length issues. Test with long contexts.",
            )

    def check_tokenizer_compatibility(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> CompatibilityCheck:
        """Check if tokenizers are compatible.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            CompatibilityCheck result
        """
        adapter_base = adapter_config.get("base_model_id")

        # Simple heuristic: same model family = compatible tokenizers
        if adapter_base not in self.model_architectures or base_model_id not in self.model_architectures:
            return CompatibilityCheck(
                check_name="tokenizer_compatibility",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Cannot verify tokenizer compatibility - unknown models",
                remediation="Manually test tokenizer vocab size and special tokens",
            )

        adapter_family = self.model_architectures[adapter_base]["architecture_family"]
        target_family = self.model_architectures[base_model_id]["architecture_family"]

        if adapter_family == target_family:
            return CompatibilityCheck(
                check_name="tokenizer_compatibility",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"Same model family - tokenizers likely compatible",
                details={"family": adapter_family},
            )
        else:
            return CompatibilityCheck(
                check_name="tokenizer_compatibility",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Different model families - tokenizer may differ",
                details={
                    "adapter_family": adapter_family,
                    "target_family": target_family,
                },
                remediation="Test for special token differences and vocab size mismatches",
            )

    def check_adapter_type_support(
        self,
        adapter_config: Dict[str, Any],
        base_model_id: str,
    ) -> CompatibilityCheck:
        """Check if adapter type is supported.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model identifier

        Returns:
            CompatibilityCheck result
        """
        adapter_type = adapter_config.get("adapter_type", "").lower()

        supported_types = ["lora", "qlora", "adalora"]

        if adapter_type in supported_types:
            return CompatibilityCheck(
                check_name="adapter_type_support",
                passed=True,
                severity=CheckSeverity.INFO,
                message=f"Adapter type '{adapter_type}' is supported",
                details={"adapter_type": adapter_type},
            )
        elif adapter_type == "full_finetune":
            return CompatibilityCheck(
                check_name="adapter_type_support",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message="Full fine-tune models cannot be cross-loaded",
                details={"adapter_type": adapter_type},
                remediation="Full fine-tunes are base model-specific. Cannot cross-load.",
            )
        else:
            return CompatibilityCheck(
                check_name="adapter_type_support",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Unknown adapter type: {adapter_type}",
                details={"adapter_type": adapter_type},
                remediation="Verify adapter type is LoRA-based",
            )

    def generate_report(
        self,
        checks: List[CompatibilityCheck],
        verbose: bool = True,
    ) -> Tuple[bool, str]:
        """Generate human-readable compatibility report.

        Args:
            checks: List of compatibility check results
            verbose: Include detailed information

        Returns:
            Tuple of (all_passed, report_text)
        """
        lines = []
        lines.append("=" * 80)
        lines.append("ADAPTER COMPATIBILITY CHECK REPORT")
        lines.append("=" * 80)

        # Summary
        total = len(checks)
        passed = len([c for c in checks if c.passed])
        critical_failures = [c for c in checks if not c.passed and c.severity == CheckSeverity.CRITICAL]
        warnings = [c for c in checks if not c.passed and c.severity == CheckSeverity.WARNING]

        lines.append(f"\nSummary: {passed}/{total} checks passed")
        lines.append(f"  Critical Failures: {len(critical_failures)}")
        lines.append(f"  Warnings: {len(warnings)}")

        all_passed = len(critical_failures) == 0

        if all_passed:
            lines.append("\nOverall Status: COMPATIBLE (with possible warnings)")
        else:
            lines.append("\nOverall Status: INCOMPATIBLE (critical failures detected)")

        # Critical failures
        if critical_failures:
            lines.append("\n" + "=" * 80)
            lines.append("CRITICAL FAILURES (BLOCKING)")
            lines.append("=" * 80)

            for check in critical_failures:
                lines.append(f"\n[CRITICAL] {check.check_name}")
                lines.append(f"  Message: {check.message}")
                if check.remediation:
                    lines.append(f"  Remediation: {check.remediation}")
                if verbose and check.details:
                    lines.append(f"  Details: {json.dumps(check.details, indent=4)}")

        # Warnings
        if warnings:
            lines.append("\n" + "=" * 80)
            lines.append("WARNINGS (NON-BLOCKING)")
            lines.append("=" * 80)

            for check in warnings:
                lines.append(f"\n[WARNING] {check.check_name}")
                lines.append(f"  Message: {check.message}")
                if check.remediation:
                    lines.append(f"  Remediation: {check.remediation}")
                if verbose and check.details:
                    lines.append(f"  Details: {json.dumps(check.details, indent=4)}")

        # All checks detail
        if verbose:
            lines.append("\n" + "=" * 80)
            lines.append("ALL CHECKS DETAIL")
            lines.append("=" * 80)

            for check in checks:
                status = "PASS" if check.passed else "FAIL"
                lines.append(f"\n[{status}] {check.check_name} ({check.severity.value})")
                lines.append(f"  {check.message}")

        lines.append("\n" + "=" * 80)

        return all_passed, "\n".join(lines)


def main():
    """Main entry point for compatibility checks."""
    parser = argparse.ArgumentParser(
        description="Automated adapter compatibility checks"
    )
    parser.add_argument(
        "--adapter",
        type=str,
        required=True,
        help="Adapter name or config file",
    )
    parser.add_argument(
        "--base",
        type=str,
        required=True,
        help="Base model ID",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Only run pre-flight checks, don't run full tests",
    )
    parser.add_argument(
        "--exit-on-failure",
        action="store_true",
        help="Exit with code 1 on critical failures (for CI/CD)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Load adapter config (mock for now)
    # In production, this would load from a config file or registry
    adapter_config = {
        "name": args.adapter,
        "base_model_id": "ai2/OLMo-7B-Instruct",  # Default assumption
        "adapter_type": "lora",
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    }

    # Map short names to full IDs
    base_model_map = {
        "olmo": "ai2/OLMo-7B-Instruct",
        "llama": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "deepseek": "deepseek-ai/DeepSeek-V2-Lite",
    }

    base_model_id = base_model_map.get(args.base.lower(), args.base)

    # Run checks
    checker = AdapterCompatibilityChecker()
    checks = checker.run_all_checks(adapter_config, base_model_id)

    # Generate report
    all_passed, report = checker.generate_report(checks, verbose=args.verbose)

    print(report)

    # Exit with appropriate code
    if args.exit_on_failure and not all_passed:
        logger.error("Critical compatibility failures detected")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
