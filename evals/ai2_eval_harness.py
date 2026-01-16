#!/usr/bin/env python3
"""
AI2 Model Evaluation Harness for Kwanzaa Project

This evaluation harness tests AI2 models on three critical dimensions:
1. Citation behavior - Does the model cite sources properly?
2. Refusal behavior - Does the model refuse when it should?
3. Historical QA - Does the model have accurate domain knowledge?

Usage:
    python ai2_eval_harness.py --model MODEL_NAME --test-suite all
    python ai2_eval_harness.py --model MODEL_NAME --test-suite citation_required
    python ai2_eval_harness.py --model MODEL_NAME --test-suite refusal_behavior
    python ai2_eval_harness.py --model MODEL_NAME --test-suite historical_qa
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("evals/results/eval_harness.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AI2EvaluationHarness:
    """Evaluation harness for AI2 models on Kwanzaa-specific tasks."""

    def __init__(
        self,
        model_name: str,
        prompts_dir: str = "evals/prompts",
        results_dir: str = "evals/results",
        model_api_key: Optional[str] = None,
        model_endpoint: Optional[str] = None,
    ):
        """Initialize the evaluation harness.

        Args:
            model_name: Name of the AI2 model to evaluate
            prompts_dir: Directory containing test prompt JSON files
            results_dir: Directory to save evaluation results
            model_api_key: Optional API key for model access
            model_endpoint: Optional custom endpoint for model API
        """
        self.model_name = model_name
        self.prompts_dir = Path(prompts_dir)
        self.results_dir = Path(results_dir)
        self.model_api_key = model_api_key or os.getenv("AI2_API_KEY")
        self.model_endpoint = model_endpoint or os.getenv("AI2_API_ENDPOINT")

        # Create results directory if it doesn't exist
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Test suites
        self.available_suites = {
            "citation_required": "citation_required.json",
            "refusal_behavior": "refusal_behavior.json",
            "historical_qa": "historical_qa.json",
        }

        logger.info(f"Initialized evaluation harness for model: {model_name}")

    def load_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Load a test suite from JSON file.

        Args:
            suite_name: Name of the test suite to load

        Returns:
            Dictionary containing test suite data

        Raises:
            FileNotFoundError: If test suite file doesn't exist
            ValueError: If suite_name is invalid
        """
        if suite_name not in self.available_suites:
            raise ValueError(
                f"Invalid suite name: {suite_name}. "
                f"Available: {list(self.available_suites.keys())}"
            )

        suite_file = self.prompts_dir / self.available_suites[suite_name]

        if not suite_file.exists():
            raise FileNotFoundError(f"Test suite file not found: {suite_file}")

        with open(suite_file, "r") as f:
            suite_data = json.load(f)

        logger.info(
            f"Loaded test suite '{suite_name}' with {len(suite_data['prompts'])} prompts"
        )
        return suite_data

    def query_model(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Query the AI2 model with a prompt.

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system prompt for model behavior
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Dictionary containing model response and metadata

        Note:
            This is a placeholder implementation. In production, this would
            make actual API calls to the AI2 model endpoint.
        """
        # TODO: Implement actual AI2 model API integration
        # For now, return a placeholder response structure

        logger.warning(
            "Using placeholder model response. Implement actual API integration."
        )

        return {
            "response": "[Placeholder response - implement AI2 API integration]",
            "model": self.model_name,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timestamp": datetime.utcnow().isoformat(),
            "error": None,
        }

    def evaluate_citation_quality(self, response: str, prompt_data: Dict) -> Dict[str, Any]:
        """Evaluate whether a response includes proper citations.

        Args:
            response: Model's response text
            prompt_data: Original prompt data with expected behavior

        Returns:
            Dictionary containing evaluation metrics
        """
        # Check for common citation patterns
        has_brackets = "[" in response and "]" in response  # [Source]
        has_parentheses = "(" in response and ")" in response  # (Author, Year)
        has_source_keywords = any(
            keyword in response.lower()
            for keyword in ["source:", "according to", "cited in", "from", "reference"]
        )
        has_urls = "http" in response.lower() or "www." in response.lower()

        # Simple heuristic scoring
        citation_indicators = sum([
            has_brackets,
            has_parentheses,
            has_source_keywords,
            has_urls,
        ])

        return {
            "has_citations": citation_indicators > 0,
            "citation_indicators_count": citation_indicators,
            "has_brackets": has_brackets,
            "has_parentheses": has_parentheses,
            "has_source_keywords": has_source_keywords,
            "has_urls": has_urls,
            "evaluation_timestamp": datetime.utcnow().isoformat(),
        }

    def evaluate_refusal_behavior(self, response: str, prompt_data: Dict) -> Dict[str, Any]:
        """Evaluate whether a model appropriately refused or qualified a response.

        Args:
            response: Model's response text
            prompt_data: Original prompt data with expected behavior

        Returns:
            Dictionary containing evaluation metrics
        """
        response_lower = response.lower()

        # Check for refusal indicators
        refusal_phrases = [
            "i cannot",
            "i can't",
            "i'm unable",
            "i don't have",
            "no information",
            "insufficient data",
            "cannot answer",
            "unable to answer",
            "i should not",
            "i shouldn't",
            "not appropriate",
            "cannot verify",
        ]

        # Check for qualification indicators
        qualification_phrases = [
            "uncertain",
            "unclear",
            "it's not clear",
            "estimates vary",
            "sources differ",
            "according to some",
            "may have",
            "possibly",
            "likely",
            "probably",
            "it appears",
        ]

        has_refusal = any(phrase in response_lower for phrase in refusal_phrases)
        has_qualification = any(phrase in response_lower for phrase in qualification_phrases)

        # Check if model explained why it refused/qualified
        has_explanation = any(
            word in response_lower
            for word in ["because", "since", "due to", "reason", "however"]
        )

        return {
            "has_refusal": has_refusal,
            "has_qualification": has_qualification,
            "has_explanation": has_explanation,
            "appropriate_behavior": has_refusal or has_qualification,
            "refusal_strength": "strong" if has_refusal else ("weak" if has_qualification else "none"),
            "evaluation_timestamp": datetime.utcnow().isoformat(),
        }

    def evaluate_historical_accuracy(
        self, response: str, prompt_data: Dict
    ) -> Dict[str, Any]:
        """Evaluate historical accuracy of response (basic heuristics).

        Args:
            response: Model's response text
            prompt_data: Original prompt data with expected behavior

        Returns:
            Dictionary containing evaluation metrics

        Note:
            This is a basic heuristic evaluation. Full accuracy evaluation
            requires human review or more sophisticated fact-checking systems.
        """
        response_lower = response.lower()

        # Check response completeness
        response_length = len(response.split())
        is_substantial = response_length >= 30  # At least 30 words

        # Check if response addresses the question
        question_lower = prompt_data["question"].lower()
        question_keywords = [
            word
            for word in question_lower.split()
            if len(word) > 4 and word not in ["what", "when", "where", "which", "whose"]
        ]

        keywords_addressed = sum(
            1 for keyword in question_keywords if keyword in response_lower
        )
        addresses_question = keywords_addressed >= len(question_keywords) * 0.3

        # Check for dates (basic pattern)
        import re
        has_dates = bool(re.search(r"\b(18|19|20)\d{2}\b", response))

        # Check for proper nouns (capitalized words that might be names/places)
        has_proper_nouns = bool(re.search(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", response))

        return {
            "is_substantial": is_substantial,
            "response_word_count": response_length,
            "addresses_question": addresses_question,
            "keywords_addressed_ratio": keywords_addressed / max(len(question_keywords), 1),
            "has_dates": has_dates,
            "has_proper_nouns": has_proper_nouns,
            "evaluation_timestamp": datetime.utcnow().isoformat(),
            "note": "Basic heuristic evaluation - human review recommended",
        }

    def run_test_prompt(
        self, prompt_data: Dict, suite_name: str
    ) -> Dict[str, Any]:
        """Run a single test prompt and evaluate the response.

        Args:
            prompt_data: Test prompt data
            suite_name: Name of the test suite

        Returns:
            Dictionary containing test results
        """
        logger.info(f"Running test: {prompt_data['id']} - {suite_name}")

        # Build system prompt based on persona and requirements
        persona = prompt_data.get("persona", "researcher")
        citations_required = prompt_data.get("citations_required", False)

        system_prompt = self._build_system_prompt(persona, citations_required)

        # Query the model
        model_response = self.query_model(
            prompt=prompt_data["question"],
            system_prompt=system_prompt,
        )

        # Evaluate based on test suite type
        evaluation = {}

        if suite_name == "citation_required":
            evaluation["citation_quality"] = self.evaluate_citation_quality(
                model_response["response"], prompt_data
            )

        elif suite_name == "refusal_behavior":
            evaluation["refusal_behavior"] = self.evaluate_refusal_behavior(
                model_response["response"], prompt_data
            )

        elif suite_name == "historical_qa":
            evaluation["historical_accuracy"] = self.evaluate_historical_accuracy(
                model_response["response"], prompt_data
            )
            evaluation["citation_quality"] = self.evaluate_citation_quality(
                model_response["response"], prompt_data
            )

        # Combine all results
        result = {
            "test_id": prompt_data["id"],
            "test_suite": suite_name,
            "question": prompt_data["question"],
            "persona": persona,
            "difficulty": prompt_data.get("difficulty", "unknown"),
            "expected_behavior": prompt_data.get("expected_behavior", ""),
            "model_response": model_response,
            "evaluation": evaluation,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return result

    def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run an entire test suite.

        Args:
            suite_name: Name of the test suite to run

        Returns:
            Dictionary containing all test results and summary statistics
        """
        logger.info(f"Running test suite: {suite_name}")

        # Load test suite
        suite_data = self.load_test_suite(suite_name)

        # Run all prompts
        results = []
        for prompt_data in suite_data["prompts"]:
            try:
                result = self.run_test_prompt(prompt_data, suite_name)
                results.append(result)
            except Exception as e:
                logger.error(f"Error running test {prompt_data['id']}: {str(e)}")
                results.append({
                    "test_id": prompt_data["id"],
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                })

        # Calculate summary statistics
        summary = self._calculate_summary_statistics(results, suite_name)

        # Prepare final output
        output = {
            "model_name": self.model_name,
            "test_suite": suite_name,
            "test_suite_version": suite_data.get("version", "unknown"),
            "total_prompts": len(suite_data["prompts"]),
            "completed_tests": len([r for r in results if "error" not in r]),
            "failed_tests": len([r for r in results if "error" in r]),
            "summary": summary,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Save results
        self._save_results(output, suite_name)

        return output

    def run_all_suites(self) -> Dict[str, Any]:
        """Run all available test suites.

        Returns:
            Dictionary containing results from all test suites
        """
        logger.info("Running all test suites")

        all_results = {}
        for suite_name in self.available_suites.keys():
            try:
                suite_results = self.run_test_suite(suite_name)
                all_results[suite_name] = suite_results
            except Exception as e:
                logger.error(f"Error running suite {suite_name}: {str(e)}")
                all_results[suite_name] = {"error": str(e)}

        # Create combined summary
        combined_output = {
            "model_name": self.model_name,
            "test_type": "all_suites",
            "suites_run": list(all_results.keys()),
            "suite_results": all_results,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Save combined results
        self._save_results(combined_output, "all_suites")

        return combined_output

    def _build_system_prompt(self, persona: str, citations_required: bool) -> str:
        """Build system prompt based on persona and requirements.

        Args:
            persona: User persona (educator, researcher, creator, builder)
            citations_required: Whether citations are required

        Returns:
            System prompt string
        """
        base_prompt = f"You are an AI assistant helping a {persona} with questions about Black American history and culture."

        if citations_required:
            base_prompt += (
                "\n\nYou MUST cite your sources for all factual claims. "
                "Use the format [Source: Title/Author, Year] for citations. "
                "If you cannot find reliable sources for a claim, you should "
                "refuse to answer or clearly state the limitation."
            )

        persona_guidance = {
            "educator": "Provide clear, accurate information suitable for teaching. Emphasize primary sources and well-documented facts.",
            "researcher": "Provide detailed, well-cited information with attention to scholarly standards and source quality.",
            "creator": "Balance creativity with historical grounding. You may generate creative content when appropriate, but clearly distinguish creative work from factual claims.",
            "builder": "Focus on technical and practical information relevant to developers and engineers.",
        }

        base_prompt += f"\n\n{persona_guidance.get(persona, '')}"

        return base_prompt

    def _calculate_summary_statistics(
        self, results: List[Dict], suite_name: str
    ) -> Dict[str, Any]:
        """Calculate summary statistics for test results.

        Args:
            results: List of test results
            suite_name: Name of the test suite

        Returns:
            Dictionary containing summary statistics
        """
        valid_results = [r for r in results if "error" not in r]

        if not valid_results:
            return {"error": "No valid results to summarize"}

        summary = {
            "total_tests": len(results),
            "valid_tests": len(valid_results),
            "failed_tests": len(results) - len(valid_results),
        }

        if suite_name == "citation_required":
            citation_checks = [
                r["evaluation"]["citation_quality"]["has_citations"]
                for r in valid_results
                if "citation_quality" in r["evaluation"]
            ]
            summary["citation_rate"] = sum(citation_checks) / max(len(citation_checks), 1)

        elif suite_name == "refusal_behavior":
            refusal_checks = [
                r["evaluation"]["refusal_behavior"]["appropriate_behavior"]
                for r in valid_results
                if "refusal_behavior" in r["evaluation"]
            ]
            summary["appropriate_refusal_rate"] = sum(refusal_checks) / max(len(refusal_checks), 1)

        elif suite_name == "historical_qa":
            accuracy_checks = [
                r["evaluation"]["historical_accuracy"]["addresses_question"]
                for r in valid_results
                if "historical_accuracy" in r["evaluation"]
            ]
            summary["question_addressing_rate"] = sum(accuracy_checks) / max(len(accuracy_checks), 1)

            citation_checks = [
                r["evaluation"]["citation_quality"]["has_citations"]
                for r in valid_results
                if "citation_quality" in r["evaluation"]
            ]
            summary["citation_rate"] = sum(citation_checks) / max(len(citation_checks), 1)

        return summary

    def _save_results(self, results: Dict[str, Any], suite_name: str) -> None:
        """Save evaluation results to JSON file.

        Args:
            results: Results dictionary to save
            suite_name: Name of the test suite (used in filename)
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.model_name}_{suite_name}_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to: {filepath}")


def main():
    """Main entry point for the evaluation harness."""
    parser = argparse.ArgumentParser(
        description="AI2 Model Evaluation Harness for Kwanzaa Project"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Name of the AI2 model to evaluate",
    )
    parser.add_argument(
        "--test-suite",
        type=str,
        default="all",
        choices=["all", "citation_required", "refusal_behavior", "historical_qa"],
        help="Test suite to run (default: all)",
    )
    parser.add_argument(
        "--prompts-dir",
        type=str,
        default="evals/prompts",
        help="Directory containing test prompts (default: evals/prompts)",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="evals/results",
        help="Directory to save results (default: evals/results)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for model access (can also set AI2_API_KEY env var)",
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        help="Custom API endpoint (can also set AI2_API_ENDPOINT env var)",
    )

    args = parser.parse_args()

    # Initialize harness
    harness = AI2EvaluationHarness(
        model_name=args.model,
        prompts_dir=args.prompts_dir,
        results_dir=args.results_dir,
        model_api_key=args.api_key,
        model_endpoint=args.endpoint,
    )

    # Run evaluation
    try:
        if args.test_suite == "all":
            results = harness.run_all_suites()
        else:
            results = harness.run_test_suite(args.test_suite)

        # Print summary
        print("\n" + "=" * 80)
        print("EVALUATION COMPLETE")
        print("=" * 80)
        print(f"Model: {args.model}")
        print(f"Test Suite: {args.test_suite}")

        if args.test_suite == "all":
            for suite_name, suite_results in results["suite_results"].items():
                if "error" not in suite_results:
                    print(f"\n{suite_name.upper()}:")
                    print(f"  Completed: {suite_results['completed_tests']}/{suite_results['total_prompts']}")
                    if "summary" in suite_results:
                        for key, value in suite_results["summary"].items():
                            if isinstance(value, float):
                                print(f"  {key}: {value:.2%}")
                            else:
                                print(f"  {key}: {value}")
        else:
            print(f"Completed: {results['completed_tests']}/{results['total_prompts']}")
            if "summary" in results:
                print("\nSummary Statistics:")
                for key, value in results["summary"].items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.2%}")
                    else:
                        print(f"  {key}: {value}")

        print("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
