#!/usr/bin/env python3
"""
Simple adapter test - no 4-bit quantization (uses more RAM but easier to run)
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

print("Loading model and adapter...")

# Load base model (without quantization for simplicity)
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-1B-Instruct",
    device_map="auto",
)

# Load adapter
model = PeftModel.from_pretrained(
    base_model,
    "backend/models/adapters/kwanzaa-adapter-v1"
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    "backend/models/adapters/kwanzaa-adapter-v1"
)

print("✓ Model ready!\n")

# Simple test
messages = [
    {"role": "system", "content": "You are a Kwanzaa expert."},
    {"role": "user", "content": "What are the seven principles of Kwanzaa?"}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)

print("Generating response...\n")
outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.7)
response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

print("Response:")
print("=" * 60)
print(response)
print("=" * 60)
