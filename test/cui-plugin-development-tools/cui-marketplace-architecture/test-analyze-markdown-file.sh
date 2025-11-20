#!/bin/bash
# Test suite for analyze-markdown-file.sh
#
# Usage: ./test-analyze-markdown-file.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/analyze-markdown-file.sh"
TEST_FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run a test
run_test() {
    local test_name="$1"
    local test_file="$2"
    local expected_lines="$3"
    local expected_ci_rule="$4"
    local expected_frontmatter="$5"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test: $test_name ... "

    # Run script
    result=$("$SCRIPT_UNDER_TEST" "$test_file" 2>&1)

    # Parse JSON
    actual_lines=$(echo "$result" | jq -r '.metrics.line_count')
    actual_ci=$(echo "$result" | jq -r '.continuous_improvement_rule.present')
    actual_fm=$(echo "$result" | jq -r '.frontmatter.present')

    # Verify line count matches wc -l
    wc_lines=$(wc -l < "$test_file" | tr -d ' ')

    if [ "$actual_lines" != "$wc_lines" ]; then
        echo -e "${RED}FAIL${NC}"
        echo "  Line count mismatch: script=$actual_lines, wc -l=$wc_lines"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Verify expected values
    if [ "$actual_lines" != "$expected_lines" ] || \
       [ "$actual_ci" != "$expected_ci_rule" ] || \
       [ "$actual_fm" != "$expected_frontmatter" ]; then
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: lines=$expected_lines, ci=$expected_ci_rule, fm=$expected_frontmatter"
        echo "  Actual:   lines=$actual_lines, ci=$actual_ci, fm=$actual_fm"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    echo -e "${GREEN}PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test with real marketplace files
test_real_files() {
    echo ""
    echo "=== Testing with real marketplace files ==="
    echo ""

    # Test known files from the marketplace
    local test_cases=(
        "plugin-diagnose-skills.md|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md"
        "orchestrate-language.md|$PROJECT_ROOT/marketplace/bundles/cui-task-workflow/commands/orchestrate-language.md"
        "js-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-frontend-expert/commands/js-implement-code.md"
        "java-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-java-expert/commands/java-implement-code.md"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file <<< "$test_case"

        if [ ! -f "$file" ]; then
            echo "SKIP: $name (file not found)"
            continue
        fi

        # Get actual line count
        lines=$(wc -l < "$file" | tr -d ' ')

        # Determine if CI rule and frontmatter present
        has_ci="false"
        if grep -qi "CONTINUOUS IMPROVEMENT" "$file"; then
            has_ci="true"
        fi

        has_fm="false"
        if head -1 "$file" | grep -q "^---$"; then
            has_fm="true"
        fi

        run_test "$name" "$file" "$lines" "$has_ci" "$has_fm"
    done
}

# Test classification logic
test_classification() {
    echo ""
    echo "=== Testing bloat classification ==="
    echo ""

    local test_cases=(
        "plugin-diagnose-skills.md|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md|LARGE"
        "js-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-frontend-expert/commands/js-implement-code.md|BLOATED"
        "java-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-java-expert/commands/java-implement-code.md|BLOATED"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file expected_class <<< "$test_case"

        if [ ! -f "$file" ]; then
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Classify: $name ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        lines=$(echo "$result" | jq -r '.metrics.line_count')

        # Apply classification logic
        if [ "$lines" -gt 500 ]; then
            actual_class="BLOATED"
        elif [ "$lines" -gt 400 ]; then
            actual_class="LARGE"
        else
            actual_class="ACCEPTABLE"
        fi

        if [ "$actual_class" == "$expected_class" ]; then
            echo -e "${GREEN}PASS${NC} ($lines lines = $actual_class)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}"
            echo "  Expected: $expected_class, Got: $actual_class ($lines lines)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done
}

# Main test execution
main() {
    echo "========================================"
    echo "Test Suite: analyze-markdown-file.sh"
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

    # Run tests
    test_real_files
    test_classification

    # Print summary
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo "Total:  $TESTS_RUN"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
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
