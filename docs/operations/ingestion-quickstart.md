# Ingestion Jobs Quick Start

## Prerequisites

1. **Environment Variables**
   ```bash
   export ZERODB_API_KEY="your-api-key"
   export ZERODB_PROJECT_ID="your-project-id"
   ```

2. **Optional Notifications**
   ```bash
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
   export NOTIFICATION_WEBHOOK="https://your-webhook.com/..."
   export NOTIFICATION_EMAIL="team@example.com"
   ```

## Quick Commands

### Run Locally (Dev)

```bash
# Basic run
./scripts/manual_trigger.sh run --environment dev

# With options
./scripts/manual_trigger.sh run --environment dev --full-refresh
./scripts/manual_trigger.sh run --environment dev --source "Library of Congress"
./scripts/manual_trigger.sh run --environment dev --dry-run
```

### Check Status

```bash
./scripts/manual_trigger.sh status
```

### View Logs

```bash
./scripts/manual_trigger.sh logs run_20250116_120000_12345
```

### Trigger via GitHub Actions

```bash
# Install GitHub CLI first: https://cli.github.com/
gh workflow run daily-ingestion.yml \
  --ref main \
  --raw-field environment=staging \
  --raw-field full_refresh=false
```

## Common Workflows

### Initial Setup

```bash
# 1. Configure environment
export ZERODB_API_KEY="your-key"
export ZERODB_PROJECT_ID="your-project"

# 2. Test dry run
./scripts/manual_trigger.sh run --environment dev --dry-run

# 3. Run first ingestion
./scripts/manual_trigger.sh run --environment dev

# 4. Check results
./scripts/manual_trigger.sh status
```

### Daily Operations

```bash
# Check yesterday's run
./scripts/manual_trigger.sh status

# Re-run if needed
./scripts/manual_trigger.sh run --environment prod

# View logs for debugging
./scripts/manual_trigger.sh logs <run_id>
```

### Troubleshooting

```bash
# Force full refresh
./scripts/manual_trigger.sh run --full-refresh

# Process specific source
./scripts/manual_trigger.sh run --source "Source Name"

# Check logs for errors
grep ERROR logs/ingestion/*.log | tail -20
```

## GitHub Actions Setup

1. **Add Secrets** (Settings → Secrets and variables → Actions)
   - `ZERODB_API_KEY_DEV`
   - `ZERODB_PROJECT_ID_DEV`
   - `ZERODB_API_KEY_STAGING`
   - `ZERODB_PROJECT_ID_STAGING`
   - `ZERODB_API_KEY_PROD`
   - `ZERODB_PROJECT_ID_PROD`
   - Optional: `SLACK_WEBHOOK_URL`, `NOTIFICATION_WEBHOOK`

2. **Enable Workflow**
   - Go to Actions tab
   - Enable workflows if disabled
   - Workflow runs daily at 2 AM UTC automatically

3. **Manual Trigger**
   - Actions → Daily Ingestion Job → Run workflow
   - Select options and run

## File Structure

```
kwanzaa/
├── scripts/
│   ├── daily_ingestion.sh          # Main orchestrator
│   ├── manual_trigger.sh           # CLI tool
│   └── ingestion/                  # Helper scripts
│       ├── init_run.py
│       ├── ingest_metadata.py
│       ├── expand_fulltext.py
│       ├── finalize_run.py
│       └── send_notification.py
├── data/
│   └── manifests/
│       └── first_fruits_manifest.json  # Source definitions
├── logs/
│   └── ingestion/                  # Run logs and metadata
└── .github/
    └── workflows/
        └── daily-ingestion.yml     # GitHub Actions
```

## Next Steps

- [Complete Documentation](daily-ingestion-jobs.md)
- [Manifest Configuration](../planning/technical-ingestion.md)
- [Troubleshooting Guide](daily-ingestion-jobs.md#troubleshooting)
