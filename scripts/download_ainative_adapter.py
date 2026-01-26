#!/usr/bin/env python3
"""
Download AINative adapter from HuggingFace Space.

This script downloads the trained AINative adapter (Llama-3.2-1B + QLoRA)
from the HuggingFace Space training environment.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

HF_TOKEN = os.getenv("HF_TOKEN")
HF_TRAINING_SPACE = os.getenv("HF_TRAINING_SPACE", "https://huggingface.co/spaces/ainativestudio/kwanzaa-training")

# Extract space ID from URL
space_id = HF_TRAINING_SPACE.replace("https://huggingface.co/spaces/", "")

# Download configuration
ADAPTER_NAME = "ainative-adapter-v1"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "adapters" / "ainative-v1"

def main():
    """Download the trained adapter from HuggingFace Space."""

    print(f"🚀 Downloading AINative adapter from HuggingFace Space")
    print(f"   Space: {space_id}")
    print(f"   Adapter: {ADAPTER_NAME}")
    print(f"   Output: {OUTPUT_DIR}")
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Initialize HuggingFace API
        api = HfApi(token=HF_TOKEN)

        # List files in the Space to find the adapter
        print("📋 Listing files in Space...")
        try:
            files = api.list_repo_files(repo_id=space_id, repo_type="space")
            adapter_files = [f for f in files if ADAPTER_NAME in f]

            print(f"   Found {len(adapter_files)} adapter files:")
            for f in adapter_files[:10]:  # Show first 10
                print(f"   - {f}")
            if len(adapter_files) > 10:
                print(f"   ... and {len(adapter_files) - 10} more")
            print()
        except Exception as e:
            print(f"⚠️  Could not list files: {e}")
            print("   Proceeding with download attempt...")
            print()

        # Download adapter files
        print(f"⬇️  Downloading adapter to {OUTPUT_DIR}...")

        # Download all files matching the adapter name
        downloaded_path = snapshot_download(
            repo_id=space_id,
            repo_type="space",
            allow_patterns=f"{ADAPTER_NAME}/**",
            local_dir=OUTPUT_DIR.parent,
            token=HF_TOKEN,
            resume_download=True
        )

        print(f"✅ Download complete!")
        print(f"   Location: {downloaded_path}")
        print()

        # Verify downloaded files
        adapter_path = OUTPUT_DIR.parent / ADAPTER_NAME
        if adapter_path.exists():
            files = list(adapter_path.rglob("*"))
            print(f"📦 Downloaded {len(files)} files:")

            # Check for key adapter files
            key_files = {
                "adapter_config.json": False,
                "adapter_model.safetensors": False,
                "adapter_model.bin": False
            }

            for file in files:
                if file.is_file():
                    print(f"   - {file.relative_to(adapter_path)}")
                    for key_file in key_files:
                        if file.name == key_file:
                            key_files[key_file] = True

            print()
            print("🔍 Adapter file validation:")
            for key_file, found in key_files.items():
                status = "✅" if found else "⚠️"
                print(f"   {status} {key_file}: {'Found' if found else 'Missing'}")

            if any(key_files.values()):
                print()
                print("✅ Adapter successfully downloaded and validated!")
                return 0
            else:
                print()
                print("⚠️  No adapter files found. The adapter may not be in the expected location.")
                print("   Check the Space files tab to verify the adapter path.")
                return 1
        else:
            print(f"⚠️  Adapter directory not found: {adapter_path}")
            print("   The training may have used a different output directory.")
            return 1

    except Exception as e:
        print(f"❌ Download failed: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Verify HF_TOKEN in backend/.env is valid")
        print("   2. Check Space URL in backend/.env (HF_TRAINING_SPACE)")
        print("   3. Ensure adapter files exist in the Space")
        print("   4. Visit Space directly: " + HF_TRAINING_SPACE)
        return 1

if __name__ == "__main__":
    sys.exit(main())
