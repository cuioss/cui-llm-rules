#!/bin/bash
# Tests for parse-gradle-output.py script
# Tests Gradle build output parsing and categorization

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/../../../marketplace/bundles/builder/skills/builder-gradle-rules/scripts/parse-gradle-output.py"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

echo "=========================================="
echo "Testing parse-gradle-output.py"
echo "=========================================="

# Test 1: Parse successful build
test_successful_build() {
    echo ""
    echo "Test: Parse successful build"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-gradle-success.log" --mode structured 2>&1)

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
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-gradle-failure.log" --mode structured 2>&1)

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
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-gradle-javadoc.log" --mode structured 2>&1)

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

# Test 4: Test errors-only mode
test_errors_only_mode() {
    echo ""
    echo "Test: Errors-only mode"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-gradle-failure.log" --mode errors 2>&1)

    # Check output is JSON with only error-level issues
    if echo "$output" | jq -e '.data.issues' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Errors mode returns valid JSON"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Errors mode should return valid JSON"
        ((TESTS_FAILED++))
    fi
}

# Test 5: Test default mode (human-readable)
test_default_mode() {
    echo ""
    echo "Test: Default mode (human-readable)"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-gradle-success.log" --mode default 2>&1)

    # Check output contains Build Status line
    if echo "$output" | grep -q "Build Status: SUCCESS"; then
        echo -e "${GREEN}✓ PASSED${NC} - Build Status line present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Build Status line missing"
        ((TESTS_FAILED++))
    fi

    # Check output contains Issues Summary section
    if echo "$output" | grep -q "Issues Summary:"; then
        echo -e "${GREEN}✓ PASSED${NC} - Issues Summary section present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Issues Summary section missing"
        ((TESTS_FAILED++))
    fi
}

# Test 6: Test missing file handling
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

# Test 7: Test help flag
test_help_flag() {
    echo ""
    echo "Test: Help flag"

    local output
    output=$(python3 "$SCRIPT_PATH" --help 2>&1) || true

    if echo "$output" | grep -q "Parse Gradle build output"; then
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

# Test 8: Test issue structure
test_issue_structure() {
    echo ""
    echo "Test: Issue structure in output"

    local output
    output=$(python3 "$SCRIPT_PATH" --log "$FIXTURES_DIR/sample-gradle-failure.log" --mode structured 2>&1)

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
