# HuggingFace Spaces Deployment Guide - AINative Adapter Training

**Date**: 2026-01-22
**Purpose**: Deploy AINative adapter training to HuggingFace Spaces

## Overview

This guide walks through deploying the AINative adapter training environment to HuggingFace Spaces with ZeroGPU support.

## Prerequisites

- HuggingFace account
- HF_TOKEN with write access
- AINative training dataset (98 examples ready)

## Step 1: Upload Dataset to HuggingFace Hub

```bash
# Set your HuggingFace token
export HF_TOKEN="your_token_here"

# Run upload script
python3 scripts/upload_dataset_to_hf.py
```

This will upload the dataset to: `ainative/ainative-training-v1`

## Step 2: Create HuggingFace Space

1. **Go to HuggingFace**: https://huggingface.co/spaces
2. **Click "Create new Space"**
3. **Configure Space**:
   - **Name**: `ainative-adapter-training`
   - **License**: Apache 2.0
   - **SDK**: Gradio
   - **Hardware**: ZeroGPU (A100 - Free tier)
   - **Visibility**: Public

4. **Click "Create Space"**

## Step 3: Upload Files to Space

Upload these files to your Space:

### Required Files

From `hf_space/` directory:

1. **app.py** - Main Gradio app
2. **requirements.txt** - Python dependencies
3. **README.md** - Space documentation

### File Structure

```
ainative-adapter-training/
├── app.py
├── requirements.txt
└── README.md
```

## Step 4: Add HF_TOKEN Secret

1. Go to **Space Settings**
2. Click **Secrets**
3. Add new secret:
   - **Name**: `HF_TOKEN`
   - **Value**: Your HuggingFace token
4. Click **Save**

## Step 5: Wait for Build

The Space will automatically:
1. Install dependencies from `requirements.txt`
2. Launch the Gradio app
3. Display training interface

Build time: ~5-10 minutes

## Step 6: Start Training

1. **Open the Space** in your browser
2. **Verify Configuration**:
   - Dataset: `ainative/ainative-training-v1`
   - Model: `unsloth/Llama-3.2-1B-Instruct`
   - Epochs: 4
   - Learning Rate: 0.0002
3. **Click "Start Training"**
4. **Monitor Progress** in the status panel

## Training Details

### Configuration

- **Base Model**: Llama-3.2-1B-Instruct
- **Method**: QLoRA (4-bit)
- **Dataset**: 88 train, 10 eval examples
- **Epochs**: 4
- **Learning Rate**: 2e-4
- **LoRA Rank**: 16
- **Batch Size**: 2
- **Gradient Accumulation**: 8

### Expected Timeline

- **Setup**: 5-10 minutes (first time)
- **Training**: 1-2 hours (with ZeroGPU A100)
- **Total**: ~2 hours

### Resource Usage

- **GPU**: A100 (40GB) via ZeroGPU
- **Cost**: Free (ZeroGPU tier)
- **VRAM**: ~8-12GB during training

## Step 7: Download Trained Adapter

After training completes:

1. **Go to Files tab** in the Space
2. **Navigate to** `ainative-adapter-v1/`
3. **Download files**:
   - `adapter_config.json`
   - `adapter_model.safetensors`
   - (Optional) `training_args.bin`

## Step 8: Test Adapter Locally

```python
from unsloth import FastLanguageModel

# Load adapter
model, tokenizer = FastLanguageModel.from_pretrained(
    "path/to/ainative-adapter-v1",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Test prompt
prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert AINative platform developer...<|eot_id|><|start_header_id|>user<|end_header_id|>

How do I implement Agent Swarm task delegation?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

# Generate
FastLanguageModel.for_inference(model)
output = tokenizer.decode(
    model.generate(
        **tokenizer(prompt, return_tensors="pt"),
        max_new_tokens=512
    )[0]
)

print(output)
```

## Troubleshooting

### Space Build Fails

**Issue**: Dependencies fail to install
**Solution**:
- Check `requirements.txt` compatibility
- Try pinning specific versions
- Use smaller dependency set

### Training Fails with OOM

**Issue**: Out of memory during training
**Solution**:
- Reduce batch size to 1
- Increase gradient accumulation to 16
- Reduce max_seq_length to 1024

### Dataset Not Found

**Issue**: "Dataset not found" error
**Solution**:
- Verify dataset uploaded to Hub
- Check dataset name matches exactly
- Ensure HF_TOKEN is set correctly

### Training Hangs

**Issue**: Training appears stuck
**Solution**:
- Check ZeroGPU queue status
- Restart the Space
- Try during off-peak hours

## Alternative: Manual Upload to Existing Space

If you already have a Space set up:

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/ainative-adapter-training
cd ainative-adapter-training

# Copy files
cp ../hf_space/app.py .
cp ../hf_space/requirements.txt .
cp ../hf_space/README.md .

# Commit and push
git add .
git commit -m "Add AINative adapter training"
git push
```

## Production Deployment

For production training:

1. **Upgrade to Paid GPU**:
   - A100 (80GB): Faster training
   - Dedicated instance: No queue time

2. **Enable Monitoring**:
   - Add Weights & Biases integration
   - Track metrics and losses

3. **Automate Downloads**:
   - Use HuggingFace Hub API
   - Automatically publish to Model Hub

## Files Reference

### app.py
Gradio interface with:
- Training configuration UI
- Status monitoring
- AutoTrain integration

### requirements.txt
```
gradio>=4.0.0
transformers>=4.36.0
datasets>=2.16.0
huggingface-hub>=0.20.0
autotrain-advanced>=0.7.0
torch>=2.0.0
accelerate>=0.25.0
peft>=0.7.0
bitsandbytes>=0.41.0
trl>=0.7.0
```

### README.md
Space documentation with:
- Training details
- Dataset statistics
- Usage instructions

## Next Steps After Training

1. **Validate Adapter** (Issue #77)
   - Test AINative-specific prompts
   - Verify AIkit SDK knowledge
   - Check Agent Swarm patterns

2. **Integrate into Backend** (Issue #78)
   - Add to model registry
   - Update configuration
   - Deploy to staging

3. **Monitor Performance**
   - Collect user feedback
   - Track response quality
   - Iterate and improve

## Support

- HuggingFace Docs: https://huggingface.co/docs/hub/spaces
- Gradio Docs: https://gradio.app/docs
- AutoTrain Docs: https://huggingface.co/docs/autotrain

## Summary

The HuggingFace Spaces setup provides:
- ✅ Free GPU access (ZeroGPU A100)
- ✅ Web-based training interface
- ✅ Automatic dependency management
- ✅ Easy model sharing and download
- ✅ No local GPU required

Estimated total time from setup to trained adapter: **~2-3 hours**
