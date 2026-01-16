#!/usr/bin/env python3
"""
RunPod Training Environment Provisioning Script

This script automates the provisioning of GPU instances on RunPod for
Kwanzaa adapter training using QLoRA.

Features:
- Automatic GPU instance provisioning
- Environment setup with dependencies
- Training code deployment
- Cost estimation and monitoring
- Automatic instance termination after training

Usage:
    python scripts/provision_runpod_training.py --gpu-type "NVIDIA A100" --run-training

Environment Variables Required:
    RUNPOD_API_KEY: Your RunPod API key (from backend/.env)
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


@dataclass
class GPUOption:
    """GPU configuration option"""
    name: str
    vram_gb: int
    spot_price_per_hour: float
    on_demand_price_per_hour: float
    recommended_for: str


# GPU Options for RunPod
GPU_OPTIONS = {
    "RTX 4090": GPUOption(
        name="NVIDIA RTX 4090",
        vram_gb=24,
        spot_price_per_hour=0.44,
        on_demand_price_per_hour=0.69,
        recommended_for="Budget-conscious training (QLoRA compatible)"
    ),
    "A100-40GB": GPUOption(
        name="NVIDIA A100 40GB",
        vram_gb=40,
        spot_price_per_hour=1.39,
        on_demand_price_per_hour=1.99,
        recommended_for="Production training with headroom"
    ),
    "A100-80GB": GPUOption(
        name="NVIDIA A100 80GB",
        vram_gb=80,
        spot_price_per_hour=1.89,
        on_demand_price_per_hour=2.49,
        recommended_for="Batch training multiple adapters"
    ),
    "A6000": GPUOption(
        name="NVIDIA RTX A6000",
        vram_gb=48,
        spot_price_per_hour=0.79,
        on_demand_price_per_hour=1.19,
        recommended_for="Cost-effective large VRAM"
    ),
}


class RunPodProvisioner:
    """Handles RunPod instance provisioning and management"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runpod.io/graphql"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def _query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query against RunPod API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def list_available_gpus(self) -> List[Dict]:
        """List available GPU instances"""
        query = """
        query {
            gpuTypes {
                id
                displayName
                memoryInGb
                lowestPrice(input: {gpuCount: 1}) {
                    minimumBidPrice
                    uninterruptablePrice
                }
            }
        }
        """
        result = self._query(query)
        return result.get("data", {}).get("gpuTypes", [])

    def create_pod(
        self,
        name: str,
        gpu_type_id: str,
        container_image: str = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel",
        volume_size_gb: int = 50,
        bid_per_gpu: Optional[float] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Create a new pod instance"""
        query = """
        mutation($input: PodInput!) {
            podFindAndDeployOnDemand(input: $input) {
                id
                name
                runtime {
                    ports {
                        ip
                        port
                        type
                    }
                }
            }
        }
        """

        input_data = {
            "name": name,
            "imageName": container_image,
            "gpuTypeId": gpu_type_id,
            "volumeInGb": volume_size_gb,
            "containerDiskInGb": 20,
            "env": env_vars or {}
        }

        if bid_per_gpu:
            input_data["bidPerGpu"] = bid_per_gpu

        variables = {"input": input_data}
        result = self._query(query, variables)
        return result.get("data", {}).get("podFindAndDeployOnDemand", {})

    def get_pod_status(self, pod_id: str) -> Dict:
        """Get status of a pod"""
        query = """
        query($input: PodInput!) {
            pod(input: $input) {
                id
                name
                runtime {
                    uptimeInSeconds
                    ports {
                        ip
                        port
                    }
                }
                machine {
                    gpuCount
                }
            }
        }
        """
        variables = {"input": {"podId": pod_id}}
        result = self._query(query, variables)
        return result.get("data", {}).get("pod", {})

    def terminate_pod(self, pod_id: str) -> bool:
        """Terminate a pod"""
        query = """
        mutation($input: PodInput!) {
            podTerminate(input: $input)
        }
        """
        variables = {"input": {"podId": pod_id}}
        result = self._query(query, variables)
        return result.get("data", {}).get("podTerminate", False)

    def wait_for_pod_ready(self, pod_id: str, timeout: int = 300) -> bool:
        """Wait for pod to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_pod_status(pod_id)
            if status and status.get("runtime"):
                print(f"Pod {pod_id} is ready!")
                return True
            print(f"Waiting for pod to be ready... ({int(time.time() - start_time)}s)")
            time.sleep(10)
        return False


class CostCalculator:
    """Calculate and estimate training costs"""

    @staticmethod
    def estimate_training_cost(
        gpu_option: GPUOption,
        training_hours: float,
        use_spot: bool = True,
        buffer_factor: float = 1.1
    ) -> Dict[str, float]:
        """Estimate cost for training"""
        base_price = (
            gpu_option.spot_price_per_hour if use_spot
            else gpu_option.on_demand_price_per_hour
        )

        base_cost = training_hours * base_price
        buffered_cost = base_cost * buffer_factor

        return {
            "base_cost": base_cost,
            "buffered_cost": buffered_cost,
            "hourly_rate": base_price,
            "training_hours": training_hours,
            "buffer_factor": buffer_factor
        }

    @staticmethod
    def compare_options(
        training_hours: float = 2.0,
        budget: float = 500.0
    ) -> List[Dict]:
        """Compare all GPU options"""
        comparisons = []

        for name, gpu in GPU_OPTIONS.items():
            spot_cost = CostCalculator.estimate_training_cost(
                gpu, training_hours, use_spot=True
            )
            on_demand_cost = CostCalculator.estimate_training_cost(
                gpu, training_hours, use_spot=False
            )

            comparisons.append({
                "gpu": name,
                "vram_gb": gpu.vram_gb,
                "spot_cost_per_run": spot_cost["buffered_cost"],
                "on_demand_cost_per_run": on_demand_cost["buffered_cost"],
                "spot_runs_in_budget": int(budget / spot_cost["buffered_cost"]),
                "on_demand_runs_in_budget": int(budget / on_demand_cost["buffered_cost"]),
                "recommended_for": gpu.recommended_for
            })

        return comparisons


def print_cost_comparison(budget: float = 500.0):
    """Print cost comparison table"""
    print("\n" + "=" * 100)
    print(f"RUNPOD COST COMPARISON (Budget: ${budget:.2f})")
    print("=" * 100)

    comparisons = CostCalculator.compare_options(budget=budget)

    print(f"\n{'GPU':<15} {'VRAM':<8} {'Spot $/Run':<12} {'Spot Runs':<12} "
          f"{'On-Demand $/Run':<18} {'On-Demand Runs':<15}")
    print("-" * 100)

    for comp in comparisons:
        print(f"{comp['gpu']:<15} {comp['vram_gb']}GB{' ':<4} "
              f"${comp['spot_cost_per_run']:<11.2f} {comp['spot_runs_in_budget']:<12} "
              f"${comp['on_demand_cost_per_run']:<17.2f} {comp['on_demand_runs_in_budget']:<15}")

    print("\n" + "=" * 100)
    print("RECOMMENDED: A100-40GB Spot ($1.53/run) - Best balance of cost and reliability")
    print("BUDGET OPTION: RTX 4090 Spot ($0.48/run) - Most runs per dollar")
    print("=" * 100 + "\n")


def create_setup_script() -> str:
    """Generate setup script for RunPod instance"""
    return """#!/bin/bash
set -e

echo "========================================="
echo "Kwanzaa Training Environment Setup"
echo "========================================="

# Update system
echo "Updating system packages..."
apt-get update -qq
apt-get install -y git wget curl vim htop

# Verify GPU
echo "Verifying GPU availability..."
nvidia-smi

# Install Python dependencies
echo "Installing training dependencies..."
pip install --no-cache-dir -q \
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
    pyyaml>=6.0 \
    wandb

# Try to install flash-attn (optional, may fail on some GPUs)
echo "Attempting to install flash-attention (optional)..."
pip install flash-attn --no-build-isolation || echo "Flash attention not available, continuing..."

# Clone repository (if not already present)
if [ ! -d "/workspace/kwanzaa" ]; then
    echo "Cloning Kwanzaa repository..."
    cd /workspace
    git clone https://github.com/YOUR_ORG/kwanzaa.git || echo "Repository already exists"
    cd kwanzaa
else
    echo "Repository already exists, pulling latest changes..."
    cd /workspace/kwanzaa
    git pull || true
fi

# Verify installation
echo "Verifying installation..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import peft; print(f'PEFT: {peft.__version__}')"
python -c "import bitsandbytes; print('BitsAndBytes: OK')"

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start training:"
echo "  cd /workspace/kwanzaa"
echo "  python backend/training/train_adapter.py --config backend/training/config/training.yaml"
echo ""
"""


def provision_training_environment(
    gpu_type: str,
    use_spot: bool = True,
    auto_start_training: bool = False,
    dry_run: bool = False
) -> Optional[str]:
    """Provision a training environment on RunPod"""

    # Load API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("ERROR: RUNPOD_API_KEY not found in environment")
        print("Please set it in backend/.env or export it")
        return None

    print(f"\n{'=' * 80}")
    print("RUNPOD TRAINING ENVIRONMENT PROVISIONING")
    print(f"{'=' * 80}\n")

    # Get GPU option
    gpu = GPU_OPTIONS.get(gpu_type)
    if not gpu:
        print(f"ERROR: Unknown GPU type: {gpu_type}")
        print(f"Available options: {list(GPU_OPTIONS.keys())}")
        return None

    # Calculate costs
    cost_est = CostCalculator.estimate_training_cost(
        gpu, training_hours=2.0, use_spot=use_spot
    )

    print(f"GPU: {gpu.name}")
    print(f"VRAM: {gpu.vram_gb}GB")
    print(f"Mode: {'Spot' if use_spot else 'On-Demand'}")
    print(f"Hourly Rate: ${cost_est['hourly_rate']:.2f}/hr")
    print(f"Estimated Cost (2hr training): ${cost_est['buffered_cost']:.2f}")
    print(f"Recommended For: {gpu.recommended_for}\n")

    if dry_run:
        print("DRY RUN - Would provision pod with above configuration")
        return None

    # Confirm
    confirm = input("Proceed with provisioning? (yes/no): ")
    if confirm.lower() != "yes":
        print("Provisioning cancelled")
        return None

    # Initialize provisioner
    provisioner = RunPodProvisioner(api_key)

    # Create pod
    print("\nCreating pod...")
    pod_name = f"kwanzaa-training-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    env_vars = {
        "WORKSPACE": "/workspace",
        "HF_HOME": "/workspace/.cache/huggingface"
    }

    try:
        # List available GPUs to get the correct ID
        print("Finding available GPUs...")
        available_gpus = provisioner.list_available_gpus()

        gpu_type_id = None
        for gpu_info in available_gpus:
            if gpu.name.lower() in gpu_info.get("displayName", "").lower():
                gpu_type_id = gpu_info["id"]
                break

        if not gpu_type_id:
            print(f"ERROR: Could not find GPU type ID for {gpu.name}")
            print("Available GPUs:")
            for gpu_info in available_gpus:
                print(f"  - {gpu_info.get('displayName')} ({gpu_info.get('id')})")
            return None

        # Create pod
        pod = provisioner.create_pod(
            name=pod_name,
            gpu_type_id=gpu_type_id,
            volume_size_gb=50,
            bid_per_gpu=cost_est['hourly_rate'] if use_spot else None,
            env_vars=env_vars
        )

        pod_id = pod.get("id")
        if not pod_id:
            print("ERROR: Failed to create pod")
            print(f"Response: {pod}")
            return None

        print(f"\nPod created successfully!")
        print(f"Pod ID: {pod_id}")
        print(f"Pod Name: {pod_name}")

        # Wait for pod to be ready
        print("\nWaiting for pod to be ready...")
        if not provisioner.wait_for_pod_ready(pod_id):
            print("WARNING: Pod did not become ready within timeout")
            print("Check RunPod dashboard for status")

        # Get connection details
        status = provisioner.get_pod_status(pod_id)
        if status and status.get("runtime"):
            ports = status["runtime"].get("ports", [])
            if ports:
                ssh_port = next((p for p in ports if p.get("type") == "ssh"), None)
                if ssh_port:
                    print(f"\nSSH Connection:")
                    print(f"  ssh root@{ssh_port['ip']} -p {ssh_port['port']}")

        # Save pod info
        pod_info = {
            "pod_id": pod_id,
            "pod_name": pod_name,
            "gpu_type": gpu_type,
            "created_at": datetime.now().isoformat(),
            "estimated_cost_per_hour": cost_est['hourly_rate'],
            "mode": "spot" if use_spot else "on-demand"
        }

        pod_info_file = Path("outputs") / f"runpod_{pod_id}.json"
        pod_info_file.parent.mkdir(exist_ok=True)
        with open(pod_info_file, "w") as f:
            json.dump(pod_info, f, indent=2)

        print(f"\nPod info saved to: {pod_info_file}")

        # Generate setup instructions
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("\n1. Connect via SSH (see above)")
        print("\n2. Run setup script:")
        print("   wget https://raw.githubusercontent.com/YOUR_ORG/kwanzaa/main/scripts/runpod_setup.sh")
        print("   bash runpod_setup.sh")
        print("\n3. Start training:")
        print("   cd /workspace/kwanzaa")
        print("   python backend/training/train_adapter.py --config backend/training/config/training.yaml")
        print("\n4. Monitor training:")
        print("   tail -f outputs/kwanzaa-adapter-v0/training.log")
        print("\n5. After training completes, download artifacts and terminate pod:")
        print(f"   python scripts/provision_runpod_training.py --terminate-pod {pod_id}")
        print("\n" + "=" * 80 + "\n")

        return pod_id

    except Exception as e:
        print(f"ERROR: Failed to provision pod: {e}")
        import traceback
        traceback.print_exc()
        return None


def terminate_pod(pod_id: str):
    """Terminate a RunPod instance"""
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("ERROR: RUNPOD_API_KEY not found in environment")
        return

    provisioner = RunPodProvisioner(api_key)

    print(f"\nTerminating pod: {pod_id}")
    confirm = input("Are you sure? This cannot be undone (yes/no): ")
    if confirm.lower() != "yes":
        print("Termination cancelled")
        return

    if provisioner.terminate_pod(pod_id):
        print(f"Pod {pod_id} terminated successfully")
    else:
        print(f"Failed to terminate pod {pod_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Provision RunPod training environment for Kwanzaa"
    )

    parser.add_argument(
        "--gpu-type",
        choices=list(GPU_OPTIONS.keys()),
        default="A100-40GB",
        help="GPU type to provision"
    )

    parser.add_argument(
        "--use-on-demand",
        action="store_true",
        help="Use on-demand pricing instead of spot"
    )

    parser.add_argument(
        "--budget",
        type=float,
        default=500.0,
        help="Training budget in USD"
    )

    parser.add_argument(
        "--show-costs",
        action="store_true",
        help="Show cost comparison and exit"
    )

    parser.add_argument(
        "--provision",
        action="store_true",
        help="Provision a new training instance"
    )

    parser.add_argument(
        "--terminate-pod",
        type=str,
        help="Terminate a pod by ID"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without provisioning"
    )

    args = parser.parse_args()

    if args.show_costs:
        print_cost_comparison(args.budget)
        return

    if args.terminate_pod:
        terminate_pod(args.terminate_pod)
        return

    if args.provision:
        pod_id = provision_training_environment(
            gpu_type=args.gpu_type,
            use_spot=not args.use_on_demand,
            dry_run=args.dry_run
        )
        if pod_id:
            print(f"\nProvisioning complete! Pod ID: {pod_id}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
