#!/bin/bash
# Test suite for check-acceptable-warnings.py
# Tests warning categorization against acceptable patterns

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/builder-maven/skills/builder-maven-rules/scripts/check-acceptable-warnings.py"
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

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-with-warnings.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)
    exit_code=$?

    # Should exit 1 because there are fixable warnings
    assert_exit_code 1 $exit_code "Mixed warnings should exit with 1" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['total_warnings']" "7" "Should have 7 total warnings" || return 1
    # javadoc (2) + deprecation (1) + unchecked (1) = 4 fixable (ALWAYS_FIXABLE_TYPES)
    assert_json_field "$output" "['data']['fixable']" "4" "Should have 4 fixable warnings" || return 1
    # openrewrite_info (1) + "Using platform encoding" (1, matches config) = 2 acceptable
    assert_json_field "$output" "['data']['acceptable']" "2" "Should have 2 acceptable warnings" || return 1
    # "The POM for com.example:some-lib" doesn't match config pattern (different artifact)
    assert_json_field "$output" "['data']['unknown']" "1" "Should have 1 unknown warning" || return 1
}

test_no_warnings() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-no-warnings.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "No warnings should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['total_warnings']" "0" "Should have 0 warnings" || return 1
    assert_json_field "$output" "['data']['fixable']" "0" "Should have 0 fixable" || return 1
    assert_json_field "$output" "['data']['acceptable']" "0" "Should have 0 acceptable" || return 1
    assert_json_field "$output" "['data']['unknown']" "0" "Should have 0 unknown" || return 1
}

test_all_acceptable() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-all-acceptable.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "All acceptable should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['total_warnings']" "2" "Should have 2 warnings" || return 1
    assert_json_field "$output" "['data']['acceptable']" "2" "Should have 2 acceptable" || return 1
    assert_json_field "$output" "['data']['fixable']" "0" "Should have 0 fixable" || return 1
    assert_json_field "$output" "['data']['unknown']" "0" "Should have 0 unknown" || return 1
}

test_no_config_file() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-with-warnings.json" \
        --config "/nonexistent/config.md" 2>/dev/null)
    exit_code=$?

    # Should still work - no acceptable patterns means nothing is acceptable
    assert_exit_code 1 $exit_code "Missing config should exit 1 (has fixable)" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    # With no config, nothing from "other" type is acceptable
    # Still has ALWAYS_FIXABLE_TYPES as fixable
}

test_empty_config() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-with-warnings.json" \
        --config "$FIXTURES_DIR/config-empty.md" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Empty config should exit 1 (has fixable)" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    # Without acceptable patterns, "other" warnings become unknown
}

test_invalid_parsed_output() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-invalid.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Invalid input should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "load_failed" "Error type should be load_failed" || return 1
}

test_missing_parsed_output() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "/nonexistent/file.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Missing input should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "load_failed" "Error type should be load_failed" || return 1
}

test_javadoc_always_fixable() {
    # JavaDoc warnings should ALWAYS be fixable, never acceptable
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-with-warnings.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)

    # Get fixable_warnings array and check for javadoc
    local has_javadoc=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fixable = data['data']['fixable_warnings']
has_javadoc = any(w.get('type') == 'javadoc_warning' for w in fixable)
print('true' if has_javadoc else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_javadoc" "JavaDoc warnings should be in fixable list" || return 1
}

test_deprecation_always_fixable() {
    # Deprecation warnings should ALWAYS be fixable
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-with-warnings.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)

    local has_deprecation=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fixable = data['data']['fixable_warnings']
has_deprecation = any(w.get('type') == 'deprecation_warning' for w in fixable)
print('true' if has_deprecation else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_deprecation" "Deprecation warnings should be in fixable list" || return 1
}

test_unknown_has_classification_flag() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-with-warnings.json" \
        --config "$FIXTURES_DIR/config-with-acceptable.md" 2>/dev/null)

    # Check unknown warnings have requires_classification flag
    local has_flag=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
unknown = data['data']['unknown_warnings']
if unknown:
    all_have_flag = all(w.get('requires_classification') == True for w in unknown)
    print('true' if all_have_flag else 'false')
else:
    print('empty')
" 2>/dev/null)

    # If there are unknown warnings, they should have the flag
    if [[ "$has_flag" == "true" ]]; then
        return 0
    elif [[ "$has_flag" == "empty" ]]; then
        return 0  # No unknown warnings to check
    else
        echo -e "${RED}Unknown warnings missing requires_classification flag${NC}"
        return 1
    fi
}

test_openrewrite_info_acceptable() {
    # OpenRewrite info warnings should be acceptable by default
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --parsed-output "$FIXTURES_DIR/parsed-output-with-warnings.json" \
        --config "$FIXTURES_DIR/config-empty.md" 2>/dev/null)  # Use empty config

    local has_openrewrite=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
acceptable = data['data']['acceptable_warnings']
has_openrewrite = any(w.get('type') == 'openrewrite_info' for w in acceptable)
print('true' if has_openrewrite else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_openrewrite" "OpenRewrite info should be in acceptable list" || return 1
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
               parsed-output-all-acceptable.json parsed-output-invalid.json \
               config-with-acceptable.md config-empty.md; do
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
run_test "no config file" test_no_config_file
run_test "empty config" test_empty_config
run_test "invalid parsed output" test_invalid_parsed_output
run_test "missing parsed output" test_missing_parsed_output
run_test "javadoc always fixable" test_javadoc_always_fixable
run_test "deprecation always fixable" test_deprecation_always_fixable
run_test "unknown has classification flag" test_unknown_has_classification_flag
run_test "openrewrite info acceptable" test_openrewrite_info_acceptable

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
