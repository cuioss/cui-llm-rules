#!/usr/bin/env python3
"""Tests for validate-memory.py script.

Migrated from test-validate-memory.sh - tests memory file format validation
including required fields, categories, and JSON syntax.
"""

import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('general-tools', 'manage-memories', 'validate-memory.py')


# =============================================================================
# Test Helpers
# =============================================================================

class FixturesContext:
    """Context manager for tests that need temporary fixtures."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self._setup_fixtures()
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _setup_fixtures(self):
        """Create test fixtures."""
        fixtures = self.temp_dir

        # Create memory directory structure
        memory_dir = fixtures / '.claude' / 'memory' / 'context'
        memory_dir.mkdir(parents=True)

        # Valid memory file
        (memory_dir / 'test-memory.json').write_text('''{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "context",
    "summary": "test-feature"
  },
  "content": {
    "decisions": ["Use JWT"]
  }
}''')

        # Invalid memory file (missing meta)
        (fixtures / 'invalid-memory.json').write_text('''{
  "content": {
    "test": true
  }
}''')

        # Invalid memory file (missing content)
        (fixtures / 'missing-content.json').write_text('''{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "context",
    "summary": "test"
  }
}''')

        # Invalid memory file (invalid category)
        (fixtures / 'invalid-category.json').write_text('''{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "invalid",
    "summary": "test"
  },
  "content": {}
}''')

        # Invalid JSON syntax
        (fixtures / 'invalid-json.json').write_text('''{
  "broken": true,
  missing-quotes: "value"
}''')


# Shared fixtures context
_fixtures = None


def setup_module():
    """Setup fixtures before running tests."""
    global _fixtures
    _fixtures = FixturesContext()
    _fixtures.__enter__()


def teardown_module():
    """Cleanup fixtures after tests."""
    global _fixtures
    if _fixtures:
        _fixtures.__exit__(None, None, None)


def get_fixtures_dir():
    """Get the fixtures directory."""
    return _fixtures.temp_dir


# =============================================================================
# Tests
# =============================================================================

def test_valid_memory():
    """Test validate valid memory file."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        str(fixtures / '.claude' / 'memory' / 'context' / 'test-memory.json')
    )
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    assert data.get('valid') is True, "Valid memory file should be valid"


def test_invalid_memory_no_meta():
    """Test detect invalid memory file (missing meta)."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'invalid-memory.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed (validation ran)"
    assert data.get('valid') is False, "Missing meta should be invalid"


def test_invalid_memory_no_content():
    """Test detect invalid memory file (missing content)."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'missing-content.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed (validation ran)"
    assert data.get('valid') is False, "Missing content should be invalid"


def test_invalid_category():
    """Test detect invalid category."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'invalid-category.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed (validation ran)"
    assert data.get('valid') is False, "Invalid category should be invalid"


def test_invalid_json_syntax():
    """Test detect invalid JSON syntax."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'invalid-json.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed (validation ran)"
    assert data.get('valid') is False, "Invalid JSON should be invalid"


def test_checks_array():
    """Test output includes checks array."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        str(fixtures / '.claude' / 'memory' / 'context' / 'test-memory.json')
    )
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    checks = data.get('checks', [])
    assert len(checks) > 0, "Should include checks array with items"


def test_file_not_found():
    """Test file not found returns error."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'nonexistent.json'))
    # Script may output to stderr for errors
    data = result.json_or_error()

    assert data.get('success') is False, "Should fail for non-existent file"


def test_format_is_memory():
    """Test format is memory."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        str(fixtures / '.claude' / 'memory' / 'context' / 'test-memory.json')
    )
    data = result.json()

    assert data.get('format') == 'memory', "Format should be 'memory'"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    setup_module()
    try:
        runner = TestRunner()
        runner.add_tests([
            test_valid_memory,
            test_invalid_memory_no_meta,
            test_invalid_memory_no_content,
            test_invalid_category,
            test_invalid_json_syntax,
            test_checks_array,
            test_file_not_found,
            test_format_is_memory,
        ])
        sys.exit(runner.run())
    finally:
        teardown_module()
