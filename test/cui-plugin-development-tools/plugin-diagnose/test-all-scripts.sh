#!/bin/bash
# Quick smoke tests for all plugin-diagnose scripts
#
# Usage: ./test-all-scripts.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-diagnose/scripts"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

test_script() {
    local script_name="$1"
    shift
    local args="$@"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Test: $script_name ... "

    if result=$("$SCRIPTS_DIR/$script_name" $args 2>&1); then
        # Verify JSON output
        if echo "$result" | jq . > /dev/null 2>&1; then
            echo -e "${GREEN}PASS${NC} (valid JSON)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            return 0
        else
            echo -e "${RED}FAIL${NC} (invalid JSON)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            return 1
        fi
    else
        echo -e "${RED}FAIL${NC} (execution error)"
        echo "  Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "========================================"
echo "Plugin-Diagnose Scripts Smoke Tests"
echo "========================================"
echo ""

# Test analyze-markdown-file.sh
test_script "analyze-markdown-file.sh" "$SCRIPT_DIR/fixtures/markdown-file/valid-agent.md" "agent"

# Test analyze-tool-coverage.sh
test_script "analyze-tool-coverage.sh" "$SCRIPT_DIR/fixtures/markdown-file/valid-agent.md"

# Test analyze-skill-structure.sh (use a real skill)
test_script "analyze-skill-structure.sh" "$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-diagnose"

# Test validate-references.py
test_script "validate-references.py" "$SCRIPT_DIR/fixtures/markdown-file/valid-agent.md"

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo "Total:  $TESTS_RUN"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed!${NC}"
    exit 1
fi
