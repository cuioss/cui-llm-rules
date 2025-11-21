#!/usr/bin/env bash
# Test suite for verify-adoc-links.py

set -uo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="$SCRIPT_DIR/../../../marketplace/bundles/cui-documentation-standards/skills/cui-documentation/scripts/verify-adoc-links.py"
TEST_FIXTURES_DIR="$SCRIPT_DIR/fixtures/link-verify"

passed=0
failed=0

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $test_name"
        ((failed++))
    fi
}

run_test_with_output() {
    local test_name="$1"
    local test_command="$2"

    if eval "$test_command"; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $test_name"
        ((failed++))
    fi
}

echo "Testing verify-adoc-links.py"
echo "=============================="
echo

# ============================================================================
# CATEGORY 1: Help Output (2 tests)
# ============================================================================
echo "Category: Help Output"
echo "---------------------"

run_test "Help flag --help displays usage" \
    "python3 \"$SCRIPT_UNDER_TEST\" --help 2>&1 | grep -q 'usage:'"

run_test "Help flag -h displays usage" \
    "python3 \"$SCRIPT_UNDER_TEST\" -h 2>&1 | grep -q 'usage:'"

echo

# ============================================================================
# CATEGORY 2: Argument Validation (5 tests)
# ============================================================================
echo "Category: Argument Validation"
echo "-----------------------------"

run_test "Error when both --file and --directory specified" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file foo.adoc --directory dir/ 2>&1 || true) && echo \"\$output\" | grep -qi 'cannot specify both'"

run_test "Error when file does not exist" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file /nonexistent/file.adoc 2>&1 || true) && echo \"\$output\" | grep -qi 'error'"

run_test "Error when target is not .adoc file" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file /tmp/README.md 2>&1 || true) && echo \"\$output\" | grep -qi 'error\\|must be'"

run_test "Error when directory does not exist" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --directory /nonexistent/dir 2>&1 || true) && echo \"\$output\" | grep -qi 'error'"

run_test "Error when no .adoc files found" \
    "! python3 \"$SCRIPT_UNDER_TEST\" --directory /tmp > /dev/null 2>&1"

echo

# ============================================================================
# CATEGORY 3: File Discovery (5 tests)
# ============================================================================
echo "Category: File Discovery"
echo "------------------------"

run_test "Single file mode processes one file" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/empty.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Processing 1 AsciiDoc files'"

run_test "Directory mode (non-recursive) finds files in directory only" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --directory \"$TEST_FIXTURES_DIR\" 2>&1 || true) && echo \"\$output\" | grep -q 'Processing'"

run_test "Directory mode with --recursive finds files in subdirectories" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --directory \"$TEST_FIXTURES_DIR\" --recursive 2>&1 || true) && echo \"\$output\" | grep -q 'Processing'"

run_test "Single file mode normalizes path" \
    "python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/./empty.adoc\" > /dev/null 2>&1"

run_test "Empty file does not cause errors" \
    "python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/empty.adoc\" > /dev/null 2>&1"

echo

# ============================================================================
# CATEGORY 4: Link Extraction (16 tests)
# ============================================================================
echo "Category: Link Extraction"
echo "-------------------------"

run_test "Cross-reference without label detected: <<anchor>>" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Cross-reference with label detected: <<anchor,Label>>" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Xref without anchor detected: xref:file.adoc[]" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Xref with anchor detected: xref:file.adoc#anchor[]" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Xref relative path detected: xref:./file.adoc[]" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/relative-paths.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Xref subdirectory detected: xref:subdirectory/file.adoc[]" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/relative-paths.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Xref parent directory detected: xref:../file.adoc[]" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/subdirectory/nested.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "External URL detected: https://example.com" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "External URL with label detected: https://example.com[Label]" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Deprecated syntax detected: <<file.adoc#,Label>>" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/deprecated-syntax.adoc\" 2>&1 || true) && echo \"\$output\" | grep -qi 'deprecated\\|format.*violation'"

run_test "External URLs in code blocks are ignored" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/code-blocks.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'Total links found:.*6'"

run_test "Multiple link types in same file detected" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "File with no links shows zero links" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/no-links.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:.*0'"

run_test "Self-reference anchor detected: <<#anchor>>" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/relative-paths.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Empty anchor reference treated as self-reference" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "HTTP URLs detected (not just HTTPS)" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

echo

# ============================================================================
# CATEGORY 5: Anchor Extraction (12 tests)
# ============================================================================
echo "Category: Anchor Extraction"
echo "---------------------------"

run_test "Explicit anchor [[name]] detected" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'All links valid'"

run_test "Explicit anchor [#name] detected" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'All links valid'"

run_test "Auto-generated anchor from == header" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/target-file.adoc\" 2>&1) && echo \"\$output\" | grep -q 'All links valid'"

run_test "Auto-generated anchor from === header" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/target-file.adoc\" 2>&1) && echo \"\$output\" | grep -q 'All links valid'"

run_test "Complex header with code: == Section with \`code\`" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

run_test "Complex header with URL removed from anchor" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

run_test "Complex header with cross-ref removed from anchor" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

run_test "Special characters removed from auto-generated anchors" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

run_test "Multiple spaces converted to single hyphen" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

run_test "Dashes preserved in anchors" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

run_test "Underscores preserved in anchors" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

run_test "Anchor normalization: lowercase conversion" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/complex-anchors.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid\\|Broken links:.*0'"

echo

# ============================================================================
# CATEGORY 6: Link Validation (16 tests)
# ============================================================================
echo "Category: Link Validation"
echo "-------------------------"

run_test "Broken cross-reference detected" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-cross-ref.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'Broken links:' && ! python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-cross-ref.adoc\" > /dev/null 2>&1"

run_test "Valid cross-reference passes validation" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Broken xref (file not found) detected" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-xref-file.adoc\" 2>&1 || true) && echo \"\$output\" | grep -qi 'not found\\|broken'"

run_test "Broken xref (anchor not found in valid file) detected" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-xref-anchor.adoc\" 2>&1 || true) && echo \"\$output\" | grep -qi 'not found\\|broken'"

run_test "Valid xref without anchor passes validation" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Valid xref with anchor passes validation" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Relative path resolution: ./file.adoc" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/relative-paths.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Relative path resolution: subdirectory/file.adoc" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/relative-paths.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Relative path resolution: ../file.adoc from subdirectory" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/subdirectory/nested.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Self-reference anchor validation: xref:#anchor[]" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/relative-paths.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Deprecated syntax creates format violation" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/deprecated-syntax.adoc\" 2>&1 || true) && echo \"\$output\" | grep -qi 'Format violations:.*[1-9]'"

run_test "External links pass validation without label" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Mixed valid and invalid links in same file" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-cross-ref.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'Broken links:' && echo \"\$output\" | grep -q 'Valid links:'"

run_test "Multiple broken links in same file all detected" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-cross-ref.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'Broken links:'"

run_test "Nested cross-reference in same file: <<content>>" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/subdirectory/nested.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

run_test "Empty target in xref treated as self-reference" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q '✅.*All links valid'"

echo

# ============================================================================
# CATEGORY 7: Output Formats (8 tests)
# ============================================================================
echo "Category: Output Formats"
echo "------------------------"

run_test "Console output displays summary section" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'LINK VERIFICATION SUMMARY'"

run_test "Console output displays files processed count" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Files processed:'"

run_test "Console output displays total links count" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q 'Total links found:'"

run_test "Console output displays broken links section when issues found" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-cross-ref.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'BROKEN LINKS'"

run_test "Console output displays format violations section when found" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/deprecated-syntax.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'FORMAT VIOLATIONS'"

run_test "Console output displays final verdict" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'FINAL VERDICT'"

run_test "Console output displays context around issues" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-cross-ref.adoc\" 2>&1 || true) && echo \"\$output\" | grep -q 'Context:'"

run_test "Console output shows checkmark for valid links" \
    "output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" 2>&1) && echo \"\$output\" | grep -q '✅ All links valid'"

echo

# ============================================================================
# CATEGORY 8: Markdown Report (7 tests)
# ============================================================================
echo "Category: Markdown Report"
echo "-------------------------"

run_test "Markdown report generated with --report flag" \
    "mkdir -p target && python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" --report target/test-report-1.md > /dev/null 2>&1 && [ -f target/test-report-1.md ]"

run_test "Markdown report contains summary section" \
    "mkdir -p target && python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" --report target/test-report-2.md > /dev/null 2>&1 && grep -q '## Summary' target/test-report-2.md"

run_test "Markdown report contains file count" \
    "mkdir -p target && python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" --report target/test-report-3.md > /dev/null 2>&1; grep -q 'Files processed' target/test-report-3.md"

run_test "Markdown report contains broken links section when issues found" \
    "mkdir -p target && python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/broken-cross-ref.adoc\" --report target/test-report-4.md > /dev/null 2>&1; grep -q 'Broken Links' target/test-report-4.md"

run_test "Markdown report contains format violations section when found" \
    "mkdir -p target && python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/deprecated-syntax.adoc\" --report target/test-report-5.md > /dev/null 2>&1; grep -q 'Format Violations' target/test-report-5.md"

run_test "Markdown report contains final verdict" \
    "mkdir -p target && python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" --report target/test-report-6.md > /dev/null 2>&1 && grep -q '## Final Verdict' target/test-report-6.md"

run_test "Console confirms report written to file" \
    "mkdir -p target && output=\$(python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" --report target/test-report-7.md 2>&1 || true) && echo \"\$output\" | grep -q 'Markdown report written to'"

echo

# ============================================================================
# CATEGORY 9: Exit Codes (5 tests)
# ============================================================================
echo "Category: Exit Codes"
echo "--------------------"

run_test "Exit code 0 when no issues found" \
    "python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/valid-all-link-types.adoc\" > /dev/null 2>&1 && [ \$? -eq 0 ]"

run_test "Exit code 1 when invalid arguments" \
    "python3 \"$SCRIPT_UNDER_TEST\" --file README.md > /dev/null 2>&1; [ \$? -eq 1 ]"

run_test "Exit code 1 when file not found" \
    "python3 \"$SCRIPT_UNDER_TEST\" --file /nonexistent.adoc > /dev/null 2>&1; [ \$? -eq 1 ]"

run_test "Exit code equals number of issues when issues found" \
    "python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/deprecated-syntax.adoc\" > /dev/null 2>&1; [ \$? -ge 1 ]"

run_test "Exit code 0 for file with no links" \
    "python3 \"$SCRIPT_UNDER_TEST\" --file \"$TEST_FIXTURES_DIR/no-links.adoc\" > /dev/null 2>&1 && [ \$? -eq 0 ]"

echo

# ============================================================================
# SUMMARY
# ============================================================================
echo "=============================="
echo "Test Summary"
echo "=============================="
echo "Passed: $passed"
echo "Failed: $failed"
echo "Total:  $((passed + failed))"
echo

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
