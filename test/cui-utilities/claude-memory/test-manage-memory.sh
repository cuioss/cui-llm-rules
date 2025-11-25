#!/bin/bash
# Test suite for manage-memory.py
# Tests memory layer CRUD operations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$PROJECT_ROOT/marketplace/bundles/cui-utilities/skills/claude-memory/scripts/manage-memory.py"
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

# Change to temp directory for tests
cd "$TEMP_DIR"

# Test: init creates directory structure
test_init() {
    result=$(python3 "$SCRIPT" init 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and len(d['created'])>=4 else 1)" 2>/dev/null; then
        # Verify directories exist
        if [ -d ".claude/memory/context" ] && [ -d ".claude/memory/decisions" ] && [ -d ".claude/memory/interfaces" ] && [ -d ".claude/memory/handoffs" ]; then
            pass "init creates directory structure"
        else
            fail "init creates directory structure" "all category directories" "missing directories"
        fi
    else
        fail "init creates directory structure" "success=true with 4+ created" "$result"
    fi
}

# Test: save to context category
test_save_context() {
    result=$(python3 "$SCRIPT" save --category context --identifier "test-feature" --content '{"decisions": ["Use JWT"]}' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and 'context' in d['path'] else 1)" 2>/dev/null; then
        pass "save to context category"
    else
        fail "save to context category" "success=true with context path" "$result"
    fi
}

# Test: save to decisions category
test_save_decisions() {
    result=$(python3 "$SCRIPT" save --category decisions --identifier "auth-approach" --content '{"decision": "Use JWT", "rationale": "Stateless"}' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and 'decisions' in d['path'] else 1)" 2>/dev/null; then
        pass "save to decisions category"
    else
        fail "save to decisions category" "success=true with decisions path" "$result"
    fi
}

# Test: save to handoffs category
test_save_handoffs() {
    result=$(python3 "$SCRIPT" save --category handoffs --identifier "task-42" --content '{"task": "Auth feature", "progress": "50%"}' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and 'handoffs' in d['path'] else 1)" 2>/dev/null; then
        pass "save to handoffs category"
    else
        fail "save to handoffs category" "success=true with handoffs path" "$result"
    fi
}

# Test: load memory file
test_load() {
    # First save
    python3 "$SCRIPT" save --category decisions --identifier "load-test" --content '{"value": 123}' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" load --category decisions --identifier "load-test" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['content']['value']==123 else 1)" 2>/dev/null; then
        pass "load memory file"
    else
        fail "load memory file" "content.value=123" "$result"
    fi
}

# Test: load verifies meta envelope
test_load_has_meta() {
    python3 "$SCRIPT" save --category decisions --identifier "meta-test" --content '{"test": true}' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" load --category decisions --identifier "meta-test" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and 'created' in d['meta'] and d['meta']['category']=='decisions' else 1)" 2>/dev/null; then
        pass "load includes meta envelope"
    else
        fail "load includes meta envelope" "meta with created and category" "$result"
    fi
}

# Test: list files in category
test_list_category() {
    # Save a few files
    python3 "$SCRIPT" save --category decisions --identifier "list-test-1" --content '{}' > /dev/null 2>&1
    python3 "$SCRIPT" save --category decisions --identifier "list-test-2" --content '{}' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" list --category decisions 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['count']>=2 else 1)" 2>/dev/null; then
        pass "list files in category"
    else
        fail "list files in category" "count>=2" "$result"
    fi
}

# Test: list all categories
test_list_all() {
    result=$(python3 "$SCRIPT" list 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] else 1)" 2>/dev/null; then
        pass "list all categories"
    else
        fail "list all categories" "success=true" "$result"
    fi
}

# Test: query by pattern
test_query_pattern() {
    python3 "$SCRIPT" save --category decisions --identifier "query-auth-test" --content '{}' > /dev/null 2>&1
    python3 "$SCRIPT" save --category decisions --identifier "query-data-test" --content '{}' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" query --pattern "query-auth*" --category decisions 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['count']>=1 else 1)" 2>/dev/null; then
        pass "query by pattern"
    else
        fail "query by pattern" "count>=1" "$result"
    fi
}

# Test: archive moves file
test_archive() {
    python3 "$SCRIPT" save --category handoffs --identifier "archive-test" --content '{"done": true}' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" archive --category handoffs --identifier "archive-test" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and 'archive' in d['destination'] else 1)" 2>/dev/null; then
        # Verify original is gone
        if [ ! -f ".claude/memory/handoffs/archive-test.json" ]; then
            pass "archive moves file"
        else
            fail "archive moves file" "original removed" "original still exists"
        fi
    else
        fail "archive moves file" "success with archive destination" "$result"
    fi
}

# Test: cleanup old files
test_cleanup() {
    # Create a file with an old created timestamp directly in the JSON
    mkdir -p .claude/memory/context
    cat > ".claude/memory/context/old-cleanup-test.json" << 'EOF'
{
  "meta": {
    "created": "2020-01-01T00:00:00Z",
    "category": "context",
    "summary": "cleanup-test"
  },
  "content": {}
}
EOF

    result=$(python3 "$SCRIPT" cleanup --category context --older-than 1d 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['removed_count']>=1 else 1)" 2>/dev/null; then
        pass "cleanup removes old files"
    else
        fail "cleanup removes old files" "removed_count>=1" "$result"
    fi
}

# Test: load non-existent file error
test_load_not_found() {
    result=$(python3 "$SCRIPT" load --category decisions --identifier "nonexistent" 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] else 1)" 2>/dev/null; then
        pass "load non-existent file returns error"
    else
        fail "load non-existent file returns error" "success=false" "$result"
    fi
}

# Test: invalid category error
test_invalid_category() {
    result=$(python3 "$SCRIPT" save --category invalid --identifier "test" --content '{}' 2>&1 || true)

    # argparse validates choices before our code runs, so check for the error message
    if echo "$result" | grep -q "invalid choice"; then
        pass "invalid category returns error"
    else
        fail "invalid category returns error" "error message with 'invalid choice'" "$result"
    fi
}

# Test: context files get date prefix
test_context_date_prefix() {
    result=$(python3 "$SCRIPT" save --category context --identifier "date-prefix-test" --content '{}' 2>&1)

    if echo "$result" | python3 -c "import sys,json; import re; d=json.load(sys.stdin); exit(0 if d['success'] and re.search(r'\\d{4}-\\d{2}-\\d{2}', d['identifier']) else 1)" 2>/dev/null; then
        pass "context files get date prefix"
    else
        fail "context files get date prefix" "identifier with date prefix" "$result"
    fi
}

# Run all tests
echo "========================================"
echo "Testing manage-memory.py"
echo "========================================"
echo ""

run_test test_init
run_test test_save_context
run_test test_save_decisions
run_test test_save_handoffs
run_test test_load
run_test test_load_has_meta
run_test test_list_category
run_test test_list_all
run_test test_query_pattern
run_test test_archive
run_test test_cleanup
run_test test_load_not_found
run_test test_invalid_category
run_test test_context_date_prefix

echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN tests passed"
echo "========================================"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    exit 0
else
    exit 1
fi
