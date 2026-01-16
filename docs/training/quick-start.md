# Adapter Training Quick Start

Get started training your first QLoRA adapter in 5 minutes.

## Prerequisites

- NVIDIA GPU with 24GB+ VRAM (RTX 3090, A100, etc.)
- Python 3.10+
- CUDA 11.8+

## Quick Setup

### 1. Install Dependencies

```bash
# From project root
pip install -r backend/training/requirements.txt
```

### 2. Prepare Training Data

Create your training datasets in JSONL format:

**data/training/kwanzaa_train.jsonl**:
```json
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Question?"}, {"role": "assistant", "content": "Answer with citation [1]."}]}
```

**data/training/kwanzaa_eval.jsonl**:
```json
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Test question?"}, {"role": "assistant", "content": "Test answer."}]}
```

### 3. Run Training

```bash
python backend/training/train_adapter.py
```

That's it! Training will start with default configuration.

## What Happens During Training

1. Loads AI2 OLMo-7B-Instruct base model (auto-downloads from Hugging Face)
2. Applies 4-bit quantization to reduce VRAM usage
3. Adds LoRA adapter layers (only ~42M trainable parameters)
4. Trains for 2 epochs with learning rate 2e-4
5. Saves adapter to `outputs/kwanzaa-adapter-v0/`

## Expected Output

```
Loading base model: allenai/OLMo-7B-Instruct
Trainable parameters: 41,943,040 / 7,015,612,416 (0.60%)
Starting training...
Step 10/1000 (1.0%) | Loss: 2.3456 | LR: 1.94e-04
...
Training completed in 3600.00 seconds
SUCCESS: Base model weights remain unchanged
Final artifact: outputs/kwanzaa-adapter-v0/final_artifact
```

## Using Your Trained Adapter

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base + adapter
base = AutoModelForCausalLM.from_pretrained(
    "allenai/OLMo-7B-Instruct",
    device_map="auto"
)
model = PeftModel.from_pretrained(
    base,
    "outputs/kwanzaa-adapter-v0/final_artifact"
)

# Generate
tokenizer = AutoTokenizer.from_pretrained("allenai/OLMo-7B-Instruct")
inputs = tokenizer("Your question here", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=800, temperature=0.2)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Customization

### Change Hyperparameters

Edit `backend/training/config/training.yaml`:

```yaml
training:
  num_train_epochs: 3        # More epochs
  learning_rate: 0.0001      # Lower learning rate
```

### Custom Output Directory

```bash
python backend/training/train_adapter.py --output-dir outputs/my-adapter-v1
```

### Monitor with TensorBoard

```bash
tensorboard --logdir outputs/kwanzaa-adapter-v0/tensorboard
```

## Troubleshooting

### Out of Memory

Reduce batch size in config:
```yaml
training:
  gradient_accumulation_steps: 8  # Reduce from 16
```

### Dataset Not Found

Ensure datasets exist:
```bash
ls -lh data/training/
# Should show kwanzaa_train.jsonl and kwanzaa_eval.jsonl
```

### Slow Download

Base model downloads ~14GB on first run. Be patient or use Hugging Face cache:
```bash
export HF_HOME=/path/to/large/cache
```

## Next Steps

1. **Full Documentation**: See `docs/training/adapter-training-guide.md`
2. **Advanced Config**: Explore `backend/training/config/training.yaml`
3. **Integration**: Add adapter to Kwanzaa backend
4. **Evaluation**: Test adapter on held-out dataset

## Get Help

- Documentation: `docs/training/adapter-training-guide.md`
- Troubleshooting: See guide Section 9
- Tests: `pytest backend/tests/test_training_utils.py -v`
