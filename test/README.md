# Test Framework

This directory contains tests for Python scripts in the marketplace bundles. Tests use **Python stdlib only** - no external frameworks required.

## Quick Start

```bash
# Run a single test file
python3 test/cui-task-workflow/plan-files/test_parse_plan.py

# Run all tests in a directory
for f in test/cui-task-workflow/plan-files/test_*.py; do python3 "$f"; done
```

## Directory Structure

```
test/
  conftest.py                    # Shared infrastructure (import this)
  README.md                      # This file

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
SCRIPT_PATH = get_script_path('cui-task-workflow', 'plan-files', 'parse-plan.py')

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

## Test Patterns

### 1. Success Case

```python
def test_successful_operation():
    result = run_script(SCRIPT_PATH, '--mode', 'structured')
    assert result.success
    data = result.json()
    assert data['status'] == 'success'
```

### 2. Error Case

```python
def test_missing_required_arg():
    result = run_script(SCRIPT_PATH)  # Missing required arg
    assert not result.success
    assert result.returncode != 0
```

### 3. File Input

```python
def test_with_file_input():
    content = "# Test Content"
    temp_file = create_temp_file(content)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
    finally:
        temp_file.unlink()
```

### 4. JSON Validation

```python
def test_json_structure():
    result = run_script(SCRIPT_PATH, '--mode', 'json')
    data = result.json()

    # Check required fields
    assert 'status' in data
    assert 'data' in data

    # Check nested structure
    assert 'items' in data['data']
    assert isinstance(data['data']['items'], list)
```

### 5. Using Fixtures Directory

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

## Test Categories

### Required Tests Per Script

Every script should have tests for:

1. **Happy path** - Normal successful execution
2. **Missing input** - Required file/argument not provided
3. **Invalid input** - Malformed input data
4. **Edge cases** - Empty input, boundary values

### Example Coverage

```python
# Required test categories
def test_basic_success():
    """Happy path - normal operation."""
    pass

def test_file_not_found():
    """Missing input - file doesn't exist."""
    pass

def test_invalid_format():
    """Invalid input - malformed content."""
    pass

def test_empty_input():
    """Edge case - empty file."""
    pass
```

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
path = get_script_path('cui-task-workflow', 'plan-files', 'parse-plan.py')
# Returns: /path/to/marketplace/bundles/cui-task-workflow/skills/plan-files/scripts/parse-plan.py
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

## Migration from Shell Tests

See [plan/python-test/shell-migration-plan.md](../plan/python-test/shell-migration-plan.md) for detailed migration guide.

### Quick Reference

| Shell Pattern | Python Equivalent |
|---------------|-------------------|
| `output=$(python3 "$SCRIPT")` | `result = run_script(SCRIPT_PATH)` |
| `echo "$output" \| jq '.status'` | `result.json()['status']` |
| `[ "$?" -eq 0 ]` | `result.success` |
| `mktemp` | `create_temp_file(content)` |
| `$FIXTURES_DIR/file.log` | `FIXTURES_DIR / 'file.log'` |
