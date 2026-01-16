#!/usr/bin/env python3
"""
Environment Verification Script for Kwanzaa Training Dependencies

EPIC 3A - Hugging Face Environment & Prerequisites
Issue #51: E3A-US5 - Install Training Dependencies

This script verifies that all required dependencies are installed correctly
and that the system is ready for adapter training.

Usage:
    python backend/training/verify_environment.py
    python backend/training/verify_environment.py --verbose
"""

import sys
import os
import subprocess
from typing import Dict, List, Tuple
import importlib.metadata


# Required packages with minimum versions
REQUIRED_PACKAGES = {
    "torch": "2.1.0",
    "transformers": "4.37.0",
    "datasets": "2.16.0",
    "accelerate": "0.26.0",
    "peft": "0.8.0",
    "trl": "0.7.0",
    "optimum": "1.16.0",
    "sentencepiece": "0.1.99",
    "safetensors": "0.4.0",
    "wandb": "0.16.0",
    "tensorboard": "2.15.0",
    "numpy": "1.26.0",
    "pandas": "2.1.0",
    "scikit-learn": "1.4.0",
    "pyyaml": "6.0.0",
    "tqdm": "4.66.0",
    "evaluate": "0.4.0",
    "huggingface-hub": "0.20.0",
    "tokenizers": "0.15.0",
}

# Optional packages (may fail on some platforms)
OPTIONAL_PACKAGES = {
    "bitsandbytes": "0.42.0",  # GPU-only
    "mlflow": "2.10.0",
}


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}\n")


def print_section(text: str) -> None:
    """Print a formatted section."""
    print(f"\n{'-' * 80}")
    print(f"  {text}")
    print(f"{'-' * 80}\n")


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major == 3 and version.minor >= 9:
        return True, f"Python {version_str} (OK)"
    else:
        return False, f"Python {version_str} (FAILED: Requires Python 3.9+)"


def check_package_version(package_name: str, min_version: str) -> Tuple[bool, str]:
    """Check if a package is installed with the correct version."""
    try:
        installed_version = importlib.metadata.version(package_name)

        # Simple version comparison (works for most cases)
        installed_parts = [int(x) for x in installed_version.split('.')[:3]]
        min_parts = [int(x) for x in min_version.split('.')[:3]]

        # Pad with zeros if needed
        while len(installed_parts) < 3:
            installed_parts.append(0)
        while len(min_parts) < 3:
            min_parts.append(0)

        is_ok = installed_parts >= min_parts
        status = "OK" if is_ok else f"FAILED: Version {installed_version} < {min_version}"

        return is_ok, f"{package_name}=={installed_version} ({status})"
    except importlib.metadata.PackageNotFoundError:
        return False, f"{package_name} (FAILED: Not installed)"
    except Exception as e:
        return False, f"{package_name} (FAILED: {str(e)})"


def check_torch_cuda() -> Tuple[bool, str, Dict]:
    """Check PyTorch and CUDA availability."""
    try:
        import torch

        info = {
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "cudnn_version": torch.backends.cudnn.version() if torch.cuda.is_available() else None,
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "devices": [],
        }

        if info["cuda_available"]:
            for i in range(info["device_count"]):
                device_info = {
                    "id": i,
                    "name": torch.cuda.get_device_name(i),
                    "capability": torch.cuda.get_device_capability(i),
                    "total_memory": torch.cuda.get_device_properties(i).total_memory / 1e9,  # GB
                }
                info["devices"].append(device_info)

        # Check for Apple Silicon MPS
        info["mps_available"] = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()

        return True, "PyTorch imported successfully", info
    except Exception as e:
        return False, f"Failed to import PyTorch: {str(e)}", {}


def check_transformers() -> Tuple[bool, str]:
    """Check if transformers can be imported."""
    try:
        import transformers
        from transformers import AutoTokenizer, AutoModel
        return True, f"Transformers {transformers.__version__} (OK)"
    except Exception as e:
        return False, f"Transformers import failed: {str(e)}"


def check_peft() -> Tuple[bool, str]:
    """Check if PEFT can be imported."""
    try:
        import peft
        from peft import LoraConfig, get_peft_model
        return True, f"PEFT {peft.__version__} (OK)"
    except Exception as e:
        return False, f"PEFT import failed: {str(e)}"


def check_disk_space() -> Tuple[bool, str]:
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024 ** 3)

        min_required_gb = 10
        is_ok = free_gb >= min_required_gb
        status = "OK" if is_ok else f"WARNING: Less than {min_required_gb}GB free"

        return is_ok, f"{free_gb:.1f} GB free ({status})"
    except Exception as e:
        return False, f"Failed to check disk space: {str(e)}"


def check_memory() -> Tuple[bool, str]:
    """Check available system memory."""
    try:
        # Try to get memory info (platform-specific)
        if sys.platform == "linux":
            with open("/proc/meminfo") as f:
                meminfo = dict(line.split()[:2] for line in f if ":" in line)
                total_kb = int(meminfo.get("MemTotal:", "0"))
                available_kb = int(meminfo.get("MemAvailable:", "0"))
                total_gb = total_kb / (1024 ** 2)
                available_gb = available_kb / (1024 ** 2)
        else:
            # For macOS/Windows, just check using Python
            import psutil
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)

        min_required_gb = 16
        is_ok = total_gb >= min_required_gb
        status = "OK" if is_ok else f"WARNING: Less than {min_required_gb}GB RAM"

        return is_ok, f"{total_gb:.1f} GB total, {available_gb:.1f} GB available ({status})"
    except Exception as e:
        # psutil might not be installed, that's okay
        return True, "Could not check memory (non-critical)"


def run_verification(verbose: bool = False) -> bool:
    """Run all verification checks."""
    all_checks_passed = True

    print_header("Kwanzaa Training Environment Verification")
    print("This script verifies that all required dependencies are installed")
    print("and that your system is ready for adapter training.\n")

    # Check Python version
    print_section("Python Version")
    success, message = check_python_version()
    print(f"{'✓' if success else '✗'} {message}")
    if not success:
        all_checks_passed = False

    # Check system resources
    print_section("System Resources")

    # Disk space
    success, message = check_disk_space()
    print(f"{'✓' if success else '⚠'} Disk Space: {message}")

    # Memory
    success, message = check_memory()
    print(f"{'✓' if success else '⚠'} Memory: {message}")

    # Check PyTorch and CUDA
    print_section("PyTorch & CUDA")
    success, message, torch_info = check_torch_cuda()
    print(f"{'✓' if success else '✗'} {message}")

    if success and torch_info:
        print(f"  - Version: {torch_info['torch_version']}")
        print(f"  - CUDA Available: {torch_info['cuda_available']}")

        if torch_info['cuda_available']:
            print(f"  - CUDA Version: {torch_info['cuda_version']}")
            print(f"  - cuDNN Version: {torch_info['cudnn_version']}")
            print(f"  - GPU Count: {torch_info['device_count']}")

            if verbose:
                for device in torch_info['devices']:
                    print(f"\n  GPU {device['id']}:")
                    print(f"    - Name: {device['name']}")
                    print(f"    - Compute Capability: {device['capability']}")
                    print(f"    - Memory: {device['total_memory']:.2f} GB")

        if torch_info.get('mps_available'):
            print(f"  - Apple Silicon MPS: Available")

    if not success:
        all_checks_passed = False

    # Check required packages
    print_section("Required Packages")
    failed_packages = []

    for package, min_version in REQUIRED_PACKAGES.items():
        success, message = check_package_version(package, min_version)
        print(f"{'✓' if success else '✗'} {message}")
        if not success:
            failed_packages.append(package)
            all_checks_passed = False

    # Check optional packages
    print_section("Optional Packages")
    for package, min_version in OPTIONAL_PACKAGES.items():
        success, message = check_package_version(package, min_version)
        status_symbol = '✓' if success else '⚠'
        print(f"{status_symbol} {message}")
        # Don't fail overall check for optional packages

    # Check critical imports
    print_section("Critical Imports")

    # Transformers
    success, message = check_transformers()
    print(f"{'✓' if success else '✗'} {message}")
    if not success:
        all_checks_passed = False

    # PEFT
    success, message = check_peft()
    print(f"{'✓' if success else '✗'} {message}")
    if not success:
        all_checks_passed = False

    # Print summary
    print_section("Verification Summary")

    if all_checks_passed:
        print("✓ ALL CHECKS PASSED!")
        print("\nYour environment is ready for adapter training.")
        print("\nNext steps:")
        print("  1. Review the installation guide: docs/training/installation-guide.md")
        print("  2. Start training: docs/training/adapter-training-guide.md")
        print("  3. Quick start: docs/training/quick-start.md")
        return True
    else:
        print("✗ SOME CHECKS FAILED!")
        print("\nPlease fix the issues above before proceeding.")

        if failed_packages:
            print("\nFailed packages:")
            for package in failed_packages:
                print(f"  - {package}")
            print("\nTo install missing packages:")
            print("  pip install -r backend/training/requirements.txt")

        print("\nFor troubleshooting, see:")
        print("  docs/training/installation-guide.md#troubleshooting")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify Kwanzaa training environment setup"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information"
    )

    args = parser.parse_args()

    try:
        success = run_verification(verbose=args.verbose)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
