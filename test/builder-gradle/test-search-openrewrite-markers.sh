#!/bin/bash
# Test suite for search-openrewrite-markers.py
# Tests OpenRewrite marker detection and categorization

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/builder-gradle/skills/builder-gradle-rules/scripts/search-openrewrite-markers.py"
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

assert_greater_than() {
    local value="$1"
    local threshold="$2"
    local message="$3"

    if [[ "$value" -gt "$threshold" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Value: $value should be greater than $threshold"
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

test_find_markers() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)
    exit_code=$?

    # Should find markers, exit 1 because there are ask_user markers
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1

    local total_markers
    total_markers=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['total_markers'])")
    assert_greater_than "$total_markers" 0 "Should find some markers" || return 1
}

test_no_markers_found() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-no-markers/src" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "No markers should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['total_markers']" "0" "Should find 0 markers" || return 1
}

test_categorize_auto_suppress() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check auto_suppress count
    local auto_suppress_count
    auto_suppress_count=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['auto_suppress_count'])")

    assert_greater_than "$auto_suppress_count" 0 "Should have auto-suppressible markers" || return 1
}

test_categorize_ask_user() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check ask_user count
    local ask_user_count
    ask_user_count=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['ask_user_count'])")

    assert_greater_than "$ask_user_count" 0 "Should have ask_user markers" || return 1
}

test_recipe_summary() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check recipe_summary exists
    local has_summary=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
summary = data['data']['recipe_summary']
print('true' if summary else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_summary" "Should have recipe summary" || return 1
}

test_files_affected_count() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    local files_affected
    files_affected=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['files_affected'])")

    assert_greater_than "$files_affected" 0 "Should report affected files" || return 1
}

test_suppression_comment_generated() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check auto_suppress entries have suppression_comment
    local has_comment=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
auto_suppress = data['data']['by_category']['auto_suppress']
if auto_suppress:
    has_comment = all('suppression_comment' in m for m in auto_suppress)
    print('true' if has_comment else 'false')
else:
    print('empty')
" 2>/dev/null)

    if [[ "$has_comment" == "true" ]] || [[ "$has_comment" == "empty" ]]; then
        return 0
    else
        echo -e "${RED}Auto-suppress markers should have suppression_comment${NC}"
        return 1
    fi
}

test_directory_not_found() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "/nonexistent/directory" 2>/dev/null)
    exit_code=$?

    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "directory_not_found" "Error should be directory_not_found" || return 1
}

test_custom_extensions() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" \
        --extensions ".java" 2>/dev/null)
    exit_code=$?

    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
}

test_marker_has_line_number() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check markers have line field
    local has_line=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
markers = data['data']['markers']
if markers:
    has_line = all('line' in m for m in markers)
    print('true' if has_line else 'false')
else:
    print('empty')
" 2>/dev/null)

    if [[ "$has_line" == "true" ]] || [[ "$has_line" == "empty" ]]; then
        return 0
    else
        echo -e "${RED}Markers should have line number${NC}"
        return 1
    fi
}

# =============================================================================
# MAIN
# =============================================================================

echo ""
echo "========================================"
echo "  search-openrewrite-markers.py Tests"
echo "========================================"
echo ""

# Verify script exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo -e "${RED}ERROR: Script not found: $SCRIPT_PATH${NC}"
    exit 1
fi

# Verify fixtures exist
if [[ ! -d "$FIXTURES_DIR/source-with-markers" ]]; then
    echo -e "${RED}ERROR: Fixture not found: $FIXTURES_DIR/source-with-markers${NC}"
    exit 1
fi

echo "Running tests..."
echo ""

# Run all tests
run_test "find markers" test_find_markers
run_test "no markers found" test_no_markers_found
run_test "categorize auto suppress" test_categorize_auto_suppress
run_test "categorize ask user" test_categorize_ask_user
run_test "recipe summary" test_recipe_summary
run_test "files affected count" test_files_affected_count
run_test "suppression comment generated" test_suppression_comment_generated
run_test "directory not found" test_directory_not_found
run_test "custom extensions" test_custom_extensions
run_test "marker has line number" test_marker_has_line_number

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
