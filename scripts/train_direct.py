#!/usr/bin/env python3
"""
Direct RunPod Training Script
Uses RunPod Python SDK to train Kwanzaa adapter
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def log_info(msg):
    print(f"\033[34m[INFO]\033[0m {msg}")

def log_success(msg):
    print(f"\033[32m[SUCCESS]\033[0m {msg}")

def log_error(msg):
    print(f"\033[31m[ERROR]\033[0m {msg}")

def check_runpodctl():
    """Check if runpodctl is available"""
    runpodctl_path = Path.home() / ".local" / "bin" / "runpodctl"
    if not runpodctl_path.exists():
        log_error("runpodctl not found")
        return None
    return str(runpodctl_path)

def run_command(cmd, env=None):
    """Run a command and return output"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        env=env or os.environ.copy()
    )
    return result

def main():
    log_info("Kwanzaa Adapter Direct Training")
    log_info("=" * 50)

    # Check runpodctl
    runpodctl = check_runpodctl()
    if not runpodctl:
        log_error("Please install runpodctl first")
        return 1

    log_success(f"Found runpodctl at: {runpodctl}")

    # Set up environment
    env = os.environ.copy()
    env["PATH"] = f"{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    env["RUNPOD_API_KEY"] = "your-runpod-api-key-here"

    # Check current pods
    log_info("Checking current pods...")
    result = run_command(f"{runpodctl} get pod", env=env)
    print(result.stdout)

    log_info("\nReady to create training pod")
    log_info("GPU: RTX4090")
    log_info("Estimated cost: ~$0.29")
    log_info("Estimated time: ~20 minutes")

    response = input("\nContinue? (y/N): ")
    if response.lower() != 'y':
        log_info("Cancelled")
        return 0

    # Create pod
    log_info("Creating pod...")
    create_cmd = f"""{runpodctl} create pod \\
        --name kwanzaa-training-{int(time.time())} \\
        --gpuType RTX4090 \\
        --imageName runpod/pytorch:2.1.0-py3.11-cuda12.1.0-devel-ubuntu22.04 \\
        --containerDiskSize 20 \\
        --volumeSize 20 \\
        --ports 8888/http"""

    log_info(f"Running: {create_cmd}")
    result = run_command(create_cmd, env=env)

    if result.returncode != 0:
        log_error(f"Failed to create pod: {result.stderr}")
        return 1

    print(result.stdout)
    log_success("Pod creation initiated")
    log_info("Check pod status with: runpodctl get pod")

    return 0

if __name__ == "__main__":
    sys.exit(main())
