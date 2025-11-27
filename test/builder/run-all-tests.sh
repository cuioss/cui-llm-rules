#!/bin/bash
# Run all test suites for unified builder bundle

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track overall results
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Builder Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to run a test suite
run_suite() {
    local suite_name="$1"
    local suite_script="$2"

    TOTAL_SUITES=$((TOTAL_SUITES + 1))

    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}Running: $suite_name${NC}"
    echo -e "${BLUE}----------------------------------------${NC}\n"

    if bash "$suite_script"; then
        PASSED_SUITES=$((PASSED_SUITES + 1))
        echo -e "\n${GREEN}✓ $suite_name PASSED${NC}\n"
    else
        FAILED_SUITES=$((FAILED_SUITES + 1))
        echo -e "\n${RED}✗ $suite_name FAILED${NC}\n"
    fi
}

# Run Gradle tests
if [[ -d "$SCRIPT_DIR/gradle" ]]; then
    echo -e "${BLUE}=== GRADLE TESTS ===${NC}\n"
    for test_script in "$SCRIPT_DIR"/gradle/test-*.sh; do
        if [[ -f "$test_script" ]]; then
            run_suite "$(basename "$test_script" .sh)" "$test_script"
        fi
    done
fi

# Run Maven tests
if [[ -d "$SCRIPT_DIR/maven" ]]; then
    echo -e "${BLUE}=== MAVEN TESTS ===${NC}\n"
    for test_script in "$SCRIPT_DIR"/maven/test-*.sh; do
        if [[ -f "$test_script" ]]; then
            run_suite "$(basename "$test_script" .sh)" "$test_script"
        fi
    done
fi

# Run npm tests
if [[ -d "$SCRIPT_DIR/npm" ]]; then
    echo -e "${BLUE}=== NPM TESTS ===${NC}\n"
    for test_script in "$SCRIPT_DIR"/npm/test-*.sh; do
        if [[ -f "$test_script" ]]; then
            run_suite "$(basename "$test_script" .sh)" "$test_script"
        fi
    done
fi

# Print overall summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Overall Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Test suites run:    $TOTAL_SUITES"
echo -e "${GREEN}Test suites passed: $PASSED_SUITES${NC}"

if [[ $FAILED_SUITES -gt 0 ]]; then
    echo -e "${RED}Test suites failed: $FAILED_SUITES${NC}"
    echo -e "\n${RED}TESTS FAILED${NC}"
    exit 1
else
    echo -e "\n${GREEN}ALL TESTS PASSED${NC}"
    exit 0
fi
