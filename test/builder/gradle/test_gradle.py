#!/usr/bin/env python3
"""Tests for consolidated gradle.py script with subcommands.

Tests all Gradle build operations:
- execute: Execute Gradle builds
- parse: Parse Gradle build output
- find-project: Find Gradle project paths
- search-markers: Search OpenRewrite markers
- check-warnings: Categorize build warnings
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test - consolidated gradle.py
SCRIPT_PATH = get_script_path('builder', 'builder-gradle-rules', 'gradle.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'
MOCKS_DIR = Path(__file__).parent / 'mocks'


# =============================================================================
# Test Helpers
# =============================================================================

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
# Execute Subcommand Tests
# =============================================================================

def test_execute_successful_build():
    """Test successful Gradle build."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--tasks', 'clean build',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )

        assert result.returncode == 0, f"Successful build should exit with 0, got {result.returncode}"
        data = result.json()
        assert data['status'] == 'success', "Status should be success"
        assert 'log_file' in data['data'], "Output should contain log_file"
        assert 'duration_ms' in data['data'], "Output should contain duration_ms"


def test_execute_project_parameter():
    """Test project parameter is passed correctly."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--tasks', 'build',
            '--project', ':core',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )
        data = result.json()
        command_executed = data['data']['command_executed']

        assert ':core' in command_executed, "Command should contain project flag"


def test_execute_skip_tests():
    """Test skip-tests flag is passed correctly."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--tasks', 'build',
            '--skip-tests',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )
        data = result.json()
        command_executed = data['data']['command_executed']

        assert '-x test' in command_executed, "Command should contain skip tests flag"


def test_execute_log_file_creation():
    """Test log file is created."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--tasks', 'build',
            '--gradlew', str(MOCKS_DIR / 'gradlew-success.sh')
        )
        data = result.json()
        log_file = Path(data['data']['log_file'])

        assert log_file.exists(), f"Log file should be created: {log_file}"


# =============================================================================
# Parse Subcommand Tests
# =============================================================================

def test_parse_successful_build():
    """Test parsing successful Gradle build output."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-gradle-success.log'),
        '--mode', 'structured'
    )
    assert result.success, f"Script failed: {result.stderr}"
    data = result.json()

    assert data['status'] == 'success', "Status should be success"
    assert data['data']['build_status'] == 'SUCCESS', "Build status should be SUCCESS"
    assert data['data']['summary'].get('compilation_errors', 0) == 0, "No compilation errors"


def test_parse_compilation_errors():
    """Test parsing build with compilation errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-gradle-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['data']['build_status'] == 'FAILURE', "Build status should be FAILURE"
    assert data['data']['summary'].get('compilation_errors', 0) > 0 or data['data']['summary'].get('test_failures', 0) > 0, "Should detect errors or failures"


def test_parse_javadoc_warnings():
    """Test parsing JavaDoc warnings."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-gradle-javadoc.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['data']['build_status'] == 'SUCCESS', "Build status should be SUCCESS"
    assert data['data']['summary'].get('javadoc_warnings', 0) > 0, "Should detect JavaDoc warnings"


def test_parse_errors_only_mode():
    """Test errors-only mode."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-gradle-failure.log'),
        '--mode', 'errors'
    )
    data = result.json()

    assert 'data' in data, "Output should have data"
    assert 'issues' in data['data'], "Output should have issues"


def test_parse_default_mode():
    """Test default mode (human-readable)."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-gradle-success.log'),
        '--mode', 'default'
    )

    assert 'Build Status: SUCCESS' in result.stdout, "Build Status line should be present"


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


# =============================================================================
# Find-Project Subcommand Tests
# =============================================================================

def test_find_project_by_name():
    """Test finding project by name."""
    with TempDirContext() as temp_dir:
        # Create test structure
        project_dir = temp_dir / 'modules' / 'core'
        project_dir.mkdir(parents=True)
        build_file = project_dir / 'build.gradle'
        build_file.write_text('// Gradle build file')

        settings_file = temp_dir / 'settings.gradle'
        settings_file.write_text("include ':modules:core'")

        result = run_script(
            SCRIPT_PATH,
            'find-project',
            '--project-name', 'core',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', f"Should find project: {data}"


def test_find_project_not_found():
    """Test finding non-existent project."""
    with TempDirContext() as temp_dir:
        settings_file = temp_dir / 'settings.gradle'
        settings_file.write_text("")

        result = run_script(
            SCRIPT_PATH,
            'find-project',
            '--project-name', 'nonexistent',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'error', "Should return error for non-existent project"


def test_find_project_validate_path():
    """Test validating explicit project path."""
    with TempDirContext() as temp_dir:
        # Create test structure
        project_dir = temp_dir / 'services' / 'api'
        project_dir.mkdir(parents=True)
        build_file = project_dir / 'build.gradle.kts'
        build_file.write_text('// Gradle Kotlin DSL')

        result = run_script(
            SCRIPT_PATH,
            'find-project',
            '--project-path', 'services/api',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', f"Should validate existing path: {data}"


# =============================================================================
# Search-Markers Subcommand Tests
# =============================================================================

def test_search_markers_no_markers():
    """Test searching when no markers exist."""
    with TempDirContext() as temp_dir:
        src_dir = temp_dir / 'src' / 'main' / 'java'
        src_dir.mkdir(parents=True)
        java_file = src_dir / 'Test.java'
        java_file.write_text('public class Test {}')

        result = run_script(
            SCRIPT_PATH,
            'search-markers',
            '--source-dir', str(temp_dir / 'src')
        )
        data = result.json()

        assert data['status'] == 'success', "Should succeed with no markers"
        assert data['data']['total_markers'] == 0, "Should find no markers"


def test_search_markers_finds_todo():
    """Test finding OpenRewrite TODO markers."""
    with TempDirContext() as temp_dir:
        src_dir = temp_dir / 'src' / 'main' / 'java'
        src_dir.mkdir(parents=True)
        java_file = src_dir / 'Test.java'
        # Use the actual OpenRewrite marker format: /*~~(TODO: ...)>*/
        java_file.write_text('''public class Test {
    /*~~(TODO: CuiLogRecordPatternRecipe Replace with CUI logging)>*/void method() {}
}''')

        result = run_script(
            SCRIPT_PATH,
            'search-markers',
            '--source-dir', str(temp_dir / 'src')
        )
        data = result.json()

        assert data['status'] == 'success', f"Should succeed: {data}"
        assert data['data']['total_markers'] > 0, "Should find TODO marker"


def test_search_markers_categorization():
    """Test marker categorization (auto_suppress vs ask_user)."""
    with TempDirContext() as temp_dir:
        src_dir = temp_dir / 'src' / 'main' / 'java'
        src_dir.mkdir(parents=True)
        java_file = src_dir / 'Test.java'
        # Use the actual OpenRewrite marker format: /*~~(TODO: ...)>*/
        java_file.write_text('''public class Test {
    /*~~(TODO: CuiLogRecordPatternRecipe Should be auto-suppressed)>*/void autoSuppress() {}
    /*~~(TODO: SomeOtherRecipe Should ask user)>*/void askUser() {}
}''')

        result = run_script(
            SCRIPT_PATH,
            'search-markers',
            '--source-dir', str(temp_dir / 'src')
        )
        data = result.json()

        assert 'by_category' in data['data'], "Should have category breakdown"


# =============================================================================
# Check-Warnings Subcommand Tests
# =============================================================================

def test_check_warnings_empty():
    """Test with no warnings."""
    warnings = json.dumps([])
    acceptable = json.dumps({})

    result = run_script(
        SCRIPT_PATH,
        'check-warnings',
        '--warnings', warnings,
        '--acceptable-warnings', acceptable
    )
    data = result.json()

    assert data['success'] is True, "Should succeed with no warnings"
    assert data['total'] == 0, "Total should be 0"


def test_check_warnings_fixable():
    """Test identifying fixable warnings."""
    warnings = json.dumps([
        {'type': 'javadoc_warning', 'message': 'Missing @param', 'file': 'Test.java', 'line': 10}
    ])
    acceptable = json.dumps({})

    result = run_script(
        SCRIPT_PATH,
        'check-warnings',
        '--warnings', warnings,
        '--acceptable-warnings', acceptable
    )
    data = result.json()

    assert data['fixable'] > 0, "Should identify fixable warning"
    assert result.returncode == 1, "Should exit with 1 when fixable warnings exist"


def test_check_warnings_acceptable():
    """Test acceptable warnings are filtered."""
    warnings = json.dumps([
        {'type': 'other', 'message': 'Using deprecated gradle feature'}
    ])
    acceptable = json.dumps({
        'gradle_deprecation': ['Using deprecated gradle feature']
    })

    result = run_script(
        SCRIPT_PATH,
        'check-warnings',
        '--warnings', warnings,
        '--acceptable-warnings', acceptable
    )
    data = result.json()

    assert data['acceptable'] > 0, "Should identify acceptable warning"


def test_check_warnings_always_fixable_types():
    """Test that certain types are always fixable regardless of patterns."""
    warnings = json.dumps([
        {'type': 'compilation_error', 'message': 'some error', 'file': 'Test.java', 'line': 5}
    ])
    acceptable = json.dumps({
        'compilation_error': ['some error']  # Should be ignored
    })

    result = run_script(
        SCRIPT_PATH,
        'check-warnings',
        '--warnings', warnings,
        '--acceptable-warnings', acceptable
    )
    data = result.json()

    assert data['fixable'] > 0, "Compilation errors should always be fixable"


# =============================================================================
# Help Tests
# =============================================================================

def test_help_main():
    """Test main --help output."""
    result = run_script(SCRIPT_PATH, '--help')
    assert 'execute' in result.stdout, "Should show execute subcommand"
    assert 'parse' in result.stdout, "Should show parse subcommand"
    assert 'find-project' in result.stdout, "Should show find-project subcommand"


def test_help_execute():
    """Test execute --help output."""
    result = run_script(SCRIPT_PATH, 'execute', '--help')
    assert '--tasks' in result.stdout, "Should show --tasks option"
    assert '--project' in result.stdout, "Should show --project option"


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
        # Execute tests
        test_execute_successful_build,
        test_execute_project_parameter,
        test_execute_skip_tests,
        test_execute_log_file_creation,
        # Parse tests
        test_parse_successful_build,
        test_parse_compilation_errors,
        test_parse_javadoc_warnings,
        test_parse_errors_only_mode,
        test_parse_default_mode,
        test_parse_missing_file,
        # Find-project tests
        test_find_project_by_name,
        test_find_project_not_found,
        test_find_project_validate_path,
        # Search-markers tests
        test_search_markers_no_markers,
        test_search_markers_finds_todo,
        test_search_markers_categorization,
        # Check-warnings tests
        test_check_warnings_empty,
        test_check_warnings_fixable,
        test_check_warnings_acceptable,
        test_check_warnings_always_fixable_types,
        # Help tests
        test_help_main,
        test_help_execute,
        test_help_parse,
    ])
    sys.exit(runner.run())
