#!/usr/bin/env python3
"""
Simple test script for adapter v3 to verify it loads and works
"""
import sys
sys.path.insert(0, 'backend')

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

print("="*60)
print("Testing Adapter v3")
print("="*60)

# Load base model and adapter separately (avoids offloading issues)
print("\n1. Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-1B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="cpu",  # Load to CPU to avoid offloading issues
    low_cpu_mem_usage=True
)

print("\n2. Loading adapter v3...")
adapter_path = "models/adapters/kwanzaa-adapter-v3"
model = PeftModel.from_pretrained(
    base_model,
    adapter_path
)

print("\n3. Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(adapter_path)

# Test with a simple educator question
print("\n4. Testing inference with educator question...")
test_question = "When was the Emancipation Proclamation signed, and what did it declare?"

messages = [
    {"role": "system", "content": "You are a knowledgeable educator providing accurate historical information. Always cite your sources using [1], [2], etc."},
    {"role": "user", "content": test_question}
]

inputs = tokenizer.apply_chat_template(
    messages,
    return_tensors="pt",
    add_generation_prompt=True
)

with torch.no_grad():
    outputs = model.generate(
        inputs,
        max_new_tokens=256,
        do_sample=False,
        temperature=None,
        top_p=None,
    )

response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

print("\nQuestion:", test_question)
print("\nResponse:", response)

# Check for citations
import re
citation_pattern = r'\[(\d+)\]'
citations_found = re.findall(citation_pattern, response)

print("\n" + "="*60)
if citations_found:
    print(f"✅ SUCCESS! Found {len(citations_found)} citation(s): {citations_found}")
else:
    print("❌ WARNING: No citations found in response")
print("="*60)
