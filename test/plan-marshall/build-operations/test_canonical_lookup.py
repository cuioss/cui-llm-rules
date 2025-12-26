#!/usr/bin/env python3
"""Tests for canonical command lookup API in build-env.py.

Tests lookup, get-available-commands, and validate-required subcommands.
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

class LookupFixturesContext:
    """Context manager for tests that need marshal.json fixtures."""

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
        plan_dir = single_bs / '.plan'
        plan_dir.mkdir()
        (plan_dir / 'marshal.json').write_text(json.dumps({
            "modules": {
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
            }
        }, indent=2))

        # Hybrid module project (Maven + npm)
        hybrid = fixtures / 'hybrid-project'
        hybrid.mkdir()
        (hybrid / 'pom.xml').write_text('<project></project>')
        (hybrid / 'package.json').write_text('{"name": "hybrid"}')
        plan_dir = hybrid / '.plan'
        plan_dir.mkdir()
        (plan_dir / 'marshal.json').write_text(json.dumps({
            "modules": {
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
            }
        }, indent=2))

        # POM-only module project
        pom_only = fixtures / 'pom-only-project'
        pom_only.mkdir()
        (pom_only / 'pom.xml').write_text('<project><packaging>pom</packaging></project>')
        plan_dir = pom_only / '.plan'
        plan_dir.mkdir()
        (plan_dir / 'marshal.json').write_text(json.dumps({
            "modules": {
                "bom": {
                    "path": "bom",
                    "domains": [],
                    "build_systems": ["maven"],
                    "type": "pom",
                    "commands": {
                        "install": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"install\" --module bom"
                    }
                }
            }
        }, indent=2))

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


def test_validate_required_missing_commands():
    """Test validate-required detects missing commands."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'validate-required',
        '--module', 'core',
        '--project-dir', str(fixtures / 'single-build-system')
    )

    # core module is missing quality-gate which is required for jar type
    assert not result.success, "Should fail when required commands missing"
    assert "incomplete" in result.stdout.lower() or "missing" in result.stdout.lower(), \
        f"Should indicate incomplete: {result.stdout}"
    assert "quality-gate" in result.stdout, "Should list quality-gate as missing"


def test_validate_required_pom_module():
    """Test validate-required for pom-only module."""
    fixtures = get_fixtures_dir()
    result = run_script(
        SCRIPT_PATH,
        'validate-required',
        '--module', 'bom',
        '--project-dir', str(fixtures / 'pom-only-project')
    )

    # pom modules have different required commands (only quality-gate is required for pom)
    # Since bom only has install, it should be missing quality-gate
    assert not result.success or "quality-gate" in result.stdout, \
        "Should either succeed or show quality-gate as missing"


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

class MinimalModeContext:
    """Context manager for minimal mode tests."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        (self.temp_dir / '.plan').mkdir()
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def test_persist_minimal_only_required():
    """Test persist --minimal only generates required commands."""
    with MinimalModeContext() as temp_dir:
        # Create a Maven jar project
        (temp_dir / 'pom.xml').write_text('<project><packaging>jar</packaging></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--minimal',
            '--project-dir', str(temp_dir)
        )

        assert result.success, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        # Required commands should be present
        assert 'module-tests' in commands, "Should have module-tests (required)"
        assert 'quality-gate' in commands, "Should have quality-gate (required)"
        assert 'verify' in commands, "Should have verify (required)"

        # Non-required commands should NOT be present
        assert 'compile' not in commands, "Should NOT have compile (not required)"
        assert 'install' not in commands, "Should NOT have install (not required)"


def test_persist_minimal_with_include_profiles():
    """Test persist --minimal with --include-profiles adds selected profiles."""
    with MinimalModeContext() as temp_dir:
        # Create a Maven jar project with a profile
        pom_content = '''<project>
            <packaging>jar</packaging>
            <profiles>
                <profile>
                    <id>coverage</id>
                </profile>
                <profile>
                    <id>integration-tests</id>
                </profile>
            </profiles>
        </project>'''
        (temp_dir / 'pom.xml').write_text(pom_content)

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--minimal',
            '--include-profiles', 'default:coverage',
            '--project-dir', str(temp_dir)
        )

        assert result.success, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        # Required commands should be present
        assert 'module-tests' in commands, "Should have module-tests (required)"
        assert 'quality-gate' in commands, "Should have quality-gate (required)"
        assert 'verify' in commands, "Should have verify (required)"

        # Included profile should be present
        assert 'coverage' in commands, "Should have coverage (explicitly included)"

        # Non-included profile should NOT be present
        assert 'integration-tests' not in commands, "Should NOT have integration-tests (not included)"


def test_persist_include_profiles_filter():
    """Test persist --minimal with --include-profiles filters to selected profiles only."""
    with MinimalModeContext() as temp_dir:
        # Create a Maven jar project with multiple profiles
        pom_content = '''<project>
            <packaging>jar</packaging>
            <profiles>
                <profile><id>coverage</id></profile>
                <profile><id>integration-tests</id></profile>
                <profile><id>benchmark</id></profile>
            </profiles>
        </project>'''
        (temp_dir / 'pom.xml').write_text(pom_content)

        # Use --minimal with --include-profiles to control which commands are generated
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--minimal',
            '--include-profiles', 'default:coverage,default:integration-tests',
            '--project-dir', str(temp_dir)
        )

        assert result.success, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        # Required commands should be present (from --minimal base)
        assert 'module-tests' in commands, "Should have module-tests (required)"
        assert 'quality-gate' in commands, "Should have quality-gate (required)"
        assert 'verify' in commands, "Should have verify (required)"

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
            test_validate_required_missing_commands,
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
