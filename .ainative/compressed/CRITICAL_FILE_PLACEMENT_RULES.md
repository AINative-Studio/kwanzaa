# 🚨 CRITICAL FILE PLACEMENT RULES

## ABSOLUTE PROHIBITIONS

### FORBIDDEN LOCATIONS:
```
/path/to/project/*.md  (except README.md)
/path/to/project/src/backend/*.md
/path/to/project/AINative-website/*.md (except README.md, CODY.md)
```

### REQUIRED LOCATIONS:
- Backend docs: `/path/to/project/docs/{category}/filename.md`
- Frontend docs: `/path/to/project/AINative-website/docs/{category}/filename.md`

## SCRIPT & URL RULES

### SCRIPT PLACEMENT:
- ❌ No .sh scripts in backend
- ✅ Scripts only in: `/path/to/project/scripts/script_name.sh`

### BASE URL FORMAT:
```bash
# ✅ CORRECT
BASE_URL="https://api.ainative.studio"

# Use full paths
curl "$BASE_URL/api/v1/projects/"
```

## DOCUMENTATION CATEGORIES

### Backend Documentation Categories:

| Pattern | Destination | Example |
|---------|-------------|---------|
| `ISSUE_*`, `BUG_*` | `docs/issues/` | ISSUE_24_SUMMARY.md |
| `*_TEST*`, `QA_*` | `docs/testing/` | QA_TEST_REPORT.md |
| `AGENT_SWARM_*`, `WORKFLOW_*` | `docs/agent-swarm/` | AGENT_SWARM_WORKFLOW.md |
| `API_*`, `*_ENDPOINTS*` | `docs/api/` | API_DOCUMENTATION.md |

## ENFORCEMENT CHECKLIST

1. ✅ Check root directory status
2. ✅ Determine correct category
3. ✅ Create in correct location
4. ✅ Verify no root directory files

## CONSEQUENCES OF VIOLATIONS

- Project becomes disorganized
- Developers waste time cleaning up
- Decreased AI assistant trust
- Slowed development velocity

## VERIFICATION COMMANDS

```bash
ls /path/to/project/*.md
ls /path/to/project/src/backend/*.md
ls /path/to/project/src/backend/*.sh
```

## AI ASSISTANT RESPONSIBILITIES

- Read rules before file creation
- Follow categorization guide
- Create files in correct locations
- Never create files in root directories
- Ask if unsure about categorization

🚨 THESE RULES ARE MANDATORY AND NON-NEGOTIABLE