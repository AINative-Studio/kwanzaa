#!/usr/bin/env python3
import os
from huggingface_hub import HfApi

api = HfApi()
HF_TOKEN = os.getenv("HF_TOKEN")  # Load from environment variable

# Upload files
api.upload_file(
    path_or_fileobj="data/training/kwanzaa_train.jsonl",
    path_in_repo="train.jsonl",
    repo_id="ainativestudio/kwanzaa-training-data",
    repo_type="dataset",
    token=HF_TOKEN
)

api.upload_file(
    path_or_fileobj="data/training/kwanzaa_eval.jsonl",
    path_in_repo="test.jsonl",
    repo_id="ainativestudio/kwanzaa-training-data",
    repo_type="dataset",
    token=HF_TOKEN
)

print("✓ Uploaded training data to HuggingFace Hub")
print(f"  - train.jsonl: 142 samples")
print(f"  - test.jsonl: 36 samples")
print(f"  - Total: 178 samples")
