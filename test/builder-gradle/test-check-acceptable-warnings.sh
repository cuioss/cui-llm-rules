#!/bin/bash
# Test suite for check-acceptable-warnings.py
# Tests warning categorization against acceptable patterns

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/builder-gradle/skills/builder-gradle-rules/scripts/check-acceptable-warnings.py"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    if [[ "$expected" == "$actual" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

assert_json_field() {
    local json="$1"
    local field="$2"
    local expected="$3"
    local message="$4"

    local actual=$(echo "$json" | python3 -c "import sys, json; print(json.load(sys.stdin)$field)" 2>/dev/null)

    if [[ "$expected" == "$actual" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Field: $field"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    if [[ "$expected" -eq "$actual" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Expected exit code: $expected"
        echo "  Actual exit code:   $actual"
        return 1
    fi
}

run_test() {
    local test_name="$1"
    local test_func="$2"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "  Testing: $test_name... "

    if $test_func; then
        echo -e "${GREEN}PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# =============================================================================
# TEST CASES
# =============================================================================

test_categorize_mixed_warnings() {
    local output
    local exit_code
    local warnings_json
    local acceptable_json

    warnings_json=$(cat "$FIXTURES_DIR/parsed-output-with-warnings.json")
    acceptable_json='{"platform_specific": ["*platform encoding*"], "openrewrite": ["*openrewrite*"]}'

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" \
        --acceptable-warnings "$acceptable_json" 2>/dev/null)
    exit_code=$?

    # Should exit 1 because there are fixable warnings
    assert_exit_code 1 $exit_code "Mixed warnings should exit with 1" || return 1
    assert_json_field "$output" "['success']" "True" "Success should be True" || return 1
}

test_no_warnings() {
    local output
    local exit_code
    local warnings_json

    warnings_json=$(cat "$FIXTURES_DIR/parsed-output-no-warnings.json")

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "No warnings should exit with 0" || return 1
    assert_json_field "$output" "['success']" "True" "Success should be True" || return 1
    assert_json_field "$output" "['total']" "0" "Should have 0 warnings" || return 1
    assert_json_field "$output" "['fixable']" "0" "Should have 0 fixable" || return 1
}

test_all_acceptable() {
    local output
    local exit_code
    local warnings_json
    local acceptable_json

    warnings_json=$(cat "$FIXTURES_DIR/parsed-output-all-acceptable.json")
    acceptable_json='{"platform_specific": ["*platform encoding*"], "openrewrite": ["*openrewrite*"]}'

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" \
        --acceptable-warnings "$acceptable_json" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "All acceptable should exit with 0" || return 1
    assert_json_field "$output" "['success']" "True" "Success should be True" || return 1
    assert_json_field "$output" "['fixable']" "0" "Should have 0 fixable" || return 1
}

test_javadoc_always_fixable() {
    # JavaDoc warnings should ALWAYS be fixable, never acceptable
    local output
    local warnings_json
    local acceptable_json

    warnings_json=$(cat "$FIXTURES_DIR/parsed-output-with-warnings.json")
    # Even if we try to accept javadoc warnings, they should still be fixable
    acceptable_json='{"javadoc": ["*"]}'

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" \
        --acceptable-warnings "$acceptable_json" 2>/dev/null)

    # Check fixable count includes javadoc warnings
    local fixable
    fixable=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['fixable'])")

    if [[ "$fixable" -gt 0 ]]; then
        return 0
    else
        echo -e "${RED}JavaDoc warnings should be fixable${NC}"
        return 1
    fi
}

test_deprecation_always_fixable() {
    # Deprecation warnings should ALWAYS be fixable
    local output
    local warnings_json

    warnings_json=$(cat "$FIXTURES_DIR/parsed-output-with-warnings.json")

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" 2>/dev/null)

    # Get fixable_warnings array and check for deprecation
    local has_deprecation=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fixable = data['categorized']['fixable']
has_deprecation = any(w.get('type') == 'deprecation_warning' for w in fixable)
print('true' if has_deprecation else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_deprecation" "Deprecation warnings should be in fixable list" || return 1
}

test_unchecked_always_fixable() {
    # Unchecked warnings should ALWAYS be fixable
    local output
    local warnings_json

    warnings_json=$(cat "$FIXTURES_DIR/parsed-output-with-warnings.json")

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" 2>/dev/null)

    local has_unchecked=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fixable = data['categorized']['fixable']
has_unchecked = any(w.get('type') == 'unchecked_warning' for w in fixable)
print('true' if has_unchecked else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_unchecked" "Unchecked warnings should be in fixable list" || return 1
}

test_pattern_matching_contains() {
    # Test contains pattern matching (*pattern*)
    local output
    local warnings_json
    local acceptable_json

    warnings_json='{"warnings": [{"type": "other", "message": "Using platform encoding UTF-8", "severity": "WARNING"}]}'
    acceptable_json='{"platform": ["*platform*"]}'

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" \
        --acceptable-warnings "$acceptable_json" 2>/dev/null)

    local acceptable_count
    acceptable_count=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['acceptable'])")

    assert_equals "1" "$acceptable_count" "Contains pattern should match" || return 1
}

test_pattern_matching_prefix() {
    # Test prefix pattern matching (pattern*)
    local output
    local warnings_json
    local acceptable_json

    warnings_json='{"warnings": [{"type": "other", "message": "Could not resolve artifact", "severity": "WARNING"}]}'
    acceptable_json='{"dependency": ["Could not resolve*"]}'

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" \
        --acceptable-warnings "$acceptable_json" 2>/dev/null)

    local acceptable_count
    acceptable_count=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['acceptable'])")

    assert_equals "1" "$acceptable_count" "Prefix pattern should match" || return 1
}

test_empty_acceptable_patterns() {
    local output
    local exit_code
    local warnings_json

    warnings_json=$(cat "$FIXTURES_DIR/parsed-output-with-warnings.json")

    output=$(echo "$warnings_json" | python3 "$SCRIPT_PATH" \
        --acceptable-warnings '{}' 2>/dev/null)
    exit_code=$?

    # Should still categorize - "other" types become unknown
    assert_exit_code 1 $exit_code "Should exit 1 with fixable warnings" || return 1
    assert_json_field "$output" "['success']" "True" "Success should be True" || return 1
}

test_stdin_input() {
    local output
    local exit_code

    output=$(echo '{"warnings": []}' | python3 "$SCRIPT_PATH" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "Stdin input should work" || return 1
    assert_json_field "$output" "['success']" "True" "Success should be True" || return 1
}

# =============================================================================
# MAIN
# =============================================================================

echo ""
echo "========================================"
echo "  check-acceptable-warnings.py Tests"
echo "========================================"
echo ""

# Verify script exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo -e "${RED}ERROR: Script not found: $SCRIPT_PATH${NC}"
    exit 1
fi

# Verify fixtures exist
for fixture in parsed-output-with-warnings.json parsed-output-no-warnings.json \
               parsed-output-all-acceptable.json; do
    if [[ ! -f "$FIXTURES_DIR/$fixture" ]]; then
        echo -e "${RED}ERROR: Fixture not found: $FIXTURES_DIR/$fixture${NC}"
        exit 1
    fi
done

echo "Running tests..."
echo ""

# Run all tests
run_test "categorize mixed warnings" test_categorize_mixed_warnings
run_test "no warnings" test_no_warnings
run_test "all acceptable" test_all_acceptable
run_test "javadoc always fixable" test_javadoc_always_fixable
run_test "deprecation always fixable" test_deprecation_always_fixable
run_test "unchecked always fixable" test_unchecked_always_fixable
run_test "pattern matching contains" test_pattern_matching_contains
run_test "pattern matching prefix" test_pattern_matching_prefix
run_test "empty acceptable patterns" test_empty_acceptable_patterns
run_test "stdin input" test_stdin_input

echo ""
echo "========================================"
echo "  Results: $TESTS_PASSED/$TESTS_RUN passed"
echo "========================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}  $TESTS_FAILED test(s) failed${NC}"
    exit 1
else
    echo -e "${GREEN}  All tests passed!${NC}"
    exit 0
fi
