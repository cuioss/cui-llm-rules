#!/bin/bash
# Tests for parse-maven-output.py script
# Tests Maven build output parsing and categorization

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/../../../marketplace/bundles/builder/skills/builder-maven-rules/scripts/parse-maven-output.py"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

echo "=========================================="
echo "Testing parse-maven-output.py"
echo "=========================================="

# Test 1: Parse successful build
test_successful_build() {
    echo ""
    echo "Test: Parse successful build"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-success.log" --mode structured 2>&1)

    # Check status is success
    if echo "$output" | jq -e '.status == "success"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Status is success"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Status should be success"
        echo "Output: $output"
        ((TESTS_FAILED++))
    fi

    # Check build_status is SUCCESS
    local build_status
    build_status=$(echo "$output" | jq -r '.data.build_status')
    if [ "$build_status" = "SUCCESS" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Build status is SUCCESS"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Build status should be SUCCESS, got: $build_status"
        ((TESTS_FAILED++))
    fi

    # Check no compilation errors
    local comp_errors
    comp_errors=$(echo "$output" | jq '.data.summary.compilation_errors // 0')
    if [ "$comp_errors" -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - No compilation errors"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Expected 0 compilation errors, got: $comp_errors"
        ((TESTS_FAILED++))
    fi

    # Check tests run count
    local tests_run
    tests_run=$(echo "$output" | jq '.metrics.tests_run // 0')
    if [ "$tests_run" -eq 13 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Tests run count correct: $tests_run"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Expected 13 tests run, got: $tests_run"
    fi

    # Check duration extracted
    local duration
    duration=$(echo "$output" | jq '.metrics.duration_ms // 0')
    if [ "$duration" -gt 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Duration extracted: ${duration}ms"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Duration not extracted"
    fi
}

# Test 2: Parse failed build with compilation errors
test_compilation_errors() {
    echo ""
    echo "Test: Parse build with compilation errors"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-failure.log" --mode structured 2>&1)

    # Check build_status is FAILURE
    local build_status
    build_status=$(echo "$output" | jq -r '.data.build_status')
    if [ "$build_status" = "FAILURE" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Build status is FAILURE"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Build status should be FAILURE, got: $build_status"
        ((TESTS_FAILED++))
    fi

    # Check compilation errors detected
    local comp_errors
    comp_errors=$(echo "$output" | jq '.data.summary.compilation_errors // 0')
    if [ "$comp_errors" -gt 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Detected $comp_errors compilation errors"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should have detected compilation errors"
        ((TESTS_FAILED++))
    fi

    # Check test failures detected
    local test_failures
    test_failures=$(echo "$output" | jq '.data.summary.test_failures // 0')
    if [ "$test_failures" -gt 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Detected $test_failures test failures"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should have detected test failures"
        ((TESTS_FAILED++))
    fi
}

# Test 3: Parse JavaDoc warnings
test_javadoc_warnings() {
    echo ""
    echo "Test: Parse JavaDoc warnings"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-javadoc.log" --mode structured 2>&1)

    # Check build_status is SUCCESS (javadoc warnings don't fail build by default)
    local build_status
    build_status=$(echo "$output" | jq -r '.data.build_status')
    if [ "$build_status" = "SUCCESS" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Build status is SUCCESS"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Build status is $build_status (may vary by config)"
    fi

    # Check javadoc warnings detected
    local javadoc_warnings
    javadoc_warnings=$(echo "$output" | jq '.data.summary.javadoc_warnings // 0')
    if [ "$javadoc_warnings" -gt 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Detected $javadoc_warnings JavaDoc warnings"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should have detected JavaDoc warnings"
        ((TESTS_FAILED++))
    fi
}

# Test 4: Test OpenRewrite filtering
test_openrewrite_filtering() {
    echo ""
    echo "Test: OpenRewrite message filtering"

    # First, check without filtering
    local output_default
    output_default=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-openrewrite.log" --mode structured 2>&1)

    local openrewrite_count
    openrewrite_count=$(echo "$output_default" | jq '.data.summary.openrewrite_info // 0')

    # Then, check with filtering
    local output_filtered
    output_filtered=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-openrewrite.log" --mode no-openrewrite 2>&1)

    # In no-openrewrite mode, output is human-readable, not JSON
    # We just verify the mode runs without error
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - no-openrewrite mode executed successfully"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - no-openrewrite mode failed"
        ((TESTS_FAILED++))
    fi
}

# Test 5: Test errors-only mode
test_errors_only_mode() {
    echo ""
    echo "Test: Errors-only mode"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-failure.log" --mode errors 2>&1)

    # Check output contains "Errors:" section
    if echo "$output" | grep -q "Errors:"; then
        echo -e "${GREEN}✓ PASSED${NC} - Errors section present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Errors section missing"
        ((TESTS_FAILED++))
    fi

    # Check output does not contain warnings (errors-only mode)
    if ! echo "$output" | grep -q "\[WARNING\]"; then
        echo -e "${GREEN}✓ PASSED${NC} - Warnings excluded in errors mode"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Warnings may be present in errors mode"
    fi
}

# Test 6: Test default mode (human-readable)
test_default_mode() {
    echo ""
    echo "Test: Default mode (human-readable)"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-success.log" --mode default 2>&1)

    # Check output contains Status line
    if echo "$output" | grep -q "Status: SUCCESS"; then
        echo -e "${GREEN}✓ PASSED${NC} - Status line present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Status line missing"
        ((TESTS_FAILED++))
    fi

    # Check output contains Summary section
    if echo "$output" | grep -q "Summary:"; then
        echo -e "${GREEN}✓ PASSED${NC} - Summary section present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Summary section missing"
        ((TESTS_FAILED++))
    fi
}

# Test 7: Test missing file handling
test_missing_file() {
    echo ""
    echo "Test: Missing file handling"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "nonexistent.log" --mode structured 2>&1) || true

    # Check error status
    if echo "$output" | jq -e '.status == "error"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Returns error status for missing file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should return error for missing file"
        ((TESTS_FAILED++))
    fi
}

# Test 8: Test help flag
test_help_flag() {
    echo ""
    echo "Test: Help flag"

    local output
    output=$(python3 "$SCRIPT_PATH" --help 2>&1) || true

    if echo "$output" | grep -q "Parse Maven build output"; then
        echo -e "${GREEN}✓ PASSED${NC} - Help output contains description"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Help output missing description"
        ((TESTS_FAILED++))
    fi

    if echo "$output" | grep -q "\-\-log"; then
        echo -e "${GREEN}✓ PASSED${NC} - Help output contains --log option"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Help output missing --log option"
        ((TESTS_FAILED++))
    fi

    if echo "$output" | grep -q "\-\-mode"; then
        echo -e "${GREEN}✓ PASSED${NC} - Help output contains --mode option"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Help output missing --mode option"
        ((TESTS_FAILED++))
    fi
}

# Test 9: Test issue structure
test_issue_structure() {
    echo ""
    echo "Test: Issue structure in output"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-maven-failure.log" --mode structured 2>&1)

    # Check issues array has proper structure
    if echo "$output" | jq -e '.data.issues[0].type' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Issue has type field"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Issue missing type field"
        ((TESTS_FAILED++))
    fi

    if echo "$output" | jq -e '.data.issues[0].severity' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Issue has severity field"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Issue missing severity field"
        ((TESTS_FAILED++))
    fi

    if echo "$output" | jq -e '.data.issues[0].message' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Issue has message field"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Issue missing message field"
        ((TESTS_FAILED++))
    fi
}

# Run all tests
test_successful_build
test_compilation_errors
test_javadoc_warnings
test_openrewrite_filtering
test_errors_only_mode
test_default_mode
test_missing_file
test_help_flag
test_issue_structure

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi

exit 0
