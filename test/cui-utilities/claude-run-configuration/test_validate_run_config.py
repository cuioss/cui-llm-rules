#!/usr/bin/env python3
"""Tests for validate-run-config.py script.

Migrated from test-validate-run-config.sh - tests run-configuration.json
format validation including required fields, types, and optional sections.
"""

import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-utilities', 'claude-run-configuration', 'validate-run-config.py')


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

        # Valid run-configuration.json
        (fixtures / 'run-configuration.json').write_text('''{
  "version": 1,
  "commands": {
    "test-cmd": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS"
      }
    }
  }
}''')

        # Invalid - missing version
        (fixtures / 'missing-version.json').write_text('''{
  "commands": {
    "test-cmd": {}
  }
}''')

        # Invalid - missing commands
        (fixtures / 'missing-commands.json').write_text('''{
  "version": 1
}''')

        # Invalid - wrong version type
        (fixtures / 'wrong-version-type.json').write_text('''{
  "version": "1",
  "commands": {}
}''')

        # Valid with maven section
        (fixtures / 'with-maven.json').write_text('''{
  "version": 1,
  "commands": {},
  "maven": {
    "build": {
      "last_execution": {
        "duration_ms": 45000
      }
    }
  }
}''')

        # Valid with agent_decisions section
        (fixtures / 'with-agent-decisions.json').write_text('''{
  "version": 1,
  "commands": {},
  "agent_decisions": {
    "test-agent": {
      "status": "keep-monolithic",
      "decision_date": "2025-11-25"
    }
  }
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

def test_valid_run_config():
    """Test validate valid run-configuration.json."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'run-configuration.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    assert data.get('valid') is True, "Valid config should be valid"


def test_missing_version():
    """Test detect missing version."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'missing-version.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    assert data.get('valid') is False, "Missing version should be invalid"


def test_missing_commands():
    """Test detect missing commands."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'missing-commands.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    assert data.get('valid') is False, "Missing commands should be invalid"


def test_wrong_version_type():
    """Test detect wrong version type."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'wrong-version-type.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    assert data.get('valid') is False, "Wrong version type should be invalid"


def test_with_maven():
    """Test validate with maven section."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'with-maven.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    assert data.get('valid') is True, "Config with maven section should be valid"


def test_with_agent_decisions():
    """Test validate with agent_decisions section."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'with-agent-decisions.json'))
    data = result.json()

    assert data.get('success') is True, "Should succeed"
    assert data.get('valid') is True, "Config with agent_decisions should be valid"


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
    result = run_script(SCRIPT_PATH, str(fixtures / 'run-configuration.json'))
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


def test_format_is_run_config():
    """Test format is run-config."""
    fixtures = get_fixtures_dir()
    result = run_script(SCRIPT_PATH, str(fixtures / 'run-configuration.json'))
    data = result.json()

    assert data.get('format') == 'run-config', "Format should be 'run-config'"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    setup_module()
    try:
        runner = TestRunner()
        runner.add_tests([
            test_valid_run_config,
            test_missing_version,
            test_missing_commands,
            test_wrong_version_type,
            test_with_maven,
            test_with_agent_decisions,
            test_invalid_json_syntax,
            test_checks_array,
            test_file_not_found,
            test_format_is_run_config,
        ])
        sys.exit(runner.run())
    finally:
        teardown_module()
