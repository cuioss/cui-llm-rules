# Script Standards

Comprehensive standards for marketplace scripts including location, documentation requirements, testing, help output, stdlib-only dependencies, JSON output format, and error handling.

## Overview

Scripts are executable files (shell scripts, Python scripts) providing deterministic validation logic. They complement AI-powered agents by handling pattern matching, parsing, and calculation tasks.

**Key Characteristics**:
- Located in `{skill-dir}/scripts/` directory
- Invoked via `Bash: {baseDir}/scripts/script-name.sh` from SKILL.md
- Stdlib-only (no external dependencies)
- JSON output format (for machine parsing)
- Executable permissions required
- Must support `--help` flag

## Script Location

**Standard Location**: `{skill-dir}/scripts/`

**Example**:
```
marketplace/bundles/cui-plugin-development-tools/skills/plugin-diagnose/
└── scripts/
    ├── analyze-markdown-file.sh
    ├── analyze-tool-coverage.sh
    ├── analyze-skill-structure.sh
    └── validate-references.py
```

**Invocation from SKILL.md**:
```bash
Bash: {baseDir}/scripts/analyze-markdown-file.sh {file_path} agent
```

## Documentation Requirements in SKILL.md

**CRITICAL**: All scripts MUST be documented in SKILL.md.

### Required Documentation

**For Each Script**:

1. **Purpose**: One-sentence description of what script does
2. **Input**: Parameters, types, formats
3. **Output**: Return format (typically JSON with schema)
4. **Usage**: Example invocation from workflow

**Template**:
```markdown
## External Resources

### Scripts (in {baseDir}/scripts/)

**1. script-name.sh**: Brief purpose statement
- **Input**: parameter1 (type), parameter2 (type)
- **Output**: JSON with {field_names}
- **Usage**:
  ```bash
  Bash: {baseDir}/scripts/script-name.sh {param1} {param2}
  ```
- **Example Output**:
  ```json
  {
    "field1": "value",
    "field2": 123
  }
  ```
```

### Example Documentation

**Real Example** (from plugin-diagnose SKILL.md):
```markdown
### Scripts (in {baseDir}/scripts/)

**1. analyze-markdown-file.sh**: Analyzes file structure, frontmatter, bloat, Rule 6/7/Pattern 22 violations
- **Input**: file path, component type (agent|command|skill)
- **Output**: JSON with structural analysis
- **Usage**:
  ```bash
  Bash: {baseDir}/scripts/analyze-markdown-file.sh {file_path} agent
  ```

**2. analyze-tool-coverage.sh**: Analyzes tool coverage and fit for agents/commands
- **Input**: file path
- **Output**: JSON with tool analysis (score, missing, unused, critical violations)
- **Usage**:
  ```bash
  Bash: {baseDir}/scripts/analyze-tool-coverage.sh {file_path}
  ```

**3. analyze-skill-structure.sh**: Analyzes skill directory structure and file references
- **Input**: skill directory path
- **Output**: JSON with structure analysis (score, missing files, unreferenced files)
- **Usage**:
  ```bash
  Bash: {baseDir}/scripts/analyze-skill-structure.sh {skill_dir}
  ```

**4. validate-references.py**: Python script for reference pre-filtering and extraction
- **Input**: file path
- **Output**: JSON with detected references and pre-filter statistics
- **Usage**:
  ```bash
  Bash: python3 {baseDir}/scripts/validate-references.py {file_path}
  ```
```

## Test File Requirements

**CRITICAL**: All scripts MUST have test files.

### Test File Naming Convention

**Pattern**: `test/cui-plugin-development-tools/{skill-name}/test-{script-name}.sh`

**Example**:
```
test/cui-plugin-development-tools/plugin-diagnose/
├── test-analyze-markdown-file.sh
├── test-analyze-tool-coverage.sh
├── test-analyze-skill-structure.sh
└── test-validate-references.sh
```

### Test File Structure

**Standard Structure**:
```bash
#!/bin/bash
# Test suite for script-name.sh
#
# Usage: ./test-script-name.sh

set -euo pipefail

# Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/.../scripts/script-name.sh"
FIXTURES_DIR="$SCRIPT_DIR/fixtures/script-name"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test functions
run_test() {
    local test_name="$1"
    # ... test logic
}

# Test cases
test_case_1() {
    run_test "Test case 1" ...
}

test_case_2() {
    run_test "Test case 2" ...
}

# Main
main() {
    echo "Test Suite: script-name.sh"

    test_case_1
    test_case_2
    # ... more tests

    # Summary
    echo "Tests: $TESTS_RUN, Passed: $TESTS_PASSED, Failed: $TESTS_FAILED"

    if [ $TESTS_FAILED -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

main
```

### Test Fixtures

**Location**: `test/{bundle}/{skill}/fixtures/{script-name}/`

**Purpose**: Test input files and expected outputs

**Example**:
```
test/cui-plugin-development-tools/plugin-diagnose/fixtures/
└── analyze-markdown-file/
    ├── valid-agent.md
    ├── bloated-command.md
    ├── missing-frontmatter.md
    └── invalid-yaml.md
```

### Running Tests

**Manual Execution**:
```bash
cd test/cui-plugin-development-tools/plugin-diagnose/
./test-analyze-markdown-file.sh
```

**Expected Output**:
```
========================================
Test Suite: analyze-markdown-file.sh
========================================

Test: Valid agent ... PASS
Test: Bloated command ... PASS
Test: Missing frontmatter ... PASS
Test: Invalid YAML ... PASS

========================================
Test Summary
========================================
Total tests:   4
Passed:        4
Failed:        0

✓ All tests passed!
```

## Help Output Requirements

**CRITICAL**: All scripts MUST support `--help` flag.

### Help Output Format

**Required Sections**:
1. **Usage**: Command syntax
2. **Description**: What the script does
3. **Parameters**: Input parameters with descriptions
4. **Output**: Output format
5. **Examples**: Usage examples

**Template**:
```bash
# In script:
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    cat <<EOF
Usage: $(basename "$0") <file_path> [component_type]

Description:
  Analyzes markdown file structure, frontmatter, and compliance.

Parameters:
  file_path       Path to markdown file to analyze
  component_type  Optional: agent|command|skill (default: auto-detect)

Output:
  JSON with structural analysis including:
  - file_path: Input file path
  - metrics: Line count, section count
  - frontmatter: Presence, validity, required fields
  - bloat: Classification (NORMAL, LARGE, BLOATED, CRITICAL)

Examples:
  # Analyze agent file:
  $(basename "$0") agents/my-agent.md agent

  # Auto-detect component type:
  $(basename "$0") commands/my-command.md

EOF
    exit 0
fi
```

### Help Output Validation

**Test**:
```bash
Bash: {baseDir}/scripts/script-name.sh --help
```

**Verify**:
- ✅ Prints usage information
- ✅ Exit code 0
- ✅ Output includes all required sections
- ✅ Examples are accurate

## Stdlib-Only Requirement

**CRITICAL**: Scripts MUST use only standard library (no external dependencies).

### Shell Scripts (bash)

**Allowed**:
- ✅ Standard Unix utilities (grep, sed, awk, find, cat, etc.)
- ✅ jq (widely available JSON processor) - documented exception
- ✅ Bash built-ins (if, for, while, functions, etc.)

**Prohibited**:
- ❌ External tools requiring installation (yq, xmllint, etc.)
- ❌ Language-specific tools (npm, pip, cargo) unless wrapper scripts

**Example** (stdlib-only):
```bash
#!/bin/bash
set -euo pipefail

FILE_PATH="${1:-}"

# ✅ Standard Unix utilities
LINE_COUNT=$(wc -l < "$FILE_PATH")
CONTENT=$(cat "$FILE_PATH")

# ✅ Bash built-ins and standard tools
if echo "$CONTENT" | grep -q "^---$"; then
    FRONTMATTER=$(awk '/^---$/{if(++count==2) exit; if(count==1) next} count==1' "$FILE_PATH")
fi

# ✅ jq for JSON output (documented exception)
echo "{\"line_count\": $LINE_COUNT}" | jq .
```

### Python Scripts

**Allowed**:
- ✅ Standard library modules (json, re, sys, os, pathlib, etc.)
- ✅ Built-in types and functions

**Prohibited**:
- ❌ pip packages (requests, pandas, numpy, etc.)
- ❌ Third-party libraries requiring installation

**Example** (stdlib-only):
```python
#!/usr/bin/env python3
"""Validates references in markdown files."""

import json
import re
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "File path required"}), file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    # ✅ Standard library only
    if not Path(file_path).is_file():
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ✅ Standard library regex
    references = re.findall(r'Skill:\s*([a-z0-9:-]+)', content)

    # ✅ Standard library JSON
    result = {"file_path": file_path, "references": references}
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

## JSON Output Format

**CRITICAL**: Scripts MUST output valid JSON (for machine parsing).

### Standard Format

**Success**:
```json
{
  "file_path": "input_file.md",
  "result_field_1": "value",
  "result_field_2": 123,
  "nested_object": {
    "field": "value"
  }
}
```

**Error**:
```json
{
  "error": "Clear error message"
}
```

### Output to stdout (Success) or stderr (Error)

**Success** (exit code 0):
```bash
echo '{
  "status": "success",
  "result": "data"
}' | jq .
exit 0
```

**Error** (exit code 1):
```bash
echo '{"error": "File not found"}' >&2
exit 1
```

## Executable Permissions

**CRITICAL**: Scripts MUST have executable permissions.

**Set Permissions**:
```bash
chmod +x {baseDir}/scripts/script-name.sh
chmod +x {baseDir}/scripts/script-name.py
```

**Verify**:
```bash
ls -l {baseDir}/scripts/
# Should show: -rwxr-xr-x (executable flag set)
```

**Shebang Required**:
```bash
#!/bin/bash              # Shell scripts
#!/usr/bin/env python3   # Python scripts
```

## Error Handling

**CRITICAL**: Scripts MUST handle errors gracefully.

### Input Validation

```bash
#!/bin/bash
set -euo pipefail

FILE_PATH="${1:-}"

# Validate parameter provided
if [ -z "$FILE_PATH" ]; then
    echo '{"error": "File path required"}' >&2
    exit 1
fi

# Validate file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\"}" >&2
    exit 1
fi

# Validate file readable
if [ ! -r "$FILE_PATH" ]; then
    echo "{\"error\": \"File not readable: $FILE_PATH\"}" >&2
    exit 1
fi
```

### Error Messages

**Format**: Clear, actionable error messages

**Good Examples**:
```json
{"error": "File not found: agents/missing.md"}
{"error": "Invalid component type. Expected: agent|command|skill, got: invalid"}
{"error": "JSON parsing failed at line 42: unexpected comma"}
```

**Bad Examples**:
```json
{"error": "Error"}  // Too vague
{"error": "Failed"}  // No context
{"error": "1"}  // Not descriptive
```

## Common Issues and Fixes

### Issue 1: Script Not Documented in SKILL.md

**Symptoms**:
- Script exists but not referenced in SKILL.md
- Users don't know script exists

**Diagnosis**:
```bash
# List scripts
ls {skill_dir}/scripts/

# Check SKILL.md references
Grep: pattern="scripts/", path="{skill_dir}/SKILL.md"
```

**Fix**:
Add script documentation to SKILL.md (see Documentation Requirements section).

### Issue 2: Missing Test File

**Symptoms**:
- No test file for script
- Untested script behavior

**Diagnosis**:
```bash
# Check for test file
ls test/{bundle}/{skill}/test-{script-name}.sh
```

**Fix**:
Create test file following Test File Structure template.

### Issue 3: No --help Support

**Symptoms**:
- Script fails with `--help` flag
- No usage documentation

**Diagnosis**:
```bash
Bash: {baseDir}/scripts/script-name.sh --help
# Should print help and exit 0
```

**Fix**:
Add help output handler (see Help Output Requirements section).

### Issue 4: External Dependencies

**Symptoms**:
- Script requires pip packages, npm modules, etc.
- Fails on systems without dependencies installed

**Diagnosis**:
```bash
# Shell scripts: Check for non-standard commands
grep -E "pip|npm|cargo|gem|composer" {script_path}

# Python scripts: Check for imports
grep -E "^import |^from .* import" {script_path}
# Verify all imports are stdlib
```

**Fix**:
Refactor to use stdlib-only (see Stdlib-Only Requirement section).

### Issue 5: Invalid JSON Output

**Symptoms**:
- JSON parsing fails
- Script output can't be processed

**Diagnosis**:
```bash
# Run script and validate JSON
{script_path} {args} | jq .
# If jq fails, JSON is invalid
```

**Fix**:
- Use `jq` for JSON generation in shell scripts
- Use `json.dumps()` in Python scripts
- Validate output with JSON parser

### Issue 6: Missing Executable Permissions

**Symptoms**:
- Script fails with "Permission denied"
- Cannot execute script

**Diagnosis**:
```bash
ls -l {script_path}
# Check for 'x' flag: -rwxr-xr-x
```

**Fix**:
```bash
chmod +x {script_path}
```

## Script Quality Checklist

**Before marking script as "quality approved"**:
- ✅ Documented in SKILL.md (purpose, input, output, usage)
- ✅ Test file exists and passes (`test-{script-name}.sh`)
- ✅ Supports `--help` flag (prints usage, exits 0)
- ✅ Stdlib-only (no external dependencies)
- ✅ JSON output format (valid, parseable)
- ✅ Executable permissions set (`chmod +x`)
- ✅ Error handling (validates inputs, graceful failures)
- ✅ Clear error messages (actionable, descriptive)
- ✅ Proper shebang (`#!/bin/bash` or `#!/usr/bin/env python3`)
- ✅ Exit codes (0 for success, 1 for error)

## Summary

**Scripts are**:
- Deterministic validation logic
- Stdlib-only (portable, no dependencies)
- JSON output (machine-readable)
- Documented in SKILL.md
- Tested with test files
- Executable with --help support

**Scripts complement AI agents**:
- Agents: Context interpretation, reasoning, user interaction
- Scripts: Pattern matching, parsing, calculation, validation

**Quality = Documentation + Tests + Standards**
