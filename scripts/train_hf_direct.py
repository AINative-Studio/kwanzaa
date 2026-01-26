#!/usr/bin/env python3
"""
Direct HuggingFace Training Script - No AutoTrain needed
Uses transformers + TRL + PEFT directly
"""

import json
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from trl import SFTTrainer
try:
    from trl import DataCollatorForCompletionOnlyLM
except ImportError:
    # Fallback for older TRL versions
    DataCollatorForCompletionOnlyLM = None

# Configuration
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
OUTPUT_DIR = "./outputs/kwanzaa-adapter-v2"
TRAIN_FILE = "data/training/kwanzaa_train.jsonl"
EVAL_FILE = "data/training/kwanzaa_eval.jsonl"

print("="*60)
print("Kwanzaa Adapter Training - Direct HF API")
print("="*60)

# Load JSONL data
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

print("\n1. Loading training data...")
train_data = load_jsonl(TRAIN_FILE)
eval_data = load_jsonl(EVAL_FILE)

train_dataset = Dataset.from_list(train_data)
eval_dataset = Dataset.from_list(eval_data)

print(f"   Training samples: {len(train_dataset)}")
print(f"   Eval samples: {len(eval_dataset)}")

# 4-bit quantization config
print("\n2. Configuring 4-bit quantization...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load model and tokenizer
print("\n3. Loading Llama-3.2-1B-Instruct...")
# Force CPU for Mac compatibility
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map={"": "cpu"},  # Force CPU
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Prepare for k-bit training
print("\n4. Preparing model for k-bit training...")
model = prepare_model_for_kbit_training(model)

# LoRA configuration
print("\n5. Applying LoRA adapters...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
trainable_params = model.print_trainable_parameters()

# Format and tokenize with chat template
print("\n6. Applying chat template and tokenizing...")
def format_and_tokenize(example):
    messages = example["messages"]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    # Tokenize
    tokenized = tokenizer(text, truncation=True, max_length=2048, padding=False)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

train_dataset = train_dataset.map(format_and_tokenize, remove_columns=train_dataset.column_names)
eval_dataset = eval_dataset.map(format_and_tokenize, remove_columns=eval_dataset.column_names)

# Training arguments
print("\n7. Configuring training arguments...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_steps=10,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=50,
    save_strategy="epoch",
    save_total_limit=2,
    bf16=False,  # Not supported on Mac
    fp16=False,  # Not supported on Mac
    max_grad_norm=0.3,
    group_by_length=True,
    report_to="none",
    push_to_hub=False,
    use_cpu=True,  # Force CPU training
    no_cuda=True,  # Disable CUDA
)

# Data collator
from transformers import DataCollatorForLanguageModeling
collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Initialize trainer
print("\n8. Initializing SFTTrainer...")
from transformers import Trainer

# Use standard Trainer instead of SFTTrainer for compatibility
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=collator,
)
trainer.tokenizer = tokenizer

# Train!
print("\n" + "="*60)
print("Starting training...")
print("="*60 + "\n")

trainer.train()

print("\n" + "="*60)
print("Training complete!")
print("="*60)

# Save adapter
print("\n9. Saving adapter...")
trainer.model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\nAdapter saved to: {OUTPUT_DIR}")
print("\nFiles created:")
import os
for f in os.listdir(OUTPUT_DIR):
    fpath = os.path.join(OUTPUT_DIR, f)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath) / (1024*1024)
        print(f"  - {f} ({size:.2f} MB)")

print("\n" + "="*60)
print("SUCCESS! Adapter training complete!")
print("="*60)
