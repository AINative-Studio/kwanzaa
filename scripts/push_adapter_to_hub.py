#!/usr/bin/env python3
"""
Push AINative adapter to HuggingFace Hub

This script should be run IN the HuggingFace Space after training completes.
It will push the trained adapter to a permanent model repository.

Usage:
  python push_adapter_to_hub.py
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo

# Configuration
ADAPTER_DIR = "ainative-adapter-v1"  # Output directory from AutoTrain
REPO_ID = "ainativestudio/ainative-adapter-v1"
HF_TOKEN = os.getenv("HF_TOKEN")

def main():
    """Push adapter to HuggingFace Hub."""

    print("🚀 Pushing AINative Adapter to HuggingFace Hub\n")
    print(f"Adapter Directory: {ADAPTER_DIR}")
    print(f"Target Repository: {REPO_ID}")
    print()

    # Check if adapter directory exists
    adapter_path = Path(ADAPTER_DIR)
    if not adapter_path.exists():
        print(f"❌ Adapter directory not found: {adapter_path}")
        print("\nSearching for adapter in current directory...")

        # List all directories
        dirs = [d for d in Path(".").iterdir() if d.is_dir() and "adapter" in d.name.lower()]
        if dirs:
            print(f"Found {len(dirs)} adapter-related directories:")
            for d in dirs:
                print(f"  - {d}")
                files = list(d.rglob("*"))
                print(f"    Files: {len(files)}")
        else:
            print("No adapter directories found")
        return 1

    # List adapter files
    adapter_files = list(adapter_path.rglob("*"))
    print(f"📦 Found {len(adapter_files)} files in adapter directory:")
    for f in adapter_files[:20]:
        if f.is_file():
            size = f.stat().st_size / (1024 * 1024)  # MB
            print(f"  - {f.relative_to(adapter_path)} ({size:.2f} MB)")
    if len(adapter_files) > 20:
        print(f"  ... and {len(adapter_files) - 20} more")
    print()

    # Check for required files
    required_files = ["adapter_config.json"]
    adapter_weight_files = ["adapter_model.safetensors", "adapter_model.bin"]

    has_config = any((adapter_path / f).exists() for f in required_files)
    has_weights = any((adapter_path / f).exists() for f in adapter_weight_files)

    if not has_config:
        print("⚠️  Missing adapter_config.json")
    if not has_weights:
        print("⚠️  Missing adapter weights file")

    if not (has_config and has_weights):
        print("\n❌ Adapter directory incomplete")
        return 1

    print("✅ Adapter files validated\n")

    # Initialize HuggingFace API
    if not HF_TOKEN:
        print("❌ HF_TOKEN not found in environment")
        print("Please set HF_TOKEN environment variable")
        return 1

    api = HfApi(token=HF_TOKEN)

    # Create repository
    print(f"📝 Creating model repository: {REPO_ID}")
    try:
        create_repo(
            repo_id=REPO_ID,
            repo_type="model",
            exist_ok=True,
            token=HF_TOKEN
        )
        print("✅ Repository created/verified\n")
    except Exception as e:
        print(f"❌ Failed to create repository: {e}")
        return 1

    # Upload adapter
    print(f"⬆️  Uploading adapter files to {REPO_ID}...")
    try:
        api.upload_folder(
            folder_path=str(adapter_path),
            repo_id=REPO_ID,
            repo_type="model",
            token=HF_TOKEN,
            commit_message="Upload AINative adapter v1 - Llama-3.2-1B QLoRA"
        )
        print("✅ Upload complete!\n")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return 1

    # Create README
    readme_content = f"""---
license: apache-2.0
base_model: unsloth/Llama-3.2-1B-Instruct
tags:
- peft
- lora
- qlora
- ainative
- agent-swarm
- zerodb
pipeline_tag: text-generation
---

# AINative Platform Adapter v1

Llama-3.2-1B adapter fine-tuned on AINative platform expertise.

## Training Details

- **Base Model**: unsloth/Llama-3.2-1B-Instruct (meta-llama/Llama-3.2-1B-Instruct)
- **Method**: QLoRA (4-bit quantization)
- **LoRA Rank**: 16
- **LoRA Alpha**: 32
- **Dataset**: [ainativestudio/ainative-training-v1](https://huggingface.co/datasets/ainativestudio/ainative-training-v1)
- **Examples**: 98 (88 train, 10 eval)
- **Quality**: 92% valid, 0% AI attribution

## Expertise Areas

- **Agent Swarm Orchestration**: Multi-agent coordination patterns
- **AIkit SDK Integration**: React, Vue, Svelte, Next.js SDKs
- **ZeroDB Operations**: Vector database and semantic search
- **Test-Driven Development**: Pytest with 80%+ coverage
- **OpenAPI Specifications**: API design and client generation

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base model
base_model = "unsloth/Llama-3.2-1B-Instruct"
model = AutoModelForCausalLM.from_pretrained(base_model)
tokenizer = AutoTokenizer.from_pretrained(base_model)

# Load adapter
model = PeftModel.from_pretrained(model, "{REPO_ID}")

# Generate
prompt = "How do I create a parallel agent swarm with 3 agents?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=256)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

## Training Configuration

- Epochs: 4
- Learning Rate: 2e-4
- Batch Size: 2
- Gradient Accumulation: 8
- Max Sequence Length: 2048
- Optimizer: AdamW (8-bit)
- Scheduler: Cosine with 3% warmup

## License

Apache 2.0
"""

    print("📄 Creating README.md...")
    try:
        api.upload_file(
            path_or_fileobj=readme_content.encode(),
            path_in_repo="README.md",
            repo_id=REPO_ID,
            repo_type="model",
            token=HF_TOKEN,
            commit_message="Add README"
        )
        print("✅ README created\n")
    except Exception as e:
        print(f"⚠️  Failed to create README: {e}\n")

    print("="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"\nAdapter available at: https://huggingface.co/{REPO_ID}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
