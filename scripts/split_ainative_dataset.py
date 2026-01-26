#!/usr/bin/env python3
"""
Split AINative Training Dataset

Splits the combined dataset into train (90%) and eval (10%) sets
following the same workflow as Kwanzaa adapter training.

Issue: #75
Epic: #69
"""

import json
import random
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Set seed for reproducibility
random.seed(42)


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


def main():
    """Split dataset into train/eval sets."""
    # Load combined dataset
    input_path = Path("data/training/ainative_train_combined.jsonl")

    logger.info("Loading combined dataset from %s", input_path)
    examples = load_jsonl(input_path)
    total = len(examples)

    logger.info("Total examples: %d", total)

    # Shuffle examples
    random.shuffle(examples)

    # Calculate split point (90/10)
    split_point = int(total * 0.9)

    train_examples = examples[:split_point]
    eval_examples = examples[split_point:]

    logger.info("Train examples: %d (%.1f%%)", len(train_examples),
                len(train_examples) / total * 100)
    logger.info("Eval examples: %d (%.1f%%)", len(eval_examples),
                len(eval_examples) / total * 100)

    # Save splits
    train_path = Path("data/training/ainative_train.jsonl")
    eval_path = Path("data/training/ainative_eval.jsonl")

    save_jsonl(train_examples, train_path)
    save_jsonl(eval_examples, eval_path)

    logger.info("Saved train set to %s", train_path)
    logger.info("Saved eval set to %s", eval_path)

    print("\n" + "=" * 70)
    print("DATASET SPLIT COMPLETE")
    print("=" * 70)
    print(f"Total examples: {total}")
    print(f"Train: {len(train_examples)} ({len(train_examples)/total*100:.1f}%)")
    print(f"Eval:  {len(eval_examples)} ({len(eval_examples)/total*100:.1f}%)")
    print("=" * 70)


if __name__ == "__main__":
    main()
