#!/bin/bash
# Test suite for scan-marketplace-inventory.sh
#
# Usage: ./test-scan-marketplace-inventory.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/marketplace-inventory/scripts/scan-marketplace-inventory.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
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
    local check_field="$2"
    local expected_value="$3"
    shift 3
    # Remaining arguments are script parameters

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test: $test_name ... "

    # Run script and capture output
    if ! result=$("$SCRIPT_UNDER_TEST" "$@" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        echo "  Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON
    actual_value=$(echo "$result" | jq -r "$check_field")

    # Compare
    if [ "$actual_value" = "$expected_value" ]; then
        echo -e "${GREEN}PASS${NC}"
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

run_comparison_test() {
    local test_name="$1"
    local check_field="$2"
    local min_value="$3"
    shift 3
    # Remaining arguments are script parameters

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test: $test_name ... "

    # Run script
    if ! result=$("$SCRIPT_UNDER_TEST" "$@" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON
    actual_value=$(echo "$result" | jq -r "$check_field")

    # Compare
    if (( actual_value >= min_value )); then
        echo -e "${GREEN}PASS${NC} ($check_field=$actual_value)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: $check_field >= $min_value"
        echo "  Actual:   $check_field = $actual_value"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# TEST SUITES
# ============================================================================

test_basic_discovery() {
    echo ""
    echo "=== Testing basic discovery ==="
    echo ""

    # Test 1: Default scan finds bundles
    run_comparison_test "default-scan-finds-bundles" \
        ".statistics.total_bundles" 5

    # Test 2: Finds agents
    run_comparison_test "default-scan-finds-agents" \
        ".statistics.total_agents" 20

    # Test 3: Finds commands
    run_comparison_test "default-scan-finds-commands" \
        ".statistics.total_commands" 40

    # Test 4: Finds skills
    run_comparison_test "default-scan-finds-skills" \
        ".statistics.total_skills" 20

    # Test 5: Scope is marketplace
    run_test "default-scope-is-marketplace" \
        ".scope" "marketplace"
}

test_resource_filtering() {
    echo ""
    echo "=== Testing resource type filtering ==="
    echo ""

    # Test 1: Agents only
    run_test "agents-only-no-commands" \
        ".statistics.total_commands" "0" \
        --resource-types agents

    run_test "agents-only-no-skills" \
        ".statistics.total_skills" "0" \
        --resource-types agents

    run_comparison_test "agents-only-has-agents" \
        ".statistics.total_agents" 20 \
        --resource-types agents

    # Test 2: Commands only
    run_test "commands-only-no-agents" \
        ".statistics.total_agents" "0" \
        --resource-types commands

    run_comparison_test "commands-only-has-commands" \
        ".statistics.total_commands" 40 \
        --resource-types commands

    # Test 3: Skills only
    run_test "skills-only-no-agents" \
        ".statistics.total_agents" "0" \
        --resource-types skills

    run_comparison_test "skills-only-has-skills" \
        ".statistics.total_skills" 20 \
        --resource-types skills

    # Test 4: Multiple types (agents,commands)
    run_comparison_test "agents-commands-has-both" \
        ".statistics.total_agents" 20 \
        --resource-types agents,commands
}

test_description_extraction() {
    echo ""
    echo "=== Testing description extraction ==="
    echo ""

    # Test 1: Without descriptions (default)
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: no-descriptions-returns-null ... "

    result=$("$SCRIPT_UNDER_TEST" 2>&1)

    # Check if any agent has description field
    has_desc_count=$(echo "$result" | jq '[.bundles[].agents[] | select(has("description"))] | length')

    if [ "$has_desc_count" -eq 0 ]; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (description field present without --include-descriptions)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    # Test 2: With descriptions enabled
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: with-descriptions-extracts-desc ... "

    result=$("$SCRIPT_UNDER_TEST" --include-descriptions 2>&1)

    # Check if descriptions are present
    desc_count=$(echo "$result" | jq '[.bundles[].agents[].description] | map(select(. != null)) | length')

    if (( desc_count > 0 )); then
        echo -e "${GREEN}PASS${NC} (found $desc_count descriptions)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (no descriptions found)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

test_json_validity() {
    echo ""
    echo "=== Testing JSON validity ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: default-produces-valid-json ... "

    if result=$("$SCRIPT_UNDER_TEST" 2>&1) && echo "$result" | jq . > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: with-descriptions-produces-valid-json ... "

    if result=$("$SCRIPT_UNDER_TEST" --include-descriptions 2>&1) && echo "$result" | jq . > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: filtered-produces-valid-json ... "

    if result=$("$SCRIPT_UNDER_TEST" --resource-types agents 2>&1) && echo "$result" | jq . > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

test_bundle_structure() {
    echo ""
    echo "=== Testing bundle structure ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: bundles-have-required-fields ... "

    result=$("$SCRIPT_UNDER_TEST" 2>&1)

    # Check first bundle has required fields
    has_name=$(echo "$result" | jq '.bundles[0] | has("name")')
    has_path=$(echo "$result" | jq '.bundles[0] | has("path")')
    has_agents=$(echo "$result" | jq '.bundles[0] | has("agents")')
    has_commands=$(echo "$result" | jq '.bundles[0] | has("commands")')
    has_skills=$(echo "$result" | jq '.bundles[0] | has("skills")')
    has_stats=$(echo "$result" | jq '.bundles[0] | has("statistics")')

    if [ "$has_name" = "true" ] && [ "$has_path" = "true" ] && \
       [ "$has_agents" = "true" ] && [ "$has_commands" = "true" ] && \
       [ "$has_skills" = "true" ] && [ "$has_stats" = "true" ]; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} (missing required fields)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

test_error_handling() {
    echo ""
    echo "=== Testing error handling ==="
    echo ""

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: invalid-scope-returns-error ... "

    if result=$("$SCRIPT_UNDER_TEST" --scope invalid 2>&1); then
        echo -e "${RED}FAIL${NC} (should have returned error)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    else
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: invalid-resource-type-returns-error ... "

    if result=$("$SCRIPT_UNDER_TEST" --resource-types invalid 2>&1); then
        echo -e "${RED}FAIL${NC} (should have returned error)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    else
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    echo "============================================"
    echo "Test Suite: scan-marketplace-inventory.sh"
    echo "============================================"

    # Change to project root (script expects to run from there)
    cd "$PROJECT_ROOT"

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

    # Run all test suites
    test_basic_discovery
    test_resource_filtering
    test_description_extraction
    test_json_validity
    test_bundle_structure
    test_error_handling

    # Print summary
    echo ""
    echo "============================================"
    echo "Test Summary"
    echo "============================================"
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
