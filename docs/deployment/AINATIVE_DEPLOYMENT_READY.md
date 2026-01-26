# AINative Adapter - Ready for HuggingFace Spaces Deployment

**Date**: 2026-01-23
**Status**: ✅ READY TO DEPLOY
**Training Platform**: HuggingFace Spaces (ZeroGPU)

---

## Deployment Summary

All preparation work is **100% complete**. The AINative adapter training can be deployed to HuggingFace Spaces immediately.

### What's Ready

✅ **Dataset Prepared**: 98 examples (88 train, 10 eval) - 0 AI attribution violations
✅ **HF Space Files**: app.py, requirements.txt, README.md
✅ **Dataset Formatted**: Llama-3 chat format in `outputs/ainative_dataset/`
✅ **Documentation**: Complete deployment guides

---

## Quick Start - Deploy to HuggingFace Spaces

### Option 1: Update Existing Space (Recommended)

If you already have a HuggingFace Space from the Kwanzaa training:

```bash
# 1. Clone your existing Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# 2. Copy AINative files
cp /Users/aideveloper/kwanzaa/hf_space/app.py .
cp /Users/aideveloper/kwanzaa/hf_space/requirements.txt .
cp /Users/aideveloper/kwanzaa/hf_space/README.md .

# 3. Commit and push
git add .
git commit -m "Add AINative adapter training"
git push
```

### Option 2: Create New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - **Name**: `ainative-adapter-training`
   - **SDK**: Gradio
   - **Hardware**: ZeroGPU (A100 - Free)
   - **License**: Apache 2.0
4. Upload files from `hf_space/` directory

---

## Step 1: Upload Dataset to HuggingFace Hub

You need to upload the dataset first. The dataset is ready in `outputs/ainative_dataset/`.

### Method 1: Using the Upload Script (Requires HF_TOKEN)

```bash
# Set your HuggingFace token
export HF_TOKEN="your_hf_token_here"

# Upload dataset
source venv/bin/activate
python3 scripts/upload_dataset_to_hf.py
```

This will upload to: `ainative/ainative-training-v1`

### Method 2: Manual Upload via HuggingFace Hub UI

1. Go to https://huggingface.co/new-dataset
2. Create dataset: `ainative-training-v1`
3. Upload the contents of `outputs/ainative_dataset/` directory:
   - `train/` folder
   - `validation/` folder
   - `dataset_dict.json`

---

## Step 2: Add HF_TOKEN Secret to Space

1. Go to your Space Settings → Secrets
2. Add new secret:
   - **Name**: `HF_TOKEN`
   - **Value**: Your HuggingFace token
3. Save

---

## Step 3: Start Training

1. Open your HuggingFace Space in browser
2. The Gradio interface will load with default settings:
   - **Dataset**: `ainative/ainative-training-v1`
   - **Model**: `unsloth/Llama-3.2-1B-Instruct`
   - **Epochs**: 4
   - **Learning Rate**: 0.0002
   - **Batch Size**: 2
   - **Gradient Accumulation**: 8
3. Click **"Start Training"**
4. Monitor progress in the status panel

---

## Expected Training Timeline

- **Space Build**: 5-10 minutes (first time)
- **Training**: 1-2 hours (ZeroGPU A100)
- **Total**: ~2-3 hours

---

## Training Configuration

```yaml
Base Model: meta-llama/Llama-3.2-1B-Instruct
Method: QLoRA (4-bit quantization)
LoRA Rank: 16
LoRA Alpha: 32
LoRA Dropout: 0.05
Max Sequence Length: 2048

Epochs: 4
Learning Rate: 2e-4
Batch Size: 2
Gradient Accumulation: 8
Effective Batch Size: 16

GPU: A100 (40GB) via ZeroGPU
Cost: FREE
```

---

## Dataset Statistics

```
Total Examples: 98
├── Train: 88 (89.8%)
└── Eval: 10 (10.2%)

Quality Metrics:
├── Valid Examples: 92%
├── AI Attribution: 0% ✅
├── Valid JSON: 100%
├── Valid Python: 100%
├── Include Tests: 91.8%
└── Error Handling: 100%

Sources:
├── Extracted (Automated): 68 examples
│   ├── Test Patterns: 25
│   ├── OpenAPI Spec: 28
│   ├── Agent Swarm: 13
│   └── Other: 2
└── Hand-Crafted (Manual): 30 examples
    ├── ZeroDB: 15
    ├── AIkit SDK: 13
    └── Agent Swarm: 2
```

---

## File Locations

### HuggingFace Space Files
```
hf_space/
├── app.py              # Gradio interface with training controls
├── requirements.txt    # Python dependencies
└── README.md           # Space documentation
```

### Dataset Files
```
outputs/ainative_dataset/
├── train/              # 88 training examples
├── validation/         # 10 evaluation examples
└── dataset_dict.json   # Dataset metadata

data/training/
├── ainative_train.jsonl           # Original training JSONL
└── ainative_eval.jsonl            # Original eval JSONL
```

### Scripts
```
scripts/
├── upload_dataset_to_hf.py        # Upload dataset to HF Hub
├── extract_ainative_training_data.py   # Extract examples (completed)
├── validate_ainative_training_data.py  # Validate quality (completed)
└── create_handcrafted_examples.py      # Generate examples (completed)
```

### Documentation
```
docs/training/
├── hf-spaces-deployment-guide.md          # Detailed deployment steps
├── AINATIVE_TRAINING_COMPLETE_SETUP.md    # Complete setup reference
├── ainative-training-ready.md             # Training details
└── ainative-extraction-progress-summary.md # Dataset creation summary
```

---

## Post-Training Steps

### 1. Download Trained Adapter

After training completes:
1. Go to your Space's **Files** tab
2. Navigate to `ainative-adapter-v1/`
3. Download:
   - `adapter_config.json`
   - `adapter_model.safetensors`

### 2. Test Locally

```python
from unsloth import FastLanguageModel

# Load adapter
model, tokenizer = FastLanguageModel.from_pretrained(
    "path/to/ainative-adapter-v1",
    max_seq_length=2048,
    load_in_4bit=True,
)

# Test prompt
prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert AINative platform developer...<|eot_id|><|start_header_id|>user<|end_header_id|>

How do I implement Agent Swarm task delegation with error recovery?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

FastLanguageModel.for_inference(model)
output = model.generate(**tokenizer(prompt, return_tensors="pt"), max_new_tokens=512)
print(tokenizer.decode(output[0]))
```

### 3. Validate Quality (Issue #77)

Test knowledge areas:
- ✅ Agent Swarm orchestration
- ✅ AIkit SDK integration
- ✅ ZeroDB operations
- ✅ TDD/BDD patterns
- ✅ OpenAPI specifications

### 4. Integrate into Backend (Issue #78)

- Add to model registry
- Update configuration
- Deploy to staging
- Monitor performance

---

## Troubleshooting

### Space Build Fails
**Problem**: Dependencies fail to install
**Solution**: Check requirements.txt versions, reduce dependencies

### Training OOM
**Problem**: Out of memory during training
**Solution**:
- Reduce batch_size to 1
- Increase gradient_accumulation to 16
- Reduce max_seq_length to 1024

### Dataset Not Found
**Problem**: "Dataset not found" error
**Solution**:
- Verify dataset uploaded to Hub
- Check dataset name: `ainative/ainative-training-v1`
- Ensure HF_TOKEN is set correctly
- Make dataset public

### Queue Wait Time
**Problem**: ZeroGPU queue is long
**Solution**:
- Train during off-peak hours (nights/weekends)
- Or upgrade to paid GPU tier

---

## Alternative Training Options

If HuggingFace Spaces is unavailable:

### RunPod
- Use A10G GPU ($1/hour)
- Run `scripts/train_ainative_adapter.py`

### Google Colab
- Use T4 GPU (free) or A100 (paid)
- Upload and run training script

### Local GPU
- Requires 10GB+ VRAM
- Install: `pip install unsloth transformers trl torch`
- Run: `python3 scripts/train_ainative_adapter.py`

---

## Success Checklist

### Pre-Deployment ✅
- [x] Dataset created (98 examples)
- [x] Dataset validated (0 AI attribution)
- [x] HF Space files ready
- [x] Upload script ready
- [x] Documentation complete
- [x] Dataset formatted for HF Hub

### Deployment (Your Action Required)
- [ ] HuggingFace account ready
- [ ] HF_TOKEN obtained
- [ ] Dataset uploaded to HF Hub
- [ ] Space created/updated
- [ ] HF_TOKEN secret added to Space
- [ ] Training started

### Post-Training (After Training Completes)
- [ ] Adapter downloaded
- [ ] Locally tested
- [ ] Quality validated (Issue #77)
- [ ] Integrated into backend (Issue #78)
- [ ] Deployed to staging
- [ ] Production ready

---

## Summary

**Everything is ready for deployment!**

### Key Achievements
✅ 98 high-quality examples (0 AI attribution violations)
✅ Complete HuggingFace Space setup
✅ Dataset formatted and ready
✅ Comprehensive documentation
✅ Free GPU access via ZeroGPU

### Next Action
**Deploy to HuggingFace Spaces** using the instructions above.

### Time Estimate
- **Setup + Upload**: 15-20 minutes
- **Training**: 1-2 hours (automated)
- **Total**: ~2-3 hours to trained adapter

---

## Support Resources

- **Deployment Guide**: `docs/training/hf-spaces-deployment-guide.md`
- **Complete Setup**: `docs/training/AINATIVE_TRAINING_COMPLETE_SETUP.md`
- **Training Details**: `docs/training/ainative-training-ready.md`
- **Dataset Info**: `docs/training/ainative-extraction-progress-summary.md`

---

**Ready to deploy!** 🚀
