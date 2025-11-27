#!/bin/bash
# Test suite for init-run-config.py
# Tests run-configuration.json initialization

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$PROJECT_ROOT/marketplace/bundles/cui-utilities/skills/claude-run-configuration/scripts/init-run-config.py"
TEMP_DIR=$(mktemp -d)

# Cleanup on exit
trap "rm -rf $TEMP_DIR" EXIT

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

TESTS_RUN=0
TESTS_PASSED=0

# Test helper functions
pass() {
    echo -e "${GREEN}PASS${NC}: $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail() {
    echo -e "${RED}FAIL${NC}: $1"
    echo "  Expected: $2"
    echo "  Got: $3"
}

run_test() {
    TESTS_RUN=$((TESTS_RUN + 1))
    "$@"
}

# Test: create new run-configuration.json
test_create_new_config() {
    local test_dir="$TEMP_DIR/test_create"
    mkdir -p "$test_dir"

    result=$(python3 "$SCRIPT" --project-dir "$test_dir" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['action']=='created' else 1)" 2>/dev/null; then
        # Also verify file exists
        if [ -f "$test_dir/.claude/run-configuration.json" ]; then
            pass "create new run-configuration.json"
        else
            fail "create new run-configuration.json" "file created" "file not found"
        fi
    else
        fail "create new run-configuration.json" "success=true, action=created" "$result"
    fi
}

# Test: skip if file already exists
test_skip_existing() {
    local test_dir="$TEMP_DIR/test_skip"
    mkdir -p "$test_dir/.claude"
    echo '{"version": 1, "commands": {}}' > "$test_dir/.claude/run-configuration.json"

    result=$(python3 "$SCRIPT" --project-dir "$test_dir" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['action']=='skipped' else 1)" 2>/dev/null; then
        pass "skip if file already exists"
    else
        fail "skip if file already exists" "success=true, action=skipped" "$result"
    fi
}

# Test: force overwrite existing file
test_force_overwrite() {
    local test_dir="$TEMP_DIR/test_force"
    mkdir -p "$test_dir/.claude"
    echo '{"version": 1, "commands": {"old": {}}}' > "$test_dir/.claude/run-configuration.json"

    result=$(python3 "$SCRIPT" --project-dir "$test_dir" --force 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] else 1)" 2>/dev/null; then
        # Verify file was overwritten (old command entry should be gone)
        content=$(cat "$test_dir/.claude/run-configuration.json")
        if echo "$content" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'old' not in d['commands'] else 1)" 2>/dev/null; then
            pass "force overwrite existing file"
        else
            fail "force overwrite existing file" "old command removed" "$content"
        fi
    else
        fail "force overwrite existing file" "success=true" "$result"
    fi
}

# Test: created file has correct structure
test_correct_structure() {
    local test_dir="$TEMP_DIR/test_structure"
    mkdir -p "$test_dir"

    python3 "$SCRIPT" --project-dir "$test_dir" >/dev/null 2>&1

    content=$(cat "$test_dir/.claude/run-configuration.json")

    # Check version is 1
    if ! echo "$content" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['version']==1 else 1)" 2>/dev/null; then
        fail "correct structure - version" "version=1" "$content"
        return
    fi

    # Check commands is empty object
    if ! echo "$content" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['commands']=={} else 1)" 2>/dev/null; then
        fail "correct structure - commands" "commands={}" "$content"
        return
    fi

    # Check maven section exists with acceptable_warnings
    if ! echo "$content" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'acceptable_warnings' in d.get('maven',{}) else 1)" 2>/dev/null; then
        fail "correct structure - maven" "maven.acceptable_warnings exists" "$content"
        return
    fi

    # Check acceptable_warnings categories
    if echo "$content" | python3 -c "import sys,json; d=json.load(sys.stdin); aw=d['maven']['acceptable_warnings']; exit(0 if 'transitive_dependency' in aw and 'plugin_compatibility' in aw and 'platform_specific' in aw else 1)" 2>/dev/null; then
        pass "correct structure"
    else
        fail "correct structure - categories" "all warning categories present" "$content"
    fi
}

# Test: creates .claude directory if needed
test_creates_claude_dir() {
    local test_dir="$TEMP_DIR/test_mkdir"
    mkdir -p "$test_dir"
    # Ensure .claude doesn't exist
    rm -rf "$test_dir/.claude"

    result=$(python3 "$SCRIPT" --project-dir "$test_dir" 2>&1)

    if [ -d "$test_dir/.claude" ] && [ -f "$test_dir/.claude/run-configuration.json" ]; then
        pass "creates .claude directory if needed"
    else
        fail "creates .claude directory if needed" ".claude directory and file created" "directory or file missing"
    fi
}

# Test: output includes path
test_output_includes_path() {
    local test_dir="$TEMP_DIR/test_path"
    mkdir -p "$test_dir"

    result=$(python3 "$SCRIPT" --project-dir "$test_dir" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'path' in d else 1)" 2>/dev/null; then
        pass "output includes path"
    else
        fail "output includes path" "path field in output" "$result"
    fi
}

# Test: output includes structure when created
test_output_includes_structure() {
    local test_dir="$TEMP_DIR/test_struct_out"
    mkdir -p "$test_dir"

    result=$(python3 "$SCRIPT" --project-dir "$test_dir" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['action']=='created' and 'structure' in d else 1)" 2>/dev/null; then
        pass "output includes structure when created"
    else
        fail "output includes structure when created" "structure field in output" "$result"
    fi
}

# Test: default project dir is current directory
test_default_project_dir() {
    local test_dir="$TEMP_DIR/test_default"
    mkdir -p "$test_dir"

    # Run from test_dir
    cd "$test_dir"
    result=$(python3 "$SCRIPT" 2>&1)
    cd - >/dev/null

    if [ -f "$test_dir/.claude/run-configuration.json" ]; then
        pass "default project dir is current directory"
    else
        fail "default project dir is current directory" "file in current dir" "file not found"
    fi
}

# Run all tests
echo "========================================"
echo "Testing init-run-config.py"
echo "========================================"
echo ""

run_test test_create_new_config
run_test test_skip_existing
run_test test_force_overwrite
run_test test_correct_structure
run_test test_creates_claude_dir
run_test test_output_includes_path
run_test test_output_includes_structure
run_test test_default_project_dir

echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN tests passed"
echo "========================================"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    exit 0
else
    exit 1
fi
