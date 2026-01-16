# Training Dependencies Installation Guide

**EPIC 3A - Hugging Face Environment & Prerequisites**
**Issue #51: E3A-US5 - Install Training Dependencies**

This guide provides comprehensive instructions for installing all Python dependencies required for adapter training in the Kwanzaa project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Method 1: Quick Installation (Recommended)](#method-1-quick-installation-recommended)
  - [Method 2: Platform-Specific Installation](#method-2-platform-specific-installation)
  - [Method 3: CPU-Only Installation](#method-3-cpu-only-installation)
- [Environment Verification](#environment-verification)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [Dependency Overview](#dependency-overview)

---

## Prerequisites

### Python Version

- **Required**: Python 3.9 or higher
- **Recommended**: Python 3.10 or 3.11
- **Not supported**: Python 3.8 or below, Python 3.12+ (limited library support)

Check your Python version:

```bash
python --version
# or
python3 --version
```

### CUDA Requirements (for GPU training)

For GPU-accelerated training, you need:

- **CUDA Toolkit**: Version 11.8 or 12.1+
- **NVIDIA GPU**: Compute Capability 7.0+ (V100, T4, RTX 20xx/30xx/40xx, A100, H100)
- **GPU Memory**: Minimum 8GB VRAM (16GB+ recommended for QLoRA)

Check CUDA version:

```bash
nvidia-smi
# or
nvcc --version
```

### Disk Space

- **Minimum**: 10GB free space
- **Recommended**: 50GB+ for models, datasets, and checkpoints

---

## System Requirements

### Minimum Requirements

- **RAM**: 16GB
- **GPU**: Optional, but strongly recommended (8GB+ VRAM)
- **CPU**: 4+ cores
- **OS**: Linux (Ubuntu 20.04+), macOS 11+, Windows 10+ (with WSL2)

### Recommended Requirements

- **RAM**: 32GB+
- **GPU**: NVIDIA GPU with 16GB+ VRAM (RTX 3090, A100, etc.)
- **CPU**: 8+ cores
- **SSD**: For faster data loading
- **OS**: Ubuntu 22.04 LTS

---

## Installation Methods

### Method 1: Quick Installation (Recommended)

This method works for most Linux systems with CUDA 11.8 installed.

#### Step 1: Create Virtual Environment

```bash
# Navigate to the project root
cd /Users/aideveloper/kwanzaa/backend

# Create a virtual environment
python3 -m venv training_env

# Activate the environment
source training_env/bin/activate  # Linux/macOS
# or
training_env\Scripts\activate  # Windows
```

#### Step 2: Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

#### Step 3: Install Training Dependencies

```bash
# Install from requirements file
pip install -r training/requirements.txt
```

#### Step 4: Verify Installation

```bash
# Run verification script
python training/verify_environment.py
```

---

### Method 2: Platform-Specific Installation

#### Linux with CUDA 11.8

```bash
# Step 1: Create and activate virtual environment
python3 -m venv training_env
source training_env/bin/activate

# Step 2: Upgrade pip
pip install --upgrade pip setuptools wheel

# Step 3: Install PyTorch for CUDA 11.8
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# Step 4: Install remaining dependencies
pip install -r training/requirements.txt
```

#### Linux with CUDA 12.1+

```bash
# Step 1: Create and activate virtual environment
python3 -m venv training_env
source training_env/bin/activate

# Step 2: Upgrade pip
pip install --upgrade pip setuptools wheel

# Step 3: Install PyTorch for CUDA 12.1
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu121

# Step 4: Install remaining dependencies
pip install -r training/requirements.txt
```

#### macOS (Apple Silicon M1/M2/M3)

```bash
# Step 1: Create and activate virtual environment
python3 -m venv training_env
source training_env/bin/activate

# Step 2: Upgrade pip
pip install --upgrade pip setuptools wheel

# Step 3: Install PyTorch (MPS backend for Apple Silicon)
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2

# Step 4: Install remaining dependencies (skip bitsandbytes)
pip install -r training/requirements.txt || true
# Note: bitsandbytes may not install on macOS, which is expected

# Step 5: Verify MPS availability
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

#### Windows with WSL2 (Recommended)

```bash
# Install WSL2 and Ubuntu 22.04 first
# Then follow Linux with CUDA instructions above

# Alternative: Native Windows (not recommended for production)
# Step 1: Create virtual environment
python -m venv training_env
training_env\Scripts\activate

# Step 2: Upgrade pip
pip install --upgrade pip setuptools wheel

# Step 3: Install PyTorch for CUDA 11.8
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# Step 4: Install remaining dependencies
pip install -r training/requirements.txt
```

---

### Method 3: CPU-Only Installation

For systems without GPU or for testing purposes.

```bash
# Step 1: Create and activate virtual environment
python3 -m venv training_env
source training_env/bin/activate  # Linux/macOS

# Step 2: Upgrade pip
pip install --upgrade pip setuptools wheel

# Step 3: Install PyTorch CPU version
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# Step 4: Install remaining dependencies (skip bitsandbytes)
grep -v "bitsandbytes" training/requirements.txt > requirements_cpu.txt
pip install -r requirements_cpu.txt

# Note: CPU training is much slower and not recommended for production
```

---

## Environment Verification

After installation, verify your environment:

### Quick Verification

```bash
python training/verify_environment.py
```

The script checks:
- Python version
- PyTorch installation and version
- CUDA/GPU availability
- All required packages
- Version compatibility
- Import verification

### Manual Verification

#### Check PyTorch and CUDA

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"
```

Expected output (GPU):
```
PyTorch: 2.1.2
CUDA Available: True
CUDA Version: 11.8
```

#### Check Transformers

```bash
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

Expected output:
```
Transformers: 4.37.2
```

#### Check PEFT and TRL

```bash
python -c "import peft; import trl; print(f'PEFT: {peft.__version__}'); print(f'TRL: {trl.__version__}')"
```

Expected output:
```
PEFT: 0.8.2
TRL: 0.7.10
```

#### Check GPU Memory

```bash
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: CUDA Version Mismatch

**Error**: `The detected CUDA version mismatches the version that was used to compile PyTorch`

**Solution**:
```bash
# Check your CUDA version
nvidia-smi

# Install PyTorch matching your CUDA version
# For CUDA 11.8:
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cu121
```

#### Issue 2: bitsandbytes Installation Failure

**Error**: `Could not find a version that satisfies the requirement bitsandbytes`

**Solution**:
```bash
# For Linux with CUDA:
pip install bitsandbytes==0.42.0

# For macOS or CPU-only:
# Skip bitsandbytes - it's only needed for quantization
pip install -r training/requirements.txt --no-deps
# Then manually install other packages
```

#### Issue 3: Out of Memory (OOM) Errors

**Error**: `CUDA out of memory`

**Solution**:
```bash
# Check available GPU memory
nvidia-smi

# Solutions:
# 1. Reduce batch size in training config
# 2. Enable gradient checkpointing
# 3. Use QLoRA (4-bit quantization) instead of LoRA
# 4. Reduce sequence length
# 5. Use a smaller model
```

#### Issue 4: Import Errors

**Error**: `ModuleNotFoundError: No module named 'transformers'`

**Solution**:
```bash
# Ensure virtual environment is activated
source training_env/bin/activate

# Reinstall dependencies
pip install -r training/requirements.txt --force-reinstall
```

#### Issue 5: flash-attn Compilation Failure

**Error**: `Failed building wheel for flash-attn`

**Solution**:
```bash
# flash-attn is optional and requires compilation
# Skip it if installation fails:
# 1. Comment out flash-attn in requirements.txt
# 2. Or install without it:
grep -v "flash-attn" training/requirements.txt | pip install -r /dev/stdin

# Note: You'll lose 2-3x speedup but training will still work
```

#### Issue 6: Transformers Version Conflicts

**Error**: `ERROR: pip's dependency resolver does not currently take into account...`

**Solution**:
```bash
# Use --no-deps flag and install in specific order
pip install torch==2.1.2
pip install transformers==4.37.2
pip install peft==0.8.2
pip install -r training/requirements.txt --no-deps
```

#### Issue 7: SSL Certificate Errors

**Error**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution**:
```bash
# For macOS:
/Applications/Python\ 3.10/Install\ Certificates.command

# For Linux/WSL:
pip install --upgrade certifi
```

#### Issue 8: Slow Download Speeds

**Solution**:
```bash
# Use Hugging Face mirror (China)
export HF_ENDPOINT=https://hf-mirror.com

# Or use pip cache
pip install -r training/requirements.txt --cache-dir=/tmp/pip-cache
```

---

## Advanced Configuration

### Environment Variables

Create a `.env` file in `/Users/aideveloper/kwanzaa/backend/training/`:

```bash
# Hugging Face Hub Token (for private models)
HF_TOKEN=your_token_here

# Weights & Biases API Key
WANDB_API_KEY=your_wandb_key_here

# Cache directories
HF_HOME=/path/to/huggingface/cache
TRANSFORMERS_CACHE=/path/to/transformers/cache

# Training settings
CUDA_VISIBLE_DEVICES=0,1,2,3  # GPUs to use
OMP_NUM_THREADS=8  # CPU threads
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512  # Memory allocation
```

### Hugging Face Login

```bash
# Login to Hugging Face Hub (for downloading gated models)
huggingface-cli login

# Or use environment variable
export HF_TOKEN=your_token_here
```

### Weights & Biases Setup

```bash
# Login to W&B
wandb login

# Or use environment variable
export WANDB_API_KEY=your_key_here

# Disable W&B (for offline training)
export WANDB_MODE=offline
```

### Flash Attention 2 (Optional)

For 2-3x training speedup on compatible GPUs:

```bash
# Requirements:
# - NVIDIA GPU with Compute Capability 8.0+ (A100, H100, RTX 30xx/40xx)
# - CUDA 11.8+

pip install flash-attn==2.5.0 --no-build-isolation
```

### DeepSpeed (Optional)

For multi-GPU distributed training:

```bash
pip install deepspeed==0.12.6

# Test DeepSpeed
ds_report
```

---

## Dependency Overview

### Core ML Frameworks

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| torch | 2.1.2 | Deep learning framework | Yes |
| transformers | 4.37.2 | Pre-trained models | Yes |
| datasets | 2.16.1 | Dataset loading | Yes |
| accelerate | 0.26.1 | Distributed training | Yes |

### PEFT & Quantization

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| peft | 0.8.2 | LoRA/QLoRA adapters | Yes |
| bitsandbytes | 0.42.0 | 4-bit quantization | Yes (GPU only) |

### Training Utilities

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| trl | 0.7.10 | RLHF, DPO, PPO | Yes |
| optimum | 1.16.2 | Model optimization | Yes |
| sentencepiece | 0.1.99 | Tokenization | Yes |

### Experiment Tracking

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| wandb | 0.16.2 | Experiment tracking | Optional |
| tensorboard | 2.15.1 | Visualization | Yes |
| mlflow | 2.10.0 | Model registry | Optional |

### Data Processing

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| numpy | 1.26.3 | Numerical computing | Yes |
| pandas | 2.1.4 | Data manipulation | Yes |
| scikit-learn | 1.4.0 | ML utilities | Yes |

### Evaluation

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| evaluate | 0.4.1 | Metrics | Yes |
| rouge-score | 0.1.2 | Summarization metrics | Yes |
| sacrebleu | 2.4.0 | Translation metrics | Yes |
| nltk | 3.8.1 | NLP utilities | Yes |

---

## Best Practices

### 1. Use Virtual Environments

Always create isolated environments for different projects:

```bash
# Create
python3 -m venv training_env

# Activate
source training_env/bin/activate

# Deactivate
deactivate
```

### 2. Pin Dependencies

Always use pinned versions in production (already done in `requirements.txt`).

### 3. Cache Models and Datasets

```bash
# Set cache directory to avoid re-downloading
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

### 4. Monitor GPU Usage

```bash
# Real-time monitoring
watch -n 1 nvidia-smi

# Or use gpustat
pip install gpustat
gpustat -i 1
```

### 5. Use Mixed Precision Training

Already configured in `accelerate`, but ensure it's enabled:

```bash
accelerate config
# Select "fp16" or "bf16" for mixed precision
```

---

## Next Steps

After successful installation:

1. **Verify Environment**: Run `python training/verify_environment.py`
2. **Download Model**: See `/Users/aideveloper/kwanzaa/docs/training/quick-start.md`
3. **Prepare Dataset**: See `/Users/aideveloper/kwanzaa/docs/training/dataset-preparation.md`
4. **Start Training**: See `/Users/aideveloper/kwanzaa/docs/training/adapter-training-guide.md`

---

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review [Common Issues](./adapter-compatibility-known-issues.md)
3. Create an issue on GitHub with:
   - Python version (`python --version`)
   - PyTorch version (`python -c "import torch; print(torch.__version__)"`)
   - CUDA version (`nvidia-smi`)
   - Full error traceback
   - Output of `pip list`

---

## References

- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [Accelerate Documentation](https://huggingface.co/docs/accelerate)
- [TRL Documentation](https://huggingface.co/docs/trl)

---

**Last Updated**: 2026-01-16
**Issue**: #51 - E3A-US5 - Install Training Dependencies
**EPIC**: 3A - Hugging Face Environment & Prerequisites
