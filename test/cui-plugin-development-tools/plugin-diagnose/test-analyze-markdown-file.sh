#!/bin/bash
# Test suite for analyze-markdown-file.sh
#
# Usage: ./test-analyze-markdown-file.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-diagnose/scripts/analyze-markdown-file.sh"
FIXTURES_DIR="$SCRIPT_DIR/fixtures/markdown-file"

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
    local component_type="$3"
    local check_field="$4"
    local expected_value="$5"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test: $test_name ... "

    # Run script and capture output
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_file" "$component_type" 2>&1); then
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

test_valid_agent() {
    echo ""
    echo "=== Testing valid agent ==="
    echo ""

    run_test "valid-agent-has-frontmatter" \
        "$FIXTURES_DIR/valid-agent.md" \
        "agent" \
        ".frontmatter.present" \
        "true"

    run_test "valid-agent-yaml-valid" \
        "$FIXTURES_DIR/valid-agent.md" \
        "agent" \
        ".frontmatter.yaml_valid" \
        "true"

    run_test "valid-agent-has-ci-rule" \
        "$FIXTURES_DIR/valid-agent.md" \
        "agent" \
        ".continuous_improvement_rule.present" \
        "true"

    run_test "valid-agent-no-rule6" \
        "$FIXTURES_DIR/valid-agent.md" \
        "agent" \
        ".rules.rule_6_violation" \
        "false"
}

test_bloated_command() {
    echo ""
    echo "=== Testing bloated command ==="
    echo ""

    run_test "bloated-command-classification" \
        "$FIXTURES_DIR/bloated-command.md" \
        "command" \
        ".bloat.classification" \
        "LARGE"
}

test_rule6_violation() {
    echo ""
    echo "=== Testing Rule 6 violation ==="
    echo ""

    run_test "rule6-violation-detected" \
        "$FIXTURES_DIR/rule6-violation.md" \
        "agent" \
        ".rules.rule_6_violation" \
        "true"
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    echo "========================================"
    echo "Test Suite: analyze-markdown-file.sh"
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
    test_valid_agent
    test_bloated_command
    test_rule6_violation

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
