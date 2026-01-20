"""
Prepare training data for Hugging Face AutoTrain
Converts our JSONL format to AutoTrain's expected CSV format
"""

import json
import pandas as pd
from pathlib import Path

def load_jsonl(file_path):
    """Load JSONL file"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def messages_to_text(messages):
    """Convert messages array to formatted text"""
    text_parts = []
    for msg in messages:
        role = msg['role']
        content = msg['content']
        text_parts.append(f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}")
    return "<|begin_of_text|>" + "<|eot_id|>".join(text_parts) + "<|eot_id|>"

def prepare_data():
    """Prepare training and eval data for AutoTrain"""

    # Load JSONL files
    print("Loading training data...")
    train_data = load_jsonl('data/training/kwanzaa_train.jsonl')
    eval_data = load_jsonl('data/training/kwanzaa_eval.jsonl')

    print(f"Loaded {len(train_data)} training samples")
    print(f"Loaded {len(eval_data)} eval samples")

    # Convert to text format
    print("\nConverting to AutoTrain format...")
    train_texts = [{"text": messages_to_text(item['messages'])} for item in train_data]
    eval_texts = [{"text": messages_to_text(item['messages'])} for item in eval_data]

    # Create DataFrames
    train_df = pd.DataFrame(train_texts)
    eval_df = pd.DataFrame(eval_texts)

    # Create output directory
    output_dir = Path('data/training/autotrain')
    output_dir.mkdir(exist_ok=True)

    # Save as CSV
    train_path = output_dir / 'train.csv'
    eval_path = output_dir / 'eval.csv'

    train_df.to_csv(train_path, index=False)
    eval_df.to_csv(eval_path, index=False)

    print(f"\nSaved train data to: {train_path}")
    print(f"Saved eval data to: {eval_path}")
    print(f"\nSample text format:")
    print(train_texts[0]['text'][:500])
    print("\n✅ Data preparation complete!")

if __name__ == '__main__':
    prepare_data()
