#!/usr/bin/env python3
"""
Upload AINative Training Dataset to HuggingFace

Uploads the train and eval datasets to HuggingFace Hub for training.

Issue: #75
Epic: #69
"""

import os
from pathlib import Path
from datasets import load_dataset
from huggingface_hub import HfApi
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Upload AINative dataset to HuggingFace Hub."""
    # Configuration
    dataset_name = "ainative/ainative-platform-training-v1"
    train_file = "data/training/ainative_train.jsonl"
    eval_file = "data/training/ainative_eval.jsonl"

    logger.info("Loading dataset files...")
    logger.info("Train: %s", train_file)
    logger.info("Eval: %s", eval_file)

    # Load dataset
    dataset = load_dataset(
        "json",
        data_files={
            "train": train_file,
            "validation": eval_file
        }
    )

    logger.info("Dataset loaded:")
    logger.info("  Train examples: %d", len(dataset["train"]))
    logger.info("  Eval examples: %d", len(dataset["validation"]))

    # Get HuggingFace token
    token = os.getenv("HF_TOKEN")
    if not token:
        logger.warning("HF_TOKEN not found in environment")
        logger.info("Skipping upload. Set HF_TOKEN to upload to HuggingFace")
        logger.info("Dataset ready for local training")
        return

    # Push to Hub
    logger.info("Uploading to HuggingFace Hub: %s", dataset_name)

    dataset.push_to_hub(
        dataset_name,
        token=token,
        private=False
    )

    logger.info("Upload complete!")
    logger.info("Dataset URL: https://huggingface.co/datasets/%s", dataset_name)


if __name__ == "__main__":
    main()
