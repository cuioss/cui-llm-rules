#!/usr/bin/env python3
"""Tests for npm run subcommand.

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

# Script under test - pm-dev-frontend bundle
SCRIPT_PATH = get_script_path('pm-dev-frontend', 'build-operations', 'npm.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


class TempDirContext:
    """Context manager for tests that need a temporary directory with npm mock."""

    def __init__(self, npm_script_content: str = None):
        self.temp_dir = None
        self.original_cwd = None
        self.npm_content = npm_script_content or '''#!/bin/bash
echo "npm run test"
echo ""
echo "> test"
echo "> jest"
echo ""
echo "PASS src/test.js"
exit 0
'''

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        # Create target directory for log files
        (self.temp_dir / 'target').mkdir()
        # Create mock npm script
        npm_mock = self.temp_dir / 'npm'
        npm_mock.write_text(self.npm_content)
        npm_mock.chmod(0o755)
        # Add to PATH
        os.environ['PATH'] = str(self.temp_dir) + ':' + os.environ.get('PATH', '')
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class FailingNpmContext(TempDirContext):
    """Context with failing npm mock."""

    def __init__(self):
        super().__init__('''#!/bin/bash
echo "npm run test"
echo ""
echo "> test"
echo "> jest"
echo ""
echo "FAIL src/test.js"
echo "  ● Test suite failed to run"
echo ""
echo "    Error: Cannot find module './missing'"
echo ""
echo "      at src/test.js:1:1"
exit 1
''')


# =============================================================================
# Run Success Tests
# =============================================================================

def test_run_success_output_format():
    """Test run command success output format (TOON format)."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'run test'
        )

        assert result.returncode == 0, f"Successful run should exit with 0: {result.stderr}"

        # Parse TOON output
        assert 'status: success' in result.stdout, f"Status should be success: {result.stdout}"
        assert 'log_file' in result.stdout, "Should include log_file"
        assert 'exit_code: 0' in result.stdout, "Exit code should be 0"


def test_run_includes_duration():
    """Test run command includes duration in output."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'run test'
        )

        assert 'duration_seconds' in result.stdout, "Should include duration_seconds"


def test_run_includes_command_executed():
    """Test run command includes command_executed in output."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'run test'
        )

        assert 'command_executed' in result.stdout, "Should include command_executed"


# =============================================================================
# Run Failure Tests
# =============================================================================

def test_run_failure_includes_errors():
    """Test run command failure includes error status."""
    with FailingNpmContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'run test'
        )

        assert result.returncode == 1, f"Failed run should exit with 1: {result.stdout}"
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
            '--targets', 'run test',
            '--mode', 'actionable'
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'status: success' in result.stdout


def test_run_mode_errors():
    """Test run with --mode errors (no warnings)."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'run test',
            '--mode', 'errors'
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"


def test_run_mode_structured():
    """Test run with --mode structured (all issues with markers)."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'run test',
            '--mode', 'structured'
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"


# =============================================================================
# Workspace Parameter Tests
# =============================================================================

def test_run_with_workspace():
    """Test run with --workspace parameter."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'run',
            '--targets', 'run test',
            '--workspace', 'packages/core'
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
        test_run_includes_command_executed,
        test_run_failure_includes_errors,
        test_run_mode_actionable,
        test_run_mode_errors,
        test_run_mode_structured,
        test_run_with_workspace,
        test_run_help,
    ])
    sys.exit(runner.run())
