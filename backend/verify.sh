#!/bin/bash

# Kwanzaa Backend Verification Script
# Checks implementation completeness and runs tests

set -e

echo "=========================================="
echo "Kwanzaa Semantic Search - Verification"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check file structure
echo -e "${YELLOW}Verifying file structure...${NC}"

files=(
    "app/main.py"
    "app/core/config.py"
    "app/core/errors.py"
    "app/models/search.py"
    "app/services/search.py"
    "app/services/embedding.py"
    "app/db/zerodb.py"
    "app/api/v1/endpoints/search.py"
    "tests/conftest.py"
    "tests/test_models.py"
    "tests/test_search_service.py"
    "tests/test_api_search.py"
    "requirements.txt"
    "pyproject.toml"
    ".env.example"
    "README.md"
)

missing_files=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        missing_files=$((missing_files + 1))
    fi
done

echo ""
if [ $missing_files -eq 0 ]; then
    echo -e "${GREEN}✓ All files present${NC}"
else
    echo -e "${RED}✗ $missing_files files missing${NC}"
    exit 1
fi
echo ""

# Check environment configuration
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"

    # Check for required variables
    required_vars=("ZERODB_PROJECT_ID" "ZERODB_API_KEY")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env 2>/dev/null; then
            value=$(grep "^${var}=" .env | cut -d '=' -f 2)
            if [ -n "$value" ] && [ "$value" != "your-project-id" ] && [ "$value" != "your-api-key" ]; then
                echo -e "${GREEN}✓${NC} $var configured"
            else
                echo -e "${YELLOW}⚠${NC} $var needs configuration"
            fi
        else
            echo -e "${RED}✗${NC} $var missing"
        fi
    done
else
    echo -e "${YELLOW}⚠ .env file not found (using test defaults)${NC}"
fi
echo ""

# Run code quality checks
echo -e "${YELLOW}Running code quality checks...${NC}"

# Check if black is installed
if command -v black &> /dev/null; then
    echo "Checking code formatting..."
    black --check app tests 2>&1 | grep -q "would" && echo -e "${YELLOW}⚠ Code needs formatting (run: black app tests)${NC}" || echo -e "${GREEN}✓ Code is formatted${NC}"
else
    echo -e "${YELLOW}⚠ black not installed (skipping format check)${NC}"
fi

# Check if ruff is installed
if command -v ruff &> /dev/null; then
    echo "Running linter..."
    ruff app tests && echo -e "${GREEN}✓ No linting errors${NC}" || echo -e "${RED}✗ Linting errors found${NC}"
else
    echo -e "${YELLOW}⚠ ruff not installed (skipping lint check)${NC}"
fi

echo ""

# Run tests
echo -e "${YELLOW}Running test suite...${NC}"
echo ""

# Run pytest with coverage
if pytest --cov=app --cov-report=term --cov-report=html --cov-fail-under=80 -v; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✓ All tests passed!"
    echo "✓ Coverage >= 80%"
    echo "==========================================${NC}"
    echo ""
    echo "Coverage report: htmlcov/index.html"
    echo ""

    # Summary
    echo -e "${GREEN}Implementation verified successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review coverage report: open htmlcov/index.html"
    echo "2. Start the server: ./start.sh --dev"
    echo "3. Access API docs: http://localhost:8000/docs"
    echo ""

    exit 0
else
    echo ""
    echo -e "${RED}=========================================="
    echo "✗ Tests failed or coverage < 80%"
    echo "==========================================${NC}"
    echo ""
    echo "Review the output above for details."
    echo ""
    exit 1
fi
