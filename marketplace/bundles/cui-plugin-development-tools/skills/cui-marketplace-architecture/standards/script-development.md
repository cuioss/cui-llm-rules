# Script Development Standards

Standards for creating analysis scripts in the cui-marketplace-architecture skill.

## Purpose

This document defines standards for creating deterministic analysis scripts used by diagnose agents and commands. These scripts provide reliable, testable, and efficient alternatives to AI-based analysis for file operations, structure validation, and metadata extraction.

## When to Use Scripts vs AI Agents

### Use Scripts For:
- **Deterministic operations**: File discovery, counting, structure validation
- **Metadata extraction**: YAML parsing, frontmatter extraction, pattern matching
- **Ground truth operations**: Line counts, word counts, file existence checks
- **High-frequency operations**: Called repeatedly across many files
- **Performance-critical paths**: Inventory scanning, bulk validation

### Use AI Agents For:
- **Semantic understanding**: Code quality assessment, architectural patterns
- **Complex reasoning**: Issue categorization, prioritization, recommendations
- **Context-dependent decisions**: When to fix vs suppress, refactoring strategies
- **Natural language output**: Reports, summaries, explanations

### Key Principle:
Scripts provide **exact, reproducible data**. Agents provide **interpretation and recommendations** based on that data.

## Default Language: Shell Script

### Shell Script as Default
**Use shell scripts (bash) unless there is a significant benefit from another language.**

**Rationale**:
- Available everywhere (no installation required)
- Excellent for file operations, text processing
- Direct access to Unix tools (wc, grep, sed, awk, jq)
- Fast execution for simple operations
- Easy to test and debug

**When to consider alternatives**:
- Complex JSON manipulation (Python with json library)
- Regular expression complexity exceeds sed/awk capabilities
- Need for data structures (arrays, maps) beyond bash capabilities
- Performance-critical operations on large datasets

**Decision tree**:
1. Can it be done with standard Unix tools + jq? → Shell script
2. Requires complex JSON or YAML manipulation? → Consider Python
3. Requires complex data structures? → Consider Python
4. Simple file operations + text processing? → Shell script (default)

## Script Structure

### Standard Template

```bash
#!/bin/bash
# script-name.sh
# Brief description of what this script does
#
# Usage: ./script-name.sh <param1> <param2> [--flag]
# Returns: JSON object with analysis results

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# ============================================================================
# USAGE AND HELP
# ============================================================================

usage() {
    cat <<EOF
Usage: $(basename "$0") <file_path> [options]

Description:
  Brief description of what the script does

Arguments:
  file_path    Path to the file to analyze (required)

Options:
  --flag       Optional flag description
  --help       Show this help message

Output:
  JSON object with analysis results

Exit Codes:
  0 - Success
  1 - Invalid arguments or file not found
  2 - Analysis error

Examples:
  $(basename "$0") path/to/file.md
  $(basename "$0") path/to/file.md --flag
EOF
    exit 0
}

# ============================================================================
# PARAMETER PARSING
# ============================================================================

# Check for help flag
if [ $# -eq 0 ] || [ "$1" = "--help" ]; then
    usage
fi

# Required parameters
FILE_PATH="${1:-}"

# Optional parameters
FLAG=false
if [ "${2:-}" = "--flag" ]; then
    FLAG=true
fi

# ============================================================================
# INPUT VALIDATION
# ============================================================================

# Validate required parameters
if [ -z "$FILE_PATH" ]; then
    echo '{"error": "file_path parameter required"}' >&2
    exit 1
fi

# Validate file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\"}" >&2
    exit 1
fi

# ============================================================================
# ANALYSIS LOGIC
# ============================================================================

# Perform analysis operations
METRIC=$(wc -l < "$FILE_PATH" | tr -d ' ')

# ============================================================================
# JSON OUTPUT
# ============================================================================

# Helper function for JSON escaping
escape_json() {
    local input="$1"
    # Replace backslash, then quotes, then newlines, then tabs
    echo "$input" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//'
}

# Build and output JSON
cat <<EOF
{
  "file_path": "$FILE_PATH",
  "metrics": {
    "line_count": $METRIC
  },
  "status": "success"
}
EOF
```

### Required Components

1. **Shebang and header comment**: Script path, description, usage
2. **Strict error handling**: `set -euo pipefail`
3. **Usage function**: Complete help text with examples
4. **Parameter parsing**: Clear validation and defaults
5. **Input validation**: Check required parameters and file existence
6. **Analysis logic**: Core functionality with comments
7. **JSON output**: Structured data with proper escaping
8. **Exit codes**: 0=success, 1=invalid input, 2=analysis error

## JSON Output Format

### Standard Structure

All scripts **MUST** return valid JSON to stdout on success:

```json
{
  "file_path": "/path/to/analyzed/file",
  "metrics": {
    "line_count": 521,
    "word_count": 3500
  },
  "analysis": {
    "classification": "LARGE",
    "score": 85.5
  },
  "status": "success"
}
```

### Error Handling

Errors **MUST** be returned to stderr as JSON, with non-zero exit code:

```json
{
  "error": "File not found: /path/to/file",
  "file_path": "/path/to/file",
  "exit_code": 1
}
```

### JSON Escaping

**CRITICAL**: Always escape special characters in JSON strings:

```bash
escape_json() {
    local input="$1"
    # Replace backslash, then quotes, then newlines, then tabs
    echo "$input" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//'
}

# Usage
ESCAPED=$(escape_json "$RAW_TEXT")
echo "\"field\": \"$ESCAPED\""
```

### Required Fields

Every JSON response **MUST** include:
- `file_path` or relevant input parameter
- `status`: "success" or "error"
- Analysis results (script-specific)

## Error Handling Patterns

### Exit Codes

**Standard exit codes**:
- `0`: Success - analysis completed, JSON on stdout
- `1`: Invalid arguments - missing/invalid parameters, file not found
- `2`: Analysis error - script failed during processing

### Error Message Format

```bash
# Invalid argument
if [ -z "$REQUIRED_PARAM" ]; then
    echo '{"error": "parameter_name required", "exit_code": 1}' >&2
    exit 1
fi

# File not found
if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\", \"exit_code\": 1}" >&2
    exit 1
fi

# Analysis error
if ! result=$(some_command 2>&1); then
    echo "{\"error\": \"Analysis failed: $result\", \"exit_code\": 2}" >&2
    exit 2
fi
```

### Defensive Programming

```bash
# Always use strict mode
set -euo pipefail

# Check command availability
if ! command -v jq &> /dev/null; then
    echo '{"error": "jq command not found - please install jq"}' >&2
    exit 2
fi

# Validate file is readable
if [ ! -r "$FILE_PATH" ]; then
    echo "{\"error\": \"File not readable: $FILE_PATH\"}" >&2
    exit 1
fi

# Handle empty files gracefully
if [ ! -s "$FILE_PATH" ]; then
    LINE_COUNT=0  # Empty file = 0 lines
else
    LINE_COUNT=$(wc -l < "$FILE_PATH" | tr -d ' ')
fi
```

## Test-Driven Development

### Test Suite Structure

Follow the pattern from `test-analyze-markdown-file.sh`:

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# TEST SETUP
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/script-name.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

run_test() {
    local test_name="$1"
    local test_file="$2"
    local expected_value="$3"
    local jq_query="$4"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Testing: $test_name ... "

    # Run script and capture output
    if ! result=$("$SCRIPT_UNDER_TEST" "$test_file" 2>&1); then
        echo -e "${RED}FAIL${NC} - Script returned error"
        echo "  Output: $result"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Extract value using jq
    actual_value=$(echo "$result" | jq -r "$jq_query")

    # Compare
    if [ "$actual_value" = "$expected_value" ]; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: $expected_value"
        echo "  Actual:   $actual_value"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# TEST CASES
# ============================================================================

echo "========================================"
echo "Testing: script-name.sh"
echo "========================================"
echo ""

# Test 1: Basic functionality
run_test "Basic line count" \
    "$SCRIPT_DIR/fixtures/test-file.md" \
    "42" \
    ".metrics.line_count"

# Test 2: Error handling
run_test "Missing file error" \
    "/nonexistent/file.md" \
    "File not found" \
    ".error"

# ============================================================================
# TEST SUMMARY
# ============================================================================

echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Total tests:   $TESTS_RUN"
echo -e "Passed:        ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:        ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
```

### Test Fixtures

Create test fixtures in `test/cui-plugin-development-tools/cui-marketplace-architecture/fixtures/<category>/`:

```
fixtures/
├── markdown/
│   ├── valid-yaml.md           # Test valid YAML parsing
│   ├── invalid-yaml.md         # Test error handling
│   ├── missing-fields.md       # Test validation
│   └── edge-cases.md           # Test edge cases
├── tool-coverage/
│   ├── perfect-fit.md          # Test 100% coverage
│   └── missing-tool.md         # Test detection
└── <category>/
    └── test-file.md
```

### Ground Truth Validation

**CRITICAL**: Always validate against ground truth:

```bash
# Verify line count matches wc -l exactly
run_test() {
    local test_file="$1"

    # Get script result
    script_lines=$(script.sh "$test_file" | jq -r '.metrics.line_count')

    # Get ground truth
    wc_lines=$(wc -l < "$test_file" | tr -d ' ')

    # Must match exactly
    if [ "$script_lines" != "$wc_lines" ]; then
        echo "FAIL: Line count mismatch"
        return 1
    fi
}
```

### Test Coverage Requirements

**Every script MUST have tests for**:
- [ ] Valid input (happy path)
- [ ] Missing file (error handling)
- [ ] Invalid parameters (validation)
- [ ] Edge cases (empty file, large file)
- [ ] Ground truth validation (wc -l, actual counts)
- [ ] JSON output validity (valid JSON, required fields)

## Deterministic Output

### Ground Truth Alignment

Scripts **MUST** match ground truth exactly:

```bash
# ✓ CORRECT: Use wc -l directly
LINE_COUNT=$(wc -l < "$FILE_PATH" | tr -d ' ')

# ✗ WRONG: Estimate or count in bash
LINE_COUNT=0
while IFS= read -r line; do
    LINE_COUNT=$((LINE_COUNT + 1))
done < "$FILE_PATH"
```

### Consistent Results

Scripts **MUST** return identical results for identical inputs:

- No random values
- No timestamps (unless explicitly required)
- No environment-dependent paths (use relative paths)
- Sort results alphabetically/numerically for consistent ordering

### Example: Deterministic File Discovery

```bash
# Find all .md files, sorted consistently
FILES=$(find "$DIRECTORY" -name "*.md" -type f | sort)

# Count files deterministically
FILE_COUNT=$(echo "$FILES" | grep -c "^" || echo 0)
```

## Input Validation

### Required Validations

**Every script MUST validate**:

1. **Parameter presence**:
```bash
if [ $# -eq 0 ]; then
    echo '{"error": "Usage: script.sh <file_path>"}' >&2
    exit 1
fi
```

2. **File existence**:
```bash
if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\"}" >&2
    exit 1
fi
```

3. **File readability**:
```bash
if [ ! -r "$FILE_PATH" ]; then
    echo "{\"error\": \"File not readable: $FILE_PATH\"}" >&2
    exit 1
fi
```

4. **Format validation** (if applicable):
```bash
if [[ ! "$FILE_PATH" =~ \.md$ ]]; then
    echo "{\"error\": \"Expected .md file, got: $FILE_PATH\"}" >&2
    exit 1
fi
```

### Early Exit on Invalid Input

Validate **before** performing any analysis:

```bash
# ✓ CORRECT: Validate first, then analyze
validate_input || exit 1
perform_analysis

# ✗ WRONG: Start analysis before validation
perform_analysis
validate_input  # Too late!
```

## Integration with Agents

### Tool Permission Pattern

Agents calling scripts **MUST** declare Bash tool permission:

```yaml
---
name: diagnose-command
description: Analyzes command files for bloat and quality
tools: [Read, Bash(./.claude/skills/cui-marketplace-architecture/scripts/analyze-markdown-file.sh:*)]
---
```

**Path pattern**: `./.claude/skills/cui-marketplace-architecture/scripts/<script-name>.sh`

### Agent Workflow Integration

**Step 1: Call script FIRST (before Read)**
```markdown
### Step 2: Analyze File Structure

**CRITICAL: Execute the analysis script FIRST (before any Read operations):**

```bash
./.claude/skills/cui-marketplace-architecture/scripts/analyze-markdown-file.sh {command_path}
```
```

**Step 2: Parse JSON output**
```markdown
**Parse the JSON output and extract:**
- `metrics.line_count` → Store as TOTAL_LINES
- `bloat.classification` → Store bloat classification
- `frontmatter.present` → Store for validation
```

**Step 3: Use parsed data in analysis**
```markdown
**Use script data for deterministic checks:**
- Line count from script (matches wc -l exactly)
- Bloat classification from script
- YAML validity from script
```

### Example Agent Integration

```markdown
## YOUR TASK

Analyze command file for bloat, quality, and standards compliance.

## WORKFLOW

### Step 1: Validate Input

Check `command_path` parameter is provided and valid.

### Step 2: Run Analysis Script

**CRITICAL: Call script FIRST:**

```bash
./.claude/skills/cui-marketplace-architecture/scripts/analyze-markdown-file.sh {command_path}
```

**Parse JSON output:**
```json
{
  "metrics": {"line_count": 521, "word_count": 3500},
  "bloat": {"classification": "LARGE", "score": 130.2},
  "frontmatter": {"present": true, "yaml_valid": true},
  "continuous_improvement_rule": {"present": true}
}
```

Store values:
- TOTAL_LINES = 521
- BLOAT_CLASS = "LARGE"
- YAML_VALID = true
- HAS_CI_RULE = true

### Step 3: Perform AI Analysis

Use script data as **ground truth** for:
- Bloat detection (use script classification)
- Line count (use script count)
- YAML validation (use script result)

Perform AI analysis for:
- Issue categorization
- Content quality assessment
- Recommendations

### Step 4: Generate Report

Combine script data + AI analysis into final report.
```

## Tool Usage Standards

### Follow cui-diagnostic-patterns Skill

**CRITICAL**: Scripts called by agents should follow non-prompting tool patterns when agents themselves need file operations.

**For scripts**: Shell scripts naturally avoid prompts
**For agents calling scripts**: Follow cui-diagnostic-patterns:
- Use Glob instead of `find` via Bash
- Use Read instead of `test -f` via Bash
- Use Grep instead of `grep` via Bash
- Reserve Bash only for: Git, build commands, **and approved scripts**

### Script as Approved Bash Usage

Scripts in `./.claude/skills/cui-marketplace-architecture/scripts/` are **approved Bash usage** because:
- They return deterministic results
- They are tested and verified
- They don't trigger user prompts
- They are self-contained and validated

## Documentation Format

### Script Header Documentation

**Every script MUST include**:

```bash
#!/bin/bash
# script-name.sh
# Brief one-line description
#
# Usage: ./script-name.sh <param1> [--option]
# Returns: JSON object with analysis results
#
# Purpose:
#   Detailed description of what this script does and why it exists.
#   Explain the problem it solves and how it integrates with agents.
#
# Parameters:
#   param1       - Description (required)
#   --option     - Description (optional, default: value)
#
# Output:
#   JSON structure:
#   {
#     "field": "value",
#     "metrics": {...}
#   }
#
# Exit Codes:
#   0 - Success
#   1 - Invalid arguments or file not found
#   2 - Analysis error
#
# Examples:
#   ./script-name.sh path/to/file.md
#   ./script-name.sh path/to/file.md --option
#
# Dependencies:
#   - jq (required for JSON processing)
#   - standard Unix tools (wc, grep, sed, awk)
```

### README Documentation

Update `test/cui-plugin-development-tools/cui-marketplace-architecture/README.md`:

```markdown
## Scripts

### script-name.sh

**Purpose**: Brief description

**Usage**:
```bash
./script-name.sh <file_path>
```

**Output**: JSON with analysis results

**Tests**: test-script-name.sh (15 tests, 100% pass rate)
```

## Performance Considerations

### Optimization Guidelines

1. **Use built-in tools**: Prefer wc, grep, sed, awk over bash loops
2. **Avoid unnecessary reads**: Read file once, extract multiple metrics
3. **Pipeline efficiently**: Use pipes to avoid intermediate files
4. **Limit output**: Don't extract huge text blocks (limit to ~50 lines)
5. **Early exit**: Fail fast on validation errors

### Performance Patterns

```bash
# ✓ GOOD: Single pass, multiple metrics
LINE_COUNT=$(wc -l < "$FILE")
WORD_COUNT=$(wc -w < "$FILE")

# ✗ BAD: Multiple file reads
while IFS= read -r line; do
    LINE_COUNT=$((LINE_COUNT + 1))
done < "$FILE"
```

### Benchmarking

Test scripts with realistic workloads:
```bash
time for i in {1..100}; do
    ./script.sh test-file.md > /dev/null
done
```

Target: <100ms per file for typical commands/agents

## Quality Checklist

### Before Committing a Script

- [ ] Script uses shell (bash) unless significant benefit from alternative
- [ ] Script includes complete header documentation
- [ ] Script returns valid JSON to stdout
- [ ] Script handles errors with JSON to stderr
- [ ] Script validates all input parameters
- [ ] Script checks file existence/readability
- [ ] Script uses deterministic operations (matches ground truth)
- [ ] Script has proper exit codes (0, 1, 2)
- [ ] Script is executable (`chmod +x`)
- [ ] Test suite created with 100% coverage
- [ ] Test fixtures created for all scenarios
- [ ] All tests validate against ground truth
- [ ] All tests pass (100% success rate)
- [ ] README.md updated with script documentation
- [ ] Agent integration documented (if applicable)

## References

### Related Skills
- **cui-general-development-rules**: When to ask users, research requirements, dependency management
- **cui-diagnostic-patterns**: Tool usage patterns for non-prompting file operations in agents

### Integration Points
- **diagnose-command agent**: Uses analyze-markdown-file.sh
- **diagnose-agent agent**: Uses analyze-markdown-file.sh, analyze-tool-coverage.sh
- **diagnose-skill agent**: Uses analyze-skill-structure.sh
- **Multiple commands**: Will use scan-marketplace-inventory.sh

### Test Examples
- **test-analyze-markdown-file.sh**: Reference implementation for test suite pattern
- **analyze-markdown-file.sh**: Reference implementation for script structure
