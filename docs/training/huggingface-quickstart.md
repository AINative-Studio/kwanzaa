# HuggingFace Quick Start Guide

Quick reference for using HuggingFace with the Kwanzaa project.

## Current Setup (Verified ✅)

- **Account**: `ainativestudio`
- **Token**: Configured in `backend/.env` as `HF_TOKEN`
- **Status**: Valid and verified
- **Permissions**: Read + Write
- **Gated Models**: Accessible (LLaMA 3.2, Mistral)

## Quick Commands

### Verify Token

```bash
# Basic verification
python scripts/verify-huggingface-token.py

# Full verification with all checks
python scripts/verify-huggingface-token.py --check-gated-models --check-write-access
```

### Download Model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

model_id = "meta-llama/Llama-3.2-1B"
token = os.getenv("HF_TOKEN")

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    token=token,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
```

### Upload Adapter

```python
from huggingface_hub import HfApi
import os

api = HfApi(token=os.getenv("HF_TOKEN"))

# Create repository
repo_id = "ainativestudio/kwanzaa-adapter-v1"
api.create_repo(repo_id=repo_id, repo_type="model", private=True)

# Upload adapter
api.upload_folder(
    folder_path="./trained_adapters/kwanzaa-v1",
    repo_id=repo_id
)
```

## Environment Setup

```bash
# 1. Ensure .env file exists
cd backend/
cat .env | grep HF_TOKEN

# 2. Verify .env is gitignored
git check-ignore .env

# 3. Load environment variables
export $(cat .env | grep HF_TOKEN)

# 4. Test token
python scripts/verify-huggingface-token.py
```

## Security Checklist (Quick)

- [ ] Token in `backend/.env` (not hardcoded)
- [ ] `.env` in `.gitignore`
- [ ] No tokens in git history
- [ ] Token has required permissions
- [ ] Token rotated every 90 days

**Full Checklist**: See `docs/training/huggingface-security-checklist.md`

## Common Issues

### Issue: "Invalid authentication token"

```bash
# Solution: Verify token is set correctly
echo $HF_TOKEN
python scripts/verify-huggingface-token.py
```

### Issue: "Access denied to gated model"

```bash
# Solution: Request access first
# 1. Visit model page (e.g., https://huggingface.co/meta-llama/Llama-3.2-1B)
# 2. Click "Request Access"
# 3. Accept terms
# 4. Wait for approval (usually instant)
```

### Issue: "No write permission"

```bash
# Solution: Check token type
python scripts/verify-huggingface-token.py --check-write-access

# If read-only, generate new write token:
# https://huggingface.co/settings/tokens
```

## Next Steps

### For Development
✅ You're ready! Token is configured and verified.

### For Organization Setup (Optional)
See: `docs/training/huggingface-organization-recommendations.md`

1. Create organization: `kwanzaa-project`
2. Update `.env`: `HF_ORGANIZATION=kwanzaa-project`
3. Invite team members

### For Production
See: `docs/training/huggingface-security-checklist.md`

1. Use secrets manager (not .env)
2. Generate fine-grained token for CI/CD
3. Complete security checklist
4. Setup token rotation

## Documentation

| Document | Purpose |
|----------|---------|
| `huggingface-setup.md` | Complete setup guide |
| `huggingface-security-checklist.md` | Security best practices |
| `huggingface-organization-recommendations.md` | Organization decision guide |
| `huggingface-quickstart.md` | This quick reference |

## Support

- **Token issues**: Run `python scripts/verify-huggingface-token.py`
- **Security questions**: See security checklist
- **Setup help**: See main setup guide
- **HuggingFace support**: https://discuss.huggingface.co

---

**Last Updated**: 2026-01-16
**Status**: Production Ready for Development
