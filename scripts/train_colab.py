"""
Kwanzaa Adapter Training on Google Colab (Free T4 GPU)
======================================================

Instructions:
1. Open this in Google Colab: https://colab.research.google.com
2. Runtime > Change runtime type > T4 GPU
3. Upload kwanzaa_train.jsonl and kwanzaa_eval.jsonl to /content/
4. Run all cells
5. Download the adapter from /content/outputs/

Training Configuration:
- Model: meta-llama/Llama-3.2-1B-Instruct
- Method: QLoRA (4-bit quantization)
- Training samples: 107
- Eval samples: 27
- Estimated time: 15-20 minutes on free T4
"""

# ============================================================================
# CELL 1: Install Dependencies
# ============================================================================
"""
!pip install -q -U \
    transformers \
    datasets \
    peft \
    bitsandbytes \
    trl \
    accelerate \
    huggingface_hub

# Accept Llama 3.2 license at: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
# Then login with your token
from huggingface_hub import notebook_login
notebook_login()
"""

# ============================================================================
# CELL 2: Load and Prepare Data
# ============================================================================
"""
import json
from datasets import Dataset

# Load JSONL files
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

# Load training and eval data
train_data = load_jsonl('/content/kwanzaa_train.jsonl')
eval_data = load_jsonl('/content/kwanzaa_eval.jsonl')

# Convert to HF Dataset
train_dataset = Dataset.from_list(train_data)
eval_dataset = Dataset.from_list(eval_data)

print(f"Training samples: {len(train_dataset)}")
print(f"Eval samples: {len(eval_dataset)}")
print(f"\\nSample format:")
print(train_dataset[0])
"""

# ============================================================================
# CELL 3: Configure Model and Tokenizer
# ============================================================================
"""
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM

# Model configuration
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
OUTPUT_DIR = "/content/outputs/kwanzaa-adapter-v1"

# 4-bit quantization config for free T4 GPU
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load model and tokenizer
print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Prepare model for k-bit training
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Apply LoRA
model = get_peft_model(model, lora_config)
print(f"\\nTrainable parameters: {model.print_trainable_parameters()}")
"""

# ============================================================================
# CELL 4: Prepare Chat Template
# ============================================================================
"""
# Format messages for chat template
def format_chat_template(example):
    messages = example["messages"]
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": text}

# Apply chat template
train_dataset = train_dataset.map(format_chat_template)
eval_dataset = eval_dataset.map(format_chat_template)

print("Sample formatted text:")
print(train_dataset[0]["text"][:500])
"""

# ============================================================================
# CELL 5: Training Configuration
# ============================================================================
"""
# Training arguments optimized for free Colab T4
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
    bf16=True,
    tf32=True,
    max_grad_norm=0.3,
    group_by_length=True,
    report_to="none",
    push_to_hub=False,
)

# Data collator for completion-only training
# Only train on assistant responses, not the full conversation
response_template = "<|start_header_id|>assistant<|end_header_id|>"
collator = DataCollatorForCompletionOnlyLM(
    response_template=response_template,
    tokenizer=tokenizer,
)
"""

# ============================================================================
# CELL 6: Initialize Trainer and Train
# ============================================================================
"""
# Initialize trainer
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=collator,
    dataset_text_field="text",
    max_seq_length=2048,
    packing=False,
)

# Start training!
print("\\n" + "="*50)
print("Starting training...")
print("="*50 + "\\n")

trainer.train()

print("\\n" + "="*50)
print("Training complete!")
print("="*50)
"""

# ============================================================================
# CELL 7: Save and Download Adapter
# ============================================================================
"""
# Save the adapter
print("\\nSaving adapter...")
trainer.model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\\nAdapter saved to: {OUTPUT_DIR}")
print("\\nFiles created:")
!ls -lh {OUTPUT_DIR}

print("\\n" + "="*50)
print("TRAINING COMPLETE!")
print("="*50)
print(f"\\nDownload the adapter files from: {OUTPUT_DIR}")
print("\\nYou can now:")
print("1. Download the adapter folder manually from Colab Files")
print("2. Or push to Hugging Face Hub (optional)")
print("\\nAdapter files to download:")
print("  - adapter_config.json")
print("  - adapter_model.safetensors")
print("  - tokenizer files")
"""

# ============================================================================
# CELL 8: (Optional) Push to Hugging Face Hub
# ============================================================================
"""
# Uncomment to push to your HF account
# HF_REPO_NAME = "your-username/kwanzaa-adapter-v1"
#
# trainer.model.push_to_hub(HF_REPO_NAME)
# tokenizer.push_to_hub(HF_REPO_NAME)
#
# print(f"Adapter pushed to: https://huggingface.co/{HF_REPO_NAME}")
"""

# ============================================================================
# CELL 9: Test the Adapter
# ============================================================================
"""
# Test inference with the trained adapter
from transformers import pipeline

# Create pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
    temperature=0.7,
)

# Test message
test_messages = [
    {
        "role": "system",
        "content": "You are a researcher assistant specializing in Kwanzaa and African American culture."
    },
    {
        "role": "user",
        "content": '''Retrieved Documents:

[1] Title: "Kwanzaa Principles"
Content: "The seven principles of Kwanzaa are called Nguzo Saba..."

Query: What are the seven principles of Kwanzaa?'''
    }
]

print("\\nTesting adapter:")
print("="*50)
result = pipe(test_messages)
print(result[0]['generated_text'][-1]['content'])
"""
