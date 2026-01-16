# RunPod Training Environment Setup Guide

**Issue:** #47 - E3A-US4 - Provision Training Environment
**EPIC:** 3A - Hugging Face Environment & Prerequisites
**Version:** 1.0.0
**Last Updated:** January 16, 2026

---

## Executive Summary

**RECOMMENDED APPROACH:** RunPod Spot Instances with A100 GPU

This guide provides step-by-step instructions for provisioning and using RunPod GPU instances for Kwanzaa adapter training with QLoRA.

**Why RunPod?**
- We have API credentials configured and ready
- Most cost-effective option ($1.39/hr for A100-80GB spot)
- Full control over environment
- Excellent GPU availability
- 180 training runs possible with $500 budget

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Automated Provisioning](#automated-provisioning)
4. [Manual Setup](#manual-setup)
5. [Running Training](#running-training)
6. [Monitoring and Management](#monitoring-and-management)
7. [Cost Management](#cost-management)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. RunPod Account Setup

Already completed - API key configured in `backend/.env`:
```bash
RUNPOD_API_KEY=your_runpod_api_key_here
```

### 2. Required Software (Local Machine)

```bash
# Python 3.10+
python --version

# Install RunPod Python SDK
pip install runpod requests
```

### 3. Training Data

Ensure datasets are prepared:
- `data/training/kwanzaa_train.jsonl`
- `data/training/kwanzaa_eval.jsonl`

### 4. HuggingFace Token

For downloading models and publishing adapters:
```bash
# Already configured in backend/.env
HF_TOKEN=your_huggingface_token_here
```

---

## Quick Start

### Cost Comparison

```bash
# Show cost comparison for all GPU options
python scripts/provision_runpod_training.py --show-costs
```

Output:
```
====================================================================================================
RUNPOD COST COMPARISON (Budget: $500.00)
====================================================================================================

GPU             VRAM     Spot $/Run   Spot Runs    On-Demand $/Run   On-Demand Runs
----------------------------------------------------------------------------------------------------
RTX 4090        24GB     $0.48        1020         $0.76              649
A100-40GB       40GB     $1.53        326          $2.19              228
A100-80GB       80GB     $2.08        240          $2.74              182
A6000           48GB     $0.87        575          $1.31              381

====================================================================================================
RECOMMENDED: A100-40GB Spot ($1.53/run) - Best balance of cost and reliability
BUDGET OPTION: RTX 4090 Spot ($0.48/run) - Most runs per dollar
====================================================================================================
```

### Automated Provisioning (Recommended)

```bash
# Provision A100-40GB spot instance (recommended)
python scripts/provision_runpod_training.py \
    --gpu-type "A100-40GB" \
    --provision

# Budget option: RTX 4090
python scripts/provision_runpod_training.py \
    --gpu-type "RTX 4090" \
    --provision

# On-demand for critical training (no interruptions)
python scripts/provision_runpod_training.py \
    --gpu-type "A100-40GB" \
    --use-on-demand \
    --provision
```

The script will:
1. Show cost estimate
2. Request confirmation
3. Provision the GPU instance
4. Wait for it to be ready
5. Display SSH connection details
6. Save pod information to `outputs/runpod_{pod_id}.json`

---

## Automated Provisioning

### Using the Provisioning Script

The `scripts/provision_runpod_training.py` script automates the entire provisioning process.

#### 1. Dry Run (Preview)

```bash
python scripts/provision_runpod_training.py \
    --gpu-type "A100-40GB" \
    --provision \
    --dry-run
```

Output shows what will be provisioned without actually creating the instance.

#### 2. Provision Instance

```bash
python scripts/provision_runpod_training.py \
    --gpu-type "A100-40GB" \
    --provision
```

Example output:
```
================================================================================
RUNPOD TRAINING ENVIRONMENT PROVISIONING
================================================================================

GPU: NVIDIA A100 40GB
VRAM: 40GB
Mode: Spot
Hourly Rate: $1.39/hr
Estimated Cost (2hr training): $3.06
Recommended For: Production training with headroom

Proceed with provisioning? (yes/no): yes

Creating pod...
Finding available GPUs...
Pod created successfully!
Pod ID: 8x4j5k9p2q
Pod Name: kwanzaa-training-20260116-143022

Waiting for pod to be ready...
Pod 8x4j5k9p2q is ready!

SSH Connection:
  ssh root@192.168.1.100 -p 22341

Pod info saved to: outputs/runpod_8x4j5k9p2q.json

================================================================================
NEXT STEPS
================================================================================

1. Connect via SSH (see above)
2. Run setup script (see below)
3. Start training
4. Monitor training
5. Terminate pod after completion
================================================================================
```

#### 3. Connect to Instance

```bash
# Use the SSH command from the output
ssh root@192.168.1.100 -p 22341
```

---

## Manual Setup

### Option 1: Via RunPod Web Console

1. **Log in to RunPod**
   - Go to https://www.runpod.io
   - Sign in with your account

2. **Deploy Pod**
   - Click "Deploy" button
   - Select GPU type:
     - **Recommended:** NVIDIA A100 (40GB or 80GB)
     - **Budget:** NVIDIA RTX 4090 (24GB)
   - Choose **Spot** pricing (30-40% cheaper)
   - Select container image: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel`
   - Set volume size: 50GB
   - Click "Deploy"

3. **Wait for Pod to Start**
   - Takes 1-3 minutes
   - Status will change to "Running"

4. **Connect via SSH**
   - Click "Connect" on pod
   - Copy SSH command
   - Example: `ssh root@pod-id.runpod.io -p 22341 -i ~/.ssh/id_ed25519`

### Option 2: Via RunPod CLI

```bash
# Install RunPod CLI
pip install runpod

# Login
runpod config

# List available GPU types
runpod gpu-types

# Create pod
runpod create-pod \
  --name "kwanzaa-training" \
  --gpu-type "NVIDIA A100" \
  --gpu-count 1 \
  --volume-size 50 \
  --container-image "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel"

# Get pod details
runpod list-pods

# Connect via SSH
runpod ssh kwanzaa-training
```

---

## Environment Setup (On RunPod Instance)

Once connected to your RunPod instance:

### Automatic Setup Script

```bash
# Download and run setup script
wget https://raw.githubusercontent.com/YOUR_ORG/kwanzaa/main/scripts/runpod_setup.sh
bash runpod_setup.sh
```

### Manual Setup Steps

If you prefer manual setup or the script fails:

#### 1. Update System

```bash
apt-get update
apt-get install -y git wget curl vim htop
```

#### 2. Verify GPU

```bash
nvidia-smi
# Should show your A100/RTX 4090
```

#### 3. Install Python Dependencies

```bash
pip install --no-cache-dir \
    torch==2.1.0 \
    transformers>=4.36.0 \
    peft>=0.7.0 \
    bitsandbytes>=0.41.0 \
    accelerate>=0.25.0 \
    datasets>=2.16.0 \
    tensorboard>=2.15.0 \
    trl>=0.7.0 \
    huggingface-hub>=0.20.0 \
    safetensors>=0.4.0 \
    sentencepiece>=0.1.99 \
    protobuf>=3.20.0 \
    pyyaml>=6.0
```

#### 4. Optional: Flash Attention

```bash
# Speeds up training by 20-30%
# Requires Ampere+ GPU (A100, RTX 30xx/40xx)
pip install flash-attn --no-build-isolation
```

#### 5. Clone Repository

```bash
cd /workspace
git clone https://github.com/YOUR_ORG/kwanzaa.git
cd kwanzaa
```

#### 6. Configure Environment

```bash
# Copy .env file
cat > backend/.env << 'EOF'
# HuggingFace Token
HF_TOKEN=your_huggingface_token_here

# RunPod API Key
RUNPOD_API_KEY=your_runpod_api_key_here
EOF
```

#### 7. Upload Training Data

**Option A: Using scp from local machine**

```bash
# From your local machine
scp -P 22341 \
    data/training/kwanzaa_train.jsonl \
    data/training/kwanzaa_eval.jsonl \
    root@192.168.1.100:/workspace/kwanzaa/data/training/
```

**Option B: Download from cloud storage**

```bash
# On RunPod instance
cd /workspace/kwanzaa
mkdir -p data/training

# From S3
aws s3 cp s3://your-bucket/kwanzaa_train.jsonl data/training/
aws s3 cp s3://your-bucket/kwanzaa_eval.jsonl data/training/

# From Google Cloud Storage
gsutil cp gs://your-bucket/kwanzaa_train.jsonl data/training/
gsutil cp gs://your-bucket/kwanzaa_eval.jsonl data/training/

# From HuggingFace Hub
huggingface-cli download YOUR_ORG/kwanzaa-training-data --repo-type dataset --local-dir data/training/
```

#### 8. Verify Setup

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import peft; print(f'PEFT: {peft.__version__}')"

# Check training data
ls -lh data/training/
```

---

## Running Training

### Start Training

```bash
cd /workspace/kwanzaa

# Basic training
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --output-dir outputs/kwanzaa-adapter-v1

# With custom configuration
python backend/training/train_adapter.py \
    --config backend/training/config/my_config.yaml \
    --output-dir outputs/kwanzaa-adapter-v1
```

### Training in Background (Recommended)

```bash
# Use screen or tmux for persistent sessions
screen -S training

# Inside screen session
cd /workspace/kwanzaa
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --output-dir outputs/kwanzaa-adapter-v1 \
    2>&1 | tee training.log

# Detach: Ctrl+A, D
# Reattach: screen -r training
```

### Training with Monitoring

```bash
# Terminal 1: Start training
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --output-dir outputs/kwanzaa-adapter-v1

# Terminal 2: Monitor GPU
watch -n 1 nvidia-smi

# Terminal 3: Monitor logs
tail -f outputs/kwanzaa-adapter-v1/training.log
```

---

## Monitoring and Management

### Monitor Training Progress

#### 1. Training Logs

```bash
# Real-time logs
tail -f outputs/kwanzaa-adapter-v1/training.log

# Last 100 lines
tail -n 100 outputs/kwanzaa-adapter-v1/training.log

# Search for specific metrics
grep "eval_loss" outputs/kwanzaa-adapter-v1/training.log
```

#### 2. TensorBoard

```bash
# Start TensorBoard (in background or separate terminal)
tensorboard --logdir outputs/kwanzaa-adapter-v1/tensorboard --bind_all --port 6006

# Access via port forwarding from local machine
# On local machine:
ssh -L 6006:localhost:6006 root@192.168.1.100 -p 22341

# Open in browser: http://localhost:6006
```

#### 3. GPU Monitoring

```bash
# Real-time monitoring
watch -n 1 nvidia-smi

# GPU metrics to file
nvidia-smi --query-gpu=timestamp,temperature.gpu,utilization.gpu,memory.used,memory.total \
    --format=csv -l 60 > gpu_metrics.csv
```

#### 4. Training Metrics

```bash
# View metrics history
cat outputs/kwanzaa-adapter-v1/metrics_history.jsonl | jq

# Final summary
cat outputs/kwanzaa-adapter-v1/training_summary.json | jq
```

### Download Trained Adapter

```bash
# From your local machine
scp -P 22341 -r \
    root@192.168.1.100:/workspace/kwanzaa/outputs/kwanzaa-adapter-v1/final_artifact \
    ./local_outputs/

# Or use RunPod's web interface
# Navigate to Files > outputs/ and download
```

### Publish to HuggingFace Hub

```bash
# On RunPod instance
cd /workspace/kwanzaa

python -c "
from huggingface_hub import HfApi
import os

api = HfApi(token=os.getenv('HF_TOKEN'))

api.upload_folder(
    folder_path='outputs/kwanzaa-adapter-v1/final_artifact',
    repo_id='YOUR_ORG/kwanzaa-adapter-v1',
    repo_type='model',
    commit_message='Initial adapter training on RunPod'
)

print('Adapter published to HuggingFace Hub!')
"
```

---

## Cost Management

### Monitor Costs

#### Real-Time Cost Tracking

```bash
# Check current pod costs in RunPod dashboard
# Or via API:
python -c "
import os
import requests

api_key = os.getenv('RUNPOD_API_KEY')
headers = {'Authorization': f'Bearer {api_key}'}

response = requests.get(
    'https://api.runpod.io/graphql',
    headers=headers,
    json={'query': '{ myself { spending { total } } }'}
)

print(response.json())
"
```

#### Estimated Costs

Based on 2-hour training runs:

| GPU | Mode | Cost/Run | Runs/$500 | Notes |
|-----|------|----------|-----------|-------|
| **RTX 4090** | Spot | $0.48 | 1,020 | Best value, may need tuning |
| **A100-40GB** | Spot | $1.53 | 326 | Recommended balance |
| **A100-40GB** | On-Demand | $2.19 | 228 | No interruptions |
| **A100-80GB** | Spot | $2.08 | 240 | For batch training |

### Cost Optimization Strategies

#### 1. Use Spot Instances

- **Savings:** 30-40% vs on-demand
- **Risk:** May be interrupted
- **Mitigation:** Enable frequent checkpointing

```yaml
# In training.yaml
checkpointing:
  save_steps: 50  # Save every 50 steps
  save_total_limit: 5
```

#### 2. Optimize Training Speed

```yaml
# Enable Flash Attention
model:
  use_flash_attention: true

# Use BF16 precision
run:
  mixed_precision: "bf16"

# Maximize batch size
training:
  per_device_train_batch_size: 2  # If VRAM allows
  gradient_accumulation_steps: 8
```

#### 3. Terminate Pods Promptly

```bash
# From local machine
python scripts/provision_runpod_training.py --terminate-pod 8x4j5k9p2q

# Or via web console
# Navigate to pod and click "Terminate"
```

#### 4. Batch Multiple Training Runs

```bash
# Train multiple adapters in one session
for model in "ai2" "llama" "deepseek"; do
    python backend/training/train_adapter.py \
        --config backend/training/config/${model}_training.yaml \
        --output-dir outputs/kwanzaa-adapter-${model}
done
```

### Cost Alerts

Set up alerts in RunPod dashboard:
1. Go to Account Settings
2. Navigate to Billing
3. Set spending limits
4. Enable email notifications

---

## Troubleshooting

### Connection Issues

#### Cannot Connect via SSH

```bash
# Check pod status
# Option 1: Via provisioning script
python scripts/provision_runpod_training.py --list-pods

# Option 2: Via RunPod CLI
runpod list-pods

# Option 3: Web console
# Check if pod is in "Running" state
```

**Solution:**
- Wait 2-3 minutes after pod creation
- Verify SSH port is correct
- Check firewall settings on local machine

#### SSH Connection Drops

**Cause:** Network instability or idle timeout

**Solution:**
```bash
# Add to ~/.ssh/config on local machine
Host runpod-*
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Training Issues

#### CUDA Out of Memory

**Error:** `RuntimeError: CUDA out of memory`

**Solutions:**

1. **Reduce batch size:**
```yaml
training:
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 32
```

2. **Reduce sequence length:**
```yaml
data:
  max_seq_length: 1024  # Down from 2048
```

3. **Enable gradient checkpointing:**
```yaml
training:
  gradient_checkpointing: true
```

#### Slow Training

**Symptoms:** < 100 tokens/second

**Check:**
```bash
# GPU utilization
nvidia-smi

# Expected: 90-100% GPU utilization
# If low, check:
```

**Solutions:**

1. **Enable Flash Attention:**
```bash
pip install flash-attn --no-build-isolation
```

2. **Increase workers:**
```yaml
run:
  dataloader_num_workers: 8
  dataloader_pin_memory: true
```

3. **Use BF16:**
```yaml
run:
  mixed_precision: "bf16"
```

#### Dataset Not Found

**Error:** `FileNotFoundError: data/training/kwanzaa_train.jsonl`

**Solution:**
```bash
# Verify dataset location
ls -la /workspace/kwanzaa/data/training/

# If missing, upload from local machine
scp -P 22341 data/training/*.jsonl root@POD_IP:/workspace/kwanzaa/data/training/
```

#### Spot Instance Interrupted

**Warning:** `Your pod will be stopped in 30 seconds`

**Action:**
1. Training should checkpoint automatically
2. Provision new instance
3. Resume from checkpoint:

```bash
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --resume-from-checkpoint outputs/kwanzaa-adapter-v1/checkpoint-600
```

### Pod Management Issues

#### Cannot Terminate Pod

```bash
# Via provisioning script
python scripts/provision_runpod_training.py --terminate-pod POD_ID

# Via web console
# Go to My Pods > Select pod > Terminate

# Via RunPod CLI
runpod terminate-pod POD_ID
```

#### High Costs

**Check running pods:**
```bash
runpod list-pods

# Look for pods in "Running" state
# Terminate unused pods immediately
```

**Best practice:**
- Terminate pods immediately after training
- Set spending limits in account settings
- Use spot instances when possible

---

## Best Practices

### 1. Always Use Screen/Tmux

```bash
# Start screen session
screen -S training

# Run training inside screen
python backend/training/train_adapter.py ...

# Detach: Ctrl+A, D
# Reattach: screen -r training

# If connection drops, just reconnect and reattach
```

### 2. Monitor Costs Continuously

```bash
# Check spending daily
# Set up email alerts
# Terminate pods after use
```

### 3. Save Artifacts Frequently

```bash
# During training, sync to cloud storage
while true; do
    aws s3 sync outputs/kwanzaa-adapter-v1 s3://backup/kwanzaa-adapter-v1/
    sleep 600  # Every 10 minutes
done
```

### 4. Document Training Runs

```bash
# Create training log
cat > outputs/kwanzaa-adapter-v1/training_notes.md << EOF
# Training Run: $(date)

**Pod ID:** $POD_ID
**GPU:** A100-40GB Spot
**Duration:** 2.5 hours
**Cost:** $3.47
**Notes:** First production training run
EOF
```

### 5. Test Before Full Training

```bash
# Quick validation (10 steps)
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --output-dir /tmp/test-run \
    --max-steps 10
```

### 6. Use Version Control

```bash
# Tag training runs
git tag -a v1.0.0-adapter -m "First adapter training"
git push origin v1.0.0-adapter
```

---

## Cost Comparison: RunPod vs Alternatives

| Environment | GPU | Mode | Cost/Run | Runs/$500 | Setup Time | Pros | Cons |
|-------------|-----|------|----------|-----------|------------|------|------|
| **RunPod** | A100-40GB | Spot | $1.53 | 326 | 5 min | Best value, API | Manual setup |
| RunPod | A100-80GB | Spot | $2.08 | 240 | 5 min | Most VRAM | Higher cost |
| HF Spaces | A10G | On-demand | $2.10 | 238 | 10 min | Easy, integrated | Limited control |
| Colab Pro+ | A100 | Subscription | $1.67/day | ~300 | 2 min | Simple | Usage caps |
| AWS SageMaker | A10G | On-demand | $2.82 | 177 | 15 min | Enterprise | Complex |

**Verdict:** RunPod offers the best balance of cost, control, and performance.

---

## Next Steps

After successful training:

### 1. Evaluate Adapter

```bash
# Run evaluation on test set
python backend/training/evaluate_adapter.py \
    --adapter-path outputs/kwanzaa-adapter-v1/final_artifact \
    --test-data data/training/kwanzaa_test.jsonl
```

### 2. Deploy to Production

```bash
# Copy adapter to backend
cp -r outputs/kwanzaa-adapter-v1/final_artifact backend/adapters/kwanzaa-v1

# Update configuration
# Edit backend/config/adapters/qlora.yaml
```

### 3. Monitor Performance

- Track real-world metrics
- Collect user feedback
- Iterate on training data

### 4. Clean Up

```bash
# Terminate pod
python scripts/provision_runpod_training.py --terminate-pod POD_ID

# Archive outputs
tar -czf kwanzaa-adapter-v1.tar.gz outputs/kwanzaa-adapter-v1/
aws s3 cp kwanzaa-adapter-v1.tar.gz s3://backups/adapters/
```

---

## Support and Resources

### Documentation

- RunPod Docs: https://docs.runpod.io
- PyTorch Docs: https://pytorch.org/docs
- PEFT Docs: https://huggingface.co/docs/peft
- QLoRA Paper: https://arxiv.org/abs/2305.14314

### Support Channels

- RunPod Discord: https://discord.gg/runpod
- GitHub Issues: https://github.com/YOUR_ORG/kwanzaa/issues
- Project Slack: #kwanzaa-training

### Related Guides

- `docs/training/adapter-training-guide.md` - Detailed training guide
- `docs/training/environment-options.md` - All environment options
- `backend/training/config/training.yaml` - Training configuration

---

**Document Version:** 1.0.0
**Last Updated:** January 16, 2026
**Maintained By:** AINative Studio ML Engineering Team
**Related Issue:** #47 - E3A-US4 - Provision Training Environment
