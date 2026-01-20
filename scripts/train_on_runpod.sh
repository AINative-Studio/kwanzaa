#!/usr/bin/env bash
#
# Automated RunPod Training Script for Kwanzaa Adapter
# =====================================================
# This script automates the entire workflow:
# 1. Creates RunPod GPU instance
# 2. Uploads code and data
# 3. Installs dependencies
# 4. Runs training
# 5. Downloads trained adapter
# 6. Terminates pod
#
# Requirements:
# - runpodctl CLI installed: curl -s https://raw.githubusercontent.com/runpod/runpodctl/master/install.sh | bash
# - RUNPOD_API_KEY environment variable set
#
# Usage:
#   ./scripts/train_on_runpod.sh [OPTIONS]
#
# Options:
#   --gpu GPU_TYPE          GPU type (default: RTX4090)
#   --epochs NUM            Number of epochs (default: 4)
#   --output NAME           Output adapter name (default: kwanzaa-adapter-v0)
#   --dry-run               Test mode - don't actually train
#   --keep-pod              Don't terminate pod after completion
#   --help                  Show this help message
#
# Examples:
#   ./scripts/train_on_runpod.sh
#   ./scripts/train_on_runpod.sh --gpu A100 --epochs 6
#   ./scripts/train_on_runpod.sh --dry-run --keep-pod
#

set -euo pipefail

# ==================== Configuration ====================

# Default values
GPU_TYPE="RTX4090"
NUM_EPOCHS=4
OUTPUT_NAME="kwanzaa-adapter-v0"
DRY_RUN=false
KEEP_POD=false
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== Helper Functions ====================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    sed -n '/^#/,/^$/p' "$0" | sed 's/^# \?//' | tail -n +2 | head -n -1
    exit 0
}

check_requirements() {
    log_info "Checking requirements..."

    # Check runpodctl
    if ! command -v runpodctl &> /dev/null; then
        log_error "runpodctl not found. Install with:"
        echo "  curl -s https://raw.githubusercontent.com/runpod/runpodctl/master/install.sh | bash"
        exit 1
    fi

    # Check API key
    if [ -z "${RUNPOD_API_KEY:-}" ]; then
        log_error "RUNPOD_API_KEY environment variable not set"
        log_info "Get your API key from: https://www.runpod.io/console/user/settings"
        exit 1
    fi

    # Check project files
    if [ ! -f "$PROJECT_ROOT/backend/training/train_adapter.py" ]; then
        log_error "Training script not found at: $PROJECT_ROOT/backend/training/train_adapter.py"
        exit 1
    fi

    if [ ! -f "$PROJECT_ROOT/data/training/kwanzaa_train.jsonl" ]; then
        log_error "Training data not found at: $PROJECT_ROOT/data/training/kwanzaa_train.jsonl"
        exit 1
    fi

    log_success "All requirements met"
}

estimate_cost() {
    local gpu_cost_per_hour
    case "$GPU_TYPE" in
        RTX3090)
            gpu_cost_per_hour=0.49
            ;;
        RTX4090)
            gpu_cost_per_hour=0.89
            ;;
        A5000)
            gpu_cost_per_hour=0.79
            ;;
        A100)
            gpu_cost_per_hour=1.89
            ;;
        *)
            gpu_cost_per_hour=1.00
            ;;
    esac

    # Estimate 15-20 minutes for training
    local estimated_hours=0.33
    local estimated_cost=$(echo "$gpu_cost_per_hour * $estimated_hours" | bc -l)

    log_info "Cost estimate for $GPU_TYPE:"
    echo "  - Hourly rate: \$$gpu_cost_per_hour/hour"
    echo "  - Estimated time: 15-20 minutes"
    echo "  - Estimated cost: \$$estimated_cost"
}

create_pod() {
    log_info "Creating RunPod instance..."
    log_info "GPU: $GPU_TYPE"
    log_info "Template: runpod/pytorch:2.1.0-py3.11-cuda12.1.0-devel-ubuntu22.04"

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN: Would create pod here"
        return 0
    fi

    # Create pod and capture pod ID
    # Note: Adjust template and GPU type as needed
    POD_ID=$(runpodctl create pod \
        --name "kwanzaa-training-$(date +%s)" \
        --gpuType "$GPU_TYPE" \
        --imageName "runpod/pytorch:2.1.0-py3.11-cuda12.1.0-devel-ubuntu22.04" \
        --containerDiskSize 20 \
        --volumeSize 20 \
        --ports "8888/http" \
        --env "HF_TOKEN=${HF_TOKEN:-}" \
        --json | jq -r '.id')

    if [ -z "$POD_ID" ]; then
        log_error "Failed to create pod"
        exit 1
    fi

    log_success "Pod created: $POD_ID"

    # Wait for pod to be ready
    log_info "Waiting for pod to be ready..."
    sleep 30

    runpodctl list pods
}

upload_files() {
    log_info "Uploading code and data to pod..."

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN: Would upload files here"
        return 0
    fi

    # Create tar archive of necessary files
    log_info "Creating archive..."
    tar -czf /tmp/kwanzaa-training.tar.gz \
        -C "$PROJECT_ROOT" \
        backend/training \
        data/training \
        backend/config

    # Upload to pod
    runpodctl send "$POD_ID" /tmp/kwanzaa-training.tar.gz /workspace/

    # Extract on pod
    runpodctl exec "$POD_ID" "cd /workspace && tar -xzf kwanzaa-training.tar.gz"

    log_success "Files uploaded"
}

install_dependencies() {
    log_info "Installing dependencies on pod..."

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN: Would install dependencies here"
        return 0
    fi

    runpodctl exec "$POD_ID" "cd /workspace && pip install -r backend/training/requirements.txt"

    log_success "Dependencies installed"
}

run_training() {
    log_info "Starting training..."
    log_info "Configuration: backend/training/config/training.yaml"
    log_info "Epochs: $NUM_EPOCHS"
    log_info "Output: $OUTPUT_NAME"

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN: Would start training here"
        return 0
    fi

    # Run training script
    runpodctl exec "$POD_ID" "cd /workspace && python backend/training/train_adapter.py \
        --config backend/training/config/training.yaml \
        --num_epochs $NUM_EPOCHS \
        --output_dir outputs/$OUTPUT_NAME"

    log_success "Training completed"
}

download_adapter() {
    log_info "Downloading trained adapter..."

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN: Would download adapter here"
        return 0
    fi

    # Create local output directory
    mkdir -p "$PROJECT_ROOT/outputs/$OUTPUT_NAME"

    # Download adapter files
    runpodctl receive "$POD_ID" "/workspace/outputs/$OUTPUT_NAME" "$PROJECT_ROOT/outputs/"

    log_success "Adapter downloaded to: $PROJECT_ROOT/outputs/$OUTPUT_NAME"

    # List downloaded files
    ls -lh "$PROJECT_ROOT/outputs/$OUTPUT_NAME"
}

terminate_pod() {
    if [ "$KEEP_POD" = true ]; then
        log_warn "Keeping pod alive (--keep-pod specified)"
        log_info "Pod ID: $POD_ID"
        log_info "Terminate manually with: runpodctl stop pod $POD_ID"
        return 0
    fi

    log_info "Terminating pod..."

    if [ "$DRY_RUN" = true ]; then
        log_warn "DRY RUN: Would terminate pod here"
        return 0
    fi

    runpodctl stop pod "$POD_ID"

    log_success "Pod terminated"
}

# ==================== Parse Arguments ====================

while [[ $# -gt 0 ]]; do
    case $1 in
        --gpu)
            GPU_TYPE="$2"
            shift 2
            ;;
        --epochs)
            NUM_EPOCHS="$2"
            shift 2
            ;;
        --output)
            OUTPUT_NAME="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --keep-pod)
            KEEP_POD=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ==================== Main Workflow ====================

main() {
    log_info "Kwanzaa Adapter Training on RunPod"
    log_info "=================================="
    echo ""

    check_requirements
    estimate_cost

    echo ""
    if [ "$DRY_RUN" = false ]; then
        read -p "Continue with training? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cancelled"
            exit 0
        fi
    fi

    create_pod
    upload_files
    install_dependencies
    run_training
    download_adapter
    terminate_pod

    echo ""
    log_success "Training complete!"
    log_success "Adapter saved to: $PROJECT_ROOT/outputs/$OUTPUT_NAME"
    echo ""
    log_info "Next steps:"
    echo "  1. Verify adapter: ls -lh outputs/$OUTPUT_NAME"
    echo "  2. Test inference: python backend/training/test_adapter.py"
    echo "  3. Publish to HF: python backend/training/publish_adapter.py"
}

# Run main workflow
main
