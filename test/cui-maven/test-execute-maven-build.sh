#!/bin/bash
# Test suite for execute-maven-build.py
# Tests Maven build execution with mock wrappers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/cui-maven/skills/cui-maven-rules/scripts/execute-maven-build.py"
MOCKS_DIR="$SCRIPT_DIR/mocks"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Temporary directory for test outputs
TEST_TMP_DIR=""

setup() {
    TEST_TMP_DIR=$(mktemp -d)
    cd "$TEST_TMP_DIR"
}

teardown() {
    cd "$PROJECT_ROOT"
    if [[ -n "$TEST_TMP_DIR" && -d "$TEST_TMP_DIR" ]]; then
        rm -rf "$TEST_TMP_DIR"
    fi
}

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

    setup

    if $test_func; then
        echo -e "${GREEN}PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    teardown
}

# =============================================================================
# TEST CASES
# =============================================================================

test_successful_build() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    exit_code=$?

    assert_exit_code 0 $exit_code "Successful build should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['exit_code']" "0" "Exit code should be 0" || return 1
    assert_contains "$output" "log_file" "Output should contain log_file" || return 1
    assert_contains "$output" "duration_ms" "Output should contain duration_ms" || return 1
    assert_contains "$output" "command_executed" "Output should contain command_executed" || return 1
}

test_failed_build() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-failure.sh" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Failed build should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "build_failed" "Error type should be build_failed" || return 1
    assert_json_field "$output" "['data']['exit_code']" "1" "Exit code should be 1" || return 1
}

test_javadoc_warnings_build() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-javadoc.sh" 2>/dev/null)
    exit_code=$?

    # JavaDoc warnings don't fail the build
    assert_exit_code 0 $exit_code "JavaDoc warnings build should exit with 0" || return 1
    assert_json_field "$output" "['status']" "success" "Status should be success" || return 1
    assert_json_field "$output" "['data']['exit_code']" "0" "Exit code should be 0" || return 1
}

test_timeout_handling() {
    local output
    local exit_code

    # Use very short timeout to trigger timeout quickly
    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --timeout 500 --mvnw "$MOCKS_DIR/mvnw-timeout.sh" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Timed out build should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "timeout" "Error type should be timeout" || return 1
    assert_contains "$output" "timed out" "Message should mention timeout" || return 1
}

test_log_file_creation() {
    local output
    local log_file

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    log_file=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['log_file'])")

    # Verify log file was created
    if [[ -f "$log_file" ]]; then
        return 0
    else
        echo "Log file was not created: $log_file"
        return 1
    fi
}

test_log_file_has_content() {
    local output
    local log_file

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    log_file=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['log_file'])")

    # Verify log file has content
    if [[ -s "$log_file" ]]; then
        # Check for expected content
        if grep -q "BUILD SUCCESS" "$log_file"; then
            return 0
        else
            echo "Log file missing BUILD SUCCESS"
            return 1
        fi
    else
        echo "Log file is empty: $log_file"
        return 1
    fi
}

test_profile_parameter() {
    local output
    local command_executed

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --profile pre-commit --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    command_executed=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['command_executed'])")

    assert_contains "$command_executed" "-Ppre-commit" "Command should contain profile flag" || return 1
}

test_module_parameter() {
    local output
    local command_executed

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --module auth-service --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    command_executed=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['command_executed'])")

    assert_contains "$command_executed" "-pl auth-service" "Command should contain module flag" || return 1
}

test_combined_parameters() {
    local output
    local command_executed

    output=$(python3 "$SCRIPT_PATH" --goals "clean verify" --profile coverage --module core --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    command_executed=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['command_executed'])")

    assert_contains "$command_executed" "-Pcoverage" "Command should contain profile flag" || return 1
    assert_contains "$command_executed" "-pl core" "Command should contain module flag" || return 1
    assert_contains "$command_executed" "clean" "Command should contain clean goal" || return 1
    assert_contains "$command_executed" "verify" "Command should contain verify goal" || return 1
}

test_exec_line_printed() {
    local stderr_output

    stderr_output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>&1 >/dev/null)

    assert_contains "$stderr_output" "[EXEC]" "Should print [EXEC] line to stderr" || return 1
}

test_timestamped_log_filename() {
    local output
    local log_file

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    log_file=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['log_file'])")

    # Check filename format: target/build-output-YYYY-MM-DD-HHMMSS.log
    if [[ "$log_file" =~ target/build-output-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}\.log ]]; then
        return 0
    else
        echo "Log filename doesn't match expected pattern: $log_file"
        return 1
    fi
}

test_missing_mvnw() {
    local output
    local exit_code

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "/nonexistent/mvnw" 2>/dev/null)
    exit_code=$?

    assert_exit_code 1 $exit_code "Missing mvnw should exit with 1" || return 1
    assert_json_field "$output" "['status']" "error" "Status should be error" || return 1
    assert_json_field "$output" "['error']" "execution_failed" "Error type should be execution_failed" || return 1
}

test_duration_tracking() {
    local output
    local duration

    output=$(python3 "$SCRIPT_PATH" --goals "clean install" --mvnw "$MOCKS_DIR/mvnw-success.sh" 2>/dev/null)
    duration=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['duration_ms'])")

    # Duration should be a positive number
    if [[ "$duration" =~ ^[0-9]+$ ]] && [[ "$duration" -ge 0 ]]; then
        return 0
    else
        echo "Invalid duration: $duration"
        return 1
    fi
}

# =============================================================================
# MAIN
# =============================================================================

echo ""
echo "========================================"
echo "  execute-maven-build.py Test Suite"
echo "========================================"
echo ""

# Verify script exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo -e "${RED}ERROR: Script not found: $SCRIPT_PATH${NC}"
    exit 1
fi

# Verify mocks exist
for mock in mvnw-success.sh mvnw-failure.sh mvnw-javadoc.sh mvnw-timeout.sh; do
    if [[ ! -x "$MOCKS_DIR/$mock" ]]; then
        echo -e "${RED}ERROR: Mock not found or not executable: $MOCKS_DIR/$mock${NC}"
        exit 1
    fi
done

echo "Running tests..."
echo ""

# Run all tests
run_test "successful build" test_successful_build
run_test "failed build" test_failed_build
run_test "javadoc warnings build" test_javadoc_warnings_build
run_test "timeout handling" test_timeout_handling
run_test "log file creation" test_log_file_creation
run_test "log file has content" test_log_file_has_content
run_test "profile parameter" test_profile_parameter
run_test "module parameter" test_module_parameter
run_test "combined parameters" test_combined_parameters
run_test "EXEC line printed" test_exec_line_printed
run_test "timestamped log filename" test_timestamped_log_filename
run_test "missing mvnw" test_missing_mvnw
run_test "duration tracking" test_duration_tracking

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
