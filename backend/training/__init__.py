"""
Adapter training module for Kwanzaa.

This module provides utilities and scripts for training QLoRA adapters on top of
base models while ensuring base weights remain unchanged.

Key Components:
- train_adapter.py: Main training script
- utils/: Training utilities (artifacts, metrics, verification)
- config/: Training configurations

Example Usage:
    python backend/training/train_adapter.py --config backend/training/config/training.yaml

For detailed documentation, see docs/training/adapter-training-guide.md
"""

__version__ = "0.1.0"
