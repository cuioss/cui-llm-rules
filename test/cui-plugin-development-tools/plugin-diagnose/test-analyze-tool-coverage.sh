#!/bin/bash
# Test suite for analyze-tool-coverage.sh
#
# Usage: ./test-analyze-tool-coverage.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-diagnose/scripts/analyze-tool-coverage.sh"
FIXTURES_DIR="$SCRIPT_DIR/fixtures/tool-coverage"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# TEST HELPER FUNCTIONS
# ============================================================================

run_test() {
    local test_name="$1"
    local test_file="$2"
    local check_field="$3"
    local expected_value="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test: $test_name ... "

    # Run script and capture output
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_file" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        echo "  Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON
    actual_value=$(echo "$result" | jq -r "$check_field")

    # Compare
    if [ "$actual_value" = "$expected_value" ]; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: $check_field=$expected_value"
        echo "  Actual:   $check_field=$actual_value"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# TEST SUITES
# ============================================================================

test_perfect_coverage() {
    echo ""
    echo "=== Testing perfect tool coverage ==="
    echo ""

    run_test "perfect-coverage-score" \
        "$FIXTURES_DIR/perfect-coverage.md" \
        ".tool_coverage.tool_fit_score" \
        "100.0"

    run_test "perfect-coverage-rating" \
        "$FIXTURES_DIR/perfect-coverage.md" \
        ".tool_coverage.rating" \
        "Excellent"

    run_test "perfect-coverage-missing-count" \
        "$FIXTURES_DIR/perfect-coverage.md" \
        ".tool_coverage.missing_count" \
        "0"

    run_test "perfect-coverage-unused-count" \
        "$FIXTURES_DIR/perfect-coverage.md" \
        ".tool_coverage.unused_count" \
        "0"
}

test_unused_tools() {
    echo ""
    echo "=== Testing unused tools detection ==="
    echo ""

    run_test "unused-tools-count" \
        "$FIXTURES_DIR/unused-tools.md" \
        ".tool_coverage.unused_count" \
        "3"

    run_test "unused-tools-declared" \
        "$FIXTURES_DIR/unused-tools.md" \
        ".tool_coverage.declared_count" \
        "5"

    run_test "unused-tools-used" \
        "$FIXTURES_DIR/unused-tools.md" \
        ".tool_coverage.used_count" \
        "2"
}

test_missing_tools() {
    echo ""
    echo "=== Testing missing tools detection ==="
    echo ""

    run_test "missing-tools-count" \
        "$FIXTURES_DIR/missing-tools.md" \
        ".tool_coverage.missing_count" \
        "3"

    run_test "missing-tools-declared" \
        "$FIXTURES_DIR/missing-tools.md" \
        ".tool_coverage.declared_count" \
        "2"
}

test_critical_violations() {
    echo ""
    echo "=== Testing critical violations ==="
    echo ""

    run_test "critical-has-task-tool" \
        "$FIXTURES_DIR/critical-violations.md" \
        ".critical_violations.has_task_tool" \
        "true"

    run_test "critical-has-task-calls" \
        "$FIXTURES_DIR/critical-violations.md" \
        ".critical_violations.has_task_calls" \
        "true"

    # Check Maven calls detected (should be > 0)
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: critical-maven-calls-detected ... "
    result=$("$SCRIPT_UNDER_TEST" "$FIXTURES_DIR/critical-violations.md" 2>&1)
    maven_count=$(echo "$result" | jq -r '.critical_violations.maven_calls | length')
    if [ "$maven_count" -gt 0 ]; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: maven_calls > 0"
        echo "  Actual:   maven_calls = $maven_count"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    # Check backup patterns detected (should be > 0)
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: critical-backup-patterns-detected ... "
    backup_count=$(echo "$result" | jq -r '.critical_violations.backup_file_patterns | length')
    if [ "$backup_count" -gt 0 ]; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: backup_patterns > 0"
        echo "  Actual:   backup_patterns = $backup_count"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    echo "========================================"
    echo "Test Suite: analyze-tool-coverage.sh"
    echo "========================================"

    # Check script exists
    if [ ! -f "$SCRIPT_UNDER_TEST" ]; then
        echo -e "${RED}ERROR: Script not found: $SCRIPT_UNDER_TEST${NC}"
        exit 1
    fi

    # Check jq is available
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}ERROR: jq is required for tests${NC}"
        exit 1
    fi

    # Check fixtures exist
    if [ ! -d "$FIXTURES_DIR" ]; then
        echo -e "${RED}ERROR: Fixtures directory not found: $FIXTURES_DIR${NC}"
        exit 1
    fi

    # Run all test suites
    test_perfect_coverage
    test_unused_tools
    test_missing_tools
    test_critical_violations

    # Print summary
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
        echo -e "${RED}✗ Some tests failed!${NC}"
        exit 1
    fi
}

# Run main
main
