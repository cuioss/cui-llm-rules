#!/usr/bin/env python3
"""Integration tests for plan-marshall-config.py script.

Happy-path tests verifying the monolithic CLI API.
Detailed variant and corner case tests are in:
- test_cmd_init.py
- test_cmd_skill_domains.py
- test_cmd_modules.py
- test_cmd_build_systems.py
- test_cmd_system_plan.py
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, PlanTestContext
from test_helpers import SCRIPT_PATH, create_marshal_json, create_nested_marshal_json


# =============================================================================
# Happy-Path Integration Tests
# =============================================================================

def test_init_creates_marshal_json():
    """Test init creates marshal.json with defaults."""
    with PlanTestContext() as ctx:
        result = run_script(SCRIPT_PATH, 'init')

        assert result.success, f"Init should succeed: {result.stderr}"
        assert 'success' in result.stdout.lower()

        marshal_path = ctx.fixture_dir / 'marshal.json'
        assert marshal_path.exists(), "marshal.json should be created"


def test_skill_domains_list():
    """Test skill-domains list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout


def test_skill_domains_get():
    """Test skill-domains get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-java:java-core' in result.stdout


def test_modules_list():
    """Test modules list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'my-core' in result.stdout


def test_modules_get():
    """Test modules get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'my-core')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout.lower()


def test_build_systems_list():
    """Test build-systems list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()


def test_build_systems_get():
    """Test build-systems get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'maven')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-builder:builder-maven-rules' in result.stdout


def test_system_retention_get():
    """Test system retention get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'system', 'retention', 'get')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'logs_days' in result.stdout


def test_plan_defaults_list():
    """Test plan defaults list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'plan', 'defaults', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'commit_strategy' in result.stdout


def test_resolve_domain_skills():
    """Test resolve-domain-skills command."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'resolve-domain-skills',
            '--domain', 'java',
            '--profile', 'implementation'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-java:java-core' in result.stdout


def test_get_workflow_skills():
    """Test get-workflow-skills command."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'get-workflow-skills')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'solution_outline' in result.stdout


def test_error_without_marshal_json():
    """Test operations fail gracefully without marshal.json."""
    with PlanTestContext() as ctx:
        # Don't create marshal.json

        result = run_script(SCRIPT_PATH, 'skill-domains', 'list')

        assert 'error' in result.stdout.lower(), "Should report error"


def test_help_output():
    """Test --help outputs usage information."""
    result = run_script(SCRIPT_PATH, '--help')

    assert result.success, "Help should succeed"
    assert 'skill-domains' in result.stdout
    assert 'modules' in result.stdout
    assert 'build-systems' in result.stdout


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_init_creates_marshal_json,
        test_skill_domains_list,
        test_skill_domains_get,
        test_modules_list,
        test_modules_get,
        test_build_systems_list,
        test_build_systems_get,
        test_system_retention_get,
        test_plan_defaults_list,
        test_resolve_domain_skills,
        test_get_workflow_skills,
        test_error_without_marshal_json,
        test_help_output,
    ])
    sys.exit(runner.run())
