#!/bin/bash
# Tests for verify-clean-build.py script
# Tests parsing of Maven build logs and status detection

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"
SCRIPT_PATH="${SCRIPT_DIR}/../../marketplace/bundles/cui-java-expert/skills/cui-java-core/scripts/verify-clean-build.py"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

test_success_build() {
    echo "Test: Parse successful build log"

    local output
    output=$(python3 "$SCRIPT_PATH" --log-file "${FIXTURES_DIR}/sample-build-success.log" 2>&1)

    if echo "$output" | jq -e '.status == "clean"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Correctly identified clean build"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Expected status 'clean', got: $output"
        ((TESTS_FAILED++))
    fi

    # Verify no errors or warnings reported
    if echo "$output" | jq -e '.data.errors | length == 0' > /dev/null 2>&1 && \
       echo "$output" | jq -e '.data.warnings | length == 0' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - No errors or warnings reported"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Unexpected errors or warnings in clean build"
        ((TESTS_FAILED++))
    fi
}

test_error_build() {
    echo ""
    echo "Test: Parse build log with errors"

    local output
    output=$(python3 "$SCRIPT_PATH" --log-file "${FIXTURES_DIR}/sample-build-errors.log" 2>&1)

    if echo "$output" | jq -e '.status == "has-errors"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Correctly identified build errors"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Expected status 'has-errors', got: $output"
        ((TESTS_FAILED++))
    fi

    # Verify errors are parsed
    local error_count
    error_count=$(echo "$output" | jq '.data.errors | length' 2>/dev/null || echo "0")
    if [ "$error_count" -ge 3 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Correctly parsed 3 errors"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Expected 3 errors, got: $error_count"
        ((TESTS_FAILED++))
    fi

    # Verify error details are present
    if echo "$output" | jq -e '.data.errors[0] | has("file") and has("line") and has("message")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Error contains file, line, and message"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Error missing required fields"
        ((TESTS_FAILED++))
    fi
}

test_warning_build() {
    echo ""
    echo "Test: Parse build log with warnings"

    local output
    output=$(python3 "$SCRIPT_PATH" --log-file "${FIXTURES_DIR}/sample-build-warnings.log" 2>&1)

    if echo "$output" | jq -e '.status == "has-warnings"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Correctly identified build warnings"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Expected status 'has-warnings', got: $output"
        ((TESTS_FAILED++))
    fi

    # Verify warnings are parsed
    local warning_count
    warning_count=$(echo "$output" | jq '.data.warnings | length' 2>/dev/null || echo "0")
    if [ "$warning_count" -ge 2 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Correctly parsed warnings"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Expected 2+ warnings, got: $warning_count"
        ((TESTS_FAILED++))
    fi
}

test_json_structure() {
    echo ""
    echo "Test: Verify JSON output structure"

    local output
    output=$(python3 "$SCRIPT_PATH" --log-file "${FIXTURES_DIR}/sample-build-success.log" 2>&1)

    # Check for required top-level fields
    if echo "$output" | jq -e 'has("status") and has("data")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - JSON has required top-level fields"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - JSON missing required top-level fields"
        ((TESTS_FAILED++))
    fi

    # Check for data structure
    if echo "$output" | jq -e '.data | has("errors") and has("warnings")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - JSON data has required arrays"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - JSON data missing required arrays"
        ((TESTS_FAILED++))
    fi
}

test_help_flag() {
    echo ""
    echo "Test: --help flag works"

    if python3 "$SCRIPT_PATH" --help > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - --help flag works"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - --help flag failed"
        ((TESTS_FAILED++))
    fi
}

# Run all tests
echo "=========================================="
echo "Testing verify-clean-build.py"
echo "=========================================="
echo ""

test_success_build
test_error_build
test_warning_build
test_json_structure
test_help_flag

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
