#!/bin/bash
# Test suite for documentation-stats.sh
#
# Usage: ./test-documentation-stats.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-documentation-standards/skills/cui-documentation/scripts/documentation-stats.sh"
TEST_FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run a test
run_test() {
    local test_name="$1"
    shift
    local test_command=("$@")

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: $test_name ... "

    if "${test_command[@]}" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test help flag
test_help() {
    echo ""
    echo "=== Testing help flag ==="
    echo ""

    run_test "help-flag-works" "$SCRIPT_UNDER_TEST" --help
    run_test "h-flag-works" "$SCRIPT_UNDER_TEST" -h
}

# Test console output format
test_console_output() {
    echo ""
    echo "=== Testing console output format ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: console-format-default ... "

    output=$("$SCRIPT_UNDER_TEST" "$TEST_FIXTURES_DIR" 2>&1)

    if echo "$output" | grep -q "Documentation Statistics"; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test JSON output format
test_json_output() {
    echo ""
    echo "=== Testing JSON output format ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: json-format-valid ... "

    output=$("$SCRIPT_UNDER_TEST" -f json "$TEST_FIXTURES_DIR" 2>&1)

    if echo "$output" | jq empty 2>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (invalid JSON)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: json-has-required-fields ... "

    total_files=$(echo "$output" | jq -r '.summary.total_files' 2>/dev/null)

    if [ -n "$total_files" ] && [ "$total_files" != "null" ]; then
        echo -e "${GREEN}PASS${NC} (total_files=$total_files)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (missing required fields)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test CSV output format
test_csv_output() {
    echo ""
    echo "=== Testing CSV output format ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: csv-format-valid ... "

    output=$("$SCRIPT_UNDER_TEST" -f csv "$TEST_FIXTURES_DIR" 2>&1)

    if echo "$output" | head -1 | grep -q "File,Lines,Words"; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test Markdown output format
test_markdown_output() {
    echo ""
    echo "=== Testing Markdown output format ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: markdown-format-valid ... "

    output=$("$SCRIPT_UNDER_TEST" -f markdown "$TEST_FIXTURES_DIR" 2>&1)

    if echo "$output" | grep -q "^# Documentation Statistics"; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test detailed output
test_detailed_output() {
    echo ""
    echo "=== Testing detailed output ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: details-flag-includes-files ... "

    output=$("$SCRIPT_UNDER_TEST" -d "$TEST_FIXTURES_DIR" 2>&1)

    if echo "$output" | grep -q "valid.adoc"; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test metric collection
test_metric_collection() {
    echo ""
    echo "=== Testing metric collection ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: counts-files-correctly ... "

    output=$("$SCRIPT_UNDER_TEST" -f json "$TEST_FIXTURES_DIR" 2>&1)
    file_count=$(echo "$output" | jq -r '.summary.total_files')

    # We have 3 fixture files
    expected_count=3

    if [ "$file_count" -eq "$expected_count" ]; then
        echo -e "${GREEN}PASS${NC} (found $file_count files)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (expected $expected_count, got $file_count)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: detects-xrefs ... "

    xref_count=$(echo "$output" | jq -r '.summary.total_xrefs')

    if [ "$xref_count" -ge 1 ]; then
        echo -e "${GREEN}PASS${NC} (found $xref_count xrefs)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (expected ≥1, got $xref_count)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: detects-code-blocks ... "

    code_blocks=$(echo "$output" | jq -r '.summary.total_code_blocks')

    if [ "$code_blocks" -ge 1 ]; then
        echo -e "${GREEN}PASS${NC} (found $code_blocks code blocks)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (expected ≥1, got $code_blocks)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test with real standards directory
test_real_standards() {
    echo ""
    echo "=== Testing with real standards directory ==="
    echo ""

    local standards_dir="$PROJECT_ROOT/standards"

    if [ ! -d "$standards_dir" ]; then
        echo "SKIP: standards directory not found"
        return
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: real-standards-stats ... "

    output=$("$SCRIPT_UNDER_TEST" -f json "$standards_dir" 2>&1)
    file_count=$(echo "$output" | jq -r '.summary.total_files' 2>/dev/null)

    if [ -n "$file_count" ] && [ "$file_count" -gt 0 ]; then
        echo -e "${GREEN}PASS${NC} (found $file_count files)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test error handling
test_error_handling() {
    echo ""
    echo "=== Testing error handling ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: invalid-format-rejected ... "

    if ! "$SCRIPT_UNDER_TEST" -f invalid_format >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: empty-directory-handled ... "

    temp_dir=$(mktemp -d)
    if "$SCRIPT_UNDER_TEST" "$temp_dir" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    rmdir "$temp_dir"
}

# Main execution
main() {
    echo "========================================"
    echo "Test Suite: documentation-stats.sh"
    echo "========================================"

    test_help
    test_console_output
    test_json_output
    test_csv_output
    test_markdown_output
    test_detailed_output
    test_metric_collection
    test_real_standards
    test_error_handling

    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo "Total tests:   $TESTS_RUN"
    echo -e "Passed:        ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed:        ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        exit 1
    fi
}

main
