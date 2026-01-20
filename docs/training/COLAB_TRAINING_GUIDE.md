# Google Colab Training Guide - Kwanzaa Adapter

## Overview

This guide will help you train the Kwanzaa adapter on Google Colab's **FREE T4 GPU** instead of RunPod.

**Advantages:**
- ✅ Completely FREE (with usage limits)
- ✅ No credit card required
- ✅ 15-20 minute training time
- ✅ Easy file upload/download
- ✅ No CLI configuration needed

**Training Stats:**
- Model: Llama-3.2-1B-Instruct
- Method: QLoRA (4-bit quantization)
- Training samples: 107
- Eval samples: 27
- GPU: NVIDIA T4 (free tier)
- Estimated time: 15-20 minutes

## Step-by-Step Instructions

### 1. Prepare Files

You need these two files from your local machine:
- `data/training/kwanzaa_train.jsonl` (107 samples, 578KB)
- `data/training/kwanzaa_eval.jsonl` (27 samples, 126KB)

### 2. Open Google Colab

1. Go to https://colab.research.google.com
2. Sign in with your Google account
3. Click: **File → Upload notebook**
4. Upload: `kwanzaa_training_colab.ipynb` from this repo

### 3. Enable GPU

1. Click: **Runtime → Change runtime type**
2. Hardware accelerator: **T4 GPU**
3. Click: **Save**

### 4. Upload Training Data

1. Click the **Files** icon in left sidebar (folder icon)
2. Click **Upload** button
3. Upload both JSONL files:
   - `kwanzaa_train.jsonl`
   - `kwanzaa_eval.jsonl`
4. They should appear in `/content/` directory

### 5. Accept Llama License

Before running the notebook:
1. Go to: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
2. Click **Access repository**
3. Accept the license agreement
4. Get your Hugging Face token: https://huggingface.co/settings/tokens
   - Create a token with "Read" access if you don't have one

### 6. Run Training

1. Click: **Runtime → Run all** (or press Ctrl+F9)
2. When prompted, paste your Hugging Face token
3. Wait 15-20 minutes for training to complete

**What happens:**
- Cell 1: Installs dependencies (~2 min)
- Cell 2: Login to HF (requires your token)
- Cell 3: Loads training data
- Cell 4: Loads model in 4-bit mode (~2 min)
- Cell 5: Formats data with chat template
- Cell 6: Configures training
- Cell 7: **TRAINS THE MODEL** (~15 min)
- Cell 8: Saves adapter
- Cell 9: Tests the adapter

### 7. Monitor Training

You'll see output like:
```
Step 10/321 | Loss: 1.234 | LR: 0.0002
Step 20/321 | Loss: 1.123 | LR: 0.00019
...
Training complete!
```

### 8. Download Adapter

After training completes:
1. In Files sidebar, navigate to: `/content/outputs/kwanzaa-adapter-v1/`
2. Right-click the folder
3. Click **Download**

**Files you'll get:**
- `adapter_config.json` - LoRA configuration
- `adapter_model.safetensors` - Trained weights (~6MB)
- `tokenizer_config.json` - Tokenizer settings
- `tokenizer.json` - Tokenizer vocabulary
- `special_tokens_map.json` - Special tokens

### 9. Test the Adapter (Optional)

Cell 9 in the notebook will test the adapter with a sample query. You should see a properly formatted JSON response with citations.

### 10. (Optional) Push to Hugging Face

If you want to save the adapter to your HF account:
1. Uncomment the code in Cell 10
2. Replace `your-username` with your HF username
3. Run the cell
4. Adapter will be available at: `https://huggingface.co/your-username/kwanzaa-adapter-v1`

## Troubleshooting

### "No GPU available"
- Make sure you selected T4 GPU in Runtime settings
- Free tier has usage limits; try again later if quota exceeded

### "File not found: kwanzaa_train.jsonl"
- Make sure you uploaded both JSONL files to `/content/` directory
- Check the Files sidebar to verify files are present

### "Token is invalid"
- Get a new token from: https://huggingface.co/settings/tokens
- Make sure you accepted the Llama 3.2 license

### "CUDA out of memory"
- This shouldn't happen with 1B model on T4
- Try: Runtime → Restart runtime → Run all again
- Reduce `per_device_train_batch_size` to 1 (already set)

### Training taking too long
- Free Colab disconnects after ~12 hours
- Our training takes 15-20 min, so this shouldn't be an issue
- Keep the browser tab open during training

## What's Next?

After downloading the adapter:
1. Save it to: `backend/models/adapters/kwanzaa-adapter-v1/`
2. Update Issue #52 (Save & Version Adapter Artifact)
3. Run evaluations (Issues #54, #56, #58, #60)
4. Deploy to production

## Cost Comparison

| Platform | GPU | Cost | Time | Complexity |
|----------|-----|------|------|------------|
| **Google Colab** | T4 | **$0.00** | 15-20 min | ⭐ Easy |
| RunPod | RTX 4090 | $0.34/hr (~$0.10) | 10-15 min | ⭐⭐⭐ Complex |
| HF Spaces | T4 Small | $0.40/hr (~$0.13) | 15-20 min | ⭐⭐ Medium |

**Winner:** Google Colab for free training! 🎉

## Free Tier Limits

Google Colab free tier includes:
- T4 GPU access (when available)
- ~12 hours max session
- Variable availability (peak times may have no GPUs)
- Session timeout after ~90 min idle

**Our training takes 15-20 minutes, well within limits!**

## Need Help?

- Colab FAQ: https://research.google.com/colaboratory/faq.html
- HF Token Help: https://huggingface.co/docs/hub/security-tokens
- Llama 3.2 Docs: https://huggingface.co/docs/transformers/model_doc/llama3

---

**Ready to train?** Upload `kwanzaa_training_colab.ipynb` to Colab and let's go! 🚀
