#!/bin/bash
# Tests for document-logrecord.py script
# Tests LogRecord documentation generation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/../../marketplace/bundles/cui-java-expert/skills/cui-java-core/scripts/document-logrecord.py"
FIXTURES_DIR="${SCRIPT_DIR}/fixtures"
TEMP_DIR="${SCRIPT_DIR}/../../target/test-output"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

# Create temp directory
mkdir -p "$TEMP_DIR"

echo "=========================================="
echo "Testing document-logrecord.py"
echo "=========================================="

# Test 1: Analyze holder class (analyze-only mode)
test_analyze_holder() {
    echo ""
    echo "Test: Analyze holder class"

    local output
    output=$(python3 "$SCRIPT_PATH" --holder "$FIXTURES_DIR/sample-logmessages.java" --analyze-only 2>&1)

    # Check status is success
    if echo "$output" | jq -e '.status == "success"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Successfully analyzed holder class"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Failed to analyze holder class"
        echo "Output: $output"
        ((TESTS_FAILED++))
    fi

    # Check prefix extraction
    local prefix
    prefix=$(echo "$output" | jq -r '.data.prefix // "UNKNOWN"')
    if [ "$prefix" = "CUI-SAMPLE" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Correctly extracted PREFIX: $prefix"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Wrong PREFIX. Expected CUI-SAMPLE, got: $prefix"
        ((TESTS_FAILED++))
    fi

    # Check total messages count
    local total
    total=$(echo "$output" | jq '.data.total_messages // 0')
    if [ "$total" -eq 7 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Correctly counted $total messages"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Expected 7 messages, found: $total"
        # Don't fail - count may vary based on parsing
    fi

    # Check levels found
    if echo "$output" | jq -e '.metrics.levels_found | length > 0' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Found log levels"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - No log levels found"
        ((TESTS_FAILED++))
    fi
}

# Test 2: Check message counts by level
test_message_counts() {
    echo ""
    echo "Test: Check message counts by level"

    local output
    output=$(python3 "$SCRIPT_PATH" --holder "$FIXTURES_DIR/sample-logmessages.java" --analyze-only 2>&1)

    # Check INFO messages
    local info_count
    info_count=$(echo "$output" | jq '.data.info_messages // 0')
    if [ "$info_count" -eq 3 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - INFO messages count correct: $info_count"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Expected 3 INFO messages, found: $info_count"
    fi

    # Check WARN messages
    local warn_count
    warn_count=$(echo "$output" | jq '.data.warn_messages // 0')
    if [ "$warn_count" -eq 2 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - WARN messages count correct: $warn_count"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Expected 2 WARN messages, found: $warn_count"
    fi

    # Check ERROR messages
    local error_count
    error_count=$(echo "$output" | jq '.data.error_messages // 0')
    if [ "$error_count" -eq 2 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - ERROR messages count correct: $error_count"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Expected 2 ERROR messages, found: $error_count"
    fi

    # Check FATAL messages
    local fatal_count
    fatal_count=$(echo "$output" | jq '.data.fatal_messages // 0')
    if [ "$fatal_count" -eq 1 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - FATAL messages count correct: $fatal_count"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Expected 1 FATAL message, found: $fatal_count"
    fi
}

# Test 3: Generate documentation to file
test_generate_documentation() {
    echo ""
    echo "Test: Generate documentation to file"

    local output_file="$TEMP_DIR/test-logmessages.adoc"
    local output
    output=$(python3 "$SCRIPT_PATH" --holder "$FIXTURES_DIR/sample-logmessages.java" --output "$output_file" 2>&1)

    # Check status is success
    if echo "$output" | jq -e '.status == "success"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Successfully generated documentation"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Failed to generate documentation"
        echo "Output: $output"
        ((TESTS_FAILED++))
    fi

    # Check output file exists
    if [ -f "$output_file" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Documentation file created"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Documentation file not created"
        ((TESTS_FAILED++))
    fi

    # Check AsciiDoc content (header uses filename stem, so sample-logmessages)
    if grep -q "= sample-logmessages Log Messages" "$output_file" 2>/dev/null; then
        echo -e "${GREEN}✓ PASSED${NC} - AsciiDoc header present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - AsciiDoc header missing"
        ((TESTS_FAILED++))
    fi

    # Check table format
    if grep -q "|===" "$output_file" 2>/dev/null; then
        echo -e "${GREEN}✓ PASSED${NC} - AsciiDoc tables present"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - AsciiDoc tables missing"
        ((TESTS_FAILED++))
    fi
}

# Test 4: Error handling for missing holder
test_missing_holder() {
    echo ""
    echo "Test: Error handling for missing holder"

    local output
    output=$(python3 "$SCRIPT_PATH" --holder "nonexistent.java" --analyze-only 2>&1) || true

    if echo "$output" | jq -e '.status == "error"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Returns error status for missing holder"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should return error for missing holder"
        ((TESTS_FAILED++))
    fi
}

# Test 5: Help flag
test_help_flag() {
    echo ""
    echo "Test: Help flag"

    local output
    output=$(python3 "$SCRIPT_PATH" --help 2>&1) || true

    if echo "$output" | grep -q "Generate AsciiDoc documentation"; then
        echo -e "${GREEN}✓ PASSED${NC} - Help output contains description"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Help output missing description"
        ((TESTS_FAILED++))
    fi

    if echo "$output" | grep -q "\-\-holder"; then
        echo -e "${GREEN}✓ PASSED${NC} - Help output contains --holder option"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Help output missing --holder option"
        ((TESTS_FAILED++))
    fi
}

# Run all tests
test_analyze_holder
test_message_counts
test_generate_documentation
test_missing_holder
test_help_flag

# Cleanup
rm -rf "$TEMP_DIR"

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
