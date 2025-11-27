#!/usr/bin/env python3
"""Tests for detect-build-systems.py script.

Migrated from test-detect-build-systems.sh - tests build system detection logic.
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
SCRIPT_PATH = get_script_path('builder', 'environment-detection', 'detect-build-systems.py')


# =============================================================================
# Test Helpers
# =============================================================================

class FixturesContext:
    """Context manager for tests that need temporary project fixtures."""

    def __init__(self):
        self.fixtures_dir = None

    def __enter__(self):
        self.fixtures_dir = Path(tempfile.mkdtemp())
        self._setup_fixtures()
        return self.fixtures_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.fixtures_dir, ignore_errors=True)

    def _setup_fixtures(self):
        """Create test project fixtures."""
        fixtures = self.fixtures_dir

        # Maven project
        (fixtures / 'maven-project').mkdir()
        (fixtures / 'maven-project' / 'pom.xml').write_text('<project></project>')

        # Gradle project (Kotlin DSL)
        (fixtures / 'gradle-project').mkdir()
        (fixtures / 'gradle-project' / 'build.gradle.kts').write_text('plugins { java }')

        # Gradle project (Groovy DSL)
        (fixtures / 'gradle-groovy-project').mkdir()
        (fixtures / 'gradle-groovy-project' / 'build.gradle').write_text('plugins { id "java" }')

        # npm project
        (fixtures / 'npm-project').mkdir()
        (fixtures / 'npm-project' / 'package.json').write_text('{"name": "test", "version": "1.0.0"}')

        # Mixed Maven + npm project
        (fixtures / 'mixed-maven-npm').mkdir()
        (fixtures / 'mixed-maven-npm' / 'pom.xml').write_text('<project></project>')
        (fixtures / 'mixed-maven-npm' / 'package.json').write_text('{"name": "frontend"}')

        # Mixed Gradle + npm project
        (fixtures / 'mixed-gradle-npm').mkdir()
        (fixtures / 'mixed-gradle-npm' / 'build.gradle.kts').write_text('plugins { java }')
        (fixtures / 'mixed-gradle-npm' / 'package.json').write_text('{"name": "frontend"}')

        # Empty project (no build files)
        (fixtures / 'empty-project').mkdir()

        # Settings-only Gradle project
        (fixtures / 'gradle-settings-only').mkdir()
        (fixtures / 'gradle-settings-only' / 'settings.gradle.kts').write_text('rootProject.name = "test"')


# Shared fixtures context for all tests
_fixtures = None


def setup_module():
    """Setup fixtures before running tests."""
    global _fixtures
    _fixtures = FixturesContext()
    _fixtures.__enter__()


def teardown_module():
    """Cleanup fixtures after tests."""
    global _fixtures
    if _fixtures:
        _fixtures.__exit__(None, None, None)


def get_fixtures_dir():
    """Get the fixtures directory."""
    return _fixtures.fixtures_dir


# =============================================================================
# Tests
# =============================================================================

def test_maven_project_detection():
    """Test Maven project detection."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'maven-project')
    )
    data = result.json()

    assert data.get('available_systems') == 'maven', "Maven detected as available"
    assert data.get('default_system') == 'maven', "Maven is default"


def test_gradle_kotlin_dsl_detection():
    """Test Gradle project detection (Kotlin DSL)."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'gradle-project')
    )
    data = result.json()

    assert data.get('available_systems') == 'gradle', "Gradle detected as available"
    assert data.get('default_system') == 'gradle', "Gradle is default"


def test_gradle_groovy_dsl_detection():
    """Test Gradle project detection (Groovy DSL)."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'gradle-groovy-project')
    )
    data = result.json()

    assert data.get('available_systems') == 'gradle', "Gradle (Groovy) detected"
    assert data.get('default_system') == 'gradle', "Gradle (Groovy) is default"


def test_npm_project_detection():
    """Test npm project detection."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'npm-project')
    )
    data = result.json()

    assert data.get('available_systems') == 'npm', "npm detected as available"
    assert data.get('default_system') == 'npm', "npm is default"


def test_mixed_maven_npm_project():
    """Test mixed Maven + npm project detection."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'mixed-maven-npm')
    )
    data = result.json()

    assert data.get('available_systems') == 'maven,npm', "Both Maven and npm detected"
    assert data.get('default_system') == 'maven', "Maven has priority over npm"


def test_mixed_gradle_npm_project():
    """Test mixed Gradle + npm project detection."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'mixed-gradle-npm')
    )
    data = result.json()

    assert data.get('available_systems') == 'gradle,npm', "Both Gradle and npm detected"
    assert data.get('default_system') == 'gradle', "Gradle has priority over npm"


def test_empty_project():
    """Test empty project (no build files)."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'empty-project')
    )
    data = result.json()

    assert data.get('available_systems') == '', "No systems detected"
    assert data.get('default_system') == '', "No default system"
    assert 'No build systems detected' in result.stdout, "Correct message for empty project"


def test_gradle_settings_only_project():
    """Test Gradle settings-only project detection."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'gradle-settings-only')
    )
    data = result.json()

    assert data.get('available_systems') == 'gradle', "Gradle detected from settings file"


def test_simple_output_format():
    """Test simple output format."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        '--project-dir', str(fixtures / 'maven-project'),
        '--format', 'simple'
    )

    assert 'available_systems=maven' in result.stdout, "Simple format shows available_systems"
    assert 'default_system=maven' in result.stdout, "Simple format shows default_system"


def test_help_flag():
    """Test --help flag."""
    result = run_script(SCRIPT_PATH, '--help')

    assert 'project-dir' in result.stdout, "Help shows project-dir option"
    assert 'format' in result.stdout, "Help shows format option"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    setup_module()
    try:
        runner = TestRunner()
        runner.add_tests([
            test_maven_project_detection,
            test_gradle_kotlin_dsl_detection,
            test_gradle_groovy_dsl_detection,
            test_npm_project_detection,
            test_mixed_maven_npm_project,
            test_mixed_gradle_npm_project,
            test_empty_project,
            test_gradle_settings_only_project,
            test_simple_output_format,
            test_help_flag,
        ])
        sys.exit(runner.run())
    finally:
        teardown_module()
