#!/usr/bin/env python3
"""
List all files in the HuggingFace training Space.
"""

import os
from pathlib import Path
from huggingface_hub import HfApi
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

HF_TOKEN = os.getenv("HF_TOKEN")
HF_TRAINING_SPACE = os.getenv("HF_TRAINING_SPACE", "https://huggingface.co/spaces/ainativestudio/kwanzaa-training")

# Extract space ID from URL
space_id = HF_TRAINING_SPACE.replace("https://huggingface.co/spaces/", "")

def main():
    """List all files in the Space."""

    print(f"📋 Listing all files in Space: {space_id}\n")

    try:
        api = HfApi(token=HF_TOKEN)
        files = api.list_repo_files(repo_id=space_id, repo_type="space")

        print(f"Total files: {len(files)}\n")

        for i, file in enumerate(files, 1):
            print(f"{i:3d}. {file}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
