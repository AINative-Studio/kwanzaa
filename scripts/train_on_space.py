#!/usr/bin/env python3
"""
Training script to run on HuggingFace Space with GPU
Upload this to your Space and run it
"""

import json
import torch
import os
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from transformers import Trainer, DataCollatorForLanguageModeling
from huggingface_hub import login

# Login with HF token from environment
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    login(token=hf_token)
    print("✓ Logged in to HuggingFace")
else:
    print("⚠ Warning: No HF_TOKEN found in environment")

MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
OUTPUT_DIR = "/tmp/kwanzaa-adapter-v1"
HUB_MODEL_ID = "ainativestudio/kwanzaa-adapter-v1"

print("="*60)
print("Kwanzaa Adapter Training on HuggingFace Space")
print("="*60)

# Load data from HuggingFace Hub
print("\n1. Loading training data from HuggingFace Hub...")
dataset = load_dataset("ainativestudio/kwanzaa-training-data")

train_dataset = dataset["train"] if "train" in dataset else dataset
eval_dataset = dataset["validation"] if "validation" in dataset else dataset

print(f"   Training samples: {len(train_dataset)}")
print(f"   Eval samples: {len(eval_dataset) if eval_dataset != train_dataset else 'Using same as train'}")

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
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
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
model.print_trainable_parameters()

# Format chat template
print("\n6. Formatting data with chat template...")
def format_chat(example):
    messages = example["messages"]
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": text}

train_dataset = train_dataset.map(format_chat)
if eval_dataset != train_dataset:
    eval_dataset = eval_dataset.map(format_chat)

# Training arguments
print("\n7. Configuring training...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
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
    bf16=True,
    tf32=True,
    max_grad_norm=0.3,
    group_by_length=True,
    report_to="none",
    push_to_hub=True,
    hub_model_id=HUB_MODEL_ID,
)

# Data collator
print("\n8. Creating data collator...")
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# Tokenize the data
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=2048, padding="max_length")

print("   Tokenizing datasets...")
train_dataset = train_dataset.map(tokenize_function, remove_columns=["text", "messages"])
if eval_dataset != train_dataset:
    eval_dataset = eval_dataset.map(tokenize_function, remove_columns=["text", "messages"])

# Initialize trainer
print("\n9. Initializing trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset if eval_dataset != train_dataset else None,
    data_collator=data_collator,
)

# Train
print("\n" + "="*60)
print("Starting training...")
print("="*60 + "\n")

trainer.train()

print("\n" + "="*60)
print("Training complete!")
print("="*60)

# Save
print("\nSaving adapter...")
trainer.model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\nPushing to HuggingFace Hub...")
trainer.push_to_hub()

print("\n" + "="*60)
print("SUCCESS! Adapter available at:")
print(f"https://huggingface.co/{HUB_MODEL_ID}")
print("="*60)
