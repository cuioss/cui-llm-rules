#!/usr/bin/env python3
"""Tests for extension discovery in build_env.py.

Tests:
- Extension discovery finds pm-dev-java and pm-dev-frontend
- is_applicable() correctly filters bundles
- get_command_mappings() returns correct templates
- Placeholder resolution
"""

import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'extension-api', 'build_env.py')


# =============================================================================
# Test Helpers
# =============================================================================

class ExtensionTestContext:
    """Context manager for extension discovery tests."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        (self.temp_dir / '.plan').mkdir()
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Extension Discovery Tests
# =============================================================================

def test_discovers_java_extension():
    """Test that pm-dev-java extension is discovered for Maven projects."""
    with ExtensionTestContext() as temp_dir:
        # Create pom.xml to trigger Java detection
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Should have maven commands from pm-dev-java extension
        commands = config['modules']['default']['commands']
        assert 'module-tests' in commands, "Should have module-tests command"
        assert 'pm-dev-java:plan-marshall-plugin:maven' in commands['module-tests'], \
            f"Should use pm-dev-java script: {commands['module-tests']}"


def test_discovers_frontend_extension():
    """Test that pm-dev-frontend extension is discovered for npm projects."""
    with ExtensionTestContext() as temp_dir:
        # Create package.json to trigger frontend detection
        (temp_dir / 'package.json').write_text('{"name": "test", "version": "1.0.0"}')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Should have npm commands from pm-dev-frontend extension
        commands = config['modules']['default']['commands']
        assert 'module-tests' in commands, "Should have module-tests command"
        assert 'pm-dev-frontend:plan-marshall-plugin:npm' in commands['module-tests'], \
            f"Should use pm-dev-frontend script: {commands['module-tests']}"


def test_discovers_gradle_extension():
    """Test that pm-dev-java extension is discovered for Gradle projects."""
    with ExtensionTestContext() as temp_dir:
        # Create build.gradle to trigger Gradle detection
        (temp_dir / 'build.gradle').write_text('plugins { id "java" }')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Should have gradle commands from pm-dev-java extension
        commands = config['modules']['default']['commands']
        assert 'module-tests' in commands, "Should have module-tests command"
        assert 'pm-dev-java:plan-marshall-plugin:gradle' in commands['module-tests'], \
            f"Should use pm-dev-java gradle script: {commands['module-tests']}"


def test_discovers_multiple_extensions():
    """Test that multiple extensions are discovered for hybrid projects."""
    with ExtensionTestContext() as temp_dir:
        # Create both pom.xml and package.json
        (temp_dir / 'pom.xml').write_text('<project></project>')
        (temp_dir / 'package.json').write_text('{"name": "test", "version": "1.0.0"}')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Should have both build systems
        build_systems = config['modules']['default']['build_systems']
        assert 'maven' in build_systems, "Should detect maven"
        assert 'npm' in build_systems, "Should detect npm"


# =============================================================================
# is_applicable Tests
# =============================================================================

def test_java_not_applicable_without_build_files():
    """Test that Java extension is not applied without Maven/Gradle files."""
    with ExtensionTestContext() as temp_dir:
        # Create package.json only
        (temp_dir / 'package.json').write_text('{"name": "test"}')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Should only have npm, not maven/gradle
        build_systems = config['modules']['default']['build_systems']
        assert 'maven' not in build_systems, "Should not detect maven"
        assert 'gradle' not in build_systems, "Should not detect gradle"
        assert 'npm' in build_systems, "Should detect npm"


def test_frontend_not_applicable_without_package_json():
    """Test that frontend extension is not applied without package.json."""
    with ExtensionTestContext() as temp_dir:
        # Create pom.xml only
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Should only have maven, not npm
        build_systems = config['modules']['default']['build_systems']
        assert 'maven' in build_systems, "Should detect maven"
        assert 'npm' not in build_systems, "Should not detect npm"


# =============================================================================
# get_command_mappings Tests
# =============================================================================

def test_command_mappings_include_run_subcommand():
    """Test that command mappings use 'run' subcommand."""
    with ExtensionTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        commands = config['modules']['default']['commands']
        module_tests = commands['module-tests']

        # Should use 'run' subcommand (not 'execute')
        assert 'maven run' in module_tests, f"Should use 'maven run': {module_tests}"


def test_command_mappings_include_execute_script_prefix():
    """Test that command mappings include execute-script.py prefix."""
    with ExtensionTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        commands = config['modules']['default']['commands']
        module_tests = commands['module-tests']

        # Should include execute-script.py prefix
        assert 'python3 .plan/execute-script.py' in module_tests, \
            f"Should use execute-script.py: {module_tests}"


# =============================================================================
# Placeholder Resolution Tests
# =============================================================================

def test_module_placeholder_resolved_for_default():
    """Test that {module} placeholder is resolved to empty for default module."""
    with ExtensionTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        commands = config['modules']['default']['commands']
        module_tests = commands['module-tests']

        # Should not contain unresolved placeholder
        assert '{module}' not in module_tests, f"Placeholder should be resolved: {module_tests}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_discovers_java_extension,
        test_discovers_frontend_extension,
        test_discovers_gradle_extension,
        test_discovers_multiple_extensions,
        test_java_not_applicable_without_build_files,
        test_frontend_not_applicable_without_package_json,
        test_command_mappings_include_run_subcommand,
        test_command_mappings_include_execute_script_prefix,
        test_module_placeholder_resolved_for_default,
    ])
    sys.exit(runner.run())
