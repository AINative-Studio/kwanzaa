#!/bin/bash
################################################################################
# RunPod Training Environment Setup Script
#
# Automates the setup of a RunPod GPU instance for Kwanzaa adapter training.
# This script installs all dependencies, configures the environment, and
# verifies everything is ready for training.
#
# Usage:
#   wget https://raw.githubusercontent.com/YOUR_ORG/kwanzaa/main/scripts/runpod_setup.sh
#   bash runpod_setup.sh
#
# Or on RunPod instance:
#   curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/kwanzaa/main/scripts/runpod_setup.sh | bash
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo "========================================================================"
    echo "$1"
    echo "========================================================================"
    echo ""
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_warn "Not running as root. Some commands may require sudo."
fi

log_section "Kwanzaa Training Environment Setup"

# Step 1: System Update
log_section "Step 1: Updating System Packages"
apt-get update -qq || log_warn "apt-get update failed, continuing anyway"
apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    vim \
    htop \
    tmux \
    screen \
    ca-certificates \
    || log_error "Failed to install system packages"

log_info "System packages installed"

# Step 2: Verify GPU
log_section "Step 2: Verifying GPU Availability"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
    GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader | head -n 1)
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -n 1)

    log_info "GPU detected: $GPU_NAME"
    log_info "GPU count: $GPU_COUNT"
    log_info "GPU memory: $GPU_MEMORY"
else
    log_error "nvidia-smi not found! GPU may not be available."
    exit 1
fi

# Step 3: Python Environment
log_section "Step 3: Verifying Python Environment"
PYTHON_VERSION=$(python --version 2>&1)
log_info "Python version: $PYTHON_VERSION"

if ! command -v pip &> /dev/null; then
    log_error "pip not found!"
    exit 1
fi

# Step 4: Install Training Dependencies
log_section "Step 4: Installing Training Dependencies"

log_info "Installing PyTorch..."
pip install --no-cache-dir -q torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

log_info "Installing Transformers ecosystem..."
pip install --no-cache-dir -q \
    transformers>=4.36.0 \
    peft>=0.7.0 \
    accelerate>=0.25.0 \
    datasets>=2.16.0 \
    trl>=0.7.0

log_info "Installing quantization and optimization..."
pip install --no-cache-dir -q \
    bitsandbytes>=0.41.0 \
    optimum>=1.16.0

log_info "Installing utilities..."
pip install --no-cache-dir -q \
    huggingface-hub>=0.20.0 \
    safetensors>=0.4.0 \
    sentencepiece>=0.1.99 \
    protobuf>=3.20.0 \
    pyyaml>=6.0 \
    tensorboard>=2.15.0 \
    wandb>=0.16.0

log_info "Core dependencies installed"

# Step 5: Optional Flash Attention
log_section "Step 5: Installing Flash Attention (Optional)"
log_info "Attempting to install flash-attn (may take 5-10 minutes)..."

# Check GPU compute capability
COMPUTE_CAP=$(python -c "import torch; print(f'{torch.cuda.get_device_capability()[0]}.{torch.cuda.get_device_capability()[1]}')" 2>/dev/null || echo "0.0")
log_info "GPU compute capability: $COMPUTE_CAP"

if python -c "import torch; exit(0 if torch.cuda.get_device_capability()[0] >= 8 else 1)" 2>/dev/null; then
    log_info "GPU supports flash attention, installing..."
    pip install flash-attn --no-build-isolation -q || log_warn "Flash attention installation failed, continuing without it"
else
    log_warn "GPU does not support flash attention (requires compute capability >= 8.0)"
fi

# Step 6: Verify Installation
log_section "Step 6: Verifying Installation"

log_info "Testing PyTorch..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}')" || log_error "PyTorch test failed"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" || log_error "CUDA test failed"
python -c "import torch; print(f'CUDA version: {torch.version.cuda}')" || log_error "CUDA version test failed"

log_info "Testing Transformers..."
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')" || log_error "Transformers test failed"

log_info "Testing PEFT..."
python -c "import peft; print(f'PEFT version: {peft.__version__}')" || log_error "PEFT test failed"

log_info "Testing BitsAndBytes..."
python -c "import bitsandbytes as bnb; print('BitsAndBytes: OK')" || log_error "BitsAndBytes test failed"

log_info "Testing Accelerate..."
python -c "import accelerate; print(f'Accelerate version: {accelerate.__version__}')" || log_error "Accelerate test failed"

# Step 7: Clone Repository (if not exists)
log_section "Step 7: Setting Up Repository"

WORKSPACE_DIR="/workspace"
REPO_DIR="$WORKSPACE_DIR/kwanzaa"

cd $WORKSPACE_DIR || exit 1

if [ -d "$REPO_DIR" ]; then
    log_info "Repository already exists at $REPO_DIR"
    cd $REPO_DIR
    log_info "Pulling latest changes..."
    git pull || log_warn "Git pull failed, using existing code"
else
    log_warn "Repository not found. Please clone manually:"
    log_warn "  cd /workspace"
    log_warn "  git clone https://github.com/YOUR_ORG/kwanzaa.git"
    log_warn "  cd kwanzaa"
    log_warn ""
    log_warn "Or if you have SSH access:"
    log_warn "  git clone git@github.com:YOUR_ORG/kwanzaa.git"
fi

# Step 8: Create Directory Structure
log_section "Step 8: Creating Directory Structure"

mkdir -p $WORKSPACE_DIR/kwanzaa/data/training
mkdir -p $WORKSPACE_DIR/kwanzaa/outputs
mkdir -p $WORKSPACE_DIR/kwanzaa/backend/training/config
mkdir -p $WORKSPACE_DIR/.cache/huggingface

log_info "Directory structure created"

# Step 9: Set Environment Variables
log_section "Step 9: Configuring Environment"

# Create .env file template if it doesn't exist
if [ ! -f "$REPO_DIR/backend/.env" ] && [ -d "$REPO_DIR/backend" ]; then
    log_info "Creating .env template..."
    cat > $REPO_DIR/backend/.env << 'EOF'
# HuggingFace Token (required for downloading models and publishing adapters)
# Get from: https://huggingface.co/settings/tokens
HF_TOKEN=your-token-here

# RunPod API Key (for provisioning)
RUNPOD_API_KEY=your-api-key-here

# Model Configuration
BASE_MODEL=ai2
ADAPTER_TYPE=qlora
MODEL_CACHE_DIR=.cache/models
EOF
    log_warn "Please edit backend/.env and add your tokens"
fi

# Set cache directory
export HF_HOME="$WORKSPACE_DIR/.cache/huggingface"
export TRANSFORMERS_CACHE="$WORKSPACE_DIR/.cache/huggingface"

log_info "Environment configured"

# Step 10: Quick GPU Test
log_section "Step 10: Running GPU Test"

log_info "Testing GPU with PyTorch..."
python << 'EOPYTHON'
import torch

print("=" * 70)
print("GPU Test Results")
print("=" * 70)

# Basic CUDA info
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"PyTorch version: {torch.__version__}")

if torch.cuda.is_available():
    print(f"\nGPU count: {torch.cuda.device_count()}")
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")

    props = torch.cuda.get_device_properties(0)
    print(f"\nGPU Properties:")
    print(f"  Total memory: {props.total_memory / 1e9:.2f} GB")
    print(f"  Compute capability: {props.major}.{props.minor}")

    # Test BF16 support
    bf16_supported = torch.cuda.get_device_capability()[0] >= 8
    print(f"  BF16 supported: {bf16_supported}")

    # Simple tensor operation
    print("\nRunning simple GPU test...")
    x = torch.randn(1000, 1000).cuda()
    y = torch.randn(1000, 1000).cuda()
    z = torch.matmul(x, y)
    print(f"  Matrix multiplication successful: {z.shape}")

    print("\nGPU is ready for training!")
else:
    print("\nWARNING: CUDA not available!")

print("=" * 70)
EOPYTHON

# Final Summary
log_section "Setup Complete!"

echo ""
echo "Environment Setup Summary:"
echo "  - System packages: Installed"
echo "  - GPU: $GPU_NAME ($GPU_MEMORY)"
echo "  - Python: $PYTHON_VERSION"
echo "  - PyTorch: Installed with CUDA support"
echo "  - Training dependencies: Installed"
echo "  - Flash Attention: $(pip list | grep flash-attn > /dev/null && echo 'Installed' || echo 'Not installed')"
echo "  - Repository: $REPO_DIR"
echo ""
echo "Next Steps:"
echo ""
echo "1. Upload training data:"
echo "   scp -P PORT data/training/*.jsonl root@HOST:/workspace/kwanzaa/data/training/"
echo ""
echo "2. Configure environment (if needed):"
echo "   vim $REPO_DIR/backend/.env"
echo ""
echo "3. Start training:"
echo "   cd /workspace/kwanzaa"
echo "   python backend/training/train_adapter.py \\"
echo "       --config backend/training/config/training.yaml \\"
echo "       --output-dir outputs/kwanzaa-adapter-v1"
echo ""
echo "4. Monitor training:"
echo "   tail -f outputs/kwanzaa-adapter-v1/training.log"
echo ""
echo "5. Use screen/tmux for persistent sessions:"
echo "   screen -S training"
echo "   # Run training"
echo "   # Detach: Ctrl+A, D"
echo "   # Reattach: screen -r training"
echo ""

log_section "Ready for Training!"

# Save setup info
SETUP_INFO="$WORKSPACE_DIR/setup_info.txt"
cat > $SETUP_INFO << EOF
Setup completed: $(date)
GPU: $GPU_NAME
Memory: $GPU_MEMORY
Python: $PYTHON_VERSION
Compute Capability: $COMPUTE_CAP
EOF

log_info "Setup information saved to: $SETUP_INFO"

exit 0
