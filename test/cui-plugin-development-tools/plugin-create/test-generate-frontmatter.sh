#!/bin/bash
# Test suite for generate-frontmatter.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="marketplace/bundles/cui-plugin-development-tools/skills/plugin-create/scripts/generate-frontmatter.py"
FIXTURES="$SCRIPT_DIR/fixtures"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run a test
run_test() {
    local test_num="$1"
    local test_name="$2"
    local component_type="$3"
    local input_file="$4"
    local expected_pattern="$5"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}Test $test_num: $test_name${NC}"

    # Read input JSON
    input_json=$(cat "$FIXTURES/$input_file")

    # Run generation script
    result=$(python3 "$SCRIPT" "$component_type" "$input_json" 2>&1 || true)

    # Check if result contains expected pattern
    if echo "$result" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✓ Test $test_num passed${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ Test $test_num FAILED${NC}"
        echo "Expected pattern: $expected_pattern"
        echo "Actual output:"
        echo "$result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Helper function to check for comma-separated tools
check_comma_separated() {
    local test_num="$1"
    local test_name="$2"
    local component_type="$3"
    local input_file="$4"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}Test $test_num: $test_name${NC}"

    input_json=$(cat "$FIXTURES/$input_file")
    result=$(python3 "$SCRIPT" "$component_type" "$input_json" 2>&1 || true)

    # Check that tools are comma-separated, not array syntax
    if echo "$result" | grep -qE "tools: [A-Za-z]+(, [A-Za-z]+)*"; then
        # Check that array syntax is NOT present
        if echo "$result" | grep -q "\["; then
            echo -e "${RED}✗ Test $test_num FAILED - Array syntax found${NC}"
            echo "Output: $result"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            return 1
        fi
        echo -e "${GREEN}✓ Test $test_num passed - Comma-separated format correct${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ Test $test_num FAILED - Comma-separated format not found${NC}"
        echo "Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "========================================"
echo "generate-frontmatter.py Test Suite"
echo "========================================"
echo ""

# Test 2.1: Agent frontmatter with all fields
run_test "2.1" "Agent frontmatter with all fields" "agent" "agent-answers-full.json" "model: sonnet"
check_comma_separated "2.1a" "Agent tools comma-separated" "agent" "agent-answers-full.json"

# Test 2.2: Agent without optional model
run_test "2.2" "Agent without optional model" "agent" "agent-answers-no-model.json" "name: test-agent"

# Test 2.3: Special characters in description
run_test "2.3" "Special characters in description" "agent" "agent-answers-special-chars.json" "quotes"

# Test 2.4: Command frontmatter (no tools field)
TESTS_RUN=$((TESTS_RUN + 1))
echo -e "${YELLOW}Test 2.4: Command frontmatter${NC}"
input_json=$(cat "$FIXTURES/command-answers.json")
result=$(python3 "$SCRIPT" "command" "$input_json" 2>&1 || true)
if echo "$result" | grep -q "name: test-command" && ! echo "$result" | grep -q "tools:"; then
    echo -e "${GREEN}✓ Test 2.4 passed - No tools field for commands${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Test 2.4 FAILED${NC}"
    echo "Output: $result"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 2.5: Skill with allowed-tools
run_test "2.5" "Skill with allowed-tools" "skill" "skill-answers-with-tools.json" "allowed-tools: Read, Grep"

# Test 2.6: Skill without tools
TESTS_RUN=$((TESTS_RUN + 1))
echo -e "${YELLOW}Test 2.6: Skill without tools${NC}"
input_json=$(cat "$FIXTURES/skill-answers-no-tools.json")
result=$(python3 "$SCRIPT" "skill" "$input_json" 2>&1 || true)
if echo "$result" | grep -q "name: test-skill" && ! echo "$result" | grep -q "allowed-tools:"; then
    echo -e "${GREEN}✓ Test 2.6 passed - Optional allowed-tools omitted${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Test 2.6 FAILED${NC}"
    echo "Output: $result"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 2.7: Empty tools array (should error or warn)
TESTS_RUN=$((TESTS_RUN + 1))
echo -e "${YELLOW}Test 2.7: Empty tools array${NC}"
result=$(python3 "$SCRIPT" "agent" '{"name": "test", "description": "Test", "tools": []}' 2>&1 || true)
if echo "$result" | grep -qiE "(error|warning|at least one)"; then
    echo -e "${GREEN}✓ Test 2.7 passed - Empty tools array handled${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Test 2.7 FAILED - Should error on empty tools${NC}"
    echo "Output: $result"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 2.8: Invalid component type
TESTS_RUN=$((TESTS_RUN + 1))
echo -e "${YELLOW}Test 2.8: Invalid component type${NC}"
result=$(python3 "$SCRIPT" "invalid-type" '{"name": "test", "description": "Test"}' 2>&1 || true)
if echo "$result" | grep -qiE "(error|invalid|unknown)"; then
    echo -e "${GREEN}✓ Test 2.8 passed - Invalid type detected${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Test 2.8 FAILED - Should error on invalid type${NC}"
    echo "Output: $result"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "========================================"
echo "Test Results"
echo "========================================"
echo "Tests run:    $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    exit 1
else
    echo -e "Tests failed: ${GREEN}$TESTS_FAILED${NC}"
    echo ""
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
