#!/bin/bash
# Test suite for analyze-skill-structure.sh (plugin-doctor version)
#
# Tests for improved reference detection:
# 1. Table-format references (| `script.py` |)
# 2. Example code blocks (should be ignored)
# 3. Cross-skill reference notation (bundle:references/file.md)
#
# Usage: ./test-analyze-skill-structure.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-doctor/scripts/analyze-skill-structure.sh"
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
        echo -e "${GREEN}PASS${NC} (score=$actual_score >= $min_score)"
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
        echo "  Full output:"
        echo "$result" | jq "$json_path"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# TEST SUITES
# ============================================================================

test_table_format_references() {
    echo ""
    echo "=== Test Suite: Table-Format References ==="
    echo ""
    echo "Verifies that scripts/references in markdown tables are detected."
    echo ""

    local test_dir="$FIXTURES_DIR/table-references"

    # Test: All table-referenced files should be detected (no unreferenced files)
    run_array_test "table-refs: no unreferenced files" \
        "$test_dir" \
        ".standards_files.unreferenced_files" \
        0

    # Test: No missing files (all referenced files exist)
    run_array_test "table-refs: no missing files" \
        "$test_dir" \
        ".standards_files.missing_files" \
        0

    # Test: Perfect score (all files properly referenced)
    run_score_test "table-refs: perfect score" \
        "$test_dir" \
        100
}

test_code_block_examples() {
    echo ""
    echo "=== Test Suite: Code Block Examples ==="
    echo ""
    echo "Verifies that example paths in code blocks are NOT detected as real references."
    echo ""

    local test_dir="$FIXTURES_DIR/code-block-examples"

    # Test: Should NOT report code block examples as missing files
    # The code block contains: scripts/analyzer.py, references/core-principles.md, assets/template.html
    # These don't exist and should NOT be flagged as missing (they're examples)
    run_array_test "code-block: no false positive missing files" \
        "$test_dir" \
        ".standards_files.missing_files" \
        0

    # Test: The actual reference (references/actual-guide.md) should be detected
    run_array_test "code-block: no unreferenced files" \
        "$test_dir" \
        ".standards_files.unreferenced_files" \
        0

    # Test: Perfect score (examples ignored, real refs detected)
    run_score_test "code-block: perfect score" \
        "$test_dir" \
        100
}

test_cross_skill_references() {
    echo ""
    echo "=== Test Suite: Cross-Skill References ==="
    echo ""
    echo "Verifies that cross-skill refs (bundle:references/file.md) are NOT flagged as missing."
    echo ""

    local test_dir="$FIXTURES_DIR/cross-skill-references"

    # Test: Cross-skill reference should NOT be flagged as missing
    # plugin-architecture:references/script-standards.md is a cross-skill ref, not a local file
    run_array_test "cross-skill: no false positive missing files" \
        "$test_dir" \
        ".standards_files.missing_files" \
        0

    # Test: Local reference should be detected
    run_array_test "cross-skill: no unreferenced files" \
        "$test_dir" \
        ".standards_files.unreferenced_files" \
        0

    # Test: Perfect score (cross-skill refs handled correctly)
    run_score_test "cross-skill: perfect score" \
        "$test_dir" \
        100
}

test_real_skills() {
    echo ""
    echo "=== Test Suite: Real Skills Validation ==="
    echo ""
    echo "Verifies that real marketplace skills pass with improved detection."
    echo ""

    # Test plugin-architecture skill (has example code blocks)
    local dir="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-architecture"
    if [ -d "$dir" ]; then
        # After fix: Should not flag example code as missing files
        run_score_test "real: plugin-architecture (should not flag examples)" \
            "$dir" \
            90
    else
        echo "SKIP: plugin-architecture skill not found"
    fi

    # Test plugin-doctor skill (has table-format refs and cross-skill refs)
    dir="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-doctor"
    if [ -d "$dir" ]; then
        # After fix: Should detect table refs and handle cross-skill refs
        run_score_test "real: plugin-doctor (should detect table refs)" \
            "$dir" \
            90
    else
        echo "SKIP: plugin-doctor skill not found"
    fi

    # Test plugin-create skill (has template files in assets)
    # Note: plugin-create has 2 legitimately unreferenced files (bundle-guide.md, bundle-structure.json)
    # that are documented but not actively used in workflows. Score 80 is acceptable.
    dir="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-create"
    if [ -d "$dir" ]; then
        run_score_test "real: plugin-create (has some documented-only files)" \
            "$dir" \
            80
    else
        echo "SKIP: plugin-create skill not found"
    fi
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    echo "========================================"
    echo "Test Suite: analyze-skill-structure.sh"
    echo "(plugin-doctor version)"
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
    test_table_format_references
    test_code_block_examples
    test_cross_skill_references
    test_real_skills

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
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

# Run main
main
