# RunPod Training Environment - Quick Reference

**Issue:** #47 - E3A-US4 - Provision Training Environment
**Last Updated:** January 16, 2026

---

## Quick Start (5 Minutes)

### 1. Show Costs
```bash
python scripts/provision_runpod_training.py --show-costs
```

### 2. Provision Instance
```bash
# Recommended
python scripts/provision_runpod_training.py --gpu-type "A100-40GB" --provision

# Budget option
python scripts/provision_runpod_training.py --gpu-type "RTX 4090" --provision
```

### 3. Connect
```bash
ssh root@{IP} -p {PORT}
```

### 4. Setup Environment
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/kwanzaa/main/scripts/runpod_setup.sh | bash
```

### 5. Upload Data
```bash
# From local machine
scp -P {PORT} data/training/*.jsonl root@{IP}:/workspace/kwanzaa/data/training/
```

### 6. Start Training
```bash
# On RunPod instance
screen -S training
cd /workspace/kwanzaa
python backend/training/train_adapter.py --config backend/training/config/training.yaml
# Detach: Ctrl+A, D
```

### 7. Terminate
```bash
# From local machine
python scripts/provision_runpod_training.py --terminate-pod {POD_ID}
```

---

## Cost Reference

| GPU | Mode | $/Hour | $/Run (2hr) | Runs/$500 |
|-----|------|--------|-------------|-----------|
| RTX 4090 | Spot | $0.44 | $0.97 | 515 |
| A100-40GB | Spot | $1.39 | $3.06 | 163 |
| A100-80GB | Spot | $1.89 | $4.16 | 120 |
| A100-40GB | On-Demand | $1.99 | $4.38 | 114 |

**Recommended:** A100-40GB Spot ($3.06/run)

---

## Common Commands

### Instance Management
```bash
# List running pods
runpod list-pods

# Get pod status
python scripts/provision_runpod_training.py --status {POD_ID}

# Terminate pod
python scripts/provision_runpod_training.py --terminate-pod {POD_ID}
```

### Monitoring
```bash
# Training logs
tail -f outputs/kwanzaa-adapter-v1/training.log

# GPU usage
watch -n 1 nvidia-smi

# Disk space
df -h /workspace
```

### Screen Management
```bash
# Create session
screen -S training

# List sessions
screen -ls

# Reattach
screen -r training

# Detach
Ctrl+A, D

# Kill session
screen -X -S training quit
```

---

## Training Workflow

### Standard Training
```bash
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --output-dir outputs/kwanzaa-adapter-v1
```

### Custom Configuration
```bash
python backend/training/train_adapter.py \
    --config backend/training/config/my_config.yaml \
    --output-dir outputs/kwanzaa-adapter-custom
```

### Resume from Checkpoint
```bash
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --resume-from-checkpoint outputs/kwanzaa-adapter-v1/checkpoint-600
```

---

## File Transfers

### Upload to RunPod
```bash
# Single file
scp -P {PORT} file.txt root@{IP}:/workspace/kwanzaa/

# Directory
scp -P {PORT} -r local_dir/ root@{IP}:/workspace/kwanzaa/

# Training data
scp -P {PORT} data/training/*.jsonl root@{IP}:/workspace/kwanzaa/data/training/
```

### Download from RunPod
```bash
# Trained adapter
scp -P {PORT} -r root@{IP}:/workspace/kwanzaa/outputs/kwanzaa-adapter-v1/final_artifact ./

# Training logs
scp -P {PORT} root@{IP}:/workspace/kwanzaa/outputs/kwanzaa-adapter-v1/training.log ./

# All outputs
scp -P {PORT} -r root@{IP}:/workspace/kwanzaa/outputs/ ./local_outputs/
```

---

## Troubleshooting

### Connection Issues
```bash
# Test SSH connection
ssh -v root@{IP} -p {PORT}

# Check pod status in RunPod dashboard
# https://www.runpod.io/console/pods
```

### CUDA Out of Memory
```yaml
# Edit training.yaml
training:
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 32
  gradient_checkpointing: true
```

### Slow Training
```bash
# Check GPU utilization (should be 90-100%)
nvidia-smi

# Enable Flash Attention
pip install flash-attn --no-build-isolation
```

### Spot Instance Interrupted
```bash
# Training resumes automatically from last checkpoint
# Or manually resume:
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --resume-from-checkpoint outputs/kwanzaa-adapter-v1/checkpoint-{LAST}
```

---

## Best Practices

1. **Always use screen/tmux** for long-running training
2. **Enable frequent checkpointing** for spot instances
3. **Monitor GPU utilization** - should be 90-100%
4. **Download artifacts immediately** after training
5. **Terminate pods promptly** to avoid unnecessary costs
6. **Use spot instances** for 30-40% cost savings
7. **Sync to cloud storage** during training (S3, GCS)

---

## Environment Variables

### Required
```bash
# In backend/.env
RUNPOD_API_KEY=your_runpod_api_key_here
HF_TOKEN=your_huggingface_token_here
```

### Optional
```bash
WANDB_API_KEY=your-wandb-key  # For W&B monitoring
AWS_ACCESS_KEY_ID=your-key     # For S3 backup
AWS_SECRET_ACCESS_KEY=your-secret
```

---

## Cost Optimization

### Maximize Runs per Dollar
1. Use RTX 4090 spot ($0.97/run) for experiments
2. Use A100-40GB spot ($3.06/run) for production
3. Enable Flash Attention (20-30% speedup)
4. Optimize batch size to max GPU utilization
5. Batch multiple training runs in one session

### Example: Training 3 Adapters
```bash
# One pod session
for model in "ai2" "llama" "deepseek"; do
    python backend/training/train_adapter.py \
        --config backend/training/config/${model}_training.yaml \
        --output-dir outputs/kwanzaa-adapter-${model}
done

# Cost: 1 pod × 6 hours = $8.34 (vs 3 pods × 2 hours = $9.18)
```

---

## Support

### Documentation
- **Complete Guide:** `docs/training/runpod-setup-guide.md`
- **Environment Options:** `docs/training/environment-options.md`
- **Training Guide:** `docs/training/adapter-training-guide.md`
- **Implementation Summary:** `docs/training/issue-47-implementation-summary.md`

### Scripts
- **Provisioning:** `scripts/provision_runpod_training.py`
- **Setup:** `scripts/runpod_setup.sh`
- **Data Validation:** `scripts/validate_training_data.py`

### External Links
- RunPod Console: https://www.runpod.io/console/pods
- RunPod Docs: https://docs.runpod.io
- RunPod Discord: https://discord.gg/runpod

---

## Status Check

### Pre-Training Validation
```bash
# GPU available?
nvidia-smi

# CUDA working?
python -c "import torch; print(torch.cuda.is_available())"

# Training data present?
ls -lh data/training/

# Config valid?
python backend/training/train_adapter.py --config backend/training/config/training.yaml --help
```

### Post-Training Validation
```bash
# Adapter artifact exists?
ls -lh outputs/kwanzaa-adapter-v1/final_artifact/

# Training completed successfully?
tail -n 50 outputs/kwanzaa-adapter-v1/training.log

# Metrics recorded?
cat outputs/kwanzaa-adapter-v1/training_summary.json
```

---

**Quick Reference Version:** 1.0.0
**Last Updated:** January 16, 2026
**Related Issue:** #47
