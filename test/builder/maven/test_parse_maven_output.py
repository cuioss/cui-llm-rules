#!/usr/bin/env python3
"""Tests for parse-maven-output.py script.

Migrated from test-parse-maven-output.sh - tests Maven build output parsing and categorization.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('builder', 'builder-maven-rules', 'parse-maven-output.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_successful_build():
    """Test parsing successful Maven build output."""
    result = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-success.log'),
        '--mode', 'structured'
    )
    assert result.success, f"Script failed: {result.stderr}"
    data = result.json()

    # Check status is success
    assert data['status'] == 'success', "Status should be success"

    # Check build_status is SUCCESS
    assert data['data']['build_status'] == 'SUCCESS', "Build status should be SUCCESS"

    # Check no compilation errors
    comp_errors = data['data']['summary'].get('compilation_errors', 0)
    assert comp_errors == 0, f"Expected 0 compilation errors, got: {comp_errors}"

    # Check tests run count (if present)
    tests_run = data.get('metrics', {}).get('tests_run', 0)
    assert tests_run >= 0, "Tests run should be non-negative"

    # Check duration extracted (if present)
    duration = data.get('metrics', {}).get('duration_ms', 0)
    assert duration >= 0, "Duration should be non-negative"


def test_compilation_errors():
    """Test parsing build with compilation errors."""
    result = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    # Check build_status is FAILURE
    assert data['data']['build_status'] == 'FAILURE', "Build status should be FAILURE"

    # Check compilation errors detected
    comp_errors = data['data']['summary'].get('compilation_errors', 0)
    assert comp_errors > 0, "Should have detected compilation errors"

    # Check test failures detected
    test_failures = data['data']['summary'].get('test_failures', 0)
    assert test_failures > 0, "Should have detected test failures"


def test_javadoc_warnings():
    """Test parsing JavaDoc warnings."""
    result = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-javadoc.log'),
        '--mode', 'structured'
    )
    data = result.json()

    # Check build_status is SUCCESS (javadoc warnings don't fail build by default)
    assert data['data']['build_status'] == 'SUCCESS', "Build status should be SUCCESS"

    # Check javadoc warnings detected
    javadoc_warnings = data['data']['summary'].get('javadoc_warnings', 0)
    assert javadoc_warnings > 0, "Should have detected JavaDoc warnings"


def test_openrewrite_filtering():
    """Test OpenRewrite message filtering."""
    # First, check with structured mode
    result_default = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-openrewrite.log'),
        '--mode', 'structured'
    )
    assert result_default.success, f"Structured mode failed: {result_default.stderr}"

    # Check no-openrewrite mode runs without error
    result_filtered = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-openrewrite.log'),
        '--mode', 'no-openrewrite'
    )
    assert result_filtered.success, "no-openrewrite mode should execute successfully"


def test_errors_only_mode():
    """Test errors-only mode."""
    result = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-failure.log'),
        '--mode', 'errors'
    )

    # Check output contains "Errors:" section
    assert 'Errors:' in result.stdout, "Errors section should be present"


def test_default_mode():
    """Test default mode (human-readable)."""
    result = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-success.log'),
        '--mode', 'default'
    )

    # Check output contains Status line
    assert 'Status: SUCCESS' in result.stdout, "Status line should be present"

    # Check output contains Summary section
    assert 'Summary:' in result.stdout, "Summary section should be present"


def test_missing_file():
    """Test missing file handling."""
    result = run_script(
        SCRIPT_PATH,
        '--log', 'nonexistent.log',
        '--mode', 'structured'
    )
    data = result.json()

    # Check error status
    assert data['status'] == 'error', "Should return error status for missing file"


def test_help_flag():
    """Test --help flag."""
    result = run_script(SCRIPT_PATH, '--help')

    assert 'Parse Maven build output' in result.stdout, "Help should contain description"
    assert '--log' in result.stdout, "Help should contain --log option"
    assert '--mode' in result.stdout, "Help should contain --mode option"


def test_issue_structure():
    """Test issue structure in output."""
    result = run_script(
        SCRIPT_PATH,
        '--log', str(FIXTURES_DIR / 'sample-maven-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    # Check issues array has proper structure
    issues = data['data'].get('issues', [])
    if len(issues) > 0:
        first_issue = issues[0]
        assert 'type' in first_issue, "Issue should have type field"
        assert 'severity' in first_issue, "Issue should have severity field"
        assert 'message' in first_issue, "Issue should have message field"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_successful_build,
        test_compilation_errors,
        test_javadoc_warnings,
        test_openrewrite_filtering,
        test_errors_only_mode,
        test_default_mode,
        test_missing_file,
        test_help_flag,
        test_issue_structure,
    ])
    sys.exit(runner.run())
