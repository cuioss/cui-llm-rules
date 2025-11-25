#!/bin/bash
# Test suite for validate-memory.py
# Tests memory file format validation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$PROJECT_ROOT/marketplace/bundles/cui-utilities/skills/claude-memory/scripts/validate-memory.py"
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

# Create test fixtures
setup_fixtures() {
    mkdir -p "$TEMP_DIR/.claude/memory/context"

    # Valid memory file
    cat > "$TEMP_DIR/.claude/memory/context/test-memory.json" << 'EOF'
{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "context",
    "summary": "test-feature"
  },
  "content": {
    "decisions": ["Use JWT"]
  }
}
EOF

    # Invalid memory file (missing meta)
    cat > "$TEMP_DIR/invalid-memory.json" << 'EOF'
{
  "content": {
    "test": true
  }
}
EOF

    # Invalid memory file (missing content)
    cat > "$TEMP_DIR/missing-content.json" << 'EOF'
{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "context",
    "summary": "test"
  }
}
EOF

    # Invalid memory file (invalid category)
    cat > "$TEMP_DIR/invalid-category.json" << 'EOF'
{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "invalid",
    "summary": "test"
  },
  "content": {}
}
EOF

    # Invalid JSON syntax
    cat > "$TEMP_DIR/invalid-json.json" << 'EOF'
{
  "broken": true,
  missing-quotes: "value"
}
EOF
}

# Test: validate valid memory file
test_valid_memory() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/.claude/memory/context/test-memory.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate valid memory file"
    else
        fail "validate valid memory file" "valid=true" "$result"
    fi
}

# Test: validate invalid memory file (missing meta)
test_invalid_memory_no_meta() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-memory.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid memory file (missing meta)"
    else
        fail "detect invalid memory file (missing meta)" "valid=false" "$result"
    fi
}

# Test: validate invalid memory file (missing content)
test_invalid_memory_no_content() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/missing-content.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid memory file (missing content)"
    else
        fail "detect invalid memory file (missing content)" "valid=false" "$result"
    fi
}

# Test: validate invalid category
test_invalid_category() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-category.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid category"
    else
        fail "detect invalid category" "valid=false" "$result"
    fi
}

# Test: detect invalid JSON syntax
test_invalid_json_syntax() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-json.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid JSON syntax"
    else
        fail "detect invalid JSON syntax" "valid=false" "$result"
    fi
}

# Test: checks array in output
test_checks_array() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/.claude/memory/context/test-memory.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and len(d['checks'])>0 else 1)" 2>/dev/null; then
        pass "output includes checks array"
    else
        fail "output includes checks array" "checks array with items" "$result"
    fi
}

# Test: file not found error
test_file_not_found() {
    result=$(python3 "$SCRIPT" "$TEMP_DIR/nonexistent.json" 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] else 1)" 2>/dev/null; then
        pass "file not found returns error"
    else
        fail "file not found returns error" "success=false" "$result"
    fi
}

# Test: format is memory
test_format_is_memory() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/.claude/memory/context/test-memory.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['format']=='memory' else 1)" 2>/dev/null; then
        pass "format is memory"
    else
        fail "format is memory" "format=memory" "$result"
    fi
}

# Run all tests
echo "========================================"
echo "Testing validate-memory.py"
echo "========================================"
echo ""

run_test test_valid_memory
run_test test_invalid_memory_no_meta
run_test test_invalid_memory_no_content
run_test test_invalid_category
run_test test_invalid_json_syntax
run_test test_checks_array
run_test test_file_not_found
run_test test_format_is_memory

echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN tests passed"
echo "========================================"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    exit 0
else
    exit 1
fi
