#!/bin/bash
# Test suite for execute-npm-build.py
# Tests npm/npx build execution with mock scripts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/cui-frontend-expert/skills/cui-npm-rules/scripts/execute-npm-build.py"
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

    # Create target directory
    mkdir -p target

    # Create mock npm and npx in PATH
    export PATH="$MOCKS_DIR:$PATH"
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

    local actual=$(echo "$json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data$field)" 2>/dev/null || echo "ERROR")

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

assert_file_exists() {
    local file="$1"
    local message="$2"

    if [[ -f "$file" ]]; then
        return 0
    else
        echo -e "${RED}ASSERTION FAILED: $message${NC}"
        echo "  File not found: $file"
        return 1
    fi
}

run_test() {
    local test_name="$1"
    local test_func="$2"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}Running: $test_name${NC}"

    setup

    if $test_func; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓ PASS${NC}\n"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗ FAIL${NC}\n"
    fi

    teardown
}

# TEST 1: Successful npm test execution
test_successful_npm_test() {
    # Create wrapper that calls our mock
    cat > npm << 'EOF'
#!/bin/bash
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    local output=$(python3 "$SCRIPT_PATH" --command "run test" --timeout 5000 2>&1)
    local exit_code=$?

    assert_equals "0" "$exit_code" "Script should exit successfully" &&
    assert_json_field "$output" "['status']" "success" "Status should be success" &&
    assert_json_field "$output" "['data']['exit_code']" "0" "Exit code should be 0" &&
    assert_json_field "$output" "['data']['command_type']" "npm" "Command type should be npm" &&
    assert_contains "$output" "target/npm-output-" "Should contain log file path"
}

# TEST 2: Failed npm test execution
test_failed_npm_test() {
    # Create wrapper that calls our mock
    cat > npm << 'EOF'
#!/bin/bash
exec "$MOCKS_DIR/npm-failure.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    local output=$(python3 "$SCRIPT_PATH" --command "run test" --timeout 5000 2>&1)
    local exit_code=$?

    assert_equals "0" "$exit_code" "Script itself should exit successfully" &&
    assert_json_field "$output" "['status']" "success" "Status should be success" &&
    assert_json_field "$output" "['data']['exit_code']" "1" "Exit code should be 1 (test failure)" &&
    assert_contains "$output" "target/npm-output-" "Should contain log file path"
}

# TEST 3: npm command type detection
test_npm_command_detection() {
    cat > npm << 'EOF'
#!/bin/bash
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    local output=$(python3 "$SCRIPT_PATH" --command "run build" --timeout 5000 2>&1)

    assert_json_field "$output" "['data']['command_type']" "npm" "Should detect npm command"
}

# TEST 4: npx command type detection
test_npx_command_detection() {
    cat > npx << 'EOF'
#!/bin/bash
exec "$MOCKS_DIR/npx-playwright-success.sh" "$@"
EOF
    chmod +x npx
    export PATH=".:$PATH"

    local output=$(python3 "$SCRIPT_PATH" --command "playwright test" --timeout 5000 2>&1)

    assert_json_field "$output" "['data']['command_type']" "npx" "Should detect npx command"
}

# TEST 5: Log file creation
test_log_file_creation() {
    cat > npm << 'EOF'
#!/bin/bash
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    local output=$(python3 "$SCRIPT_PATH" --command "run test" --timeout 5000 2>&1)
    local log_file=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['log_file'])" 2>/dev/null)

    assert_file_exists "$log_file" "Log file should be created" &&
    assert_contains "$(cat "$log_file")" "Test Suites:" "Log file should contain test output"
}

# TEST 6: Workspace parameter handling
test_workspace_parameter() {
    cat > npm << 'EOF'
#!/bin/bash
# Check if --workspace flag is present
if [[ "$*" == *"--workspace="* ]]; then
    echo "Workspace flag detected" > /tmp/workspace-test
fi
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    python3 "$SCRIPT_PATH" --command "run test" --workspace "e-2-e-playwright" --timeout 5000 >/dev/null 2>&1

    assert_file_exists "/tmp/workspace-test" "Should pass workspace flag to npm" &&
    rm -f /tmp/workspace-test
}

# TEST 7: Environment variables
test_environment_variables() {
    cat > npm << 'EOF'
#!/bin/bash
# Check if NODE_ENV is set
if [[ "$NODE_ENV" == "test" ]]; then
    echo "NODE_ENV is test" > /tmp/env-test
fi
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    python3 "$SCRIPT_PATH" --command "run test" --env "NODE_ENV=test" --timeout 5000 >/dev/null 2>&1

    assert_file_exists "/tmp/env-test" "Should set environment variables" &&
    rm -f /tmp/env-test
}

# TEST 8: Command execution timing
test_execution_timing() {
    cat > npm << 'EOF'
#!/bin/bash
sleep 1
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    local output=$(python3 "$SCRIPT_PATH" --command "run test" --timeout 5000 2>&1)
    local duration=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['duration_ms'])" 2>/dev/null)

    # Duration should be >= 1000ms (1 second sleep)
    if [[ "$duration" -ge 1000 ]]; then
        return 0
    else
        echo -e "${RED}Duration $duration is less than expected 1000ms${NC}"
        return 1
    fi
}

# TEST 9: Timeout handling
test_timeout_handling() {
    cat > npm << 'EOF'
#!/bin/bash
# Sleep longer than timeout
sleep 10
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    local output=$(python3 "$SCRIPT_PATH" --command "run test" --timeout 1000 2>&1)
    local exit_code=$(echo "$output" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['exit_code'])" 2>/dev/null)

    assert_equals "124" "$exit_code" "Should return timeout exit code (124)"
}

# TEST 10: [EXEC] output generation
test_exec_output() {
    cat > npm << 'EOF'
#!/bin/bash
exec "$MOCKS_DIR/npm-success.sh" "$@"
EOF
    chmod +x npm
    export PATH=".:$PATH"

    local stderr_output=$(python3 "$SCRIPT_PATH" --command "run test" --timeout 5000 2>&1 >/dev/null)

    assert_contains "$stderr_output" "[EXEC]" "Should print [EXEC] line" &&
    assert_contains "$stderr_output" "npm run test" "Should show executed command"
}

# Run all tests
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Testing execute-npm-build.py${NC}"
echo -e "${YELLOW}========================================${NC}\n"

run_test "Successful npm test execution" test_successful_npm_test
run_test "Failed npm test execution" test_failed_npm_test
run_test "npm command type detection" test_npm_command_detection
run_test "npx command type detection" test_npx_command_detection
run_test "Log file creation" test_log_file_creation
run_test "Workspace parameter handling" test_workspace_parameter
run_test "Environment variables" test_environment_variables
run_test "Command execution timing" test_execution_timing
run_test "Timeout handling" test_timeout_handling
run_test "[EXEC] output generation" test_exec_output

# Print summary
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Test Summary${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Tests run:    $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
