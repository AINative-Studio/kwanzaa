#!/bin/bash
#
# Pre-HuggingFace Space Push Hook
#
# This hook validates Space configuration before pushing to HuggingFace
# to prevent common build failures.
#
# Triggered when: About to push files to HuggingFace Space
#
# Exit codes:
#   0 - Validation passed, safe to push
#   1 - Validation failed, do not push
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 Pre-HuggingFace Space Push Validation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if this is a Space push
# Look for common indicators in the context
if [[ "$1" == "--space-dir" ]]; then
    SPACE_DIR="$2"
elif [[ -d "/tmp/kwanzaa-training" ]]; then
    SPACE_DIR="/tmp/kwanzaa-training"
else
    echo -e "${YELLOW}⚠️  Not a Space push, skipping validation${NC}"
    exit 0
fi

echo -e "${BLUE}Validating Space directory: $SPACE_DIR${NC}"
echo

# Run validation script
if [ -f "scripts/validate_hf_space_config.py" ]; then
    python3 scripts/validate_hf_space_config.py "$SPACE_DIR"
    VALIDATION_RESULT=$?

    if [ $VALIDATION_RESULT -eq 0 ]; then
        echo
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✅ Validation PASSED - Safe to push to HuggingFace${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        exit 0
    else
        echo
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}❌ Validation FAILED - Do NOT push${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        echo -e "${YELLOW}Fix the issues above before pushing to Space.${NC}"
        echo -e "${YELLOW}This prevents build failures and saves time.${NC}"
        echo
        exit 1
    fi
else
    echo -e "${RED}❌ Validation script not found: scripts/validate_hf_space_config.py${NC}"
    echo -e "${YELLOW}⚠️  Proceeding without validation (not recommended)${NC}"
    exit 0
fi
