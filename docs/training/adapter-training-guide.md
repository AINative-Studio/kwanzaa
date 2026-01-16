# Adapter Training Guide

Comprehensive guide for training QLoRA adapters for Kwanzaa citation-grounded chat.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Training Configuration](#training-configuration)
5. [Running Training](#running-training)
6. [Monitoring Training](#monitoring-training)
7. [Artifact Verification](#artifact-verification)
8. [Loading Trained Adapter](#loading-trained-adapter)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Overview

This guide covers the complete workflow for training a QLoRA (Quantized Low-Rank Adaptation) adapter on top of the AI2 OLMo-7B-Instruct base model. The adapter training pipeline ensures:

- **Reproducibility**: Versioned artifacts with checksums
- **Safety**: Base model weights remain unchanged
- **Efficiency**: QLoRA reduces VRAM requirements to ~12GB
- **Quality**: Comprehensive metrics tracking and validation

### What is QLoRA?

QLoRA combines:
- **LoRA**: Low-Rank Adaptation - only train small adapter matrices
- **4-bit Quantization**: Reduce base model memory footprint
- **Result**: Train 7B models on consumer GPUs (RTX 3090, 4090, etc.)

## Prerequisites

### Hardware Requirements

**Minimum**:
- GPU: NVIDIA RTX 3090 (24GB VRAM) or equivalent
- RAM: 32GB system RAM
- Storage: 50GB free space

**Recommended**:
- GPU: NVIDIA A100 (40GB VRAM) or RTX 4090
- RAM: 64GB system RAM
- Storage: 100GB free space (for checkpoints)

### Software Requirements

- Python 3.10 or higher
- CUDA 11.8 or higher
- Git

### Dataset Requirements

Training data must be in JSONL format with the following structure:

```json
{
  "messages": [
    {"role": "system", "content": "System prompt..."},
    {"role": "user", "content": "### Retrieved Context:\n...\n\n### Instruction:\n..."},
    {"role": "assistant", "content": "Response with citations [1]..."}
  ]
}
```

Place your datasets at:
- `data/training/kwanzaa_train.jsonl`
- `data/training/kwanzaa_eval.jsonl`

## Environment Setup

### 1. Install Training Dependencies

```bash
# Navigate to project root
cd /path/to/kwanzaa

# Install training requirements
pip install -r backend/training/requirements.txt

# Optional: Install Flash Attention 2 for faster training (if supported)
pip install flash-attn --no-build-isolation
```

### 2. Verify GPU Setup

```bash
# Check CUDA is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"

# Check bitsandbytes (for 4-bit quantization)
python -c "import bitsandbytes as bnb; print('bitsandbytes OK')"
```

### 3. Verify Base Model Access

```bash
# Test loading base model (will download if not cached)
python -c "
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('allenai/OLMo-7B-Instruct')
print('Base model accessible')
"
```

## Training Configuration

The training configuration is defined in `backend/training/config/training.yaml`.

### Key Configuration Sections

#### Model Configuration

```yaml
model:
  base_model_id: "allenai/OLMo-7B-Instruct"
  trust_remote_code: true
  use_flash_attention: true
```

#### Adapter Configuration (QLoRA)

```yaml
adapter:
  method: "qlora"
  lora:
    r: 16                    # LoRA rank (higher = more capacity, more VRAM)
    alpha: 32                # Scaling factor (typically 2*r)
    dropout: 0.05            # Regularization
    target_modules:          # Which layers to adapt
      - "q_proj"
      - "k_proj"
      - "v_proj"
      - "o_proj"
      - "gate_proj"
      - "up_proj"
      - "down_proj"
```

#### Training Hyperparameters

```yaml
training:
  num_train_epochs: 2
  learning_rate: 0.0002              # 2e-4 standard for QLoRA
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 16    # Effective batch size = 16
  max_grad_norm: 1.0
  optim: "paged_adamw_8bit"          # Memory-efficient optimizer
```

### Customizing Configuration

To modify training settings:

1. Copy the default config:
```bash
cp backend/training/config/training.yaml backend/training/config/my_training.yaml
```

2. Edit your config:
```bash
# Change hyperparameters, paths, etc.
vim backend/training/config/my_training.yaml
```

3. Use your config when training:
```bash
python backend/training/train_adapter.py --config backend/training/config/my_training.yaml
```

## Running Training

### Basic Training Command

```bash
# From project root
python backend/training/train_adapter.py \
  --config backend/training/config/training.yaml \
  --output-dir outputs/kwanzaa-adapter-v0
```

### Training Script Options

```bash
python backend/training/train_adapter.py --help

Options:
  --config PATH         Path to training config YAML (default: backend/training/config/training.yaml)
  --output-dir PATH     Output directory (overrides config)
  --verify-only         Only verify existing artifact without training
  --artifact-dir PATH   Artifact directory to verify (with --verify-only)
```

### Training Workflow

When you run training, the script:

1. **Loads configuration** from YAML file
2. **Initializes model** with 4-bit quantization
3. **Applies LoRA adapters** to target modules
4. **Saves baseline checksums** of base model weights
5. **Loads and preprocesses** training/eval datasets
6. **Trains adapter** (only adapter weights update)
7. **Verifies base weights unchanged** after training
8. **Saves adapter artifacts** with metadata and checksums
9. **Validates artifact integrity**

### Expected Output

During training, you'll see:

```
Loading base model: allenai/OLMo-7B-Instruct
Trainable parameters: 41,943,040 / 7,015,612,416 (0.60%)
Verified: Only adapter parameters are trainable
Saving baseline checksums of base model weights
Loading datasets from data/training/kwanzaa_train.jsonl
Train dataset size: 1000
Eval dataset size: 200
Starting training...
Step 10/1000 (1.0%) | Loss: 2.3456 | LR: 1.94e-04
Step 20/1000 (2.0%) | Loss: 2.1234 | LR: 1.97e-04
...
Training completed in 3600.00 seconds
Verifying base model weights unchanged...
SUCCESS: Base model weights remain unchanged
Final eval loss: 1.2345
Final perplexity: 3.44
Creating final artifact package...
Artifact integrity verification passed
```

## Monitoring Training

### TensorBoard

Training logs are automatically saved for TensorBoard:

```bash
# Start TensorBoard
tensorboard --logdir outputs/kwanzaa-adapter-v0/tensorboard

# Open in browser: http://localhost:6006
```

Metrics tracked:
- Training loss
- Evaluation loss
- Learning rate
- Gradient norm
- Perplexity

### Weights & Biases (Optional)

To enable W&B tracking:

1. Install wandb: `pip install wandb`
2. Login: `wandb login`
3. Enable in config:
```yaml
monitoring:
  wandb:
    enabled: true
    project: "kwanzaa-training"
    entity: "your-username"
```

### Training Metrics Files

Metrics are also saved to files:

- `outputs/kwanzaa-adapter-v0/metrics_history.jsonl` - Line-by-line metrics
- `outputs/kwanzaa-adapter-v0/training_summary.json` - Final summary
- `outputs/kwanzaa-adapter-v0/training_results.json` - Complete results

## Artifact Verification

### Automatic Verification

The training script automatically verifies:

1. **Base weights unchanged**: Checksums match baseline
2. **Artifact completeness**: All required files present
3. **File integrity**: Checksums match for all files

### Manual Verification

Verify an existing artifact:

```bash
python backend/training/train_adapter.py \
  --verify-only \
  --artifact-dir outputs/kwanzaa-adapter-v0/final_artifact
```

Output:
```
Verifying artifact at outputs/kwanzaa-adapter-v0/final_artifact
Checking required files...
Verifying file integrity...
Artifact verification PASSED
```

### Artifact Structure

A valid artifact contains:

```
final_artifact/
├── adapter_config.json          # LoRA configuration
├── adapter_model.safetensors    # Adapter weights (only)
├── metadata.json                # Training metadata
├── training_config.yaml         # Full training config
├── training_metrics.json        # Final metrics
├── checksums.json               # File checksums
└── README.md                    # Usage instructions
```

### Checksum Verification

Checksums ensure artifact integrity:

```python
import json
from backend.training.utils.artifacts import verify_artifact_integrity

# Load checksums
with open("outputs/kwanzaa-adapter-v0/final_artifact/checksums.json") as f:
    checksums = json.load(f)

# Verify
is_valid, errors = verify_artifact_integrity(
    "outputs/kwanzaa-adapter-v0/final_artifact",
    checksums
)

if is_valid:
    print("Artifact integrity verified")
else:
    print(f"Errors: {errors}")
```

## Loading Trained Adapter

### Python API

```python
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "allenai/OLMo-7B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Load adapter
adapter_path = "outputs/kwanzaa-adapter-v0/final_artifact"
model = PeftModel.from_pretrained(base_model, adapter_path)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("allenai/OLMo-7B-Instruct")

# Generate
prompt = "What is machine learning?"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs,
    max_new_tokens=800,
    temperature=0.2,
    top_p=0.9
)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Integration with Kwanzaa Backend

```python
# In your Kwanzaa service
from backend.models.ai2 import AI2Model

# Initialize with adapter
model = AI2Model(
    model_id="allenai/OLMo-7B-Instruct",
    adapter_path="outputs/kwanzaa-adapter-v0/final_artifact"
)

# Use normally
response = await model.generate(
    prompt="User question",
    context="Retrieved context...",
    max_tokens=800
)
```

### Merging Adapter into Base Model (Optional)

For deployment, you can merge the adapter into the base model:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

# Load model with adapter
base_model = AutoModelForCausalLM.from_pretrained("allenai/OLMo-7B-Instruct")
model = PeftModel.from_pretrained(base_model, "path/to/adapter")

# Merge adapter weights into base model
merged_model = model.merge_and_unload()

# Save merged model
merged_model.save_pretrained("outputs/merged_model")
```

**Note**: Merged model requires full model VRAM (~14GB) without quantization.

## Troubleshooting

### CUDA Out of Memory

**Error**: `CUDA out of memory`

**Solutions**:
1. Reduce batch size:
```yaml
training:
  per_device_train_batch_size: 1  # Already minimum
  gradient_accumulation_steps: 8  # Reduce from 16
```

2. Reduce sequence length:
```yaml
data:
  max_seq_length: 1024  # Reduce from 2048
```

3. Enable gradient checkpointing (already enabled by default):
```yaml
training:
  gradient_checkpointing: true
```

### Base Weights Modified Error

**Error**: `ERROR: Base model weights were modified!`

**Cause**: Something caused base model parameters to update during training.

**Solutions**:
1. Verify LoRA configuration is correct
2. Check that `gradient_checkpointing` is properly configured
3. Review custom code that might modify base model

To debug:
```python
from backend.training.utils.verification import verify_only_adapter_trainable

is_correct, issues = verify_only_adapter_trainable(model)
if not is_correct:
    print(f"Issues: {issues}")
```

### Dataset Loading Errors

**Error**: `FileNotFoundError: data/training/kwanzaa_train.jsonl`

**Solution**: Ensure datasets exist at specified paths.

```bash
# Check dataset paths
ls -lh data/training/

# Create directory if needed
mkdir -p data/training/
```

### Flash Attention Not Available

**Warning**: `Flash Attention 2 not available, falling back to SDPA`

**Impact**: Slower training, not critical.

**Solution** (optional):
```bash
pip install flash-attn --no-build-isolation
```

Requires:
- CUDA 11.8+
- Compatible GPU (Ampere or newer: RTX 30xx/40xx, A100, etc.)

### Low GPU Utilization

**Observation**: GPU utilization < 50%

**Causes**:
1. Data loading bottleneck
2. Small batch size
3. CPU preprocessing too slow

**Solutions**:
```yaml
run:
  dataloader_num_workers: 8  # Increase from 4
  dataloader_pin_memory: true

data:
  num_proc: 8  # Parallel preprocessing
```

## Best Practices

### 1. Start with Small Experiments

Before full training:

```bash
# Quick validation run (1 epoch, small dataset)
# Edit config to set num_train_epochs: 1
python backend/training/train_adapter.py \
  --config backend/training/config/training.yaml \
  --output-dir outputs/test-run
```

### 2. Monitor Metrics Closely

Watch for:
- **Loss decreasing**: Good sign
- **Loss plateau**: May need longer training or higher LR
- **Loss diverging**: LR too high or data issues

### 3. Version Your Artifacts

Use meaningful version tags:

```yaml
artifacts:
  versioning:
    version_format: "v1.0.0"  # Semantic versioning
```

### 4. Save Baseline Checksums

Always preserve baseline checksums:

```bash
# Keep these files for verification
outputs/kwanzaa-adapter-v0/baseline_checksums.json
```

### 5. Test Adapter Before Deployment

```python
# Load and test adapter
from backend.training.utils.verification import load_and_verify_adapter

model, is_valid, errors = load_and_verify_adapter(
    base_model,
    "outputs/kwanzaa-adapter-v0/final_artifact",
    "outputs/kwanzaa-adapter-v0/baseline_checksums.json"
)

if is_valid:
    print("Adapter ready for deployment")
```

### 6. Document Training Runs

Keep a training log:

```
outputs/
├── v1.0.0-baseline/           # Initial adapter
├── v1.1.0-more-citations/     # Improved citation behavior
├── v1.2.0-refusal-tuning/     # Better refusal handling
└── training_log.md            # What changed in each version
```

### 7. Use Evaluation Set Effectively

Ensure eval set covers:
- Citation-required questions (educator/research personas)
- Refusal cases (no relevant context)
- JSON format compliance
- Edge cases and red-team scenarios

### 8. Hyperparameter Tuning

Key hyperparameters to tune:

| Parameter | Default | Impact |
|-----------|---------|--------|
| `learning_rate` | 2e-4 | Higher = faster but less stable |
| `lora_r` | 16 | Higher = more capacity, more VRAM |
| `lora_alpha` | 32 | Scales adapter contribution |
| `num_train_epochs` | 2 | More epochs = more training |
| `warmup_ratio` | 0.03 | Stabilizes early training |

### 9. Cost Optimization

For budget-conscious training:

```yaml
# Use smaller base model for experimentation
model:
  base_model_id: "allenai/OLMo-1B-Instruct"  # Faster, cheaper

# Reduce checkpointing
checkpointing:
  save_steps: 500  # Less frequent saves
  save_total_limit: 2  # Keep fewer checkpoints
```

### 10. Reproducibility Checklist

- [ ] Set fixed seed in config
- [ ] Use deterministic training
- [ ] Save complete training config with artifact
- [ ] Record dataset version
- [ ] Log base model version
- [ ] Save training environment info

## Additional Resources

### Configuration References

- Full config: `backend/training/config/training.yaml`
- QLoRA config: `backend/config/adapters/qlora.yaml`
- Base model config: `backend/config/models/ai2.yaml`

### Code References

- Training script: `backend/training/train_adapter.py`
- Metrics tracking: `backend/training/utils/metrics.py`
- Artifact management: `backend/training/utils/artifacts.py`
- Verification: `backend/training/utils/verification.py`

### External Documentation

- [Hugging Face PEFT](https://huggingface.co/docs/peft)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [bitsandbytes Documentation](https://github.com/TimDettmers/bitsandbytes)

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review training logs in output directory
3. Verify hardware meets [Prerequisites](#prerequisites)
4. Open an issue on the project repository

## Next Steps

After successfully training an adapter:

1. **Evaluate**: Run comprehensive evaluation on test set
2. **Deploy**: Integrate adapter into Kwanzaa backend
3. **Monitor**: Track real-world performance
4. **Iterate**: Collect feedback and retrain as needed

See `docs/planning/Training-Config.md` for advanced training strategies.
