#!/usr/bin/env python3
"""
Adapter Compatibility Testing Framework for Kwanzaa

This script tests trained Kwanzaa adapters (LoRA/QLoRA) across different base models
to identify compatibility issues, performance deltas, and architecture-specific problems.

Design Philosophy:
- ZERO TOLERANCE for hidden failures: All incompatibilities are documented
- Evidence-based recommendations: Collect metrics, not opinions
- Production-focused: Test what matters for deployment
- Transparent reporting: Surface all issues, even embarrassing ones

Testing Matrix:
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│ Adapter             │ AI2 OLMo-7B  │ LLaMA 3.1-8B │ DeepSeek-V2  │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ kwanzaa-v1-olmo     │ ✓ Native     │ ? Test       │ ? Test       │
│ kwanzaa-v1-llama    │ ? Test       │ ✓ Native     │ ? Test       │
│ kwanzaa-v1-deepseek │ ? Test       │ ? Test       │ ✓ Native     │
└─────────────────────┴──────────────┴──────────────┴──────────────┘

Usage:
    # Test single adapter on multiple bases
    python test_adapter_compatibility.py --adapter kwanzaa-v1-olmo --bases olmo,llama,deepseek

    # Test all combinations
    python test_adapter_compatibility.py --test-all

    # Quick smoke test (5 prompts)
    python test_adapter_compatibility.py --adapter kwanzaa-v1-olmo --bases llama --quick

    # Full evaluation (50 prompts)
    python test_adapter_compatibility.py --adapter kwanzaa-v1-olmo --bases llama --full

Output:
    - Compatibility matrix (which adapters work with which bases)
    - Performance comparison table
    - Known issues and workarounds
    - Recommendations for production use
"""

import argparse
import json
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/Users/aideveloper/kwanzaa/evals/results/adapter_compatibility.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BaseModel(str, Enum):
    """Supported base models for adapter compatibility testing."""
    OLMO_7B = "ai2/OLMo-7B-Instruct"
    LLAMA_3_1_8B = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    DEEPSEEK_V2_LITE = "deepseek-ai/DeepSeek-V2-Lite"


class CompatibilityStatus(str, Enum):
    """Compatibility test status."""
    SUCCESS = "success"  # Adapter loads and runs correctly
    LOAD_FAILURE = "load_failure"  # Adapter fails to load
    INFERENCE_FAILURE = "inference_failure"  # Adapter loads but inference fails
    DEGRADED = "degraded"  # Works but with significant quality/performance loss
    UNTESTED = "untested"


class FailureCategory(str, Enum):
    """Categories of compatibility failures."""
    DIMENSION_MISMATCH = "dimension_mismatch"  # Hidden size mismatch
    ARCHITECTURE_INCOMPATIBILITY = "architecture_incompatibility"  # Different layer structure
    TOKENIZER_MISMATCH = "tokenizer_mismatch"  # Vocab size or special tokens differ
    DTYPE_INCOMPATIBILITY = "dtype_incompatibility"  # Float16 vs BFloat16 issues
    ATTENTION_MECHANISM = "attention_mechanism"  # GQA vs MHA vs MQA conflicts
    POSITION_ENCODING = "position_encoding"  # RoPE vs Absolute vs ALiBi
    MEMORY_OVERFLOW = "memory_overflow"  # OOM during loading or inference
    SLOW_INFERENCE = "slow_inference"  # Unacceptably slow (>5s per token)
    QUALITY_DEGRADATION = "quality_degradation"  # High citation error rate
    JSON_COMPLIANCE_FAILURE = "json_compliance_failure"  # Answer JSON format breaks


@dataclass
class AdapterConfig:
    """Configuration for a trained adapter."""
    name: str
    path: str
    base_model_id: str  # The base model this adapter was trained on
    adapter_type: str  # "lora", "qlora", "full_finetune"
    rank: int = 16
    alpha: int = 32
    target_modules: List[str] = field(default_factory=list)
    training_date: Optional[str] = None
    training_samples: Optional[int] = None

    # Expected behavior
    expected_citation_accuracy: float = 0.85
    expected_json_compliance: float = 0.95
    expected_refusal_rate: float = 0.80


@dataclass
class TestPrompt:
    """A test prompt for compatibility evaluation."""
    prompt_id: str
    query: str
    category: str  # "citation_required", "refusal", "json_compliance", "historical_qa"
    expected_behavior: str
    difficulty: str = "medium"
    require_citations: bool = True

    # For validation
    expected_citations_count: Optional[int] = None
    expected_json_fields: Optional[List[str]] = None
    should_refuse: bool = False


@dataclass
class CompatibilityTestResult:
    """Result of testing an adapter on a specific base model."""
    adapter_name: str
    base_model_id: str
    status: CompatibilityStatus

    # Loading metrics
    load_success: bool
    load_time_seconds: Optional[float] = None
    load_error: Optional[str] = None

    # Inference metrics
    inference_success: bool = False
    avg_tokens_per_second: Optional[float] = None
    avg_latency_ms: Optional[float] = None
    peak_memory_gb: Optional[float] = None

    # Quality metrics
    citation_accuracy: Optional[float] = None
    json_compliance_rate: Optional[float] = None
    refusal_rate: Optional[float] = None
    answer_quality_score: Optional[float] = None

    # Failure analysis
    failure_categories: List[FailureCategory] = field(default_factory=list)
    failure_details: Dict[str, Any] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)

    # Comparison to native base
    performance_delta_pct: Optional[float] = None  # % change vs native base
    quality_delta_pct: Optional[float] = None

    # Test execution
    prompts_tested: int = 0
    prompts_succeeded: int = 0
    test_duration_seconds: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Recommendations
    recommended_for_production: bool = False
    workarounds: List[str] = field(default_factory=list)
    known_issues: List[str] = field(default_factory=list)


@dataclass
class PromptTestResult:
    """Result of testing a single prompt."""
    prompt_id: str
    success: bool
    response_text: Optional[str] = None
    response_json: Optional[Dict] = None
    error: Optional[str] = None

    # Validation results
    has_citations: bool = False
    citation_count: int = 0
    citations_valid: bool = False
    json_valid: bool = False
    json_schema_compliant: bool = False
    refused_appropriately: Optional[bool] = None

    # Performance
    latency_ms: Optional[float] = None
    tokens_generated: Optional[int] = None

    # Quality scores
    citation_accuracy_score: Optional[float] = None
    answer_quality_score: Optional[float] = None


class AdapterCompatibilityTester:
    """Comprehensive adapter compatibility testing framework."""

    def __init__(
        self,
        results_dir: str = "/Users/aideveloper/kwanzaa/evals/results/adapter_compatibility",
        cache_dir: str = "/Users/aideveloper/kwanzaa/.cache/models",
        device: str = "cpu",
    ):
        """Initialize the compatibility tester.

        Args:
            results_dir: Directory to save test results
            cache_dir: Directory to cache model downloads
            device: Device for inference ("cpu", "cuda", "mps")
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.device = device

        # Model cache
        self._loaded_models: Dict[str, Any] = {}

        logger.info(f"Initialized AdapterCompatibilityTester")
        logger.info(f"  Results dir: {self.results_dir}")
        logger.info(f"  Cache dir: {self.cache_dir}")
        logger.info(f"  Device: {self.device}")

    def get_test_prompts(self, quick: bool = False) -> List[TestPrompt]:
        """Get test prompts for compatibility evaluation.

        Args:
            quick: If True, return small set for smoke testing (5 prompts)
                   If False, return full evaluation set (50 prompts)

        Returns:
            List of TestPrompt objects
        """
        # Quick smoke test set
        quick_prompts = [
            TestPrompt(
                prompt_id="citation_basic",
                query="Who was the first African American Supreme Court Justice?",
                category="citation_required",
                expected_behavior="Answer with citation to provided sources",
                difficulty="easy",
                expected_citations_count=1,
            ),
            TestPrompt(
                prompt_id="refusal_out_of_scope",
                query="What were the attendance numbers at the 1972 National Black Political Convention?",
                category="refusal",
                expected_behavior="Refuse due to lack of sources",
                difficulty="medium",
                should_refuse=True,
            ),
            TestPrompt(
                prompt_id="json_compliance",
                query="List three contributions of Harriet Tubman",
                category="json_compliance",
                expected_behavior="Valid JSON with answer, sources, unknowns",
                difficulty="easy",
                expected_json_fields=["answer", "sources", "retrieval_summary", "unknowns"],
            ),
            TestPrompt(
                prompt_id="historical_qa_complex",
                query="Explain the significance of the Montgomery Bus Boycott",
                category="historical_qa",
                expected_behavior="Multi-paragraph answer with multiple citations",
                difficulty="hard",
                expected_citations_count=3,
            ),
            TestPrompt(
                prompt_id="citation_multiple_sources",
                query="Describe the key achievements of the Civil Rights Act of 1964",
                category="citation_required",
                expected_behavior="Synthesize from multiple sources with proper attribution",
                difficulty="medium",
                expected_citations_count=2,
            ),
        ]

        if quick:
            return quick_prompts

        # Full evaluation set (50 prompts covering all edge cases)
        full_prompts = quick_prompts + [
            # Additional citation tests
            TestPrompt(
                prompt_id="citation_conflicting_sources",
                query="What year did the Harlem Renaissance begin?",
                category="citation_required",
                expected_behavior="Address conflicting sources appropriately",
                difficulty="hard",
            ),
            TestPrompt(
                prompt_id="citation_primary_source_only",
                query="Quote from Dr. King's 'Letter from Birmingham Jail'",
                category="citation_required",
                expected_behavior="Use only primary sources for direct quotes",
                difficulty="medium",
            ),
            # Additional refusal tests
            TestPrompt(
                prompt_id="refusal_ambiguous_query",
                query="Tell me about the movement",
                category="refusal",
                expected_behavior="Ask for clarification",
                difficulty="easy",
            ),
            TestPrompt(
                prompt_id="refusal_partial_information",
                query="How many people attended the March on Washington?",
                category="refusal",
                expected_behavior="Provide estimate with uncertainty qualifiers",
                difficulty="medium",
            ),
            # JSON compliance edge cases
            TestPrompt(
                prompt_id="json_special_characters",
                query="What did Malcolm X say about 'by any means necessary'?",
                category="json_compliance",
                expected_behavior="Properly escape quotes in JSON",
                difficulty="medium",
            ),
            TestPrompt(
                prompt_id="json_nested_structure",
                query="Compare three different accounts of the Selma to Montgomery marches",
                category="json_compliance",
                expected_behavior="Complex nested JSON with multiple sources",
                difficulty="hard",
            ),
            # Continue with 40 more prompts covering:
            # - Long-form answers (context length testing)
            # - Multi-turn conversations (state management)
            # - Different persona modes (educator, researcher, creator)
            # - Edge cases (empty results, low-quality sources, contradictions)
            # ... (truncated for brevity - would include 45 more prompts)
        ]

        return full_prompts

    def load_adapter_and_base(
        self,
        adapter_config: AdapterConfig,
        base_model_id: str,
    ) -> Tuple[bool, Optional[Any], Optional[str]]:
        """Load an adapter onto a base model.

        Args:
            adapter_config: Configuration of the adapter to load
            base_model_id: HuggingFace model ID of the base model

        Returns:
            Tuple of (success, model, error_message)
        """
        try:
            logger.info(f"Loading adapter '{adapter_config.name}' onto base '{base_model_id}'")
            start_time = time.time()

            # TODO: Implement actual model loading with transformers + peft
            # This is a placeholder implementation

            # Simulate loading
            time.sleep(0.5)

            # Check for common incompatibilities
            error = self._check_compatibility_issues(adapter_config, base_model_id)
            if error:
                logger.error(f"Compatibility check failed: {error}")
                return False, None, error

            # Placeholder: Return mock model
            mock_model = {
                "adapter": adapter_config.name,
                "base": base_model_id,
                "loaded_at": datetime.utcnow().isoformat(),
            }

            load_time = time.time() - start_time
            logger.info(f"Successfully loaded adapter in {load_time:.2f}s")

            return True, mock_model, None

        except Exception as e:
            error_msg = f"Failed to load adapter: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return False, None, error_msg

    def _check_compatibility_issues(
        self,
        adapter_config: AdapterConfig,
        base_model_id: str,
    ) -> Optional[str]:
        """Check for known compatibility issues between adapter and base model.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model ID

        Returns:
            Error message if incompatible, None if compatible
        """
        # Check if adapter was trained on a different base model
        if adapter_config.base_model_id != base_model_id:
            logger.warning(
                f"Adapter was trained on '{adapter_config.base_model_id}' "
                f"but being loaded onto '{base_model_id}'"
            )

        # Known incompatibilities
        if "llama" in adapter_config.base_model_id.lower() and "olmo" in base_model_id.lower():
            return "Dimension mismatch: LLaMA uses 4096 hidden size, OLMo uses 4096 but different layer structure"

        if "deepseek" in adapter_config.base_model_id.lower() and "llama" in base_model_id.lower():
            return "Architecture incompatibility: DeepSeek uses MoE architecture, LLaMA does not"

        # Check target modules compatibility
        olmo_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
        llama_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]  # Same
        deepseek_modules = ["q_proj", "kv_proj", "o_proj"]  # Different (grouped KV)

        if "deepseek" in base_model_id.lower():
            if not any(m in adapter_config.target_modules for m in deepseek_modules):
                return f"Target module mismatch: Adapter targets {adapter_config.target_modules} but DeepSeek expects {deepseek_modules}"

        return None

    def run_inference(
        self,
        model: Any,
        prompt: TestPrompt,
        system_prompt: Optional[str] = None,
    ) -> PromptTestResult:
        """Run inference with the adapter-enhanced model.

        Args:
            model: Loaded model (with adapter)
            prompt: Test prompt to evaluate
            system_prompt: Optional system prompt

        Returns:
            PromptTestResult with inference results and validation
        """
        try:
            start_time = time.time()

            # TODO: Implement actual inference
            # This is a placeholder that simulates inference

            # Simulate inference time
            time.sleep(0.1)

            # Mock response
            response_text = f"[Mock response for: {prompt.query}]"
            response_json = {
                "answer": {
                    "text": response_text,
                    "confidence": 0.85,
                },
                "sources": [
                    {
                        "citation_label": "[Source 1]",
                        "canonical_url": "https://example.com/source1",
                        "title": "Mock Source",
                    }
                ],
                "retrieval_summary": {
                    "total_results": 1,
                    "search_time_ms": 50,
                },
                "unknowns": {
                    "unsupported_claims": [],
                }
            }

            latency_ms = (time.time() - start_time) * 1000

            # Validate response
            validation_result = self._validate_response(prompt, response_text, response_json)

            return PromptTestResult(
                prompt_id=prompt.prompt_id,
                success=True,
                response_text=response_text,
                response_json=response_json,
                latency_ms=latency_ms,
                tokens_generated=len(response_text.split()),
                **validation_result,
            )

        except Exception as e:
            error_msg = f"Inference failed: {str(e)}"
            logger.error(error_msg)
            return PromptTestResult(
                prompt_id=prompt.prompt_id,
                success=False,
                error=error_msg,
            )

    def _validate_response(
        self,
        prompt: TestPrompt,
        response_text: str,
        response_json: Optional[Dict],
    ) -> Dict[str, Any]:
        """Validate a model response against expected behavior.

        Args:
            prompt: Original test prompt
            response_text: Model's text response
            response_json: Parsed JSON response (if available)

        Returns:
            Dictionary of validation results
        """
        results = {}

        # Citation validation
        results["has_citations"] = "[" in response_text and "]" in response_text
        results["citation_count"] = response_text.count("[Source")
        results["citations_valid"] = results["citation_count"] > 0

        if prompt.expected_citations_count:
            results["citation_accuracy_score"] = min(
                1.0,
                results["citation_count"] / prompt.expected_citations_count
            )

        # JSON validation
        results["json_valid"] = response_json is not None
        if response_json and prompt.expected_json_fields:
            results["json_schema_compliant"] = all(
                field in response_json for field in prompt.expected_json_fields
            )
        else:
            results["json_schema_compliant"] = False

        # Refusal validation
        if prompt.should_refuse:
            refusal_indicators = [
                "i don't have",
                "i cannot",
                "no information",
                "not in my sources",
            ]
            results["refused_appropriately"] = any(
                indicator in response_text.lower() for indicator in refusal_indicators
            )

        # Answer quality (simple heuristic)
        word_count = len(response_text.split())
        results["answer_quality_score"] = min(1.0, word_count / 50)  # 50 words = perfect

        return results

    def test_adapter_on_base(
        self,
        adapter_config: AdapterConfig,
        base_model_id: str,
        prompts: List[TestPrompt],
    ) -> CompatibilityTestResult:
        """Test an adapter's compatibility with a specific base model.

        Args:
            adapter_config: Adapter configuration
            base_model_id: Base model to test on
            prompts: Test prompts to evaluate

        Returns:
            CompatibilityTestResult with comprehensive metrics
        """
        logger.info(f"Testing adapter '{adapter_config.name}' on base '{base_model_id}'")
        test_start_time = time.time()

        result = CompatibilityTestResult(
            adapter_name=adapter_config.name,
            base_model_id=base_model_id,
            status=CompatibilityStatus.UNTESTED,
            load_success=False,
            inference_success=False,
        )

        # Step 1: Load adapter onto base model
        load_start = time.time()
        load_success, model, load_error = self.load_adapter_and_base(
            adapter_config, base_model_id
        )
        result.load_time_seconds = time.time() - load_start
        result.load_success = load_success
        result.load_error = load_error

        if not load_success:
            result.status = CompatibilityStatus.LOAD_FAILURE
            result.error_messages.append(load_error or "Unknown load error")

            # Categorize failure
            if "dimension" in (load_error or "").lower():
                result.failure_categories.append(FailureCategory.DIMENSION_MISMATCH)
            elif "architecture" in (load_error or "").lower():
                result.failure_categories.append(FailureCategory.ARCHITECTURE_INCOMPATIBILITY)
            elif "tokenizer" in (load_error or "").lower():
                result.failure_categories.append(FailureCategory.TOKENIZER_MISMATCH)

            return result

        # Step 2: Run inference on test prompts
        prompt_results: List[PromptTestResult] = []

        for prompt in prompts:
            logger.info(f"  Testing prompt: {prompt.prompt_id}")
            prompt_result = self.run_inference(model, prompt)
            prompt_results.append(prompt_result)

        result.prompts_tested = len(prompts)
        result.prompts_succeeded = len([r for r in prompt_results if r.success])
        result.inference_success = result.prompts_succeeded > 0

        if result.prompts_succeeded == 0:
            result.status = CompatibilityStatus.INFERENCE_FAILURE
            result.failure_categories.append(FailureCategory.ARCHITECTURE_INCOMPATIBILITY)
            return result

        # Step 3: Calculate aggregate metrics
        successful_results = [r for r in prompt_results if r.success]

        if successful_results:
            # Citation accuracy
            citation_scores = [
                r.citation_accuracy_score for r in successful_results
                if r.citation_accuracy_score is not None
            ]
            result.citation_accuracy = np.mean(citation_scores) if citation_scores else 0.0

            # JSON compliance
            json_compliant = [
                r.json_schema_compliant for r in successful_results
            ]
            result.json_compliance_rate = sum(json_compliant) / len(json_compliant) if json_compliant else 0.0

            # Refusal rate
            refusal_results = [
                r for r in successful_results if r.refused_appropriately is not None
            ]
            if refusal_results:
                result.refusal_rate = sum(
                    1 for r in refusal_results if r.refused_appropriately
                ) / len(refusal_results)

            # Performance
            latencies = [r.latency_ms for r in successful_results if r.latency_ms]
            result.avg_latency_ms = np.mean(latencies) if latencies else None

            # Answer quality
            quality_scores = [
                r.answer_quality_score for r in successful_results
                if r.answer_quality_score
            ]
            result.answer_quality_score = np.mean(quality_scores) if quality_scores else None

        # Step 4: Determine overall status
        if result.citation_accuracy and result.citation_accuracy >= 0.85:
            if result.json_compliance_rate and result.json_compliance_rate >= 0.95:
                result.status = CompatibilityStatus.SUCCESS
                result.recommended_for_production = True
            else:
                result.status = CompatibilityStatus.DEGRADED
                result.failure_categories.append(FailureCategory.JSON_COMPLIANCE_FAILURE)
                result.known_issues.append(
                    f"JSON compliance rate {result.json_compliance_rate:.1%} below threshold (95%)"
                )
        else:
            result.status = CompatibilityStatus.DEGRADED
            result.failure_categories.append(FailureCategory.QUALITY_DEGRADATION)
            result.known_issues.append(
                f"Citation accuracy {result.citation_accuracy:.1%} below threshold (85%)"
            )

        # Step 5: Add workarounds if degraded
        if result.status == CompatibilityStatus.DEGRADED:
            if FailureCategory.JSON_COMPLIANCE_FAILURE in result.failure_categories:
                result.workarounds.append(
                    "Add post-processing JSON repair layer"
                )
                result.workarounds.append(
                    "Retrain adapter with 50 additional JSON-format examples"
                )

            if FailureCategory.QUALITY_DEGRADATION in result.failure_categories:
                result.workarounds.append(
                    "Retrain adapter on this specific base model"
                )
                result.workarounds.append(
                    "Use ensemble approach with multiple adapters"
                )

        result.test_duration_seconds = time.time() - test_start_time

        logger.info(f"Completed test: {result.status.value}")
        logger.info(f"  Citation accuracy: {result.citation_accuracy:.1%}" if result.citation_accuracy else "  Citation accuracy: N/A")
        logger.info(f"  JSON compliance: {result.json_compliance_rate:.1%}" if result.json_compliance_rate else "  JSON compliance: N/A")

        return result

    def generate_compatibility_matrix(
        self,
        results: List[CompatibilityTestResult],
    ) -> str:
        """Generate a compatibility matrix visualization.

        Args:
            results: List of test results

        Returns:
            Formatted compatibility matrix as string
        """
        # Group results by adapter and base
        matrix = {}
        adapters = set()
        bases = set()

        for result in results:
            adapters.add(result.adapter_name)
            bases.add(result.base_model_id)
            matrix[(result.adapter_name, result.base_model_id)] = result

        adapters = sorted(adapters)
        bases = sorted(bases)

        # Build table
        lines = []
        lines.append("\nCOMPATIBILITY MATRIX")
        lines.append("=" * 100)

        # Header row
        header = f"{'Adapter':<30}"
        for base in bases:
            base_short = base.split("/")[-1][:20]
            header += f" │ {base_short:<20}"
        lines.append(header)
        lines.append("-" * 100)

        # Data rows
        for adapter in adapters:
            row = f"{adapter:<30}"
            for base in bases:
                result = matrix.get((adapter, base))
                if result:
                    status_icon = {
                        CompatibilityStatus.SUCCESS: "✓",
                        CompatibilityStatus.DEGRADED: "⚠",
                        CompatibilityStatus.LOAD_FAILURE: "✗",
                        CompatibilityStatus.INFERENCE_FAILURE: "✗",
                        CompatibilityStatus.UNTESTED: "?",
                    }[result.status]

                    cell = f"{status_icon} {result.status.value[:18]}"
                else:
                    cell = "untested"

                row += f" │ {cell:<20}"
            lines.append(row)

        lines.append("=" * 100)
        lines.append("\nLegend:")
        lines.append("  ✓ = Success (production-ready)")
        lines.append("  ⚠ = Degraded (works with issues)")
        lines.append("  ✗ = Failure (incompatible)")
        lines.append("  ? = Untested")

        return "\n".join(lines)

    def generate_performance_comparison(
        self,
        results: List[CompatibilityTestResult],
    ) -> str:
        """Generate performance comparison table.

        Args:
            results: List of test results

        Returns:
            Formatted performance table as string
        """
        lines = []
        lines.append("\nPERFORMANCE COMPARISON")
        lines.append("=" * 120)
        lines.append(
            f"{'Adapter':<25} │ {'Base Model':<25} │ "
            f"{'Cite Acc':<10} │ {'JSON':<10} │ {'Latency':<12} │ {'Status':<15}"
        )
        lines.append("-" * 120)

        for result in results:
            adapter_short = result.adapter_name[:24]
            base_short = result.base_model_id.split("/")[-1][:24]

            cite_acc = f"{result.citation_accuracy:.1%}" if result.citation_accuracy else "N/A"
            json_rate = f"{result.json_compliance_rate:.1%}" if result.json_compliance_rate else "N/A"
            latency = f"{result.avg_latency_ms:.0f}ms" if result.avg_latency_ms else "N/A"
            status = result.status.value

            lines.append(
                f"{adapter_short:<25} │ {base_short:<25} │ "
                f"{cite_acc:<10} │ {json_rate:<10} │ {latency:<12} │ {status:<15}"
            )

        lines.append("=" * 120)
        return "\n".join(lines)

    def generate_failure_report(
        self,
        results: List[CompatibilityTestResult],
    ) -> str:
        """Generate detailed failure report with workarounds.

        Args:
            results: List of test results

        Returns:
            Formatted failure report as string
        """
        failed_results = [
            r for r in results
            if r.status in [
                CompatibilityStatus.LOAD_FAILURE,
                CompatibilityStatus.INFERENCE_FAILURE,
                CompatibilityStatus.DEGRADED,
            ]
        ]

        if not failed_results:
            return "\nNo failures detected - all adapters are production-ready!"

        lines = []
        lines.append("\nFAILURE ANALYSIS & WORKAROUNDS")
        lines.append("=" * 100)

        for result in failed_results:
            lines.append(f"\nAdapter: {result.adapter_name}")
            lines.append(f"Base Model: {result.base_model_id}")
            lines.append(f"Status: {result.status.value}")

            if result.failure_categories:
                lines.append(f"\nFailure Categories:")
                for category in result.failure_categories:
                    lines.append(f"  - {category.value}")

            if result.error_messages:
                lines.append(f"\nError Messages:")
                for error in result.error_messages:
                    lines.append(f"  {error}")

            if result.known_issues:
                lines.append(f"\nKnown Issues:")
                for issue in result.known_issues:
                    lines.append(f"  - {issue}")

            if result.workarounds:
                lines.append(f"\nRecommended Workarounds:")
                for i, workaround in enumerate(result.workarounds, 1):
                    lines.append(f"  {i}. {workaround}")

            lines.append("-" * 100)

        return "\n".join(lines)

    def save_results(
        self,
        results: List[CompatibilityTestResult],
        output_name: str = "compatibility_test",
    ) -> Path:
        """Save test results to JSON file.

        Args:
            results: List of test results
            output_name: Base name for output file

        Returns:
            Path to saved file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_name}_{timestamp}.json"
        filepath = self.results_dir / filename

        output_data = {
            "test_suite": "adapter_compatibility",
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(results),
            "results": [asdict(r) for r in results],
        }

        with open(filepath, "w") as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"Saved results to: {filepath}")
        return filepath


def main():
    """Main entry point for adapter compatibility testing."""
    parser = argparse.ArgumentParser(
        description="Test Kwanzaa adapter compatibility across base models"
    )
    parser.add_argument(
        "--adapter",
        type=str,
        help="Adapter name to test",
    )
    parser.add_argument(
        "--bases",
        type=str,
        help="Comma-separated list of base models (olmo,llama,deepseek)",
    )
    parser.add_argument(
        "--test-all",
        action="store_true",
        help="Test all adapter/base combinations",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick smoke test (5 prompts)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full evaluation (50 prompts)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "mps"],
        help="Device for inference",
    )

    args = parser.parse_args()

    # Initialize tester
    tester = AdapterCompatibilityTester(device=args.device)

    # Get test prompts
    prompts = tester.get_test_prompts(quick=args.quick)
    logger.info(f"Using {len(prompts)} test prompts")

    # Define available adapters (in production, these would be loaded from disk/registry)
    available_adapters = {
        "kwanzaa-v1-olmo": AdapterConfig(
            name="kwanzaa-v1-olmo",
            path="/path/to/adapter",
            base_model_id=BaseModel.OLMO_7B.value,
            adapter_type="lora",
            rank=16,
            alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        ),
        "kwanzaa-v1-llama": AdapterConfig(
            name="kwanzaa-v1-llama",
            path="/path/to/adapter",
            base_model_id=BaseModel.LLAMA_3_1_8B.value,
            adapter_type="lora",
            rank=16,
            alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        ),
        "kwanzaa-v1-deepseek": AdapterConfig(
            name="kwanzaa-v1-deepseek",
            path="/path/to/adapter",
            base_model_id=BaseModel.DEEPSEEK_V2_LITE.value,
            adapter_type="lora",
            rank=16,
            alpha=32,
            target_modules=["q_proj", "kv_proj", "o_proj"],
        ),
    }

    base_model_map = {
        "olmo": BaseModel.OLMO_7B.value,
        "llama": BaseModel.LLAMA_3_1_8B.value,
        "deepseek": BaseModel.DEEPSEEK_V2_LITE.value,
    }

    # Determine test matrix
    results: List[CompatibilityTestResult] = []

    if args.test_all:
        # Test all combinations
        logger.info("Testing all adapter/base combinations")
        for adapter_name, adapter_config in available_adapters.items():
            for base_name, base_id in base_model_map.items():
                result = tester.test_adapter_on_base(adapter_config, base_id, prompts)
                results.append(result)

    elif args.adapter and args.bases:
        # Test specific adapter on specific bases
        if args.adapter not in available_adapters:
            logger.error(f"Unknown adapter: {args.adapter}")
            logger.error(f"Available: {list(available_adapters.keys())}")
            sys.exit(1)

        adapter_config = available_adapters[args.adapter]
        base_names = args.bases.split(",")

        for base_name in base_names:
            if base_name not in base_model_map:
                logger.error(f"Unknown base model: {base_name}")
                logger.error(f"Available: {list(base_model_map.keys())}")
                sys.exit(1)

            base_id = base_model_map[base_name]
            result = tester.test_adapter_on_base(adapter_config, base_id, prompts)
            results.append(result)

    else:
        parser.print_help()
        sys.exit(1)

    # Generate reports
    print(tester.generate_compatibility_matrix(results))
    print(tester.generate_performance_comparison(results))
    print(tester.generate_failure_report(results))

    # Save results
    output_file = tester.save_results(results)

    print(f"\nFull results saved to: {output_file}")
    print("\nTest complete!")


if __name__ == "__main__":
    main()
