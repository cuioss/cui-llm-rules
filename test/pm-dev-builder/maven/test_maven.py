#!/usr/bin/env python3
"""Tests for consolidated maven.py script with subcommands.

Tests all Maven build operations:
- execute: Execute Maven builds
- parse: Parse Maven build output
- find-module: Find Maven module paths
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

# Script under test - consolidated maven.py
SCRIPT_PATH = get_script_path('pm-dev-builder', 'builder-maven-rules', 'maven.py')
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
    """Test successful Maven build."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--goals', 'clean install',
            '--mvnw', str(MOCKS_DIR / 'mvnw-success.sh')
        )

        assert result.returncode == 0, f"Successful build should exit with 0, got {result.returncode}"
        data = result.json()
        assert data['status'] == 'success', "Status should be success"
        assert data['data']['exit_code'] == 0, "Exit code should be 0"
        assert 'log_file' in data['data'], "Output should contain log_file"
        assert 'duration_ms' in data['data'], "Output should contain duration_ms"


def test_execute_failed_build():
    """Test failed Maven build."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--goals', 'clean install',
            '--mvnw', str(MOCKS_DIR / 'mvnw-failure.sh')
        )

        assert result.returncode == 1, "Failed build should exit with 1"
        data = result.json()
        assert data['status'] == 'error', "Status should be error"
        assert data['error'] == 'build_failed', "Error type should be build_failed"


def test_execute_profile_parameter():
    """Test profile parameter is passed correctly."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--goals', 'clean install',
            '--profile', 'pre-commit',
            '--mvnw', str(MOCKS_DIR / 'mvnw-success.sh')
        )
        data = result.json()
        command_executed = data['data']['command_executed']

        assert '-Ppre-commit' in command_executed, "Command should contain profile flag"


def test_execute_module_parameter():
    """Test module parameter is passed correctly."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--goals', 'clean install',
            '--module', 'auth-service',
            '--mvnw', str(MOCKS_DIR / 'mvnw-success.sh')
        )
        data = result.json()
        command_executed = data['data']['command_executed']

        assert '-pl auth-service' in command_executed, "Command should contain module flag"


def test_execute_log_file_creation():
    """Test log file is created."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--goals', 'clean install',
            '--mvnw', str(MOCKS_DIR / 'mvnw-success.sh')
        )
        data = result.json()
        log_file = Path(data['data']['log_file'])

        assert log_file.exists(), f"Log file should be created: {log_file}"


# =============================================================================
# Parse Subcommand Tests
# =============================================================================

def test_parse_successful_build():
    """Test parsing successful Maven build output."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-maven-success.log'),
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
        '--log', str(FIXTURES_DIR / 'sample-maven-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['data']['build_status'] == 'FAILURE', "Build status should be FAILURE"
    assert data['data']['summary'].get('compilation_errors', 0) > 0, "Should detect compilation errors"


def test_parse_javadoc_warnings():
    """Test parsing JavaDoc warnings."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-maven-javadoc.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['data']['build_status'] == 'SUCCESS', "Build status should be SUCCESS"
    assert data['data']['summary'].get('javadoc_warnings', 0) > 0, "Should detect JavaDoc warnings"


def test_parse_openrewrite_filtering():
    """Test OpenRewrite message filtering."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-maven-openrewrite.log'),
        '--mode', 'no-openrewrite'
    )
    assert result.success, "no-openrewrite mode should execute successfully"


def test_parse_errors_only_mode():
    """Test errors-only mode."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-maven-failure.log'),
        '--mode', 'errors'
    )

    assert 'Errors:' in result.stdout, "Errors section should be present"


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
# Find-Module Subcommand Tests
# =============================================================================

def test_find_module_by_artifact_id():
    """Test finding module by artifactId (without namespace)."""
    with TempDirContext() as temp_dir:
        # Create test structure - use POM without namespace
        module_dir = temp_dir / 'modules' / 'auth-service'
        module_dir.mkdir(parents=True)
        pom = module_dir / 'pom.xml'
        pom.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>auth-service</artifactId>
    <version>1.0.0</version>
</project>''')

        result = run_script(
            SCRIPT_PATH,
            'find-module',
            '--artifact-id', 'auth-service',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', f"Should find module: {data}"
        assert 'auth-service' in data['data']['module_path'], "Module path should contain auth-service"


def test_find_module_by_artifact_id_with_namespace():
    """Test finding module by artifactId with Maven namespace (real-world POMs)."""
    with TempDirContext() as temp_dir:
        # Create test structure - use POM WITH namespace (standard Maven POM)
        module_dir = temp_dir / 'modules' / 'core-service'
        module_dir.mkdir(parents=True)
        pom = module_dir / 'pom.xml'
        pom.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>core-service</artifactId>
    <version>1.0.0</version>
</project>''')

        result = run_script(
            SCRIPT_PATH,
            'find-module',
            '--artifact-id', 'core-service',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', f"Should find module with namespace: {data}"
        assert 'core-service' in data['data']['module_path'], "Module path should contain core-service"


def test_find_module_with_fixture():
    """Test finding module using real fixture with namespace."""
    # Use the existing multi-module fixture which has namespaced POMs
    fixture_dir = FIXTURES_DIR / 'multi-module-project'

    result = run_script(
        SCRIPT_PATH,
        'find-module',
        '--artifact-id', 'core-module',
        '--root', str(fixture_dir)
    )
    data = result.json()

    assert data['status'] == 'success', f"Should find core-module in fixture: {data}"
    assert data['data']['module_path'] == 'core', f"Module path should be 'core': {data}"


def test_find_module_not_found():
    """Test finding non-existent module."""
    with TempDirContext() as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'find-module',
            '--artifact-id', 'nonexistent',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'error', "Should return error for non-existent module"


def test_find_module_validate_path():
    """Test validating explicit module path (without namespace)."""
    with TempDirContext() as temp_dir:
        # Create test structure - use POM without namespace
        module_dir = temp_dir / 'services' / 'api'
        module_dir.mkdir(parents=True)
        pom = module_dir / 'pom.xml'
        pom.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>api-service</artifactId>
    <version>1.0.0</version>
</project>''')

        result = run_script(
            SCRIPT_PATH,
            'find-module',
            '--module-path', 'services/api',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', f"Should validate existing path: {data}"


def test_find_module_validate_path_with_namespace():
    """Test validating explicit module path with Maven namespace."""
    with TempDirContext() as temp_dir:
        # Create test structure - use POM WITH namespace
        module_dir = temp_dir / 'services' / 'api'
        module_dir.mkdir(parents=True)
        pom = module_dir / 'pom.xml'
        pom.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>api-service</artifactId>
    <version>1.0.0</version>
</project>''')

        result = run_script(
            SCRIPT_PATH,
            'find-module',
            '--module-path', 'services/api',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', f"Should validate path with namespace: {data}"
        assert data['data']['artifact_id'] == 'api-service', f"Should extract artifact_id: {data}"


def test_find_module_ambiguous():
    """Test finding module with multiple matches (ambiguous artifactId)."""
    # Use the existing multi-module fixture which has auth-service in two locations
    fixture_dir = FIXTURES_DIR / 'multi-module-project'

    result = run_script(
        SCRIPT_PATH,
        'find-module',
        '--artifact-id', 'auth-service',
        '--root', str(fixture_dir)
    )
    data = result.json()

    assert data['status'] == 'error', f"Should return error for ambiguous: {data}"
    assert data['error'] == 'ambiguous_artifact_id', f"Error type should be ambiguous: {data}"
    assert 'choices' in data, f"Should provide choices: {data}"
    assert len(data['choices']) == 2, f"Should have 2 choices: {data}"


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
    # Warnings must have severity: WARNING to be processed by check-warnings
    warnings = json.dumps([
        {'type': 'javadoc_warning', 'message': 'Missing @param', 'file': 'Test.java', 'line': 10, 'severity': 'WARNING'}
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
    # Warnings must have severity: WARNING to be processed
    warnings = json.dumps([
        {'type': 'other', 'message': 'The POM for com.example:lib is missing', 'file': '', 'line': 0, 'severity': 'WARNING'}
    ])
    acceptable = json.dumps({
        'transitive_dependency': ['The POM for com.example:lib is missing']
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
    # Warnings must have severity: WARNING to be processed
    warnings = json.dumps([
        {'type': 'compilation_error', 'message': 'some error', 'file': 'Test.java', 'line': 5, 'severity': 'WARNING'}
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
    assert 'find-module' in result.stdout, "Should show find-module subcommand"


def test_help_execute():
    """Test execute --help output."""
    result = run_script(SCRIPT_PATH, 'execute', '--help')
    assert '--goals' in result.stdout, "Should show --goals option"
    assert '--profile' in result.stdout, "Should show --profile option"


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
        test_execute_failed_build,
        test_execute_profile_parameter,
        test_execute_module_parameter,
        test_execute_log_file_creation,
        # Parse tests
        test_parse_successful_build,
        test_parse_compilation_errors,
        test_parse_javadoc_warnings,
        test_parse_openrewrite_filtering,
        test_parse_errors_only_mode,
        test_parse_missing_file,
        # Find-module tests
        test_find_module_by_artifact_id,
        test_find_module_by_artifact_id_with_namespace,
        test_find_module_with_fixture,
        test_find_module_not_found,
        test_find_module_validate_path,
        test_find_module_validate_path_with_namespace,
        test_find_module_ambiguous,
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
