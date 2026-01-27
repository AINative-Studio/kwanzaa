# HuggingFace Adapter Training Skill

Complete workflow for training Kwanzaa and AINative LoRA adapters on HuggingFace Spaces with data preparation and validation.

## Metadata

```yaml
version: 1.1.0
tags: [huggingface, lora, adapter, training, kwanzaa, ainative]
triggers:
  - "train adapter"
  - "huggingface training"
  - "train on hf spaces"
  - "lora training"
  - "qlora training"
dependencies:
  - huggingface_hub
  - datasets
  - transformers
  - peft
  - trl
```

## Overview

This skill provides a complete workflow for training QLoRA (Quantized Low-Rank Adaptation) adapters on HuggingFace Spaces infrastructure. It covers two primary use cases:

1. **Kwanzaa Adapter**: Citation-grounded chat with retrieved context
2. **AINative Adapter**: Platform-specific knowledge (ZeroDB, AIkit SDK, Agent Swarm, etc.)

### What is QLoRA?

QLoRA combines:
- **LoRA**: Low-Rank Adaptation - only train small adapter matrices (~42M params vs 7B base)
- **4-bit Quantization**: Reduce base model memory footprint by 4x
- **Result**: Train 7B models on consumer GPUs with 10-12GB VRAM

### Why HuggingFace Spaces?

- **Zero local GPU required**: Train in the cloud on A100/T4 GPUs
- **ZeroGPU support**: Pay-per-second pricing (~$0.10-0.35 per training run)
- **Managed infrastructure**: No server setup, automatic scaling
- **Direct Hub integration**: Trained adapters auto-push to HuggingFace Hub

## Dataset Locations

### Kwanzaa (Citation-Grounded Chat)

```bash
# Local paths
Train: data/training/kwanzaa_train.jsonl
Eval:  data/training/kwanzaa_eval.jsonl

# HuggingFace Hub (if uploaded)
Dataset: ainativestudio/kwanzaa-training-v1
```

### AINative (Platform Knowledge)

```bash
# Local paths
Train: data/training/ainative_train.jsonl
Eval:  data/training/ainative_eval.jsonl

# Enhanced versions (with improved examples)
Train: data/training/ainative_train_enhanced_v2.jsonl
Eval:  data/training/ainative_eval_enhanced_v2.jsonl

# HuggingFace Hub
Dataset: ainativestudio/ainative-training-v2 (RECOMMENDED - 60 samples total)
Dataset: ainativestudio/ainative-training-v1 (Legacy - 48 samples)
```

## Training Data Structure

All training data uses the **messages format** (standard for chat models):

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert AINative platform developer with deep knowledge of..."
    },
    {
      "role": "user",
      "content": "Create a client for the GET /v1/dashboard/activity endpoint"
    },
    {
      "role": "assistant",
      "content": "# Implementation with full code, tests, error handling..."
    }
  ]
}
```

### Key Fields

- **messages**: Array of conversation turns
- **role**: One of `system`, `user`, `assistant`
- **content**: Text content for that turn

### For Kwanzaa Dataset

User messages include retrieved context:

```json
{
  "role": "user",
  "content": "### Retrieved Context:\n[1] Source text...\n\n### Instruction:\nWhat is the question?"
}
```

Assistant responses include citations:

```json
{
  "role": "assistant",
  "content": "Answer with citation [1]..."
}
```

## Phase 1: Prepare Training Data

### Step 1.1: Verify Data Exists

```bash
# Check Kwanzaa data
ls -lh data/training/kwanzaa_*.jsonl

# Check AINative data (use enhanced v2 for best results)
ls -lh data/training/ainative_*enhanced_v2*.jsonl

# Verify format
head -1 data/training/kwanzaa_train.jsonl | jq .
```

### Step 1.2: Upload to HuggingFace Hub (Optional but Recommended)

**Why upload?** HuggingFace Spaces can directly load datasets from the Hub, avoiding manual file uploads.

```bash
# Set HuggingFace token (NEVER hardcode!)
export HF_TOKEN=$(grep HF_TOKEN backend/.env.local | cut -d '=' -f2)

# Or interactively
export HF_TOKEN="hf_your_token_here"

# Upload Kwanzaa dataset
python scripts/upload_dataset_to_hf.py \
  --train data/training/kwanzaa_train.jsonl \
  --eval data/training/kwanzaa_eval.jsonl \
  --repo ainativestudio/kwanzaa-training-v1 \
  --token $HF_TOKEN

# Upload AINative dataset (enhanced v2)
python scripts/upload_dataset_to_hf.py \
  --train data/training/ainative_train_enhanced_v2.jsonl \
  --eval data/training/ainative_eval_enhanced_v2.jsonl \
  --repo ainativestudio/ainative-training-v2 \
  --token $HF_TOKEN
```

### Step 1.3: Verify Dataset Structure

```python
from datasets import load_dataset

# Load from Hub
ds = load_dataset("ainativestudio/ainative-training-v2")

print(f"Splits: {list(ds.keys())}")
print(f"Train samples: {len(ds['train'])}")
print(f"Eval samples: {len(ds['eval'])}")
print(f"Features: {ds['train'].features}")

# Check first example
print(ds['train'][0]['messages'])
```

## Phase 2: Create HuggingFace Space

### Step 2.1: Create New Space

Go to: https://huggingface.co/new-space

**Configuration:**
- **Owner**: `ainativestudio` (or your org)
- **Space name**: `kwanzaa-training` or `ainative-training`
- **License**: MIT
- **SDK**: Gradio
- **Hardware**: ZeroGPU (A100) - Pay per second
- **Visibility**: Public or Private

Click **"Create Space"**

### Step 2.2: Clone Space Locally

```bash
# Set token
export HF_TOKEN=$(grep HF_TOKEN backend/.env.local | cut -d '=' -f2)

# Clone space
cd /tmp
git clone https://huggingface.co/spaces/ainativestudio/ainative-training
cd ainative-training

# Or use existing local Space
cd /Users/aideveloper/kwanzaa/hf_space
```

### Step 2.3: Copy Training Files

```bash
# From project root
cd /Users/aideveloper/kwanzaa

# Copy Space app to HF Space directory
cp hf_space/app.py /path/to/space/
cp hf_space/requirements.txt /path/to/space/
cp hf_space/README.md /path/to/space/

# Or if creating from scratch, use the template in hf_space/
```

### Step 2.4: Configure Space

Edit `app.py` and update default values:

```python
def train_with_autotrain(
    dataset_name: str = "ainativestudio/ainative-training-v2",  # Your dataset
    model_name: str = "unsloth/Llama-3.2-1B-Instruct",         # Base model
    num_epochs: int = 4,                                        # Training epochs
    learning_rate: float = 0.0002,                              # Learning rate
    batch_size: int = 2,                                        # Batch size
    gradient_accumulation: int = 8                              # Gradient accumulation
):
```

### Step 2.5: Push to HuggingFace

```bash
cd /path/to/space

# Add files
git add app.py requirements.txt README.md

# Commit
git commit -m "Add AINative adapter training interface"

# Push (triggers Space rebuild)
git push
```

## Phase 3: Run Training on Space

### Step 3.1: Wait for Space to Build

After pushing, HuggingFace will rebuild the Space (1-2 minutes).

**Check status:**
- Go to: `https://huggingface.co/spaces/ainativestudio/ainative-training`
- Look for green **"Running"** badge at top
- Interface should load without errors

### Step 3.2: Verify Configuration

In the Space UI, verify these settings:

| Setting | Kwanzaa | AINative |
|---------|---------|----------|
| **Dataset** | `ainativestudio/kwanzaa-training-v1` | `ainativestudio/ainative-training-v2` |
| **Base Model** | `unsloth/Llama-3.2-1B-Instruct` | `unsloth/Llama-3.2-1B-Instruct` |
| **Epochs** | 3-4 | 4 |
| **Learning Rate** | 0.0002 | 0.0002 |
| **Batch Size** | 2 | 2 |
| **Gradient Accumulation** | 8 | 8 |

### Step 3.3: Start Training

1. Click **"🚀 Start Training"** button in Space UI
2. Training begins automatically
3. Progress shows in output panel

**Expected Duration:**
- ZeroGPU A100: 1-2 hours
- T4 medium: 2-3 hours

### Step 3.4: Monitor Training

Watch the Space logs for progress:

```
[0:00] 🚀 Starting AINative Adapter Training...
[0:02] Loading dataset: ainativestudio/ainative-training-v2
[0:05] Initializing model: Llama-3.2-1B-Instruct
[0:08] Applying QLoRA (r=16, alpha=32)
[0:10] Trainable params: 41,943,040 / 1,235,814,400 (3.39%)
[0:12] Starting training (Epoch 1/4)...

Step 5/60   | Train Loss: 1.234 | LR: 0.0002
Step 10/60  | Train Loss: 1.123 | LR: 0.00019
Step 15/60  | Train Loss: 0.987 | LR: 0.00018
...
Epoch 1/4 Complete | Eval Loss: 0.856

[0:30] Starting Epoch 2/4...
Step 20/60  | Train Loss: 0.765 | LR: 0.00017
...

[2:00] Training Complete! ✅
[2:02] Final Eval Loss: 0.512
[2:03] Saving adapter to: ainative-adapter-v1/
```

### Step 3.5: Handle Training Errors

**Error: "Out of Memory"**
```
Solution:
1. Reduce batch_size to 1
2. Increase gradient_accumulation to 16
3. Or upgrade to larger GPU (T4 → A10G)
```

**Error: "Dataset not found"**
```
Solution:
1. Verify dataset exists: https://huggingface.co/datasets/ainativestudio/ainative-training-v2
2. Check dataset is public or you have access
3. Ensure HF token has READ permission
```

**Error: "Model not found"**
```
Solution:
1. Accept model license: https://huggingface.co/unsloth/Llama-3.2-1B-Instruct
2. Verify HF token is set
```

## Phase 4: Download and Save Adapter

### Step 4.1: Push Adapter to HuggingFace Hub

After training completes, the adapter is saved in the Space filesystem. Push it to the Hub for permanent storage:

**Option 1: Manual Upload (from Space)**
1. In Space, click **"📤 Push to Hub"** button (if available)
2. Adapter uploads to: `ainativestudio/ainative-adapter-v1`

**Option 2: Script-based Upload**
```bash
# From local machine
export HF_TOKEN=$(grep HF_TOKEN backend/.env.local | cut -d '=' -f2)

python scripts/push_adapter_to_hub.py \
  --adapter-path outputs/ainative-adapter-v1 \
  --repo ainativestudio/ainative-adapter-v1 \
  --token $HF_TOKEN
```

### Step 4.2: Download Adapter Locally

```bash
# Set token
export HF_TOKEN=$(grep HF_TOKEN backend/.env.local | cut -d '=' -f2)

# Download AINative adapter
python scripts/download_ainative_adapter.py \
  --version v1 \
  --output-dir backend/models/adapters/ainative-adapter-v1

# Download Kwanzaa adapter
python scripts/download_adapter_from_hub.py \
  --repo ainativestudio/kwanzaa-adapter-v1 \
  --output-dir backend/models/adapters/kwanzaa-adapter-v1
```

### Step 4.3: Verify Downloaded Files

```bash
# Check adapter files
ls -lh backend/models/adapters/ainative-adapter-v1/

# Expected files:
# - adapter_config.json        (LoRA configuration)
# - adapter_model.safetensors  (Adapter weights, ~84MB)
# - special_tokens_map.json    (Tokenizer config)
# - tokenizer_config.json      (Tokenizer settings)
# - tokenizer.json             (Tokenizer vocabulary)
```

### Step 4.4: Version Control

**IMPORTANT**: Adapters are large binary files. Use Git LFS or external storage.

```bash
# Option 1: Track with Git LFS (if configured)
cd backend/models/adapters/ainative-adapter-v1
git lfs track "*.safetensors"
git add .
git commit -m "Add AINative adapter v1"

# Option 2: Store only metadata, download from Hub
# Keep adapter on HuggingFace Hub only
# In backend/models/adapters/ainative-adapter-v1/README.md:
echo "Download from: https://huggingface.co/ainativestudio/ainative-adapter-v1" > README.md
```

## Phase 5: Validate Adapter

### Step 5.1: Load Adapter for Testing

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "unsloth/Llama-3.2-1B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Load adapter
adapter_path = "backend/models/adapters/ainative-adapter-v1"
model = PeftModel.from_pretrained(base_model, adapter_path)
model.eval()

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("unsloth/Llama-3.2-1B-Instruct")

print("✅ Adapter loaded successfully")
```

### Step 5.2: Run Quick Validation

```bash
# AINative adapter validation
python scripts/validate_ainative_adapter_cpu.py

# Expected output:
# Category: ZeroDB - Accuracy: 70%+
# Category: AIkit SDK - Accuracy: 70%+
# Category: Agent Swarm - Accuracy: 70%+
# Overall Accuracy: 75%+
```

### Step 5.3: Test with Sample Prompts

```python
# Test AINative knowledge
test_prompts = [
    "How do I query the ZeroDB vector database?",
    "Create a React hook using AIkit SDK",
    "Implement an Agent Swarm orchestrator",
]

for prompt in test_prompts:
    messages = [
        {"role": "system", "content": "You are an expert AINative developer..."},
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=800,
        temperature=0.2,
        top_p=0.9,
        do_sample=True
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}\n")
```

## Validation Workflow

### Validation Checklist

After training, validate the adapter against all success criteria:

**For AINative Adapter:**
- [ ] ZeroDB queries: Correct syntax and patterns
- [ ] AIkit SDK usage: Proper hook patterns and API calls
- [ ] Agent Swarm: Orchestration patterns and error handling
- [ ] File placement rules: Follows docs/{category}/ structure
- [ ] Test patterns: BDD naming, class-based, 80%+ coverage
- [ ] No AI attribution: NEVER includes Claude/AI markers

**For Kwanzaa Adapter:**
- [ ] Citation format: Correct [1], [2] usage
- [ ] Grounding: Only uses provided context
- [ ] Refusal: Says "no relevant context" when appropriate
- [ ] JSON format: Valid response structure
- [ ] Context handling: Properly parses retrieved docs

### Automated Validation Scripts

```bash
# Run all AINative validations
python scripts/validate_ainative_adapter_cpu.py --verbose

# Run Kwanzaa validations
python scripts/validate_training_data_learned.py

# Run comprehensive evaluation suite
pytest tests/test_adapter_integration.py -v
```

### Success Metrics

**AINative Adapter:**
- Overall accuracy: **75%+** ✅
- Per-category accuracy: **70%+** ✅
- Test coverage: **80%+** ✅
- No hallucinations on platform APIs ✅

**Kwanzaa Adapter:**
- Citation coverage: **90%+** ✅
- Grounding rate: **95%+** ✅
- JSON validity: **100%** ✅
- Refusal correctness: **85%+** ✅

## Troubleshooting

### Issue: Space Won't Start

**Symptoms:**
- Space shows "Runtime Error" or "Application Error"
- Logs show import errors or version conflicts

**Solutions:**

1. **Check Gradio compatibility**
```python
# In app.py, use Gradio 5.x compatible syntax:
with gr.Blocks(title="Training") as demo:
    # ... interface ...
demo.launch()  # NOT demo.launch(show_api=False) for Gradio 6+
```

2. **Verify requirements.txt versions**
```txt
gradio>=5.0.0,<6.0.0
transformers>=4.40.0
peft>=0.10.0
trl>=0.8.0
bitsandbytes>=0.43.0
accelerate>=0.28.0
```

3. **Factory reboot Space**
- Go to Space Settings
- Click "Factory reboot"
- Wait 2 minutes

### Issue: Training Fails Immediately

**Symptoms:**
- Training starts but crashes within seconds
- Error: "CUDA out of memory" or similar

**Solutions:**

1. **Reduce memory usage**
```python
# In training config
batch_size = 1  # Minimum
gradient_accumulation = 16  # Increase to maintain effective batch size
max_seq_length = 1024  # Reduce from 2048
```

2. **Enable gradient checkpointing**
```python
gradient_checkpointing = True
gradient_checkpointing_kwargs = {"use_reentrant": False}
```

3. **Upgrade GPU tier**
- ZeroGPU → T4 medium
- T4 medium → A10G small

### Issue: Adapter Quality Poor

**Symptoms:**
- Adapter passes validation but responses are low quality
- Hallucinations or incorrect information

**Solutions:**

1. **Increase training data**
- Need 100+ samples per category minimum
- Add more diverse examples
- Include edge cases

2. **Improve data quality**
```bash
# Review and enhance examples
python scripts/extract_ainative_training_data.py --enhance
python scripts/create_handcrafted_examples.py
```

3. **Tune hyperparameters**
```yaml
num_epochs: 6  # Increase from 4
learning_rate: 0.0003  # Slightly higher
lora_r: 32  # Increase from 16 (more capacity)
lora_alpha: 64  # Scale with r (2*r)
```

4. **Train longer**
- Increase epochs from 4 → 6-8
- Monitor eval loss to avoid overfitting

### Issue: Can't Download from Hub

**Symptoms:**
- `OSError: Repository not found`
- `403 Forbidden` errors

**Solutions:**

1. **Check authentication**
```bash
# Verify token is set
export HF_TOKEN=$(grep HF_TOKEN backend/.env.local | cut -d '=' -f2)
echo $HF_TOKEN  # Should show token (check it's not empty)

# Test authentication
huggingface-cli whoami
```

2. **Verify repository access**
```bash
# Check repo exists and is accessible
huggingface-cli repo-info ainativestudio/ainative-adapter-v1
```

3. **Use correct token permissions**
- Token needs READ access for public repos
- Token needs WRITE access for private repos or uploads

### Issue: Base Model License Error

**Symptoms:**
- `OSError: You are trying to access a gated repo`
- License acceptance required

**Solutions:**

1. **Accept model license**
- Go to: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
- Click "Agree and access repository"
- Wait 1-2 minutes for access to propagate

2. **Use ungated alternative**
```python
# Instead of meta-llama/Llama-3.2-1B-Instruct
model_name = "unsloth/Llama-3.2-1B-Instruct"  # Pre-quantized, no gate
```

## Quick Reference

### Environment Variables

**CRITICAL**: NEVER hardcode tokens in code or scripts!

```bash
# Set HF token from .env file
export HF_TOKEN=$(grep HF_TOKEN backend/.env.local | cut -d '=' -f2)

# Verify it's set
echo $HF_TOKEN

# Use in Python
import os
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN not set. Run: export HF_TOKEN=$(grep HF_TOKEN backend/.env.local | cut -d '=' -f2)")
```

### Training Parameters

| Parameter | Kwanzaa | AINative | Description |
|-----------|---------|----------|-------------|
| `num_epochs` | 3-4 | 4-6 | Training epochs |
| `learning_rate` | 2e-4 | 2e-4 | Learning rate |
| `batch_size` | 1-2 | 2 | Per-device batch size |
| `gradient_accumulation` | 8-16 | 8 | Effective batch = batch × accum |
| `lora_r` | 16 | 16 | LoRA rank (capacity) |
| `lora_alpha` | 32 | 32 | LoRA scaling (2*r) |
| `lora_dropout` | 0.05 | 0.05 | Regularization |
| `max_seq_length` | 2048 | 2048 | Maximum sequence length |

### Essential Commands

```bash
# Upload dataset to Hub
python scripts/upload_dataset_to_hf.py \
  --train data/training/ainative_train_enhanced_v2.jsonl \
  --eval data/training/ainative_eval_enhanced_v2.jsonl \
  --repo ainativestudio/ainative-training-v2 \
  --token $HF_TOKEN

# Download trained adapter
python scripts/download_ainative_adapter.py \
  --version v1 \
  --output-dir backend/models/adapters/ainative-adapter-v1

# Validate adapter
python scripts/validate_ainative_adapter_cpu.py --verbose

# Push adapter to Hub
python scripts/push_adapter_to_hub.py \
  --adapter-path outputs/ainative-adapter-v1 \
  --repo ainativestudio/ainative-adapter-v1 \
  --token $HF_TOKEN
```

### Cost Estimates

| GPU | Training Time | Cost/Hour | Total Cost |
|-----|---------------|-----------|------------|
| ZeroGPU A100 | 1-2 hours | $0.10/min | $6-12 |
| T4 medium | 2-3 hours | $0.60/hr | $1.20-1.80 |
| A10G small | 1.5-2 hours | $1.05/hr | $1.58-2.10 |

**Recommended**: ZeroGPU A100 for fastest training and pay-per-second pricing.

### File Locations

```
Project Structure:
├── data/training/
│   ├── kwanzaa_train.jsonl           # Kwanzaa training data
│   ├── kwanzaa_eval.jsonl            # Kwanzaa eval data
│   ├── ainative_train_enhanced_v2.jsonl  # AINative training (BEST)
│   └── ainative_eval_enhanced_v2.jsonl   # AINative eval (BEST)
│
├── backend/models/adapters/
│   ├── kwanzaa-adapter-v1/           # Downloaded Kwanzaa adapter
│   └── ainative-adapter-v1/          # Downloaded AINative adapter
│
├── hf_space/
│   ├── app.py                        # Gradio training interface
│   ├── requirements.txt              # Python dependencies
│   └── README.md                     # Space documentation
│
└── scripts/
    ├── upload_dataset_to_hf.py       # Upload data to Hub
    ├── download_ainative_adapter.py  # Download adapter
    ├── validate_ainative_adapter_cpu.py  # Validate adapter
    └── train_hf_direct.py            # Direct training script
```

### HuggingFace Resources

- **Training Space**: `https://huggingface.co/spaces/ainativestudio/kwanzaa-training`
- **Dataset Hub**: `https://huggingface.co/datasets/ainativestudio/ainative-training-v2`
- **Adapter Hub**: `https://huggingface.co/ainativestudio/ainative-adapter-v1`
- **Base Model**: `https://huggingface.co/unsloth/Llama-3.2-1B-Instruct`

## Additional Resources

### Documentation

- [HuggingFace Spaces Guide](https://huggingface.co/docs/hub/spaces)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [TRL Training Guide](https://huggingface.co/docs/trl)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)

### Internal Docs

- `/Users/aideveloper/kwanzaa/docs/training/adapter-training-guide.md` - Complete training guide
- `/Users/aideveloper/kwanzaa/docs/training/HF_AUTOTRAIN_GUIDE.md` - AutoTrain setup
- `/Users/aideveloper/kwanzaa/backend/training/config/training.yaml` - Training config reference

### Scripts

- `scripts/train_hf_direct.py` - Direct training without AutoTrain
- `scripts/upload_dataset_to_hf.py` - Upload datasets to Hub
- `scripts/download_ainative_adapter.py` - Download trained adapters
- `scripts/validate_ainative_adapter_cpu.py` - CPU-based validation

## Notes

1. **Token Security**: ALWAYS use environment variables for tokens, NEVER hardcode
2. **Dataset Versions**: Use `ainative-training-v2` (enhanced, 60 samples) for best results
3. **GPU Selection**: ZeroGPU A100 is most cost-effective for fast training
4. **Validation Required**: ALWAYS validate adapters before deployment
5. **Version Control**: Tag adapter versions (v1, v2, etc.) for tracking
6. **Quality over Quantity**: 60 high-quality examples > 200 low-quality examples

## Success Criteria

Before considering training complete:

- [ ] Training completes without errors
- [ ] Final eval loss < 0.6
- [ ] Adapter pushed to HuggingFace Hub
- [ ] Adapter downloaded locally
- [ ] Validation passes with 75%+ accuracy
- [ ] No hallucinations on platform-specific knowledge
- [ ] Adapter versioned and documented

## Version History

- **v1.1.0** (2026-01-27): Added AINative platform training workflow, comprehensive troubleshooting
- **v1.0.0** (2026-01-21): Initial version with Kwanzaa training workflow
