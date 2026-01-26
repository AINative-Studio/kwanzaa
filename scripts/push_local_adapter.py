#!/usr/bin/env python3
"""
Push locally trained adapter to HuggingFace Hub as ainative-adapter-v1

This script pushes the kwanzaa-adapter-v4 (latest local adapter) to HuggingFace Hub
at ainativestudio/ainative-adapter-v1 for the AINative platform.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo

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

# Configuration
LOCAL_ADAPTER_DIR = Path(__file__).parent.parent / "backend" / "models" / "adapters" / "kwanzaa-adapter-v4"
REPO_ID = "ainativestudio/ainative-adapter-v1"
HF_TOKEN = os.getenv("HF_TOKEN")

def main():
    """Push local adapter to HuggingFace Hub."""

    print("🚀 Pushing AINative Adapter to HuggingFace Hub\n")
    print(f"Local Adapter: {LOCAL_ADAPTER_DIR}")
    print(f"Target Repository: {REPO_ID}")
    print()

    # Check if adapter directory exists
    if not LOCAL_ADAPTER_DIR.exists():
        print(f"❌ Adapter directory not found: {LOCAL_ADAPTER_DIR}")
        return 1

    # List adapter files
    adapter_files = list(LOCAL_ADAPTER_DIR.rglob("*"))
    print(f"📦 Found {len(adapter_files)} files in adapter directory:")
    for f in adapter_files[:20]:
        if f.is_file():
            size = f.stat().st_size / (1024 * 1024)  # MB
            print(f"  - {f.name} ({size:.2f} MB)")
    if len(adapter_files) > 20:
        print(f"  ... and {len(adapter_files) - 20} more")
    print()

    # Check for required files
    required_files = ["adapter_config.json"]
    adapter_weight_files = ["adapter_model.safetensors", "adapter_model.bin"]

    has_config = any((LOCAL_ADAPTER_DIR / f).exists() for f in required_files)
    has_weights = any((LOCAL_ADAPTER_DIR / f).exists() for f in adapter_weight_files)

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
        print("Please set HF_TOKEN in backend/.env")
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
            folder_path=str(LOCAL_ADAPTER_DIR),
            repo_id=REPO_ID,
            repo_type="model",
            token=HF_TOKEN,
            commit_message="Upload AINative adapter v1 - Kwanzaa knowledge fine-tuned Llama-3.2-1B QLoRA"
        )
        print("✅ Upload complete!\n")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
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
- kwanzaa
- cultural-knowledge
pipeline_tag: text-generation
library_name: peft
---

# AINative Platform Adapter v1 - Kwanzaa Knowledge

Llama-3.2-1B adapter fine-tuned on Kwanzaa cultural knowledge and historical sources for the AINative platform.

## Model Details

- **Base Model**: unsloth/Llama-3.2-1B-Instruct (meta-llama/Llama-3.2-1B-Instruct)
- **Method**: QLoRA (4-bit quantization)
- **LoRA Rank**: 16
- **LoRA Alpha**: 32
- **Training Framework**: Unsloth + HuggingFace Transformers
- **Fine-tuned for**: Kwanzaa cultural expertise, historical accuracy, citation generation

## Training Details

This adapter was trained to provide accurate, well-cited responses about:
- Kwanzaa principles (Nguzo Saba) and their applications
- Historical context and cultural significance
- Cultural contributions and community practices
- Proper citation of primary and secondary sources

### Dataset Composition
- **Citation Examples**: Proper source attribution and formatting
- **Grounded Answers**: Factual responses with evidence
- **Cultural Contributions**: Historical and contemporary contributions
- **Format Compliance**: Consistent response formatting
- **Refusal Patterns**: Appropriate handling of out-of-scope queries

### Training Configuration
- Epochs: 3-4
- Learning Rate: 2e-4
- Batch Size: 2
- Gradient Accumulation: 4-8
- Max Sequence Length: 2048
- Optimizer: AdamW (8-bit)
- Scheduler: Cosine with warmup
- LoRA Target Modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

## Usage

### With PEFT

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base model
base_model = "unsloth/Llama-3.2-1B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained(base_model)

# Load adapter
model = PeftModel.from_pretrained(model, "{REPO_ID}")

# Generate response
prompt = \"\"\"What is the principle of Umoja and how is it applied in daily life?

Please provide citations from primary sources.\"\"\"

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

### With Unsloth (for training/inference)

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="{REPO_ID}",
    max_seq_length=2048,
    dtype=None,  # Auto-detect
    load_in_4bit=True,
)

FastLanguageModel.for_inference(model)  # Enable inference mode

# Use the model
inputs = tokenizer("What are the Seven Principles of Kwanzaa?", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=256)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Performance

The adapter is optimized for:
- Accurate cultural knowledge representation
- Proper citation formatting
- Grounded, evidence-based responses
- Appropriate scope handling (refusals for out-of-domain queries)

## Limitations

- Trained specifically on Kwanzaa cultural knowledge
- May not perform well on general-purpose tasks
- Requires base model knowledge for broader reasoning
- Best used with retrieval-augmented generation (RAG) for up-to-date information

## Integration with AINative Platform

This adapter is designed to work with:
- **ZeroDB**: Vector database for semantic search
- **RAG Pipeline**: Enhanced with retrieved primary sources
- **Agent Swarm**: Multi-agent coordination for complex queries

## Citation Format

Responses include citations in this format:
```
[Source: Author Last Name, "Title" (Year), page/section]
```

## License

Apache 2.0

## Citation

If you use this adapter, please cite:
```bibtex
@misc{{ainative-kwanzaa-adapter-v1,
  title={{AINative Platform Adapter v1 - Kwanzaa Knowledge}},
  author={{AINative Studio}},
  year={{2026}},
  publisher={{HuggingFace}},
  howpublished={{\\url{{https://huggingface.co/{REPO_ID}}}}}
}}
```

## Contact

For questions or issues:
- Repository: [kwanzaa-project](https://github.com/ainativestudio/kwanzaa)
- Platform: [AINative](https://ainative.io)
"""

    print("📄 Creating README.md...")
    try:
        api.upload_file(
            path_or_fileobj=readme_content.encode(),
            path_in_repo="README.md",
            repo_id=REPO_ID,
            repo_type="model",
            token=HF_TOKEN,
            commit_message="Add comprehensive README"
        )
        print("✅ README created\n")
    except Exception as e:
        print(f"⚠️  Failed to create README: {e}\n")

    print("="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"\n🔗 Adapter available at: https://huggingface.co/{REPO_ID}")
    print(f"\n📊 Model card: https://huggingface.co/{REPO_ID}")
    print(f"\n💾 Files: https://huggingface.co/{REPO_ID}/tree/main")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
