#!/bin/bash
# Test suite for find-module-path.py
# Tests Maven module path detection and ambiguity handling

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/cui-maven/skills/cui-maven-rules/scripts/find-module-path.py"
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

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    if [[ "$haystack" == *"$needle"* ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  Expected to contain: $needle"
        echo "  Actual: $haystack"
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

test_find_unique_module() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id user-service \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "Unique module should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['artifact_id']" "user-service" "ArtifactId should match" || return 1
    assert_json_field "$output" "['data']['module_path']" "services/user-service" "Module path should be correct" || return 1
    assert_contains "$output" "-pl services/user-service" "Should contain maven_pl_argument" || return 1
}

test_find_core_module() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id core-module \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "Core module should exit with 0" || return 1
    assert_json_field "$output" "['data']['module_path']" "core" "Module path should be core" || return 1
}

test_ambiguous_artifact_id() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id auth-service \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Ambiguous module should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "ambiguous_artifact_id" "Error should be ambiguous_artifact_id" || return 1
    assert_contains "$output" "choices" "Should contain choices array" || return 1
    assert_contains "$output" "services/auth-service" "Choices should include services/auth-service" || return 1
    assert_contains "$output" "legacy/auth-service" "Choices should include legacy/auth-service" || return 1
}

test_artifact_not_found() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id nonexistent-module \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Not found should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "artifact_not_found" "Error should be artifact_not_found" || return 1
}

test_validate_module_path() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --module-path services/auth-service \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "Valid path should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['artifact_id']" "auth-service" "Should extract artifactId" || return 1
    assert_json_field "$output" "['data']['module_path']" "services/auth-service" "Path should match" || return 1
}

test_validate_invalid_path() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --module-path nonexistent/path \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Invalid path should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "module_not_found" "Error should be module_not_found" || return 1
}

test_single_module_project() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id simple-app \
        --root "$FIXTURES_DIR/single-module-project" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "Single module should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['module_path']" "." "Module path should be root" || return 1
}

test_parent_modules_extraction() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id user-service \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)

    # Check parent_modules contains "services"
    local has_services=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
parents = data['data']['parent_modules']
print('true' if 'services' in parents else 'false')
" 2>/dev/null)

    assert_equals "true" "$has_services" "Parent modules should include 'services'" || return 1
}

test_root_not_found() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id test \
        --root "/nonexistent/directory" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Missing root should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "root_not_found" "Error should be root_not_found" || return 1
}

test_pom_file_in_output() {
    local output

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id core-module \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)

    assert_contains "$output" "core/pom.xml" "Output should include pom_file path" || return 1
}

test_does_not_match_dependencies() {
    # user-service has auth-service as a dependency
    # Searching for auth-service should NOT match user-service
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" \
        --artifact-id auth-service \
        --root "$FIXTURES_DIR/multi-module-project" 2>/dev/null)
    exit_code=$?

    # Should find exactly 2 modules (services/auth-service and legacy/auth-service)
    # NOT user-service (which only has it as dependency)
    local choice_count=$(echo "$output" | python3 -c "
import sys, json
data = json.load(sys.stdin)
choices = data.get('choices', [])
print(len(choices))
" 2>/dev/null)

    assert_equals "2" "$choice_count" "Should find exactly 2 auth-service modules (not dependencies)" || return 1
}

# =============================================================================
# MAIN
# =============================================================================

echo ""
echo "========================================"
echo "  find-module-path.py Test Suite"
echo "========================================"
echo ""

# Verify script exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo -e "${RED}ERROR: Script not found: $SCRIPT_PATH${NC}"
    exit 1
fi

# Verify fixtures exist
if [[ ! -d "$FIXTURES_DIR/multi-module-project" ]]; then
    echo -e "${RED}ERROR: Fixture not found: $FIXTURES_DIR/multi-module-project${NC}"
    exit 1
fi

echo "Running tests..."
echo ""

# Run all tests
run_test "find unique module" test_find_unique_module
run_test "find core module" test_find_core_module
run_test "ambiguous artifact id" test_ambiguous_artifact_id
run_test "artifact not found" test_artifact_not_found
run_test "validate module path" test_validate_module_path
run_test "validate invalid path" test_validate_invalid_path
run_test "single module project" test_single_module_project
run_test "parent modules extraction" test_parent_modules_extraction
run_test "root not found" test_root_not_found
run_test "pom file in output" test_pom_file_in_output
run_test "does not match dependencies" test_does_not_match_dependencies

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
