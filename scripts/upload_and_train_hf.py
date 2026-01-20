#!/usr/bin/env python3
"""
Upload data to HF and start training - fully automated
"""

from huggingface_hub import HfApi, create_repo, upload_file
import os

HF_TOKEN = os.environ.get("HF_TOKEN", "your-huggingface-token-here")
USERNAME = "ainativestudio"
DATASET_NAME = f"{USERNAME}/kwanzaa-training-data"

api = HfApi(token=HF_TOKEN)

print("="*60)
print("Uploading training data to HuggingFace Hub")
print("="*60)

# Create dataset repo
print("\n1. Creating dataset repository...")
try:
    create_repo(
        repo_id=DATASET_NAME,
        repo_type="dataset",
        token=HF_TOKEN,
        exist_ok=True
    )
    print(f"   ✓ Repository created: {DATASET_NAME}")
except Exception as e:
    print(f"   Note: {e}")

# Upload training files
print("\n2. Uploading training files...")
files_to_upload = [
    ("data/training/kwanzaa_train.jsonl", "kwanzaa_train.jsonl"),
    ("data/training/kwanzaa_eval.jsonl", "kwanzaa_eval.jsonl"),
]

for local_path, remote_name in files_to_upload:
    print(f"   Uploading {remote_name}...")
    api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=remote_name,
        repo_id=DATASET_NAME,
        repo_type="dataset",
        token=HF_TOKEN,
    )
    print(f"   ✓ {remote_name} uploaded")

print("\n" + "="*60)
print("SUCCESS! Data uploaded to:")
print(f"https://huggingface.co/datasets/{DATASET_NAME}")
print("="*60)

print("\n" + "="*60)
print("Now starting training...")
print("="*60)

# Now run training
print("\nInstalling training dependencies...")
os.system("pip install -q transformers datasets peft bitsandbytes trl accelerate")

print("\nStarting training script...")
os.system("python scripts/train_hf_direct.py")
