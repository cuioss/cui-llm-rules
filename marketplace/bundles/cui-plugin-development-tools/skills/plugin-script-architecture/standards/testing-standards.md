# Testing Standards

Standards for testing Python scripts in the marketplace. Tests use **Python stdlib only** - no external frameworks required.

## Quick Start

```bash
python3 test/run-tests.py                                          # all tests
python3 test/run-tests.py test/planning/                           # directory
python3 test/run-tests.py test/planning/plan-files/test_parse_plan.py  # single file
```

## Directory Structure

```
test/
  conftest.py                    # Shared infrastructure (import this)

  {bundle-name}/                 # Matches marketplace bundle
    {skill-name}/                # Matches skill directory
      test_{script-name}.py      # Tests for scripts/{script-name}.py
      fixtures/                  # Optional fixture files
        sample-input.md
```

## Writing Tests

### Option 1: Functional Style (Recommended for simple scripts)

```python
#!/usr/bin/env python3
"""Tests for parse-plan.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_file, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('planning', 'plan-files', 'parse-plan.py')

# Test fixtures (inline for simple cases)
BASIC_PLAN = """# Task Plan: Test Feature

**Current Phase**: init
**Current Task**: task-1
"""

def test_parse_basic_plan():
    """Test parsing a basic plan."""
    temp_file = create_temp_file(BASIC_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()
        assert data['title'] == 'Test Feature'
        assert data['current_phase'] == 'init'
    finally:
        temp_file.unlink()

def test_file_not_found():
    """Test error handling for missing file."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path.md')
    assert not result.success
    data = result.json_or_error()
    assert 'error' in data

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_basic_plan,
        test_file_not_found,
    ])
    sys.exit(runner.run())
```

### Option 2: Class-Based Style (For complex scripts with setup/teardown)

```python
#!/usr/bin/env python3
"""Tests for manage-adr.py script."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import ScriptTestCase

class TestManageAdr(ScriptTestCase):
    """Test ADR management script."""

    bundle = 'cui-documentation-standards'
    skill = 'adr-management'
    script = 'manage-adr.py'

    def test_create_adr(self):
        """Test creating a new ADR."""
        result = self.run_script('create', '--title', 'Use PostgreSQL')
        self.assert_success(result)
        data = result.json()
        self.assertEqual(data['number'], 1)
        self.assertIn('001-Use_PostgreSQL.adoc', data['path'])

    def test_list_empty(self):
        """Test listing ADRs when none exist."""
        result = self.run_script('list')
        self.assert_success(result)
        data = result.json()
        self.assertEqual(data['count'], 0)

if __name__ == '__main__':
    unittest.main()
```

## Required Test Categories

**CRITICAL**: Every script MUST have tests for these categories:

### 1. Happy Path
Normal successful execution.

```python
def test_basic_success():
    """Happy path - normal operation."""
    result = run_script(SCRIPT_PATH, '--mode', 'structured')
    assert result.success
    data = result.json()
    assert data['status'] == 'success'
```

### 2. Missing Input
Required file/argument not provided.

```python
def test_file_not_found():
    """Missing input - file doesn't exist."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path.md')
    assert not result.success
    data = result.json_or_error()
    assert 'error' in data
```

### 3. Invalid Input
Malformed input data.

```python
def test_invalid_format():
    """Invalid input - malformed content."""
    temp_file = create_temp_file("not valid yaml: {{{")
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert not result.success
    finally:
        temp_file.unlink()
```

### 4. Edge Cases
Empty input, boundary values.

```python
def test_empty_input():
    """Edge case - empty file."""
    temp_file = create_temp_file("")
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        # Verify appropriate handling
        assert result.success or 'error' in result.json_or_error()
    finally:
        temp_file.unlink()
```

## Assertion Requirements

**CRITICAL**: Every test function MUST contain at least one `assert` statement.

Tests without assertions provide no verification value.

### Common Assertion Patterns

```python
# Verify exit code 0
assert result.success

# Explicit exit code check
assert result.returncode == 0

# Verify output content
assert 'expected' in result.stdout

# Verify parsed data
assert data['field'] == expected_value

# Verify expected failure
assert not result.success
```

### Anti-patterns to Avoid

```python
# BAD: Test only calls function without assertions
def test_no_assertion():
    result = run_script(SCRIPT_PATH, 'arg')
    result.json()  # No assertion!

# BAD: Assigns to variable but never asserts
def test_assigns_only():
    result = run_script(SCRIPT_PATH, 'arg')
    data = result.json()
    status = data['status']  # No assertion on status!

# BAD: Checks parsing without verifying content
def test_parses_only():
    result = run_script(SCRIPT_PATH, 'arg')
    result.json()  # Just checks it parses, not content!
```

## Test Fixtures

**Location**: `test/{bundle}/{skill}/fixtures/`

**Purpose**: Test input files and expected outputs

```
test/cui-plugin-development-tools/plugin-diagnose/fixtures/
└── analyze-markdown-file/
    ├── valid-agent.md
    ├── bloated-command.md
    ├── missing-frontmatter.md
    └── invalid-yaml.md
```

### Using Fixtures

```python
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / 'fixtures'

def test_with_fixture_file():
    fixture_path = FIXTURES_DIR / 'sample-maven-success.log'
    result = run_script(SCRIPT_PATH, '--log', str(fixture_path))
    assert result.success
```

## Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Test file | `test_{script_name}.py` | `test_parse_plan.py` |
| Test function | `test_{what_it_tests}` | `test_parse_basic_plan` |
| Test class | `Test{ScriptName}` | `TestParseConfig` |
| Fixture file | `sample-{description}.{ext}` | `sample-maven-success.log` |

## API Reference

### `conftest.run_script(script_path, *args, input_data=None, cwd=None, timeout=30)`

Run a Python script and capture output.

**Returns**: `ScriptResult` with:
- `.returncode` - Exit code
- `.stdout` - Standard output
- `.stderr` - Standard error
- `.success` - True if returncode == 0
- `.json()` - Parse stdout as JSON
- `.json_or_error()` - Parse stdout or stderr as JSON

### `conftest.get_script_path(bundle, skill, script)`

Get absolute path to a marketplace script.

**Example**:
```python
path = get_script_path('planning', 'plan-files', 'parse-plan.py')
# Returns: /path/to/marketplace/bundles/planning/skills/plan-files/scripts/parse-plan.py
```

### `conftest.create_temp_file(content, suffix='.md', dir=None)`

Create a temporary file with content. Caller must delete.

### `conftest.ScriptTestCase`

Base class for unittest-style tests with automatic cleanup.

**Class attributes**:
- `bundle` - Bundle name
- `skill` - Skill name
- `script` - Script filename

**Methods**:
- `run_script(*args)` - Run the configured script
- `run_script_with_file(content, *args)` - Create temp file and run
- `assert_success(result)` - Assert returncode == 0
- `assert_failure(result)` - Assert returncode != 0

### `conftest.TestRunner`

Simple test runner for functional-style tests.

```python
runner = TestRunner()
runner.add_tests([test_a, test_b, test_c])
sys.exit(runner.run())
```

## Test Quality Checklist

Before marking tests as complete:

- [ ] Test file exists: `test/{bundle}/{skill}/test_{script}.py`
- [ ] Happy path test with assertions
- [ ] Missing input test with assertions
- [ ] Invalid input test with assertions
- [ ] Edge case tests with assertions
- [ ] All tests have at least one `assert` statement
- [ ] Fixtures are in `fixtures/` directory
- [ ] Tests pass: `python3 test/run-tests.py test/{bundle}/{skill}/`
