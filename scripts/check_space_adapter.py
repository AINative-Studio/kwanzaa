#!/usr/bin/env python3
"""Check if adapter exists in HuggingFace Space."""

import os
from pathlib import Path
from huggingface_hub import HfApi, list_repo_files

# Load HF_TOKEN from .env file
env_path = Path(__file__).parent.parent / "backend" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    if key == "HF_TOKEN":
                        os.environ["HF_TOKEN"] = value

HF_TOKEN = os.getenv("HF_TOKEN")
SPACE_ID = "ainativestudio/kwanzaa-training"

def main():
    print(f"🔍 Checking HuggingFace Space: {SPACE_ID}\n")

    api = HfApi(token=HF_TOKEN)

    try:
        # List all files in the Space
        files = list(list_repo_files(repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN))

        print(f"📂 Space contains {len(files)} files:\n")

        # Look for adapter-related files
        adapter_files = [f for f in files if "adapter" in f.lower() or "ainative" in f.lower()]

        if adapter_files:
            print("✅ Found adapter-related files:")
            for f in adapter_files:
                print(f"  - {f}")
        else:
            print("❌ No adapter files found in Space")
            print("\n📋 All files in Space:")
            for f in sorted(files):
                print(f"  - {f}")

    except Exception as e:
        print(f"❌ Error accessing Space: {e}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
