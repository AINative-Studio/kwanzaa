# AINative Adapter Retrieval Guide

## Overview

The AINative adapter (Llama-3.2-1B + QLoRA) was successfully trained on HuggingFace Spaces. This guide explains how to retrieve the trained adapter files.

## Training Status

- **Training Space**: https://huggingface.co/spaces/ainativestudio/kwanzaa-training
- **Training Status**: ✅ Completed
- **Dataset**: https://huggingface.co/datasets/ainativestudio/ainative-training-v1 (98 examples)
- **Base Model**: unsloth/Llama-3.2-1B-Instruct
- **Method**: QLoRA (4-bit quantization, LoRA r=16, alpha=32)
- **Training Environment**: ZeroGPU A100 (40GB)

## Adapter Location

The trained adapter files are located in the HuggingFace Space's temporary storage:
- Path: `ainative-adapter-v1/` (created by AutoTrain during training)
- Files needed:
  - `adapter_config.json` - Adapter configuration
  - `adapter_model.safetensors` or `adapter_model.bin` - Trained weights

## Retrieval Options

### Option 1: Manual Download from Space (Recommended)

1. **Visit the Space's Files tab**:
   ```
   https://huggingface.co/spaces/ainativestudio/kwanzaa-training/tree/main
   ```

2. **Navigate to the adapter directory**:
   - Look for `ainative-adapter-v1/` or similar output directory
   - Check subdirectories if not in the root

3. **Download adapter files**:
   - Download all files in the adapter directory
   - Minimum required: `adapter_config.json` and `adapter_model.*`

4. **Place in project**:
   ```bash
   mkdir -p outputs/adapters/ainative-v1
   # Copy downloaded files to outputs/adapters/ainative-v1/
   ```

### Option 2: Push Adapter to HuggingFace Hub

If you have access to the Space, you can push the adapter to Hub:

1. **From the Space terminal or Gradio interface**:
   ```python
   from huggingface_hub import HfApi
   import os

   api = HfApi(token=os.getenv("HF_TOKEN"))

   # Create model repository
   repo_id = "ainativestudio/ainative-adapter-v1"
   api.create_repo(repo_id, repo_type="model", exist_ok=True)

   # Upload adapter
   api.upload_folder(
       folder_path="ainative-adapter-v1",
       repo_id=repo_id,
       repo_type="model"
   )
   ```

2. **Then download using our script**:
   ```bash
   # Update download script to use the new repo
   python scripts/download_ainative_adapter.py
   ```

### Option 3: Re-run Training Locally

If adapter files are not accessible, you can re-run training:

```bash
# Using the same dataset and configuration
python scripts/upload_dataset_to_hf.py  # Already done
python scripts/train_ainative_adapter_local.py  # TODO: Create this script
```

## Verification

Once you have the adapter files, verify them:

```bash
# Check adapter structure
ls -lh outputs/adapters/ainative-v1/

# Expected output:
# adapter_config.json
# adapter_model.safetensors (or adapter_model.bin)
# README.md (optional)
# training_args.bin (optional)
```

## Validation

After retrieval, validate the adapter:

```bash
python scripts/validate_ainative_adapter.py
```

This will test the adapter on:
- Agent Swarm orchestration (2 tests)
- AIkit SDK integration (2 tests)
- ZeroDB operations (2 tests)
- TDD/BDD patterns (2 tests)
- OpenAPI specifications (2 tests)

Expected results:
- Overall Score: ≥70%
- Zero AI Attribution: ✅ PASSED
- Category Scores: All ≥60%

## Next Steps

After successful retrieval and validation:

1. **Issue #77**: Validate adapter quality ✅ (validation script created)
2. **Issue #78**: Integrate into backend API
   - Update `backend/config/models.yaml`
   - Add adapter to model registry
   - Configure adapter loading
   - Test with backend endpoints

## Troubleshooting

### Adapter Files Not Found in Space

**Cause**: Space may have cleared temporary files after training

**Solutions**:
1. Re-run training in the Space (configuration already updated)
2. Train locally using the same dataset (already on HuggingFace Hub)
3. Contact HuggingFace support for assistance with Space storage

### Adapter Format Issues

**Cause**: AutoTrain may save in different formats

**Check for**:
- `.safetensors` format (preferred)
- `.bin` format (PyTorch)
- `.pt` format (PyTorch)

All formats are compatible with PEFT/Transformers.

## References

- **Training Configuration**: `hf_space_clone/app.py`
- **Dataset Validation**: `data/training/validation_report.txt`
- **Dataset Upload Script**: `scripts/upload_dataset_to_hf.py`
- **Validation Script**: `scripts/validate_ainative_adapter.py`
- **HuggingFace Space**: https://huggingface.co/spaces/ainativestudio/kwanzaa-training
- **Dataset Hub**: https://huggingface.co/datasets/ainativestudio/ainative-training-v1
