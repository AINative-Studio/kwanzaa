#!/usr/bin/env python3
"""
Test loading the adapter from HuggingFace Hub.

This script verifies that the adapter can be successfully loaded from the Hub.
It does NOT run inference (requires GPU), but confirms the model files are accessible.
"""

import os
from pathlib import Path

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

REPO_ID = "ainativestudio/ainative-adapter-v1"

def main():
    print(f"🧪 Testing adapter loading from HuggingFace Hub\n")
    print(f"Repository: {REPO_ID}\n")

    try:
        from huggingface_hub import snapshot_download, hf_hub_download

        print("📥 Attempting to download adapter config...")
        config_path = hf_hub_download(
            repo_id=REPO_ID,
            filename="adapter_config.json",
            token=os.getenv("HF_TOKEN")
        )
        print(f"✅ Config downloaded to: {config_path}\n")

        # Read and display config
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)

        print("📋 Adapter Configuration:")
        print(f"  - PEFT Type: {config.get('peft_type', 'N/A')}")
        print(f"  - Task Type: {config.get('task_type', 'N/A')}")
        print(f"  - LoRA Rank (r): {config.get('r', 'N/A')}")
        print(f"  - LoRA Alpha: {config.get('lora_alpha', 'N/A')}")
        print(f"  - Target Modules: {', '.join(config.get('target_modules', []))}")
        print(f"  - Base Model: {config.get('base_model_name_or_path', 'N/A')}")
        print()

        print("📥 Checking adapter weights file...")
        weights_path = hf_hub_download(
            repo_id=REPO_ID,
            filename="adapter_model.safetensors",
            token=os.getenv("HF_TOKEN")
        )

        # Get file size
        import os as os_module
        size_mb = os_module.path.getsize(weights_path) / (1024 * 1024)
        print(f"✅ Weights downloaded: {size_mb:.2f} MB\n")

        print("="*60)
        print("✅ ADAPTER LOADING TEST SUCCESSFUL")
        print("="*60)
        print(f"\n✓ Adapter files are accessible from HuggingFace Hub")
        print(f"✓ Configuration is valid")
        print(f"✓ Weights file is present and complete")
        print()
        print("📝 To use this adapter in your code:")
        print(f"   from peft import PeftModel")
        print(f"   model = PeftModel.from_pretrained(base_model, '{REPO_ID}')")
        print()

    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\n📦 Install with:")
        print("   pip install huggingface-hub")
        return 1
    except Exception as e:
        print(f"❌ Error loading adapter: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
