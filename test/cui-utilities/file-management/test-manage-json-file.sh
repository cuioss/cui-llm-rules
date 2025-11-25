#!/bin/bash
# Test suite for manage-json-file.py
# Tests JSON file CRUD operations with path notation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$PROJECT_ROOT/marketplace/bundles/cui-utilities/skills/file-management/scripts/manage-json-file.py"
FIXTURES="$SCRIPT_DIR/fixtures"
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
    cat > "$TEMP_DIR/test-config.json" << 'EOF'
{
  "version": 1,
  "commands": {
    "test-cmd": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS"
      },
      "lessons_learned": ["lesson1", "lesson2"]
    }
  },
  "array_field": [1, 2, 3]
}
EOF
}

# Test: read entire file
test_read_entire_file() {
    setup_fixtures
    result=$(python3 "$SCRIPT" read "$TEMP_DIR/test-config.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['value']['version']==1 else 1)" 2>/dev/null; then
        pass "read entire file"
    else
        fail "read entire file" "success=true, version=1" "$result"
    fi
}

# Test: read specific field
test_read_field() {
    setup_fixtures
    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "commands.test-cmd.last_execution.status" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['value']=='SUCCESS' else 1)" 2>/dev/null; then
        pass "read specific field"
    else
        fail "read specific field" "value=SUCCESS" "$result"
    fi
}

# Test: read nested field
test_read_nested_field() {
    setup_fixtures
    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "commands.test-cmd.lessons_learned" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and len(d['value'])==2 else 1)" 2>/dev/null; then
        pass "read nested array field"
    else
        fail "read nested array field" "array with 2 elements" "$result"
    fi
}

# Test: read array index
test_read_array_index() {
    setup_fixtures
    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "array_field[1]" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['value']==2 else 1)" 2>/dev/null; then
        pass "read array index"
    else
        fail "read array index" "value=2" "$result"
    fi
}

# Test: read non-existent field (should fail gracefully)
test_read_nonexistent_field() {
    setup_fixtures
    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "nonexistent.field" 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] else 1)" 2>/dev/null; then
        pass "read non-existent field returns error"
    else
        fail "read non-existent field returns error" "success=false" "$result"
    fi
}

# Test: update field
test_update_field() {
    setup_fixtures
    python3 "$SCRIPT" update-field "$TEMP_DIR/test-config.json" --field "commands.test-cmd.last_execution.status" --value '"UPDATED"' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "commands.test-cmd.last_execution.status" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['value']=='UPDATED' else 1)" 2>/dev/null; then
        pass "update field"
    else
        fail "update field" "value=UPDATED" "$result"
    fi
}

# Test: update creates intermediate objects
test_update_creates_path() {
    setup_fixtures
    python3 "$SCRIPT" update-field "$TEMP_DIR/test-config.json" --field "new_section.nested.value" --value '42' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "new_section.nested.value" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['value']==42 else 1)" 2>/dev/null; then
        pass "update creates intermediate objects"
    else
        fail "update creates intermediate objects" "value=42" "$result"
    fi
}

# Test: add entry to array
test_add_entry_to_array() {
    setup_fixtures
    python3 "$SCRIPT" add-entry "$TEMP_DIR/test-config.json" --field "commands.test-cmd.lessons_learned" --value '"lesson3"' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "commands.test-cmd.lessons_learned" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if len(d['value'])==3 and 'lesson3' in d['value'] else 1)" 2>/dev/null; then
        pass "add entry to array"
    else
        fail "add entry to array" "3 elements including lesson3" "$result"
    fi
}

# Test: remove entry from array
test_remove_entry_from_array() {
    setup_fixtures
    python3 "$SCRIPT" remove-entry "$TEMP_DIR/test-config.json" --field "commands.test-cmd.lessons_learned" --value '"lesson1"' > /dev/null 2>&1

    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "commands.test-cmd.lessons_learned" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if len(d['value'])==1 and 'lesson1' not in d['value'] else 1)" 2>/dev/null; then
        pass "remove entry from array"
    else
        fail "remove entry from array" "1 element without lesson1" "$result"
    fi
}

# Test: remove field entirely
test_remove_field() {
    setup_fixtures
    python3 "$SCRIPT" remove-entry "$TEMP_DIR/test-config.json" --field "commands.test-cmd.lessons_learned" > /dev/null 2>&1

    result=$(python3 "$SCRIPT" read-field "$TEMP_DIR/test-config.json" --field "commands.test-cmd.lessons_learned" 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] else 1)" 2>/dev/null; then
        pass "remove field entirely"
    else
        fail "remove field entirely" "field not found" "$result"
    fi
}

# Test: write entire file
test_write_entire_file() {
    result=$(python3 "$SCRIPT" write "$TEMP_DIR/new-file.json" --value '{"test": true, "value": 123}' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] else 1)" 2>/dev/null; then
        # Verify content
        verify=$(python3 "$SCRIPT" read-field "$TEMP_DIR/new-file.json" --field "value" 2>&1)
        if echo "$verify" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['value']==123 else 1)" 2>/dev/null; then
            pass "write entire file"
        else
            fail "write entire file" "value=123" "$verify"
        fi
    else
        fail "write entire file" "success=true" "$result"
    fi
}

# Test: file not found error
test_file_not_found() {
    result=$(python3 "$SCRIPT" read "$TEMP_DIR/nonexistent.json" 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] and 'not found' in d['error'].lower() else 1)" 2>/dev/null; then
        pass "file not found returns error"
    else
        fail "file not found returns error" "success=false with 'not found'" "$result"
    fi
}

# Test: invalid JSON value error
test_invalid_json_value() {
    setup_fixtures
    result=$(python3 "$SCRIPT" update-field "$TEMP_DIR/test-config.json" --field "test" --value 'not valid json' 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] else 1)" 2>/dev/null; then
        pass "invalid JSON value returns error"
    else
        fail "invalid JSON value returns error" "success=false" "$result"
    fi
}

# Run all tests
echo "========================================"
echo "Testing manage-json-file.py"
echo "========================================"
echo ""

run_test test_read_entire_file
run_test test_read_field
run_test test_read_nested_field
run_test test_read_array_index
run_test test_read_nonexistent_field
run_test test_update_field
run_test test_update_creates_path
run_test test_add_entry_to_array
run_test test_remove_entry_from_array
run_test test_remove_field
run_test test_write_entire_file
run_test test_file_not_found
run_test test_invalid_json_value

echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN tests passed"
echo "========================================"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    exit 0
else
    exit 1
fi
