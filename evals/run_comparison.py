#!/usr/bin/env python3
"""Quick script to run model comparisons.

Usage:
    python evals/run_comparison.py --baseline baseline --alternative llama2_7b
    python evals/run_comparison.py --preset full_comparison
    python evals/run_comparison.py --list-models
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evals.alternative_models_eval import (
    AlternativeModelEvaluator,
    ModelConfig,
    ModelProvider,
    ModelType,
)


def load_model_configs() -> dict:
    """Load model configurations from JSON file."""
    config_path = Path(__file__).parent / "model_configs.json"

    with open(config_path, "r") as f:
        return json.load(f)


def create_model_config(config_dict: dict) -> ModelConfig:
    """Create ModelConfig from dictionary."""
    return ModelConfig(
        name=config_dict["name"],
        provider=ModelProvider(config_dict["provider"]),
        model_type=ModelType(config_dict["model_type"]),
        model_id=config_dict["model_id"],
        embedding_dimensions=config_dict.get("embedding_dimensions", 1536),
        device=config_dict.get("device", "cpu"),
        quantization=config_dict.get("quantization"),
    )


def list_available_models():
    """List all available model configurations."""
    configs = load_model_configs()

    print("\n" + "=" * 80)
    print("AVAILABLE MODELS")
    print("=" * 80)

    for model_id, config in configs["models"].items():
        print(f"\nModel ID: {model_id}")
        print(f"  Name: {config['name']}")
        print(f"  Provider: {config['provider']}")
        print(f"  Model Type: {config['model_type']}")
        print(f"  Model ID: {config['model_id']}")
        print(f"  Description: {config['description']}")

    print("\n" + "=" * 80)
    print("EVALUATION PRESETS")
    print("=" * 80)

    for preset_id, preset in configs["evaluation_presets"].items():
        print(f"\nPreset ID: {preset_id}")
        print(f"  Description: {preset['description']}")
        print(f"  Models: {', '.join(preset['models'])}")
        print(f"  Prompt Count: {preset['prompt_count']}")

    print("\n" + "=" * 80)


async def run_comparison(baseline_id: str, alternative_id: str):
    """Run comparison between two models."""
    configs = load_model_configs()

    # Get model configs
    if baseline_id not in configs["models"]:
        print(f"Error: Baseline model '{baseline_id}' not found")
        list_available_models()
        sys.exit(1)

    if alternative_id not in configs["models"]:
        print(f"Error: Alternative model '{alternative_id}' not found")
        list_available_models()
        sys.exit(1)

    baseline_config = create_model_config(configs["models"][baseline_id])
    alternative_config = create_model_config(configs["models"][alternative_id])

    # Create evaluator
    evaluator = AlternativeModelEvaluator(baseline_config=baseline_config)

    # Run comparison
    print(f"\nComparing {baseline_id} vs {alternative_id}...")
    report = await evaluator.compare_models(
        baseline_config=baseline_config,
        alternative_config=alternative_config,
    )

    # Print report
    evaluator.print_report(report)


async def run_preset(preset_id: str):
    """Run a preset evaluation configuration."""
    configs = load_model_configs()

    if preset_id not in configs["evaluation_presets"]:
        print(f"Error: Preset '{preset_id}' not found")
        list_available_models()
        sys.exit(1)

    preset = configs["evaluation_presets"][preset_id]
    models = preset["models"]

    if len(models) < 2:
        print(f"Error: Preset must have at least 2 models")
        sys.exit(1)

    baseline_id = models[0]
    baseline_config = create_model_config(configs["models"][baseline_id])

    # Run comparisons for all alternative models
    for alternative_id in models[1:]:
        alternative_config = create_model_config(configs["models"][alternative_id])

        evaluator = AlternativeModelEvaluator(baseline_config=baseline_config)

        print(f"\n{'=' * 80}")
        print(f"Comparing {baseline_id} vs {alternative_id}")
        print(f"{'=' * 80}\n")

        report = await evaluator.compare_models(
            baseline_config=baseline_config,
            alternative_config=alternative_config,
        )

        evaluator.print_report(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run model comparison evaluations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare baseline with LLaMA 2
  python evals/run_comparison.py --baseline baseline --alternative llama2_7b

  # Run full comparison preset
  python evals/run_comparison.py --preset full_comparison

  # List available models and presets
  python evals/run_comparison.py --list-models
        """,
    )

    parser.add_argument(
        "--baseline",
        type=str,
        help="Baseline model ID (from model_configs.json)",
    )

    parser.add_argument(
        "--alternative",
        type=str,
        help="Alternative model ID (from model_configs.json)",
    )

    parser.add_argument(
        "--preset",
        type=str,
        help="Evaluation preset ID (from model_configs.json)",
    )

    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List all available models and presets",
    )

    args = parser.parse_args()

    # Handle list models
    if args.list_models:
        list_available_models()
        return

    # Handle preset
    if args.preset:
        asyncio.run(run_preset(args.preset))
        return

    # Handle direct comparison
    if args.baseline and args.alternative:
        asyncio.run(run_comparison(args.baseline, args.alternative))
        return

    # No valid arguments
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
