#!/bin/bash
# Test suite for parse-npm-output.py
# Tests npm/npx output parsing and issue categorization

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/builder-npm/skills/builder-npm-rules/scripts/parse-npm-output.py"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    if [[ "$expected" == "$actual" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    if [[ "$haystack" == *"$needle"* ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Expected to contain: $needle"
        echo "  Actual: $haystack"
        return 1
    fi
}

assert_json_field() {
    local json="$1"
    local field="$2"
    local expected="$3"
    local message="$4"

    local actual=$(echo "$json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data$field)" 2>/dev/null || echo "ERROR")

    if [[ "$expected" == "$actual" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Field: $field"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

assert_json_greater_than() {
    local json="$1"
    local field="$2"
    local expected="$3"
    local message="$4"

    local actual=$(echo "$json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data$field)" 2>/dev/null || echo "0")

    if [[ "$actual" -gt "$expected" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Field: $field"
        echo "  Expected > $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

run_test() {
    local test_name="$1"
    local test_func="$2"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}Running: $test_name${NC}"

    if $test_func; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓ PASS${NC}\n"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗ FAIL${NC}\n"
    fi
}

# TEST 1: Parse successful build
test_parse_successful_build() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-success.log" --mode structured 2>&1)

    assert_json_field "$output" "['status']" "success" "Status should be success" &&
    assert_json_field "$output" "['metrics']['total_issues']" "0" "Should have 0 issues" &&
    assert_json_field "$output" "['metrics']['test_failures']" "0" "Should have 0 test failures"
}

# TEST 2: Parse test failures
test_parse_test_failures() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-test-failure.log" --mode structured 2>&1)

    assert_json_field "$output" "['status']" "failure" "Status should be failure" &&
    assert_json_greater_than "$output" "['metrics']['test_failures']" "0" "Should detect test failures" &&
    assert_json_greater_than "$output" "['metrics']['total_issues']" "0" "Should have issues"
}

# TEST 3: Parse lint errors
test_parse_lint_errors() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-lint-errors.log" --mode structured 2>&1)

    assert_json_field "$output" "['status']" "failure" "Status should be failure" &&
    assert_json_greater_than "$output" "['metrics']['lint_errors']" "0" "Should detect lint errors" &&
    assert_json_greater_than "$output" "['metrics']['total_errors']" "0" "Should count errors"
}

# TEST 4: Parse compilation errors
test_parse_compilation_errors() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-compilation-error.log" --mode structured 2>&1)

    assert_json_field "$output" "['status']" "failure" "Status should be failure" &&
    assert_json_greater_than "$output" "['metrics']['compilation_errors']" "0" "Should detect compilation errors"
}

# TEST 5: Parse Playwright failures
test_parse_playwright_failures() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-playwright-failure.log" --mode structured 2>&1)

    assert_json_field "$output" "['status']" "failure" "Status should be failure" &&
    assert_json_greater_than "$output" "['metrics']['playwright_errors']" "0" "Should detect Playwright errors" &&
    assert_json_greater_than "$output" "['metrics']['total_issues']" "0" "Should have issues"
}

# TEST 6: Parse dependency errors
test_parse_dependency_errors() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-dependency-error.log" --mode structured 2>&1)

    assert_json_field "$output" "['status']" "failure" "Status should be failure" &&
    assert_json_greater_than "$output" "['metrics']['dependency_errors']" "0" "Should detect dependency errors"
}

# TEST 7: Default mode output
test_default_mode_output() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-lint-errors.log" --mode default 2>&1)

    assert_contains "$output" "Status:" "Should show status" &&
    assert_contains "$output" "Errors:" "Should show errors section"
}

# TEST 8: Errors-only mode
test_errors_only_mode() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-lint-errors.log" --mode errors 2>&1)

    assert_contains "$output" "Status:" "Should show status" &&
    assert_contains "$output" "Errors:" "Should show errors section"
    # Warnings section should not be present in errors-only mode
}

# TEST 9: File location extraction
test_file_location_extraction() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-lint-errors.log" --mode structured 2>&1)

    # Check that issues have file locations
    local has_file=$(echo "$output" | python3 -c "import sys, json; data=json.load(sys.stdin); print('true' if len(data.get('data', {}).get('issues', [])) > 0 and data['data']['issues'][0].get('file') else 'false')" 2>/dev/null)

    assert_equals "true" "$has_file" "Should extract file locations from errors"
}

# TEST 10: Issue categorization accuracy
test_issue_categorization() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-test-failure.log" --mode structured 2>&1)

    # Test failures should be categorized correctly
    local test_failures=$(echo "$output" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['metrics']['test_failures'])" 2>/dev/null)

    assert_equals "1" "$test_failures" "Should correctly categorize test failures"
}

# TEST 11: Lint error with line and column extraction
test_lint_error_location() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-lint-errors.log" --mode structured 2>&1)

    # Check first issue has line and column
    local has_line=$(echo "$output" | python3 -c "import sys, json; data=json.load(sys.stdin); issues=data.get('data', {}).get('issues', []); print('true' if len(issues) > 0 and issues[0].get('line') is not None else 'false')" 2>/dev/null)

    assert_equals "true" "$has_line" "Should extract line numbers from lint errors"
}

# TEST 12: Multiple error types in single file
test_multiple_error_types() {
    local output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-npm-lint-errors.log" --mode structured 2>&1)

    # Should have both errors and warnings
    local total_errors=$(echo "$output" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['metrics']['total_errors'])" 2>/dev/null)
    local total_warnings=$(echo "$output" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['metrics']['total_warnings'])" 2>/dev/null)

    if [[ "$total_errors" -gt "0" && "$total_warnings" -gt "0" ]]; then
        return 0
    else
        echo -e "${RED}Expected both errors and warnings${NC}"
        echo "  Errors: $total_errors"
        echo "  Warnings: $total_warnings"
        return 1
    fi
}

# Run all tests
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Testing parse-npm-output.py${NC}"
echo -e "${YELLOW}========================================${NC}\n"

run_test "Parse successful build" test_parse_successful_build
run_test "Parse test failures" test_parse_test_failures
run_test "Parse lint errors" test_parse_lint_errors
run_test "Parse compilation errors" test_parse_compilation_errors
run_test "Parse Playwright failures" test_parse_playwright_failures
run_test "Parse dependency errors" test_parse_dependency_errors
run_test "Default mode output" test_default_mode_output
run_test "Errors-only mode" test_errors_only_mode
run_test "File location extraction" test_file_location_extraction
run_test "Issue categorization accuracy" test_issue_categorization
run_test "Lint error with line and column extraction" test_lint_error_location
run_test "Multiple error types in single file" test_multiple_error_types

# Print summary
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Test Summary${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Tests run:    $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
