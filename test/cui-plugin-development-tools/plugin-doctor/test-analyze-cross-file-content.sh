#!/bin/bash
# Test script for analyze-cross-file-content.py
# Validates cross-file content analysis functionality

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-doctor/scripts/analyze-cross-file-content.py"
FIXTURES_DIR="$SCRIPT_DIR/fixtures/cross-file-analysis"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

pass() {
    echo -e "${GREEN}✓${NC} $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    FAILED=$((FAILED + 1))
}

info() {
    echo -e "${YELLOW}→${NC} $1"
}

echo "============================================="
echo "Testing analyze-cross-file-content.py"
echo "============================================="
echo ""

# Test 1: Script exists and is executable
info "Test 1: Script exists and is executable"
if [ -f "$SCRIPT_PATH" ] && [ -x "$SCRIPT_PATH" ]; then
    pass "Script exists and is executable"
else
    fail "Script not found or not executable: $SCRIPT_PATH"
fi

# Test 2: Help output
info "Test 2: Help output"
HELP_OUTPUT=$(python3 "$SCRIPT_PATH" --help 2>&1)
if echo "$HELP_OUTPUT" | grep -q "analyze-cross-file-content.py"; then
    pass "Help output available"
else
    fail "Help output missing or incorrect"
fi

# Test 3: Missing argument error
info "Test 3: Missing argument error"
set +e  # Disable exit on error temporarily
ERROR_OUTPUT=$(python3 "$SCRIPT_PATH" 2>&1)
EXIT_CODE=$?
set -e
if [ $EXIT_CODE -ne 0 ] && echo "$ERROR_OUTPUT" | grep -q "error"; then
    pass "Returns error for missing argument"
else
    fail "Should return error for missing argument"
fi

# Test 4: Invalid path error
info "Test 4: Invalid path error"
set +e
ERROR_OUTPUT=$(python3 "$SCRIPT_PATH" --skill-path "/nonexistent/path" 2>&1)
EXIT_CODE=$?
set -e
if [ $EXIT_CODE -ne 0 ] && echo "$ERROR_OUTPUT" | grep -q "not found"; then
    pass "Returns error for invalid path"
else
    fail "Should return error for invalid path"
fi

# Test 5: Analyze skill with duplicates
info "Test 5: Analyze skill with duplicates"
DUPLICATES_SKILL="$FIXTURES_DIR/skill-with-duplicates"
if [ -d "$DUPLICATES_SKILL" ]; then
    OUTPUT=$(python3 "$SCRIPT_PATH" --skill-path "$DUPLICATES_SKILL" 2>&1)

    # Check JSON structure
    if echo "$OUTPUT" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
        pass "Returns valid JSON for skill with duplicates"
    else
        fail "Invalid JSON output for skill with duplicates"
    fi

    # Check for exact duplicates detection (Code Standards section is duplicated)
    if echo "$OUTPUT" | grep -q "exact_duplicates"; then
        EXACT_COUNT=$(echo "$OUTPUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(len(d.get('exact_duplicates', [])))" 2>/dev/null)
        if [ "${EXACT_COUNT:-0}" -ge 1 ]; then
            pass "Detected exact duplicates (found $EXACT_COUNT)"
        else
            fail "Should detect exact duplicates in Code Standards section"
        fi
    else
        fail "Missing exact_duplicates field"
    fi

    # Check for extraction candidates (template placeholders)
    if echo "$OUTPUT" | grep -q "extraction_candidates"; then
        EXTRACT_COUNT=$(echo "$OUTPUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(len(d.get('extraction_candidates', [])))" 2>/dev/null)
        if [ "${EXTRACT_COUNT:-0}" -ge 1 ]; then
            pass "Detected extraction candidates (found $EXTRACT_COUNT)"
        else
            info "No extraction candidates found (placeholders may be in code blocks)"
        fi
    else
        fail "Missing extraction_candidates field"
    fi

    # Check summary
    if echo "$OUTPUT" | grep -q '"llm_review_required"'; then
        pass "Contains llm_review_required flag"
    else
        fail "Missing llm_review_required flag in summary"
    fi
else
    fail "Fixture directory not found: $DUPLICATES_SKILL"
fi

# Test 6: Analyze clean skill
info "Test 6: Analyze clean skill"
CLEAN_SKILL="$FIXTURES_DIR/skill-clean"
if [ -d "$CLEAN_SKILL" ]; then
    OUTPUT=$(python3 "$SCRIPT_PATH" --skill-path "$CLEAN_SKILL" 2>&1)

    # Check JSON structure
    if echo "$OUTPUT" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
        pass "Returns valid JSON for clean skill"
    else
        fail "Invalid JSON output for clean skill"
    fi

    # Check for no exact duplicates
    EXACT_COUNT=$(echo "$OUTPUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(len(d.get('exact_duplicates', [])))" 2>/dev/null)
    if [ "${EXACT_COUNT:-0}" -eq 0 ]; then
        pass "No exact duplicates in clean skill"
    else
        info "Found $EXACT_COUNT duplicates in clean skill (may be acceptable)"
    fi

    # Check files_analyzed count
    FILES_COUNT=$(echo "$OUTPUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(d.get('files_analyzed', 0))" 2>/dev/null)
    if [ "${FILES_COUNT:-0}" -ge 3 ]; then
        pass "Analyzed multiple files (found $FILES_COUNT)"
    else
        fail "Should analyze multiple files in clean skill"
    fi
else
    fail "Fixture directory not found: $CLEAN_SKILL"
fi

# Test 7: Custom similarity threshold
info "Test 7: Custom similarity threshold"
OUTPUT=$(python3 "$SCRIPT_PATH" --skill-path "$CLEAN_SKILL" --similarity-threshold 0.3 2>&1)
if echo "$OUTPUT" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
    pass "Accepts custom similarity threshold"
else
    fail "Should accept custom similarity threshold"
fi

# Test 8: Content blocks extraction
info "Test 8: Content blocks extraction"
OUTPUT=$(python3 "$SCRIPT_PATH" --skill-path "$DUPLICATES_SKILL" 2>&1)
BLOCKS_COUNT=$(echo "$OUTPUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(len(d.get('content_blocks', [])))" 2>/dev/null)
if [ "${BLOCKS_COUNT:-0}" -ge 5 ]; then
    pass "Extracted content blocks (found $BLOCKS_COUNT)"
else
    fail "Should extract multiple content blocks"
fi

echo ""
echo "============================================="
echo "Results: $PASSED passed, $FAILED failed"
echo "============================================="

if [ $FAILED -gt 0 ]; then
    exit 1
fi

exit 0
