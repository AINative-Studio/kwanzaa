#!/usr/bin/env python3
"""
Download AINative adapter from HuggingFace Hub model repository.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_REPO = "ainativestudio/ainative-adapter-v1"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "adapters" / "ainative-v1"

def main():
    """Download adapter from HuggingFace Hub."""

    print(f"🚀 Downloading AINative adapter from HuggingFace Hub")
    print(f"   Repository: {MODEL_REPO}")
    print(f"   Output: {OUTPUT_DIR}")
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Download adapter
        print(f"⬇️  Downloading adapter files...")
        downloaded_path = snapshot_download(
            repo_id=MODEL_REPO,
            repo_type="model",
            local_dir=OUTPUT_DIR,
            token=HF_TOKEN,
            resume_download=True
        )

        print(f"✅ Download complete!")
        print(f"   Location: {downloaded_path}")
        print()

        # List downloaded files
        files = list(OUTPUT_DIR.rglob("*"))
        file_count = sum(1 for f in files if f.is_file())

        print(f"📦 Downloaded {file_count} files:")

        # Check for key files
        key_files = {
            "adapter_config.json": OUTPUT_DIR / "adapter_config.json",
            "adapter_model.safetensors": OUTPUT_DIR / "adapter_model.safetensors",
            "adapter_model.bin": OUTPUT_DIR / "adapter_model.bin"
        }

        found_files = []
        for name, path in key_files.items():
            if path.exists():
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"   ✅ {name} ({size_mb:.2f} MB)")
                found_files.append(name)
            elif "adapter_model" in name:
                continue  # Skip if other format exists
            else:
                print(f"   ⚠️  {name} - Not found")

        print()

        if "adapter_config.json" in found_files and \
           ("adapter_model.safetensors" in found_files or "adapter_model.bin" in found_files):
            print("✅ Adapter successfully downloaded and validated!")
            print()
            print("Next step: Run validation")
            print("   source backend/.venv/bin/activate")
            print("   python scripts/validate_ainative_adapter_cpu.py")
            return 0
        else:
            print("⚠️  Adapter files incomplete")
            print("   Missing required files")
            return 1

    except Exception as e:
        print(f"❌ Download failed: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Verify repository exists: https://huggingface.co/ainativestudio/ainative-adapter-v1")
        print("   2. Check HF_TOKEN in backend/.env")
        print("   3. Ensure you have network connectivity")
        return 1

if __name__ == "__main__":
    sys.exit(main())
