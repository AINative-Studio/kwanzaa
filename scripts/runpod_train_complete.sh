#!/bin/bash
# Complete Kwanzaa Training Script for RunPod
# Copy and paste this entire script into the RunPod web terminal

set -e

echo "=== Kwanzaa Adapter Training on RunPod ==="
echo "Starting setup..."

# Install dependencies
echo "[1/6] Installing dependencies..."
pip install -q transformers==4.36.0 datasets peft bitsandbytes accelerate torch trl pyyaml scipy

# Create directories
echo "[2/6] Creating directories..."
mkdir -p /workspace/data/training
mkdir -p /workspace/outputs

# Create training data (embedded in script)
echo "[3/6] Creating training data..."

# We'll download from a public source or use base64
# For now, create a minimal training script that works

cat > /workspace/train_kwanzaa.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""Kwanzaa Adapter Training Script"""

import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset

print("[INFO] Starting Kwanzaa adapter training")
print("[INFO] GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")

# Configuration
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
OUTPUT_DIR = "/workspace/outputs/kwanzaa-adapter-v0"

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

print(f"[INFO] Loading model: {MODEL_ID}")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# LoRA configuration
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

print("[INFO] Preparing model for training")
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Load dataset
print("[INFO] Loading training data")
try:
    dataset = load_dataset("json", data_files={
        "train": "/workspace/data/training/kwanzaa_train.jsonl",
        "eval": "/workspace/data/training/kwanzaa_eval.jsonl",
    })
    print(f"[INFO] Training samples: {len(dataset['train'])}")
    print(f"[INFO] Eval samples: {len(dataset['eval'])}")
except Exception as e:
    print(f"[ERROR] Could not load data: {e}")
    print("[INFO] Creating minimal test dataset instead")
    # Create minimal dataset for testing
    from datasets import Dataset
    test_data = {
        "messages": [
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is Kwanzaa?"},
                {"role": "assistant", "content": "Kwanzaa is an African American holiday."}
            ]
        ] * 10
    }
    dataset = {"train": Dataset.from_dict(test_data), "eval": Dataset.from_dict(test_data)}

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=4,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=7,
    eval_steps=7,
    save_steps=7,
    save_total_limit=3,
    evaluation_strategy="steps",
    load_best_model_at_end=True,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
)

# Format messages function
def format_messages(example):
    if isinstance(example["messages"], str):
        return {"text": example["messages"]}

    # Format chat messages
    formatted = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False
    )
    return {"text": formatted}

# Create trainer
print("[INFO] Creating trainer")
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["eval"],
    tokenizer=tokenizer,
    formatting_func=format_messages,
    max_seq_length=2048,
    packing=True,
)

# Train
print("[INFO] Starting training...")
print("=" * 60)
trainer.train()
print("=" * 60)

# Save
print("[INFO] Saving adapter...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"[SUCCESS] Training complete!")
print(f"[INFO] Adapter saved to: {OUTPUT_DIR}")
print(f"[INFO] Files:")
import os
for f in os.listdir(OUTPUT_DIR):
    size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    print(f"  - {f} ({size / 1024 / 1024:.2f} MB)")

PYTHON_SCRIPT

echo "[4/6] Training script created"
echo ""
echo "=== IMPORTANT: Upload Training Data ==="
echo "Before running training, you need to upload the training data files:"
echo ""
echo "Option 1: Use Jupyter Lab to upload files"
echo "  1. Click 'Upload' button"
echo "  2. Upload kwanzaa_train.jsonl to /workspace/data/training/"
echo "  3. Upload kwanzaa_eval.jsonl to /workspace/data/training/"
echo ""
echo "Option 2: Use wget/curl if files are hosted"
echo "  wget -O /workspace/data/training/kwanzaa_train.jsonl YOUR_URL"
echo ""
echo "Option 3: Training will use test data if files not found"
echo ""
read -p "Press ENTER when data is uploaded (or to continue with test data)..."

echo "[5/6] Starting training..."
python /workspace/train_kwanzaa.py

echo "[6/6] Training complete!"
echo ""
echo "Download your adapter:"
echo "  Location: /workspace/outputs/kwanzaa-adapter-v0/"
echo "  Use Jupyter Lab to download the folder"
echo ""
echo "=== Training Complete ==="
