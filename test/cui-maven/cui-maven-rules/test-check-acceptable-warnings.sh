#!/bin/bash
# Test suite for check-acceptable-warnings.py
# Tests warning categorization with JSON input/output

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$PROJECT_ROOT/marketplace/bundles/cui-maven/skills/cui-maven-rules/scripts/check-acceptable-warnings.py"

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

# Test: categorize warning as acceptable via pattern match
test_acceptable_pattern_match() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"other","message":"The POM for org.example:lib is missing","severity":"WARNING"}]' \
        --patterns '["The POM for org.example:lib is missing"]' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['acceptable']==1 and d['fixable']==0 else 1)" 2>/dev/null; then
        pass "acceptable pattern match"
    else
        fail "acceptable pattern match" "acceptable=1, fixable=0" "$result"
    fi
}

# Test: categorize warning as fixable (javadoc always fixable)
test_javadoc_always_fixable() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"javadoc_warning","message":"Missing @param tag","severity":"WARNING"}]' \
        --patterns '["Missing @param tag"]' 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['fixable']==1 and d['acceptable']==0 else 1)" 2>/dev/null; then
        pass "javadoc warnings always fixable (even with matching pattern)"
    else
        fail "javadoc warnings always fixable" "fixable=1, acceptable=0" "$result"
    fi
}

# Test: categorize unknown warning
test_unknown_warning() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"other","message":"Some random warning","severity":"WARNING"}]' \
        --patterns '[]' 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['unknown']==1 else 1)" 2>/dev/null; then
        pass "unknown warning categorization"
    else
        fail "unknown warning categorization" "unknown=1" "$result"
    fi
}

# Test: empty warnings array
test_empty_warnings() {
    result=$(python3 "$SCRIPT" \
        --warnings '[]' \
        --patterns '[]' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['total']==0 else 1)" 2>/dev/null; then
        pass "empty warnings returns success with total=0"
    else
        fail "empty warnings" "total=0" "$result"
    fi
}

# Test: filter only WARNING severity
test_filter_warning_severity() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"other","message":"error msg","severity":"ERROR"},{"type":"other","message":"warn msg","severity":"WARNING"}]' \
        --patterns '[]' 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['total']==1 else 1)" 2>/dev/null; then
        pass "filter only WARNING severity"
    else
        fail "filter only WARNING severity" "total=1" "$result"
    fi
}

# Test: acceptable_warnings object flattening
test_acceptable_warnings_object() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"other","message":"Missing POM","severity":"WARNING"}]' \
        --acceptable-warnings '{"transitive_dependency":["Missing POM"],"plugin_compatibility":[]}' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['acceptable']==1 else 1)" 2>/dev/null; then
        pass "acceptable_warnings object flattening"
    else
        fail "acceptable_warnings object flattening" "acceptable=1" "$result"
    fi
}

# Test: stdin input
test_stdin_input() {
    result=$(echo '{"warnings":[{"type":"other","message":"test warn","severity":"WARNING"}],"patterns":["test warn"]}' | python3 "$SCRIPT" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['acceptable']==1 else 1)" 2>/dev/null; then
        pass "stdin input"
    else
        fail "stdin input" "acceptable=1" "$result"
    fi
}

# Test: stdin with acceptable_warnings object
test_stdin_acceptable_warnings_object() {
    result=$(echo '{"warnings":[{"type":"other","message":"dep warn","severity":"WARNING"}],"acceptable_warnings":{"transitive_dependency":["dep warn"]}}' | python3 "$SCRIPT" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['acceptable']==1 else 1)" 2>/dev/null; then
        pass "stdin with acceptable_warnings object"
    else
        fail "stdin with acceptable_warnings object" "acceptable=1" "$result"
    fi
}

# Test: regex pattern matching
test_regex_pattern() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"other","message":"Using platform encoding UTF-8","severity":"WARNING"}]' \
        --patterns '["Using platform encoding.*"]' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['acceptable']==1 else 1)" 2>/dev/null; then
        pass "regex pattern matching"
    else
        fail "regex pattern matching" "acceptable=1" "$result"
    fi
}

# Test: strip [WARNING] prefix from patterns
test_strip_warning_prefix() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"other","message":"Some warning text","severity":"WARNING"}]' \
        --patterns '["[WARNING] Some warning text"]' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['acceptable']==1 else 1)" 2>/dev/null; then
        pass "strip [WARNING] prefix from patterns"
    else
        fail "strip [WARNING] prefix from patterns" "acceptable=1" "$result"
    fi
}

# Test: openrewrite_info is acceptable
test_openrewrite_info_acceptable() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"openrewrite_info","message":"Recipe applied","severity":"WARNING"}]' \
        --patterns '[]' 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['acceptable']==1 else 1)" 2>/dev/null; then
        pass "openrewrite_info is acceptable"
    else
        fail "openrewrite_info is acceptable" "acceptable=1" "$result"
    fi
}

# Test: exit code 0 when no fixable/unknown
test_exit_code_clean() {
    python3 "$SCRIPT" \
        --warnings '[{"type":"other","message":"accepted warn","severity":"WARNING"}]' \
        --patterns '["accepted warn"]' > /dev/null 2>&1
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        pass "exit code 0 when no fixable/unknown warnings"
    else
        fail "exit code 0 when no fixable/unknown warnings" "exit 0" "exit $exit_code"
    fi
}

# Test: exit code 1 when fixable warnings exist
test_exit_code_fixable() {
    python3 "$SCRIPT" \
        --warnings '[{"type":"javadoc_warning","message":"fix me","severity":"WARNING"}]' \
        --patterns '[]' > /dev/null 2>&1 || exit_code=$?

    if [ "${exit_code:-0}" -eq 1 ]; then
        pass "exit code 1 when fixable warnings exist"
    else
        fail "exit code 1 when fixable warnings exist" "exit 1" "exit ${exit_code:-0}"
    fi
}

# Test: categorized output structure
test_categorized_output_structure() {
    result=$(python3 "$SCRIPT" \
        --warnings '[{"type":"javadoc_warning","message":"fix","severity":"WARNING"},{"type":"other","message":"accept","severity":"WARNING"}]' \
        --patterns '["accept"]' 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'categorized' in d and 'acceptable' in d['categorized'] and 'fixable' in d['categorized'] and 'unknown' in d['categorized'] else 1)" 2>/dev/null; then
        pass "categorized output structure"
    else
        fail "categorized output structure" "categorized.{acceptable,fixable,unknown}" "$result"
    fi
}

# Test: invalid JSON error handling
test_invalid_json_warnings() {
    result=$(python3 "$SCRIPT" --warnings 'not json' --patterns '[]' 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] and 'error' in d else 1)" 2>/dev/null; then
        pass "invalid JSON in --warnings returns error"
    else
        fail "invalid JSON in --warnings returns error" "success=false" "$result"
    fi
}

# Run all tests
echo "========================================"
echo "Testing check-acceptable-warnings.py"
echo "========================================"
echo ""

run_test test_acceptable_pattern_match
run_test test_javadoc_always_fixable
run_test test_unknown_warning
run_test test_empty_warnings
run_test test_filter_warning_severity
run_test test_acceptable_warnings_object
run_test test_stdin_input
run_test test_stdin_acceptable_warnings_object
run_test test_regex_pattern
run_test test_strip_warning_prefix
run_test test_openrewrite_info_acceptable
run_test test_exit_code_clean
run_test test_exit_code_fixable
run_test test_categorized_output_structure
run_test test_invalid_json_warnings

echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN tests passed"
echo "========================================"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    exit 0
else
    exit 1
fi
