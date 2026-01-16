# Daily Incremental Ingestion Jobs

## Overview

The Kwanzaa daily ingestion system automates the process of discovering, processing, and storing content from various sources into ZeroDB. This system implements the E4-US4 requirements for automated daily incremental ingestion with append-only behavior and comprehensive monitoring.

## Architecture

### Components

1. **Orchestration Script** (`scripts/daily_ingestion.sh`)
   - Main entry point for ingestion jobs
   - Handles workflow coordination
   - Manages error handling and recovery
   - Generates comprehensive logs

2. **Python Helper Scripts** (`scripts/ingestion/`)
   - `init_run.py` - Initialize run tracking
   - `ingest_metadata.py` - Metadata ingestion (E4-US2)
   - `expand_fulltext.py` - Full-text expansion (E4-US3)
   - `finalize_run.py` - Finalize and calculate statistics
   - `send_notification.py` - Send alerts and notifications
   - `update_run_status.py` - Update run status (error handling)

3. **GitHub Actions Workflow** (`.github/workflows/daily-ingestion.yml`)
   - Scheduled daily runs at 2 AM UTC
   - Manual trigger capability
   - Webhook trigger support
   - Environment-aware execution

4. **Run Tracking** (ZeroDB table: `kw_ingestion_runs`)
   - Stores metadata for each run
   - Tracks progress and statistics
   - Enables auditing and debugging

## Workflow

### Ingestion Pipeline

```
┌─────────────────┐
│  Start Job      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Initialize     │
│  Run Metadata   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 1:       │
│  Metadata       │
│  Ingestion      │
│  (E4-US2)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 2:       │
│  Full-Text      │
│  Expansion      │
│  (E4-US3)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Finalize Run   │
│  & Calculate    │
│  Statistics     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Send           │
│  Notifications  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cleanup &      │
│  Health Check   │
└─────────────────┘
```

### Phase 1: Metadata Ingestion

Discovers and stores metadata for all enabled sources:

- Loads ingestion manifest
- Filters sources based on configuration
- Discovers records using source-specific methods (API, bulk, scrape)
- Stores metadata with proper provenance
- Supports incremental processing (skips unchanged records)

### Phase 2: Full-Text Expansion

Expands P0 priority sources to full text:

- Loads metadata from Phase 1
- Filters by priority (P0 only for MVP)
- Fetches full text content
- Chunks content for retrieval
- Generates embeddings
- Stores vectors in appropriate ZeroDB namespaces

## Usage

### Local Execution

#### Basic Run

```bash
./scripts/daily_ingestion.sh --environment dev --manual
```

#### Full Refresh (Ignore Checkpoints)

```bash
./scripts/daily_ingestion.sh --environment dev --full-refresh --manual
```

#### Process Specific Source

```bash
./scripts/daily_ingestion.sh --environment dev --source "Library of Congress" --manual
```

#### Dry Run (No Changes)

```bash
./scripts/daily_ingestion.sh --environment dev --dry-run --manual
```

### Manual Trigger CLI

The `manual_trigger.sh` script provides convenient commands for managing ingestion jobs:

#### Run Locally

```bash
./scripts/manual_trigger.sh run --environment dev
./scripts/manual_trigger.sh run --environment staging --full-refresh
./scripts/manual_trigger.sh run --source "Library of Congress"
```

#### Trigger GitHub Actions

```bash
./scripts/manual_trigger.sh trigger-github --environment prod
./scripts/manual_trigger.sh trigger-github --environment staging --full-refresh
```

#### Check Status

```bash
./scripts/manual_trigger.sh status
```

#### View Logs

```bash
./scripts/manual_trigger.sh logs run_20250116_120000_12345
```

#### Clean Old Logs

```bash
./scripts/manual_trigger.sh clean 30  # Remove logs older than 30 days
```

### GitHub Actions

#### Scheduled Runs

Automatic daily runs at 2 AM UTC on the `main` branch in production environment.

#### Manual Trigger

1. Go to GitHub Actions tab
2. Select "Daily Ingestion Job" workflow
3. Click "Run workflow"
4. Configure options:
   - Environment (dev/staging/prod)
   - Full refresh (true/false)
   - Specific source (optional)
   - Dry run (true/false)
5. Click "Run workflow"

#### Webhook Trigger

Trigger via API:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/AINative-Studio/kwanzaa/dispatches \
  -d '{"event_type":"trigger-ingestion","client_payload":{"environment":"staging"}}'
```

## Configuration

### Environment Variables

#### Required

- `ZERODB_API_KEY` - ZeroDB API key for authentication
- `ZERODB_PROJECT_ID` - ZeroDB project identifier

#### Optional

- `NOTIFICATION_WEBHOOK` - Webhook URL for status notifications
- `SLACK_WEBHOOK_URL` - Slack webhook for team notifications
- `NOTIFICATION_EMAIL` - Email addresses for notifications (comma-separated)
- `HEALTHCHECK_URL` - Health check endpoint to ping on success

### GitHub Secrets

Configure these secrets in GitHub repository settings:

#### Development
- `ZERODB_API_KEY_DEV`
- `ZERODB_PROJECT_ID_DEV`

#### Staging
- `ZERODB_API_KEY_STAGING`
- `ZERODB_PROJECT_ID_STAGING`

#### Production
- `ZERODB_API_KEY_PROD`
- `ZERODB_PROJECT_ID_PROD`

#### Notifications (Optional)
- `SLACK_WEBHOOK_URL`
- `NOTIFICATION_WEBHOOK`
- `NOTIFICATION_EMAIL`
- `HEALTHCHECK_URL`

### Ingestion Manifest

The ingestion manifest (`data/manifests/first_fruits_manifest.json`) defines all sources and their configuration:

```json
{
  "version": "1.0.0",
  "sources": [
    {
      "source_name": "Library of Congress",
      "source_type": "archive",
      "base_url": "https://www.loc.gov/api/",
      "access_method": "api",
      "license": "Public Domain",
      "priority": "P0",
      "default_namespace": "kwanzaa_primary_sources",
      "enabled": true,
      "tags": ["government", "archive"],
      "query_templates": []
    }
  ],
  "global_config": {
    "max_parallel_sources": 3,
    "default_rate_limit": 1.0,
    "chunk_size": 1000,
    "chunk_overlap": 200
  },
  "namespaces": {
    "kwanzaa_primary_sources": {
      "description": "Primary sources and archival records"
    }
  }
}
```

## Monitoring

### Run Tracking

Each run creates several tracking files in `logs/ingestion/`:

- `{run_id}_metadata.json` - Initial run metadata
- `{run_id}_progress.json` - Metadata ingestion progress
- `{run_id}_expansion.json` - Full-text expansion progress
- `{run_id}_final.json` - Final statistics and status
- `{run_id}.log` - Complete execution log

### Run Status

Run status values:

- `pending` - Run initialized, not started
- `running` - Currently executing
- `completed` - Successfully completed
- `partial` - Partially successful (some sources failed)
- `failed` - Failed to complete

### Notifications

Notifications are sent via configured channels:

#### Success Notification

```
✅ Kwanzaa Ingestion Job COMPLETED

Run ID: run_20250116_020000_12345
Environment: prod
Summary: Ingestion completed in 1234s

Statistics:
  • Documents discovered: 1500
  • Documents processed: 1500
  • Chunks created: 15000
  • Vectors upserted: 15000

Duration: 20m 34s
```

#### Failure Notification

```
❌ Kwanzaa Ingestion Job FAILED

Run ID: run_20250116_020000_12345
Environment: prod
Summary: Ingestion job failed at line 245

Statistics:
  • Documents discovered: 1500
  • Documents processed: 800
  • Documents failed: 700
  • Chunks created: 8000
  • Vectors upserted: 8000

Duration: 10m 15s
```

### GitHub Actions Artifacts

Each workflow run uploads:

1. **Ingestion Logs** (30-day retention)
   - Complete execution logs
   - Searchable via GitHub UI

2. **Run Metadata** (90-day retention)
   - JSON metadata files
   - Statistics and status information

## Troubleshooting

### Common Issues

#### 1. Run Fails to Initialize

**Symptoms:**
- Error: "ZERODB_API_KEY is not set"
- Run doesn't start

**Solution:**
```bash
# Check environment variables
echo $ZERODB_API_KEY
echo $ZERODB_PROJECT_ID

# Set if missing
export ZERODB_API_KEY="your-key"
export ZERODB_PROJECT_ID="your-project-id"
```

#### 2. Metadata Ingestion Fails

**Symptoms:**
- Phase 1 fails with source errors
- "Failed to discover records" messages

**Solution:**
```bash
# Check manifest configuration
cat data/manifests/first_fruits_manifest.json | jq '.sources'

# Test specific source
./scripts/manual_trigger.sh run --source "Source Name" --dry-run
```

#### 3. Full-Text Expansion Fails

**Symptoms:**
- Phase 2 fails
- Partial status

**Solution:**
```bash
# Check logs for specific errors
./scripts/manual_trigger.sh logs run_XXXXXX | grep ERROR

# Retry with full refresh
./scripts/manual_trigger.sh run --full-refresh
```

#### 4. Notifications Not Sending

**Symptoms:**
- Job completes but no notifications received

**Solution:**
```bash
# Verify webhook URLs
curl -X POST ${SLACK_WEBHOOK_URL} \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'

# Check notification script
python3 scripts/ingestion/send_notification.py --help
```

### Debug Mode

Enable verbose logging:

```bash
# Add debug flag to script
bash -x ./scripts/daily_ingestion.sh --environment dev --manual
```

### Log Analysis

View recent errors:

```bash
# Show errors from recent runs
grep -r "ERROR" logs/ingestion/*.log | tail -20

# Show failed runs
./scripts/manual_trigger.sh status | grep -A 5 "failed"
```

## Maintenance

### Log Rotation

Logs are automatically managed:

- Logs older than 7 days are compressed (gzip)
- Logs older than 30 days are deleted
- Manual cleanup: `./scripts/manual_trigger.sh clean 30`

### Database Maintenance

The `kw_ingestion_runs` table should be periodically cleaned:

```python
# Archive runs older than 90 days
# (Implementation depends on ZeroDB capabilities)
```

### Manifest Updates

When updating the manifest:

1. Update `data/manifests/first_fruits_manifest.json`
2. Test with dry run: `./scripts/manual_trigger.sh run --dry-run`
3. Test with specific source: `./scripts/manual_trigger.sh run --source "New Source"`
4. Deploy to production

### Schedule Updates

To change the ingestion schedule, edit `.github/workflows/daily-ingestion.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Change time here (UTC)
```

## Performance Optimization

### Parallel Processing

Adjust parallelization in manifest:

```json
{
  "global_config": {
    "max_parallel_sources": 5  // Increase for faster processing
  }
}
```

### Rate Limiting

Configure per-source rate limits:

```json
{
  "sources": [
    {
      "source_name": "Example Source",
      "rate_limit_per_second": 2.0  // Adjust based on API limits
    }
  ]
}
```

### Incremental Processing

Incremental mode (default) only processes new/changed records:

```bash
# Force full refresh when needed
./scripts/manual_trigger.sh run --full-refresh
```

## Security

### Secrets Management

- Never commit API keys or credentials
- Use environment variables or GitHub Secrets
- Rotate keys regularly
- Use separate keys per environment

### Access Control

- Restrict who can trigger production runs
- Use GitHub branch protection rules
- Enable required approvals for production deployments

### Audit Trail

All runs are logged with:

- Timestamp and trigger source
- User/system that initiated
- Environment and configuration
- Complete execution logs

## Best Practices

### Before Deploying

1. Test in development environment
2. Run with dry-run flag
3. Verify notifications work
4. Check manifest configuration
5. Review recent run history

### Monitoring Checklist

- [ ] Check daily run status
- [ ] Review error rates
- [ ] Monitor processing times
- [ ] Verify data quality
- [ ] Check notification delivery

### Incident Response

1. Check recent run status: `./scripts/manual_trigger.sh status`
2. View logs: `./scripts/manual_trigger.sh logs <run_id>`
3. Identify failed sources
4. Fix issues (manifest, API, credentials)
5. Retry: `./scripts/manual_trigger.sh run --source "Failed Source"`
6. Document incident and resolution

## Support

For issues or questions:

1. Check logs: `./scripts/manual_trigger.sh logs`
2. View status: `./scripts/manual_trigger.sh status`
3. Review this documentation
4. Check GitHub Issues
5. Contact platform team

## References

- [Data Ingestion Plan](/Users/aideveloper/kwanzaa/docs/planning/Data-Ingestion.md)
- [Technical Ingestion PRD](/Users/aideveloper/kwanzaa/docs/planning/technical-ingestion.md)
- [ZeroDB Documentation](https://docs.zerodb.ainative.io)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
