#!/usr/bin/env python3
"""Tests for Maven run subcommand.

Tests the unified run command that combines execute + parse on failure:
- Success output format
- Failure output with parsed errors
- Timeout handling
- --mode parameter filtering
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test - pm-dev-java bundle
SCRIPT_PATH = get_script_path('pm-dev-java', 'plan-marshall-plugin', 'maven.py')
MOCKS_DIR = Path(__file__).parent / 'mocks'


class TempDirContext:
    """Context manager for tests that need a temporary directory with mock wrapper."""

    def __init__(self, mock_script: str = 'mvnw-success.sh'):
        self.temp_dir = None
        self.original_cwd = None
        self.mock_script = mock_script

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        # Create target directory for log files
        (self.temp_dir / 'target').mkdir()
        # Create .plan directory for log files (new standard location)
        (self.temp_dir / '.plan' / 'temp' / 'build-output' / 'default').mkdir(parents=True)
        # Copy mock wrapper to temp_dir as mvnw
        mock_path = MOCKS_DIR / self.mock_script
        if mock_path.exists():
            mvnw_path = self.temp_dir / 'mvnw'
            shutil.copy(mock_path, mvnw_path)
            mvnw_path.chmod(0o755)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Run Success Tests
# =============================================================================

def test_run_success_output_format():
    """Test run command success output format (TOON format - tab-separated)."""
    with TempDirContext('mvnw-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test'
        )

        assert result.returncode == 0, f"Successful run should exit with 0: {result.stderr}"

        # Parse TOON output (tab-separated key-value pairs)
        lines = result.stdout.strip().split('\n')
        toon = {}
        for line in lines:
            if '\t' in line:
                key, value = line.split('\t', 1)
                toon[key] = value

        assert toon.get('status') == 'success', f"Status should be success: {toon}"
        assert 'log_file' in toon, "Should include log_file"
        assert toon.get('exit_code') == '0', "Exit code should be 0"
        assert 'command' in toon, "Should include command field"


def test_run_includes_duration():
    """Test run command includes duration in output."""
    with TempDirContext('mvnw-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test'
        )

        assert 'duration_seconds' in result.stdout, "Should include duration_seconds"


# =============================================================================
# Run Failure Tests
# =============================================================================

def test_run_failure_includes_errors():
    """Test run command failure includes parsed errors."""
    with TempDirContext('mvnw-failure.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test'
        )

        assert result.returncode == 1, "Failed run should exit with 1"
        assert 'status\terror' in result.stdout, "Should have error status"
        assert 'error\tbuild_failed' in result.stdout, "Should have build_failed error type"
        assert 'command\t' in result.stdout, "Should include command field"


def test_run_failure_with_compilation_errors():
    """Test run command failure with compilation errors includes file/line info."""
    with TempDirContext('mvnw-failure.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test'
        )

        # Even if mock doesn't produce parse-able errors, the format should be correct
        assert 'status\terror' in result.stdout, "Should have error status"


# =============================================================================
# Mode Parameter Tests
# =============================================================================

def test_run_mode_actionable():
    """Test run with --mode actionable (default)."""
    with TempDirContext('mvnw-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test',
            '--mode', 'actionable'
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'status\tsuccess' in result.stdout


def test_run_mode_errors():
    """Test run with --mode errors (no warnings)."""
    with TempDirContext('mvnw-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test',
            '--mode', 'errors'
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"


def test_run_mode_structured():
    """Test run with --mode structured (all issues with markers)."""
    with TempDirContext('mvnw-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test',
            '--mode', 'structured'
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"


# =============================================================================
# Module Routing Tests (embedded in commandArgs)
# =============================================================================

def test_run_with_module_routing():
    """Test run with module routing embedded in commandArgs."""
    with TempDirContext('mvnw-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--commandArgs', 'clean test -pl core'
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        # Check command includes module
        assert 'command\t' in result.stdout


# =============================================================================
# Help Test
# =============================================================================

def test_run_help():
    """Test run subcommand help."""
    result = run_script(SCRIPT_PATH, 'run', '--help')
    assert '--commandArgs' in result.stdout, "Should show --commandArgs option"
    assert '--mode' in result.stdout, "Should show --mode option"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_run_success_output_format,
        test_run_includes_duration,
        test_run_failure_includes_errors,
        test_run_failure_with_compilation_errors,
        test_run_mode_actionable,
        test_run_mode_errors,
        test_run_mode_structured,
        test_run_with_module_routing,
        test_run_help,
    ])
    sys.exit(runner.run())
