#!/usr/bin/env python3
"""Tests for find-module-path.py script.

Migrated from test-find-module-path.sh - tests Maven module path detection and ambiguity handling.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('builder', 'builder-maven-rules', 'find-module-path.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_find_unique_module():
    """Test finding a unique module by artifact ID."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'user-service',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )

    assert result.returncode == 0, "Unique module should exit with 0"
    data = result.json()
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['artifact_id'] == 'user-service', "ArtifactId should match"
    assert data['data']['module_path'] == 'services/user-service', "Module path should be correct"
    assert '-pl services/user-service' in str(data), "Should contain maven_pl_argument"


def test_find_core_module():
    """Test finding the core module."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'core-module',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )

    assert result.returncode == 0, "Core module should exit with 0"
    data = result.json()
    assert data['data']['module_path'] == 'core', "Module path should be core"


def test_ambiguous_artifact_id():
    """Test handling of ambiguous artifact ID (multiple matches)."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'auth-service',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )

    assert result.returncode == 1, "Ambiguous module should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'ambiguous_artifact_id', "Error should be ambiguous_artifact_id"
    assert 'choices' in data, "Should contain choices array"
    # Should include both auth-service locations
    choices_str = str(data['choices'])
    assert 'services/auth-service' in choices_str, "Choices should include services/auth-service"
    assert 'legacy/auth-service' in choices_str, "Choices should include legacy/auth-service"


def test_artifact_not_found():
    """Test handling of non-existent artifact ID."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'nonexistent-module',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )

    assert result.returncode == 1, "Not found should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'artifact_not_found', "Error should be artifact_not_found"


def test_validate_module_path():
    """Test validating an existing module path."""
    result = run_script(
        SCRIPT_PATH,
        '--module-path', 'services/auth-service',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )

    assert result.returncode == 0, "Valid path should exit with 0"
    data = result.json()
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['artifact_id'] == 'auth-service', "Should extract artifactId"
    assert data['data']['module_path'] == 'services/auth-service', "Path should match"


def test_validate_invalid_path():
    """Test validating a non-existent module path."""
    result = run_script(
        SCRIPT_PATH,
        '--module-path', 'nonexistent/path',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )

    assert result.returncode == 1, "Invalid path should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'module_not_found', "Error should be module_not_found"


def test_single_module_project():
    """Test with a single module project."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'simple-app',
        '--root', str(FIXTURES_DIR / 'single-module-project')
    )

    assert result.returncode == 0, "Single module should exit with 0"
    data = result.json()
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['module_path'] == '.', "Module path should be root"


def test_parent_modules_extraction():
    """Test that parent modules are extracted correctly."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'user-service',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )
    data = result.json()

    # Check parent_modules contains "services"
    parent_modules = data['data'].get('parent_modules', [])
    assert 'services' in parent_modules, "Parent modules should include 'services'"


def test_root_not_found():
    """Test error when root directory doesn't exist."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'test',
        '--root', '/nonexistent/directory'
    )

    assert result.returncode == 1, "Missing root should exit with 1"
    data = result.json()
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'root_not_found', "Error should be root_not_found"


def test_pom_file_in_output():
    """Test that pom file path is included in output."""
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'core-module',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )
    data = result.json()

    assert 'core/pom.xml' in str(data), "Output should include pom_file path"


def test_does_not_match_dependencies():
    """Test that artifact ID search doesn't match dependencies."""
    # user-service has auth-service as a dependency
    # Searching for auth-service should NOT match user-service
    result = run_script(
        SCRIPT_PATH,
        '--artifact-id', 'auth-service',
        '--root', str(FIXTURES_DIR / 'multi-module-project')
    )
    data = result.json()

    # Should find exactly 2 modules (services/auth-service and legacy/auth-service)
    # NOT user-service (which only has it as dependency)
    choices = data.get('choices', [])
    assert len(choices) == 2, f"Should find exactly 2 auth-service modules (not dependencies), got {len(choices)}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_find_unique_module,
        test_find_core_module,
        test_ambiguous_artifact_id,
        test_artifact_not_found,
        test_validate_module_path,
        test_validate_invalid_path,
        test_single_module_project,
        test_parent_modules_extraction,
        test_root_not_found,
        test_pom_file_in_output,
        test_does_not_match_dependencies,
    ])
    sys.exit(runner.run())
