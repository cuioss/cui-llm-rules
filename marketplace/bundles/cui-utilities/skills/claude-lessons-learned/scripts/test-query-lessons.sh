#!/bin/bash
#
# Test script for query-lessons.py
#
# This script creates sample lesson files and tests various query scenarios.
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test directory
TEST_DIR=$(mktemp -d)
LESSONS_DIR="$TEST_DIR/.claude/lessons-learned"

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUERY_SCRIPT="$SCRIPT_DIR/query-lessons.py"

# Cleanup on exit
cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Helper functions
log_test() {
    echo -e "${YELLOW}TEST:${NC} $1"
    TESTS_RUN=$((TESTS_RUN + 1))
}

pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

assert_json_valid() {
    if echo "$1" | python3 -m json.tool >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

assert_count() {
    local expected=$1
    local json=$2
    local actual=$(echo "$json" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))")

    if [ "$actual" -eq "$expected" ]; then
        return 0
    else
        echo "Expected count: $expected, Got: $actual" >&2
        return 1
    fi
}

assert_contains() {
    local needle=$1
    local haystack=$2

    if echo "$haystack" | grep -q "$needle"; then
        return 0
    else
        echo "Expected to contain: $needle" >&2
        return 1
    fi
}

# Setup test environment
setup_test_lessons() {
    mkdir -p "$LESSONS_DIR"

    # Lesson 1: Bug in maven-build-and-fix (unapplied)
    cat > "$LESSONS_DIR/2025-11-27-001.md" <<'EOF'
id=2025-11-27-001
component.type=command
component.name=maven-build-and-fix
component.bundle=builder-maven
date=2025-11-27
category=bug
applied=false

# Paths with spaces cause failures

## Detail

Bash calls fail when paths contain spaces.
EOF

    # Lesson 2: Improvement in maven-build-and-fix (unapplied)
    cat > "$LESSONS_DIR/2025-11-27-002.md" <<'EOF'
id=2025-11-27-002
component.type=command
component.name=maven-build-and-fix
component.bundle=builder-maven
date=2025-11-27
category=improvement
applied=false

# Add progress indicator

## Detail

Show progress for long operations.
EOF

    # Lesson 3: Pattern in builder-maven-rules (applied)
    cat > "$LESSONS_DIR/2025-11-27-003.md" <<'EOF'
id=2025-11-27-003
component.type=skill
component.name=builder-maven-rules
component.bundle=builder-maven
date=2025-11-27
category=pattern
applied=true

# Validate inputs early

## Detail

Check inputs in Step 1.
EOF

    # Lesson 4: Bug in java-create (unapplied)
    cat > "$LESSONS_DIR/2025-11-26-001.md" <<'EOF'
id=2025-11-26-001
component.type=command
component.name=java-create
component.bundle=cui-java-expert
date=2025-11-26
category=bug
applied=false

# Missing package validation

## Detail

Need to validate package names.
EOF

    # Lesson 5: Anti-pattern in java-refactor (applied)
    cat > "$LESSONS_DIR/2025-11-25-001.md" <<'EOF'
id=2025-11-25-001
component.type=command
component.name=java-refactor
component.bundle=cui-java-expert
date=2025-11-25
category=anti-pattern
applied=true

# Don't modify during iteration

## Detail

Collect files first, then process.
EOF
}

# Run tests
echo "========================================="
echo "Testing query-lessons.py"
echo "========================================="
echo

# Check script exists
if [ ! -f "$QUERY_SCRIPT" ]; then
    echo -e "${RED}ERROR:${NC} Script not found: $QUERY_SCRIPT"
    exit 1
fi

# Setup test data
setup_test_lessons

# Test 1: Query all lessons
log_test "Query all lessons"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --all)
if assert_json_valid "$output" && assert_count 5 "$output"; then
    pass
else
    fail "Failed to query all lessons"
fi

# Test 2: Filter by component name
log_test "Filter by component name (maven-build-and-fix)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --component maven-build-and-fix)
if assert_json_valid "$output" && assert_count 2 "$output"; then
    pass
else
    fail "Failed to filter by component"
fi

# Test 3: Filter by applied status (false)
log_test "Filter by applied status (false)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --applied false)
if assert_json_valid "$output" && assert_count 3 "$output"; then
    pass
else
    fail "Failed to filter by applied=false"
fi

# Test 4: Filter by applied status (true)
log_test "Filter by applied status (true)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --applied true)
if assert_json_valid "$output" && assert_count 2 "$output"; then
    pass
else
    fail "Failed to filter by applied=true"
fi

# Test 5: Filter by category
log_test "Filter by category (bug)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --category bug)
if assert_json_valid "$output" && assert_count 2 "$output"; then
    pass
else
    fail "Failed to filter by category"
fi

# Test 6: Filter by bundle
log_test "Filter by bundle (builder-maven)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --bundle builder-maven)
if assert_json_valid "$output" && assert_count 3 "$output"; then
    pass
else
    fail "Failed to filter by bundle"
fi

# Test 7: Combine filters (component + applied)
log_test "Combine filters (component=maven-build-and-fix, applied=false)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --component maven-build-and-fix --applied false)
if assert_json_valid "$output" && assert_count 2 "$output"; then
    pass
else
    fail "Failed to combine filters"
fi

# Test 8: Filter by type
log_test "Filter by component type (command)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --type command)
if assert_json_valid "$output" && assert_count 4 "$output"; then
    pass
else
    fail "Failed to filter by type"
fi

# Test 9: No matches
log_test "Filter with no matches (component=nonexistent)"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$LESSONS_DIR" --component nonexistent)
if assert_json_valid "$output" && assert_count 0 "$output"; then
    pass
else
    fail "Failed to handle no matches"
fi

# Test 10: Empty directory
log_test "Handle empty lessons directory"
EMPTY_DIR="$TEST_DIR/.claude/empty-lessons"
mkdir -p "$EMPTY_DIR"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$EMPTY_DIR" --all)
if assert_json_valid "$output" && assert_count 0 "$output"; then
    pass
else
    fail "Failed to handle empty directory"
fi

# Test 11: Non-existent directory
log_test "Handle non-existent directory"
output=$(python3 "$QUERY_SCRIPT" --lessons-dir "$TEST_DIR/.claude/nonexistent" --all 2>&1)
if assert_contains "not found" "$output"; then
    pass
else
    fail "Failed to handle non-existent directory"
fi

# Summary
echo
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Tests run:    $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    exit 1
else
    echo "Tests failed: 0"
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
