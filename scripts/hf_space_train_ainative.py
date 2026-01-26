#!/usr/bin/env python3
"""
AINative Adapter Training for HuggingFace Spaces

This script trains the AINative platform adapter on HuggingFace Spaces
using ZeroGPU and AutoTrain-Advanced.

Issue: #76
Epic: #69
"""

import os
import json
from pathlib import Path
import gradio as gr

# Training configuration
TRAINING_CONFIG = {
    "project_name": "ainative-adapter-v1",
    "model": "unsloth/Llama-3.2-1B-Instruct",
    "train_split": "train",
    "valid_split": "validation",
    "trainer": "sft",
    "text_column": "text",
    "learning_rate": 0.0002,
    "num_epochs": 4,
    "batch_size": 2,
    "gradient_accumulation": 8,
    "warmup_ratio": 0.03,
    "optimizer": "adamw_torch",
    "scheduler": "cosine",
    "weight_decay": 0.01,
    "max_seq_length": 2048,
    "peft": True,
    "quantization": "int4",
    "lora_r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "logging_steps": 5,
    "eval_steps": 5,
    "save_steps": 5,
    "save_total_limit": 3,
    "fp16": False,
    "bf16": True,
    "seed": 42,
}


def format_messages_to_text(messages):
    """Convert messages format to Llama-3 chat format."""
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


def prepare_dataset():
    """Prepare dataset in HuggingFace format."""
    print("📚 Loading datasets...")

    # Load JSONL files
    train_data = []
    eval_data = []

    train_file = Path("data/training/ainative_train.jsonl")
    eval_file = Path("data/training/ainative_eval.jsonl")

    if train_file.exists():
        with open(train_file, 'r') as f:
            for line in f:
                example = json.loads(line)
                text = format_messages_to_text(example["messages"])
                train_data.append({"text": text})

    if eval_file.exists():
        with open(eval_file, 'r') as f:
            for line in f:
                example = json.loads(line)
                text = format_messages_to_text(example["messages"])
                eval_data.append({"text": text})

    print(f"✅ Train examples: {len(train_data)}")
    print(f"✅ Eval examples: {len(eval_data)}")

    # Save formatted dataset
    from datasets import Dataset, DatasetDict

    dataset = DatasetDict({
        "train": Dataset.from_list(train_data),
        "validation": Dataset.from_list(eval_data)
    })

    # Push to HuggingFace Hub
    token = os.getenv("HF_TOKEN")
    if token:
        dataset.push_to_hub("ainative/ainative-training-v1", token=token, private=False)
        print("✅ Dataset uploaded to HuggingFace Hub")

    return dataset


def train_adapter():
    """Train the adapter using AutoTrain-Advanced."""
    try:
        from autotrain.trainers.clm.train_sft import train as train_sft
        from autotrain.trainers.common import AutoTrainParams
    except ImportError:
        return "❌ Error: autotrain-advanced not installed"

    # Prepare dataset
    dataset = prepare_dataset()

    # Create training params
    params = AutoTrainParams(**TRAINING_CONFIG)

    # Train
    print("\n🚀 Starting training...")
    print(f"Model: {TRAINING_CONFIG['model']}")
    print(f"Epochs: {TRAINING_CONFIG['num_epochs']}")
    print(f"Learning Rate: {TRAINING_CONFIG['learning_rate']}")

    try:
        train_sft(params)
        return "✅ Training complete! Model saved to outputs/"
    except Exception as e:
        return f"❌ Training failed: {str(e)}"


def create_gradio_interface():
    """Create Gradio interface for HuggingFace Spaces."""
    with gr.Blocks(title="AINative Adapter Training") as demo:
        gr.Markdown("# 🚀 AINative Platform Adapter Training")
        gr.Markdown("Training Llama-3.2-1B on AINative platform expertise")

        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📊 Training Configuration")
                gr.JSON(TRAINING_CONFIG, label="Configuration")

            with gr.Column():
                gr.Markdown("## 📈 Status")
                status_output = gr.Textbox(label="Training Status", lines=10)

        with gr.Row():
            train_btn = gr.Button("🚀 Start Training", variant="primary")

        train_btn.click(
            fn=train_adapter,
            outputs=status_output
        )

        gr.Markdown("## 📝 Dataset Info")
        gr.Markdown("""
        - **Train Examples**: 88
        - **Eval Examples**: 10
        - **Categories**: Agent Swarm, AIkit SDK, ZeroDB, Tests, OpenAPI
        - **Quality**: 92% (0 AI attribution violations)
        """)

    return demo


if __name__ == "__main__":
    # For HuggingFace Spaces
    demo = create_gradio_interface()
    demo.launch()
