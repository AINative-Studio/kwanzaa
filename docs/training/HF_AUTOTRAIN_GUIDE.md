# Hugging Face AutoTrain Guide - Kwanzaa Adapter

## Overview

Train the Kwanzaa adapter using **Hugging Face AutoTrain** - a managed training service that handles all the infrastructure.

**Cost Estimate:**
- GPU: ~$0.40-$1.00/hour depending on GPU type
- Training time: 15-20 minutes
- **Total cost: ~$0.10-$0.35**

## Option 1: AutoTrain CLI (Local Control)

Run training from your machine, data stays local until training starts.

### 1. Install AutoTrain

```bash
cd /Users/aideveloper/kwanzaa
source venv/bin/activate
pip install autotrain-advanced
```

### 2. Prepare Data

AutoTrain expects CSV format with a `text` column:

```bash
python scripts/prepare_autotrain_data.py
```

This creates:
- `data/training/autotrain/train.csv` (107 samples)
- `data/training/autotrain/eval.csv` (27 samples)

### 3. Set HF Token

```bash
export HF_TOKEN=your_huggingface_token_here
```

Get token from: https://huggingface.co/settings/tokens (needs WRITE access)

### 4. Run Training

```bash
autotrain llm \
  --train \
  --model meta-llama/Llama-3.2-1B-Instruct \
  --project-name kwanzaa-adapter-v1 \
  --data-path data/training/autotrain \
  --train-split train \
  --valid-split eval \
  --text-column text \
  --lr 2e-4 \
  --batch-size 1 \
  --epochs 3 \
  --block-size 2048 \
  --warmup-ratio 0.1 \
  --lora-r 16 \
  --lora-alpha 32 \
  --lora-dropout 0.05 \
  --weight-decay 0.01 \
  --gradient-accumulation 8 \
  --bf16 \
  --use-peft \
  --use-int4 \
  --optimizer paged_adamw_8bit \
  --scheduler cosine \
  --logging-steps 10 \
  --eval-strategy steps \
  --eval-steps 50 \
  --save-total-limit 2 \
  --push-to-hub \
  --token $HF_TOKEN \
  --repo-id your-username/kwanzaa-adapter-v1
```

### 5. Monitor Training

AutoTrain will show progress in terminal:
```
Step 10/321 | Loss: 1.234 | LR: 0.0002
Step 20/321 | Loss: 1.123 | LR: 0.00019
...
```

### 6. Download Adapter

After training, adapter is automatically pushed to your HF Hub:
- https://huggingface.co/your-username/kwanzaa-adapter-v1

Download files:
- `adapter_config.json`
- `adapter_model.safetensors`
- Tokenizer files

---

## Option 2: AutoTrain on HF Spaces (Easiest)

Use HF's web UI - no local setup needed!

### 1. Create Dataset on HF Hub

Go to: https://huggingface.co/new-dataset

1. Name: `kwanzaa-training-data`
2. License: MIT
3. Click **Create dataset**

### 2. Upload Data Files

In your new dataset repo:

1. Click **Files and versions**
2. Click **Add file → Upload files**
3. Upload both:
   - `kwanzaa_train.jsonl`
   - `kwanzaa_eval.jsonl`
4. Click **Commit changes**

### 3. Create AutoTrain Space

Go to: https://huggingface.co/spaces/autotrain-projects/autotrain-advanced

1. Click **Duplicate this Space**
2. Name: `kwanzaa-training`
3. Hardware: **T4 medium** ($0.60/hr) or **A10G small** ($1.05/hr)
4. Click **Duplicate Space**

### 4. Configure Training

In your new Space:

1. **Task**: LLM SFT Training
2. **Base Model**: `meta-llama/Llama-3.2-1B-Instruct`
3. **Dataset**: `your-username/kwanzaa-training-data`
4. **Training Split**: `train`
5. **Validation Split**: `eval`

**Advanced Settings:**
- Learning Rate: `2e-4`
- Batch Size: `1`
- Gradient Accumulation: `8`
- Epochs: `3`
- LoRA R: `16`
- LoRA Alpha: `32`
- Use PEFT: ✅
- Use INT4: ✅
- Optimizer: `paged_adamw_8bit`

6. Click **Start Training**

### 5. Monitor Progress

Watch the Space logs for training progress. Takes 15-20 minutes.

### 6. Download Adapter

After training completes:
1. Go to: `https://huggingface.co/your-username/kwanzaa-adapter-v1`
2. Click **Files and versions**
3. Download adapter files

---

## Option 3: Manual Training Script (Most Control)

Use HF Transformers + TRL directly for maximum control.

### 1. Use Our Training Script

We have a complete training script: `scripts/train_colab.py`

### 2. Run Locally (if you have GPU)

```bash
source venv/bin/activate
python scripts/train_colab.py
```

### 3. Or Upload to HF Spaces

1. Create new Space: https://huggingface.co/new-space
2. Hardware: T4 medium ($0.60/hr)
3. Upload `train_colab.py` and data files
4. Run the script in Jupyter notebook

---

## Cost Comparison

| Method | Setup | Control | Cost | Time |
|--------|-------|---------|------|------|
| **CLI (Local)** | Medium | High | ~$0.10 | 20 min |
| **Spaces (Web UI)** | Easy | Medium | ~$0.20 | 20 min |
| **Manual Script** | Complex | Maximum | ~$0.10 | 20 min |
| **Google Colab** | Easy | Medium | **$0.00** | 20 min |

## Recommended Approach

I recommend **Option 2: AutoTrain on HF Spaces** because:
- ✅ No local setup required
- ✅ Simple web UI
- ✅ Auto-saves to HF Hub
- ✅ Easy to monitor
- ✅ Only ~$0.20 for training

## GPU Options on HF

| GPU | VRAM | Cost/hr | Recommended |
|-----|------|---------|-------------|
| T4 small | 16GB | $0.40 | ✅ Yes (our 1B model fits) |
| T4 medium | 16GB | $0.60 | ✅ Faster |
| A10G small | 24GB | $1.05 | Overkill |
| A100 | 80GB | $4.00+ | Not needed |

**Best choice: T4 medium** - Good balance of speed and cost

## Data Format for AutoTrain

AutoTrain expects either:

### Format 1: CSV with text column
```csv
text
"<|begin_of_text|><|start_header_id|>system<|end_header_id|>...content..."
```

### Format 2: JSONL (our current format)
```json
{"messages": [{"role": "system", "content": "..."}, ...]}
```

AutoTrain can handle both! If using JSONL, it will automatically convert.

## Troubleshooting

### "Model not found"
- Accept Llama 3.2 license: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
- Make sure your HF token has READ access

### "Out of memory"
- Reduce batch size to 1
- Increase gradient accumulation to 16
- Use smaller GPU (T4) with INT4 quantization

### "Training not starting"
- Check HF token has WRITE access
- Verify dataset is uploaded and public
- Check Space has GPU enabled

### "Can't push to Hub"
- HF token needs WRITE permission
- Repository name must match `hub_model_id` in config
- Make sure repo exists or enable `create_repo`

## What's Next?

After training completes:
1. Download adapter from HF Hub
2. Save to: `backend/models/adapters/kwanzaa-adapter-v1/`
3. Update Issue #52 (Save & Version Adapter Artifact)
4. Run evaluations (Issues #54, #56, #58, #60)

## Need Your HF Username

Before running, I need your Hugging Face username to set up the correct paths. What's your HF username?

---

**Ready to train?** Let me know your HF username and which option you prefer!
