#!/usr/bin/env python3
"""Tests for run_config.py script.

Consolidated from:
- test_init_run_config.py → init subcommand tests
- test_validate_run_config.py → validate subcommand tests

Tests run-configuration.json initialization and validation.
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'run-config', 'run_config.py')


# =============================================================================
# Test Helpers
# =============================================================================

class TempDirContext:
    """Context manager for tests that need a fresh temp directory."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Init Subcommand Tests
# =============================================================================

def test_init_create_new_config():
    """Test init creates new run-configuration.json."""
    with TempDirContext() as temp_dir:
        result = run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('action') == 'created', "Action should be 'created'"

        # Verify file exists (uses .plan)
        config_file = temp_dir / '.plan' / 'run-configuration.json'
        assert config_file.exists(), "Config file should be created"


def test_init_skip_existing():
    """Test init skips if file already exists."""
    with TempDirContext() as temp_dir:
        # Create existing file
        plan_dir = temp_dir / '.plan'
        plan_dir.mkdir(parents=True)
        (plan_dir / 'run-configuration.json').write_text('{"version": 1, "commands": {}}')

        result = run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('action') == 'skipped', "Action should be 'skipped'"


def test_init_force_overwrite():
    """Test init with --force overwrites existing file."""
    with TempDirContext() as temp_dir:
        import json
        # Create existing file with old content
        plan_dir = temp_dir / '.plan'
        plan_dir.mkdir(parents=True)
        (plan_dir / 'run-configuration.json').write_text('{"version": 1, "commands": {"old": {}}}')

        result = run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir), '--force')
        data = result.json()

        assert data.get('success') is True, "Should succeed"

        # Verify old command entry is gone
        content = json.loads((plan_dir / 'run-configuration.json').read_text())
        assert 'old' not in content.get('commands', {}), "Old command should be removed"


def test_init_correct_structure():
    """Test init creates file with correct structure."""
    with TempDirContext() as temp_dir:
        import json
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        config_file = temp_dir / '.plan' / 'run-configuration.json'
        content = json.loads(config_file.read_text())

        # Check version
        assert content.get('version') == 1, "Version should be 1"

        # Check commands is empty object
        assert content.get('commands') == {}, "Commands should be empty object"

        # Check maven section with acceptable_warnings
        maven = content.get('maven', {})
        aw = maven.get('acceptable_warnings', {})
        assert 'transitive_dependency' in aw, "Should have transitive_dependency category"
        assert 'plugin_compatibility' in aw, "Should have plugin_compatibility category"
        assert 'platform_specific' in aw, "Should have platform_specific category"


def test_init_creates_plan_dir():
    """Test init creates .plan directory if needed."""
    with TempDirContext() as temp_dir:
        # Ensure .plan doesn't exist
        plan_dir = temp_dir / '.plan'
        if plan_dir.exists():
            shutil.rmtree(plan_dir)

        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        assert plan_dir.exists(), ".plan directory should be created"
        assert (plan_dir / 'run-configuration.json').exists(), "Config file should be created"


def test_init_output_includes_path():
    """Test init output includes path."""
    with TempDirContext() as temp_dir:
        result = run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))
        data = result.json()

        assert 'path' in data, "Output should include path field"


def test_init_output_includes_structure():
    """Test init output includes structure when created."""
    with TempDirContext() as temp_dir:
        result = run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))
        data = result.json()

        assert data.get('action') == 'created', "Should be created"
        assert 'structure' in data, "Output should include structure field"


def test_init_default_project_dir():
    """Test init default project dir is current directory."""
    with TempDirContext() as temp_dir:
        # Run from temp_dir
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            proc = subprocess.run(
                ['python3', str(SCRIPT_PATH), 'init'],
                capture_output=True,
                text=True
            )
        finally:
            os.chdir(old_cwd)

        config_file = temp_dir / '.plan' / 'run-configuration.json'
        assert config_file.exists(), "Config file should be created in current directory"


# =============================================================================
# Validate Subcommand Tests
# =============================================================================

def test_validate_valid_run_config():
    """Test validate valid run-configuration.json."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'run-configuration.json').write_text('''{
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

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'run-configuration.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('valid') is True, "Valid config should be valid"


def test_validate_missing_version():
    """Test validate detects missing version."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'missing-version.json').write_text('''{
  "commands": {
    "test-cmd": {}
  }
}''')

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'missing-version.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('valid') is False, "Missing version should be invalid"


def test_validate_missing_commands():
    """Test validate detects missing commands."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'missing-commands.json').write_text('''{
  "version": 1
}''')

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'missing-commands.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('valid') is False, "Missing commands should be invalid"


def test_validate_wrong_version_type():
    """Test validate detects wrong version type."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'wrong-version-type.json').write_text('''{
  "version": "1",
  "commands": {}
}''')

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'wrong-version-type.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('valid') is False, "Wrong version type should be invalid"


def test_validate_with_maven():
    """Test validate with maven section."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'with-maven.json').write_text('''{
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

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'with-maven.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('valid') is True, "Config with maven section should be valid"


def test_validate_with_agent_decisions():
    """Test validate with agent_decisions section."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'with-agent-decisions.json').write_text('''{
  "version": 1,
  "commands": {},
  "agent_decisions": {
    "test-agent": {
      "status": "keep-monolithic",
      "decision_date": "2025-11-25"
    }
  }
}''')

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'with-agent-decisions.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('valid') is True, "Config with agent_decisions should be valid"


def test_validate_invalid_json_syntax():
    """Test validate detects invalid JSON syntax."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'invalid-json.json').write_text('''{
  "broken": true,
  missing-quotes: "value"
}''')

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'invalid-json.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed (validation ran)"
        assert data.get('valid') is False, "Invalid JSON should be invalid"


def test_validate_checks_array():
    """Test validate output includes checks array."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'run-configuration.json').write_text('''{
  "version": 1,
  "commands": {}
}''')

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'run-configuration.json'))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        checks = data.get('checks', [])
        assert len(checks) > 0, "Should include checks array with items"


def test_validate_file_not_found():
    """Test validate file not found returns error."""
    with TempDirContext() as temp_dir:
        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'nonexistent.json'))
        # Script may output to stderr for errors
        data = result.json_or_error()

        assert data.get('success') is False, "Should fail for non-existent file"


def test_validate_format_is_run_config():
    """Test validate format is run-config."""
    with TempDirContext() as temp_dir:
        (temp_dir / 'run-configuration.json').write_text('''{
  "version": 1,
  "commands": {}
}''')

        result = run_script(SCRIPT_PATH, 'validate', '--file', str(temp_dir / 'run-configuration.json'))
        data = result.json()

        assert data.get('format') == 'run-config', "Format should be 'run-config'"


# =============================================================================
# Timeout Subcommand Tests
# =============================================================================

def parse_toon(output: str) -> dict:
    """Parse TOON output into dict."""
    result = {}
    for line in output.strip().split('\n'):
        if '\t' in line:
            key, value = line.split('\t', 1)
            result[key.strip()] = value.strip()
    return result


def test_timeout_get_default_when_no_persisted():
    """Test timeout get returns default when no persisted value."""
    with TempDirContext() as temp_dir:
        # Create .plan directory
        (temp_dir / '.plan').mkdir(parents=True)

        result = run_script(SCRIPT_PATH, 'timeout', 'get',
                          '--command', 'ci:pr_checks',
                          '--default', '300',
                          '--project-dir', str(temp_dir))

        assert result.success, f"Should succeed: {result.stderr}"
        # Plain number output
        assert result.stdout.strip() == '300'


def test_timeout_get_with_safety_margin():
    """Test timeout get applies safety margin to persisted value."""
    import json
    with TempDirContext() as temp_dir:
        plan_dir = temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        # Create config with persisted timeout
        config = {
            "version": 1,
            "commands": {
                "ci:pr_checks": {
                    "timeout_seconds": 240
                }
            }
        }
        (plan_dir / 'run-configuration.json').write_text(json.dumps(config))

        result = run_script(SCRIPT_PATH, 'timeout', 'get',
                          '--command', 'ci:pr_checks',
                          '--default', '300',
                          '--project-dir', str(temp_dir))

        assert result.success, f"Should succeed: {result.stderr}"
        # 240 * 1.25 = 300 (plain number output)
        assert result.stdout.strip() == '300'


def test_timeout_set_initial_value():
    """Test timeout set writes directly when no existing value."""
    import json
    with TempDirContext() as temp_dir:
        plan_dir = temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        result = run_script(SCRIPT_PATH, 'timeout', 'set',
                          '--command', 'ci:pr_checks',
                          '--duration', '180',
                          '--project-dir', str(temp_dir))

        assert result.success, f"Should succeed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data.get('status') == 'success'
        assert data.get('timeout_seconds') == '180'
        assert data.get('source') == 'initial'

        # Verify file was written
        config = json.loads((plan_dir / 'run-configuration.json').read_text())
        assert config['commands']['ci:pr_checks']['timeout_seconds'] == 180


def test_timeout_set_weighted_update():
    """Test timeout set computes weighted value when existing."""
    import json
    with TempDirContext() as temp_dir:
        plan_dir = temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        # Create config with existing timeout
        config = {
            "version": 1,
            "commands": {
                "ci:pr_checks": {
                    "timeout_seconds": 240
                }
            }
        }
        (plan_dir / 'run-configuration.json').write_text(json.dumps(config))

        result = run_script(SCRIPT_PATH, 'timeout', 'set',
                          '--command', 'ci:pr_checks',
                          '--duration', '180',
                          '--project-dir', str(temp_dir))

        assert result.success, f"Should succeed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data.get('status') == 'success'
        # 0.8 * 240 + 0.2 * 180 = 192 + 36 = 228
        assert data.get('timeout_seconds') == '228'
        assert data.get('previous_seconds') == '240'
        assert data.get('source') == 'computed'


def test_timeout_set_weighted_favors_higher():
    """Test timeout set weighted calculation favors higher value regardless of order."""
    import json
    with TempDirContext() as temp_dir:
        plan_dir = temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        # Create config with lower existing timeout
        config = {
            "version": 1,
            "commands": {
                "ci:pr_checks": {
                    "timeout_seconds": 180
                }
            }
        }
        (plan_dir / 'run-configuration.json').write_text(json.dumps(config))

        # Set higher duration
        result = run_script(SCRIPT_PATH, 'timeout', 'set',
                          '--command', 'ci:pr_checks',
                          '--duration', '240',
                          '--project-dir', str(temp_dir))

        assert result.success, f"Should succeed: {result.stderr}"
        data = parse_toon(result.stdout)
        # Higher=240, Lower=180: 0.8 * 240 + 0.2 * 180 = 228
        assert data.get('timeout_seconds') == '228'


def test_timeout_set_same_value():
    """Test timeout set with same value returns same value."""
    import json
    with TempDirContext() as temp_dir:
        plan_dir = temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        config = {
            "version": 1,
            "commands": {
                "ci:pr_checks": {
                    "timeout_seconds": 300
                }
            }
        }
        (plan_dir / 'run-configuration.json').write_text(json.dumps(config))

        result = run_script(SCRIPT_PATH, 'timeout', 'set',
                          '--command', 'ci:pr_checks',
                          '--duration', '300',
                          '--project-dir', str(temp_dir))

        assert result.success, f"Should succeed: {result.stderr}"
        data = parse_toon(result.stdout)
        # 0.8 * 300 + 0.2 * 300 = 300
        assert data.get('timeout_seconds') == '300'


def test_timeout_help():
    """Test timeout subcommand shows help."""
    result = run_script(SCRIPT_PATH, 'timeout', '--help')
    assert result.success, f"Should succeed: {result.stderr}"
    assert 'get' in result.stdout
    assert 'set' in result.stdout


def test_timeout_get_help():
    """Test timeout get subcommand shows help."""
    result = run_script(SCRIPT_PATH, 'timeout', 'get', '--help')
    assert result.success, f"Should succeed: {result.stderr}"
    assert '--command' in result.stdout
    assert '--default' in result.stdout


def test_timeout_set_help():
    """Test timeout set subcommand shows help."""
    result = run_script(SCRIPT_PATH, 'timeout', 'set', '--help')
    assert result.success, f"Should succeed: {result.stderr}"
    assert '--command' in result.stdout
    assert '--duration' in result.stdout


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Init subcommand tests
        test_init_create_new_config,
        test_init_skip_existing,
        test_init_force_overwrite,
        test_init_correct_structure,
        test_init_creates_plan_dir,
        test_init_output_includes_path,
        test_init_output_includes_structure,
        test_init_default_project_dir,
        # Validate subcommand tests
        test_validate_valid_run_config,
        test_validate_missing_version,
        test_validate_missing_commands,
        test_validate_wrong_version_type,
        test_validate_with_maven,
        test_validate_with_agent_decisions,
        test_validate_invalid_json_syntax,
        test_validate_checks_array,
        test_validate_file_not_found,
        test_validate_format_is_run_config,
        # Timeout subcommand tests
        test_timeout_get_default_when_no_persisted,
        test_timeout_get_with_safety_margin,
        test_timeout_set_initial_value,
        test_timeout_set_weighted_update,
        test_timeout_set_weighted_favors_higher,
        test_timeout_set_same_value,
        test_timeout_help,
        test_timeout_get_help,
        test_timeout_set_help,
    ])
    sys.exit(runner.run())
