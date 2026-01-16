#!/bin/bash
###############################################################################
# Manual Ingestion Trigger Script
#
# This script provides a convenient CLI for manually triggering ingestion jobs
# with various options and configurations.
#
# Usage:
#   ./scripts/manual_trigger.sh [command] [options]
#
# Commands:
#   run              Run ingestion job locally
#   trigger-github   Trigger GitHub Actions workflow
#   status          Check status of recent runs
#   logs            View logs from recent run
#   help            Show this help message
#
# Examples:
#   ./scripts/manual_trigger.sh run --environment dev
#   ./scripts/manual_trigger.sh run --environment staging --full-refresh
#   ./scripts/manual_trigger.sh run --source "Library of Congress"
#   ./scripts/manual_trigger.sh trigger-github --environment prod
#   ./scripts/manual_trigger.sh status
#   ./scripts/manual_trigger.sh logs run_20250116_120000_12345
#
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

###############################################################################
# Helper Functions
###############################################################################

show_help() {
    grep "^#" "$0" | tail -n +2 | sed 's/^# //'
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

###############################################################################
# Command: Run locally
###############################################################################

cmd_run() {
    log_info "Running ingestion job locally..."

    # Forward all arguments to daily_ingestion.sh
    "${SCRIPT_DIR}/daily_ingestion.sh" --manual "$@"
}

###############################################################################
# Command: Trigger GitHub Actions
###############################################################################

cmd_trigger_github() {
    log_info "Triggering GitHub Actions workflow..."

    local environment="dev"
    local full_refresh="false"
    local dry_run="false"
    local specific_source=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                environment="$2"
                shift 2
                ;;
            --full-refresh)
                full_refresh="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            --source)
                specific_source="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                return 1
                ;;
        esac
    done

    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log_info "Install it from: https://cli.github.com/"
        return 1
    fi

    # Build inputs JSON
    local inputs="{\"environment\":\"${environment}\",\"full_refresh\":${full_refresh},\"dry_run\":${dry_run}"
    if [ -n "${specific_source}" ]; then
        inputs="${inputs},\"specific_source\":\"${specific_source}\""
    fi
    inputs="${inputs}}"

    log_info "Triggering workflow with inputs:"
    echo "${inputs}" | jq '.'

    # Trigger workflow
    gh workflow run daily-ingestion.yml \
        --ref main \
        --json "${inputs}"

    log_info "Workflow triggered successfully"
    log_info "Check status with: gh run list --workflow=daily-ingestion.yml"
}

###############################################################################
# Command: Check status
###############################################################################

cmd_status() {
    log_info "Checking status of recent ingestion runs..."

    local log_dir="${PROJECT_ROOT}/logs/ingestion"

    if [ ! -d "${log_dir}" ]; then
        log_warn "No log directory found: ${log_dir}"
        return 0
    fi

    # List recent final metadata files
    local files=$(find "${log_dir}" -name "*_final.json" -type f -mtime -7 | sort -r)

    if [ -z "${files}" ]; then
        log_info "No recent runs found (last 7 days)"
        return 0
    fi

    echo ""
    echo "Recent Runs (last 7 days):"
    echo "=========================="

    while IFS= read -r file; do
        if [ -f "${file}" ]; then
            local run_id=$(basename "${file}" | sed 's/_final.json//')
            local status=$(jq -r '.status // "unknown"' "${file}")
            local environment=$(jq -r '.environment // "unknown"' "${file}")
            local started_at=$(jq -r '.started_at // "unknown"' "${file}")
            local duration=$(jq -r '.duration_seconds // 0' "${file}")

            # Color code status
            local status_colored
            case "${status}" in
                completed)
                    status_colored="${GREEN}${status}${NC}"
                    ;;
                failed)
                    status_colored="${RED}${status}${NC}"
                    ;;
                partial)
                    status_colored="${YELLOW}${status}${NC}"
                    ;;
                *)
                    status_colored="${status}"
                    ;;
            esac

            echo ""
            echo -e "Run ID: ${BLUE}${run_id}${NC}"
            echo -e "  Status: ${status_colored}"
            echo "  Environment: ${environment}"
            echo "  Started: ${started_at}"
            echo "  Duration: ${duration}s"

            # Show statistics
            local docs_processed=$(jq -r '.documents_processed // 0' "${file}")
            local chunks_created=$(jq -r '.chunks_created // 0' "${file}")
            local vectors_upserted=$(jq -r '.vectors_upserted // 0' "${file}")

            if [ "${docs_processed}" -gt 0 ]; then
                echo "  Documents: ${docs_processed}"
                echo "  Chunks: ${chunks_created}"
                echo "  Vectors: ${vectors_upserted}"
            fi
        fi
    done <<< "${files}"

    echo ""
}

###############################################################################
# Command: View logs
###############################################################################

cmd_logs() {
    local run_id="${1:-}"

    if [ -z "${run_id}" ]; then
        log_error "Run ID required"
        log_info "Usage: $0 logs <run_id>"
        log_info ""
        log_info "Available runs:"
        cmd_status
        return 1
    fi

    local log_dir="${PROJECT_ROOT}/logs/ingestion"
    local log_file="${log_dir}/${run_id}.log"

    if [ ! -f "${log_file}" ]; then
        log_error "Log file not found: ${log_file}"
        return 1
    fi

    log_info "Viewing logs for run: ${run_id}"
    echo ""

    # Use less if available, otherwise cat
    if command -v less &> /dev/null; then
        less "${log_file}"
    else
        cat "${log_file}"
    fi
}

###############################################################################
# Command: Clean old logs
###############################################################################

cmd_clean() {
    local days="${1:-30}"

    log_info "Cleaning logs older than ${days} days..."

    local log_dir="${PROJECT_ROOT}/logs/ingestion"

    if [ ! -d "${log_dir}" ]; then
        log_warn "No log directory found"
        return 0
    fi

    # Find and remove old files
    local count=$(find "${log_dir}" -type f -mtime +${days} | wc -l)

    if [ "${count}" -eq 0 ]; then
        log_info "No logs to clean"
        return 0
    fi

    log_info "Found ${count} files to remove"
    find "${log_dir}" -type f -mtime +${days} -delete

    log_info "Cleanup complete"
}

###############################################################################
# Main Command Router
###############################################################################

main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    local command="$1"
    shift

    case "${command}" in
        run)
            cmd_run "$@"
            ;;
        trigger-github)
            cmd_trigger_github "$@"
            ;;
        status)
            cmd_status "$@"
            ;;
        logs)
            cmd_logs "$@"
            ;;
        clean)
            cmd_clean "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: ${command}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
