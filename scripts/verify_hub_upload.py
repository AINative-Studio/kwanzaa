#!/usr/bin/env python3
"""Verify adapter upload to HuggingFace Hub."""

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
REPO_ID = "ainativestudio/ainative-adapter-v1"

def main():
    print(f"🔍 Verifying upload to: {REPO_ID}\n")

    api = HfApi(token=HF_TOKEN)

    try:
        # List all files in the repository
        files = list(list_repo_files(repo_id=REPO_ID, repo_type="model", token=HF_TOKEN))

        print(f"✅ Repository exists with {len(files)} files:\n")

        # Categorize files
        adapter_files = []
        tokenizer_files = []
        config_files = []
        other_files = []

        for f in sorted(files):
            if "adapter" in f.lower():
                adapter_files.append(f)
            elif "tokenizer" in f.lower():
                tokenizer_files.append(f)
            elif "config" in f.lower() or f.endswith(".json"):
                config_files.append(f)
            else:
                other_files.append(f)

        if adapter_files:
            print("📦 Adapter Files:")
            for f in adapter_files:
                print(f"  - {f}")
            print()

        if config_files:
            print("⚙️  Configuration Files:")
            for f in config_files:
                print(f"  - {f}")
            print()

        if tokenizer_files:
            print("🔤 Tokenizer Files:")
            for f in tokenizer_files:
                print(f"  - {f}")
            print()

        if other_files:
            print("📄 Other Files:")
            for f in other_files:
                print(f"  - {f}")
            print()

        # Check for essential files
        essential_files = [
            "adapter_config.json",
            "adapter_model.safetensors",
            "README.md"
        ]

        print("✅ Essential Files Check:")
        for ef in essential_files:
            status = "✓" if ef in files else "✗"
            print(f"  {status} {ef}")

        print("\n" + "="*60)
        print("🎉 VERIFICATION COMPLETE")
        print("="*60)
        print(f"\n🔗 Repository URL: https://huggingface.co/{REPO_ID}")
        print(f"📊 Model Card: https://huggingface.co/{REPO_ID}")
        print(f"💾 Files: https://huggingface.co/{REPO_ID}/tree/main")
        print(f"\n📦 Install with:")
        print(f"   pip install peft transformers")
        print(f"\n💻 Use with:")
        print(f"   from peft import PeftModel")
        print(f"   model = PeftModel.from_pretrained(base_model, '{REPO_ID}')")
        print()

    except Exception as e:
        print(f"❌ Error verifying repository: {e}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
