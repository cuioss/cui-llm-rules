#!/bin/bash
# Tests for analyze-coverage.py script
# Tests JaCoCo XML report parsing and coverage analysis

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/../../marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing/scripts/analyze-coverage.py"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

echo "=========================================="
echo "Testing analyze-coverage.py"
echo "=========================================="

# Test 1: Parse JaCoCo XML report
test_parse_jacoco_report() {
    echo ""
    echo "Test: Parse JaCoCo XML report"

    local output
    output=$(python3 "$SCRIPT_PATH" --file "$FIXTURES_DIR/sample-jacoco.xml" 2>&1)

    # Check status is success
    if echo "$output" | jq -e '.status == "success"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Successfully parsed JaCoCo report"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Failed to parse JaCoCo report"
        echo "Output: $output"
        ((TESTS_FAILED++))
    fi

    # Check overall_coverage exists in data
    if echo "$output" | jq -e '.data.overall_coverage' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Overall coverage data present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Overall coverage data missing"
        ((TESTS_FAILED++))
    fi

    # Check line_coverage is numeric
    if echo "$output" | jq -e '.data.overall_coverage.line_coverage | type == "number"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Line coverage is numeric"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Line coverage should be numeric"
        ((TESTS_FAILED++))
    fi

    # Check metrics section
    if echo "$output" | jq -e '.metrics.file_analyzed' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Metrics section present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Metrics section missing"
        ((TESTS_FAILED++))
    fi
}

# Test 2: Check threshold functionality
test_threshold_check() {
    echo ""
    echo "Test: Check threshold functionality"

    # Test with low threshold (should meet)
    local output
    output=$(python3 "$SCRIPT_PATH" --file "$FIXTURES_DIR/sample-jacoco.xml" --threshold 50 2>&1)

    if echo "$output" | jq -e '.metrics.meets_threshold == true' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Low threshold met correctly"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Low threshold should be met"
        ((TESTS_FAILED++))
    fi

    # Test with high threshold (should not meet)
    output=$(python3 "$SCRIPT_PATH" --file "$FIXTURES_DIR/sample-jacoco.xml" --threshold 95 2>&1)

    if echo "$output" | jq -e '.metrics.meets_threshold == false' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - High threshold not met correctly"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - High threshold should not be met"
        ((TESTS_FAILED++))
    fi
}

# Test 3: Error handling for missing file
test_missing_file() {
    echo ""
    echo "Test: Error handling for missing file"

    local output
    output=$(python3 "$SCRIPT_PATH" --file "nonexistent.xml" 2>&1) || true

    if echo "$output" | jq -e '.status == "error"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Returns error status for missing file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should return error for missing file"
        ((TESTS_FAILED++))
    fi
}

# Test 4: Error handling for missing arguments
test_missing_arguments() {
    echo ""
    echo "Test: Error handling for missing arguments"

    local output
    output=$(python3 "$SCRIPT_PATH" 2>&1) || true

    if echo "$output" | jq -e '.status == "error"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Returns error when no arguments provided"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should return error when no arguments"
        ((TESTS_FAILED++))
    fi
}

# Test 5: Check low coverage classes detection
test_low_coverage_classes() {
    echo ""
    echo "Test: Check low coverage classes detection"

    local output
    output=$(python3 "$SCRIPT_PATH" --file "$FIXTURES_DIR/sample-jacoco.xml" --threshold 90 2>&1)

    # Should have some low coverage classes when threshold is 90%
    if echo "$output" | jq -e '.data.low_coverage_classes | type == "array"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Low coverage classes array present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Low coverage classes array missing"
        ((TESTS_FAILED++))
    fi
}

# Run all tests
test_parse_jacoco_report
test_threshold_check
test_missing_file
test_missing_arguments
test_low_coverage_classes

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
