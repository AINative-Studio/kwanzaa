# Kwanzaa Adapter Training - Ready to Execute

**Date:** 2026-01-19
**Status:** ✅ ALL PREREQUISITES COMPLETE - Waiting for GPU Availability
**Issue:** #48 - Execute Full Training Run

---

## Summary

Everything is ready for training! RunPod CLI is installed and configured, training data is validated (134 samples), and all scripts are in place. Currently waiting for GPU availability on RunPod.

---

## What's Complete

### ✅ Infrastructure Setup
- RunPod CLI installed: `~/.local/bin/runpodctl` (v1.14.3)
- RunPod API configured: `~/.runpod/config.toml`
- SSH keys generated for pod access
- API Key confirmed working

### ✅ Training Data Validated
- **Total samples:** 134 (107 train / 27 eval)
- **Format:** HuggingFace chat JSONL
- **Quality:** All validated, schema-compliant
- **Location:**
  - `data/training/kwanzaa_train.jsonl`
  - `data/training/kwanzaa_eval.jsonl`

### ✅ Scripts Ready
- Training script: `backend/training/train_adapter.py`
- RunPod automation: `scripts/train_on_runpod.sh`
- Direct trainer: `scripts/train_direct.py`
- Configuration: `backend/training/config/training.yaml`

### ✅ Issues Closed
- ✅ Issue #59 - Create "Not in Corpus" Refusal Examples (32 samples)
- ✅ Issue #61 - Create answer_json Compliance Examples (134 samples)

---

## GPU Availability Issue

**Problem:** No GPUs currently available on RunPod
**Attempted:** RTX 4090, RTX 3090, RTX A4000, A40
**All returned:** "There are no longer any instances available"

This is a temporary capacity issue on RunPod's side.

---

## How to Execute Training (When GPUs Available)

### Option 1: Automated Script (Recommended)
```bash
# Make sure runpodctl is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Run the training script
./scripts/train_on_runpod.sh

# Or with specific GPU
./scripts/train_on_runpod.sh --gpu RTX3090
```

### Option 2: Manual RunPod CLI
```bash
# 1. Create pod
export PATH="$HOME/.local/bin:$PATH"
runpodctl create pod \
  --name kwanzaa-training \
  --gpuType RTX3090 \
  --imageName runpod/pytorch:2.1.0-py3.11-cuda12.1.0-devel-ubuntu22.04 \
  --containerDiskSize 20 \
  --volumeSize 20 \
  --ports "8888/http,22/tcp"

# 2. Get pod ID
runpodctl get pod

# 3. Wait for pod to be ready (~30 seconds)
sleep 30

# 4. Create training archive
tar -czf /tmp/kwanzaa-training.tar.gz \
  -C . backend/training data/training backend/config

# 5. Upload to pod
runpodctl send <POD_ID> /tmp/kwanzaa-training.tar.gz /workspace/

# 6. Extract on pod
runpodctl exec <POD_ID> "cd /workspace && tar -xzf kwanzaa-training.tar.gz"

# 7. Install dependencies
runpodctl exec <POD_ID> "pip install -r /workspace/backend/training/requirements.txt"

# 8. Run training
runpodctl exec <POD_ID> "cd /workspace && python backend/training/train_adapter.py \
  --config backend/training/config/training.yaml \
  --num_epochs 4 \
  --output_dir outputs/kwanzaa-adapter-v0"

# 9. Download adapter
mkdir -p outputs/kwanzaa-adapter-v0
runpodctl receive <POD_ID> /workspace/outputs/kwanzaa-adapter-v0 ./outputs/

# 10. Terminate pod
runpodctl stop pod <POD_ID>
```

### Option 3: Python Direct Script
```bash
python3 scripts/train_direct.py
```

---

## Training Configuration

### GPU Requirements
- **Minimum VRAM:** 10GB
- **Recommended:** RTX 3090 (24GB), RTX 4090 (24GB), A40 (48GB), or A100
- **Training method:** QLoRA (4-bit quantization)
- **Base model:** Llama-3.2-1B-Instruct (per docs) or OLMo-7B-Instruct (per config)

### Cost & Time Estimates
| GPU | Hourly Rate | Est. Time | Est. Cost |
|-----|-------------|-----------|-----------|
| RTX 3090 | $0.11/hr | 20 min | $0.04 |
| RTX 4090 | $0.20/hr | 15 min | $0.05 |
| A40 | $0.24/hr | 15 min | $0.06 |
| A100 | $0.60/hr | 10 min | $0.10 |

### Training Parameters
- **Epochs:** 4
- **Batch size:** 1 (gradient accumulation: 16)
- **Learning rate:** 2e-4
- **LoRA rank:** 16
- **Quantization:** 4-bit NF4
- **Max sequence length:** 2048

---

## Expected Output

After training completes, you'll have:

```
outputs/kwanzaa-adapter-v0/
├── adapter_config.json          # LoRA configuration
├── adapter_model.safetensors    # Trained weights (8-15MB)
├── training_config.yaml         # Full training settings
├── training_metrics.json        # Loss curves, perplexity
├── checksums.json              # File integrity verification
└── README.md                    # Adapter documentation
```

---

## Next Steps After Training

1. **Issue #52** - Save & Version Adapter Artifact
2. **Issue #54** - Load Adapter Into Inference Pipeline
3. **Issue #56** - Run Citation Coverage Evaluation
4. **Issue #58** - Run Hallucination Stress Tests
5. **Issue #60** - Run Cultural Integrity Red-Team

---

## Troubleshooting

### If RunPod CLI not found
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
curl -L https://github.com/runpod/runpodctl/releases/download/v1.14.3/runpodctl-darwin-arm64 -o ~/.local/bin/runpodctl
chmod +x ~/.local/bin/runpodctl
runpodctl config --apiKey "your-runpod-api-key-here"
```

### If no GPUs available
- Try different times of day (off-peak hours)
- Try different GPU types (RTX 3090, 4090, A40, A100)
- Use the web UI: https://www.runpod.io/console/pods
- Consider alternative: Modal, Lambda Labs, Vast.ai

### If training fails
- Check logs in pod: `runpodctl exec <POD_ID> "tail -f /workspace/outputs/*/logs/*"`
- Verify data uploaded: `runpodctl exec <POD_ID> "ls -la /workspace/data/training"`
- Check GPU memory: `runpodctl exec <POD_ID> "nvidia-smi"`

---

## Ready Checklist

- [x] RunPod CLI installed and configured
- [x] Training data validated (134 samples)
- [x] Training scripts ready
- [x] Configuration files ready
- [x] Cost estimated (~$0.05-$0.10)
- [x] Expected output defined
- [ ] **GPU availability** ← Current blocker

---

**Status:** Ready to train as soon as GPUs become available!
**Recommendation:** Try again in a few hours or use RunPod web UI to monitor availability.

---

Generated: 2026-01-19
Report Version: 1.0.0
