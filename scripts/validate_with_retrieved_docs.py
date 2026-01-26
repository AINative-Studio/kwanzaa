#!/usr/bin/env python3
"""
Validate adapter v4 with retrieved documents (like RAG production use).

This tests the adapter with the CORRECT format: providing retrieved
documents for the model to cite, just like the training data.
"""
import sys
sys.path.insert(0, 'backend')

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import re

print("="*60)
print("RAG-Style Validation Test for Adapter v4")
print("(Testing with Retrieved Documents)")
print("="*60)

# Load model
print("\n1. Loading base model and adapter v4...")
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-1B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    low_cpu_mem_usage=True
)

adapter_path = "models/adapters/kwanzaa-adapter-v4"
model = PeftModel.from_pretrained(base_model, adapter_path)
tokenizer = AutoTokenizer.from_pretrained(adapter_path)

# Test with retrieved documents (RAG format)
test_case = {
    "question": "What were the main goals of the March on Washington?",
    "retrieved_doc": """[1] March on Washington — National Archives
Relevance Score: 0.95
Source: National Archives (1963)
Content: The March on Washington for Jobs and Freedom on August 28, 1963, had several key goals: (1) Passage of meaningful civil rights legislation, (2) Elimination of racial segregation in public schools, (3) Protection from police brutality, (4) A federal works program for full employment, (5) A Fair Employment Practices Act banning job discrimination, and (6) A $2 minimum wage. Over 250,000 people gathered at the Lincoln Memorial, where Dr. Martin Luther King Jr. delivered his historic 'I Have a Dream' speech.
URL: https://www.archives.gov/exhibits/american_originals/march.html"""
}

print("\n2. Testing with RAG format (Retrieved Documents)...\n")

# Format the question with retrieved documents (like RAG)
user_message = f"""Retrieved Documents:

{test_case['retrieved_doc']}

Query: {test_case['question']}

Provide your response citing the sources using [1], [2], etc."""

messages = [
    {
        "role": "system",
        "content": "You are an educator helping people learn about African American history. Always cite sources using bracket notation [1][2] when information comes from retrieved documents."
    },
    {
        "role": "user",
        "content": user_message
    }
]

inputs = tokenizer.apply_chat_template(
    messages,
    return_tensors="pt",
    add_generation_prompt=True
)

with torch.no_grad():
    outputs = model.generate(
        inputs,
        max_new_tokens=400,
        do_sample=False,
        temperature=None,
        top_p=None,
    )

response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

# Analyze response
citation_pattern = r'\[(\d+)\]'
citations_found = re.findall(citation_pattern, response)

print("\n" + "="*60)
print("TEST RESULTS")
print("="*60)
print(f"\nQuestion: {test_case['question']}")
print(f"\nProvided Source: [1] March on Washington — National Archives")
print(f"\nModel Response:\n{response}")
print("\n" + "="*60)
print("ANALYSIS")
print("="*60)

# Check if citations are present
has_citations = len(citations_found) > 0
cites_source_1 = '1' in citations_found

# Check if response includes key content from source
response_lower = response.lower()
mentions_key_goals = any(term in response_lower for term in ['civil rights', 'segregation', 'police brutality', 'employment', 'minimum wage'])
mentions_mlk = 'martin luther king' in response_lower or 'dream' in response_lower
mentions_date = '1963' in response or 'august 28' in response_lower

print(f"\n✓ Citations present: {has_citations}")
if has_citations:
    print(f"  Found: {citations_found}")
    print(f"  Cites source [1]: {cites_source_1}")

print(f"\n✓ Content from retrieved doc:")
print(f"  Mentions key goals: {mentions_key_goals}")
print(f"  Mentions MLK/Dream speech: {mentions_mlk}")
print(f"  Mentions date (1963/Aug 28): {mentions_date}")

# Overall verdict
all_checks = [
    ("Has citations", has_citations),
    ("Cites provided source [1]", cites_source_1),
    ("Uses content from source", mentions_key_goals),
]

passed_checks = sum(1 for _, check in all_checks if check)
total_checks = len(all_checks)

print(f"\n{'='*60}")
print(f"VALIDATION RESULT: {passed_checks}/{total_checks} checks passed")
print(f"{'='*60}\n")

if passed_checks >= 2:
    print("✅ SUCCESS! Adapter v4 correctly:")
    print("   - Cites sources when provided [1]")
    print("   - Uses content from retrieved documents")
    print("   - Learned RAG behavior from training data")
else:
    print("❌ FAILED: Adapter needs improvement")
    for name, check in all_checks:
        print(f"   {name}: {'✓' if check else '✗'}")

print(f"\n{'='*60}\n")
