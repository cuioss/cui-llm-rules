#!/bin/bash
# Test suite for analyze-tool-coverage.sh
#
# Usage: ./test-analyze-tool-coverage.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/analyze-tool-coverage.sh"
FIXTURES_DIR="$SCRIPT_DIR/fixtures/tool-coverage"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    local expected_score="$3"
    local expected_rating="$4"

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
    actual_score=$(echo "$result" | jq -r '.tool_coverage.tool_fit_score')
    actual_rating=$(echo "$result" | jq -r '.tool_coverage.rating')

    # Compare
    if [ "$actual_score" = "$expected_score" ] && [ "$actual_rating" = "$expected_rating" ]; then
        echo -e "${GREEN}PASS${NC} (score=$actual_score, rating=$actual_rating)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: score=$expected_score, rating=$expected_rating"
        echo "  Actual:   score=$actual_score, rating=$actual_rating"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

run_violation_test() {
    local test_name="$1"
    local test_file="$2"
    local check_field="$3"
    local expected_value="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Violation: $test_name ... "

    # Run script
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_file" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON
    actual_value=$(echo "$result" | jq -r ".critical_violations.$check_field")

    # Compare
    if [ "$actual_value" = "$expected_value" ]; then
        echo -e "${GREEN}PASS${NC} ($check_field=$actual_value)"
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

run_array_test() {
    local test_name="$1"
    local test_file="$2"
    local json_path="$3"
    local expected_count="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Array: $test_name ... "

    # Run script
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_file" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON and count array elements
    actual_count=$(echo "$result" | jq -r "$json_path | length")

    # Compare
    if [ "$actual_count" -eq "$expected_count" ]; then
        echo -e "${GREEN}PASS${NC} (count=$actual_count)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected count: $expected_count"
        echo "  Actual count:   $actual_count"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# TEST SUITES
# ============================================================================

test_fixtures() {
    echo ""
    echo "=== Testing with fixtures ==="
    echo ""

    # Test 1: Perfect tool fit
    run_test "perfect-fit" \
        "$FIXTURES_DIR/perfect-fit.md" \
        "100.0" \
        "Excellent"

    # Test 2: Missing tool
    run_test "missing-tool" \
        "$FIXTURES_DIR/missing-tool.md" \
        "50.0" \
        "Poor"

    # Test 3: Unused tool
    run_test "unused-tool" \
        "$FIXTURES_DIR/unused-tool.md" \
        "66.7" \
        "Needs improvement"

    # Test 4: Check missing tools array
    run_array_test "missing-tool has 1 missing" \
        "$FIXTURES_DIR/missing-tool.md" \
        ".tool_coverage.missing_tools" \
        1

    # Test 5: Check unused tools array
    run_array_test "unused-tool has 1 unused" \
        "$FIXTURES_DIR/unused-tool.md" \
        ".tool_coverage.unused_tools" \
        1
}

test_violations() {
    echo ""
    echo "=== Testing critical violations ==="
    echo ""

    # Test 1: Task tool violation
    run_violation_test "task-in-frontmatter" \
        "$FIXTURES_DIR/task-violation.md" \
        "has_task_tool" \
        "true"

    run_violation_test "task-calls-detected" \
        "$FIXTURES_DIR/task-violation.md" \
        "has_task_calls" \
        "true"

    # Test 2: Maven anti-pattern
    run_array_test "maven-calls-detected" \
        "$FIXTURES_DIR/maven-antipattern.md" \
        ".critical_violations.maven_calls" \
        1

    # Test 3: Backup file pattern
    run_array_test "backup-pattern-detected" \
        "$FIXTURES_DIR/backup-files.md" \
        ".critical_violations.backup_file_patterns" \
        1
}

test_real_agents() {
    echo ""
    echo "=== Testing with real agent files ==="
    echo ""

    # Test with diagnose-command agent
    local file="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/agents/diagnose-command.md"
    if [ -f "$file" ]; then
        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Real agent: diagnose-command ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        score=$(echo "$result" | jq -r '.tool_coverage.tool_fit_score')
        has_task=$(echo "$result" | jq -r '.critical_violations.has_task_tool')

        if (( $(awk "BEGIN {print ($score >= 80)}") )) && [ "$has_task" = "false" ]; then
            echo -e "${GREEN}PASS${NC} (score=$score, no violations)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC} (score=$score, has_task=$has_task)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo "SKIP: diagnose-command.md not found"
    fi

    # Test with plugin-inventory-scanner agent
    file="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/agents/plugin-inventory-scanner.md"
    if [ -f "$file" ]; then
        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Real agent: plugin-inventory-scanner ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        score=$(echo "$result" | jq -r '.tool_coverage.tool_fit_score')

        if (( $(awk "BEGIN {print ($score >= 80)}") )); then
            echo -e "${GREEN}PASS${NC} (score=$score)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC} (score=$score)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo "SKIP: plugin-inventory-scanner.md not found"
    fi
}

test_json_validity() {
    echo ""
    echo "=== Testing JSON validity for all agents ==="
    echo ""

    local files=("$PROJECT_ROOT"/marketplace/bundles/*/agents/*.md)
    local valid_count=0
    local invalid_count=0

    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))

        # Try to run script and parse JSON
        if result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1) && echo "$result" | jq . > /dev/null 2>&1; then
            valid_count=$((valid_count + 1))
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}: Invalid JSON for $(basename "$file")"
            invalid_count=$((invalid_count + 1))
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done

    echo "JSON validity: $valid_count valid, $invalid_count invalid"
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
    test_fixtures
    test_violations
    test_real_agents
    test_json_validity

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
