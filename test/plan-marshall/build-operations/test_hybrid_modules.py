#!/usr/bin/env python3
"""Tests for hybrid module support in build-env.py.

Tests detect hybrid modules (Maven + npm), generate commands for each build system,
and verify lookup with and without build_system filter.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    run_script, TestRunner, get_script_path,
    BuildTestContext, MARSHAL_KEY_MODULE_CONFIG
)

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'extension-api', 'build_env.py')


# =============================================================================
# Hybrid Detection Tests
# =============================================================================

def test_detect_hybrid_maven_npm():
    """Test detection of hybrid module with Maven + npm."""
    with BuildTestContext() as ctx:
        # Create both pom.xml and package.json
        ctx.create_pom()
        ctx.create_package_json()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()

        # Should detect both build systems
        build_systems = config[MARSHAL_KEY_MODULE_CONFIG]['default']['build_systems']
        assert 'maven' in build_systems, "Should detect maven"
        assert 'npm' in build_systems, "Should detect npm"
        assert len(build_systems) == 2, f"Should have exactly 2 build systems: {build_systems}"


def test_detect_hybrid_gradle_npm():
    """Test detection of hybrid module with Gradle + npm."""
    with BuildTestContext() as ctx:
        # Create both build.gradle and package.json
        ctx.create_build_gradle()
        ctx.create_package_json()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()

        # Should detect both build systems
        build_systems = config[MARSHAL_KEY_MODULE_CONFIG]['default']['build_systems']
        assert 'gradle' in build_systems, "Should detect gradle"
        assert 'npm' in build_systems, "Should detect npm"


def test_non_hybrid_single_system():
    """Test that single build system is not detected as hybrid."""
    with BuildTestContext() as ctx:
        # Only pom.xml
        ctx.create_pom()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()

        # Should have only one build system
        build_systems = config[MARSHAL_KEY_MODULE_CONFIG]['default']['build_systems']
        assert len(build_systems) == 1, f"Should have only 1 build system: {build_systems}"
        assert 'maven' in build_systems, "Should detect maven only"


# =============================================================================
# Hybrid Command Generation Tests
# =============================================================================

def test_hybrid_commands_nested_format():
    """Test that hybrid module commands are in nested format."""
    with BuildTestContext() as ctx:
        # Create hybrid module
        ctx.create_pom()
        ctx.create_package_json()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # module-tests should be present for both build systems
        assert 'module-tests' in commands, "Should have module-tests command"

        module_tests = commands['module-tests']
        assert isinstance(module_tests, dict), "module-tests should be a dict for hybrid"
        assert 'maven' in module_tests, "module-tests should have maven entry"
        assert 'npm' in module_tests, "module-tests should have npm entry"


def test_hybrid_commands_have_correct_content():
    """Test that hybrid commands have correct content for each build system."""
    with BuildTestContext() as ctx:
        # Create hybrid module
        ctx.create_pom()
        ctx.create_package_json()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        module_tests = commands['module-tests']

        # Check maven command (now uses 'run' as primary API, not 'execute')
        maven_cmd = module_tests['maven']
        assert 'maven run' in maven_cmd, f"Maven cmd should use maven run: {maven_cmd}"
        assert 'clean test' in maven_cmd, f"Maven cmd should have clean test: {maven_cmd}"

        # Check npm command (now uses 'run' as primary API, not 'execute')
        npm_cmd = module_tests['npm']
        assert 'npm run' in npm_cmd, f"npm cmd should use npm run: {npm_cmd}"
        assert 'run test' in npm_cmd, f"npm cmd should have run test: {npm_cmd}"


def test_non_hybrid_commands_flat_format():
    """Test that non-hybrid module commands are in flat format."""
    with BuildTestContext() as ctx:
        # Single build system
        ctx.create_pom()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # module-tests should be a string (flat format)
        assert 'module-tests' in commands, "Should have module-tests command"
        module_tests = commands['module-tests']
        assert isinstance(module_tests, str), f"module-tests should be string for non-hybrid: {type(module_tests)}"


# =============================================================================
# Hybrid Lookup Tests
# =============================================================================

def test_lookup_hybrid_with_build_system_filter():
    """Test lookup for hybrid module with build_system filter returns single command."""
    with BuildTestContext() as ctx:
        # Create hybrid module
        ctx.create_pom()
        ctx.create_package_json()

        # Persist first
        run_script(SCRIPT_PATH, 'persist', '--project-dir', str(ctx.temp_dir))

        # Lookup with maven filter
        result = run_script(
            SCRIPT_PATH,
            'lookup',
            '--canonical', 'module-tests',
            '--module', 'default',
            '--build-system', 'maven',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        # Commands now use 'run' as primary API
        assert 'maven run' in result.stdout, f"Should return maven command: {result.stdout}"
        assert 'npm' not in result.stdout, f"Should not include npm: {result.stdout}"


def test_lookup_hybrid_with_npm_filter():
    """Test lookup for hybrid module with npm build_system filter."""
    with BuildTestContext() as ctx:
        # Create hybrid module
        ctx.create_pom()
        ctx.create_package_json()

        # Persist first
        run_script(SCRIPT_PATH, 'persist', '--project-dir', str(ctx.temp_dir))

        # Lookup with npm filter
        result = run_script(
            SCRIPT_PATH,
            'lookup',
            '--canonical', 'module-tests',
            '--module', 'default',
            '--build-system', 'npm',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        # Commands now use 'run' as primary API
        assert 'npm run' in result.stdout, f"Should return npm command: {result.stdout}"


def test_lookup_hybrid_without_filter_returns_ambiguous():
    """Test lookup for hybrid module without filter returns ambiguous status."""
    with BuildTestContext() as ctx:
        # Create hybrid module
        ctx.create_pom()
        ctx.create_package_json()

        # Persist first
        run_script(SCRIPT_PATH, 'persist', '--project-dir', str(ctx.temp_dir))

        # Lookup without filter
        result = run_script(
            SCRIPT_PATH,
            'lookup',
            '--canonical', 'module-tests',
            '--module', 'default',
            '--project-dir', str(ctx.temp_dir)
        )

        # Should return ambiguous status (exit code 1)
        assert result.returncode == 1, f"Should return ambiguous for hybrid without filter"
        assert 'ambiguous' in result.stdout.lower(), f"Should indicate ambiguous: {result.stdout}"


def test_lookup_non_hybrid_without_filter():
    """Test lookup for non-hybrid module without filter returns command directly."""
    with BuildTestContext() as ctx:
        # Single build system
        ctx.create_pom()

        # Persist first
        run_script(SCRIPT_PATH, 'persist', '--project-dir', str(ctx.temp_dir))

        # Lookup without filter
        result = run_script(
            SCRIPT_PATH,
            'lookup',
            '--canonical', 'module-tests',
            '--module', 'default',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        # Commands now use 'run' as primary API
        assert 'maven run' in result.stdout, f"Should return command: {result.stdout}"


# =============================================================================
# get-available-commands for Hybrid Tests
# =============================================================================

def test_get_available_commands_hybrid():
    """Test get-available-commands for hybrid module lists all commands."""
    with BuildTestContext() as ctx:
        # Create hybrid module
        ctx.create_pom()
        ctx.create_package_json()

        # Persist first
        run_script(SCRIPT_PATH, 'persist', '--project-dir', str(ctx.temp_dir))

        result = run_script(
            SCRIPT_PATH,
            'get-available-commands',
            '--module', 'default',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'module-tests' in result.stdout, "Should list module-tests"
        assert 'quality-gate' in result.stdout, "Should list quality-gate"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Hybrid detection tests
        test_detect_hybrid_maven_npm,
        test_detect_hybrid_gradle_npm,
        test_non_hybrid_single_system,
        # Command generation tests
        test_hybrid_commands_nested_format,
        test_hybrid_commands_have_correct_content,
        test_non_hybrid_commands_flat_format,
        # Lookup tests
        test_lookup_hybrid_with_build_system_filter,
        test_lookup_hybrid_with_npm_filter,
        test_lookup_hybrid_without_filter_returns_ambiguous,
        test_lookup_non_hybrid_without_filter,
        # get-available-commands
        test_get_available_commands_hybrid,
    ])
    sys.exit(runner.run())
