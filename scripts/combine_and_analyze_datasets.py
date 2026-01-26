#!/usr/bin/env python3
"""
Combine and Analyze Training Datasets

Combines extracted and hand-crafted examples, analyzes distribution
across 8 categories, and prepares for balanced dataset creation.

Issue: #74
Epic: #69
"""

import json
from pathlib import Path
from collections import Counter
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def load_jsonl(file_path: Path) -> List[Dict]:
    """Load examples from JSONL file."""
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))
    return examples


def save_jsonl(examples: List[Dict], file_path: Path):
    """Save examples to JSONL file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')


def get_category(example: Dict) -> str:
    """Extract category from example metadata or content."""
    # Check metadata first
    metadata = example.get('metadata', {})
    if 'category' in metadata:
        return metadata['category']

    # Infer from content
    messages = example.get('messages', [])
    if not messages:
        return 'unknown'

    content = ' '.join(
        msg.get('content', '').lower()
        for msg in messages
    )

    # Category detection patterns
    if 'swarm' in content or 'multi-agent' in content or 'orchestrat' in content:
        return 'agent_swarm'
    elif 'aikit' in content or 'usechat' in content or 'userag' in content:
        return 'aikit_sdk'
    elif 'zerodb' in content or 'vector' in content or 'embedding' in content:
        return 'zerodb'
    elif 'test' in content or 'pytest' in content:
        return 'tests'
    elif 'openapi' in content or 'endpoint' in content:
        return 'openapi'
    elif 'mcp' in content or 'tool' in content:
        return 'mcp_tools'
    elif 'file placement' in content or 'docs/' in content:
        return 'standards'
    else:
        return 'patterns'


def main():
    """Combine datasets and analyze distribution."""
    # Load datasets
    extracted_path = Path("data/training/ainative_train_extracted.jsonl")
    handcrafted_path = Path("data/training/ainative_train_handcrafted.jsonl")

    logger.info("Loading datasets...")
    extracted = load_jsonl(extracted_path) if extracted_path.exists() else []
    handcrafted = load_jsonl(handcrafted_path) if handcrafted_path.exists() else []

    logger.info("Extracted examples: %d", len(extracted))
    logger.info("Hand-crafted examples: %d", len(handcrafted))

    # Combine
    combined = extracted + handcrafted
    total = len(combined)

    logger.info("Total examples: %d", total)

    # Analyze category distribution
    logger.info("\nAnalyzing category distribution...")
    categories = [get_category(ex) for ex in combined]
    category_counts = Counter(categories)

    # Target distribution for 8 categories
    target_distribution = {
        'zerodb': 35,           # ZeroDB API Usage
        'tests': 35,            # TDD/BDD Test Generation
        'aikit_sdk': 30,        # AIkit SDK & Platform SDKs
        'agent_swarm': 30,      # Agent Swarm Orchestration
        'openapi': 30,          # OpenAPI Spec Integration
        'mcp_tools': 20,        # MCP Server Tools
        'standards': 20,        # File Placement & Standards
        'patterns': 25,         # Common Coding Patterns
    }

    # Print analysis
    print("\n" + "=" * 80)
    print("COMBINED DATASET ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Examples: {total}")
    print(f"Extracted: {len(extracted)}")
    print(f"Hand-crafted: {len(handcrafted)}")

    print("\n" + "-" * 80)
    print("CATEGORY DISTRIBUTION")
    print("-" * 80)
    print(f"{'Category':<25} {'Current':<10} {'Target':<10} {'Gap':<10}")
    print("-" * 80)

    total_gap = 0
    for category, target in sorted(target_distribution.items()):
        current = category_counts.get(category, 0)
        gap = max(0, target - current)
        total_gap += gap
        status = "✅" if gap == 0 else "⚠️" if gap < 10 else "❌"
        print(f"{status} {category:<22} {current:<10} {target:<10} {gap:<10}")

    print("-" * 80)
    print(f"{'TOTAL':<25} {total:<10} {sum(target_distribution.values()):<10} {total_gap:<10}")
    print("=" * 80)

    # Save combined dataset
    combined_path = Path("data/training/ainative_train_combined.jsonl")
    save_jsonl(combined, combined_path)
    logger.info("\nSaved combined dataset to %s", combined_path)

    # Generate category breakdown report
    report_data = {
        "total_examples": total,
        "extracted_count": len(extracted),
        "handcrafted_count": len(handcrafted),
        "category_distribution": dict(category_counts),
        "target_distribution": target_distribution,
        "gaps": {
            category: max(0, target - category_counts.get(category, 0))
            for category, target in target_distribution.items()
        },
        "total_gap": total_gap
    }

    report_path = Path("outputs/dataset_distribution_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

    logger.info("Saved distribution report to %s", report_path)

    print("\n" + "=" * 80)
    if total_gap == 0:
        print("✅ TARGET DISTRIBUTION ACHIEVED")
    elif total_gap < 50:
        print(f"⚠️  CLOSE TO TARGET ({total_gap} examples needed)")
    else:
        print(f"❌ {total_gap} MORE EXAMPLES NEEDED")
    print("=" * 80)


if __name__ == "__main__":
    main()
