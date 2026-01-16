# HuggingFace Organization Recommendations for Kwanzaa

Decision guide for creating and managing HuggingFace organization for the Kwanzaa project.

## Executive Summary

**Recommendation**: Create dedicated `kwanzaa-project` organization on HuggingFace

**Rationale**:
- Clear project identity and branding
- Simplified access control and permissions management
- Professional appearance for public releases
- Isolated from other AINative projects
- Easier to manage model versioning and releases

**Estimated Setup Time**: 15-20 minutes
**Ongoing Maintenance**: Minimal (monthly review)

## Options Analysis

### Option 1: Create Dedicated Organization (Recommended)

**Organization Name**: `kwanzaa-project`

#### Pros

1. **Clear Ownership**
   - All models clearly belong to Kwanzaa project
   - Easier to track project assets
   - Professional branding

2. **Simplified Access Control**
   - Grant permissions specific to this project
   - No confusion with other projects
   - Easier onboarding/offboarding

3. **Better Organization**
   - All related models in one place
   - Consistent naming conventions
   - Dedicated model cards and documentation

4. **Professional Appearance**
   - `kwanzaa-project/kwanzaa-llama-v1` vs `ainativestudio/kwanzaa-llama-v1`
   - More discoverable by community
   - Better for academic citations

5. **Flexibility**
   - Can make public when ready
   - Control over visibility per repository
   - Independent growth trajectory

#### Cons

1. **Additional Setup Required**
   - Need to create organization (15 minutes)
   - Configure organization settings
   - Invite team members

2. **Separate Management**
   - Another organization to maintain
   - Separate billing (if upgrade needed)

3. **Less Cross-Project Synergy**
   - Models separated from other AINative work
   - Can't easily share with other projects

#### Naming Convention with Dedicated Organization

```
Organization: kwanzaa-project
Models: kwanzaa-project/kwanzaa-{base-model}-{version}
Datasets: kwanzaa-project/kwanzaa-{dataset-type}-{version}

Examples:
- kwanzaa-project/kwanzaa-llama-3.2-1b-v1
- kwanzaa-project/kwanzaa-olmo-7b-v1
- kwanzaa-project/kwanzaa-primary-sources-v1
- kwanzaa-project/kwanzaa-qa-dataset-v1
```

#### Cost Analysis

| Tier | Cost | Storage | Features |
|------|------|---------|----------|
| Free | $0/mo | 50GB | Perfect for development |
| Pro | $9/mo | 1TB | More storage, faster downloads |
| Enterprise | Custom | Unlimited | SLA, support, SSO |

**Recommendation**: Start with Free tier (sufficient for adapters)

### Option 2: Use Personal Account

**Account Name**: `ainativestudio`

#### Pros

1. **No Setup Required**
   - Already exists
   - Token already configured
   - Can publish immediately

2. **Simpler Management**
   - One account to manage
   - No additional organization overhead

#### Cons

1. **Personal Account Limitations**
   - Models under personal name, not project
   - Harder to collaborate
   - Unclear ownership

2. **Naming Confusion**
   - `ainativestudio/kwanzaa-llama-v1` mixes personal and project identity
   - Less professional
   - Harder to find related models

3. **Access Control Issues**
   - Can't grant team access without organization
   - No fine-grained permissions
   - Single point of failure

4. **Scaling Problems**
   - Hard to transfer ownership later
   - Can't add collaborators easily
   - No team management features

**Recommendation**: Not recommended for production use

### Option 3: Use Existing AINative Organization

**Organization Name**: `ainative` (if exists)

#### Pros

1. **Existing Infrastructure**
   - If organization exists, no setup needed
   - Shared resources with other projects
   - Existing team access

2. **Cross-Project Benefits**
   - Potential model reuse
   - Shared visibility
   - Unified branding

#### Cons

1. **Mixed Identity**
   - Kwanzaa models mixed with other projects
   - Less project-specific branding
   - Harder to filter project models

2. **Complex Access Control**
   - Need to manage permissions across multiple projects
   - Risk of accidental access to other projects
   - More complex onboarding

3. **Namespace Conflicts**
   - Potential naming collisions
   - Need longer, more explicit names

**Recommendation**: Use only if `ainative` organization already exists and has clear multi-project structure

## Recommended Approach

### Phase 1: Create Organization (Week 1)

1. **Create `kwanzaa-project` Organization**
   ```
   URL: https://huggingface.co/organizations/new
   Name: kwanzaa-project
   Display Name: Kwanzaa Historical AI
   Type: Company/Team
   Visibility: Private (initially)
   ```

2. **Configure Organization Settings**
   - Add description and logo
   - Set default repository visibility to Private
   - Configure organization profile

3. **Invite Core Team**
   - Add 2-3 admins
   - Add ML engineers as writers
   - Add stakeholders as readers

### Phase 2: Repository Setup (Week 1-2)

1. **Create Model Repositories**
   ```bash
   # For each base model
   kwanzaa-project/kwanzaa-llama-3.2-1b-v1
   kwanzaa-project/kwanzaa-olmo-7b-v1
   kwanzaa-project/kwanzaa-mistral-7b-v1
   ```

2. **Create Dataset Repositories**
   ```bash
   kwanzaa-project/kwanzaa-primary-sources-v1
   kwanzaa-project/kwanzaa-qa-dataset-v1
   ```

3. **Setup Model Cards**
   - Add comprehensive README.md
   - Include training details
   - Add usage examples
   - Link to project documentation

### Phase 3: CI/CD Integration (Week 2-3)

1. **Generate Organization Token**
   - Fine-grained token with org access
   - Limited to specific repositories
   - 90-day expiration

2. **Configure GitHub Secrets**
   - Add `HF_ORG_TOKEN` secret
   - Update workflows to use organization

3. **Test Automated Publishing**
   - Test adapter upload
   - Verify permissions
   - Document process

### Phase 4: Public Release (When Ready)

1. **Prepare for Public Launch**
   - Complete model cards
   - Add licenses
   - Prepare announcement

2. **Change Visibility**
   - Review each repository
   - Change from Private to Public
   - Monitor downloads and issues

## Implementation Guide

### Creating the Organization

```bash
# Step 1: Visit HuggingFace
# https://huggingface.co/organizations/new

# Step 2: Fill out form
Organization Name: kwanzaa-project
Display Name: Kwanzaa Historical AI
Description: Cultural education AI platform specializing in African and African-American history with primary source citations

# Step 3: Configure settings
Default Repository Visibility: Private
Member Visibility: Private (members only)
Allow Discussions: Yes
```

### Adding Team Members

```bash
# Navigate to Members page
# https://huggingface.co/organizations/kwanzaa-project/settings/members

# Invite members with appropriate roles:
# - Admin: Project leads (2-3 people)
# - Write: ML engineers, researchers (5-10 people)
# - Read: Stakeholders, QA (10+ people)
```

### Creating First Repository

```bash
# Via CLI
pip install huggingface-hub
huggingface-cli login --token $HF_TOKEN

huggingface-cli repo create kwanzaa-llama-3.2-1b-v1 \
  --type model \
  --organization kwanzaa-project \
  --private

# Upload model
huggingface-cli upload kwanzaa-project/kwanzaa-llama-3.2-1b-v1 \
  ./trained_adapters/kwanzaa-llama-v1
```

### Updating Environment Variables

```bash
# Add to backend/.env
HF_ORGANIZATION=kwanzaa-project

# Add to CI/CD (GitHub Secrets)
HF_ORGANIZATION=kwanzaa-project
```

### Code Changes

Update publishing scripts to use organization:

```python
from huggingface_hub import HfApi
import os

api = HfApi(token=os.getenv("HF_TOKEN"))
org = os.getenv("HF_ORGANIZATION", "kwanzaa-project")

# Create repo in organization
repo_id = f"{org}/kwanzaa-llama-v1"
api.create_repo(
    repo_id=repo_id,
    token=os.getenv("HF_TOKEN"),
    private=True,
    repo_type="model"
)

# Upload adapter
api.upload_folder(
    folder_path="./trained_adapters/kwanzaa-llama-v1",
    repo_id=repo_id,
    token=os.getenv("HF_TOKEN")
)
```

## Team Access Matrix

| Role | Permissions | Who | Responsibilities |
|------|------------|-----|------------------|
| **Admin** | Full control | Project leads, DevOps | Manage org, add members, delete repos |
| **Write** | Create/modify repos | ML engineers | Train models, publish adapters |
| **Read** | View private repos | QA, PM, stakeholders | Review models, provide feedback |

## Repository Visibility Strategy

### Development Phase (Weeks 1-4)

```
Status: Private
Access: Organization members only
Purpose: Internal development and testing
Visibility: Organization → Private

Repositories:
- kwanzaa-project/kwanzaa-llama-3.2-1b-v1-dev
- kwanzaa-project/kwanzaa-olmo-7b-v1-dev
```

### Beta Phase (Weeks 5-8)

```
Status: Private with selected collaborators
Access: Organization + invited beta testers
Purpose: External validation and feedback
Visibility: Organization → Private + Collaborators

Repositories:
- kwanzaa-project/kwanzaa-llama-3.2-1b-v1-beta
```

### Production Phase (Week 9+)

```
Status: Public
Access: Open to all
Purpose: Community use and contributions
Visibility: Organization → Public

Repositories:
- kwanzaa-project/kwanzaa-llama-3.2-1b-v1
- kwanzaa-project/kwanzaa-olmo-7b-v1
```

## Governance and Policies

### Model Publishing Policy

1. **Internal Review Required**
   - All models reviewed by team before publishing
   - Check for bias, quality, documentation

2. **Model Card Mandatory**
   - Complete README.md with usage, limitations, training details
   - Include evaluation metrics
   - Add licensing information

3. **Versioning Required**
   - Semantic versioning for all releases
   - Tag releases in git
   - Document changes between versions

### Access Control Policy

1. **Principle of Least Privilege**
   - Grant minimum necessary permissions
   - Review access quarterly
   - Remove access for inactive members

2. **Token Management**
   - Personal tokens for development
   - Organization tokens for CI/CD
   - Rotate tokens every 90 days

3. **Audit Trail**
   - Log all model publishes
   - Track access changes
   - Review activity monthly

## Migration Plan (If Needed)

If models already exist under personal account:

### Step 1: Prepare Organization

1. Create organization
2. Setup repositories
3. Configure permissions

### Step 2: Transfer Models

```bash
# Option 1: Re-upload to organization
huggingface-cli upload kwanzaa-project/kwanzaa-llama-v1 \
  ./local_copy

# Option 2: Request transfer (contact HuggingFace support)
# Email: support@huggingface.co
# Subject: Transfer repository to organization
```

### Step 3: Update References

1. Update documentation
2. Update CI/CD pipelines
3. Notify team of new locations
4. Archive old repositories

### Step 4: Deprecate Old Locations

1. Add deprecation notice to old model cards
2. Redirect users to new organization
3. Set old repos to read-only
4. Delete after migration period (30 days)

## Success Metrics

Track organization health:

### Quantitative Metrics

- **Model Downloads**: Track usage
- **Repository Stars**: Community interest
- **Active Contributors**: Team engagement
- **Model Updates**: Release frequency

### Qualitative Metrics

- **Documentation Quality**: Complete model cards
- **Community Feedback**: Issues, discussions
- **Team Satisfaction**: Ease of use
- **Security Posture**: No token leaks, proper access control

## Maintenance Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Review access permissions | Quarterly | Admin |
| Rotate organization tokens | Every 90 days | DevOps |
| Audit model usage | Monthly | ML Lead |
| Update model cards | Per release | Model Owner |
| Review repository visibility | Before each release | Project Lead |
| Backup model artifacts | Weekly | DevOps |

## Decision Matrix

Use this matrix to finalize your decision:

| Criterion | Personal Account | Dedicated Org | Shared Org | Weight |
|-----------|-----------------|---------------|------------|--------|
| Professional Appearance | 2/10 | 10/10 | 6/10 | High |
| Access Control | 2/10 | 10/10 | 7/10 | High |
| Setup Complexity | 10/10 | 7/10 | 9/10 | Low |
| Scalability | 3/10 | 10/10 | 7/10 | High |
| Maintenance Overhead | 10/10 | 8/10 | 6/10 | Medium |
| Team Collaboration | 2/10 | 10/10 | 8/10 | High |
| Cost | 10/10 | 10/10 | 10/10 | Low |
| **Weighted Score** | **3.8/10** | **9.4/10** | **7.2/10** | - |

**Winner**: Dedicated Organization (`kwanzaa-project`)

## Next Steps

1. **Immediate (This Week)**
   - [ ] Create `kwanzaa-project` organization
   - [ ] Configure organization settings
   - [ ] Invite core team members
   - [ ] Update `backend/.env` with `HF_ORGANIZATION=kwanzaa-project`

2. **Short Term (Next 2 Weeks)**
   - [ ] Create first model repository
   - [ ] Write comprehensive model card
   - [ ] Test adapter publishing workflow
   - [ ] Generate organization token for CI/CD

3. **Medium Term (Next Month)**
   - [ ] Publish first adapter to organization
   - [ ] Setup automated publishing via GitHub Actions
   - [ ] Document model versioning strategy
   - [ ] Review and refine access controls

4. **Long Term (Next Quarter)**
   - [ ] Plan public release
   - [ ] Prepare marketing materials
   - [ ] Change visibility to public
   - [ ] Monitor community engagement

## References

- [HuggingFace Organizations Guide](https://huggingface.co/docs/hub/organizations)
- [Repository Visibility Settings](https://huggingface.co/docs/hub/repositories-settings)
- [Team Collaboration Best Practices](https://huggingface.co/docs/hub/repositories-settings#team-collaboration)
- [Model Cards Guide](https://huggingface.co/docs/hub/model-cards)

## Support

For questions or issues:
- HuggingFace Support: support@huggingface.co
- Internal: Slack #ml-engineering channel
- Documentation: This guide and main setup guide

---

**Last Updated**: January 16, 2026
**Document Owner**: ML Engineering Team
**Review Date**: April 16, 2026
