#!/bin/bash
# Test suite for analyze-skill-structure.sh
#
# Usage: ./test-analyze-skill-structure.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/analyze-skill-structure.sh"
FIXTURES_DIR="$SCRIPT_DIR/fixtures/skill-structure"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    local test_dir="$2"
    local check_field="$3"
    local expected_value="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test: $test_name ... "

    # Run script and capture output
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_dir" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        echo "  Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON
    actual_value=$(echo "$result" | jq -r "$check_field")

    # Compare
    if [ "$actual_value" = "$expected_value" ]; then
        echo -e "${GREEN}PASS${NC} ($check_field=$actual_value)"
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

run_score_test() {
    local test_name="$1"
    local test_dir="$2"
    local min_score="$3"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Score: $test_name ... "

    # Run script
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_dir" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON
    actual_score=$(echo "$result" | jq -r '.structure_score')

    # Compare
    if (( actual_score >= min_score )); then
        echo -e "${GREEN}PASS${NC} (score=$actual_score)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: score >= $min_score"
        echo "  Actual:   score = $actual_score"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

run_array_test() {
    local test_name="$1"
    local test_dir="$2"
    local json_path="$3"
    local expected_count="$4"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Array: $test_name ... "

    # Run script
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_dir" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse JSON and count array elements
    actual_count=$(echo "$result" | jq -r "$json_path | length")

    # Compare
    if [ "$actual_count" -eq "$expected_count" ]; then
        echo -e "${GREEN}PASS${NC} (count=$actual_count)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected count: $expected_count"
        echo "  Actual count:   $actual_count"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# TEST SUITES
# ============================================================================

test_fixtures() {
    echo ""
    echo "=== Testing with fixtures ==="
    echo ""

    # Test 1: Perfect skill structure
    run_score_test "perfect-skill" \
        "$FIXTURES_DIR/perfect-skill" \
        100

    run_test "perfect-skill-exists" \
        "$FIXTURES_DIR/perfect-skill" \
        ".skill_md.exists" \
        "true"

    run_test "perfect-skill-yaml-valid" \
        "$FIXTURES_DIR/perfect-skill" \
        ".skill_md.yaml_valid" \
        "true"

    run_array_test "perfect-skill-no-missing" \
        "$FIXTURES_DIR/perfect-skill" \
        ".standards_files.missing_files" \
        0

    run_array_test "perfect-skill-no-unreferenced" \
        "$FIXTURES_DIR/perfect-skill" \
        ".standards_files.unreferenced_files" \
        0

    # Test 2: Missing SKILL.md
    run_test "missing-skill-md" \
        "$FIXTURES_DIR/missing-skill-md" \
        ".skill_md.exists" \
        "false"

    run_score_test "missing-skill-md-low-score" \
        "$FIXTURES_DIR/missing-skill-md" \
        0

    # Test 3: Invalid YAML
    run_test "invalid-yaml-exists" \
        "$FIXTURES_DIR/invalid-yaml" \
        ".skill_md.exists" \
        "true"

    run_test "invalid-yaml-not-valid" \
        "$FIXTURES_DIR/invalid-yaml" \
        ".skill_md.yaml_valid" \
        "false"

    # Test 4: Missing file (referenced but doesn't exist)
    run_array_test "missing-file-has-1-missing" \
        "$FIXTURES_DIR/missing-file" \
        ".standards_files.missing_files" \
        1

    run_score_test "missing-file-loses-points" \
        "$FIXTURES_DIR/missing-file" \
        60  # Should be less than 100

    # Test 5: Unreferenced file (exists but not referenced)
    run_array_test "unreferenced-file-has-1-unreferenced" \
        "$FIXTURES_DIR/unreferenced-file" \
        ".standards_files.unreferenced_files" \
        1

    run_score_test "unreferenced-file-loses-points" \
        "$FIXTURES_DIR/unreferenced-file" \
        60  # Should be less than 100
}

test_real_skills() {
    echo ""
    echo "=== Testing with real skill files ==="
    echo ""

    # Test with cui-java-core skill
    local dir="$PROJECT_ROOT/marketplace/bundles/cui-java-expert/skills/cui-java-core"
    if [ -d "$dir" ]; then
        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Real skill: cui-java-core ... "

        result=$("$SCRIPT_UNDER_TEST" "$dir" 2>&1)
        score=$(echo "$result" | jq -r '.structure_score')
        missing_count=$(echo "$result" | jq -r '.standards_files.missing_files | length')

        if (( score >= 90 )) && [ "$missing_count" -eq 0 ]; then
            echo -e "${GREEN}PASS${NC} (score=$score, no missing files)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC} (score=$score, missing=$missing_count)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo "SKIP: cui-java-core skill not found"
    fi

    # Test with cui-marketplace-architecture skill
    dir="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture"
    if [ -d "$dir" ]; then
        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Real skill: cui-marketplace-architecture ... "

        result=$("$SCRIPT_UNDER_TEST" "$dir" 2>&1)
        score=$(echo "$result" | jq -r '.structure_score')

        if (( score >= 70 )); then
            echo -e "${GREEN}PASS${NC} (score=$score)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC} (score=$score)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo "SKIP: cui-marketplace-architecture skill not found"
    fi
}

test_json_validity() {
    echo ""
    echo "=== Testing JSON validity for all skills ==="
    echo ""

    local dirs=(
        "$PROJECT_ROOT"/marketplace/bundles/*/skills/*
    )
    local valid_count=0
    local invalid_count=0

    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))

        # Try to run script and parse JSON
        if result=$("$SCRIPT_UNDER_TEST" "$dir" 2>&1) && echo "$result" | jq . > /dev/null 2>&1; then
            valid_count=$((valid_count + 1))
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}: Invalid JSON for $(basename "$(dirname "$dir")")/$(basename "$dir")"
            invalid_count=$((invalid_count + 1))
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done

    echo "JSON validity: $valid_count valid, $invalid_count invalid"
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    echo "========================================"
    echo "Test Suite: analyze-skill-structure.sh"
    echo "========================================"

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

    # Check fixtures exist
    if [ ! -d "$FIXTURES_DIR" ]; then
        echo -e "${RED}ERROR: Fixtures directory not found: $FIXTURES_DIR${NC}"
        exit 1
    fi

    # Run all test suites
    test_fixtures
    test_real_skills
    test_json_validity

    # Print summary
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
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
