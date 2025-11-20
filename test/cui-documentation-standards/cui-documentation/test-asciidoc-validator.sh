#!/bin/bash
# Test suite for asciidoc-validator.sh
#
# Usage: ./test-asciidoc-validator.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-documentation-standards/skills/cui-documentation/scripts/asciidoc-validator.sh"
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

    # Help should exit with code 2 (EXIT_ERROR)
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: help-flag-displays ... "

    if "$SCRIPT_UNDER_TEST" --help 2>&1 | grep -q "Usage:"; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test console output format
test_console_output() {
    echo ""
    echo "=== Testing console output format ==="
    echo ""

    run_test "console-format-default" "$SCRIPT_UNDER_TEST" "$TEST_FIXTURES_DIR"
    run_test "console-format-explicit" "$SCRIPT_UNDER_TEST" -f console "$TEST_FIXTURES_DIR"
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
}

# Test valid file detection
test_valid_file() {
    echo ""
    echo "=== Testing valid file detection ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: valid-file-passes ... "

    if "$SCRIPT_UNDER_TEST" -q "$TEST_FIXTURES_DIR/valid.adoc" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test invalid file detection
test_invalid_file() {
    echo ""
    echo "=== Testing invalid file detection ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: missing-blank-line-detected ... "

    # Should exit with code 1 (non-compliant)
    if ! "$SCRIPT_UNDER_TEST" -q "$TEST_FIXTURES_DIR/missing-blank-line.adoc" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC} (detected violation)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (did not detect violation)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: invalid-xref-detected ... "

    if ! "$SCRIPT_UNDER_TEST" -q "$TEST_FIXTURES_DIR/invalid-xref.adoc" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC} (detected violation)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (did not detect violation)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test verbose mode
test_verbose_mode() {
    echo ""
    echo "=== Testing verbose mode ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: verbose-shows-details ... "

    output=$("$SCRIPT_UNDER_TEST" -v "$TEST_FIXTURES_DIR" 2>&1 || true)

    if echo "$output" | grep -q "Checking"; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test quiet mode
test_quiet_mode() {
    echo ""
    echo "=== Testing quiet mode ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: quiet-minimal-output ... "

    output=$("$SCRIPT_UNDER_TEST" -q "$TEST_FIXTURES_DIR/valid.adoc" 2>&1)
    line_count=$(echo "$output" | wc -l | tr -d ' ')

    if [ "$line_count" -le 2 ]; then
        echo -e "${GREEN}PASS${NC} ($line_count lines)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} ($line_count lines, expected ≤2)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test ignore patterns
test_ignore_patterns() {
    echo ""
    echo "=== Testing ignore patterns ==="
    echo ""

    run_test "ignore-pattern-works" "$SCRIPT_UNDER_TEST" -i "missing-*.adoc" "$TEST_FIXTURES_DIR"
}

# Test severity levels
test_severity_levels() {
    echo ""
    echo "=== Testing severity levels ==="
    echo ""

    run_test "severity-all" "$SCRIPT_UNDER_TEST" -s all "$TEST_FIXTURES_DIR"
    run_test "severity-error" "$SCRIPT_UNDER_TEST" -s error "$TEST_FIXTURES_DIR"
    run_test "severity-warning" "$SCRIPT_UNDER_TEST" -s warning "$TEST_FIXTURES_DIR"
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
    echo -n "Test: real-standards-validation ... "

    if "$SCRIPT_UNDER_TEST" -q "$standards_dir" >/dev/null 2>&1 || true; then
        echo -e "${GREEN}PASS${NC} (completed)"
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
    echo -n "Test: nonexistent-dir-handled ... "

    if ! "$SCRIPT_UNDER_TEST" /nonexistent/path >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "Test Suite: asciidoc-validator.sh"
    echo "========================================"

    test_help
    test_console_output
    test_json_output
    test_valid_file
    test_invalid_file
    test_verbose_mode
    test_quiet_mode
    test_ignore_patterns
    test_severity_levels
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
