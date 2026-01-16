# HuggingFace Account & Organization Setup Guide

**Issue:** #36 - E3A-US2 - Create Hugging Face Account & Org
**Epic:** EPIC 3A - HuggingFace Environment & Prerequisites
**Version:** 1.0.0
**Last Updated:** January 16, 2026

---

## Overview

This guide documents the complete process for creating and configuring a HuggingFace account and organization for the Kwanzaa project. HuggingFace infrastructure is required for training adapters, publishing models, and accessing gated models like LLaMA.

**Key Requirements:**
- HuggingFace account with appropriate permissions
- Organization for team collaboration
- Secure token management
- Access control and repository visibility

### Current Setup Status

**Last Verified**: January 16, 2026

- **Account**: `ainativestudio`
- **Token Status**: Valid and verified (37 characters, older format)
- **Token Format**: Stored in `backend/.env` as `HF_TOKEN`
- **Gated Model Access**: Enabled and verified
  - ✓ meta-llama/Llama-3.2-1B
  - ✓ meta-llama/Llama-3.2-3B
  - ✓ mistralai/Mistral-7B-v0.1
- **Write Access**: Available and confirmed
- **Organization**: Not configured (recommended to add - see Organization Setup)
- **Token Security**: Properly gitignored in `backend/.env`

**Verification Script**: `scripts/verify-huggingface-token.py`

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Account Creation](#account-creation)
3. [Organization Setup](#organization-setup)
4. [Access Token Generation](#access-token-generation)
5. [Token Storage & Management](#token-storage--management)
6. [Security Best Practices](#security-best-practices)
7. [Team Access Control](#team-access-control)
8. [Repository Management](#repository-management)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Valid email address for account creation
- [ ] Access to secure password manager
- [ ] Team member list (for organization setup)
- [ ] Project naming conventions agreed upon
- [ ] Security requirements understood

**Estimated Time:** 15-20 minutes

---

## Account Creation

### Step 1: Create Personal HuggingFace Account

1. **Navigate to HuggingFace:**
   - Visit: https://huggingface.co/join
   - Use company/project email (recommended)

2. **Complete Registration:**
   ```
   Username: Choose wisely - this is permanent
   Email: your-email@company.com
   Password: Use strong password (16+ characters, mixed case, numbers, symbols)
   ```

3. **Verify Email:**
   - Check inbox for verification email
   - Click verification link
   - Complete account activation

4. **Enable Two-Factor Authentication (Mandatory):**
   - Go to: https://huggingface.co/settings/account
   - Click "Enable Two-Factor Authentication"
   - Use authenticator app (Authy, Google Authenticator, 1Password)
   - Save backup codes in secure location

### Step 2: Complete Profile Setup

1. **Profile Information:**
   - Navigate to: https://huggingface.co/settings/profile
   - Add profile picture (optional but recommended)
   - Fill in bio mentioning project affiliation
   - Add website/GitHub links

2. **Notification Preferences:**
   - Configure email notifications
   - Enable security alerts
   - Set collaboration notifications

---

## Organization Setup

### Step 1: Create Organization

1. **Navigate to Organization Creation:**
   - Visit: https://huggingface.co/organizations/new
   - Or click profile dropdown → "New Organization"

2. **Organization Details:**
   ```
   Organization Name: kwanzaa-project
   Display Name: Kwanzaa Historical AI
   Organization Type: Company/Team
   ```

3. **Naming Conventions:**
   - **Organization:** `kwanzaa-project`
   - **Model Repository Naming:**
     - Adapters: `kwanzaa-{version}-{base-model}`
     - Example: `kwanzaa-v1-olmo`, `kwanzaa-v2-llama`
   - **Dataset Repository Naming:**
     - Datasets: `kwanzaa-{dataset-type}-{version}`
     - Example: `kwanzaa-primary-sources-v1`

### Step 2: Configure Organization Settings

1. **Organization Profile:**
   - Go to: https://huggingface.co/organizations/kwanzaa-project/settings/profile
   - Add organization description:
     ```
     Kwanzaa Historical AI - Advanced adapters for culturally-aware
     historical question answering with primary source citations.
     ```
   - Add project website
   - Add logo/avatar

2. **Organization Visibility:**
   - **Recommended:** Start with Private organization
   - Can convert to Public when ready for release
   - Configure member visibility settings

3. **Default Repository Settings:**
   - Set default visibility: Private (recommended for development)
   - Enable required approvals for public releases
   - Configure license defaults (Apache 2.0 or MIT recommended)

---

## Access Token Generation

### Understanding Token Types

HuggingFace offers different token types with varying permissions:

| Token Type | Use Case | Permissions |
|------------|----------|-------------|
| **Read** | Downloading gated models | Model downloads only |
| **Write** | Uploading adapters/models | Read + Upload models |
| **Fine-grained** | Production/CI/CD | Granular permissions |

### Step 1: Generate Read Token (For Model Downloads)

**Purpose:** Downloading gated models like LLaMA, Mistral, etc.

1. Navigate to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Configure token:
   ```
   Name: kwanzaa-read-token
   Type: read
   Expires: Never (or set appropriate expiration)
   ```
4. Click "Generate token"
5. Copy token immediately (shown only once)
6. Store in secure location (password manager)

**Token Format:** `hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` (40 characters)

### Step 2: Generate Write Token (For Adapter Publishing)

**Purpose:** Uploading trained adapters and models to HuggingFace Hub.

1. Navigate to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Configure token:
   ```
   Name: kwanzaa-write-token
   Type: write
   Expires: 90 days (recommended for security)
   ```
4. Click "Generate token"
5. Copy and store securely
6. Set calendar reminder for token rotation

### Step 3: Generate Fine-Grained Token (For CI/CD)

**Purpose:** Automated pipelines with minimal permissions.

1. Navigate to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Select "Fine-grained" token type
4. Configure permissions:
   ```
   Name: kwanzaa-ci-token
   Permissions:
     - Repositories: Read + Write (selected repos only)
     - Models: Read (specific models)
     - Datasets: Read (specific datasets)
   Scope:
     - Organization: kwanzaa-project
     - Repositories: kwanzaa-v1-olmo, kwanzaa-v2-llama (add as created)
   Expires: 90 days
   ```
5. Save token securely
6. Document which CI/CD pipelines use this token

### Token Management Matrix

| Environment | Token Type | Permissions | Rotation Schedule |
|-------------|-----------|-------------|-------------------|
| **Local Development** | Read | Model downloads | 1 year |
| **Training Machines** | Write | Upload adapters | 90 days |
| **CI/CD Pipeline** | Fine-grained | Specific repos | 90 days |
| **Production API** | Read | Model downloads | 90 days |

---

## Token Storage & Management

### Environment Variable Setup

#### Local Development

1. **Create `.env` file in project backend directory:**

```bash
cd /path/to/kwanzaa/backend
cp .env.example .env
```

2. **Add HuggingFace token:**

```bash
# Edit .env file
nano .env
```

```bash
# -----------------------------------------------------------------------------
# HuggingFace Configuration (Required for gated models)
# -----------------------------------------------------------------------------
# Get token from: https://huggingface.co/settings/tokens
# Use READ token for local development
HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

3. **Verify `.env` is in `.gitignore`:**

```bash
# Check if .env is ignored
cat .gitignore | grep -E "^\.env$"

# If not present, add it
echo ".env" >> .gitignore
```

#### CI/CD Environment (GitHub Actions)

1. **Add token as GitHub Secret:**
   - Navigate to: https://github.com/AINative-Studio/kwanzaa/settings/secrets/actions
   - Click "New repository secret"
   - Name: `HUGGINGFACE_TOKEN`
   - Value: Your token
   - Click "Add secret"

2. **Use in workflow file:**

```yaml
# .github/workflows/train-adapter.yml
name: Train Adapter

on:
  workflow_dispatch:
    inputs:
      base_model:
        description: 'Base model to train on'
        required: true

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Login to HuggingFace Hub
        env:
          HF_TOKEN: ${{ secrets.HUGGINGFACE_TOKEN }}
        run: |
          huggingface-cli login --token $HF_TOKEN

      - name: Train adapter
        run: |
          python train_adapter.py --base ${{ github.event.inputs.base_model }}
```

#### Production Deployment

**For Docker containers:**

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Set environment variable (value injected at runtime)
ENV HF_TOKEN=""

# Application code
COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
```

**Inject at runtime:**

```bash
# Using Docker run
docker run -e HF_TOKEN=$HF_TOKEN kwanzaa-api

# Using Kubernetes secret
kubectl create secret generic hf-credentials \
  --from-literal=token=$HF_TOKEN

# Reference in pod spec
env:
  - name: HF_TOKEN
    valueFrom:
      secretKeyRef:
        name: hf-credentials
        key: token
```

### Token Loading in Code

**Python example:**

```python
import os
from huggingface_hub import login

def load_huggingface_token():
    """
    Load HuggingFace token from environment variable.

    Raises:
        ValueError: If HF_TOKEN not found in environment
    """
    token = os.getenv("HF_TOKEN")

    if not token:
        raise ValueError(
            "HF_TOKEN not found in environment. "
            "Please set HF_TOKEN environment variable. "
            "Get token from: https://huggingface.co/settings/tokens"
        )

    # Login to HuggingFace Hub
    login(token=token)
    print("Successfully authenticated with HuggingFace Hub")

    return token

# Usage
if __name__ == "__main__":
    load_huggingface_token()
```

---

## Security Best Practices

### Token Security

1. **Never Commit Tokens to Git:**
   ```bash
   # Check for accidentally committed secrets
   git log -p | grep -E "hf_[a-zA-Z0-9]{40}"

   # If found, rotate token immediately and remove from history
   ```

2. **Use Environment Variables Only:**
   - Never hardcode tokens in source code
   - Never pass tokens as command-line arguments (visible in process list)
   - Never log tokens (even partially)

3. **Token Rotation Schedule:**
   - **Read tokens:** Rotate every 12 months
   - **Write tokens:** Rotate every 90 days
   - **Fine-grained tokens:** Rotate every 90 days
   - **Compromised tokens:** Revoke immediately

4. **Audit Token Usage:**
   ```bash
   # Check HuggingFace token usage logs
   # https://huggingface.co/settings/tokens → View activity

   # Review:
   - Last used timestamp
   - IP addresses
   - Operations performed
   - Suspicious activity
   ```

### Token Revocation Procedure

**If token is compromised:**

1. **Immediate Actions:**
   - Navigate to: https://huggingface.co/settings/tokens
   - Click "Revoke" on compromised token
   - Confirm revocation

2. **Generate New Token:**
   - Create new token with same permissions
   - Update all systems using old token
   - Document incident

3. **Audit Access:**
   - Check token activity logs for unauthorized access
   - Review recent model downloads/uploads
   - Check for unexpected repository changes

4. **Notify Team:**
   - Inform team of token rotation
   - Update documentation
   - Review security procedures

### Access Control Best Practices

1. **Principle of Least Privilege:**
   - Use Read tokens by default
   - Grant Write permissions only when needed
   - Use Fine-grained tokens for automation

2. **Separate Tokens by Environment:**
   - Development: Read-only tokens
   - Staging: Write tokens (limited repos)
   - Production: Fine-grained tokens (specific permissions)

3. **Personal vs Organization Tokens:**
   - Personal tokens: For individual development
   - Organization tokens: For shared resources
   - Never share personal tokens

---

## Team Access Control

### Adding Team Members to Organization

1. **Invite Members:**
   - Navigate to: https://huggingface.co/organizations/kwanzaa-project/settings/members
   - Click "Invite member"
   - Enter email address
   - Select role (see roles below)

2. **Member Roles:**

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full control | Project leads, DevOps |
| **Write** | Create/modify repos | ML engineers, researchers |
| **Read** | View private repos | QA, product managers |

3. **Role Assignment Guidelines:**
   - **Admin:** 2-3 people maximum
   - **Write:** Active contributors and trainers
   - **Read:** Stakeholders and reviewers

### Repository-Level Permissions

1. **Private Repository Access:**
   - Organization members have automatic access based on role
   - External collaborators require explicit invitation

2. **Granular Permissions:**
   ```
   Repository: kwanzaa-v1-olmo
     - Admin: Can delete, transfer ownership
     - Write: Can push models, update model cards
     - Read: Can download and use models
   ```

### External Collaborator Management

For contractors or external contributors:

1. **Create time-limited invitations:**
   - Set expiration date
   - Limit to specific repositories
   - Use Read-only access by default

2. **Offboarding Procedure:**
   - Remove from organization
   - Revoke repository access
   - Ensure tokens are revoked
   - Document access removal

---

## Repository Management

### Creating Model Repositories

#### Step 1: Create Repository

1. **Via Web Interface:**
   - Navigate to: https://huggingface.co/new
   - Select model repository type
   - Configure:
     ```
     Owner: kwanzaa-project
     Repository name: kwanzaa-v1-olmo
     Visibility: Private (during development)
     License: Apache 2.0
     ```

2. **Via CLI:**
   ```bash
   # Install HuggingFace CLI
   pip install huggingface_hub

   # Login
   huggingface-cli login

   # Create repository
   huggingface-cli repo create kwanzaa-v1-olmo \
     --type model \
     --organization kwanzaa-project \
     --private
   ```

#### Step 2: Configure Repository

1. **Add Model Card (README.md):**

```markdown
---
language:
- en
license: apache-2.0
tags:
- historical-qa
- citations
- cultural-ai
- peft
- lora
base_model: ai2/OLMo-7B-Instruct
datasets:
- kwanzaa-project/kwanzaa-primary-sources-v1
---

# Kwanzaa v1 OLMo Adapter

Culturally-aware historical question answering adapter trained on OLMo-7B-Instruct.

## Model Description

This adapter specializes in:
- Historical question answering with primary source citations
- Culturally sensitive responses about African and African-American history
- Kwanzaa traditions and principles
- JSON-structured outputs with source attribution

## Intended Use

**Primary Use Cases:**
- Educational platforms
- Historical research assistants
- Cultural education tools

**Out-of-Scope:**
- General-purpose chat
- Real-time news
- Medical or legal advice

## Training Details

- **Base Model:** ai2/OLMo-7B-Instruct
- **Adapter Type:** QLoRA
- **Training Data:** 50,000+ curated Q&A pairs
- **Evaluation Metrics:** See compatibility report

## Citation

```bibtex
@software{kwanzaa_v1_olmo,
  author = {AINative Studio},
  title = {Kwanzaa v1 OLMo Adapter},
  year = {2026},
  url = {https://huggingface.co/kwanzaa-project/kwanzaa-v1-olmo}
}
```
```

2. **Configure Repository Settings:**
   - Add topics/tags: `historical-qa`, `cultural-ai`, `peft`, `lora`
   - Set up DOI (optional, for academic citation)
   - Enable discussions (for community feedback)

### Repository Visibility Strategy

**Development Phase:**
```
Status: Private
Access: Organization members only
Purpose: Internal testing and validation
```

**Beta Phase:**
```
Status: Private
Access: Organization + invited beta testers
Purpose: Limited external validation
```

**Release Phase:**
```
Status: Public
Access: Open to all
Purpose: Community use and contributions
```

### Versioning Strategy

**Semantic Versioning for Adapters:**
```
kwanzaa-v{MAJOR}.{MINOR}-{BASE_MODEL}

Examples:
- kwanzaa-v1.0-olmo (Initial release)
- kwanzaa-v1.1-olmo (Minor improvements)
- kwanzaa-v2.0-olmo (Major architecture change)
```

**Repository Tags:**
```bash
# Tag releases in git
git tag -a v1.0.0 -m "Release v1.0.0 - OLMo adapter"
git push origin v1.0.0

# HuggingFace automatically creates release from tags
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Invalid authentication token"

**Symptoms:**
- Cannot download models
- Authentication errors in logs

**Solutions:**
1. Verify token is correctly set in environment:
   ```bash
   echo $HF_TOKEN
   # Should output: hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

2. Check token has not expired:
   - Visit: https://huggingface.co/settings/tokens
   - Verify expiration date

3. Ensure token has correct permissions:
   - Read token for downloads
   - Write token for uploads

#### Issue 2: "Access denied to gated model"

**Symptoms:**
- Cannot access LLaMA or other gated models
- 403 Forbidden errors

**Solutions:**
1. Request access to gated model:
   - Visit model page (e.g., https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)
   - Click "Request access"
   - Fill out form and accept terms
   - Wait for approval (usually 1-24 hours)

2. Verify token has access:
   - Use token AFTER access granted
   - May need to regenerate token

#### Issue 3: "Organization not found"

**Symptoms:**
- Cannot push to organization repository
- 404 errors on organization pages

**Solutions:**
1. Verify organization name:
   ```bash
   # Correct format
   kwanzaa-project/kwanzaa-v1-olmo

   # NOT
   kwanzaa_project/kwanzaa-v1-olmo
   ```

2. Check organization membership:
   - Visit: https://huggingface.co/organizations/kwanzaa-project/settings/members
   - Confirm your account is listed

3. Verify repository exists:
   - Navigate to organization page
   - Check repository list

#### Issue 4: "Token leaked in git history"

**Symptoms:**
- Accidentally committed token to git

**Solutions:**
1. **IMMEDIATE: Revoke compromised token**
2. Remove from git history:
   ```bash
   # Use git-filter-repo (recommended)
   pip install git-filter-repo
   git filter-repo --invert-paths --path .env

   # Or use BFG Repo Cleaner
   java -jar bfg.jar --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```
3. Force push to remote (if pushed):
   ```bash
   git push origin --force --all
   ```
4. Generate new token
5. Notify team of token rotation

### Getting Help

**HuggingFace Support:**
- Documentation: https://huggingface.co/docs
- Forum: https://discuss.huggingface.co
- Discord: https://discord.gg/huggingface
- Email: support@huggingface.co

**Internal Support:**
- Slack: #ml-engineering channel
- Documentation: This guide
- Team lead: Check team roster

---

## Verification Checklist

Before proceeding to adapter training, verify:

- [ ] Personal HuggingFace account created
- [ ] Two-factor authentication enabled
- [ ] Organization created (`kwanzaa-project`)
- [ ] Organization profile configured
- [ ] Read token generated and tested
- [ ] Write token generated and stored securely
- [ ] Fine-grained token created for CI/CD (if applicable)
- [ ] `.env` file configured with HF_TOKEN
- [ ] `.env` is in `.gitignore`
- [ ] GitHub secrets configured (if using CI/CD)
- [ ] Team members invited to organization
- [ ] Token rotation schedule documented
- [ ] Emergency revocation procedure understood

---

## Next Steps

After completing HuggingFace setup:

1. **Request Access to Gated Models:**
   - LLaMA: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
   - Mistral: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
   - DeepSeek: https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat

2. **Test Model Downloads:**
   ```bash
   python -c "from transformers import AutoModel; AutoModel.from_pretrained('ai2/OLMo-7B-Instruct')"
   ```

3. **Proceed to Adapter Training:**
   - See: [Adapter Training Guide](adapter-training-guide.md)
   - Start with quick-start: [Quick Start](quick-start.md)

4. **Set Up CI/CD Pipelines:**
   - Configure GitHub Actions with HF tokens
   - Test automated model publishing

---

## References

### External Documentation
- [HuggingFace Hub Documentation](https://huggingface.co/docs/hub/index)
- [Token Management Guide](https://huggingface.co/docs/hub/security-tokens)
- [Organization Guide](https://huggingface.co/docs/hub/organizations)
- [Model Cards Specification](https://huggingface.co/docs/hub/model-cards)

### Internal Documentation
- [Adapter Training Guide](adapter-training-guide.md)
- [Adapter Compatibility Testing](adapter-compatibility-testing-guide.md)
- [Dataset Preparation](dataset-preparation.md)
- [Quick Start Guide](quick-start.md)

### Project Links
- **Issue #36:** E3A-US2 - Create Hugging Face Account & Org
- **Epic 3A:** HuggingFace Environment & Prerequisites
- **GitHub Repository:** https://github.com/AINative-Studio/kwanzaa
- **HuggingFace Organization:** https://huggingface.co/kwanzaa-project

---

## Appendix

### A. Token Permission Matrix

| Operation | Read | Write | Fine-grained (Custom) |
|-----------|------|-------|-----------------------|
| Download public models | Yes | Yes | Configurable |
| Download gated models | Yes (if approved) | Yes | Configurable |
| Download private org models | Yes | Yes | Configurable |
| Upload models | No | Yes | Configurable |
| Delete models | No | No | Configurable |
| Manage org members | No | No | No |
| Modify repo settings | No | No | Configurable |

### B. Example CI/CD Integration

**GitHub Actions Workflow:**

```yaml
name: Publish Adapter to HuggingFace

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install huggingface_hub transformers peft

      - name: Publish to HuggingFace Hub
        env:
          HF_TOKEN: ${{ secrets.HUGGINGFACE_TOKEN }}
        run: |
          python scripts/publish_adapter.py \
            --adapter-path ./models/kwanzaa-v1-olmo \
            --repo-name kwanzaa-project/kwanzaa-v1-olmo \
            --private
```

### C. Emergency Contact Information

**If tokens are compromised:**

1. Revoke immediately: https://huggingface.co/settings/tokens
2. Notify team lead
3. Generate new tokens
4. Update all systems
5. Document incident

**Escalation Path:**
- Level 1: Team lead
- Level 2: Security team
- Level 3: HuggingFace support

---

**Document Version:** 1.0.0
**Last Updated:** January 16, 2026
**Maintained By:** AINative Studio ML Engineering Team
**Status:** Active

---

**End of HuggingFace Setup Guide**
