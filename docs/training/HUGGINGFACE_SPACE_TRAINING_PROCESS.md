# HuggingFace Space Training Process

**Status**: Production-Ready
**Version**: 1.0
**Last Updated**: 2026-01-27
**Skill Reference**: `.claude/skills/huggingface-adapter-training/SKILL.md`

## Overview

This document describes the CORRECT process for training Kwanzaa and AINative adapters using HuggingFace Spaces. This process has been validated and should be followed to avoid common pitfalls.

## Space Configuration

**Space URL**: https://huggingface.co/spaces/ainativestudio/kwanzaa-training
**Repository**: `ainativestudio/kwanzaa-training`
**Type**: Docker SDK Space
**Hardware**: A10G GPU (assigned when training starts)

## Critical Rules

### 1. NEVER Include requirements.txt with Docker SDK

**PROBLEM**: When using Docker SDK, HuggingFace Spaces may try to install packages from `requirements.txt` in addition to or instead of the Dockerfile, causing dependency conflicts.

**SOLUTION**: Delete any `requirements.txt` file from the Space. The Dockerfile handles ALL dependencies.

```bash
# Check for requirements.txt
python3 -c "
from huggingface_hub import list_repo_files
import os
token = os.getenv('HF_TOKEN') or open('backend/.env').read().split('HF_TOKEN=')[1].split()[0]
files = list_repo_files('ainativestudio/kwanzaa-training', repo_type='space', token=token)
if 'requirements.txt' in files:
    print('⚠️  WARNING: requirements.txt found - DELETE IT')
else:
    print('✅ No requirements.txt - correct configuration')
"
```

### 2. Use Stable Base Images

**PROBLEM**: Using `latest` tags or unstable base images causes build timeouts and failures.

**SOLUTION**: Use pinned, stable NVIDIA CUDA base images:

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
```

NOT:
- `huggingface/transformers-pytorch-gpu:latest` ❌
- `huggingface/autotrain-advanced:latest` ❌
- Any image with `:latest` tag ❌

### 3. Pin ALL Dependencies

**PROBLEM**: Unpinned dependencies cause version conflicts and build failures.

**SOLUTION**: Specify exact versions for all packages:

```dockerfile
RUN pip3 install --no-cache-dir \
    torch==2.1.0 \
    transformers==4.36.0 \
    datasets==2.16.0 \
    peft==0.7.1 \
    bitsandbytes==0.41.3 \
    trl==0.7.4 \
    accelerate==0.25.0 \
    huggingface_hub==0.20.0 \
    gradio==5.10.0
```

### 4. Install PyTorch with CUDA Index

**PROBLEM**: Installing PyTorch without specifying CUDA index downloads CPU-only version.

**SOLUTION**: Always use the CUDA index URL:

```dockerfile
RUN pip3 install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cu118
```

### 5. NO Hardcoded Tokens

**PROBLEM**: Hardcoded HF_TOKEN in files gets caught by GitHub secret scanning.

**SOLUTION**: Always reference the .env file:

```bash
# In documentation/skills
HF_TOKEN=$(grep HF_TOKEN backend/.env | cut -d '=' -f2)

# In Python scripts
token = os.getenv("HF_TOKEN")
```

## Correct File Structure

The Space should contain ONLY these files:

```
kwanzaa-training/
├── .gitattributes      # HuggingFace metadata
├── README.md           # Space description with YAML frontmatter
├── Dockerfile          # Complete build configuration
├── app.py              # Gradio UI with Start Training button
└── train.py            # Training script
```

**Total: 5 files**

If you see 6+ files, check for and delete:
- `requirements.txt` ❌
- Any other unexpected files ❌

## Required Files

### README.md

Must include YAML frontmatter:

```yaml
---
title: AINative Adapter Training
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---
```

### Dockerfile

See `.claude/skills/huggingface-adapter-training/SKILL.md` for the complete, validated Dockerfile.

Key requirements:
- NVIDIA CUDA base image (pinned version)
- Python 3.10
- PyTorch with CUDA 11.8 support
- All training dependencies pinned
- Health check endpoint
- Port 7860 exposed

### app.py

Gradio UI requirements:
- Compatible with Gradio 5.10.0 (NO `show_api=False`, NO `theme` in Blocks())
- Single "Start Training" button
- Streams output from `train.py` in real-time
- Error handling and diagnostics

### train.py

Training script requirements:
- Loads dataset from HuggingFace Hub
- Uses 4-bit quantization with bitsandbytes
- Applies QLoRA adapters (r=16, alpha=32)
- Trains for 4 epochs with lr=2e-4
- Pushes to Hub automatically

## Training Workflow

### Phase 1: Prepare Enhanced Dataset

1. **Extract training data** from relevant codebase:
   ```bash
   # For AINative adapter
   python3 scripts/extract_ainative_training_data.py
   ```

2. **Validate dataset**:
   ```bash
   python3 scripts/validate_ainative_training_data.py
   ```

3. **Upload to HuggingFace Hub**:
   ```bash
   python3 scripts/upload_ainative_dataset_hf.py
   ```

### Phase 2: Configure Space

1. **Update local Space files** in `/tmp/kwanzaa-training/`:
   - `Dockerfile` - Update dependencies if needed
   - `app.py` - Update dataset reference in UI
   - `train.py` - Update dataset and output paths

2. **Push to HuggingFace Space**:
   ```bash
   cd /tmp/kwanzaa-training

   # Initialize git if needed
   git init
   git remote add space https://huggingface.co/spaces/ainativestudio/kwanzaa-training

   # Push files
   git add Dockerfile app.py train.py README.md
   git commit -m "Update training configuration"
   git push space main
   ```

3. **Verify NO requirements.txt**:
   ```bash
   python3 /tmp/check_space_files.py
   # Should show 5 files, NOT 6
   ```

### Phase 3: Monitor Build

1. **Check Space status**:
   ```bash
   curl -s "https://huggingface.co/api/spaces/ainativestudio/kwanzaa-training" | \
     python3 -c "import sys, json; data = json.load(sys.stdin); \
     print(f'Status: {data[\"runtime\"][\"stage\"]}')"
   ```

2. **Expected build stages**:
   - `BUILDING` (10-20 minutes) - Docker image building
   - `RUNNING` - Space ready for training

3. **If BUILD_ERROR**:
   - Check for requirements.txt file (delete if present)
   - Verify Dockerfile base image is stable
   - Check all dependencies are pinned
   - Review app.py for Gradio compatibility

### Phase 4: Start Training

1. **Access Space UI**:
   https://huggingface.co/spaces/ainativestudio/kwanzaa-training

2. **Click "Start Training" button**

3. **Monitor progress** in the Gradio output textbox:
   - Training will take 1-2 hours on A10G GPU
   - Progress logged every 10 steps
   - Adapter pushed to Hub automatically on completion

### Phase 5: Validate Adapter

1. **Download trained adapter**:
   ```bash
   python3 scripts/download_ainative_adapter.py --version v2
   ```

2. **Run validation**:
   ```bash
   python3 scripts/validate_ainative_adapter_cpu.py
   ```

3. **Expected results**:
   - Overall score: ≥75%
   - Category scores: ≥70% each
   - Zero AI attribution: 100%

## Troubleshooting

### Build Timeouts

**Symptom**: "Launch timed out, workload was not healthy after 30 min"

**Causes**:
1. Using unstable base images (`:latest` tags)
2. Conflicting requirements.txt file
3. Downloading large models during build

**Solutions**:
1. Use pinned NVIDIA CUDA base image
2. Delete requirements.txt
3. Models should be downloaded at runtime, not build time

### Build Errors

**Symptom**: Space shows BUILD_ERROR status

**Debug steps**:
```bash
# 1. Check files
python3 /tmp/check_space_files.py

# 2. Read Dockerfile from Space
python3 /tmp/read_space_file.py Dockerfile

# 3. Check for requirements.txt
python3 /tmp/read_space_file.py requirements.txt
# If found, delete it:
python3 /tmp/fix_space_requirements.py
```

### Runtime Errors

**Symptom**: Space shows RUNTIME_ERROR status

**Common causes**:
1. Gradio version incompatibility
2. Missing health check endpoint
3. Wrong port configuration

**Solutions**:
1. Use Gradio 5.10.0 (avoid 6.0+ features)
2. Ensure health check uses `curl -f http://localhost:7860/`
3. Verify `app_port: 7860` in README.md YAML

## Integration with Backend

After successful training and validation:

1. **Copy adapter to backend**:
   ```bash
   cp -r backend/models/adapters/ainative-adapter-v2 \
         /path/to/production/backend/models/adapters/
   ```

2. **Update backend config** to load new adapter

3. **Test integration** with production API

4. **Deploy** following CI/CD workflow

## Quick Reference Commands

```bash
# Check Space status
curl -s "https://huggingface.co/api/spaces/ainativestudio/kwanzaa-training" | \
  python3 -c "import sys, json; d = json.load(sys.stdin); \
  print(f'Stage: {d[\"runtime\"][\"stage\"]}')"

# List Space files
python3 /tmp/check_space_files.py

# Read Space file
python3 /tmp/read_space_file.py <filename>

# Delete requirements.txt
python3 /tmp/fix_space_requirements.py

# Monitor build
tail -f /tmp/space_build_monitor.log

# Download adapter
python3 scripts/download_ainative_adapter.py --version v2

# Validate adapter
python3 scripts/validate_ainative_adapter_cpu.py
```

## Success Criteria

✅ Space shows RUNNING status
✅ Only 5 files in Space (NO requirements.txt)
✅ Build completes in 10-20 minutes
✅ Training completes in 1-2 hours
✅ Adapter uploaded to Hub automatically
✅ Validation scores ≥75% overall
✅ Zero AI attribution violations

## Related Documentation

- **Skill**: `.claude/skills/huggingface-adapter-training/SKILL.md`
- **Dataset Extraction**: `docs/training/ainative-training-data-extraction-plan.md`
- **Validation**: `docs/training/ainative-validation-results-template.md`
- **Backend Integration**: Backend README (integration steps)

## Version History

- **1.0** (2026-01-27): Initial documentation of validated process
  - Documented requirements.txt deletion requirement
  - Documented stable base image requirement
  - Documented dependency pinning requirement
  - Added troubleshooting guide
  - Added quick reference commands
