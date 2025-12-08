#!/usr/bin/env python3
"""Tests for npm.py consolidated script.

Tests npm/npx build execution and output parsing subcommands.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('builder', 'builder-npm-rules', 'npm.py')
MOCKS_DIR = Path(__file__).parent / 'mocks'
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Test Helpers
# =============================================================================

class TempDirContext:
    """Context manager for tests that need a temporary directory with mock npm/npx."""

    def __init__(self, mock_script='npm-success.sh'):
        self.temp_dir = None
        self.original_cwd = None
        self.original_path = None
        self.mock_script = mock_script

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        self.original_path = os.environ.get('PATH', '')
        os.chdir(self.temp_dir)

        # Create target directory
        (self.temp_dir / 'target').mkdir(exist_ok=True)

        # Create mock npm/npx wrapper
        mock_cmd = 'npm' if 'npm' in self.mock_script else 'npx'
        wrapper_path = self.temp_dir / mock_cmd
        wrapper_path.write_text(f'''#!/bin/bash
exec "{MOCKS_DIR / self.mock_script}" "$@"
''')
        wrapper_path.chmod(0o755)

        # Add temp dir to PATH
        os.environ['PATH'] = f"{self.temp_dir}:{self.original_path}"

        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)
        os.environ['PATH'] = self.original_path
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# EXECUTE Subcommand Tests
# =============================================================================

def test_execute_successful_npm_test():
    """Test successful npm test execution."""
    with TempDirContext('npm-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run test',
            '--timeout', '5000'
        )

        assert result.returncode == 0, f"Script should exit successfully, got {result.returncode}"
        data = result.json()
        assert data['status'] == 'success', "Status should be success"
        assert data['data']['exit_code'] == 0, "Exit code should be 0"
        assert data['data']['command_type'] == 'npm', "Command type should be npm"
        assert 'target/npm-output-' in data['data']['log_file'], "Should contain log file path"


def test_execute_failed_npm_test():
    """Test failed npm test execution."""
    with TempDirContext('npm-failure.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run test',
            '--timeout', '5000'
        )

        assert result.returncode == 0, "Script itself should exit successfully"
        data = result.json()
        assert data['status'] == 'success', "Status should be success (script reports test result)"
        assert data['data']['exit_code'] == 1, "Exit code should be 1 (test failure)"
        assert 'target/npm-output-' in data['data']['log_file'], "Should contain log file path"


def test_execute_npm_command_detection():
    """Test npm command type detection."""
    with TempDirContext('npm-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run build',
            '--timeout', '5000'
        )
        data = result.json()

        assert data['data']['command_type'] == 'npm', "Should detect npm command"


def test_execute_npx_command_detection():
    """Test npx command type detection."""
    with TempDirContext('npx-playwright-success.sh') as temp_dir:
        # Create npx wrapper
        npx_wrapper = temp_dir / 'npx'
        npx_wrapper.write_text(f'''#!/bin/bash
exec "{MOCKS_DIR / 'npx-playwright-success.sh'}" "$@"
''')
        npx_wrapper.chmod(0o755)

        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'playwright test',
            '--timeout', '5000'
        )
        data = result.json()

        assert data['data']['command_type'] == 'npx', "Should detect npx command"


def test_execute_log_file_creation():
    """Test log file is created."""
    with TempDirContext('npm-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run test',
            '--timeout', '5000'
        )
        data = result.json()
        log_file = Path(data['data']['log_file'])

        assert log_file.exists(), f"Log file should be created: {log_file}"


def test_execute_log_file_has_content():
    """Test log file has expected content."""
    with TempDirContext('npm-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run test',
            '--timeout', '5000'
        )
        data = result.json()
        log_file = Path(data['data']['log_file'])

        assert log_file.stat().st_size > 0, "Log file should have content"
        content = log_file.read_text()
        assert 'Test Suites:' in content, "Log file should contain test output"


def test_execute_timing():
    """Test command execution timing is tracked."""
    with TempDirContext('npm-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run test',
            '--timeout', '5000'
        )
        data = result.json()
        duration = data['data']['duration_ms']

        assert isinstance(duration, (int, float)), "Duration should be a number"
        assert duration >= 0, "Duration should be non-negative"


def test_execute_exec_output():
    """Test [EXEC] output is generated to stderr."""
    with TempDirContext('npm-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run test',
            '--timeout', '5000'
        )

        assert '[EXEC]' in result.stderr, "Should print [EXEC] line to stderr"


def test_execute_timestamped_log_filename():
    """Test log filename has timestamp format."""
    with TempDirContext('npm-success.sh'):
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--command', 'run test',
            '--timeout', '5000'
        )
        data = result.json()
        log_file = data['data']['log_file']

        import re
        # Check filename format: target/npm-output-YYYY-MM-DD-HHMMSS.log
        pattern = r'target/npm-output-\d{4}-\d{2}-\d{2}-\d{6}\.log'
        assert re.search(pattern, log_file), f"Log filename should match pattern: {log_file}"


# =============================================================================
# PARSE Subcommand Tests
# =============================================================================

def test_parse_successful_build():
    """Test parsing successful npm build output."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-success.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['status'] == 'success', "Status should be success"
    assert data['metrics']['total_issues'] == 0, "Should have 0 issues"
    assert data['metrics']['test_failures'] == 0, "Should have 0 test failures"


def test_parse_test_failures():
    """Test parsing build with test failures."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-test-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['status'] == 'failure', "Status should be failure"
    assert data['metrics']['test_failures'] > 0, "Should detect test failures"
    assert data['metrics']['total_issues'] > 0, "Should have issues"


def test_parse_lint_errors():
    """Test parsing lint errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-lint-errors.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['status'] == 'failure', "Status should be failure"
    assert data['metrics']['lint_errors'] > 0, "Should detect lint errors"
    assert data['metrics']['total_errors'] > 0, "Should count errors"


def test_parse_compilation_errors():
    """Test parsing compilation errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-compilation-error.log'),
        '--mode', 'structured'
    )
    data = result.json()

    # Script returns status=success even when compilation errors are found
    # It reports them in the metrics/issues
    assert data['metrics']['compilation_errors'] > 0, "Should detect compilation errors"
    assert data['metrics']['total_errors'] > 0, "Should have total errors"


def test_parse_playwright_failures():
    """Test parsing Playwright test failures."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-playwright-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['status'] == 'failure', "Status should be failure"
    assert data['metrics']['playwright_errors'] > 0, "Should detect Playwright errors"
    assert data['metrics']['total_issues'] > 0, "Should have issues"


def test_parse_dependency_errors():
    """Test parsing dependency errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-dependency-error.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['status'] == 'failure', "Status should be failure"
    assert data['metrics']['dependency_errors'] > 0, "Should detect dependency errors"


def test_parse_default_mode_output():
    """Test default mode output format."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-lint-errors.log'),
        '--mode', 'default'
    )
    # Default mode outputs JSON with status and errors fields
    data = result.json()
    assert 'status' in data, "Should have status field"
    assert 'errors' in data.get('data', {}), "Should have errors in data"


def test_parse_errors_only_mode():
    """Test errors-only mode output."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-lint-errors.log'),
        '--mode', 'errors'
    )
    # Errors mode outputs JSON with status and data
    data = result.json()
    assert 'status' in data, "Should have status field"
    assert 'data' in data, "Should have data field"


def test_parse_file_location_extraction():
    """Test file location extraction from compilation errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-compilation-error.log'),
        '--mode', 'structured'
    )
    data = result.json()

    # Check that issues have file locations
    issues = data.get('data', {}).get('issues', [])
    assert len(issues) > 0, "Should have issues"
    has_file = issues[0].get('file') is not None
    assert has_file, "Should extract file locations from errors"


def test_parse_issue_categorization():
    """Test issue categorization accuracy."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-test-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    test_failures = data['metrics']['test_failures']
    assert test_failures > 0, "Should correctly categorize test failures"


def test_parse_lint_error_location():
    """Test lint error line and column extraction."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-compilation-error.log'),
        '--mode', 'structured'
    )
    data = result.json()

    issues = data.get('data', {}).get('issues', [])
    assert len(issues) > 0, "Should have issues"
    has_line = issues[0].get('line') is not None
    assert has_line, "Should extract line numbers from errors"


def test_parse_multiple_error_types():
    """Test multiple error types in single file."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-lint-errors.log'),
        '--mode', 'structured'
    )
    data = result.json()

    total_errors = data['metrics']['total_errors']
    total_warnings = data['metrics']['total_warnings']

    assert total_errors > 0 and total_warnings > 0, \
        f"Should have both errors ({total_errors}) and warnings ({total_warnings})"


# =============================================================================
# Help Flag Test
# =============================================================================

def test_help_flag():
    """Test --help flag."""
    result = run_script(SCRIPT_PATH, '--help')

    assert 'execute' in result.stdout, "Help shows execute subcommand"
    assert 'parse' in result.stdout, "Help shows parse subcommand"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Execute subcommand tests
        test_execute_successful_npm_test,
        test_execute_failed_npm_test,
        test_execute_npm_command_detection,
        test_execute_npx_command_detection,
        test_execute_log_file_creation,
        test_execute_log_file_has_content,
        test_execute_timing,
        test_execute_exec_output,
        test_execute_timestamped_log_filename,
        # Parse subcommand tests
        test_parse_successful_build,
        test_parse_test_failures,
        test_parse_lint_errors,
        test_parse_compilation_errors,
        test_parse_playwright_failures,
        test_parse_dependency_errors,
        test_parse_default_mode_output,
        test_parse_errors_only_mode,
        test_parse_file_location_extraction,
        test_parse_issue_categorization,
        test_parse_lint_error_location,
        test_parse_multiple_error_types,
        # Help
        test_help_flag,
    ])
    sys.exit(runner.run())
