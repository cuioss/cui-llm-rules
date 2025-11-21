#!/bin/bash
# Comprehensive test suite for plugin-fix scripts
# Tests: extract-fixable-issues.py, categorize-fixes.py, apply-fix.py, verify-fix.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/../../../marketplace/bundles/cui-plugin-development-tools/skills"
PLUGIN_FIX_DIR="$SKILLS_DIR/plugin-fix"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

# Test helper function
run_test() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"

    if [ "$actual" == "$expected" ]; then
        echo -e "${GREEN}PASS${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}: $test_name"
        echo "  Expected: $expected"
        echo "  Actual: $actual"
        ((TESTS_FAILED++))
    fi
}

run_test_contains() {
    local test_name="$1"
    local expected_substring="$2"
    local actual="$3"

    if echo "$actual" | grep -q "$expected_substring"; then
        echo -e "${GREEN}PASS${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}: $test_name"
        echo "  Expected to contain: $expected_substring"
        echo "  Actual: $actual"
        ((TESTS_FAILED++))
    fi
}

run_test_json_field() {
    local test_name="$1"
    local json="$2"
    local field="$3"
    local expected="$4"

    local actual
    actual=$(echo "$json" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('$field', 'MISSING'))" 2>/dev/null || echo "PARSE_ERROR")

    if [ "$actual" == "$expected" ]; then
        echo -e "${GREEN}PASS${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}: $test_name (field: $field)"
        echo "  Expected: $expected"
        echo "  Actual: $actual"
        ((TESTS_FAILED++))
    fi
}

echo "=========================================="
echo "Plugin-Fix Scripts Test Suite"
echo "=========================================="
echo ""

# ==========================================
# Test extract-fixable-issues.py
# ==========================================
echo -e "${YELLOW}Testing extract-fixable-issues.py${NC}"
echo "------------------------------------------"

EXTRACT_SCRIPT="$PLUGIN_FIX_DIR/scripts/extract-fixable-issues.py"

# Test 1: Extract from mixed diagnosis (has both fixable and non-fixable)
result=$("$EXTRACT_SCRIPT" "$FIXTURES_DIR/diagnosis/diagnosis-with-fixable.json")
count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_count'])")
run_test "Extract fixable from mixed (count=6)" "6" "$count"

# Test 2: Extract from no-fixable diagnosis
result=$("$EXTRACT_SCRIPT" "$FIXTURES_DIR/diagnosis/diagnosis-no-fixable.json")
count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_count'])")
run_test "Extract from no-fixable (count=0)" "0" "$count"

# Test 3: Extract from all-fixable diagnosis
result=$("$EXTRACT_SCRIPT" "$FIXTURES_DIR/diagnosis/diagnosis-all-fixable.json")
count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_count'])")
run_test "Extract from all-fixable (count=4)" "4" "$count"

# Test 4: Extract from empty diagnosis
result=$("$EXTRACT_SCRIPT" "$FIXTURES_DIR/diagnosis/diagnosis-empty.json")
count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_count'])")
run_test "Extract from empty (count=0)" "0" "$count"

# Test 5: Handle stdin input
result=$(cat "$FIXTURES_DIR/diagnosis/diagnosis-with-fixable.json" | "$EXTRACT_SCRIPT" -)
run_test_contains "Stdin input works" "fixable_issues" "$result"

# Test 6: Invalid JSON handling
result=$(echo "not json" | "$EXTRACT_SCRIPT" - 2>&1 || true)
run_test_contains "Invalid JSON returns error" "Invalid JSON" "$result"

echo ""

# ==========================================
# Test categorize-fixes.py
# ==========================================
echo -e "${YELLOW}Testing categorize-fixes.py${NC}"
echo "------------------------------------------"

CATEGORIZE_SCRIPT="$PLUGIN_FIX_DIR/scripts/categorize-fixes.py"

# Test 1: Categorize safe-only issues
result=$("$CATEGORIZE_SCRIPT" "$FIXTURES_DIR/categorization/extracted-safe-only.json")
safe_count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['safe_count'])")
risky_count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['risky_count'])")
run_test "Safe-only: safe_count=3" "3" "$safe_count"
run_test "Safe-only: risky_count=0" "0" "$risky_count"

# Test 2: Categorize risky-only issues
result=$("$CATEGORIZE_SCRIPT" "$FIXTURES_DIR/categorization/extracted-risky-only.json")
safe_count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['safe_count'])")
risky_count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['risky_count'])")
run_test "Risky-only: safe_count=0" "0" "$safe_count"
run_test "Risky-only: risky_count=3" "3" "$risky_count"

# Test 3: Categorize mixed issues
result=$("$CATEGORIZE_SCRIPT" "$FIXTURES_DIR/categorization/extracted-mixed.json")
safe_count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['safe_count'])")
risky_count=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['risky_count'])")
run_test "Mixed: safe_count=3" "3" "$safe_count"
run_test "Mixed: risky_count=2" "2" "$risky_count"

# Test 4: Categorize empty
result=$("$CATEGORIZE_SCRIPT" "$FIXTURES_DIR/categorization/extracted-empty.json")
total=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['total_count'])")
run_test "Empty: total_count=0" "0" "$total"

echo ""

# ==========================================
# Test apply-fix.py
# ==========================================
echo -e "${YELLOW}Testing apply-fix.py${NC}"
echo "------------------------------------------"

APPLY_SCRIPT="$PLUGIN_FIX_DIR/scripts/apply-fix.py"

# Create temp directory for apply tests
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy fixtures to temp dir
cp -r "$FIXTURES_DIR/apply-fix/"* "$TEMP_DIR/"

# Test 1: Apply missing frontmatter fix
FIX_JSON='{"type": "missing-frontmatter", "file": "agent-missing-frontmatter.md"}'
result=$(echo "$FIX_JSON" | "$APPLY_SCRIPT" - "$TEMP_DIR")
success=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
run_test "Apply missing-frontmatter fix" "True" "$success"

# Verify the fix was applied
if head -1 "$TEMP_DIR/agent-missing-frontmatter.md" | grep -q "^---$"; then
    echo -e "${GREEN}PASS${NC}: Frontmatter actually added to file"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}: Frontmatter not added to file"
    ((TESTS_FAILED++))
fi

# Test 2: Apply array syntax fix
FIX_JSON='{"type": "array-syntax-tools", "file": "agent-array-syntax.md"}'
result=$(echo "$FIX_JSON" | "$APPLY_SCRIPT" - "$TEMP_DIR")
success=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
run_test "Apply array-syntax fix" "True" "$success"

# Test 3: Apply rule-6 fix (remove Task tool)
FIX_JSON='{"type": "rule-6-violation", "file": "agent-task-tool.md"}'
result=$(echo "$FIX_JSON" | "$APPLY_SCRIPT" - "$TEMP_DIR")
success=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
run_test "Apply rule-6 fix" "True" "$success"

# Verify Task was removed
if ! grep -q "Task" "$TEMP_DIR/agent-task-tool.md" 2>/dev/null | grep -q "^tools:"; then
    echo -e "${GREEN}PASS${NC}: Task tool removed from declaration"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}: Task tool still in declaration"
    ((TESTS_FAILED++))
fi

# Test 4: Handle missing file gracefully
FIX_JSON='{"type": "missing-frontmatter", "file": "nonexistent.md"}'
result=$(echo "$FIX_JSON" | "$APPLY_SCRIPT" - "$TEMP_DIR")
success=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
run_test "Handle missing file" "False" "$success"

# Test 5: Backup created
if ls "$TEMP_DIR"/*.fix-backup 1>/dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}: Backup files created"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}: No backup files created"
    ((TESTS_FAILED++))
fi

echo ""

# ==========================================
# Test verify-fix.sh
# ==========================================
echo -e "${YELLOW}Testing verify-fix.sh${NC}"
echo "------------------------------------------"

VERIFY_SCRIPT="$PLUGIN_FIX_DIR/scripts/verify-fix.sh"

# Test 1: Verify frontmatter fix on perfect file
result=$("$VERIFY_SCRIPT" "missing-frontmatter" "$FIXTURES_DIR/apply-fix/perfect-agent.md")
resolved=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('issue_resolved', False))")
run_test "Verify frontmatter on perfect file" "True" "$resolved"

# Test 2: Verify frontmatter fix on broken file
result=$("$VERIFY_SCRIPT" "missing-frontmatter" "$FIXTURES_DIR/apply-fix/agent-missing-frontmatter.md")
resolved=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('issue_resolved', False))")
run_test "Verify frontmatter on broken file" "False" "$resolved"

# Test 3: Verify array-syntax on fixed file
result=$("$VERIFY_SCRIPT" "array-syntax-tools" "$FIXTURES_DIR/apply-fix/perfect-agent.md")
resolved=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('issue_resolved', False))")
run_test "Verify array-syntax on good file" "True" "$resolved"

# Test 4: Verify rule-6 on good file
result=$("$VERIFY_SCRIPT" "rule-6-violation" "$FIXTURES_DIR/apply-fix/perfect-agent.md")
resolved=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('issue_resolved', False))")
run_test "Verify rule-6 on good file" "True" "$resolved"

# Test 5: Verify rule-6 on violating file
result=$("$VERIFY_SCRIPT" "rule-6-violation" "$FIXTURES_DIR/apply-fix/agent-task-tool.md")
resolved=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('issue_resolved', False))")
run_test "Verify rule-6 on violating file" "False" "$resolved"

# Test 6: Handle missing file
result=$("$VERIFY_SCRIPT" "missing-frontmatter" "/nonexistent/file.md" 2>&1 || true)
run_test_contains "Handle missing file" "not found" "$result"

echo ""

# ==========================================
# Summary
# ==========================================
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}/$TOTAL"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}/$TOTAL"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
