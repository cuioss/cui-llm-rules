#!/usr/bin/env python3
"""Tests for pm-dev-frontend:build-operations npm scripts.

Tests npm/npx build operations:
- execute: Execute npm/npx builds
- parse: Parse npm/npx build output
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test - pm-dev-frontend bundle
SCRIPT_PATH = get_script_path('pm-dev-frontend', 'plan-marshall-plugin', 'npm.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


class TempDirContext:
    """Context manager for tests that need a temporary directory."""

    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Parse Subcommand Tests
# =============================================================================

def test_parse_successful_build():
    """Test parsing successful npm build output."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-success.log'),
        '--mode', 'structured'
    )
    assert result.success, f"Script failed: {result.stderr}"
    data = result.json()

    assert data['status'] == 'success', "Status should be success"


def test_parse_compilation_errors():
    """Test parsing build with compilation errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-compilation-error.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert 'compilation_errors' in data['metrics'], "Should have compilation_errors metric"


def test_parse_test_failures():
    """Test parsing build with test failures."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-test-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert 'test_failures' in data['metrics'], "Should have test_failures metric"


def test_parse_lint_errors():
    """Test parsing build with lint errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-lint-errors.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert 'lint_errors' in data['metrics'], "Should have lint_errors metric"


def test_parse_dependency_errors():
    """Test parsing build with dependency errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-dependency-error.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert 'dependency_errors' in data['metrics'], "Should have dependency_errors metric"


def test_parse_playwright_failures():
    """Test parsing Playwright test failures."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-playwright-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert 'playwright_errors' in data['metrics'], "Should have playwright_errors metric"


def test_parse_missing_file():
    """Test missing file handling."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', 'nonexistent.log',
        '--mode', 'structured'
    )
    data = result.json()

    assert data['status'] == 'error', "Should return error status for missing file"


def test_parse_errors_only_mode():
    """Test errors-only mode."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-npm-compilation-error.log'),
        '--mode', 'errors'
    )
    data = result.json()

    assert 'errors' in data['data'], "Should have errors in data"


# =============================================================================
# Help Tests
# =============================================================================

def test_help_main():
    """Test main --help output."""
    result = run_script(SCRIPT_PATH, '--help')
    assert 'execute' in result.stdout, "Should show execute subcommand"
    assert 'parse' in result.stdout, "Should show parse subcommand"


def test_help_execute():
    """Test execute --help output."""
    result = run_script(SCRIPT_PATH, 'execute', '--help')
    assert '--command' in result.stdout, "Should show --command option"
    assert '--workspace' in result.stdout, "Should show --workspace option"


def test_help_parse():
    """Test parse --help output."""
    result = run_script(SCRIPT_PATH, 'parse', '--help')
    assert '--log' in result.stdout, "Should show --log option"
    assert '--mode' in result.stdout, "Should show --mode option"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_successful_build,
        test_parse_compilation_errors,
        test_parse_test_failures,
        test_parse_lint_errors,
        test_parse_dependency_errors,
        test_parse_playwright_failures,
        test_parse_missing_file,
        test_parse_errors_only_mode,
        test_help_main,
        test_help_execute,
        test_help_parse,
    ])
    sys.exit(runner.run())
