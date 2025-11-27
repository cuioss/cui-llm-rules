#!/bin/bash
# Test suite for search-openrewrite-markers.py
# Tests OpenRewrite marker search and categorization

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/builder-maven/skills/builder-maven-rules/scripts/search-openrewrite-markers.py"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
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

test_find_markers() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)
    exit_code=$?

    # Should exit 1 because there's an "ask_user" marker
    assert_exit_code 1 $exit_code "Should exit 1 with ask_user markers" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['total_markers']" "4" "Should find 4 markers" || return 1
    assert_json_field "$output" "['data']['files_affected']" "2" "Should affect 2 files" || return 1
}

test_categorize_auto_suppress() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Should have 3 auto-suppress (2 CuiLogRecordPatternRecipe + 1 InvalidExceptionUsageRecipe)
    assert_json_field "$output" "['data']['auto_suppress_count']" "3" "Should have 3 auto-suppress markers" || return 1
}

test_categorize_ask_user() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Should have 1 ask_user (SomeOtherRecipe)
    assert_json_field "$output" "['data']['ask_user_count']" "1" "Should have 1 ask_user marker" || return 1
}

test_no_markers() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-no-markers/src" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "Should exit 0 with no markers" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['total_markers']" "0" "Should find 0 markers" || return 1
    assert_json_field "$output" "['data']['files_affected']" "0" "Should affect 0 files" || return 1
}

test_missing_directory() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "/nonexistent/directory" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Missing dir should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "source_not_found" "Error should be source_not_found" || return 1
}

test_recipe_summary() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check recipe_summary contains expected recipes
    local logrecord_count=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data['data']['recipe_summary'].get('CuiLogRecordPatternRecipe', 0))
" 2>/dev/null)

    assert_equals "2" "$logrecord_count" "Should have 2 CuiLogRecordPatternRecipe markers" || return 1
}

test_suppression_comment() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check that auto-suppress markers have suppression comment
    local has_comment=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
auto_suppress = data['data']['by_category']['auto_suppress']
has_comment = all('suppression_comment' in m for m in auto_suppress)
print('true' if has_comment else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_comment" "Auto-suppress markers should have suppression_comment" || return 1
}

test_marker_line_numbers() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check markers have line numbers
    local has_lines=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
markers = data['data']['markers']
has_lines = all('line' in m and isinstance(m['line'], int) for m in markers)
print('true' if has_lines else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_lines" "All markers should have line numbers" || return 1
}

test_only_auto_suppress_exit_0() {
    # Create temp dir with only auto-suppress markers
    local temp_dir=$(mktemp -d)
    mkdir -p "$temp_dir/src"

    cat > "$temp_dir/src/Test.java" << 'EOF'
public class Test {
    /*~~(TODO: CuiLogRecordPatternRecipe - test)>*/
    void method() {}
}
EOF

    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" --source-dir "$temp_dir/src" 2>/dev/null)
    exit_code=$?

    rm -rf "$temp_dir"

    assert_exit_code 0 $exit_code "Only auto-suppress should exit 0" || return 1
    assert_json_field "$output" "['data']['ask_user_count']" "0" "Should have 0 ask_user" || return 1
}

test_file_paths_in_output() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --source-dir "$FIXTURES_DIR/source-with-markers/src" 2>/dev/null)

    # Check that file paths are included
    local has_files=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
markers = data['data']['markers']
has_files = all('file' in m and m['file'].endswith('.java') for m in markers)
print('true' if has_files else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_files" "All markers should have file paths" || return 1
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
run_test "categorize auto_suppress" test_categorize_auto_suppress
run_test "categorize ask_user" test_categorize_ask_user
run_test "no markers" test_no_markers
run_test "missing directory" test_missing_directory
run_test "recipe summary" test_recipe_summary
run_test "suppression comment" test_suppression_comment
run_test "marker line numbers" test_marker_line_numbers
run_test "only auto_suppress exit 0" test_only_auto_suppress_exit_0
run_test "file paths in output" test_file_paths_in_output

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
