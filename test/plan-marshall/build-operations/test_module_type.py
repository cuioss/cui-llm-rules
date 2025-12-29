#!/usr/bin/env python3
"""Tests for module type detection in build-env.py.

Tests detect-module-type subcommand and module type filtering in persist.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    run_script, TestRunner, get_script_path,
    BuildTestContext, create_marshal_json, MARSHAL_KEY_MODULE_CONFIG
)

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'extension-api', 'build_env.py')


# =============================================================================
# detect-module-type Tests - Maven
# =============================================================================

def test_detect_type_maven_jar():
    """Test detect-module-type for jar packaging (default)."""
    with BuildTestContext() as ctx:
        ctx.create_pom()  # Default is jar

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: jar' in result.stdout, "Should detect jar type"


def test_detect_type_maven_pom():
    """Test detect-module-type for pom packaging."""
    with BuildTestContext() as ctx:
        ctx.create_pom(packaging='pom')

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: pom' in result.stdout, "Should detect pom type"


def test_detect_type_maven_war():
    """Test detect-module-type for war packaging."""
    with BuildTestContext() as ctx:
        ctx.create_pom(packaging='war')

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: war' in result.stdout, "Should detect war type"


def test_detect_type_maven_quarkus():
    """Test detect-module-type for Quarkus project."""
    with BuildTestContext() as ctx:
        ctx.create_pom(with_quarkus=True)

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: quarkus' in result.stdout, "Should detect quarkus type"


# =============================================================================
# detect-module-type Tests - Gradle
# =============================================================================

def test_detect_type_gradle_jar():
    """Test detect-module-type for Gradle jar project."""
    with BuildTestContext() as ctx:
        ctx.create_build_gradle()

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: jar' in result.stdout, "Should detect jar type"


def test_detect_type_gradle_war():
    """Test detect-module-type for Gradle war project."""
    with BuildTestContext() as ctx:
        ctx.create_build_gradle(with_war=True)

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: war' in result.stdout, "Should detect war type"


def test_detect_type_gradle_quarkus():
    """Test detect-module-type for Gradle Quarkus project."""
    with BuildTestContext() as ctx:
        ctx.create_build_gradle(with_quarkus=True, kotlin=True)

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: quarkus' in result.stdout, "Should detect quarkus type"


# =============================================================================
# detect-module-type Tests - npm
# =============================================================================

def test_detect_type_npm():
    """Test detect-module-type for npm project."""
    with BuildTestContext() as ctx:
        ctx.create_package_json()

        result = run_script(
            SCRIPT_PATH,
            'detect-module-type',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'type: npm' in result.stdout, "Should detect npm type"


# =============================================================================
# persist Tests - Command Filtering by Type
# =============================================================================

def test_persist_pom_only_gets_limited_commands():
    """Test persist generates only applicable commands for pom module type."""
    with BuildTestContext() as ctx:
        # pom module with a quality profile to get quality-gate command
        ctx.create_pom(packaging='pom', profiles=['pre-commit'])

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # pom modules should only have install and quality-gate (from profile)
        assert 'install' in commands, "pom should have install"
        assert 'quality-gate' in commands, "pom should have quality-gate (from profile)"
        assert 'module-tests' not in commands, "pom should NOT have module-tests"
        assert 'verify' not in commands, "pom should NOT have verify"


def test_persist_jar_gets_all_commands():
    """Test persist generates all commands for jar module type."""
    with BuildTestContext() as ctx:
        # jar module with profiles to get profile-based commands
        ctx.create_pom(profiles=['pre-commit'])

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # jar modules should have most commands (static + profile-based)
        assert 'module-tests' in commands, "jar should have module-tests"
        assert 'verify' in commands, "jar should have verify"
        assert 'quality-gate' in commands, "jar should have quality-gate (from profile)"
        assert 'install' in commands, "jar should have install"


def test_persist_sets_type_field():
    """Test persist sets type field in module config."""
    with BuildTestContext() as ctx:
        ctx.create_pom(packaging='war')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        assert config[MARSHAL_KEY_MODULE_CONFIG]['default']['type'] == 'war', "Should set type to war"


def test_persist_output_includes_type():
    """Test persist output includes type column."""
    with BuildTestContext() as ctx:
        ctx.create_pom()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        # Output format: modules[N]{name,path,type,commands_count}:
        assert 'name,path,type,commands_count' in result.stdout, "Output should include type column"
        assert 'jar' in result.stdout, "Output should show jar type"


# =============================================================================
# validate-required Tests with Type
# =============================================================================

def test_validate_required_pom_module():
    """Test validate-required with pom module type.

    pom modules only require install (static) and optionally quality-gate (profile-based).
    Since quality-gate is profile-based, it's not considered 'required' for validation.
    """
    with BuildTestContext() as ctx:
        ctx.create_pom(packaging='pom')

        # Create marshal.json with pom config that has install
        create_marshal_json(ctx.temp_dir, module_config={
            "default": {
                "path": ".",
                "type": "pom",
                "build_systems": ["maven"],
                "commands": {
                    "install": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"install\""
                }
            }
        })

        result = run_script(
            SCRIPT_PATH,
            'validate-required',
            '--module', 'default',
            '--project-dir', str(ctx.temp_dir)
        )

        # pom modules only require install (static command), quality-gate is profile-based
        assert result.returncode == 0, f"Should succeed with install for pom: {result.stdout}"
        assert 'status: success' in result.stdout, "Should report success"


def test_validate_required_jar_missing_commands():
    """Test validate-required detects missing static commands for jar type.

    jar modules require module-tests and verify (static commands).
    quality-gate is profile-based and not checked here.
    """
    with BuildTestContext() as ctx:
        ctx.create_pom()

        # Create marshal.json with jar config missing required static commands
        create_marshal_json(ctx.temp_dir, module_config={
            "default": {
                "path": ".",
                "type": "jar",
                "build_systems": ["maven"],
                "commands": {
                    "install": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean install\""
                }
            }
        })

        result = run_script(
            SCRIPT_PATH,
            'validate-required',
            '--module', 'default',
            '--project-dir', str(ctx.temp_dir)
        )

        # jar modules require module-tests and verify (static commands)
        assert result.returncode != 0, "Should fail with missing required commands"
        assert 'incomplete' in result.stdout.lower() or 'missing' in result.stdout.lower(), \
            f"Should indicate incomplete: {result.stdout}"
        # Should list the missing static commands
        assert 'module-tests' in result.stdout or 'verify' in result.stdout, \
            f"Should list missing static commands: {result.stdout}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Maven type detection
        test_detect_type_maven_jar,
        test_detect_type_maven_pom,
        test_detect_type_maven_war,
        test_detect_type_maven_quarkus,
        # Gradle type detection
        test_detect_type_gradle_jar,
        test_detect_type_gradle_war,
        test_detect_type_gradle_quarkus,
        # npm type detection
        test_detect_type_npm,
        # persist command filtering
        test_persist_pom_only_gets_limited_commands,
        test_persist_jar_gets_all_commands,
        test_persist_sets_type_field,
        test_persist_output_includes_type,
        # validate-required with type
        test_validate_required_pom_module,
        test_validate_required_jar_missing_commands,
    ])
    sys.exit(runner.run())
