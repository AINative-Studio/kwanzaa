# Training Environment Options for Kwanzaa Adapter Training

**Issue:** #47 - E3A-US4 - Provision Training Environment
**EPIC:** 3A - Hugging Face Environment & Prerequisites
**Version:** 1.0.0
**Last Updated:** January 16, 2026

---

## Executive Summary

**RECOMMENDED ENVIRONMENT:** RunPod Spot Instances with A100 GPU

**Key Decision Factors:**
- **API credentials already configured** (RUNPOD_API_KEY in backend/.env)
- Most cost-effective option ($1.39-$1.89/hr for A100 spot)
- Full control over environment and system configuration
- Automated provisioning script provided (`scripts/provision_runpod_training.py`)
- Excellent GPU availability with wide hardware selection
- 180-326 training runs possible with $500 budget

**Estimated Cost:** $1.53-$3.06 per training run (best value in market)

**Secondary Recommendation:** HuggingFace Spaces for teams prioritizing ease of use over cost

---

## Training Requirements Analysis

Based on `/Users/aideveloper/kwanzaa/backend/training/config/training.yaml`:

### Compute Requirements

**Minimum Specifications:**
- GPU: 10GB VRAM minimum, 12GB+ recommended
- Precision: BF16 (bfloat16) preferred, FP16 fallback
- Quantization: 4-bit via bitsandbytes (NF4)
- Memory: QLoRA reduces 7B model from ~28GB to ~10GB

**Training Profile:**
- Base Model: OLMo-7B-Instruct (7 billion parameters)
- Method: QLoRA (4-bit quantized LoRA)
- Duration: ~2 hours per training run
- Batch Size: 1 per device, 16 gradient accumulation steps
- Max Sequence Length: 2048 tokens

**Dependencies:**
- PyTorch >= 2.1.0
- Transformers >= 4.36.0
- PEFT >= 0.7.0
- BitsAndBytes >= 0.41.0
- Flash Attention 2 (optional, performance boost)

### Storage Requirements

**Training Storage:**
- Base model cache: ~15GB (OLMo-7B)
- Training dataset: ~500MB-1GB
- Checkpoints: 3 checkpoints x ~150MB = 450MB
- Logs and artifacts: ~100MB
- **Total:** ~17-20GB

**Output Artifacts:**
- Final adapter: ~150MB
- Training metrics: ~10MB
- TensorBoard logs: ~50MB

---

## Environment Comparison Matrix

### 1. RunPod (RECOMMENDED - API Credentials Ready)

**Overview:**
Dedicated GPU cloud with on-demand and spot instances, API-driven provisioning.

**Specifications:**
- GPU Options: RTX 4090 (24GB), A100 (40GB/80GB), A6000 (48GB)
- Pricing: $0.44/hr (4090 spot), $1.39/hr (A100-40GB spot), $1.89/hr (A100-80GB spot)
- Storage: 50GB container + persistent volumes
- Network: Excellent (direct access to instances)

**Cost Estimate (A100-40GB Spot - RECOMMENDED):**
- Training run: 2 hours x $1.39/hr = $2.78
- Buffer (10%): $0.31
- Total per iteration: ~$3.06
- Budget of $500: ~163 training runs
- Budget of $5000: ~1,633 training runs

**Pros:**
- **API credentials already configured** in backend/.env
- **Automated provisioning script** (`scripts/provision_runpod_training.py`)
- **Most cost-effective** option in the market
- Full root access and system control
- Wide GPU selection (RTX 4090, A100, A6000)
- Spot pricing saves 30-40% vs on-demand
- SSH access with persistent volumes
- No usage caps or session limits
- Docker/custom container support
- Can run multi-day training jobs
- GraphQL API for automation

**Cons:**
- Spot instances can be interrupted (mitigated with checkpointing)
- Requires manual environment setup (automated with provided scripts)
- No native HuggingFace Hub integration (easy workaround)
- Need to manage instance lifecycle

**Best For:**
- **This project** (credentials ready, scripts provided)
- Cost-conscious training at scale
- Teams needing full environment control
- Long-running or batch training jobs
- Automated CI/CD pipelines

**Setup Time:** ~5 minutes (automated with scripts)

**Documentation:** `docs/training/runpod-setup-guide.md`

---

### 2. Hugging Face Spaces (SECONDARY OPTION)

**Overview:**
Managed Jupyter/Gradio environments with GPU access, native HF integration.

**Specifications:**
- GPU Options: T4 (16GB), A10G (24GB), A100 (40GB/80GB)
- Pricing: $0.60/hr (T4), $1.05/hr (A10G), $3.50/hr (A100-40GB)
- Storage: 50GB persistent, 500GB ephemeral
- Network: Excellent (within HF infrastructure)

**Cost Estimate (A10G 24GB):**
- Training run: 2 hours x $1.05/hr = $2.10
- Testing/validation: 1 hour x $1.05/hr = $1.05
- Total per iteration: ~$3.15
- Budget of $500: ~158 training runs

**Pros:**
- Native HuggingFace Hub integration (push models directly)
- Git-backed environment (reproducible)
- Pre-installed ML stack (PyTorch, Transformers)
- Persistent storage for checkpoints
- Public/private space options
- Built-in logging and monitoring
- Can share training notebooks publicly

**Cons:**
- Limited to HF-provided hardware tiers
- Occasional cold start times
- Less control over system configuration

**Best For:**
- Direct model publishing to HF Hub
- Reproducible research environments
- Collaborative development
- Public demos and sharing

---

### 3. Hugging Face AutoTrain

**Overview:**
Fully managed training service with GUI/API.

**Specifications:**
- GPU: Automatic selection based on model size
- Pricing: ~$2-5 per training job (opaque pricing)
- Storage: Managed automatically
- Network: Excellent

**Cost Estimate:**
- Per training job: $2-5 (estimated)
- Budget of $500: ~100-250 training runs

**Pros:**
- Zero code required (GUI-driven)
- Automatic hyperparameter tuning
- Direct HF Hub publishing
- Handles all infrastructure
- Optimized training pipelines

**Cons:**
- Limited control over training code
- Cannot use custom training script
- Less transparency on costs
- Cannot add custom metrics/callbacks
- Not suitable for research/experimentation

**Best For:**
- Quick proof-of-concept training
- Non-technical team members
- Standard fine-tuning tasks

**Verdict:** NOT RECOMMENDED for Kwanzaa (need custom metrics and training logic)

---

### 4. Google Colab Pro/Pro+

**Overview:**
Consumer-grade Jupyter notebooks with GPU access.

**Specifications:**
- Colab Pro: T4 (16GB), $9.99/month
- Colab Pro+: V100 (16GB) or A100 (40GB), $49.99/month
- Storage: 200GB Google Drive (Pro+)
- Network: Good (Google infrastructure)

**Cost Estimate (Colab Pro+):**
- Monthly subscription: $49.99
- Training runs: Unlimited (with usage caps)
- Effective cost: $1.67/day = $0.07/hour (if fully utilized)

**Pros:**
- Extremely cost-effective if used heavily
- Familiar Jupyter interface
- Good GPU availability (Pro+)
- Drive integration for storage
- Easy to get started

**Cons:**
- Usage caps (may disconnect after 12-24 hours)
- No guaranteed availability (queue-based)
- Ephemeral environment (state lost on disconnect)
- Cannot run background jobs reliably
- A100 access not guaranteed (Pro+)

**Best For:**
- Budget-constrained experimentation
- Individual researchers
- Short training runs (<4 hours)

**Verdict:** VIABLE but less reliable for production training pipelines

---

### 5. Lambda Labs

**Overview:**
Dedicated GPU cloud with simple pricing and good availability.

**Lambda Labs Specifications:**
- RTX A6000 (48GB): $0.80/hr
- A100 (40GB): $1.10/hr
- A100 (80GB): $1.50/hr
- Storage: 512GB NVMe included

**Cost Estimate (Lambda A100 40GB):**
- Training run: 2 hours x $1.10/hr = $2.20
- Total per iteration: ~$2.20
- Budget of $500: ~227 training runs

**Pros:**
- Simple, transparent pricing
- Good GPU availability
- 512GB NVMe storage included
- SSH access
- Clean interface

**Cons:**
- No spot pricing (no cost savings option)
- Smaller GPU selection than RunPod
- Manual environment setup required
- No API for automation
- Less flexible than RunPod

**Best For:**
- Teams wanting simplicity
- On-demand only (no spot instances needed)
- Predictable costs

**Verdict:** VIABLE ALTERNATIVE but RunPod offers better value and flexibility

---

### 6. AWS SageMaker

**Overview:**
Enterprise ML platform with managed training jobs.

**Specifications:**
- ml.g5.xlarge (A10G 24GB): $1.41/hr
- ml.p4d.24xlarge (A100 40GB): $40.96/hr (8x A100)
- ml.g5.2xlarge (A10G 24GB): $1.52/hr
- Storage: S3 (standard rates)

**Cost Estimate (ml.g5.xlarge):**
- Training run: 2 hours x $1.41/hr = $2.82
- S3 storage: ~$0.50/month
- Data transfer: ~$0.10
- Total per iteration: ~$3.50
- Budget of $500: ~142 training runs

**Pros:**
- Enterprise-grade reliability
- Managed Spot Training (70% cost savings)
- Integrated with AWS ecosystem
- Excellent monitoring (CloudWatch)
- Model registry and versioning
- Distributed training support
- Compliance certifications

**Cons:**
- Complex pricing structure
- Steeper learning curve
- Requires AWS expertise
- More overhead for simple tasks
- Not optimized for HuggingFace workflow

**Best For:**
- Enterprise deployments
- Regulated industries
- Existing AWS infrastructure
- Multi-region requirements

**Verdict:** OVERKILL for current scope, consider for production scale

---

### 7. Azure Machine Learning

**Overview:**
Microsoft's enterprise ML platform.

**Specifications:**
- Standard_NC6s_v3 (V100 16GB): $3.06/hr
- Standard_ND96asr_v4 (A100 40GB): $27.20/hr (8x A100)
- Standard_NC24ads_A100_v4 (A100 80GB): $3.67/hr
- Storage: Blob Storage (standard rates)

**Cost Estimate (NC24ads_A100_v4):**
- Training run: 2 hours x $3.67/hr = $7.34
- Storage: ~$0.50/month
- Total per iteration: ~$8
- Budget of $500: ~62 training runs

**Pros:**
- Microsoft ecosystem integration
- Enterprise support and SLAs
- Azure AD authentication
- Compliance certifications
- MLOps tools included

**Cons:**
- Higher pricing than alternatives
- Complex setup process
- Not HuggingFace-native
- Windows-oriented defaults

**Best For:**
- Microsoft-centric organizations
- Enterprise with Azure contracts

**Verdict:** NOT RECOMMENDED (cost and complexity)

---

## Detailed Recommendation: RunPod with A100 Spot Instances

### Why RunPod?

**Strategic Alignment:**
1. **API Credentials Ready:** `RUNPOD_API_KEY` already configured in backend/.env
2. **Automated Provisioning:** Complete provisioning script provided
3. **Most Cost-Effective:** 30-40% cheaper than alternatives with spot pricing
4. **Full Control:** Root access, custom environment, no restrictions
5. **API-Driven:** GraphQL API for automation and CI/CD integration
6. **Wide GPU Selection:** RTX 4090, A100 (40GB/80GB), A6000
7. **No Usage Caps:** Run multi-day training without interruption concerns

**Technical Fit:**
- A100 (40GB VRAM) far exceeds 12GB minimum requirement
- Supports BF16 precision natively
- 50GB container + persistent volumes
- Full PyTorch 2.1+ environment (automated setup script)
- SSH access for debugging and monitoring
- Can install any dependencies

**Cost Analysis:**
```
Per Training Run (A100-40GB Spot):
- Training: 2 hours x $1.39/hr = $2.78
- Buffer (10% for spot): $0.28
Total: ~$3.06 per complete iteration

Budget Utilization:
- $500 budget / $3.06 per run = 163 training iterations
- $5,000 budget / $3.06 per run = 1,633 training iterations

Alternative (RTX 4090 Spot - Budget Option):
- Training: 2 hours x $0.44/hr = $0.88
- Buffer (10%): $0.09
Total: ~$0.97 per iteration
- $500 budget: 515 runs
- $5,000 budget: 5,154 runs
```

**Provisioning in 3 Commands:**
```bash
# 1. Show cost comparison
python scripts/provision_runpod_training.py --show-costs

# 2. Provision instance
python scripts/provision_runpod_training.py --gpu-type "A100-40GB" --provision

# 3. Connect and start training
ssh root@IP -p PORT
bash runpod_setup.sh
python backend/training/train_adapter.py --config backend/training/config/training.yaml
```

### Secondary Recommendation: HuggingFace Spaces

**For Teams Prioritizing Ease of Use:**
- A10G (24GB): $1.05/hr on-demand only
- 2-hour training: $2.10 (plus validation/experimentation ~$3.68)
- $500 budget: 135 runs
- **Pros:** Native HF integration, git-backed, zero setup
- **Cons:** 17% more expensive, less flexibility, no spot pricing

---

## Setup Instructions: RunPod (Recommended)

### Quick Start with RunPod

**Prerequisites:**
- RunPod API key configured in `backend/.env` (already done)
- Training data prepared in `data/training/`
- HuggingFace token configured (for model downloads)

**Step 1: Show Cost Comparison**

```bash
python scripts/provision_runpod_training.py --show-costs --budget 500
```

**Step 2: Provision GPU Instance**

```bash
# Recommended: A100-40GB spot
python scripts/provision_runpod_training.py \
    --gpu-type "A100-40GB" \
    --provision

# Budget option: RTX 4090 spot
python scripts/provision_runpod_training.py \
    --gpu-type "RTX 4090" \
    --provision

# Critical training (no interruptions): A100-40GB on-demand
python scripts/provision_runpod_training.py \
    --gpu-type "A100-40GB" \
    --use-on-demand \
    --provision
```

The script will:
1. Display cost estimates
2. Request confirmation
3. Provision the instance
4. Display SSH connection details
5. Save pod info to `outputs/runpod_{pod_id}.json`

**Step 3: Connect to Instance**

```bash
# Use SSH command from provisioning output
ssh root@{IP} -p {PORT}
```

**Step 4: Run Automated Setup**

```bash
# On RunPod instance
curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/kwanzaa/main/scripts/runpod_setup.sh | bash

# Or manually:
wget https://raw.githubusercontent.com/YOUR_ORG/kwanzaa/main/scripts/runpod_setup.sh
bash runpod_setup.sh
```

**Step 5: Upload Training Data**

```bash
# From your local machine
scp -P {PORT} \
    data/training/kwanzaa_train.jsonl \
    data/training/kwanzaa_eval.jsonl \
    root@{IP}:/workspace/kwanzaa/data/training/
```

**Step 6: Start Training**

```bash
# On RunPod instance, use screen for persistence
screen -S training

cd /workspace/kwanzaa
python backend/training/train_adapter.py \
    --config backend/training/config/training.yaml \
    --output-dir outputs/kwanzaa-adapter-v1

# Detach from screen: Ctrl+A, D
# Reattach later: screen -r training
```

**Step 7: Monitor Training**

```bash
# In another terminal/screen window
tail -f outputs/kwanzaa-adapter-v1/training.log

# Monitor GPU
watch -n 1 nvidia-smi
```

**Step 8: Download Trained Adapter**

```bash
# From your local machine
scp -P {PORT} -r \
    root@{IP}:/workspace/kwanzaa/outputs/kwanzaa-adapter-v1/final_artifact \
    ./local_outputs/
```

**Step 9: Terminate Instance**

```bash
# From your local machine
python scripts/provision_runpod_training.py --terminate-pod {POD_ID}
```

**Complete documentation:** `docs/training/runpod-setup-guide.md`

---

## Alternative Setup: Hugging Face Spaces

### Prerequisites

1. **HuggingFace Account:**
   - Create account at https://huggingface.co
   - Generate access token (write permissions)
   - Set up payment method for GPU billing

2. **Project Repository:**
   - Have Kwanzaa training code ready
   - Prepare training dataset (JSONL format)
   - Review `/Users/aideveloper/kwanzaa/backend/training/train_adapter.py`

### Step 1: Create HuggingFace Space

```bash
# Method 1: Via Web UI
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Settings:
   - Space name: "kwanzaa-adapter-training"
   - License: Apache 2.0
   - SDK: Gradio (or static for notebooks)
   - Hardware: A10G Large (24GB)
   - Visibility: Private (recommended)

# Method 2: Via CLI
pip install huggingface_hub
huggingface-cli login

huggingface-cli repo create kwanzaa-adapter-training \
  --type space \
  --space_sdk gradio \
  --private
```

### Step 2: Clone Space Repository

```bash
# Clone the space (Git-backed)
git clone https://huggingface.co/spaces/YOUR_USERNAME/kwanzaa-adapter-training
cd kwanzaa-adapter-training

# Copy training code
cp -r /Users/aideveloper/kwanzaa/backend/training/* ./training/
cp /Users/aideveloper/kwanzaa/backend/training/requirements.txt ./requirements.txt
```

### Step 3: Configure Environment

Create `README.md` in Space root:

```yaml
---
title: Kwanzaa Adapter Training
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.13.0
app_file: app.py
pinned: false
license: apache-2.0
hardware: a10g-large
---
```

Create `app.py` (required for Spaces):

```python
import gradio as gr

def dummy_interface():
    return "Training environment ready. Use SSH or Jupyter."

demo = gr.Interface(fn=dummy_interface, inputs=None, outputs="text")
demo.launch()
```

### Step 4: Install Dependencies

Create `.github/workflows/setup.sh` (runs on space startup):

```bash
#!/bin/bash
set -e

echo "Installing training dependencies..."
pip install -r requirements.txt

echo "Verifying GPU availability..."
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"
python -c "import torch; print(f'GPU name: {torch.cuda.get_device_name(0)}')"

echo "Setup complete!"
```

### Step 5: Upload Training Data

```bash
# Option 1: Upload to Space
git lfs install  # Enable large file storage
cp /Users/aideveloper/kwanzaa/data/training/kwanzaa_train.jsonl ./data/
cp /Users/aideveloper/kwanzaa/data/training/kwanzaa_eval.jsonl ./data/
git add data/
git commit -m "Add training dataset"
git push

# Option 2: Upload to HF Dataset (recommended for large files)
huggingface-cli repo create kwanzaa-training-data --type dataset --private
huggingface-cli upload kwanzaa-training-data /Users/aideveloper/kwanzaa/data/training/
```

### Step 6: Run Training

**Via SSH (recommended for long runs):**

```bash
# Enable SSH on your Space (Settings > SSH)
ssh -p 2222 space@YOUR_SPACE_ID.hf.space

# Once connected:
cd /app
python training/train_adapter.py \
  --config training/config/training.yaml \
  --output-dir outputs/kwanzaa-adapter-v1 \
  --wandb-project kwanzaa-training
```

**Via Jupyter Notebook:**

1. Install JupyterLab in Space:
   ```bash
   pip install jupyterlab
   jupyter lab --ip=0.0.0.0 --port=7860 --no-browser
   ```

2. Access via Space URL: `https://YOUR_USERNAME-kwanzaa-adapter-training.hf.space`

3. Create notebook `train.ipynb`:
   ```python
   %load_ext tensorboard
   %tensorboard --logdir outputs/kwanzaa-adapter-v1/tensorboard

   !python training/train_adapter.py \
       --config training/config/training.yaml \
       --output-dir outputs/kwanzaa-adapter-v1
   ```

### Step 7: Monitor Training

**TensorBoard (built-in):**
```bash
tensorboard --logdir outputs/kwanzaa-adapter-v1/tensorboard --bind_all
```

**Weights & Biases (optional):**
```python
# In training.yaml, enable wandb:
monitoring:
  wandb:
    enabled: true
    project: "kwanzaa-training"
    entity: "YOUR_ORG"
```

**Manual Logging:**
```bash
tail -f outputs/kwanzaa-adapter-v1/training.log
```

### Step 8: Save and Publish Adapter

```bash
# After training completes, push adapter to HuggingFace Hub
python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path='outputs/kwanzaa-adapter-v1',
    repo_id='YOUR_ORG/kwanzaa-adapter-v1',
    repo_type='model',
    commit_message='Initial adapter training'
)
"
```

---

## Cost Optimization Strategies

### 1. Use Spot Instances (RunPod)

**Savings:** 30-40% cost reduction
**Risk:** Interruption (mitigated by checkpointing)

```yaml
# In training.yaml, enable frequent checkpointing:
checkpointing:
  save_steps: 50  # Save every 50 steps (default: 200)
  save_total_limit: 5  # Keep more checkpoints
```

### 2. Optimize Batch Size

**Strategy:** Maximize GPU utilization without OOM

```yaml
# Experiment with these values:
training:
  per_device_train_batch_size: 2  # Increase from 1
  gradient_accumulation_steps: 8  # Decrease from 16
  # Effective batch size remains 16
```

Test with:
```bash
python training/train_adapter.py --config training/config/training.yaml --max-steps 10
# Monitor GPU memory: watch -n 1 nvidia-smi
```

### 3. Use Mixed Precision Effectively

**BF16 vs FP16:**
- BF16: Better numerical stability, requires Ampere+ GPUs (A100, A10G, RTX 30xx+)
- FP16: Broader compatibility, may need loss scaling

```yaml
run:
  mixed_precision: "bf16"  # A10G/A100 support
  # mixed_precision: "fp16"  # Fallback for older GPUs
```

### 4. Enable Flash Attention

**Speedup:** 20-30% faster training
**Requirement:** GPU with compute capability >= 8.0 (A100, A10G, RTX 30xx)

```bash
pip install flash-attn --no-build-isolation
```

```yaml
model:
  use_flash_attention: true
```

### 5. Use Packing for Short Sequences

**Efficiency:** Reduces padding waste

```yaml
data:
  packing: true  # Concatenate multiple short samples
  max_seq_length: 2048
```

### 6. Batch Training Runs

**Strategy:** Train multiple adapters in one session

```bash
# Train overnight on HF Space (save costs)
for base_model in "olmo" "llama" "mistral"; do
  python training/train_adapter.py \
    --base-model $base_model \
    --output-dir outputs/kwanzaa-adapter-$base_model
done
```

---

## Monitoring and Logging Setup

### TensorBoard Integration

**Configuration (training.yaml):**
```yaml
monitoring:
  tensorboard:
    enabled: true
    log_dir: "outputs/kwanzaa-adapter-v1/tensorboard"
```

**Access:**
```bash
tensorboard --logdir outputs/kwanzaa-adapter-v1/tensorboard --port 6006
# For HF Spaces: tensorboard --bind_all
```

**Key Metrics to Monitor:**
1. Training Loss (should decrease steadily)
2. Evaluation Loss (should track training loss)
3. Perplexity (should decrease)
4. GPU Memory Usage (should be stable ~10-12GB)
5. Tokens/Second (throughput)
6. Custom Metrics:
   - JSON Valid Rate (target: >95%)
   - Citation Coverage Rate (target: >85%)
   - Refusal Correctness Rate (target: >80%)

### Weights & Biases (Optional)

**Setup:**
```bash
pip install wandb
wandb login  # Enter API key
```

**Configuration:**
```yaml
monitoring:
  wandb:
    enabled: true
    project: "kwanzaa-training"
    entity: "ainative"
    name: "kwanzaa-adapter-v1"
```

**Features:**
- Automatic hyperparameter logging
- Model artifact versioning
- Experiment comparison
- Real-time alerts
- Team collaboration

### Logging Best Practices

**1. Structured Logging:**
```python
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log structured data
logger.info(json.dumps({
    "event": "training_start",
    "base_model": "OLMo-7B",
    "adapter_config": "qlora",
    "timestamp": time.time()
}))
```

**2. Save Logs to Persistent Storage:**
```yaml
# In app.py or training script
log_file = f"outputs/training_{timestamp}.log"
file_handler = logging.FileHandler(log_file)
logger.addHandler(file_handler)
```

**3. Monitor GPU Health:**
```bash
# In background during training
while true; do
  nvidia-smi --query-gpu=timestamp,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv >> gpu_metrics.csv
  sleep 60
done
```

**4. Set Up Alerts:**
```python
# Example: Send alert if training stalls
import time

last_step_time = time.time()

def on_step_end(step, metrics):
    global last_step_time
    current_time = time.time()
    if current_time - last_step_time > 300:  # 5 minutes
        send_alert("Training may be stalled!")
    last_step_time = current_time
```

---

## Backup and Disaster Recovery

### Checkpoint Strategy

**Configuration:**
```yaml
checkpointing:
  save_strategy: "steps"
  save_steps: 200
  save_total_limit: 3  # Keep last 3 checkpoints
  load_best_model_at_end: true
```

**Manual Checkpointing:**
```bash
# During training, sync checkpoints to S3/GCS
while true; do
  aws s3 sync outputs/kwanzaa-adapter-v1/checkpoints s3://kwanzaa-backups/checkpoints/
  sleep 600  # Every 10 minutes
done
```

### Recovery Procedure

**If Training Interrupted:**
```bash
# Resume from last checkpoint
python training/train_adapter.py \
  --config training/config/training.yaml \
  --resume-from-checkpoint outputs/kwanzaa-adapter-v1/checkpoint-600
```

**If Checkpoint Corrupted:**
```bash
# Load previous checkpoint
python training/train_adapter.py \
  --config training/config/training.yaml \
  --resume-from-checkpoint outputs/kwanzaa-adapter-v1/checkpoint-400
```

---

## Validation Checklist

Before starting production training, validate:

- [ ] GPU has >= 12GB VRAM (verify with `nvidia-smi`)
- [ ] CUDA available in PyTorch (`torch.cuda.is_available()`)
- [ ] BF16 supported (`torch.cuda.get_device_capability() >= (8, 0)`)
- [ ] Training dataset loaded successfully
- [ ] Config file validated (all required fields present)
- [ ] Output directory writable
- [ ] Sufficient storage (20GB+ free)
- [ ] TensorBoard accessible
- [ ] Network connectivity to HuggingFace Hub
- [ ] Authentication token set (`HF_TOKEN` env var)
- [ ] Test run completes (10 steps)
- [ ] Checkpoints saving correctly
- [ ] Base model weights verified unchanged

**Quick Validation Script:**
```bash
# Run this before full training
python -c "
import torch
assert torch.cuda.is_available(), 'CUDA not available'
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
print(f'BF16 supported: {torch.cuda.get_device_capability() >= (8, 0)}')
"

python training/train_adapter.py \
  --config training/config/training.yaml \
  --max-steps 10 \
  --output-dir /tmp/test-training
```

---

## Troubleshooting

### Issue: Out of Memory (OOM)

**Symptoms:** CUDA out of memory error during training

**Solutions:**
1. Reduce batch size:
   ```yaml
   per_device_train_batch_size: 1
   gradient_accumulation_steps: 32  # Increase to maintain effective batch size
   ```

2. Enable gradient checkpointing:
   ```yaml
   training:
     gradient_checkpointing: true
   ```

3. Use 4-bit quantization (should already be enabled):
   ```yaml
   adapter:
     quantization:
       load_in_4bit: true
   ```

4. Reduce sequence length:
   ```yaml
   data:
     max_seq_length: 1024  # Down from 2048
   ```

### Issue: Training Slow (Tokens/Sec Low)

**Symptoms:** <100 tokens/second on A100/A10G

**Solutions:**
1. Enable Flash Attention:
   ```bash
   pip install flash-attn
   ```

2. Increase batch size (if VRAM allows):
   ```yaml
   per_device_train_batch_size: 2
   ```

3. Use BF16 instead of FP16:
   ```yaml
   mixed_precision: "bf16"
   ```

4. Enable tensor cores:
   ```yaml
   training:
     tf32: true  # For A100
   ```

### Issue: HuggingFace Hub Upload Fails

**Symptoms:** Network timeout or authentication error

**Solutions:**
1. Verify token:
   ```bash
   huggingface-cli whoami
   ```

2. Use resumable uploads:
   ```python
   from huggingface_hub import HfApi, CommitOperationAdd
   api = HfApi()
   api.create_commit(
       repo_id="YOUR_ORG/kwanzaa-adapter-v1",
       operations=[
           CommitOperationAdd(path_in_repo="adapter_model.safetensors",
                             path_or_fileobj="outputs/adapter_model.safetensors")
       ],
       commit_message="Upload adapter"
   )
   ```

3. Upload via CLI:
   ```bash
   huggingface-cli upload YOUR_ORG/kwanzaa-adapter-v1 outputs/kwanzaa-adapter-v1
   ```

### Issue: Checkpoints Not Saving

**Symptoms:** No checkpoint-* directories in output

**Solutions:**
1. Verify output directory writable:
   ```bash
   touch outputs/kwanzaa-adapter-v1/test.txt
   ```

2. Check disk space:
   ```bash
   df -h outputs/
   ```

3. Enable explicit checkpointing:
   ```python
   trainer.save_model("outputs/kwanzaa-adapter-v1/manual-checkpoint")
   ```

---

## Cost Estimation Spreadsheet

### Budget Scenarios

| Scenario | Environment | GPU | Hours | Cost/Hr | Total Cost | Runs |
|----------|-------------|-----|-------|---------|------------|------|
| **Minimal** | Colab Pro+ | A100 | Unlimited | $50/mo | $50/mo | ~25 runs/mo |
| **Recommended** | HF Spaces | A10G | 135 runs x 2hr | $1.05 | $283.50 | 135 |
| **Optimized** | RunPod Spot | A100 | 180 runs x 2hr | $1.39 | $500 | 180 |
| **Enterprise** | AWS SageMaker | A10G | 140 runs x 2hr | $1.41 | $395 | 140 |

### Per-Run Cost Breakdown

**HuggingFace Spaces (A10G):**
```
Training:          2.0 hrs x $1.05/hr = $2.10
Validation:        0.5 hrs x $1.05/hr = $0.53
Experimentation:   1.0 hrs x $1.05/hr = $1.05
Storage:           50GB  x $0.00/GB   = $0.00 (included)
Network:           10GB  x $0.00/GB   = $0.00 (included)
---
Total per run:                         $3.68
```

**RunPod Spot (A100 80GB):**
```
Training:          2.0 hrs x $1.39/hr = $2.78
Validation:        0.5 hrs x $1.39/hr = $0.70
Experimentation:   1.0 hrs x $1.39/hr = $1.39
Interruption tax:  +10%               = $0.49
Storage:           50GB  x $0.00/GB   = $0.00 (included)
---
Total per run:                         $5.36
```

**Google Colab Pro+ (Monthly):**
```
Subscription:      $49.99/month
Compute units:     ~100 hrs A100 equivalent
Cost per hour:     $0.50/hr effective
Training per run:  2.0 hrs x $0.50/hr = $1.00
Validation:        0.5 hrs x $0.50/hr = $0.25
---
Total per run:                         $1.25
(Best value if used heavily: 25+ runs/month)
```

### Return on Investment

**Assumptions:**
- Training run produces usable adapter: 80% success rate
- Adapter useful for 3 months before retraining needed
- Value per production-quality adapter: $1,000 (time saved vs manual annotation)

**Break-Even Analysis:**
```
Cost per successful adapter (HF Spaces): $3.68 / 0.80 = $4.60
Value created per adapter:                              $1,000
ROI per adapter:                                        21,639%

Budget of $500:
- Successful adapters:        135 runs x 0.80 = 108
- Total value created:        108 x $1,000     = $108,000
- Net value (ROI):            $108,000 - $500  = $107,500
```

---

## Next Steps

### Immediate Actions (This Week)

1. **Set Up HuggingFace Account:**
   - Create account and enable billing
   - Generate access token with write permissions
   - Configure Git credentials

2. **Create Training Space:**
   - Initialize HF Space with A10G hardware
   - Upload training code and dataset
   - Run validation script (10 steps)

3. **Run First Training:**
   - Execute full training run (2 hours)
   - Monitor metrics via TensorBoard
   - Validate adapter output

4. **Document Results:**
   - Record training metrics
   - Test adapter on evaluation set
   - Update issue #47 with findings

### Short Term (Next 2 Weeks)

1. **Optimize Training Pipeline:**
   - Enable Flash Attention
   - Tune batch sizes for performance
   - Set up automated checkpointing

2. **Establish Monitoring:**
   - Configure WandB integration
   - Set up alerting for failures
   - Create dashboard for team

3. **Scale Training:**
   - Train adapters for all base models (OLMo, LLaMA, DeepSeek)
   - Compare performance across environments
   - Document cost actuals vs estimates

### Long Term (Next Month)

1. **Production Deployment:**
   - Automate training pipeline
   - Integrate with CI/CD
   - Set up model registry

2. **Cost Optimization:**
   - Evaluate RunPod for batch jobs
   - Consider reserved instances (if scaling)
   - Implement automatic scaling

3. **Team Enablement:**
   - Create training runbooks
   - Conduct team training session
   - Establish best practices

---

## Appendix A: Environment URLs

**HuggingFace:**
- Spaces: https://huggingface.co/spaces
- Documentation: https://huggingface.co/docs/hub/spaces-gpus
- Pricing: https://huggingface.co/pricing#spaces

**RunPod:**
- Platform: https://www.runpod.io
- GPU Pricing: https://www.runpod.io/gpu-instance/pricing
- Documentation: https://docs.runpod.io

**Google Colab:**
- Colab Pro: https://colab.research.google.com/signup
- Pro+ Upgrade: https://colab.research.google.com/signup/pricing

**AWS SageMaker:**
- Console: https://console.aws.amazon.com/sagemaker
- Pricing: https://aws.amazon.com/sagemaker/pricing
- Documentation: https://docs.aws.amazon.com/sagemaker

**Lambda Labs:**
- Platform: https://lambdalabs.com
- GPU Cloud: https://lambdalabs.com/service/gpu-cloud
- Pricing: https://lambdalabs.com/service/gpu-cloud#pricing

---

## Appendix B: Hardware Specifications

### GPU Comparison

| GPU | VRAM | FP32 TFLOPS | BF16 TFLOPS | TDP | Recommended For |
|-----|------|-------------|-------------|-----|-----------------|
| **T4** | 16GB | 8.1 | N/A | 70W | Development/Testing |
| **A10G** | 24GB | 31.2 | 125 | 150W | **Production Training** |
| **A100-40GB** | 40GB | 19.5 | 312 | 400W | Large Models |
| **A100-80GB** | 80GB | 19.5 | 312 | 400W | Multi-Adapter Batches |
| **RTX 4090** | 24GB | 82.6 | 165 | 450W | Cost/Performance |
| **V100** | 16GB | 15.7 | N/A | 300W | Legacy (avoid) |

**Recommendations:**
- **Kwanzaa Training:** A10G (24GB) - best balance of cost and performance
- **Batch Training:** A100 (80GB) - train multiple adapters simultaneously
- **Experimentation:** T4 (16GB) - sufficient for quick tests

---

## Appendix C: Quick Start Commands

### HuggingFace Spaces Setup

```bash
# 1. Install CLI
pip install huggingface_hub

# 2. Login
huggingface-cli login

# 3. Create space
huggingface-cli repo create kwanzaa-adapter-training --type space --space_sdk gradio

# 4. Clone and setup
git clone https://huggingface.co/spaces/YOUR_USERNAME/kwanzaa-adapter-training
cd kwanzaa-adapter-training
cp -r /Users/aideveloper/kwanzaa/backend/training/* ./

# 5. Configure hardware (in README.md)
echo "hardware: a10g-large" >> README.md

# 6. Push
git add .
git commit -m "Initial setup"
git push

# 7. SSH into space
ssh -p 2222 space@YOUR_SPACE_ID.hf.space

# 8. Run training
python training/train_adapter.py --config training/config/training.yaml
```

### RunPod Setup

```bash
# 1. Create account at runpod.io

# 2. Deploy pod via CLI
pip install runpod
runpod create-pod \
  --name kwanzaa-training \
  --gpu-type "NVIDIA A100" \
  --gpu-count 1 \
  --container-image pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# 3. SSH into pod
runpod ssh kwanzaa-training

# 4. Clone repo and install
git clone YOUR_REPO_URL
cd kwanzaa
pip install -r backend/training/requirements.txt

# 5. Run training
python backend/training/train_adapter.py --config backend/training/config/training.yaml
```

---

**Document Version:** 1.0.0
**Last Updated:** January 16, 2026
**Maintained By:** AINative Studio ML Engineering Team
**Contact:** Issue #47 on GitHub

---
