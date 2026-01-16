"""Artifact management utilities for adapter training."""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def generate_file_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """
    Generate checksum for a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, md5, sha1)

    Returns:
        Hexadecimal checksum string
    """
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def generate_artifact_checksum(artifact_dir: str) -> Dict[str, str]:
    """
    Generate checksums for all files in artifact directory.

    Args:
        artifact_dir: Path to artifact directory

    Returns:
        Dictionary mapping file paths to checksums
    """
    checksums = {}
    artifact_path = Path(artifact_dir)

    for file_path in artifact_path.rglob("*"):
        if file_path.is_file():
            relative_path = str(file_path.relative_to(artifact_path))
            checksums[relative_path] = generate_file_checksum(str(file_path))

    return checksums


def verify_artifact_integrity(
    artifact_dir: str, checksums: Dict[str, str]
) -> tuple[bool, List[str]]:
    """
    Verify artifact integrity against checksums.

    Args:
        artifact_dir: Path to artifact directory
        checksums: Dictionary of expected checksums

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    artifact_path = Path(artifact_dir)

    for relative_path, expected_checksum in checksums.items():
        file_path = artifact_path / relative_path

        if not file_path.exists():
            errors.append(f"Missing file: {relative_path}")
            continue

        actual_checksum = generate_file_checksum(str(file_path))
        if actual_checksum != expected_checksum:
            errors.append(
                f"Checksum mismatch for {relative_path}: "
                f"expected {expected_checksum}, got {actual_checksum}"
            )

    return len(errors) == 0, errors


def create_artifact_metadata(
    base_model_id: str,
    adapter_config: Dict[str, Any],
    training_config: Dict[str, Any],
    training_metrics: Dict[str, Any],
    version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create metadata for trained adapter artifact.

    Args:
        base_model_id: Hugging Face model ID of base model
        adapter_config: Adapter configuration
        training_config: Training configuration
        training_metrics: Final training metrics
        version: Version string (auto-generated if None)

    Returns:
        Metadata dictionary
    """
    if version is None:
        version = f"v0.1.{int(datetime.now().timestamp())}"

    metadata = {
        "version": version,
        "created_at": datetime.now().isoformat(),
        "base_model": {
            "model_id": base_model_id,
            "model_type": "causal_lm",
        },
        "adapter": {
            "method": adapter_config.get("method", "qlora"),
            "lora_r": adapter_config.get("lora", {}).get("r", 16),
            "lora_alpha": adapter_config.get("lora", {}).get("alpha", 32),
            "lora_dropout": adapter_config.get("lora", {}).get("dropout", 0.05),
            "target_modules": adapter_config.get("lora", {}).get("target_modules", []),
        },
        "training": {
            "num_epochs": training_config.get("training", {}).get("num_train_epochs", 2),
            "learning_rate": training_config.get("training", {}).get("learning_rate", 0.0002),
            "batch_size": training_config.get("training", {}).get(
                "per_device_train_batch_size", 1
            ),
            "gradient_accumulation_steps": training_config.get("training", {}).get(
                "gradient_accumulation_steps", 16
            ),
            "max_seq_length": training_config.get("data", {}).get("max_seq_length", 2048),
        },
        "metrics": training_metrics,
        "task": training_config.get("artifacts", {})
        .get("metadata", {})
        .get("task", "citation_grounded_chat"),
        "dataset_version": training_config.get("artifacts", {})
        .get("metadata", {})
        .get("dataset_version", "v0"),
    }

    return metadata


def save_adapter_artifact(
    output_dir: str,
    adapter_path: str,
    training_config: Dict[str, Any],
    training_metrics: Dict[str, Any],
    base_model_id: str,
    generate_checksums: bool = True,
) -> Dict[str, Any]:
    """
    Save adapter artifact with metadata and checksums.

    Args:
        output_dir: Directory to save artifact
        adapter_path: Path to trained adapter
        training_config: Training configuration
        training_metrics: Training metrics
        base_model_id: Base model identifier
        generate_checksums: Whether to generate checksums

    Returns:
        Artifact metadata
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy adapter files
    adapter_src = Path(adapter_path)
    if adapter_src.exists():
        for file_path in adapter_src.iterdir():
            if file_path.is_file():
                shutil.copy2(file_path, output_path / file_path.name)

    # Create metadata
    adapter_config = training_config.get("adapter", {})
    metadata = create_artifact_metadata(
        base_model_id=base_model_id,
        adapter_config=adapter_config,
        training_config=training_config,
        training_metrics=training_metrics,
    )

    # Save metadata
    metadata_path = output_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save training config
    config_path = output_path / "training_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(training_config, f, default_flow_style=False)

    # Save training metrics
    metrics_path = output_path / "training_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(training_metrics, f, indent=2)

    # Generate checksums
    if generate_checksums:
        checksums = generate_artifact_checksum(str(output_path))
        checksums_path = output_path / "checksums.json"
        with open(checksums_path, "w") as f:
            json.dump(checksums, f, indent=2)
        metadata["checksums"] = checksums

    # Create README
    readme_content = generate_adapter_readme(metadata, base_model_id)
    readme_path = output_path / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)

    return metadata


def generate_adapter_readme(metadata: Dict[str, Any], base_model_id: str) -> str:
    """
    Generate README for adapter artifact.

    Args:
        metadata: Adapter metadata
        base_model_id: Base model identifier

    Returns:
        README content as string
    """
    adapter_info = metadata.get("adapter", {})
    training_info = metadata.get("training", {})
    metrics = metadata.get("metrics", {})

    readme = f"""# Kwanzaa Adapter - {metadata.get('version', 'v0.1.0')}

Citation-grounded chat adapter trained with QLoRA.

## Model Information

- **Base Model**: {base_model_id}
- **Adapter Method**: {adapter_info.get('method', 'qlora')}
- **Task**: {metadata.get('task', 'citation-grounded-chat')}
- **Created**: {metadata.get('created_at', 'N/A')}

## Adapter Configuration

- **LoRA Rank (r)**: {adapter_info.get('lora_r', 16)}
- **LoRA Alpha**: {adapter_info.get('lora_alpha', 32)}
- **LoRA Dropout**: {adapter_info.get('lora_dropout', 0.05)}
- **Target Modules**: {', '.join(adapter_info.get('target_modules', []))}

## Training Configuration

- **Epochs**: {training_info.get('num_epochs', 2)}
- **Learning Rate**: {training_info.get('learning_rate', 0.0002)}
- **Batch Size**: {training_info.get('batch_size', 1)}
- **Gradient Accumulation**: {training_info.get('gradient_accumulation_steps', 16)}
- **Max Sequence Length**: {training_info.get('max_seq_length', 2048)}

## Training Metrics

- **Final Loss**: {metrics.get('final_loss', 'N/A')}
- **Final Perplexity**: {metrics.get('final_perplexity', 'N/A')}
- **Best Eval Loss**: {metrics.get('best_eval_loss', 'N/A')}

## Usage

```python
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "{base_model_id}",
    torch_dtype="auto",
    device_map="auto"
)

# Load adapter
model = PeftModel.from_pretrained(base_model, "./")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("{base_model_id}")

# Generate
inputs = tokenizer("Your prompt here", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=800, temperature=0.2)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## License

This adapter is released under the Apache 2.0 license, matching the base model license.
"""

    return readme


def load_artifact_metadata(artifact_dir: str) -> Dict[str, Any]:
    """
    Load artifact metadata from directory.

    Args:
        artifact_dir: Path to artifact directory

    Returns:
        Metadata dictionary
    """
    metadata_path = Path(artifact_dir) / "metadata.json"
    with open(metadata_path, "r") as f:
        return json.load(f)


def verify_artifact(artifact_dir: str) -> tuple[bool, List[str]]:
    """
    Verify artifact completeness and integrity.

    Args:
        artifact_dir: Path to artifact directory

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    artifact_path = Path(artifact_dir)

    # Check required files
    required_files = [
        "adapter_config.json",
        "adapter_model.safetensors",
        "metadata.json",
        "training_config.yaml",
        "checksums.json",
    ]

    for required_file in required_files:
        if not (artifact_path / required_file).exists():
            errors.append(f"Missing required file: {required_file}")

    # If checksums exist, verify integrity
    checksums_path = artifact_path / "checksums.json"
    if checksums_path.exists():
        with open(checksums_path, "r") as f:
            checksums = json.load(f)
        is_valid, integrity_errors = verify_artifact_integrity(
            str(artifact_path), checksums
        )
        errors.extend(integrity_errors)

    return len(errors) == 0, errors
