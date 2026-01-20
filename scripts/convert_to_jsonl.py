#!/usr/bin/env python3
"""
Convert training examples from JSON to JSONL format for model training.

The training script expects JSONL format with messages in this structure:
{
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
"""

import json
import random
from pathlib import Path
from typing import Dict, List


def create_system_prompt(persona: str, toggles: Dict) -> str:
    """Create system prompt based on persona and toggles."""

    persona_descriptions = {
        "educator": "You are an educator helping people learn about Kwanzaa, African American history, and cultural traditions. Use clear, accessible language and maintain an educational tone.",
        "researcher": "You are a researcher providing scholarly analysis of Kwanzaa, African American history, and cultural topics. Use formal, academic language with proper citations.",
        "creator": "You are a creative guide helping people explore Kwanzaa and Black cultural traditions. Use conversational, engaging language that celebrates creativity and cultural expression.",
        "builder": "You are a technical guide helping people implement and build around Kwanzaa principles and cultural practices. Use practical, implementation-focused language."
    }

    base_prompt = persona_descriptions.get(persona, persona_descriptions["educator"])

    guidelines = []

    if toggles.get("require_citations", True):
        guidelines.append("Always cite sources using bracket notation [1][2] when information comes from retrieved documents.")

    if toggles.get("primary_sources_only", False):
        guidelines.append("Prioritize primary sources over secondary sources when available.")

    if not toggles.get("creative_mode", False):
        guidelines.append("Stay grounded in the retrieved context and avoid speculation.")

    guidelines.append("When you cannot answer a question due to lack of sources, acknowledge this clearly and suggest alternatives.")
    guidelines.append("Maintain cultural sensitivity and celebrate Black creativity, innovation, and self-determination.")
    guidelines.append("Always respond with valid JSON following the answer_json contract.")

    full_prompt = base_prompt + "\n\nGuidelines:\n" + "\n".join(f"- {g}" for g in guidelines)

    return full_prompt


def create_user_prompt(query: str, retrieved_context: List[Dict]) -> str:
    """Create user prompt with query and retrieved context."""

    if not retrieved_context:
        return f"Query: {query}\n\nNo relevant documents were retrieved from the corpus."

    context_text = "Retrieved Documents:\n\n"

    for ctx in retrieved_context:
        rank = ctx['rank']
        score = ctx['score']
        content = ctx['content']
        metadata = ctx['metadata']

        context_text += f"[{rank}] {metadata['citation_label']}\n"
        context_text += f"Relevance Score: {score:.2f}\n"
        context_text += f"Source: {metadata['source_org']} ({metadata['year']})\n"
        context_text += f"Content: {content}\n"
        context_text += f"URL: {metadata['canonical_url']}\n\n"

    full_prompt = f"{context_text}Query: {query}\n\nProvide your response as valid JSON following the answer_json contract."

    return full_prompt


def create_assistant_response(expected_output: Dict) -> str:
    """Create assistant response as JSON string."""
    # Return the expected_output as a formatted JSON string
    return json.dumps(expected_output, indent=2, ensure_ascii=False)


def convert_sample_to_messages(sample: Dict) -> Dict:
    """Convert a training sample to messages format."""

    persona = sample['persona']
    toggles = sample['expected_output'].get('toggles', {})
    query = sample['user_query']
    retrieved_context = sample.get('retrieved_context', [])
    expected_output = sample['expected_output']

    messages = [
        {
            "role": "system",
            "content": create_system_prompt(persona, toggles)
        },
        {
            "role": "user",
            "content": create_user_prompt(query, retrieved_context)
        },
        {
            "role": "assistant",
            "content": create_assistant_response(expected_output)
        }
    ]

    return {"messages": messages}


def convert_all_examples_to_jsonl(examples_dir: Path, output_dir: Path, train_split: float = 0.8):
    """Convert all JSON examples to JSONL format and split into train/eval sets."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all samples
    all_samples = []

    for json_file in examples_dir.glob('*-examples.json'):
        print(f"Loading {json_file.name}...")
        with open(json_file, 'r') as f:
            data = json.load(f)
            samples = data.get('samples', [])
            all_samples.extend(samples)

    print(f"\nTotal samples loaded: {len(all_samples)}")

    # Shuffle for random split
    random.seed(42)  # Reproducible split
    random.shuffle(all_samples)

    # Split into train and eval
    split_index = int(len(all_samples) * train_split)
    train_samples = all_samples[:split_index]
    eval_samples = all_samples[split_index:]

    print(f"Train samples: {len(train_samples)}")
    print(f"Eval samples: {len(eval_samples)}")

    # Convert and save training set
    train_file = output_dir / "kwanzaa_train.jsonl"
    print(f"\nConverting training samples to {train_file}...")

    with open(train_file, 'w') as f:
        for sample in train_samples:
            messages_obj = convert_sample_to_messages(sample)
            f.write(json.dumps(messages_obj, ensure_ascii=False) + '\n')

    print(f"✓ Saved {len(train_samples)} training samples")

    # Convert and save evaluation set
    eval_file = output_dir / "kwanzaa_eval.jsonl"
    print(f"\nConverting evaluation samples to {eval_file}...")

    with open(eval_file, 'w') as f:
        for sample in eval_samples:
            messages_obj = convert_sample_to_messages(sample)
            f.write(json.dumps(messages_obj, ensure_ascii=False) + '\n')

    print(f"✓ Saved {len(eval_samples)} evaluation samples")

    # Print statistics
    print("\n" + "=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)

    # Category distribution in training set
    train_categories = {}
    for sample in train_samples:
        cat = sample['category']
        train_categories[cat] = train_categories.get(cat, 0) + 1

    print("\nTraining Set Distribution:")
    for cat, count in sorted(train_categories.items()):
        percentage = (count / len(train_samples)) * 100
        print(f"  {cat}: {count} ({percentage:.1f}%)")

    # Category distribution in eval set
    eval_categories = {}
    for sample in eval_samples:
        cat = sample['category']
        eval_categories[cat] = eval_categories.get(cat, 0) + 1

    print("\nEvaluation Set Distribution:")
    for cat, count in sorted(eval_categories.items()):
        percentage = (count / len(eval_samples)) * 100
        print(f"  {cat}: {count} ({percentage:.1f}%)")

    # Persona distribution
    train_personas = {}
    for sample in train_samples:
        persona = sample['persona']
        train_personas[persona] = train_personas.get(persona, 0) + 1

    print("\nTraining Set Personas:")
    for persona, count in sorted(train_personas.items()):
        percentage = (count / len(train_samples)) * 100
        print(f"  {persona}: {count} ({percentage:.1f}%)")

    print("\n" + "=" * 80)
    print("Files created:")
    print(f"  {train_file}")
    print(f"  {eval_file}")
    print("=" * 80)

    return train_file, eval_file


def validate_jsonl_format(jsonl_file: Path, sample_count: int = 3):
    """Validate JSONL format and show sample entries."""

    print(f"\n{'=' * 80}")
    print(f"VALIDATING: {jsonl_file.name}")
    print('=' * 80)

    with open(jsonl_file, 'r') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")

    # Validate each line is valid JSON
    valid_count = 0
    for i, line in enumerate(lines, 1):
        try:
            obj = json.loads(line)
            assert 'messages' in obj, f"Line {i}: Missing 'messages' field"
            assert isinstance(obj['messages'], list), f"Line {i}: 'messages' must be a list"
            assert len(obj['messages']) == 3, f"Line {i}: Expected 3 messages (system, user, assistant)"

            for msg in obj['messages']:
                assert 'role' in msg, f"Line {i}: Message missing 'role'"
                assert 'content' in msg, f"Line {i}: Message missing 'content'"

            valid_count += 1
        except Exception as e:
            print(f"ERROR on line {i}: {e}")
            return False

    print(f"✓ All {valid_count} lines are valid")

    # Show samples
    print(f"\nShowing first {sample_count} samples:\n")

    for i in range(min(sample_count, len(lines))):
        obj = json.loads(lines[i])
        messages = obj['messages']

        print(f"{'=' * 80}")
        print(f"SAMPLE {i + 1}")
        print('=' * 80)

        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']

            if role == "ASSISTANT":
                # Parse JSON content to show structure
                try:
                    assistant_json = json.loads(content)
                    query_preview = assistant_json.get('retrieval_summary', {}).get('query', 'N/A')
                    answer_preview = assistant_json.get('answer', {}).get('text', '')[:150]
                    print(f"\n{role}:")
                    print(f"  Query: {query_preview}")
                    print(f"  Answer Preview: {answer_preview}...")
                    print(f"  Sources: {len(assistant_json.get('sources', []))}")
                except:
                    print(f"\n{role}:")
                    print(f"  {content[:200]}...")
            else:
                print(f"\n{role}:")
                print(f"  {content[:200]}...")

        print()

    return True


def main():
    """Main entry point."""

    # Paths
    project_root = Path(__file__).parent.parent
    examples_dir = project_root / "data" / "training" / "examples"
    output_dir = project_root / "data" / "training"

    print("=" * 80)
    print("TRAINING DATA CONVERSION: JSON to JSONL")
    print("=" * 80)

    # Convert
    train_file, eval_file = convert_all_examples_to_jsonl(
        examples_dir=examples_dir,
        output_dir=output_dir,
        train_split=0.8
    )

    # Validate
    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    train_valid = validate_jsonl_format(train_file, sample_count=2)
    eval_valid = validate_jsonl_format(eval_file, sample_count=1)

    if train_valid and eval_valid:
        print("\n" + "=" * 80)
        print("✓ SUCCESS! All files are valid and ready for training")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Review the generated files:")
        print(f"     - {train_file}")
        print(f"     - {eval_file}")
        print("  2. Run training:")
        print("     python backend/training/train_adapter.py")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("✗ VALIDATION FAILED - Please check errors above")
        print("=" * 80)


if __name__ == "__main__":
    main()
