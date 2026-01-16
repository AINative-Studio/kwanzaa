# Kwanzaa Adapter Training

**EPIC 3A - Hugging Face Environment & Prerequisites**

This directory contains all code and configuration for training parameter-efficient adapters (QLoRA) for the Kwanzaa cultural knowledge platform.

## Quick Start

### 1. Install Dependencies

**Native Installation**:
```bash
# Create virtual environment
cd /Users/aideveloper/kwanzaa/backend
python3 -m venv training_env
source training_env/bin/activate  # Linux/macOS
# or training_env\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r training/requirements.txt

# Verify installation
python training/verify_environment.py
```

**Docker Installation**:
```bash
# Navigate to project root
cd /Users/aideveloper/kwanzaa

# Start containers
docker-compose -f backend/training/docker-compose.yml up -d

# Access training environment
docker-compose -f backend/training/docker-compose.yml exec training bash

# Verify installation
python /workspace/verify_environment.py
```

### 2. Configure Training

```bash
# Configure accelerate (native only)
accelerate config

# Login to Hugging Face (optional, for gated models)
huggingface-cli login

# Login to Weights & Biases (optional, for experiment tracking)
wandb login
```

### 3. Run Training

```bash
# Basic training
python backend/training/train_adapter.py \
  --config backend/training/config/mistral_qlora.yaml

# With custom parameters
python backend/training/train_adapter.py \
  --config backend/training/config/mistral_qlora.yaml \
  --output_dir ./adapters/my-adapter \
  --num_epochs 3 \
  --learning_rate 2e-4
```

## Directory Structure

```
backend/training/
├── README.md                    # This file
├── requirements.txt             # Pinned dependencies (40+ packages)
├── verify_environment.py        # Environment verification script
├── train_adapter.py            # Main training script
├── __init__.py                 # Package initialization
│
├── config/                     # Training configurations
│   ├── mistral_qlora.yaml     # Mistral 7B with QLoRA
│   └── ...                     # Other model configs
│
├── utils/                      # Training utilities
│   ├── data_loader.py         # Dataset loading
│   ├── trainer.py             # Custom trainer
│   ├── evaluation.py          # Evaluation metrics
│   └── callbacks.py           # Training callbacks
│
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker orchestration
└── .dockerignore              # Docker build optimization
```

## Available Scripts

### verify_environment.py

Comprehensive environment verification:

```bash
# Basic check
python backend/training/verify_environment.py

# Verbose mode (detailed GPU info)
python backend/training/verify_environment.py --verbose
```

Checks:
- Python version (3.9+)
- System resources (disk, memory)
- PyTorch and CUDA
- All required packages
- GPU availability and capabilities

### train_adapter.py

Main training script for QLoRA adapters:

```bash
python backend/training/train_adapter.py --help
```

## Configuration Files

Training configurations are stored in `config/` directory:

- `mistral_qlora.yaml` - Mistral 7B with QLoRA (4-bit)
- Additional configs for other models (to be added)

Example config structure:
```yaml
model:
  name: mistralai/Mistral-7B-v0.1
  quantization: 4bit

lora:
  r: 16
  alpha: 32
  dropout: 0.05

training:
  batch_size: 4
  learning_rate: 2e-4
  epochs: 3
```

## Docker Support

### Build Image

```bash
docker build -t kwanzaa-training:latest -f backend/training/Dockerfile .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose -f backend/training/docker-compose.yml up -d

# View logs
docker-compose -f backend/training/docker-compose.yml logs -f

# Access container
docker-compose -f backend/training/docker-compose.yml exec training bash

# Stop services
docker-compose -f backend/training/docker-compose.yml down
```

### Run with Docker

```bash
# GPU mode
docker run --gpus all -v $(pwd):/workspace -it kwanzaa-training:latest

# CPU mode
docker run -v $(pwd):/workspace -it kwanzaa-training:latest

# With environment variables
docker run --gpus all \
  -v $(pwd):/workspace \
  -e HF_TOKEN=your_token \
  -e WANDB_API_KEY=your_key \
  -it kwanzaa-training:latest
```

## Dependencies

### Core ML Frameworks
- PyTorch 2.1.2 (CUDA 11.8)
- Transformers 4.37.2
- Datasets 2.16.1
- Accelerate 0.26.1

### PEFT & Quantization
- PEFT 0.8.2 (LoRA/QLoRA)
- Bitsandbytes 0.42.0 (4-bit quantization)

### Training Utilities
- TRL 0.7.10 (RLHF, DPO, PPO)
- Optimum 1.16.2
- SentencePiece 0.1.99

### Experiment Tracking
- Weights & Biases 0.16.2
- TensorBoard 2.15.1
- MLflow 2.10.0

See `requirements.txt` for complete list.

## Documentation

Comprehensive documentation available in `docs/training/`:

- **[Installation Guide](../../docs/training/installation-guide.md)** (626 lines)
  - Prerequisites and system requirements
  - Platform-specific installation
  - Troubleshooting
  - Best practices

- **[Docker Setup Guide](../../docs/training/docker-setup.md)** (500+ lines)
  - Docker prerequisites
  - Building and running containers
  - GPU configuration
  - Volume management
  - Troubleshooting

- **[Adapter Training Guide](../../docs/training/adapter-training-guide.md)**
  - Training process
  - Hyperparameter tuning
  - Model evaluation
  - Best practices

- **[Dataset Preparation](../../docs/training/dataset-preparation.md)**
  - Data format requirements
  - Preprocessing steps
  - Quality checks

- **[Quick Start](../../docs/training/quick-start.md)**
  - 5-minute setup
  - First training run
  - Common workflows

- **[Dependency Summary](../../docs/training/dependency-installation-summary.md)**
  - Complete implementation details
  - Testing results
  - Platform support

## System Requirements

### Minimum
- Python 3.9+
- 16GB RAM
- 10GB disk space
- 4+ CPU cores

### Recommended (GPU Training)
- Python 3.10 or 3.11
- 32GB+ RAM
- 50GB+ disk space (SSD)
- 8+ CPU cores
- NVIDIA GPU with 16GB+ VRAM
- CUDA 11.8 or 12.1+

### Supported Platforms
- Linux (Ubuntu 20.04+, RHEL 8+, Debian 11+)
- macOS 11+ (including Apple Silicon)
- Windows 10+ with WSL2
- Docker (all platforms)

## GPU Support

### NVIDIA GPUs
- CUDA 11.8 or 12.1+
- Compute Capability 7.0+ (V100, T4, RTX series, A100, H100)
- 8GB+ VRAM (16GB+ recommended)

### Apple Silicon
- M1/M2/M3 chips
- MPS (Metal Performance Shaders) backend
- Note: bitsandbytes not available (use LoRA instead of QLoRA)

### CPU-Only
- Supported but very slow
- Not recommended for production training
- Useful for testing and development

## Environment Variables

### Required (Optional)
None required by default.

### Recommended
```bash
# Hugging Face token (for gated models)
export HF_TOKEN=your_token_here

# Weights & Biases API key
export WANDB_API_KEY=your_key_here

# Disable W&B for offline training
export WANDB_MODE=offline
```

### Performance Optimization
```bash
# Cache directories
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache/transformers
export HF_DATASETS_CACHE=/path/to/cache/datasets

# GPU configuration
export CUDA_VISIBLE_DEVICES=0,1  # Use specific GPUs
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# CPU threads
export OMP_NUM_THREADS=8
export TOKENIZERS_PARALLELISM=false
```

## Troubleshooting

### Common Issues

**Issue**: Dependencies fail to install
```bash
# Solution: Upgrade pip and try again
pip install --upgrade pip setuptools wheel
pip install -r training/requirements.txt
```

**Issue**: CUDA out of memory
```bash
# Solutions:
# 1. Reduce batch size in config
# 2. Enable gradient checkpointing
# 3. Use QLoRA (4-bit) instead of LoRA
# 4. Use smaller model
```

**Issue**: GPU not detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check CUDA version
nvidia-smi
```

**Issue**: bitsandbytes not installing (macOS)
```bash
# Expected on macOS - skip bitsandbytes
# Use LoRA instead of QLoRA
grep -v "bitsandbytes" requirements.txt | pip install -r /dev/stdin
```

For more troubleshooting, see:
- [Installation Guide Troubleshooting](../../docs/training/installation-guide.md#troubleshooting)
- [Docker Setup Troubleshooting](../../docs/training/docker-setup.md#troubleshooting)

## Testing

### Run Verification Script

```bash
# Basic check
python backend/training/verify_environment.py

# Verbose output
python backend/training/verify_environment.py --verbose
```

### Expected Output

```
================================================================================
  Kwanzaa Training Environment Verification
================================================================================

✓ Python 3.10.0 (OK)
✓ Disk Space: 50.0 GB free (OK)
✓ Memory: 32.0 GB total, 16.0 GB available (OK)
✓ PyTorch imported successfully
  - Version: 2.1.2
  - CUDA Available: True
  - CUDA Version: 11.8
  - GPU Count: 1

✓ ALL CHECKS PASSED!

Your environment is ready for adapter training.
```

## Next Steps

After successful setup:

1. **Verify Environment**
   ```bash
   python backend/training/verify_environment.py
   ```

2. **Configure Training**
   ```bash
   accelerate config  # Native installation only
   ```

3. **Download Model** (optional, auto-downloads during training)
   ```bash
   python -c "from transformers import AutoModel; AutoModel.from_pretrained('mistralai/Mistral-7B-v0.1')"
   ```

4. **Prepare Dataset**
   - See [Dataset Preparation Guide](../../docs/training/dataset-preparation.md)

5. **Start Training**
   ```bash
   python backend/training/train_adapter.py --config backend/training/config/mistral_qlora.yaml
   ```

6. **Monitor Training**
   - TensorBoard: `tensorboard --logdir=./logs`
   - W&B: Check your wandb.ai dashboard

## Support

For issues or questions:

1. **Check Documentation**
   - [Installation Guide](../../docs/training/installation-guide.md)
   - [Docker Setup](../../docs/training/docker-setup.md)
   - [Training Guide](../../docs/training/adapter-training-guide.md)

2. **Run Verification**
   ```bash
   python backend/training/verify_environment.py --verbose
   ```

3. **Create GitHub Issue**
   Include:
   - Python version: `python --version`
   - PyTorch version: `python -c "import torch; print(torch.__version__)"`
   - CUDA version: `nvidia-smi` (if GPU)
   - Verification output
   - Full error traceback

## Contributing

When contributing to training code:

1. Follow the project's coding standards
2. Add tests for new features
3. Update documentation
4. Run verification before submitting PR

## License

See [LICENSE](../../LICENSE) in project root.

---

## Quick Reference

### Commands

```bash
# Install dependencies
pip install -r training/requirements.txt

# Verify environment
python training/verify_environment.py

# Train adapter
python training/train_adapter.py --config training/config/mistral_qlora.yaml

# Docker build
docker build -t kwanzaa-training:latest -f training/Dockerfile .

# Docker compose
docker-compose -f training/docker-compose.yml up -d
```

### Files

- `requirements.txt` - Dependencies
- `verify_environment.py` - Verification
- `train_adapter.py` - Training script
- `config/*.yaml` - Training configs
- `Dockerfile` - Docker image
- `docker-compose.yml` - Orchestration

### Documentation

- Installation: `../../docs/training/installation-guide.md`
- Docker: `../../docs/training/docker-setup.md`
- Training: `../../docs/training/adapter-training-guide.md`
- Dataset: `../../docs/training/dataset-preparation.md`

---

**Last Updated**: 2026-01-16
**Issue**: #51 - E3A-US5 - Install Training Dependencies
**EPIC**: 3A - Hugging Face Environment & Prerequisites
