"""Model verification utilities to ensure base weights remain unchanged."""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

import torch


def compute_model_state_checksum(state_dict: Dict[str, torch.Tensor]) -> Dict[str, str]:
    """
    Compute checksums for all tensors in model state dict.

    Args:
        state_dict: Model state dictionary

    Returns:
        Dictionary mapping parameter names to checksums
    """
    checksums = {}
    for name, tensor in state_dict.items():
        # Convert tensor to bytes and compute hash
        tensor_bytes = tensor.cpu().numpy().tobytes()
        checksum = hashlib.sha256(tensor_bytes).hexdigest()
        checksums[name] = checksum
    return checksums


def save_base_model_checksums(
    model: torch.nn.Module, output_path: str, adapter_param_prefix: str = "base_model"
) -> Dict[str, str]:
    """
    Save checksums of base model weights before training.

    Args:
        model: Model with adapters attached
        output_path: Path to save checksums
        adapter_param_prefix: Prefix for adapter parameters to exclude

    Returns:
        Dictionary of base model checksums
    """
    state_dict = model.state_dict()

    # Filter to only base model parameters (exclude adapter params)
    base_params = {
        name: param
        for name, param in state_dict.items()
        if not any(
            adapter_key in name
            for adapter_key in ["lora", "adapter", "modules_to_save"]
        )
    }

    checksums = compute_model_state_checksum(base_params)

    # Save checksums to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(checksums, f, indent=2)

    return checksums


def compare_model_checksums(
    model: torch.nn.Module,
    baseline_checksums: Dict[str, str],
    adapter_param_prefix: str = "base_model",
) -> tuple[bool, List[str]]:
    """
    Compare current model checksums against baseline.

    Args:
        model: Model to check
        baseline_checksums: Baseline checksums to compare against
        adapter_param_prefix: Prefix for adapter parameters to exclude

    Returns:
        Tuple of (all_match, list_of_differences)
    """
    state_dict = model.state_dict()

    # Filter to only base model parameters
    base_params = {
        name: param
        for name, param in state_dict.items()
        if not any(
            adapter_key in name
            for adapter_key in ["lora", "adapter", "modules_to_save"]
        )
    }

    current_checksums = compute_model_state_checksum(base_params)

    differences = []
    for name, baseline_checksum in baseline_checksums.items():
        if name not in current_checksums:
            differences.append(f"Missing parameter: {name}")
            continue

        if current_checksums[name] != baseline_checksum:
            differences.append(
                f"Parameter modified: {name} "
                f"(baseline: {baseline_checksum[:8]}..., "
                f"current: {current_checksums[name][:8]}...)"
            )

    return len(differences) == 0, differences


def verify_base_weights_unchanged(
    model: torch.nn.Module, baseline_checksums_path: str
) -> tuple[bool, List[str]]:
    """
    Verify that base model weights have not changed during training.

    Args:
        model: Trained model with adapters
        baseline_checksums_path: Path to baseline checksums file

    Returns:
        Tuple of (is_unchanged, list_of_changes)
    """
    # Load baseline checksums
    with open(baseline_checksums_path, "r") as f:
        baseline_checksums = json.load(f)

    # Compare against current state
    is_unchanged, differences = compare_model_checksums(model, baseline_checksums)

    return is_unchanged, differences


def save_adapter_only_params(
    model: torch.nn.Module, output_path: str
) -> Dict[str, torch.Tensor]:
    """
    Extract and save only adapter parameters.

    Args:
        model: Model with adapters
        output_path: Path to save adapter parameters

    Returns:
        Dictionary of adapter parameters
    """
    state_dict = model.state_dict()

    # Filter to only adapter parameters
    adapter_params = {
        name: param
        for name, param in state_dict.items()
        if any(
            adapter_key in name
            for adapter_key in ["lora", "adapter", "modules_to_save"]
        )
    }

    # Save adapter parameters
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    torch.save(adapter_params, output_file)

    return adapter_params


def load_and_verify_adapter(
    base_model: torch.nn.Module,
    adapter_path: str,
    baseline_checksums_path: Optional[str] = None,
) -> tuple[torch.nn.Module, bool, List[str]]:
    """
    Load adapter and verify base model integrity.

    Args:
        base_model: Base model to load adapter onto
        adapter_path: Path to adapter weights
        baseline_checksums_path: Optional path to baseline checksums

    Returns:
        Tuple of (model_with_adapter, is_valid, verification_errors)
    """
    from peft import PeftModel

    # Load adapter
    model = PeftModel.from_pretrained(base_model, adapter_path)

    verification_errors = []
    is_valid = True

    # Verify base weights if baseline provided
    if baseline_checksums_path:
        is_valid, verification_errors = verify_base_weights_unchanged(
            model, baseline_checksums_path
        )

    return model, is_valid, verification_errors


def get_trainable_parameters_summary(model: torch.nn.Module) -> Dict[str, any]:
    """
    Get summary of trainable vs frozen parameters.

    Args:
        model: Model to analyze

    Returns:
        Dictionary with parameter statistics
    """
    trainable_params = 0
    all_params = 0
    trainable_names = []

    for name, param in model.named_parameters():
        all_params += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
            trainable_names.append(name)

    trainable_percent = 100 * trainable_params / all_params if all_params > 0 else 0

    return {
        "total_params": all_params,
        "trainable_params": trainable_params,
        "frozen_params": all_params - trainable_params,
        "trainable_percent": trainable_percent,
        "trainable_param_names": trainable_names,
    }


def verify_only_adapter_trainable(model: torch.nn.Module) -> tuple[bool, List[str]]:
    """
    Verify that only adapter parameters are trainable.

    Args:
        model: Model to check

    Returns:
        Tuple of (is_correct, list_of_issues)
    """
    issues = []

    for name, param in model.named_parameters():
        is_adapter_param = any(
            adapter_key in name
            for adapter_key in ["lora", "adapter", "modules_to_save"]
        )

        if is_adapter_param and not param.requires_grad:
            issues.append(f"Adapter parameter not trainable: {name}")
        elif not is_adapter_param and param.requires_grad:
            issues.append(f"Base model parameter is trainable: {name}")

    return len(issues) == 0, issues
