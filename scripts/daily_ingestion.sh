#!/bin/bash
###############################################################################
# Daily Ingestion Job Orchestrator
#
# This script orchestrates the complete ingestion pipeline for the Kwanzaa
# "First Fruits" corpus, including:
# - Metadata ingestion (E4-US2)
# - Full-text expansion for P0 sources (E4-US3)
# - Incremental processing with change detection
# - Comprehensive logging and error handling
# - Job monitoring and notifications
#
# Usage:
#   ./scripts/daily_ingestion.sh [options]
#
# Options:
#   --environment <env>    Environment: dev, staging, prod (default: dev)
#   --full-refresh         Force full refresh, ignore checkpoints
#   --dry-run              Simulate run without making changes
#   --source <name>        Process only specific source
#   --manual               Mark as manual trigger (vs scheduled)
#   --help                 Show this help message
#
# Environment Variables:
#   ZERODB_API_KEY         ZeroDB API key (required)
#   ZERODB_PROJECT_ID      ZeroDB project ID (required)
#   NOTIFICATION_WEBHOOK   Webhook URL for notifications (optional)
#   NOTIFICATION_EMAIL     Email for notifications (optional)
#   SLACK_WEBHOOK_URL      Slack webhook for notifications (optional)
#
###############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/ingestion"
BACKEND_DIR="${PROJECT_ROOT}/backend"

# Default values
ENVIRONMENT="${ENVIRONMENT:-dev}"
FULL_REFRESH=false
DRY_RUN=false
SPECIFIC_SOURCE=""
TRIGGER_TYPE="scheduled"
RUN_ID="run_$(date +%Y%m%d_%H%M%S)_$$"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

###############################################################################
# Logging Functions
###############################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "${LOG_DIR}/${RUN_ID}.log"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*" | tee -a "${LOG_DIR}/${RUN_ID}.log"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "${LOG_DIR}/${RUN_ID}.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "${LOG_DIR}/${RUN_ID}.log"
}

###############################################################################
# Validation Functions
###############################################################################

validate_environment() {
    log_info "Validating environment..."

    # Check required environment variables
    if [[ -z "${ZERODB_API_KEY:-}" ]]; then
        log_error "ZERODB_API_KEY is not set"
        return 1
    fi

    if [[ -z "${ZERODB_PROJECT_ID:-}" ]]; then
        log_error "ZERODB_PROJECT_ID is not set"
        return 1
    fi

    # Check Python availability
    if ! command -v python3 &> /dev/null; then
        log_error "python3 is not installed"
        return 1
    fi

    # Check if backend directory exists
    if [[ ! -d "${BACKEND_DIR}" ]]; then
        log_error "Backend directory not found: ${BACKEND_DIR}"
        return 1
    fi

    log_info "Environment validation passed"
    return 0
}

###############################################################################
# Setup Functions
###############################################################################

setup_logging() {
    mkdir -p "${LOG_DIR}"

    log "=========================================="
    log "Kwanzaa Daily Ingestion Job"
    log "=========================================="
    log "Run ID: ${RUN_ID}"
    log "Environment: ${ENVIRONMENT}"
    log "Trigger: ${TRIGGER_TYPE}"
    log "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    log "=========================================="
}

initialize_run_metadata() {
    log_info "Initializing run metadata in ZeroDB..."

    python3 "${SCRIPT_DIR}/ingestion/init_run.py" \
        --run-id "${RUN_ID}" \
        --environment "${ENVIRONMENT}" \
        --trigger "${TRIGGER_TYPE}" \
        --log-file "${LOG_DIR}/${RUN_ID}.log" || {
            log_error "Failed to initialize run metadata"
            return 1
        }

    log_info "Run metadata initialized"
}

###############################################################################
# Pipeline Functions
###############################################################################

run_metadata_ingestion() {
    log_info "Phase 1: Metadata Ingestion (E4-US2)"

    local start_time=$(date +%s)
    local status="completed"

    if [[ "${DRY_RUN}" == "true" ]]; then
        log_warn "DRY RUN: Skipping actual metadata ingestion"
        return 0
    fi

    # Run metadata ingestion script
    if python3 "${SCRIPT_DIR}/ingestion/ingest_metadata.py" \
        --run-id "${RUN_ID}" \
        --environment "${ENVIRONMENT}" \
        --incremental "$([[ "${FULL_REFRESH}" == "false" ]] && echo "true" || echo "false")" \
        ${SPECIFIC_SOURCE:+--source "${SPECIFIC_SOURCE}"} 2>&1 | tee -a "${LOG_DIR}/${RUN_ID}.log"; then

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_info "Metadata ingestion completed in ${duration}s"
    else
        status="failed"
        log_error "Metadata ingestion failed"
        return 1
    fi
}

run_fulltext_expansion() {
    log_info "Phase 2: Full-Text Expansion for P0 Sources (E4-US3)"

    local start_time=$(date +%s)
    local status="completed"

    if [[ "${DRY_RUN}" == "true" ]]; then
        log_warn "DRY RUN: Skipping actual full-text expansion"
        return 0
    fi

    # Run full-text expansion script
    if python3 "${SCRIPT_DIR}/ingestion/expand_fulltext.py" \
        --run-id "${RUN_ID}" \
        --environment "${ENVIRONMENT}" \
        --priority "P0" \
        ${SPECIFIC_SOURCE:+--source "${SPECIFIC_SOURCE}"} 2>&1 | tee -a "${LOG_DIR}/${RUN_ID}.log"; then

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_info "Full-text expansion completed in ${duration}s"
    else
        status="failed"
        log_error "Full-text expansion failed"
        return 1
    fi
}

finalize_run() {
    log_info "Finalizing run..."

    python3 "${SCRIPT_DIR}/ingestion/finalize_run.py" \
        --run-id "${RUN_ID}" \
        --log-file "${LOG_DIR}/${RUN_ID}.log" || {
            log_error "Failed to finalize run"
            return 1
        }

    log_info "Run finalized"
}

###############################################################################
# Notification Functions
###############################################################################

send_notifications() {
    local status="$1"
    local summary="$2"

    log_info "Sending notifications..."

    python3 "${SCRIPT_DIR}/ingestion/send_notification.py" \
        --run-id "${RUN_ID}" \
        --status "${status}" \
        --summary "${summary}" \
        --log-file "${LOG_DIR}/${RUN_ID}.log" || {
            log_warn "Failed to send notifications (non-fatal)"
        }
}

###############################################################################
# Cleanup Functions
###############################################################################

cleanup() {
    log_info "Running cleanup..."

    # Compress old logs
    find "${LOG_DIR}" -name "*.log" -mtime +7 -exec gzip {} \;

    # Remove logs older than 30 days
    find "${LOG_DIR}" -name "*.log.gz" -mtime +30 -delete

    log_info "Cleanup completed"
}

health_check_ping() {
    if [[ -n "${HEALTHCHECK_URL:-}" ]]; then
        log_info "Pinging health check endpoint..."
        curl -fsS -m 10 --retry 3 "${HEALTHCHECK_URL}" || log_warn "Health check ping failed"
    fi
}

###############################################################################
# Error Handling
###############################################################################

handle_error() {
    local exit_code=$?
    local line_number=$1

    log_error "Error occurred in script at line ${line_number} (exit code: ${exit_code})"

    # Update run status to failed
    python3 "${SCRIPT_DIR}/ingestion/update_run_status.py" \
        --run-id "${RUN_ID}" \
        --status "failed" \
        --error "Script failed at line ${line_number}" 2>&1 || true

    # Send failure notification
    send_notifications "failed" "Ingestion job failed at line ${line_number}"

    exit "${exit_code}"
}

trap 'handle_error ${LINENO}' ERR

###############################################################################
# Main Execution
###############################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --full-refresh)
                FULL_REFRESH=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --source)
                SPECIFIC_SOURCE="$2"
                shift 2
                ;;
            --manual)
                TRIGGER_TYPE="manual"
                shift
                ;;
            --help)
                grep "^#" "$0" | tail -n +2 | head -n -1 | sed 's/^# //'
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

main() {
    local start_time=$(date +%s)
    local overall_status="completed"

    # Parse command line arguments
    parse_arguments "$@"

    # Setup
    setup_logging
    validate_environment || exit 1
    initialize_run_metadata || exit 1

    # Run pipeline
    log_info "Starting ingestion pipeline..."

    if run_metadata_ingestion; then
        log_info "Metadata ingestion succeeded"
    else
        overall_status="failed"
        log_error "Pipeline failed during metadata ingestion"
    fi

    if [[ "${overall_status}" == "completed" ]]; then
        if run_fulltext_expansion; then
            log_info "Full-text expansion succeeded"
        else
            overall_status="partial"
            log_warn "Pipeline partially succeeded (full-text expansion failed)"
        fi
    fi

    # Finalize
    finalize_run
    cleanup

    # Calculate duration
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))

    log "=========================================="
    log "Ingestion Job Completed"
    log "=========================================="
    log "Status: ${overall_status}"
    log "Duration: ${total_duration}s"
    log "Log: ${LOG_DIR}/${RUN_ID}.log"
    log "=========================================="

    # Send notifications
    send_notifications "${overall_status}" "Ingestion completed in ${total_duration}s"

    # Health check
    health_check_ping

    if [[ "${overall_status}" == "failed" ]]; then
        exit 1
    fi

    exit 0
}

# Execute main function
main "$@"
