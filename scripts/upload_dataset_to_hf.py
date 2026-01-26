#!/usr/bin/env python3
"""
Upload AINative Dataset to HuggingFace Hub

Prepares and uploads the training dataset to HuggingFace Hub.
"""

import os
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_messages_to_text(messages):
    """Convert messages to Llama-3 chat format."""
    text = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "system":
            text += f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
        elif role == "user":
            text += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
        elif role == "assistant":
            text += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"

    return text


def main():
    """Upload dataset to HuggingFace Hub."""
    try:
        from datasets import Dataset, DatasetDict
        from huggingface_hub import HfApi
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.info("Install with: pip install datasets huggingface-hub")
        return 1

    # Load JSONL files
    logger.info("Loading datasets...")

    train_data = []
    eval_data = []

    train_file = Path("data/training/ainative_train.jsonl")
    eval_file = Path("data/training/ainative_eval.jsonl")

    # Load train data
    if train_file.exists():
        with open(train_file, 'r') as f:
            for line in f:
                example = json.loads(line)
                text = format_messages_to_text(example["messages"])
                train_data.append({"text": text})
    else:
        logger.error(f"Train file not found: {train_file}")
        return 1

    # Load eval data
    if eval_file.exists():
        with open(eval_file, 'r') as f:
            for line in f:
                example = json.loads(line)
                text = format_messages_to_text(example["messages"])
                eval_data.append({"text": text})
    else:
        logger.error(f"Eval file not found: {eval_file}")
        return 1

    logger.info(f"Train examples: {len(train_data)}")
    logger.info(f"Eval examples: {len(eval_data)}")

    # Create HuggingFace dataset
    logger.info("Creating dataset...")

    dataset = DatasetDict({
        "train": Dataset.from_list(train_data),
        "validation": Dataset.from_list(eval_data)
    })

    logger.info(f"Dataset created:")
    logger.info(f"  train: {len(dataset['train'])} examples")
    logger.info(f"  validation: {len(dataset['validation'])} examples")

    # Get HuggingFace token
    token = os.getenv("HF_TOKEN")
    if not token:
        logger.warning("HF_TOKEN not found in environment")
        logger.info("Set HF_TOKEN environment variable to upload")
        logger.info("Dataset prepared but not uploaded")

        # Save locally for manual upload
        dataset.save_to_disk("outputs/ainative_dataset")
        logger.info("Dataset saved to: outputs/ainative_dataset")
        return 0

    # Upload to Hub
    repo_name = "ainativestudio/ainative-training-v1"
    logger.info(f"Uploading to HuggingFace Hub: {repo_name}")

    try:
        dataset.push_to_hub(
            repo_name,
            token=token,
            private=False
        )
        logger.info("✅ Upload complete!")
        logger.info(f"Dataset URL: https://huggingface.co/datasets/{repo_name}")

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        logger.info("Saving dataset locally instead...")
        dataset.save_to_disk("outputs/ainative_dataset")
        logger.info("Dataset saved to: outputs/ainative_dataset")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
