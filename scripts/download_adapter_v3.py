#!/usr/bin/env python3
"""
Download trained adapter v3 from HuggingFace Hub
"""
import os
from huggingface_hub import snapshot_download

HF_TOKEN = os.getenv("HF_TOKEN")  # Load from environment variable
REPO_ID = "ainativestudio/kwanzaa-adapter-v3"
LOCAL_DIR = "backend/models/adapters/kwanzaa-adapter-v3"

print("=" * 60)
print("Downloading kwanzaa-adapter-v3 from HuggingFace Hub")
print("=" * 60)

print(f"\nRepo: {REPO_ID}")
print(f"Local dir: {LOCAL_DIR}")

# Create directory if it doesn't exist
os.makedirs(LOCAL_DIR, exist_ok=True)

print("\nDownloading...")
snapshot_download(
    repo_id=REPO_ID,
    local_dir=LOCAL_DIR,
    token=HF_TOKEN
)

print("\n✓ Download complete!")
print(f"\nFiles in {LOCAL_DIR}:")
for f in os.listdir(LOCAL_DIR):
    fpath = os.path.join(LOCAL_DIR, f)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath) / (1024 * 1024)
        print(f"  - {f} ({size:.2f} MB)")

print("\n" + "=" * 60)
print("SUCCESS! Adapter v3 ready for use")
print("=" * 60)
