# RunPod Training - Manual Steps

**Pod Created Successfully!** ✅
- **Pod ID:** m8iue5exvrpa51
- **GPU:** 1x RTX 4090
- **Cost:** $0.340/hr
- **Status:** RUNNING

---

## Quick Start (Web Terminal Method)

### 1. Access Your Pod
Go to: https://www.runpod.io/console/pods

Click on pod **kwanzaa-training-1768890426** and select "Connect" → "Start Web Terminal" or "Start Jupyter Lab"

### 2. In the Pod Terminal, Run These Commands:

```bash
# Install dependencies
pip install transformers==4.36.0 datasets peft bitsandbytes accelerate torch trl pyyaml

# Create directory structure
mkdir -p /workspace/backend/training/config
mkdir -p /workspace/data/training

# Download training data (using curl to transfer from your local machine)
# Option A: If you have the files on GitHub
cd /workspace
git clone https://github.com/YOUR_REPO/kwanzaa.git
cd kwanzaa

# Option B: Direct upload via Jupyter
# 1. Click "Upload" in Jupyter
# 2. Upload these files:
#    - kwanzaa_train.jsonl
#    - kwanzaa_eval.jsonl
#    - train_adapter.py
#    - training.yaml

# Option C: Use base64 transfer (most reliable)
# On your local machine, run:
#   base64 -i data/training/kwanzaa_train.jsonl
# Copy the output, then in pod terminal:
echo "PASTE_BASE64_HERE" | base64 -d > /workspace/data/training/kwanzaa_train.jsonl

# Do the same for kwanzaa_eval.jsonl
```

### 3. Create Training Script on Pod

Create `/workspace/train.py`:

```python
#!/usr/bin/env python3
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset
import torch

# Config
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"  # or "allenai/OLMo-7B-Instruct"
OUTPUT_DIR = "/workspace/outputs/kwanzaa-adapter-v0"

# Load model with 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# Load data
dataset = load_dataset("json", data_files={
    "train": "/workspace/data/training/kwanzaa_train.jsonl",
    "eval": "/workspace/data/training/kwanzaa_eval.jsonl",
})

# Training args
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=4,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=7,
    eval_steps=7,
    save_steps=7,
    save_total_limit=3,
    evaluation_strategy="steps",
    load_best_model_at_end=True,
)

# Trainer
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["eval"],
    dataset_text_field="messages",
    max_seq_length=2048,
)

print("[INFO] Starting training...")
trainer.train()

print("[SUCCESS] Training complete!")
trainer.save_model(OUTPUT_DIR)
print(f"[INFO] Adapter saved to: {OUTPUT_DIR}")
```

### 4. Run Training

```bash
cd /workspace
python train.py
```

**Expected time:** ~15-20 minutes
**Output:** `/workspace/outputs/kwanzaa-adapter-v0/`

### 5. Download Adapter

After training completes, in Jupyter Lab:
- Navigate to `/workspace/outputs/kwanzaa-adapter-v0/`
- Select all files
- Right-click → Download

Or use runpodctl receive (from your local machine):
```bash
# In pod terminal:
/Users/aideveloper/.local/bin/runpodctl send /workspace/outputs/kwanzaa-adapter-v0

# Then on your local machine:
mkdir -p outputs/kwanzaa-adapter-v0
cd outputs/kwanzaa-adapter-v0
runpodctl receive
# Enter the code shown in pod terminal
```

### 6. Terminate Pod

```bash
/Users/aideveloper/.local/bin/runpodctl stop pod m8iue5exvrpa51
```

---

## Alternative: Base64 File Transfer

### Upload Training Files:

```bash
# On local machine:
cd /Users/aideveloper/kwanzaa

# Encode train data
base64 -i data/training/kwanzaa_train.jsonl | pbcopy

# In pod terminal:
cat > /workspace/data/training/kwanzaa_train.jsonl << 'EOF'
# Paste the base64 output here
EOF
base64 -d -i /workspace/data/training/kwanzaa_train.jsonl.b64 > /workspace/data/training/kwanzaa_train.jsonl

# Repeat for eval data and training script
```

---

## Monitoring Training

While training runs, you can monitor:

```bash
# Watch GPU usage
nvidia-smi -l 1

# Watch training logs
tail -f /workspace/outputs/kwanzaa-adapter-v0/trainer_state.json

# Check progress
ls -lh /workspace/outputs/kwanzaa-adapter-v0/
```

---

## Expected Output Files

After training:
```
/workspace/outputs/kwanzaa-adapter-v0/
├── adapter_config.json
├── adapter_model.safetensors  (8-15MB)
├── training_args.bin
├── trainer_state.json
├── checkpoint-*/
└── runs/  (tensorboard logs)
```

---

## Cost Tracking

- Current rate: $0.340/hr
- Training time: ~20 min = ~$0.11
- Total with setup: ~30 min = ~$0.17

**Remember to terminate the pod after downloading!**

---

## Next Steps After Training

1. Validate adapter files downloaded
2. Issue #52: Save & Version Adapter
3. Issue #54: Load Into Inference Pipeline
4. Issues #56-60: Run Evaluations

---

**Pod Status:** https://www.runpod.io/console/pods
**Pod ID:** m8iue5exvrpa51
**GPU:** RTX 4090
**Status:** RUNNING ✅
