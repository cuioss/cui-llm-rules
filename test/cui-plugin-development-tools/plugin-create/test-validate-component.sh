#!/bin/bash
# Test suite for validate-component.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="marketplace/bundles/cui-plugin-development-tools/skills/plugin-create/scripts/validate-component.py"
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
    local fixture="$3"
    local component_type="$4"
    local expected_valid="$5"
    local check_errors="$6"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}Test $test_num: $test_name${NC}"

    # Run validation script
    result=$(python3 "$SCRIPT" "$FIXTURES/$fixture" "$component_type" 2>&1 || true)

    # Parse JSON output
    valid=$(echo "$result" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('valid', False))" 2>/dev/null || echo "parse_error")

    if [ "$valid" = "parse_error" ]; then
        echo -e "${RED}✗ Test $test_num FAILED - Invalid JSON output${NC}"
        echo "Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Check if valid matches expected
    if [ "$valid" = "$expected_valid" ]; then
        # If we need to check specific errors, do additional validation
        if [ -n "$check_errors" ]; then
            errors=$(echo "$result" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data.get('errors', [])))")
            if echo "$errors" | grep -q "$check_errors"; then
                echo -e "${GREEN}✓ Test $test_num passed${NC}"
                TESTS_PASSED=$((TESTS_PASSED + 1))
                return 0
            else
                echo -e "${RED}✗ Test $test_num FAILED - Expected error pattern not found${NC}"
                echo "Expected pattern: $check_errors"
                echo "Actual errors: $errors"
                TESTS_FAILED=$((TESTS_FAILED + 1))
                return 1
            fi
        fi
        echo -e "${GREEN}✓ Test $test_num passed${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ Test $test_num FAILED${NC}"
        echo "Expected valid=$expected_valid, got valid=$valid"
        echo "Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "========================================"
echo "validate-component.py Test Suite"
echo "========================================"
echo ""

# Test 1.1: Valid agent
run_test "1.1" "Valid agent validation" "valid-agent.md" "agent" "True" ""

# Test 1.2: Valid agent without model
run_test "1.2" "Valid agent without model" "valid-agent-no-model.md" "agent" "True" ""

# Test 1.3: Agent with prohibited Task tool
run_test "1.3" "Agent with prohibited Task tool" "invalid-agent-task-tool.md" "agent" "False" "Task tool"

# Test 1.4: Agent with self-invocation pattern
run_test "1.4" "Agent with self-invocation pattern" "invalid-agent-self-invoke.md" "agent" "False" "self-invocation"

# Test 1.5: Agent missing frontmatter
run_test "1.5" "Agent missing frontmatter" "invalid-agent-no-frontmatter.md" "agent" "False" "frontmatter"

# Test 1.6: Agent with invalid YAML
run_test "1.6" "Agent with invalid YAML" "invalid-agent-bad-yaml.md" "agent" "False" "YAML"

# Test 1.7: Agent with array syntax tools (should warn but pass)
run_test "1.7" "Agent with array syntax tools" "invalid-agent-array-tools.md" "agent" "True" ""

# Test 1.8: Valid command
run_test "1.8" "Valid command validation" "valid-command.md" "command" "True" ""

# Test 1.9: Command missing required section
run_test "1.9" "Command missing WORKFLOW section" "invalid-command-missing-section.md" "command" "False" "WORKFLOW"

# Test 1.10: Valid skill
run_test "1.10" "Valid skill validation" "valid-skill.md" "skill" "True" ""

# Test 1.11: Skill with bad frontmatter
run_test "1.11" "Skill with bad frontmatter" "invalid-skill-bad-frontmatter.md" "skill" "False" "name"

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
