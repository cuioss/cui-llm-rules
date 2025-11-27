#!/usr/bin/env python3
"""Tests for find-gradle-project.py script.

Migrated from test-find-gradle-project.sh - tests Gradle project path detection and ambiguity handling.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('builder', 'builder-gradle-rules', 'find-gradle-project.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_find_unique_project():
    """Test finding a unique project by name."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'user-service',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )

    assert result.returncode == 0, "Unique project should exit with 0"
    data = result.json()
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['project_name'] == 'user-service', "Project name should match"
    assert ':services:user-service' in str(data), "Should contain project path"


def test_find_core_project():
    """Test finding the core project."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'core',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )

    assert result.returncode == 0, "Core project should exit with 0"
    data = result.json()
    assert data['data']['project_path'] == ':core', "Project path should be :core"


def test_ambiguous_project_name():
    """Test handling of ambiguous project name (multiple matches)."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'auth-service',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )

    assert result.returncode == 1, "Ambiguous project should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'ambiguous_project_name', "Error should be ambiguous_project_name"
    assert 'choices' in data, "Should contain choices array"
    # Should include both auth-service locations
    choices_str = str(data['choices'])
    assert ':services:auth-service' in choices_str, "Choices should include :services:auth-service"
    assert ':legacy:auth-service' in choices_str, "Choices should include :legacy:auth-service"


def test_project_not_found():
    """Test handling of non-existent project name."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'nonexistent-project',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )

    assert result.returncode == 1, "Not found should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'project_not_found', "Error should be project_not_found"


def test_validate_project_path():
    """Test validating an existing project path."""
    result = run_script(
        SCRIPT_PATH,
        '--project-path', 'services/auth-service',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )

    assert result.returncode == 0, "Valid path should exit with 0"
    data = result.json()
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['project_name'] == 'auth-service', "Should extract project name"
    assert ':services:auth-service' in str(data), "Path should match"


def test_validate_invalid_path():
    """Test validating a non-existent project path."""
    result = run_script(
        SCRIPT_PATH,
        '--project-path', 'nonexistent/path',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )

    assert result.returncode == 1, "Invalid path should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'path_not_found', "Error should be path_not_found"


def test_single_project():
    """Test with a single project."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'simple-app',
        '--root', str(FIXTURES_DIR / 'single-project')
    )

    assert result.returncode == 0, "Single project should exit with 0"
    data = result.json()
    assert data['status'] == 'success', "Status should be success"


def test_parent_projects_extraction():
    """Test that parent projects are extracted correctly."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'user-service',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )
    data = result.json()

    # Check parent_projects contains ":services"
    parent_projects = data['data'].get('parent_projects', [])
    assert ':services' in parent_projects, "Parent projects should include ':services'"


def test_root_not_found():
    """Test error when root directory doesn't exist."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'test',
        '--root', '/nonexistent/directory'
    )

    assert result.returncode == 1, "Missing root should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"


def test_build_file_in_output():
    """Test that build file path is included in output."""
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'core',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )
    data = result.json()

    assert 'core/build.gradle.kts' in str(data), "Output should include build_file path"


def test_does_not_match_dependencies():
    """Test that project name search doesn't match dependencies."""
    # user-service has auth-service as a dependency
    # Searching for auth-service should NOT match user-service
    result = run_script(
        SCRIPT_PATH,
        '--project-name', 'auth-service',
        '--root', str(FIXTURES_DIR / 'multi-project')
    )
    data = result.json()

    # Should find exactly 2 projects (services/auth-service and legacy/auth-service)
    # NOT user-service (which only has it as dependency)
    choices = data.get('choices', [])
    assert len(choices) == 2, f"Should find exactly 2 auth-service projects (not dependencies), got {len(choices)}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_find_unique_project,
        test_find_core_project,
        test_ambiguous_project_name,
        test_project_not_found,
        test_validate_project_path,
        test_validate_invalid_path,
        test_single_project,
        test_parent_projects_extraction,
        test_root_not_found,
        test_build_file_in_output,
        test_does_not_match_dependencies,
    ])
    sys.exit(runner.run())
