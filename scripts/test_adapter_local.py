#!/usr/bin/env python3
"""
Test the trained Kwanzaa adapter locally
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

print("="*60)
print("Testing Kwanzaa Adapter Locally")
print("="*60)

# Configuration
BASE_MODEL = "meta-llama/Llama-3.2-1B-Instruct"
ADAPTER_PATH = "backend/models/adapters/kwanzaa-adapter-v1"

print("\n1. Loading base model with 4-bit quantization...")
print(f"   Base model: {BASE_MODEL}")

# 4-bit quantization config (same as training)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

print("   ✓ Base model loaded")

print("\n2. Loading trained adapter...")
print(f"   Adapter path: {ADAPTER_PATH}")

# Load adapter
model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_PATH,
    device_map="auto",
)

print("   ✓ Adapter loaded")

print("\n3. Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
tokenizer.pad_token = tokenizer.eos_token

print("   ✓ Tokenizer loaded")

# Test queries
test_queries = [
    {
        "system": "You are a researcher assistant specializing in Kwanzaa and African American culture.",
        "query": "What are the seven principles of Kwanzaa?",
        "context": """Retrieved Documents:

[1] Title: "Kwanzaa Principles"
Content: "The seven principles of Kwanzaa are called Nguzo Saba..."

Query: What are the seven principles of Kwanzaa?"""
    },
    {
        "system": "You are a researcher assistant specializing in Kwanzaa and African American culture.",
        "query": "Who created Kwanzaa?",
        "context": """Retrieved Documents:

[1] Title: "History of Kwanzaa"
Content: "Kwanzaa was created by Dr. Maulana Karenga in 1966..."

Query: Who created Kwanzaa?"""
    }
]

print("\n" + "="*60)
print("Running Test Queries")
print("="*60)

for i, test in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}: {test['query']}")
    print(f"{'='*60}")

    messages = [
        {"role": "system", "content": test["system"]},
        {"role": "user", "content": test["context"]}
    ]

    # Format with chat template
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    # Tokenize
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    print("\nGenerating response...")

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

    print("\nResponse:")
    print("-" * 60)
    print(response)
    print("-" * 60)

print("\n" + "="*60)
print("Testing Complete!")
print("="*60)
print("\nThe adapter is working if you see:")
print("  ✓ Relevant, coherent responses")
print("  ✓ Citations or references to source documents")
print("  ✓ Knowledge about Kwanzaa principles and history")
print("\n" + "="*60)
