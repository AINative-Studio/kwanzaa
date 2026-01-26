# AINative Adapter v1 - Training Ready

**Date**: 2026-01-22
**Status**: ✅ READY FOR GPU TRAINING
**Epic**: #69 - AINative Platform Adapter Training

## Executive Summary

All preparation work is complete for training the AINative platform adapter v1. The dataset (98 examples), training configuration, and training script are ready. Training can begin immediately on a GPU-enabled machine.

## What's Complete ✅

### 1. Dataset Preparation
- **Total Examples**: 98 (88 train, 10 eval)
- **AI Attribution**: 0 violations (100% compliant)
- **Quality**: 92% overall (90/98 fully valid)
- **Split**: 90/10 train/eval ratio
- **Format**: JSONL with Llama-3 chat format

**Files**:
- `data/training/ainative_train.jsonl` (88 examples)
- `data/training/ainative_eval.jsonl` (10 examples)

### 2. Training Configuration
- **Base Model**: meta-llama/Llama-3.2-1B-Instruct
- **Method**: QLoRA (4-bit quantization)
- **Epochs**: 4
- **Learning Rate**: 2e-4
- **Batch Size**: 2 (with 8 gradient accumulation steps)
- **LoRA Rank**: 16
- **Target Modules**: All attention and MLP layers

**File**: `backend/training/config/ainative-training.yaml`

### 3. Training Script
- **Simple unsloth-based training**
- **Automatic dataset formatting**
- **TensorBoard logging**
- **Checkpoint management**
- **Memory-efficient QLoRA**

**File**: `scripts/train_ainative_adapter.py`

## Dataset Statistics

### By Source
| Source | Examples | Percentage |
|--------|----------|------------|
| Extracted (Automated) | 68 | 69.4% |
| Hand-Crafted (Manual) | 30 | 30.6% |
| **Total** | **98** | **100%** |

### By Category (Estimated)
| Category | Coverage |
|----------|----------|
| Agent Swarm | ✅ High |
| AIkit SDK | ✅ Good |
| ZeroDB | ✅ Good |
| Test Patterns | ✅ High |
| OpenAPI | ✅ High |
| MCP Tools | ⚠️ Limited |
| Standards | ⚠️ Limited |
| Patterns | ⚠️ Limited |

### Quality Metrics
| Metric | Result |
|--------|--------|
| AI Attribution | ✅ 0% (ZERO TOLERANCE met) |
| Valid JSON | ✅ 100% |
| Valid Python Syntax | ✅ 100% |
| Include Tests | ✅ 91.8% |
| Error Handling | ✅ 100% |
| Type Hints | ✅ 100% |

## Training Configuration Details

### Model Configuration
```yaml
model:
  base_model_id: "meta-llama/Llama-3.2-1B-Instruct"
  torch_dtype: "auto"  # bf16 if available
  device_map: "auto"
  load_in_4bit: true
```

### LoRA Configuration
```yaml
lora:
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj
```

### Training Hyperparameters
```yaml
training:
  num_train_epochs: 4
  learning_rate: 0.0002
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  effective_batch_size: 16
  optim: "paged_adamw_8bit"
  lr_scheduler_type: "cosine"
  warmup_ratio: 0.03
```

## How to Train

### Option 1: Local Training (Requires GPU)

```bash
# Install dependencies (if not already installed)
pip install unsloth transformers trl datasets torch

# Run training
python3 scripts/train_ainative_adapter.py

# Monitor with TensorBoard
tensorboard --logdir outputs/ainative-adapter-v1/tensorboard
```

### Option 2: RunPod Training

1. **Launch RunPod Instance**
   - GPU: A10G (recommended) or A100
   - Template: PyTorch 2.0+
   - Disk: 50GB minimum

2. **Upload Files to RunPod**
   ```bash
   # Upload dataset
   scp data/training/ainative_train.jsonl runpod:/workspace/data/training/
   scp data/training/ainative_eval.jsonl runpod:/workspace/data/training/

   # Upload training script
   scp scripts/train_ainative_adapter.py runpod:/workspace/
   ```

3. **Install Dependencies**
   ```bash
   pip install unsloth transformers trl datasets torch
   ```

4. **Run Training**
   ```bash
   python3 /workspace/train_ainative_adapter.py 2>&1 | tee training.log
   ```

5. **Download Trained Adapter**
   ```bash
   scp -r runpod:/workspace/outputs/ainative-adapter-v1 ./outputs/
   ```

### Option 3: Google Colab

1. Upload `scripts/train_ainative_adapter.py` to Colab
2. Upload dataset files to Colab
3. Install dependencies
4. Run training script
5. Download trained adapter from Colab

## Expected Training Time

| GPU | VRAM | Est. Time | Cost (est.) |
|-----|------|-----------|-------------|
| A10G | 24GB | 1.5 hours | $1.50 |
| A100 | 40GB/80GB | 1 hour | $3.00 |
| RTX 4090 | 24GB | 2 hours | Local |
| RTX 3090 | 24GB | 2.5 hours | Local |

## Post-Training Steps

After training completes:

1. **Validate Adapter** (Issue #77)
   - Test with AINative-specific prompts
   - Verify AIkit SDK knowledge
   - Check Agent Swarm patterns
   - Validate ZeroDB expertise

2. **Create Test Script**
   ```python
   from unsloth import FastLanguageModel

   model, tokenizer = FastLanguageModel.from_pretrained(
       "outputs/ainative-adapter-v1",
       max_seq_length=2048,
   )

   # Test prompt
   prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

   You are an expert AINative platform developer...<|eot_id|><|start_header_id|>user<|end_header_id|>

   How do I implement Agent Swarm task delegation with error recovery?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

   """

   output = model.generate(prompt, max_new_tokens=512)
   ```

3. **Integrate into Backend** (Issue #78)
   - Add to model registry
   - Update config files
   - Deploy to staging
   - Test in production

## Files Created

### Dataset Files
- `data/training/ainative_train_extracted.jsonl` (68 examples)
- `data/training/ainative_train_handcrafted.jsonl` (30 examples)
- `data/training/ainative_train_combined.jsonl` (98 examples)
- `data/training/ainative_train.jsonl` (88 examples - training set)
- `data/training/ainative_eval.jsonl` (10 examples - eval set)

### Scripts
- `scripts/extract_ainative_training_data.py` - Automated extraction
- `scripts/validate_ainative_training_data.py` - Quality validation
- `scripts/create_handcrafted_examples.py` - Manual example generation
- `scripts/combine_and_analyze_datasets.py` - Dataset analysis
- `scripts/split_ainative_dataset.py` - Train/eval split
- `scripts/train_ainative_adapter.py` - **Training script (ready to run)**

### Configuration
- `backend/training/config/ainative-training.yaml` - Full training config

### Documentation
- `docs/training/ainative-training-data-extraction-plan.md` - Master plan
- `docs/training/ainative-extraction-progress-summary.md` - Progress summary
- `docs/training/ainative-training-ready.md` - This document

### Reports
- `outputs/validation_errors.json` - Extracted validation
- `outputs/validation_handcrafted.json` - Handcrafted validation
- `outputs/dataset_distribution_report.json` - Distribution analysis

## Dependencies Required

```bash
# Core training dependencies
pip install unsloth
pip install transformers>=4.36.0
pip install trl
pip install datasets
pip install torch>=2.0.0

# Optional monitoring
pip install tensorboard
pip install wandb  # If using Weights & Biases
```

## Troubleshooting

### Out of Memory
- Reduce `per_device_train_batch_size` to 1
- Increase `gradient_accumulation_steps` to 16
- Ensure `load_in_4bit: true`

### Slow Training
- Verify GPU is being used: `nvidia-smi`
- Check `bf16: true` or `fp16: true`
- Ensure `use_flash_attention: true`

### Poor Quality
- Increase training epochs to 6-8
- Add more hand-crafted examples
- Balance dataset categories better
- Lower learning rate to 1e-4

## Next Actions

1. ✅ Dataset ready (98 examples, 0 AI attribution)
2. ✅ Configuration ready (QLoRA with Llama-3.2-1B)
3. ✅ Training script ready
4. ⏳ **Run training on GPU** (1-2 hours on A10G)
5. ⏳ Validate adapter quality
6. ⏳ Integrate into backend

## Success Criteria

- [x] Dataset: 70-100 examples ✅ (98 examples)
- [x] Quality: >90% valid ✅ (92% valid)
- [x] AI Attribution: 0% ✅ (0 violations)
- [x] Training config created ✅
- [x] Training script ready ✅
- [ ] Training complete
- [ ] Adapter validated
- [ ] Integrated into backend

## Conclusion

**All preparation work is complete.** The AINative adapter v1 is ready for training. The next step is to run the training on a GPU-enabled machine (RunPod, Colab, or local GPU).

Estimated training time: **1-2 hours on A10G**
Estimated cost: **$1.50-$3.00**
Success probability: **High** (following proven Kwanzaa workflow)
