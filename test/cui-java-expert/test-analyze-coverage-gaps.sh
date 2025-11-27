#!/bin/bash
# Tests for analyze-coverage-gaps.py script
# Tests parsing of JaCoCo XML reports and gap prioritization

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"
SCRIPT_PATH="${SCRIPT_DIR}/../../marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing/scripts/analyze-coverage-gaps.py"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

test_parse_jacoco_report() {
    echo "Test: Parse JaCoCo XML report"

    local output
    output=$(python3 "$SCRIPT_PATH" --report "${FIXTURES_DIR}/sample-jacoco.xml" 2>&1)

    if echo "$output" | jq -e '.status == "success"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Successfully parsed JaCoCo report"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Failed to parse JaCoCo report: $output"
        ((TESTS_FAILED++))
    fi
}

test_coverage_metrics() {
    echo ""
    echo "Test: Extract coverage metrics"

    local output
    output=$(python3 "$SCRIPT_PATH" --report "${FIXTURES_DIR}/sample-jacoco.xml" 2>&1)

    # Check for overall coverage fields
    if echo "$output" | jq -e '.data.overall_coverage | has("line") and has("branch") and has("method")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Coverage metrics present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Coverage metrics missing"
        ((TESTS_FAILED++))
    fi

    # Verify line coverage calculation (23 covered, 7 missed = 76.67%)
    local line_coverage
    line_coverage=$(echo "$output" | jq -r '.data.overall_coverage.line' 2>/dev/null || echo "0")
    if (( $(echo "$line_coverage > 75 && $line_coverage < 78" | bc -l) )); then
        echo -e "${GREEN}✓ PASSED${NC} - Line coverage correctly calculated (~76.67%)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Line coverage incorrect: $line_coverage"
        ((TESTS_FAILED++))
    fi
}

test_gap_prioritization() {
    echo ""
    echo "Test: Gap prioritization"

    local output
    output=$(python3 "$SCRIPT_PATH" --report "${FIXTURES_DIR}/sample-jacoco.xml" 2>&1)

    # Check for gaps_by_priority structure
    if echo "$output" | jq -e '.data.gaps_by_priority | has("high") and has("medium") and has("low")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Gap priorities present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Gap priorities missing"
        ((TESTS_FAILED++))
    fi

    # Verify validateExpiry is identified as high priority (uncovered public method)
    if echo "$output" | jq -e '.data.gaps_by_priority.high[] | select(.method == "validateExpiry")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Uncovered public method identified as high priority"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Uncovered public method not identified"
        ((TESTS_FAILED++))
    fi
}

test_uncovered_methods() {
    echo ""
    echo "Test: Identify uncovered methods"

    local output
    output=$(python3 "$SCRIPT_PATH" --report "${FIXTURES_DIR}/sample-jacoco.xml" 2>&1)

    # Check for untested_public_methods field
    if echo "$output" | jq -e '.data | has("untested_public_methods")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Untested public methods field present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Untested public methods field missing"
        ((TESTS_FAILED++))
    fi

    # Verify at least one method is identified (validateExpiry)
    local untested_count
    untested_count=$(echo "$output" | jq '.data.untested_public_methods | length' 2>/dev/null || echo "0")
    if [ "$untested_count" -ge 1 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Identified untested public methods"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - No untested public methods identified"
        ((TESTS_FAILED++))
    fi
}

test_priority_filter() {
    echo ""
    echo "Test: Priority filter parameter"

    local output
    output=$(python3 "$SCRIPT_PATH" --report "${FIXTURES_DIR}/sample-jacoco.xml" --priority high 2>&1)

    if echo "$output" | jq -e '.status == "success"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Priority filter accepted"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Priority filter failed"
        ((TESTS_FAILED++))
    fi

    # Verify only high priority gaps returned when filtered
    if echo "$output" | jq -e '.data.gaps_by_priority.high | length > 0' > /dev/null 2>&1 && \
       ! echo "$output" | jq -e '.data.gaps_by_priority.medium | length > 0' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Filter correctly limited to high priority"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Filter did not correctly limit results"
        ((TESTS_FAILED++))
    fi
}

test_recommendations() {
    echo ""
    echo "Test: Generate recommendations"

    local output
    output=$(python3 "$SCRIPT_PATH" --report "${FIXTURES_DIR}/sample-jacoco.xml" 2>&1)

    # Check for recommendations field
    if echo "$output" | jq -e '.data | has("recommendations")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Recommendations field present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Recommendations field missing"
        ((TESTS_FAILED++))
    fi

    # Verify recommendation structure
    if echo "$output" | jq -e '.data.recommendations[0] | has("priority") and has("class") and has("reason")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Recommendations have required fields"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Recommendations missing required fields"
        ((TESTS_FAILED++))
    fi
}

test_help_flag() {
    echo ""
    echo "Test: --help flag works"

    if python3 "$SCRIPT_PATH" --help > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - --help flag works"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - --help flag failed"
        ((TESTS_FAILED++))
    fi
}

# Run all tests
echo "=========================================="
echo "Testing analyze-coverage-gaps.py"
echo "=========================================="
echo ""

test_parse_jacoco_report
test_coverage_metrics
test_gap_prioritization
test_uncovered_methods
test_priority_filter
test_recommendations
test_help_flag

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
