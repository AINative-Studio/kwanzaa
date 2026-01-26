#!/usr/bin/env python3
"""
Check for AINative adapter model repository on HuggingFace Hub.
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, list_models
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

HF_TOKEN = os.getenv("HF_TOKEN")

def main():
    """Check for adapter model repositories."""

    print("🔍 Checking for AINative adapter repositories on HuggingFace Hub\n")

    try:
        api = HfApi(token=HF_TOKEN)

        # Search for adapter repositories
        possible_names = [
            "ainativestudio/ainative-adapter-v1",
            "ainativestudio/ainative-adapter",
            "ainativestudio/kwanzaa-training",
        ]

        print("Checking possible adapter repositories:\n")

        for repo_name in possible_names:
            try:
                info = api.repo_info(repo_id=repo_name, repo_type="model")
                print(f"✅ Found: {repo_name}")
                print(f"   Author: {info.author}")
                print(f"   Last modified: {info.lastModified}")
                print(f"   Downloads: {info.downloads}")
                print()

                # List files
                files = api.list_repo_files(repo_id=repo_name, repo_type="model")
                print(f"   Files ({len(files)}):")
                for f in files[:20]:  # Show first 20
                    print(f"   - {f}")
                if len(files) > 20:
                    print(f"   ... and {len(files) - 20} more")
                print()

            except Exception as e:
                print(f"❌ Not found: {repo_name}")
                print(f"   Error: {str(e)[:100]}")
                print()

        # Search for all ainativestudio models
        print("\n📋 All models from ainativestudio:\n")
        models = list(list_models(author="ainativestudio", token=HF_TOKEN))

        if models:
            for model in models:
                print(f"  - {model.id}")
        else:
            print("  No models found")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
