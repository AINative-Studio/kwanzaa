#!/usr/bin/env python3
"""
Train AINative Platform Adapter

Simple training script using unsloth for QLoRA fine-tuning
of Llama-3.2-1B on AINative platform expertise.

Issue: #76
Epic: #69
"""

import json
import os
from pathlib import Path

# Training configuration
CONFIG = {
    "model_name": "unsloth/Llama-3.2-1B-Instruct",
    "max_seq_length": 2048,
    "load_in_4bit": True,

    # LoRA config
    "r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],

    # Training args
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "num_train_epochs": 4,
    "learning_rate": 2e-4,
    "fp16": False,
    "bf16": True,
    "logging_steps": 5,
    "optim": "adamw_8bit",
    "weight_decay": 0.01,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.03,
    "seed": 42,

    # Output
    "output_dir": "outputs/ainative-adapter-v1",
    "save_steps": 5,
    "eval_steps": 5,
    "save_total_limit": 3,

    # Data
    "train_file": "data/training/ainative_train.jsonl",
    "eval_file": "data/training/ainative_eval.jsonl",
}


def load_jsonl(file_path):
    """Load JSONL file."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def format_prompt(example):
    """Format example into Llama-3 chat format."""
    messages = example["messages"]

    # Build conversation
    text = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "system":
            text += f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
        elif role == "user":
            text += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
        elif role == "assistant":
            text += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"

    return text


def main():
    """Train AINative adapter."""
    print("=" * 70)
    print("AINATIVE ADAPTER TRAINING")
    print("=" * 70)

    # Check dependencies
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        import torch
    except ImportError as e:
        print(f"\nError: Missing required package: {e}")
        print("\nPlease install training dependencies:")
        print("  pip install unsloth trl transformers torch")
        return 1

    # Load datasets
    print("\nLoading datasets...")
    train_data = load_jsonl(CONFIG["train_file"])
    eval_data = load_jsonl(CONFIG["eval_file"])

    print(f"  Train examples: {len(train_data)}")
    print(f"  Eval examples: {len(eval_data)}")

    # Format datasets
    print("\nFormatting datasets...")
    train_texts = [format_prompt(ex) for ex in train_data]
    eval_texts = [format_prompt(ex) for ex in eval_data]

    # Create datasets
    from datasets import Dataset
    train_dataset = Dataset.from_dict({"text": train_texts})
    eval_dataset = Dataset.from_dict({"text": eval_texts})

    # Load model
    print(f"\nLoading model: {CONFIG['model_name']}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=CONFIG["model_name"],
        max_seq_length=CONFIG["max_seq_length"],
        dtype=None,
        load_in_4bit=CONFIG["load_in_4bit"],
    )

    # Add LoRA adapters
    print("\nAdding LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=CONFIG["r"],
        target_modules=CONFIG["target_modules"],
        lora_alpha=CONFIG["lora_alpha"],
        lora_dropout=CONFIG["lora_dropout"],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=CONFIG["seed"],
    )

    # Training arguments
    print("\nConfiguring training...")
    training_args = TrainingArguments(
        output_dir=CONFIG["output_dir"],
        per_device_train_batch_size=CONFIG["per_device_train_batch_size"],
        gradient_accumulation_steps=CONFIG["gradient_accumulation_steps"],
        num_train_epochs=CONFIG["num_train_epochs"],
        learning_rate=CONFIG["learning_rate"],
        fp16=CONFIG["fp16"],
        bf16=CONFIG["bf16"],
        logging_steps=CONFIG["logging_steps"],
        optim=CONFIG["optim"],
        weight_decay=CONFIG["weight_decay"],
        lr_scheduler_type=CONFIG["lr_scheduler_type"],
        warmup_ratio=CONFIG["warmup_ratio"],
        seed=CONFIG["seed"],
        save_steps=CONFIG["save_steps"],
        eval_steps=CONFIG["eval_steps"],
        save_total_limit=CONFIG["save_total_limit"],
        evaluation_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="tensorboard",
    )

    # Create trainer
    print("\nInitializing trainer...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        dataset_text_field="text",
        max_seq_length=CONFIG["max_seq_length"],
        args=training_args,
    )

    # Train
    print("\n" + "=" * 70)
    print("STARTING TRAINING")
    print("=" * 70)
    print(f"\nModel: {CONFIG['model_name']}")
    print(f"Train examples: {len(train_data)}")
    print(f"Eval examples: {len(eval_data)}")
    print(f"Epochs: {CONFIG['num_train_epochs']}")
    print(f"Batch size: {CONFIG['per_device_train_batch_size']}")
    print(f"Learning rate: {CONFIG['learning_rate']}")
    print(f"Output: {CONFIG['output_dir']}")
    print()

    trainer.train()

    # Save final model
    print("\n" + "=" * 70)
    print("SAVING MODEL")
    print("=" * 70)

    model.save_pretrained(CONFIG["output_dir"])
    tokenizer.save_pretrained(CONFIG["output_dir"])

    print(f"\nModel saved to: {CONFIG['output_dir']}")
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
