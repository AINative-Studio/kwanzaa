# Kwanzaa Adapter Training Dockerfile
# EPIC 3A - Hugging Face Environment & Prerequisites
# Issue #51: E3A-US5 - Install Training Dependencies
#
# This Dockerfile creates a containerized environment for QLoRA adapter training
# with all required dependencies pre-installed.
#
# Build:
#   docker build -t kwanzaa-training:latest -f backend/training/Dockerfile .
#
# Run (GPU):
#   docker run --gpus all -v $(pwd):/workspace kwanzaa-training:latest
#
# Run (CPU):
#   docker run -v $(pwd):/workspace kwanzaa-training:latest

# Base image with CUDA support
# Use CUDA 11.8 for compatibility with PyTorch 2.1.2
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Metadata
LABEL maintainer="Kwanzaa Team"
LABEL description="Training environment for Kwanzaa adapter training with QLoRA"
LABEL version="1.0"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Python and build tools
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3.10-venv \
    # Build essentials
    build-essential \
    cmake \
    git \
    wget \
    curl \
    # For flash-attention compilation (optional)
    ninja-build \
    # System utilities
    htop \
    tmux \
    vim \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA 11.8 support
RUN pip install --no-cache-dir \
    torch==2.1.2 \
    torchvision==0.16.2 \
    torchaudio==2.1.2 \
    --index-url https://download.pytorch.org/whl/cu118

# Copy requirements file
COPY backend/training/requirements.txt /tmp/requirements.txt

# Install training dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install optional packages (may fail, continue anyway)
RUN pip install --no-cache-dir flash-attn==2.5.0 --no-build-isolation || \
    echo "Flash Attention installation failed (optional, continuing...)"

# Set environment variables for Hugging Face
ENV HF_HOME=/workspace/.cache/huggingface
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface/transformers
ENV HF_DATASETS_CACHE=/workspace/.cache/huggingface/datasets

# Set PyTorch environment variables
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ENV CUDA_VISIBLE_DEVICES=0

# Create cache directories
RUN mkdir -p /workspace/.cache/huggingface/transformers && \
    mkdir -p /workspace/.cache/huggingface/datasets && \
    mkdir -p /workspace/.cache/huggingface/hub

# Copy verification script
COPY backend/training/verify_environment.py /workspace/verify_environment.py

# Set up entrypoint script
RUN echo '#!/bin/bash\n\
echo "================================================================="\n\
echo "  Kwanzaa Training Environment"\n\
echo "================================================================="\n\
echo ""\n\
echo "Python version: $(python --version)"\n\
echo "PyTorch version: $(python -c \"import torch; print(torch.__version__)\" 2>/dev/null || echo \"Not installed\")"\n\
echo "CUDA available: $(python -c \"import torch; print(torch.cuda.is_available())\" 2>/dev/null || echo \"N/A\")"\n\
echo "GPU count: $(python -c \"import torch; print(torch.cuda.device_count())\" 2>/dev/null || echo \"0\")"\n\
echo ""\n\
echo "Running environment verification..."\n\
python /workspace/verify_environment.py\n\
echo ""\n\
echo "Ready for training!"\n\
echo ""\n\
exec "$@"\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; assert torch.cuda.is_available()" || exit 1

# Expose ports for TensorBoard and Jupyter (optional)
EXPOSE 6006 8888
