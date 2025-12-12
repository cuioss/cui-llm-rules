#!/usr/bin/env python3
"""Tests for plan-marshall-config.py script.

Tests the project-level infrastructure configuration management
for marshal.json including skill-domains, modules, build-systems,
system, plan, and init commands.
"""

import json
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, PlanTestContext

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'plan-marshall-config', 'plan-marshall-config.py')


# =============================================================================
# Test Helpers
# =============================================================================

def create_marshal_json(fixture_dir: Path, config: dict = None) -> Path:
    """Create marshal.json in fixture directory."""
    if config is None:
        config = {
            "skill_domains": {
                "java": {
                    "defaults": ["pm-dev-java:cui-java-core"],
                    "optionals": ["pm-dev-java:cui-java-cdi"]
                },
                "java-testing": {
                    "defaults": ["pm-dev-java:cui-java-unit-testing"],
                    "optionals": []
                }
            },
            "modules": {
                "my-core": {
                    "path": "my-core",
                    "domains": ["java"],
                    "build_systems": ["maven"]
                },
                "my-ui": {
                    "path": "my-ui",
                    "domains": ["java", "javascript"],
                    "build_systems": ["maven", "npm"],
                    "commands": {
                        "npm": {
                            "test": "custom:test"
                        }
                    }
                }
            },
            "build_systems": [
                {
                    "system": "maven",
                    "skill": "pm-dev-builder:builder-maven-rules",
                    "commands": {
                        "verify": "clean verify",
                        "test": "clean test"
                    }
                },
                {
                    "system": "npm",
                    "skill": "pm-dev-builder:builder-npm-rules",
                    "commands": {
                        "test": "run test",
                        "verify": "run test && run lint"
                    }
                }
            ],
            "system": {
                "retention": {
                    "logs_days": 1,
                    "archived_plans_days": 5,
                    "memory_days": 5,
                    "temp_on_maintenance": True
                }
            },
            "plan": {
                "defaults": {
                    "compatibility": "deprecations",
                    "commit_strategy": "phase-specific",
                    "create_pr": False,
                    "verification_required": True,
                    "branch_strategy": "direct"
                }
            }
        }
    marshal_path = fixture_dir / 'marshal.json'
    marshal_path.write_text(json.dumps(config, indent=2))
    return marshal_path


def parse_toon_output(output: str) -> dict:
    """Parse TOON output to dict (simplified parser for tests)."""
    result = {}
    lines = output.strip().split('\n')
    for line in lines:
        if ':' in line and not line.endswith(':'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Try to parse as JSON for lists/bools/numbers
            try:
                result[key] = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                result[key] = value
        elif line.startswith('- '):
            # Array item
            if 'items' not in result:
                result['items'] = []
            result['items'].append(line[2:].strip())
    return result


# =============================================================================
# Init Tests
# =============================================================================

def test_init_creates_marshal_json():
    """Test init creates marshal.json with defaults."""
    with PlanTestContext() as ctx:
        result = run_script(SCRIPT_PATH, 'init')

        assert result.success, f"Init should succeed: {result.stderr}"
        assert 'success' in result.stdout.lower(), "Should output success"

        marshal_path = ctx.fixture_dir / 'marshal.json'
        assert marshal_path.exists(), "marshal.json should be created"

        config = json.loads(marshal_path.read_text())
        assert 'skill_domains' in config, "Should have skill_domains"
        assert 'system' in config, "Should have system"
        assert 'plan' in config, "Should have plan"


def test_init_fails_if_exists():
    """Test init fails if marshal.json already exists."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'init')

        assert not result.success or 'already exists' in result.stdout.lower(), \
            "Should fail or warn when marshal.json exists"


def test_init_force_overwrites():
    """Test init --force overwrites existing marshal.json."""
    with PlanTestContext() as ctx:
        # Create existing with custom content
        create_marshal_json(ctx.fixture_dir, {"custom": True})

        result = run_script(SCRIPT_PATH, 'init', '--force')

        assert result.success, f"Init --force should succeed: {result.stderr}"

        marshal_path = ctx.fixture_dir / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        assert 'skill_domains' in config, "Should have default content"
        assert 'custom' not in config, "Should not have old custom content"


# =============================================================================
# Skill-Domains Tests
# =============================================================================

def test_skill_domains_list():
    """Test skill-domains list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'success' in result.stdout.lower()
        assert 'java' in result.stdout


def test_skill_domains_get():
    """Test skill-domains get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-java:cui-java-core' in result.stdout


def test_skill_domains_get_defaults():
    """Test skill-domains get-defaults."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get-defaults', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-java:cui-java-core' in result.stdout


def test_skill_domains_get_optionals():
    """Test skill-domains get-optionals."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get-optionals', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-java:cui-java-cdi' in result.stdout


def test_skill_domains_unknown_domain():
    """Test skill-domains get with unknown domain returns error."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'unknown')

        assert 'error' in result.stdout.lower(), "Should report error"
        assert 'unknown' in result.stdout.lower()


def test_skill_domains_add():
    """Test skill-domains add."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'skill-domains', 'add',
            '--domain', 'python',
            '--defaults', 'pm-dev-python:cui-python-core'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify added
        verify = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'python')
        assert 'pm-dev-python:cui-python-core' in verify.stdout


def test_skill_domains_validate():
    """Test skill-domains validate."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        # Valid skill
        result = run_script(
            SCRIPT_PATH, 'skill-domains', 'validate',
            '--domain', 'java',
            '--skill', 'pm-dev-java:cui-java-core'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'true' in result.stdout.lower() or 'valid' in result.stdout.lower()


# =============================================================================
# Modules Tests
# =============================================================================

def test_modules_list():
    """Test modules list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout


def test_modules_get():
    """Test modules get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'my-core')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout.lower()
        assert 'maven' in result.stdout.lower()


def test_modules_get_domains():
    """Test modules get-domains."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get-domains', '--module', 'my-ui')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout.lower()
        assert 'javascript' in result.stdout.lower()


def test_modules_get_build_systems():
    """Test modules get-build-systems."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get-build-systems', '--module', 'my-ui')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()
        assert 'npm' in result.stdout.lower()


def test_modules_get_command_project_level():
    """Test modules get-command returns project-level command."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'get-command',
            '--module', 'my-core',
            '--system', 'maven',
            '--label', 'verify'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'clean verify' in result.stdout
        assert 'project_level' in result.stdout


def test_modules_get_command_module_override():
    """Test modules get-command returns module-specific override."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'get-command',
            '--module', 'my-ui',
            '--system', 'npm',
            '--label', 'test'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'custom:test' in result.stdout
        assert 'module_override' in result.stdout


def test_modules_add():
    """Test modules add."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'add',
            '--module', 'new-module',
            '--path', 'path/to/new-module',
            '--domains', 'java,java-testing',
            '--build-systems', 'maven'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify added
        verify = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'new-module')
        assert 'path/to/new-module' in verify.stdout


def test_modules_remove():
    """Test modules remove."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'remove', '--module', 'my-core')

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify removed
        verify = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'my-core')
        assert 'error' in verify.stdout.lower()


# =============================================================================
# Build-Systems Tests
# =============================================================================

def test_build_systems_list():
    """Test build-systems list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()
        assert 'npm' in result.stdout.lower()


def test_build_systems_get():
    """Test build-systems get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'maven')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-builder:builder-maven-rules' in result.stdout
        assert 'verify' in result.stdout.lower()


def test_build_systems_get_command():
    """Test build-systems get-command."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'build-systems', 'get-command',
            '--system', 'maven',
            '--label', 'verify'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'clean verify' in result.stdout


def test_build_systems_add():
    """Test build-systems add."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'add', '--system', 'gradle')

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify added
        verify = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'gradle')
        assert 'pm-dev-builder:builder-gradle-rules' in verify.stdout


def test_build_systems_remove():
    """Test build-systems remove."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'remove', '--system', 'npm')

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify removed
        verify = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'npm')
        assert 'error' in verify.stdout.lower()


# =============================================================================
# System Tests
# =============================================================================

def test_system_retention_get():
    """Test system retention get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'system', 'retention', 'get')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'logs_days' in result.stdout
        assert '1' in result.stdout  # Default value


def test_system_retention_set():
    """Test system retention set."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'system', 'retention', 'set',
            '--field', 'logs_days',
            '--value', '7'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify changed
        verify = run_script(SCRIPT_PATH, 'system', 'retention', 'get')
        assert '7' in verify.stdout


# =============================================================================
# Plan Tests
# =============================================================================

def test_plan_defaults_list():
    """Test plan defaults list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'plan', 'defaults', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'commit_strategy' in result.stdout
        assert 'phase-specific' in result.stdout


def test_plan_defaults_get():
    """Test plan defaults get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'plan', 'defaults', 'get',
            '--field', 'commit_strategy'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'phase-specific' in result.stdout


def test_plan_defaults_set():
    """Test plan defaults set."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'plan', 'defaults', 'set',
            '--field', 'create_pr',
            '--value', 'true'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify changed
        verify = run_script(SCRIPT_PATH, 'plan', 'defaults', 'get', '--field', 'create_pr')
        assert 'true' in verify.stdout.lower()


# =============================================================================
# Error Handling Tests
# =============================================================================

def test_error_without_marshal_json():
    """Test operations fail gracefully without marshal.json."""
    with PlanTestContext() as ctx:
        # Don't create marshal.json

        result = run_script(SCRIPT_PATH, 'skill-domains', 'list')

        assert 'error' in result.stdout.lower(), "Should report error"
        assert 'marshal.json' in result.stdout.lower() or '/plan-marshall' in result.stdout.lower()


def test_help_output():
    """Test --help outputs usage information."""
    result = run_script(SCRIPT_PATH, '--help')

    assert result.success, "Help should succeed"
    assert 'skill-domains' in result.stdout
    assert 'modules' in result.stdout
    assert 'build-systems' in result.stdout
    assert 'system' in result.stdout
    assert 'plan' in result.stdout
    assert 'init' in result.stdout


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Init tests
        test_init_creates_marshal_json,
        test_init_fails_if_exists,
        test_init_force_overwrites,
        # Skill-domains tests
        test_skill_domains_list,
        test_skill_domains_get,
        test_skill_domains_get_defaults,
        test_skill_domains_get_optionals,
        test_skill_domains_unknown_domain,
        test_skill_domains_add,
        test_skill_domains_validate,
        # Modules tests
        test_modules_list,
        test_modules_get,
        test_modules_get_domains,
        test_modules_get_build_systems,
        test_modules_get_command_project_level,
        test_modules_get_command_module_override,
        test_modules_add,
        test_modules_remove,
        # Build-systems tests
        test_build_systems_list,
        test_build_systems_get,
        test_build_systems_get_command,
        test_build_systems_add,
        test_build_systems_remove,
        # System tests
        test_system_retention_get,
        test_system_retention_set,
        # Plan tests
        test_plan_defaults_list,
        test_plan_defaults_get,
        test_plan_defaults_set,
        # Error handling tests
        test_error_without_marshal_json,
        test_help_output,
    ])
    sys.exit(runner.run())
