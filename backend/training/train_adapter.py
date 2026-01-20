#!/usr/bin/env python3
"""
Adapter training script for Kwanzaa citation-grounded chat.

This script trains a QLoRA adapter on top of a base model (AI2 OLMo-7B-Instruct by default)
while ensuring base model weights remain unchanged. Includes comprehensive logging,
checkpointing, and artifact generation with checksums.
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

import torch
import yaml
from datasets import load_dataset
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)

# Add parent directory to path to import utilities
sys.path.append(str(Path(__file__).parent.parent))

from training.utils.artifacts import (
    save_adapter_artifact,
    generate_artifact_checksum,
    verify_artifact,
)
from training.utils.metrics import (
    TrainingMetrics,
    MetricsTracker,
    compute_perplexity,
    log_training_progress,
)
from training.utils.verification import (
    save_base_model_checksums,
    verify_base_weights_unchanged,
    get_trainable_parameters_summary,
    verify_only_adapter_trainable,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def load_training_config(config_path: str) -> Dict[str, Any]:
    """Load training configuration from YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded training config from {config_path}")
    return config


def setup_model_and_tokenizer(config: Dict[str, Any]) -> tuple:
    """
    Setup base model, tokenizer, and apply QLoRA configuration.

    Args:
        config: Training configuration

    Returns:
        Tuple of (model, tokenizer, peft_config)
    """
    model_config = config["model"]
    adapter_config = config["adapter"]
    quant_config = adapter_config["quantization"]

    logger.info(f"Loading base model: {model_config['base_model_id']}")

    # Configure 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=quant_config["load_in_4bit"],
        bnb_4bit_compute_dtype=getattr(
            torch, quant_config["bnb_4bit_compute_dtype"]
        ),
        bnb_4bit_use_double_quant=quant_config["bnb_4bit_use_double_quant"],
        bnb_4bit_quant_type=quant_config["bnb_4bit_quant_type"],
    )

    # Load base model with quantization
    torch_dtype_str = model_config.get("torch_dtype", "auto")
    if torch_dtype_str == "auto":
        torch_dtype = "auto"
    elif isinstance(torch_dtype_str, str):
        torch_dtype = getattr(torch, torch_dtype_str)
    else:
        torch_dtype = torch_dtype_str

    model = AutoModelForCausalLM.from_pretrained(
        model_config["base_model_id"],
        quantization_config=bnb_config,
        device_map=model_config.get("device_map", "auto"),
        trust_remote_code=model_config.get("trust_remote_code", True),
        torch_dtype=torch_dtype,
    )

    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_config["base_model_id"],
        trust_remote_code=model_config.get("trust_remote_code", True),
    )

    # Set padding token if not set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = model.config.eos_token_id

    # Configure LoRA
    lora_config_dict = adapter_config["lora"]
    peft_config = LoraConfig(
        r=lora_config_dict["r"],
        lora_alpha=lora_config_dict["alpha"],
        lora_dropout=lora_config_dict["dropout"],
        bias=lora_config_dict["bias"],
        task_type=TaskType.CAUSAL_LM,
        target_modules=lora_config_dict["target_modules"],
    )

    # Apply LoRA to model
    model = get_peft_model(model, peft_config)

    logger.info("Model and tokenizer setup complete")

    # Log trainable parameters
    param_summary = get_trainable_parameters_summary(model)
    logger.info(
        f"Trainable parameters: {param_summary['trainable_params']:,} / "
        f"{param_summary['total_params']:,} "
        f"({param_summary['trainable_percent']:.2f}%)"
    )

    # Verify only adapter parameters are trainable
    is_correct, issues = verify_only_adapter_trainable(model)
    if not is_correct:
        logger.warning(f"Adapter configuration issues detected: {issues}")
    else:
        logger.info("Verified: Only adapter parameters are trainable")

    return model, tokenizer, peft_config


def load_and_prepare_dataset(config: Dict[str, Any], tokenizer) -> tuple:
    """
    Load and prepare training and evaluation datasets.

    Args:
        config: Training configuration
        tokenizer: Tokenizer for preprocessing

    Returns:
        Tuple of (train_dataset, eval_dataset)
    """
    data_config = config["data"]

    logger.info(f"Loading datasets from {data_config['train_file']}")

    # Load datasets
    train_dataset = load_dataset(
        "json", data_files=data_config["train_file"], split="train"
    )
    eval_dataset = load_dataset(
        "json", data_files=data_config["eval_file"], split="train"
    )

    logger.info(f"Train dataset size: {len(train_dataset)}")
    logger.info(f"Eval dataset size: {len(eval_dataset)}")

    # Tokenization function
    def tokenize_function(examples):
        # Assume messages format: [{"role": "system", "content": "..."}, ...]
        texts = []
        for messages in examples["messages"]:
            # Concatenate messages into single text
            text_parts = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                text_parts.append(f"{role}: {content}")
            text = "\n".join(text_parts)
            texts.append(text)

        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            max_length=data_config["max_seq_length"],
            padding="max_length",
            return_tensors="pt",
        )

        # Add labels (same as input_ids for causal LM)
        tokenized["labels"] = tokenized["input_ids"].clone()

        return tokenized

    # Apply tokenization
    train_dataset = train_dataset.map(
        tokenize_function,
        batched=True,
        num_proc=data_config.get("num_proc", 4),
        remove_columns=train_dataset.column_names,
    )

    eval_dataset = eval_dataset.map(
        tokenize_function,
        batched=True,
        num_proc=data_config.get("num_proc", 4),
        remove_columns=eval_dataset.column_names,
    )

    logger.info("Dataset preparation complete")

    return train_dataset, eval_dataset


def create_training_arguments(config: Dict[str, Any], output_dir: str) -> TrainingArguments:
    """
    Create Hugging Face TrainingArguments from config.

    Args:
        config: Training configuration
        output_dir: Output directory for checkpoints

    Returns:
        TrainingArguments object
    """
    run_config = config["run"]
    training_config = config["training"]
    eval_config = config["evaluation"]
    checkpoint_config = config["checkpointing"]

    return TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=training_config["num_train_epochs"],
        per_device_train_batch_size=training_config["per_device_train_batch_size"],
        per_device_eval_batch_size=training_config["per_device_eval_batch_size"],
        gradient_accumulation_steps=training_config["gradient_accumulation_steps"],
        learning_rate=training_config["learning_rate"],
        lr_scheduler_type=training_config["lr_scheduler_type"],
        warmup_ratio=training_config["warmup_ratio"],
        weight_decay=training_config["weight_decay"],
        max_grad_norm=training_config["max_grad_norm"],
        optim=training_config["optim"],
        fp16=run_config["mixed_precision"] == "fp16",
        bf16=run_config["mixed_precision"] == "bf16",
        logging_steps=run_config["logging_steps"],
        save_steps=checkpoint_config["save_steps"],
        eval_steps=eval_config.get("steps", 200),
        evaluation_strategy=eval_config.get("strategy", "steps"),
        save_strategy=checkpoint_config["save_strategy"],
        save_total_limit=checkpoint_config["save_total_limit"],
        load_best_model_at_end=checkpoint_config["load_best_model_at_end"],
        metric_for_best_model=checkpoint_config["metric_for_best_model"],
        greater_is_better=checkpoint_config["greater_is_better"],
        report_to=run_config.get("report_to", ["tensorboard"]),
        seed=run_config["seed"],
        dataloader_num_workers=run_config.get("dataloader_num_workers", 4),
        dataloader_pin_memory=run_config.get("dataloader_pin_memory", True),
        gradient_checkpointing=training_config["gradient_checkpointing"],
        remove_unused_columns=False,
    )


def train_adapter(config_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Main training function.

    Args:
        config_path: Path to training configuration YAML
        output_dir: Optional override for output directory

    Returns:
        Dictionary with training results and artifact paths
    """
    # Load configuration
    config = load_training_config(config_path)

    # Setup output directory
    if output_dir is None:
        output_dir = config["run"]["output_dir"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {output_dir}")

    # Initialize metrics tracker
    metrics_tracker = MetricsTracker(output_dir)

    # Setup model and tokenizer
    model, tokenizer, peft_config = setup_model_and_tokenizer(config)

    # Save base model checksums before training
    baseline_checksums_path = output_path / "baseline_checksums.json"
    logger.info("Saving baseline checksums of base model weights")
    save_base_model_checksums(model, str(baseline_checksums_path))

    # Load and prepare datasets
    train_dataset, eval_dataset = load_and_prepare_dataset(config, tokenizer)

    # Create training arguments
    training_args = create_training_arguments(config, output_dir)

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Causal LM, not masked LM
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    # Start training
    logger.info("Starting training...")
    start_time = time.time()

    train_result = trainer.train()

    training_time = time.time() - start_time
    logger.info(f"Training completed in {training_time:.2f} seconds")

    # Verify base weights unchanged
    logger.info("Verifying base model weights unchanged...")
    is_unchanged, differences = verify_base_weights_unchanged(
        model, str(baseline_checksums_path)
    )

    if is_unchanged:
        logger.info("SUCCESS: Base model weights remain unchanged")
    else:
        logger.error("ERROR: Base model weights were modified!")
        logger.error(f"Differences detected: {len(differences)}")
        for diff in differences[:5]:  # Log first 5 differences
            logger.error(f"  - {diff}")

    # Get final metrics
    final_eval = trainer.evaluate()
    final_loss = final_eval.get("eval_loss", 0.0)
    final_perplexity = compute_perplexity(final_loss)

    logger.info(f"Final eval loss: {final_loss:.4f}")
    logger.info(f"Final perplexity: {final_perplexity:.2f}")

    # Collect training metrics
    training_metrics = {
        "final_loss": train_result.metrics.get("train_loss", 0.0),
        "final_eval_loss": final_loss,
        "final_perplexity": final_perplexity,
        "training_time_seconds": training_time,
        "total_steps": train_result.metrics.get("train_steps", 0),
        "epochs_completed": train_result.metrics.get("epoch", 0),
        "best_model_checkpoint": trainer.state.best_model_checkpoint,
    }

    # Save metrics summary
    metrics_tracker.save_summary()

    # Save adapter
    logger.info("Saving trained adapter...")
    adapter_output_dir = output_path / "adapter"
    trainer.model.save_pretrained(str(adapter_output_dir))
    tokenizer.save_pretrained(str(adapter_output_dir))

    # Create final artifact with checksums
    logger.info("Creating final artifact package...")
    artifact_metadata = save_adapter_artifact(
        output_dir=str(output_path / "final_artifact"),
        adapter_path=str(adapter_output_dir),
        training_config=config,
        training_metrics=training_metrics,
        base_model_id=config["model"]["base_model_id"],
        generate_checksums=config["checkpointing"].get("generate_checksums", True),
    )

    # Verify artifact integrity
    is_valid, errors = verify_artifact(str(output_path / "final_artifact"))
    if is_valid:
        logger.info("Artifact integrity verification passed")
    else:
        logger.error(f"Artifact verification failed: {errors}")

    results = {
        "success": is_unchanged and is_valid,
        "training_metrics": training_metrics,
        "artifact_metadata": artifact_metadata,
        "output_directory": str(output_path),
        "adapter_path": str(adapter_output_dir),
        "final_artifact_path": str(output_path / "final_artifact"),
        "base_weights_unchanged": is_unchanged,
        "artifact_valid": is_valid,
    }

    # Save results summary
    results_path = output_path / "training_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Training results saved to {results_path}")
    logger.info("=" * 80)
    logger.info("TRAINING COMPLETE")
    logger.info(f"Success: {results['success']}")
    logger.info(f"Final artifact: {results['final_artifact_path']}")
    logger.info("=" * 80)

    return results


def main():
    """Command-line interface for adapter training."""
    parser = argparse.ArgumentParser(
        description="Train QLoRA adapter for Kwanzaa citation-grounded chat"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="backend/training/config/training.yaml",
        help="Path to training configuration YAML file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (overrides config)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing artifact without training",
    )
    parser.add_argument(
        "--artifact-dir",
        type=str,
        default=None,
        help="Artifact directory to verify (with --verify-only)",
    )

    args = parser.parse_args()

    if args.verify_only:
        if not args.artifact_dir:
            parser.error("--artifact-dir required with --verify-only")

        logger.info(f"Verifying artifact at {args.artifact_dir}")
        is_valid, errors = verify_artifact(args.artifact_dir)

        if is_valid:
            logger.info("Artifact verification PASSED")
            sys.exit(0)
        else:
            logger.error("Artifact verification FAILED")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)

    # Run training
    try:
        results = train_adapter(args.config, args.output_dir)
        sys.exit(0 if results["success"] else 1)
    except Exception as e:
        logger.error(f"Training failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
