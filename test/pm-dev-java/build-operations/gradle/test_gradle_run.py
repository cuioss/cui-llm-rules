#!/usr/bin/env python3
"""Tests for Gradle run subcommand.

Tests the unified run command that combines execute + parse on failure:
- Success output format
- Failure output with parsed errors
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
SCRIPT_PATH = get_script_path('pm-dev-java', 'plan-marshall-plugin', 'gradle.py')
MOCKS_DIR = Path(__file__).parent / 'mocks'


class TempDirContext:
    """Context manager for tests that need a temporary directory."""

    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        # Create build directory for log files
        (self.temp_dir / 'build').mkdir()
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Run Success Tests
# =============================================================================

def test_run_success_output_format():
    """Test run command success output format (TOON format)."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'clean test',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )

        assert result.returncode == 0, f"Successful run should exit with 0: {result.stderr}"

        # Parse TOON output
        lines = result.stdout.strip().split('\n')
        toon = {}
        for line in lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                toon[key] = value

        assert toon.get('status') == 'success', f"Status should be success: {toon}"
        assert 'log_file' in toon, "Should include log_file"
        assert toon.get('exit_code') == '0', "Exit code should be 0"


def test_run_includes_duration():
    """Test run command includes duration in output."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'clean test',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )

        assert 'duration_seconds' in result.stdout, "Should include duration_seconds"


# =============================================================================
# Run Failure Tests
# =============================================================================

def test_run_failure_includes_errors():
    """Test run command failure includes error status."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'clean test',
            '--gradlew', str(MOCKS_DIR / 'gradlew-failure.sh')
        )

        assert result.returncode == 1, "Failed run should exit with 1"
        assert 'status: error' in result.stdout, "Should have error status"


# =============================================================================
# Mode Parameter Tests
# =============================================================================

def test_run_mode_actionable():
    """Test run with --mode actionable (default)."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'clean test',
            '--mode', 'actionable',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'status: success' in result.stdout


def test_run_mode_errors():
    """Test run with --mode errors (no warnings)."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'clean test',
            '--mode', 'errors',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"


# =============================================================================
# Project Parameter Tests
# =============================================================================

def test_run_with_project():
    """Test run with --project parameter."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'clean test',
            '--project', 'core',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"


# =============================================================================
# Help Test
# =============================================================================

def test_run_help():
    """Test run subcommand help."""
    result = run_script(SCRIPT_PATH, 'run', '--help')
    assert '--targets' in result.stdout, "Should show --targets option"
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
        test_run_mode_actionable,
        test_run_mode_errors,
        test_run_with_project,
        test_run_help,
    ])
    sys.exit(runner.run())
