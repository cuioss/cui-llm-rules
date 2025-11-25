#!/bin/bash
# Tests for verify-implementation-params.py script
# Tests task description validation and clarity scoring

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/../../marketplace/bundles/cui-java-expert/skills/cui-java-core/scripts/verify-implementation-params.py"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${YELLOW}⊘ SKIPPED${NC} - Script not yet implemented: $SCRIPT_PATH"
    echo ""
    echo "This test suite documents expected behavior for verify-implementation-params.py"
    echo ""
    echo "Expected functionality:"
    echo "  - Analyze task description for clarity and completeness"
    echo "  - Score description (0-100) based on specificity"
    echo "  - Identify missing information"
    echo "  - Detect ambiguities and vague scope"
    echo "  - Return JSON with verification_passed boolean"
    echo ""
    echo "Expected input:"
    echo '  {"description": "Add JWT token validation to the authentication service"}'
    echo ""
    echo "Expected output format:"
    echo '  {'
    echo '    "status": "success",'
    echo '    "data": {'
    echo '      "verification_passed": true,'
    echo '      "clarity_score": 85,'
    echo '      "missing_information": [],'
    echo '      "ambiguities": [],'
    echo '      "vague_scope": false'
    echo '    }'
    echo '  }'
    exit 0
fi

test_clear_description() {
    echo "Test: Validate clear task description"

    local description="Add JWT token validation to the authentication service. The validator should check token expiry, issuer, and signature using RS256 algorithm."
    local output
    output=$(python3 "$SCRIPT_PATH" --description "$description" 2>&1)

    if echo "$output" | jq -e '.data.verification_passed == true' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Clear description passes validation"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Clear description should pass"
        ((TESTS_FAILED++))
    fi

    # Check clarity score is high
    local score
    score=$(echo "$output" | jq -r '.data.clarity_score' 2>/dev/null || echo "0")
    if [ "$score" -ge 70 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Clarity score is high: $score"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Clarity score too low: $score"
        ((TESTS_FAILED++))
    fi
}

test_vague_description() {
    echo ""
    echo "Test: Detect vague task description"

    local description="Fix the thing"
    local output
    output=$(python3 "$SCRIPT_PATH" --description "$description" 2>&1)

    if echo "$output" | jq -e '.data.verification_passed == false' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Vague description fails validation"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Vague description should fail"
        ((TESTS_FAILED++))
    fi

    # Check vague_scope flag
    if echo "$output" | jq -e '.data.vague_scope == true' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Vague scope detected"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Vague scope not detected"
        ((TESTS_FAILED++))
    fi
}

test_ambiguous_description() {
    echo ""
    echo "Test: Detect ambiguous requirements"

    local description="Add validation to the service. It should validate tokens or maybe sessions."
    local output
    output=$(python3 "$SCRIPT_PATH" --description "$description" 2>&1)

    # Check for ambiguities
    if echo "$output" | jq -e '.data.ambiguities | length > 0' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Ambiguities detected"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Ambiguities not detected"
        ((TESTS_FAILED++))
    fi
}

test_missing_information() {
    echo ""
    echo "Test: Identify missing information"

    local description="Update the authentication"
    local output
    output=$(python3 "$SCRIPT_PATH" --description "$description" 2>&1)

    # Check for missing_information
    if echo "$output" | jq -e '.data.missing_information | length > 0' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Missing information identified"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Missing information not identified"
        ((TESTS_FAILED++))
    fi

    # Should fail verification
    if echo "$output" | jq -e '.data.verification_passed == false' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - Fails validation due to missing info"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Should fail validation"
        ((TESTS_FAILED++))
    fi
}

test_json_structure() {
    echo ""
    echo "Test: Verify JSON output structure"

    local description="Add token validation"
    local output
    output=$(python3 "$SCRIPT_PATH" --description "$description" 2>&1)

    # Check for required top-level fields
    if echo "$output" | jq -e 'has("status") and has("data")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - JSON has required top-level fields"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - JSON missing required fields"
        ((TESTS_FAILED++))
    fi

    # Check for data structure
    if echo "$output" | jq -e '.data | has("verification_passed") and has("clarity_score")' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC} - JSON data has required fields"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - JSON data missing required fields"
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
echo "Testing verify-implementation-params.py"
echo "=========================================="
echo ""

test_clear_description
test_vague_description
test_ambiguous_description
test_missing_information
test_json_structure
test_help_flag

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Tests Skipped: $TESTS_SKIPPED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
