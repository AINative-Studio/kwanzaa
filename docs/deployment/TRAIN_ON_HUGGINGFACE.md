# Train Adapter v2 on HuggingFace

## Quick Steps

### 1. Upload Training Data to HuggingFace Hub

```bash
# Install HF CLI
pip install huggingface_hub

# Login (need your HF token with WRITE permission)
huggingface-cli login

# Upload training files
huggingface-cli upload YOUR_USERNAME/kwanzaa-training-v2 data/training/kwanzaa_train.jsonl
huggingface-cli upload YOUR_USERNAME/kwanzaa-training-v2 data/training/kwanzaa_eval.jsonl
```

### 2. Create Training Space on HuggingFace

Go to: https://huggingface.co/spaces/autotrain-projects/autotrain-advanced

Click **"Duplicate this Space"**

Settings:
- Name: `kwanzaa-training-v2`
- Hardware: **T4 medium** ($0.60/hr - takes ~20 min = $0.20 total)
- Visibility: Private

### 3. Configure Training in the Space

- Task: **LLM SFT Training**
- Base Model: `meta-llama/Llama-3.2-1B-Instruct`
- Dataset: `YOUR_USERNAME/kwanzaa-training-v2`
- Train Split: `train`
- Valid Split: `eval`
- Learning Rate: `2e-4`
- Epochs: `3`
- Batch Size: `1`
- Gradient Accumulation: `8`
- LoRA R: `16`
- LoRA Alpha: `32`
- Use PEFT: ✅
- Use INT4: ✅

Click **"Start Training"**

### 4. Download Trained Adapter

After ~20 minutes, download from:
`https://huggingface.co/YOUR_USERNAME/kwanzaa-adapter-v2`

Save to: `backend/models/adapters/kwanzaa-adapter-v2/`

## Cost: ~$0.20 for 20 minutes on T4

**What's your HuggingFace username?** I'll prepare the upload commands.
