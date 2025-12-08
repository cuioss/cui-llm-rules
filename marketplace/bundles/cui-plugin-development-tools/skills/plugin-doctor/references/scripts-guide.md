# Script Validation Guide

Validation rules for plugin-doctor Workflow 5 (doctor-scripts) to ensure script compliance against plugin-script-architecture standards.

## Validation Categories

### 1. Subcommand Pattern Validation

**Standard**: Scripts MUST follow `{noun}.py {verb}` pattern using argparse subparsers.

**Check Criteria**:
1. Script name is `{noun}.py` (not `{verb}-{noun}.py`)
2. Script uses argparse subcommands (search for `subparsers = parser.add_subparsers`)
3. Help output shows available subcommands

**Detection**:
```python
# COMPLIANT: noun.py with subcommands
manage-files.py add --plan-id my-plan
maven.py execute --goals verify
analyze.py markdown --file input.md

# VIOLATION: verb-noun.py pattern
add-file.py --plan-id my-plan
execute-maven-build.py --goals verify
get-config.py --key foo
```

**Categorization**: Risky fix (requires script restructuring)

**Fix Strategy**: Flag for migration - script needs refactoring to subcommand pattern

### 2. Executor Pattern Validation

**Standard**: All script invocations MUST use `python3 .plan/execute-script.py {notation} {subcommand} {args}`.

**Check Criteria**:
1. Script usage examples use `python3 .plan/execute-script.py {notation} ...`
2. No direct script path usage (`python3 {path}/*.py ...`)
3. No path variable placeholders (`python3 {script_path} ...`)

**Detection in SKILL.md files**:
```markdown
# COMPLIANT
python3 .plan/execute-script.py planning:manage-files:manage-files add --plan-id my-plan
python3 .plan/execute-script.py builder:builder-maven-rules:maven execute --goals verify

# VIOLATION (direct path)
python3 /path/to/marketplace/.../manage-files.py add --plan-id my-plan
python3 marketplace/bundles/planning/skills/manage-files/scripts/manage-files.py add

# VIOLATION (path variable)
python3 {manage_files_path} add --plan-id my-plan
Bash: scripts/script-name.sh {args}
```

**Categorization**: Safe fix (pattern replacement)

**Fix Strategy**: Auto-correct to executor pattern using notation

### 3. Stdlib-Only Validation

**Standard**: Scripts MUST use only Python standard library (no pip dependencies).

**Check Criteria**:
1. Script imports only allowed stdlib modules
2. No `import yaml`, `import requests`, etc.
3. No pip dependencies in any form

**Allowed Modules** (per `plugin-script-architecture:references/stdlib-modules.md`):
- `json`, `argparse`, `pathlib`, `re`, `sys`, `os`
- `datetime`, `shutil`, `subprocess`, `tempfile`, `textwrap`
- `collections`, `typing`, `dataclasses`, `functools`, `itertools`
- `contextlib`, `io`, `hashlib`, `base64`, `urllib.parse`, `difflib`
- `unittest`, `time`, `copy`, `logging`, `string`, `enum`, `uuid`
- `glob`, `fnmatch`

**Prohibited Imports**:
```python
# VIOLATIONS
import yaml          # Use custom simple YAML parser
import requests      # Use urllib
import numpy         # Not needed for scripts
import pandas        # Not needed for scripts
from toml import *   # External package (Python < 3.11)
```

**Categorization**: Risky fix (requires code refactoring)

**Fix Strategy**: Flag for manual review - suggest stdlib alternatives

### 4. TOON Output Validation

**Standard**: Scripts SHOULD output TOON format (tab-separated, header row pattern).

**Check Criteria**:
1. Script outputs TOON format (default) or JSON (complex nested only)
2. Errors go to stderr
3. Exit codes: 0 for success, 1 for error

**TOON Format**:
```toon
status: success
count: 3

items[3]{id,name,status}:
TASK-001	Implement feature	in_progress
TASK-002	Write tests	pending
TASK-003	Update docs	pending
```

**JSON Acceptable When**:
- Complex nested structures (>3 levels deep)
- Non-uniform object shapes
- API interchange with external tools

**Categorization**: Risky fix (output format change)

**Fix Strategy**: Flag for migration - document TOON conversion needed

### 5. Test Coverage Validation

**Standard**: All scripts MUST have corresponding test files.

**Check Criteria**:
1. Test file exists: `test/{bundle}/{skill}/test_{script}.py`
2. Test file contains at least one `assert` statement
3. Tests cover: happy path, missing input, invalid input, edge cases

**Detection**:
```bash
# For script: marketplace/bundles/planning/skills/manage-files/scripts/manage-files.py
# Expected test: test/planning/manage-files/test_manage_files.py
```

**Categorization**: Safe fix (flag for test creation)

**Fix Strategy**: Report missing tests, suggest test template

### 6. Help Output Validation

**Standard**: All scripts MUST support `--help` flag via argparse.

**Check Criteria**:
1. Running `python3 .plan/execute-script.py {notation} --help` exits with code 0
2. Help output includes: usage, description, parameters, examples
3. Subcommand help also available

**Detection**:
```bash
python3 .plan/execute-script.py {bundle}:{skill} --help
python3 .plan/execute-script.py {bundle}:{skill} {subcommand} --help
```

**Categorization**: Safe fix (add argparse help)

**Fix Strategy**: Flag missing help - argparse provides automatic help

## Validation Workflow

### Step 1: Discover Scripts

```bash
Glob: pattern="scripts/*.py", path="marketplace/bundles/*/skills/*"
```

### Step 2: For Each Script, Check

1. **Naming**: Is it `{noun}.py` pattern?
2. **Structure**: Does it use argparse subcommands?
3. **Imports**: Are all imports stdlib-only?
4. **Output**: Does it use TOON/JSON format?
5. **Tests**: Does test file exist?
6. **Help**: Does `--help` work?

### Step 3: For Each SKILL.md, Check

1. **Documentation**: Are scripts documented?
2. **Invocation**: Do examples use executor pattern?

### Step 4: Categorize Issues

| Issue Type | Category | Auto-Fix |
|------------|----------|----------|
| Wrong naming pattern | Risky | No |
| Missing subcommands | Risky | No |
| Direct path invocation | Safe | Yes |
| External imports | Risky | No |
| JSON instead of TOON | Risky | No |
| Missing tests | Safe | No |
| Missing help | Safe | No |

### Step 5: Report

```toon
status: {success|issues_found}
scripts_checked: {count}
issues_found: {count}

issues[N]{script,issue_type,severity,auto_fixable}:
manage-files.py	missing_tests	medium	no
execute-build.py	wrong_naming	high	no
...
```

## Related Standards

- `cui-plugin-development-tools:plugin-script-architecture` - Full script development standards
- `plugin-script-architecture:standards/python-implementation.md` - Python patterns
- `plugin-script-architecture:standards/testing-standards.md` - Test requirements
- `plugin-script-architecture:standards/output-contract.md` - TOON/JSON output
