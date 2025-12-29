#!/usr/bin/env python3
"""Tests for canonical command lookup API in build-env.py.

Tests lookup, get-available-commands, and validate-required subcommands.
"""

import json
import sys
import shutil
import tempfile
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
# Test Fixtures
# =============================================================================

class LookupFixturesContext:
    """Context manager for tests that need multiple project fixtures.

    Creates a fixtures directory with several pre-configured projects
    for testing lookup, validation, and command listing.
    """

    def __init__(self):
        self.fixtures_dir = None

    def __enter__(self):
        self.fixtures_dir = Path(tempfile.mkdtemp())
        self._setup_fixtures()
        return self.fixtures_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.fixtures_dir, ignore_errors=True)

    def _setup_fixtures(self):
        """Create test project fixtures with marshal.json configurations."""
        fixtures = self.fixtures_dir

        # Single build system project (Maven)
        single_bs = fixtures / 'single-build-system'
        single_bs.mkdir()
        (single_bs / 'pom.xml').write_text('<project></project>')
        create_marshal_json(single_bs, module_config={
            "default": {
                "path": ".",
                "domains": ["java"],
                "build_systems": ["maven"],
                "type": "jar",
                "commands": {
                    "module-tests": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\"",
                    "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\"",
                    "quality-gate": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\""
                }
            },
            "core": {
                "path": "core",
                "domains": ["java"],
                "build_systems": ["maven"],
                "type": "jar",
                "commands": {
                    "module-tests": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\" --module core",
                    "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\" --module core"
                }
            }
        })

        # Hybrid module project (Maven + npm)
        hybrid = fixtures / 'hybrid-project'
        hybrid.mkdir()
        (hybrid / 'pom.xml').write_text('<project></project>')
        (hybrid / 'package.json').write_text('{"name": "hybrid"}')
        create_marshal_json(hybrid, module_config={
            "default": {
                "path": ".",
                "domains": ["java", "javascript"],
                "build_systems": ["maven", "npm"],
                "type": "jar",
                "commands": {
                    "module-tests": {
                        "maven": {
                            "command": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\"",
                            "source": "core"
                        },
                        "npm": {
                            "command": "python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command \"run test\"",
                            "source": "core"
                        }
                    },
                    "verify": {
                        "maven": {
                            "command": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\"",
                            "source": "core"
                        }
                    }
                }
            }
        })

        # POM-only module project
        pom_only = fixtures / 'pom-only-project'
        pom_only.mkdir()
        (pom_only / 'pom.xml').write_text('<project><packaging>pom</packaging></project>')
        create_marshal_json(pom_only, module_config={
            "bom": {
                "path": "bom",
                "domains": [],
                "build_systems": ["maven"],
                "type": "pom",
                "commands": {
                    "install": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"install\" --module bom"
                }
            }
        })

        # Empty project (no marshal.json)
        empty = fixtures / 'empty-project'
        empty.mkdir()
        plan_dir = empty / '.plan'
        plan_dir.mkdir()


# Shared fixtures context for all tests
_fixtures = None


def setup_module():
    """Setup fixtures before running tests."""
    global _fixtures
    _fixtures = LookupFixturesContext()
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
# LOOKUP Subcommand Tests
# =============================================================================

def test_lookup_single_build_system():
    """Test lookup for single build system module."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'lookup',
        '--canonical', 'module-tests',
        '--module', 'default',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert result.success, f"lookup should succeed: {result.stderr}"
    assert 'maven' in result.stdout, "Command should reference maven"
    assert 'clean test' in result.stdout, "Command should contain clean test goals"


def test_lookup_with_module_name():
    """Test lookup with specific module name."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'lookup',
        '--canonical', 'module-tests',
        '--module', 'core',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert result.success, f"lookup should succeed: {result.stderr}"
    assert '--module core' in result.stdout, "Command should include module flag"


def test_lookup_missing_command():
    """Test lookup returns error for missing command."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'lookup',
        '--canonical', 'integration-tests',
        '--module', 'default',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert not result.success, "lookup should fail for missing command"
    assert "not found" in result.stderr.lower(), "Error message should indicate not found"


def test_lookup_missing_module():
    """Test lookup returns error for missing module."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'lookup',
        '--canonical', 'module-tests',
        '--module', 'nonexistent',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert not result.success, "lookup should fail for missing module"
    assert "available modules" in result.stderr.lower(), "Error should list available modules"


def test_lookup_hybrid_without_filter():
    """Test lookup for hybrid module without build system filter."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'lookup',
        '--canonical', 'module-tests',
        '--module', 'default',
        '--project-dir', str(fixtures / 'hybrid-project')
    )

    # Should return ambiguous status with both build systems
    assert not result.success, "lookup should return non-zero for ambiguous"
    assert "ambiguous" in result.stdout.lower() or "multiple build systems" in result.stdout.lower(), \
        f"Should indicate ambiguity: {result.stdout}"


def test_lookup_hybrid_with_filter():
    """Test lookup for hybrid module with build system filter."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'lookup',
        '--canonical', 'module-tests',
        '--module', 'default',
        '--build-system', 'maven',
        '--project-dir', str(fixtures / 'hybrid-project')
    )

    assert result.success, f"lookup with filter should succeed: {result.stderr}"
    assert 'maven' in result.stdout, "Command should reference maven"


def test_lookup_no_marshal_json():
    """Test lookup with missing marshal.json."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'lookup',
        '--canonical', 'module-tests',
        '--module', 'default',
        '--project-dir', str(fixtures / 'empty-project')
    )

    assert not result.success, "lookup should fail without marshal.json"
    assert "marshal.json" in result.stderr, "Error should mention marshal.json"


# =============================================================================
# GET-AVAILABLE-COMMANDS Subcommand Tests
# =============================================================================

def test_get_available_commands_success():
    """Test get-available-commands returns correct list."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'get-available-commands',
        '--module', 'default',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert result.success, f"get-available-commands should succeed: {result.stderr}"
    assert "module-tests" in result.stdout, "Should list module-tests"
    assert "verify" in result.stdout, "Should list verify"
    assert "quality-gate" in result.stdout, "Should list quality-gate"


def test_get_available_commands_missing_module():
    """Test get-available-commands for missing module."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'get-available-commands',
        '--module', 'nonexistent',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert not result.success, "Should fail for missing module"
    assert "not found" in result.stderr.lower(), "Error should indicate not found"


def test_get_available_commands_pom_only():
    """Test get-available-commands for pom-only module."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'get-available-commands',
        '--module', 'bom',
        '--project-dir', str(fixtures / 'pom-only-project')
    )

    assert result.success, f"Should succeed: {result.stderr}"
    assert "install" in result.stdout, "Should list install"
    # pom-only modules typically only have install
    assert "count: 1" in result.stdout, "Should have 1 command"


# =============================================================================
# VALIDATE-REQUIRED Subcommand Tests
# =============================================================================

def test_validate_required_all_present():
    """Test validate-required when all required commands are present."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'validate-required',
        '--module', 'default',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert result.success, f"Should succeed when all required present: {result.stderr}"
    assert "success" in result.stdout.lower(), "Status should be success"


def test_validate_required_with_all_static_commands():
    """Test validate-required succeeds when static commands present.

    The 'core' module fixture has module-tests and verify (static commands).
    quality-gate is profile-based and not required for validation.
    """
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'validate-required',
        '--module', 'core',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    # core module has module-tests and verify which are the required static commands
    # quality-gate is profile-based and not strictly required
    assert result.success, f"Should succeed with static commands: {result.stdout}"
    assert 'success' in result.stdout.lower(), "Should indicate success"


def test_validate_required_pom_module():
    """Test validate-required for pom-only module.

    pom modules only require install (static command).
    quality-gate is profile-based and not strictly required.
    """
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'validate-required',
        '--module', 'bom',
        '--project-dir', str(fixtures / 'pom-only-project')
    )

    # pom modules only require install (static), quality-gate is profile-based
    # bom has install, so it should succeed
    assert result.success, f"Should succeed with install for pom: {result.stdout}"


def test_validate_required_missing_module():
    """Test validate-required for missing module."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'validate-required',
        '--module', 'nonexistent',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    assert not result.success, "Should fail for missing module"


# =============================================================================
# PERSIST --minimal Tests
# =============================================================================

def test_persist_minimal_only_required():
    """Test persist --minimal only generates required static commands.

    In minimal mode, only required static commands are generated.
    Profile-based commands require explicit --include-profiles.
    """
    with BuildTestContext() as ctx:
        # Create a Maven jar project (no profiles needed for static commands)
        ctx.create_pom(packaging='jar')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--minimal',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.success, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # Required static commands should be present
        assert 'module-tests' in commands, "Should have module-tests (required static)"
        assert 'verify' in commands, "Should have verify (required static)"

        # Profile-based commands NOT present without --include-profiles
        assert 'quality-gate' not in commands, "quality-gate requires --include-profiles in minimal mode"

        # Non-required commands should NOT be present
        assert 'compile' not in commands, "Should NOT have compile (not required)"
        assert 'install' not in commands, "Should NOT have install (not required)"


def test_persist_minimal_with_include_profiles():
    """Test persist --minimal with --include-profiles adds selected profiles."""
    with BuildTestContext() as ctx:
        # Create a Maven jar project with profiles
        ctx.create_pom(profiles=['pre-commit', 'coverage', 'integration-tests'])

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--minimal',
            '--include-profiles', 'default:coverage',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.success, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # Required static commands should be present
        assert 'module-tests' in commands, "Should have module-tests (required static)"
        assert 'verify' in commands, "Should have verify (required static)"
        # Note: quality-gate is profile-based and requires matching profile (pre-commit)
        # but in minimal mode, only explicitly included profiles are added

        # Included profile should be present
        assert 'coverage' in commands, "Should have coverage (explicitly included)"

        # Non-included profile should NOT be present
        assert 'integration-tests' not in commands, "Should NOT have integration-tests (not included)"


def test_persist_include_profiles_filter():
    """Test persist --minimal with --include-profiles filters to selected profiles only."""
    with BuildTestContext() as ctx:
        # Create a Maven jar project with multiple profiles
        ctx.create_pom(profiles=['coverage', 'integration-tests', 'benchmark'])

        # Use --minimal with --include-profiles to control which commands are generated
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--minimal',
            '--include-profiles', 'default:coverage,default:integration-tests',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.success, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # Required static commands should be present (from --minimal base)
        assert 'module-tests' in commands, "Should have module-tests (required static)"
        assert 'verify' in commands, "Should have verify (required static)"
        # Note: quality-gate is profile-based and not in --include-profiles filter

        # Included profiles should be present
        assert 'coverage' in commands, "Should have coverage (explicitly included)"
        assert 'integration-tests' in commands, "Should have integration-tests (explicitly included)"

        # Non-included profile should NOT be present (benchmark maps to performance)
        assert 'performance' not in commands, "Should NOT have performance (benchmark not included)"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    setup_module()
    try:
        runner = TestRunner()
        runner.add_tests([
            # Lookup tests
            test_lookup_single_build_system,
            test_lookup_with_module_name,
            test_lookup_missing_command,
            test_lookup_missing_module,
            test_lookup_hybrid_without_filter,
            test_lookup_hybrid_with_filter,
            test_lookup_no_marshal_json,
            # Get-available-commands tests
            test_get_available_commands_success,
            test_get_available_commands_missing_module,
            test_get_available_commands_pom_only,
            # Validate-required tests
            test_validate_required_all_present,
            test_validate_required_with_all_static_commands,
            test_validate_required_pom_module,
            test_validate_required_missing_module,
            # Minimal mode tests
            test_persist_minimal_only_required,
            test_persist_minimal_with_include_profiles,
            test_persist_include_profiles_filter,
        ])
        sys.exit(runner.run())
    finally:
        teardown_module()
