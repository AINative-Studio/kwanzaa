# Docker Setup for Training Environment

**EPIC 3A - Hugging Face Environment & Prerequisites**
**Issue #51: E3A-US5 - Install Training Dependencies**

This guide explains how to use Docker to run the Kwanzaa training environment in a containerized setup with GPU support.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building the Image](#building-the-image)
- [Running the Container](#running-the-container)
- [Docker Compose Usage](#docker-compose-usage)
- [GPU Configuration](#gpu-configuration)
- [Volume Mounts](#volume-mounts)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Prerequisites

### Required Software

1. **Docker**: Version 20.10+
   - [Install Docker](https://docs.docker.com/get-docker/)
   - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **NVIDIA Docker Runtime** (for GPU support):
   - [Install NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

3. **Docker Compose**: Version 1.29+ (usually included with Docker Desktop)

### Hardware Requirements

- **For GPU training**:
  - NVIDIA GPU with Compute Capability 7.0+ (V100, T4, RTX series, A100, H100)
  - 8GB+ VRAM (16GB+ recommended)
  - CUDA 11.8 compatible drivers

- **For CPU training**:
  - 8+ CPU cores
  - 16GB+ RAM
  - Not recommended for production (very slow)

### Verify Prerequisites

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Check NVIDIA Docker runtime (for GPU)
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

---

## Quick Start

The fastest way to get started with Docker:

```bash
# Navigate to project root
cd /Users/aideveloper/kwanzaa

# Build and start containers
docker-compose -f backend/training/docker-compose.yml up -d

# Access training container
docker-compose -f backend/training/docker-compose.yml exec training bash

# Verify environment inside container
python /workspace/verify_environment.py

# Start training (example)
python backend/training/train_adapter.py --config backend/training/config/mistral_qlora.yaml
```

---

## Building the Image

### Build with Docker

```bash
# Navigate to project root
cd /Users/aideveloper/kwanzaa

# Build the image
docker build -t kwanzaa-training:latest -f backend/training/Dockerfile .

# Build with custom tag
docker build -t kwanzaa-training:v1.0 -f backend/training/Dockerfile .

# Build with build arguments
docker build \
  --build-arg CUDA_VERSION=11.8 \
  --build-arg PYTHON_VERSION=3.10 \
  -t kwanzaa-training:latest \
  -f backend/training/Dockerfile .
```

### Build with Docker Compose

```bash
# Build all services
docker-compose -f backend/training/docker-compose.yml build

# Build with no cache
docker-compose -f backend/training/docker-compose.yml build --no-cache

# Pull pre-built image (if available)
docker pull kwanzaa-training:latest
```

### Verify Build

```bash
# List images
docker images | grep kwanzaa-training

# Inspect image
docker inspect kwanzaa-training:latest

# Check image size
docker images kwanzaa-training:latest --format "{{.Size}}"
```

---

## Running the Container

### Run with Docker

#### GPU Mode (Recommended)

```bash
# Run with all GPUs
docker run --gpus all \
  -v $(pwd):/workspace \
  -it kwanzaa-training:latest

# Run with specific GPU
docker run --gpus device=0 \
  -v $(pwd):/workspace \
  -it kwanzaa-training:latest

# Run with multiple GPUs
docker run --gpus '"device=0,1"' \
  -v $(pwd):/workspace \
  -it kwanzaa-training:latest
```

#### CPU Mode

```bash
# Run without GPU
docker run \
  -v $(pwd):/workspace \
  -it kwanzaa-training:latest
```

#### With Environment Variables

```bash
# Run with Hugging Face token
docker run --gpus all \
  -v $(pwd):/workspace \
  -e HF_TOKEN=your_token_here \
  -e WANDB_API_KEY=your_wandb_key \
  -it kwanzaa-training:latest
```

#### Detached Mode

```bash
# Run in background
docker run --gpus all \
  -v $(pwd):/workspace \
  --name kwanzaa-training \
  -d kwanzaa-training:latest

# Attach to running container
docker exec -it kwanzaa-training bash

# View logs
docker logs kwanzaa-training

# Stop container
docker stop kwanzaa-training
```

### Run with Docker Compose

```bash
# Start all services
docker-compose -f backend/training/docker-compose.yml up -d

# Start specific service
docker-compose -f backend/training/docker-compose.yml up -d training

# View logs
docker-compose -f backend/training/docker-compose.yml logs -f training

# Execute command in running container
docker-compose -f backend/training/docker-compose.yml exec training python verify_environment.py

# Access container shell
docker-compose -f backend/training/docker-compose.yml exec training bash

# Stop services
docker-compose -f backend/training/docker-compose.yml down

# Stop and remove volumes
docker-compose -f backend/training/docker-compose.yml down -v
```

---

## Docker Compose Usage

### Configuration

The `docker-compose.yml` file includes:

1. **Training Service**: Main container for model training
2. **TensorBoard Service**: Optional visualization service
3. **Named Volumes**: Persistent storage for cache and outputs
4. **Network**: Bridge network for service communication

### Common Commands

```bash
# Start services
docker-compose -f backend/training/docker-compose.yml up -d

# Stop services
docker-compose -f backend/training/docker-compose.yml down

# Restart services
docker-compose -f backend/training/docker-compose.yml restart

# View service status
docker-compose -f backend/training/docker-compose.yml ps

# View logs
docker-compose -f backend/training/docker-compose.yml logs -f

# Scale services (if needed)
docker-compose -f backend/training/docker-compose.yml up -d --scale training=2

# Remove all containers and volumes
docker-compose -f backend/training/docker-compose.yml down -v --remove-orphans
```

### Access TensorBoard

```bash
# TensorBoard is available at http://localhost:6007
# Logs are mounted from training container

# View TensorBoard logs
docker-compose -f backend/training/docker-compose.yml logs tensorboard
```

---

## GPU Configuration

### Check GPU Availability

```bash
# Inside container
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"

# From host
docker-compose -f backend/training/docker-compose.yml exec training nvidia-smi
```

### Configure GPU Usage

#### Use Specific GPU

```bash
# Set CUDA_VISIBLE_DEVICES in docker-compose.yml
environment:
  - CUDA_VISIBLE_DEVICES=0  # Use only GPU 0

# Or at runtime
docker run --gpus device=1 -v $(pwd):/workspace -it kwanzaa-training:latest
```

#### Use Multiple GPUs

```bash
# All GPUs
environment:
  - CUDA_VISIBLE_DEVICES=0,1,2,3

# Or at runtime
docker run --gpus all -v $(pwd):/workspace -it kwanzaa-training:latest
```

#### GPU Memory Management

```bash
# Set memory allocation strategy
environment:
  - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

---

## Volume Mounts

### Default Mounts

The docker-compose configuration includes:

1. **Project Directory**: `/workspace` (entire project)
2. **Hugging Face Cache**: `/workspace/.cache/huggingface` (persistent)
3. **Training Outputs**: `/workspace/adapters` (persistent)
4. **Logs**: `/workspace/logs` (persistent)

### Custom Mounts

```bash
# Mount custom data directory
docker run --gpus all \
  -v $(pwd):/workspace \
  -v /path/to/data:/workspace/data \
  -it kwanzaa-training:latest

# Mount custom model directory
docker run --gpus all \
  -v $(pwd):/workspace \
  -v /path/to/models:/workspace/.cache/huggingface \
  -it kwanzaa-training:latest
```

### Volume Management

```bash
# List volumes
docker volume ls | grep kwanzaa

# Inspect volume
docker volume inspect kwanzaa_huggingface-cache

# Remove unused volumes
docker volume prune

# Backup volume
docker run --rm \
  -v kwanzaa_huggingface-cache:/data \
  -v $(pwd)/backup:/backup \
  ubuntu tar czf /backup/cache-backup.tar.gz /data
```

---

## Environment Variables

### Required Variables

```bash
# None required by default
```

### Recommended Variables

```bash
# Hugging Face token (for gated models)
HF_TOKEN=your_token_here

# Weights & Biases API key
WANDB_API_KEY=your_wandb_key

# Disable W&B for offline training
WANDB_MODE=offline
```

### Optional Variables

```bash
# Custom cache directories
HF_HOME=/custom/cache/path
TRANSFORMERS_CACHE=/custom/cache/transformers
HF_DATASETS_CACHE=/custom/cache/datasets

# GPU configuration
CUDA_VISIBLE_DEVICES=0,1
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Performance
OMP_NUM_THREADS=8
TOKENIZERS_PARALLELISM=false

# Hugging Face mirror (China)
HF_ENDPOINT=https://hf-mirror.com
```

### Set Variables

#### In docker-compose.yml

```yaml
environment:
  - HF_TOKEN=your_token_here
  - WANDB_API_KEY=your_key_here
```

#### With .env File

```bash
# Create .env file in project root
echo "HF_TOKEN=your_token_here" > .env
echo "WANDB_API_KEY=your_key_here" >> .env

# Docker Compose will automatically load .env
docker-compose -f backend/training/docker-compose.yml up -d
```

#### At Runtime

```bash
docker run --gpus all \
  -v $(pwd):/workspace \
  -e HF_TOKEN=your_token_here \
  -it kwanzaa-training:latest
```

---

## Troubleshooting

### Issue 1: GPU Not Detected

**Error**: `CUDA not available` inside container

**Solution**:

```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# If fails, install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Verify
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Issue 2: Out of Memory

**Error**: `RuntimeError: CUDA out of memory`

**Solution**:

```bash
# Reduce batch size in training config
# Enable gradient checkpointing
# Use smaller model or QLoRA quantization

# Check GPU memory
docker-compose -f backend/training/docker-compose.yml exec training nvidia-smi

# Set memory allocation
environment:
  - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

### Issue 3: Slow Build Times

**Solution**:

```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker build -t kwanzaa-training:latest -f backend/training/Dockerfile .

# Or with docker-compose
DOCKER_BUILDKIT=1 docker-compose -f backend/training/docker-compose.yml build
```

### Issue 4: Permission Errors

**Error**: `Permission denied` when accessing files

**Solution**:

```bash
# Run container as current user
docker run --gpus all \
  -v $(pwd):/workspace \
  --user $(id -u):$(id -g) \
  -it kwanzaa-training:latest

# Fix permissions on host
sudo chown -R $(id -u):$(id -g) /path/to/files
```

### Issue 5: Image Size Too Large

**Solution**:

```bash
# Check image size
docker images kwanzaa-training:latest

# Reduce size with multi-stage builds
# Clean up caches in Dockerfile
# Use .dockerignore to exclude unnecessary files

# Remove unused layers
docker image prune -a
```

---

## Best Practices

### 1. Use Named Volumes

```yaml
volumes:
  huggingface-cache:
    driver: local
```

Prevents re-downloading models on container restart.

### 2. Cache Layer Optimization

Order Dockerfile commands from least to most frequently changed:

```dockerfile
# Good: Dependencies first (cached)
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Then: Application code (changes often)
COPY backend/ /workspace/backend/
```

### 3. Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '8'
      memory: 32G
    reservations:
      cpus: '4'
      memory: 16G
```

### 4. Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; assert torch.cuda.is_available()" || exit 1
```

### 5. Security

```bash
# Don't include secrets in images
# Use environment variables or Docker secrets
# Run as non-root user when possible

# Scan for vulnerabilities
docker scan kwanzaa-training:latest
```

### 6. Multi-Stage Builds

For production, use multi-stage builds to reduce image size:

```dockerfile
# Builder stage
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 AS builder
# ... install dependencies ...

# Runtime stage
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
COPY --from=builder /usr/local /usr/local
# ... copy only necessary files ...
```

---

## Next Steps

After successful Docker setup:

1. **Verify Environment**: `python /workspace/verify_environment.py`
2. **Run Quick Test**: See [Quick Start Guide](./quick-start.md)
3. **Start Training**: See [Adapter Training Guide](./adapter-training-guide.md)
4. **Monitor Training**: Access TensorBoard at `http://localhost:6007`

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PyTorch Docker Guide](https://pytorch.org/get-started/pytorch-docker/)

---

**Last Updated**: 2026-01-16
**Issue**: #51 - E3A-US5 - Install Training Dependencies
**EPIC**: 3A - Hugging Face Environment & Prerequisites
