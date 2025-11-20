#!/bin/bash
# Test suite for asciidoc-formatter.sh
#
# Usage: ./test-asciidoc-formatter.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-documentation-standards/skills/cui-documentation/scripts/asciidoc-formatter.sh"
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

# Cleanup function
cleanup() {
    # Remove any backup files created during tests
    find "$TEST_FIXTURES_DIR" -name "*.adoc.bak" -delete 2>/dev/null || true
}
trap cleanup EXIT

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

# Test dry-run mode
test_dry_run() {
    echo ""
    echo "=== Testing dry-run mode ==="
    echo ""

    local test_file="$TEST_FIXTURES_DIR/missing-blank-line.adoc"

    # Copy original
    cp "$test_file" "$test_file.original"

    # Run in dry-run mode
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: dry-run-no-modification ... "

    "$SCRIPT_UNDER_TEST" -n "$test_file" >/dev/null 2>&1

    # Verify file wasn't modified
    if diff -q "$test_file" "$test_file.original" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (file was modified in dry-run mode)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    rm "$test_file.original"
}

# Test blank line fixes
test_blank_line_fix() {
    echo ""
    echo "=== Testing blank line fixes ==="
    echo ""

    # Just verify the script can run on a test file
    run_test "formatter-runs-on-file" "$SCRIPT_UNDER_TEST" -n -t lists "$TEST_FIXTURES_DIR/missing-blank-line.adoc"
}

# Test directory processing
test_directory_processing() {
    echo ""
    echo "=== Testing directory processing ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: processes-directory ... "

    if "$SCRIPT_UNDER_TEST" -n "$TEST_FIXTURES_DIR" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
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
    echo -n "Test: real-standards-dry-run ... "

    if "$SCRIPT_UNDER_TEST" -n "$standards_dir" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test invalid arguments
test_error_handling() {
    echo ""
    echo "=== Testing error handling ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: invalid-fix-type ... "

    if ! "$SCRIPT_UNDER_TEST" -t invalid_type >/dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC} (rejected invalid type)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (accepted invalid type)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "Test Suite: asciidoc-formatter.sh"
    echo "========================================"

    test_help
    test_dry_run
    test_blank_line_fix
    test_directory_processing
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
