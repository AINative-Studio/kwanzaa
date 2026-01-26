# AINative Adapter - Next Steps

**Training Status**: ✅ Complete
**Date**: 2026-01-25

---

## Quick Summary

The AINative adapter training completed successfully on HuggingFace Spaces! The adapter is in the Space's temporary storage and ready to be pushed to HuggingFace Hub.

**What's Done**:
- ✅ Dataset uploaded to Hub (98 examples, 92% valid, 0% AI attribution)
- ✅ Training completed on ZeroGPU A100
- ✅ Validation script created
- ✅ Space updated with "Push to Hub" button

**What's Next**:
1. Push adapter to HuggingFace Hub
2. Download and validate adapter
3. Integrate into backend API (Issue #78)

---

## Option 1: Push to Hub via Space UI (Easiest)

I've updated the HuggingFace Space with a "Push to Hub" button that will automatically upload the adapter.

### Steps:

1. **Visit the Space**:
   ```
   https://huggingface.co/spaces/ainativestudio/kwanzaa-training
   ```

2. **Push the Updated Space**:
   ```bash
   cd hf_space_clone
   git push https://$HF_TOKEN@huggingface.co/spaces/ainativestudio/kwanzaa-training main
   ```

3. **Use the "Push to Hub" Button**:
   - Once the Space reloads with the new interface
   - Click the "📤 Push to Hub" button
   - Wait for upload to complete
   - Adapter will be at: https://huggingface.co/ainativestudio/ainative-adapter-v1

4. **Download the Adapter**:
   ```bash
   python scripts/download_ainative_adapter.py
   ```

5. **Validate**:
   ```bash
   python scripts/validate_ainative_adapter.py
   ```

---

## Option 2: Manual Download from Space

If you prefer manual control:

1. **Visit Space Files Tab**:
   ```
   https://huggingface.co/spaces/ainativestudio/kwanzaa-training/tree/main
   ```

2. **Navigate to Adapter Directory**:
   - Look for `ainative-adapter-v1/` or similar
   - May be in root or subdirectory

3. **Download Files**:
   - `adapter_config.json`
   - `adapter_model.safetensors` (or `adapter_model.bin`)

4. **Place in Project**:
   ```bash
   mkdir -p outputs/adapters/ainative-v1
   # Copy downloaded files to outputs/adapters/ainative-v1/
   ```

5. **Validate**:
   ```bash
   python scripts/validate_ainative_adapter.py
   ```

---

## Option 3: Re-run Training

If the adapter files aren't accessible:

1. **Push Updated Space** (with "Push to Hub" button):
   ```bash
   cd hf_space_clone
   git push https://$HF_TOKEN@huggingface.co/spaces/ainativestudio/kwanzaa-training main
   ```

2. **Visit Space and Train**:
   - Go to https://huggingface.co/spaces/ainativestudio/kwanzaa-training
   - Click "🚀 Start Training"
   - Wait for training to complete (~15-20 minutes on ZeroGPU)
   - Click "📤 Push to Hub"

3. **Download**:
   ```bash
   python scripts/download_ainative_adapter.py
   ```

---

## What I've Prepared for You

### Scripts Created

1. **`scripts/download_ainative_adapter.py`**
   - Downloads adapter from HuggingFace Hub
   - Verifies file integrity
   - Usage: `python scripts/download_ainative_adapter.py`

2. **`scripts/validate_ainative_adapter.py`**
   - 10 comprehensive tests across 5 categories
   - Tests: Agent Swarm, AIkit SDK, ZeroDB, TDD/BDD, OpenAPI
   - Zero AI Attribution check
   - Usage: `python scripts/validate_ainative_adapter.py`

3. **`scripts/push_adapter_to_hub.py`**
   - Standalone script for pushing adapter
   - Can be run locally or in Space
   - Creates model repo and README

4. **`scripts/list_space_files.py`**
   - Lists all files in HuggingFace Space
   - Useful for debugging

5. **`scripts/check_adapter_repo.py`**
   - Checks if adapter exists on Hub
   - Lists all ainativestudio models

### Space Updates

**File**: `hf_space_clone/app.py`

**New Features**:
- ✅ "📤 Push to Hub" button
- ✅ Repository name configuration
- ✅ Automatic README generation
- ✅ File validation before upload
- ✅ Status updates during push

**To Deploy**:
```bash
cd hf_space_clone
git push https://$HF_TOKEN@huggingface.co/spaces/ainativestudio/kwanzaa-training main
```

### Documentation Created

1. **`docs/training/ainative-adapter-retrieval.md`**
   - Complete retrieval guide
   - All 3 options explained
   - Troubleshooting section

2. **`docs/training/ainative-training-status.md`**
   - Full status report
   - Training configuration
   - Next steps for Issue #78

3. **`docs/training/AINATIVE_NEXT_STEPS.md`** (this file)
   - Quick reference guide
   - Step-by-step instructions

### Configuration Updates

1. **`backend/.env`**
   ```bash
   HF_TRAINING_SPACE=https://huggingface.co/spaces/ainativestudio/kwanzaa-training
   ```

2. **`.claude/skills/huggingface-adapter-training/SKILL.md`**
   - Updated with AINative dataset
   - ZERO TOLERANCE rules documented
   - Space URL canonicalized

---

## After Adapter Retrieval

Once you have the adapter files in `outputs/adapters/ainative-v1/`:

### 1. Validate Adapter (Issue #77)

```bash
python scripts/validate_ainative_adapter.py
```

**Expected Results**:
- Overall Score: ≥70%
- Tests Passed: ≥7/10
- Zero AI Attribution: ✅ PASSED
- Category Scores:
  - Agent Swarm: ≥60%
  - AIkit SDK: ≥60%
  - ZeroDB: ≥60%
  - TDD/BDD: ≥60%
  - OpenAPI: ≥60%

**Output**: `outputs/ainative_adapter_validation.json`

### 2. Integrate into Backend (Issue #78)

**Tasks**:
1. Add adapter to model registry
2. Update `backend/config/models.yaml`:
   ```yaml
   ainative:
     name: "AINative Platform Adapter"
     base_model: "unsloth/Llama-3.2-1B-Instruct"
     adapter_path: "../outputs/adapters/ainative-v1"
     type: "qlora"
     use_cases:
       - agent_swarm
       - aikit_sdk
       - zerodb
       - tdd_patterns
       - openapi_design
   ```

3. Create adapter service wrapper
4. Add API endpoints:
   - `POST /api/v1/ainative/query` - Ask AINative questions
   - `POST /api/v1/ainative/generate` - Generate code/docs
   - `GET /api/v1/ainative/health` - Adapter health check

5. Add tests:
   - Integration tests for new endpoints
   - Load tests for performance
   - Quality tests for responses

6. Deploy to staging
7. Monitor performance and quality

---

## Validation Test Examples

The validation script tests these scenarios:

**Agent Swarm**:
- "How do I create a parallel agent swarm with 3 agents using the AINative API?"
- "What's the difference between sequential and parallel agent execution?"

**AIkit SDK**:
- "Show me how to initialize the AINative React SDK"
- "How do I use the useAgentSwarm hook in a Next.js component?"

**ZeroDB**:
- "How do I store a vector embedding in ZeroDB?"
- "What's the API endpoint for semantic search in ZeroDB?"

**TDD/BDD**:
- "Write a pytest test for a FastAPI endpoint that creates a user"
- "Show me BDD-style test structure for testing API endpoints"

**OpenAPI**:
- "How do I define a POST endpoint in OpenAPI 3.0 spec?"
- "What's the structure for defining request validation in OpenAPI?"

---

## Key Resources

### HuggingFace
- **Training Space**: https://huggingface.co/spaces/ainativestudio/kwanzaa-training
- **Dataset**: https://huggingface.co/datasets/ainativestudio/ainative-training-v1
- **Adapter (after push)**: https://huggingface.co/ainativestudio/ainative-adapter-v1
- **Token**: In `backend/.env` as `HF_TOKEN`

### Local Files
- **Scripts**: `scripts/` directory
- **Documentation**: `docs/training/` directory
- **Adapter Output**: `outputs/adapters/ainative-v1/` (after download)
- **Validation Results**: `outputs/ainative_adapter_validation.json` (after validation)

### Git Repositories
- **Project**: `/Users/aideveloper/kwanzaa`
- **Space Clone**: `/Users/aideveloper/kwanzaa/hf_space_clone`

---

## Troubleshooting

### "Adapter directory not found"
**Solution**: The adapter hasn't been pushed to Hub yet. Use Option 1 or 2 above.

### "Push to Hub button not showing"
**Solution**: Push the updated Space app:
```bash
cd hf_space_clone
git push https://$HF_TOKEN@huggingface.co/spaces/ainativestudio/kwanzaa-training main
```

### "Space files tab is empty"
**Solution**: The adapter is in temporary storage. Use the "Push to Hub" button to persist it.

### "Download script fails with 404"
**Solution**: The adapter repository doesn't exist yet. Push the adapter to Hub first.

---

## Success Criteria

You'll know everything worked when:

1. ✅ Adapter repository exists: https://huggingface.co/ainativestudio/ainative-adapter-v1
2. ✅ Adapter downloaded to `outputs/adapters/ainative-v1/`
3. ✅ Validation script passes (≥70% score)
4. ✅ Zero AI attribution check passes
5. ✅ Ready to integrate into backend API

---

## Timeline Estimate

- **Push Space Updates**: 2 minutes
- **Push Adapter to Hub**: 3-5 minutes
- **Download Adapter**: 1-2 minutes
- **Validate Adapter**: 5-10 minutes
- **Total**: ~15-20 minutes

If re-running training:
- **Training Time**: 15-20 minutes (on ZeroGPU)
- **Total with Training**: ~35-40 minutes

---

## Need Help?

**Documentation**:
- `docs/training/ainative-adapter-retrieval.md` - Detailed retrieval guide
- `docs/training/ainative-training-status.md` - Full status report

**Scripts**:
- `scripts/list_space_files.py` - See what's in the Space
- `scripts/check_adapter_repo.py` - Check if adapter is on Hub

**Space URL**: https://huggingface.co/spaces/ainativestudio/kwanzaa-training

---

**Ready to proceed!** Start with Option 1 (easiest) or choose what works best for your workflow.
