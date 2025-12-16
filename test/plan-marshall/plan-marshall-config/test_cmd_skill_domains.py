#!/usr/bin/env python3
"""Tests for skill-domains commands in plan-marshall-config.

Tests skill-domains, resolve-domain-skills, get-workflow-skills commands
including nested structure variants and edge cases.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, PlanTestContext
from test_helpers import SCRIPT_PATH, create_marshal_json, create_nested_marshal_json


# =============================================================================
# skill-domains Basic Tests (Flat Structure)
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
        assert 'pm-dev-java:java-core' in result.stdout


def test_skill_domains_get_defaults():
    """Test skill-domains get-defaults."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get-defaults', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-java:java-core' in result.stdout


def test_skill_domains_get_optionals():
    """Test skill-domains get-optionals."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get-optionals', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-java:java-cdi' in result.stdout


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
            '--skill', 'pm-dev-java:java-core'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'true' in result.stdout.lower() or 'valid' in result.stdout.lower()


def test_skill_domains_validate_returns_location():
    """Test skill-domains validate returns in_defaults or in_optionals."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        # Skill in defaults
        result_defaults = run_script(
            SCRIPT_PATH, 'skill-domains', 'validate',
            '--domain', 'java',
            '--skill', 'pm-dev-java:java-core'
        )

        assert result_defaults.success, f"Should succeed: {result_defaults.stderr}"
        assert 'in_defaults' in result_defaults.stdout.lower()

        # Skill in optionals
        result_optionals = run_script(
            SCRIPT_PATH, 'skill-domains', 'validate',
            '--domain', 'java',
            '--skill', 'pm-dev-java:java-cdi'
        )

        assert result_optionals.success, f"Should succeed: {result_optionals.stderr}"
        assert 'in_optionals' in result_optionals.stdout.lower()


def test_skill_domains_validate_invalid_skill():
    """Test skill-domains validate with invalid skill returns false."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'skill-domains', 'validate',
            '--domain', 'java',
            '--skill', 'pm-dev-java:invalid-skill'
        )

        assert result.success, f"Should succeed even if invalid: {result.stderr}"
        assert 'false' in result.stdout.lower()


# =============================================================================
# skill-domains Nested Structure Tests
# =============================================================================

def test_skill_domains_get_nested_structure():
    """Test skill-domains get returns nested structure for domains with profiles."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        # Should include workflow_skills
        assert 'workflow_skills' in result.stdout
        # Should include core block
        assert 'core' in result.stdout
        # Should include implementation block
        assert 'implementation' in result.stdout
        # Should include testing block
        assert 'testing' in result.stdout


def test_skill_domains_get_defaults_nested():
    """Test skill-domains get-defaults returns core.defaults for nested structure."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get-defaults', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        # Should return core.defaults
        assert 'pm-dev-java:java-core' in result.stdout


def test_skill_domains_get_optionals_nested():
    """Test skill-domains get-optionals returns core.optionals for nested structure."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get-optionals', '--domain', 'java')

        assert result.success, f"Should succeed: {result.stderr}"
        # Should return core.optionals
        assert 'pm-dev-java:java-null-safety' in result.stdout
        assert 'pm-dev-java:java-lombok' in result.stdout


def test_skill_domains_validate_nested():
    """Test skill-domains validate works with nested structure."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        # Validate skill in core.defaults
        result = run_script(
            SCRIPT_PATH, 'skill-domains', 'validate',
            '--domain', 'java',
            '--skill', 'pm-dev-java:java-core'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'true' in result.stdout.lower() or 'valid' in result.stdout.lower()


def test_skill_domains_validate_nested_profile_skill():
    """Test skill-domains validate finds skills in profile blocks."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        # Validate skill in testing.defaults (junit-core)
        result = run_script(
            SCRIPT_PATH, 'skill-domains', 'validate',
            '--domain', 'java',
            '--skill', 'pm-dev-java:junit-core'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'true' in result.stdout.lower() or 'valid' in result.stdout.lower()
        assert 'in_defaults' in result.stdout.lower()


def test_skill_domains_get_system_flat_structure():
    """Test skill-domains get returns flat structure for system domain."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'system')

        assert result.success, f"Should succeed: {result.stderr}"
        # System domain uses flat structure
        assert 'defaults' in result.stdout
        assert 'plan-marshall:general-development-rules' in result.stdout
        # Should NOT have core/implementation/testing blocks
        assert 'workflow_skills' not in result.stdout


# =============================================================================
# skill-domains detect Tests
# =============================================================================

def test_skill_domains_detect_runs():
    """Test skill-domains detect command runs successfully."""
    with PlanTestContext() as ctx:
        # Create minimal marshal.json
        config = {
            "skill_domains": {
                "system": {
                    "defaults": ["plan-marshall:general-development-rules"],
                    "optionals": []
                }
            },
            "modules": {},
            "build_systems": [],
            "system": {"retention": {}},
            "plan": {"defaults": {}}
        }
        marshal_path = ctx.fixture_dir / 'marshal.json'
        marshal_path.write_text(json.dumps(config, indent=2))

        result = run_script(SCRIPT_PATH, 'skill-domains', 'detect')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'success' in result.stdout.lower()
        assert 'detected' in result.stdout.lower()


def test_skill_domains_detect_no_overwrite():
    """Test skill-domains detect does not overwrite existing domains."""
    with PlanTestContext() as ctx:
        # Create marshal.json with custom java domain
        config = {
            "skill_domains": {
                "system": {"defaults": [], "optionals": []},
                "java": {
                    "core": {"defaults": ["custom:skill"], "optionals": []}
                }
            },
            "modules": {},
            "build_systems": [],
            "system": {"retention": {}},
            "plan": {"defaults": {}}
        }
        marshal_path = ctx.fixture_dir / 'marshal.json'
        marshal_path.write_text(json.dumps(config, indent=2))

        result = run_script(SCRIPT_PATH, 'skill-domains', 'detect')

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify existing java domain was NOT overwritten (even if java was detected)
        verify = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'java')
        assert 'custom:skill' in verify.stdout


# =============================================================================
# resolve-domain-skills Tests
# =============================================================================

def test_resolve_domain_skills_java_implementation():
    """Test resolve-domain-skills for java + implementation profile."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'resolve-domain-skills',
            '--domain', 'java',
            '--profile', 'implementation'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        # Should include core defaults (java-core)
        assert 'pm-dev-java:java-core' in result.stdout
        # Should include implementation optionals (java-cdi, java-maintenance)
        assert 'pm-dev-java:java-cdi' in result.stdout
        # Should NOT include testing defaults (junit-core)
        assert 'pm-dev-java:junit-core' not in result.stdout


def test_resolve_domain_skills_java_testing():
    """Test resolve-domain-skills for java + testing profile."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'resolve-domain-skills',
            '--domain', 'java',
            '--profile', 'testing'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        # Should include core defaults (java-core)
        assert 'pm-dev-java:java-core' in result.stdout
        # Should include testing defaults (junit-core)
        assert 'pm-dev-java:junit-core' in result.stdout
        # Should include testing optionals (junit-integration)
        assert 'pm-dev-java:junit-integration' in result.stdout
        # Should NOT include implementation optionals (java-cdi)
        assert 'pm-dev-java:java-cdi' not in result.stdout


def test_resolve_domain_skills_javascript_implementation():
    """Test resolve-domain-skills for javascript + implementation profile."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'resolve-domain-skills',
            '--domain', 'javascript',
            '--profile', 'implementation'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        # Should include core defaults (cui-javascript)
        assert 'pm-dev-frontend:cui-javascript' in result.stdout
        # Should include implementation optionals
        assert 'pm-dev-frontend:cui-javascript-linting' in result.stdout


def test_resolve_domain_skills_unknown_domain():
    """Test resolve-domain-skills with unknown domain returns error."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'resolve-domain-skills',
            '--domain', 'unknown',
            '--profile', 'implementation'
        )

        assert 'error' in result.stdout.lower(), "Should report error"
        assert 'unknown' in result.stdout.lower()


def test_resolve_domain_skills_unknown_profile():
    """Test resolve-domain-skills with unknown profile returns error."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'resolve-domain-skills',
            '--domain', 'java',
            '--profile', 'invalid-profile'
        )

        assert 'error' in result.stdout.lower(), "Should report error"
        assert 'profile' in result.stdout.lower()


# =============================================================================
# get-workflow-skills Tests
# =============================================================================

def test_get_workflow_skills():
    """Test get-workflow-skills returns workflow skill references."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'get-workflow-skills')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'solution_outline' in result.stdout
        assert 'task_plan' in result.stdout
        assert 'implementation' in result.stdout
        assert 'testing' in result.stdout
        assert 'pm-workflow:solution-outline' in result.stdout
        assert 'pm-workflow:task-plan' in result.stdout


def test_get_workflow_skills_output_format():
    """Test get-workflow-skills returns all 4 workflow skill references."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'get-workflow-skills')

        assert result.success, f"Should succeed: {result.stderr}"
        # Verify all 4 workflow skills are returned
        assert 'pm-workflow:task-implementation' in result.stdout
        assert 'pm-workflow:task-testing' in result.stdout


# =============================================================================
# resolve-workflow-skill Tests
# =============================================================================

def test_resolve_workflow_skill_java_implementation():
    """Test resolve-workflow-skill for java + implementation phase."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'java', '--phase', 'implementation')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-workflow:task-implementation' in result.stdout
        assert 'domain' in result.stdout
        assert 'phase' in result.stdout
        assert 'workflow_skill' in result.stdout


def test_resolve_workflow_skill_java_solution_outline():
    """Test resolve-workflow-skill for java + solution_outline phase."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'java', '--phase', 'solution_outline')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-workflow:solution-outline' in result.stdout


def test_resolve_workflow_skill_java_testing():
    """Test resolve-workflow-skill for java + testing phase."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'java', '--phase', 'testing')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-workflow:task-testing' in result.stdout


def test_resolve_workflow_skill_plugin_solution_outline():
    """Test resolve-workflow-skill for plugin + solution_outline phase."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'plugin', '--phase', 'solution_outline')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-plugin-development:plugin-solution-outline' in result.stdout


def test_resolve_workflow_skill_plugin_implementation():
    """Test resolve-workflow-skill for plugin + implementation phase."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'plugin', '--phase', 'implementation')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-plugin-development:plugin-plan-implement' in result.stdout


def test_resolve_workflow_skill_generic_implementation():
    """Test resolve-workflow-skill for generic + implementation phase."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'generic', '--phase', 'implementation')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-workflow:task-implementation' in result.stdout


def test_resolve_workflow_skill_unknown_domain():
    """Test resolve-workflow-skill with unknown domain returns error."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'unknown', '--phase', 'implementation')

        assert 'error' in result.stdout.lower(), "Should report error"
        assert 'unknown' in result.stdout.lower()


def test_resolve_workflow_skill_unknown_phase():
    """Test resolve-workflow-skill with unknown phase returns error."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'java', '--phase', 'invalid_phase')

        assert 'error' in result.stdout.lower(), "Should report error"
        assert 'phase' in result.stdout.lower()


def test_resolve_workflow_skill_plugin_no_testing():
    """Test resolve-workflow-skill for plugin + testing returns error (plugin has no testing phase)."""
    with PlanTestContext() as ctx:
        create_nested_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'resolve-workflow-skill',
            '--domain', 'plugin', '--phase', 'testing')

        assert 'error' in result.stdout.lower(), "Should report error (plugin has no testing phase)"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Basic skill-domains tests (flat structure)
        test_skill_domains_list,
        test_skill_domains_get,
        test_skill_domains_get_defaults,
        test_skill_domains_get_optionals,
        test_skill_domains_unknown_domain,
        test_skill_domains_add,
        test_skill_domains_validate,
        test_skill_domains_validate_returns_location,
        test_skill_domains_validate_invalid_skill,
        # Nested structure tests
        test_skill_domains_get_nested_structure,
        test_skill_domains_get_defaults_nested,
        test_skill_domains_get_optionals_nested,
        test_skill_domains_validate_nested,
        test_skill_domains_validate_nested_profile_skill,
        test_skill_domains_get_system_flat_structure,
        # Detect tests
        test_skill_domains_detect_runs,
        test_skill_domains_detect_no_overwrite,
        # resolve-domain-skills tests
        test_resolve_domain_skills_java_implementation,
        test_resolve_domain_skills_java_testing,
        test_resolve_domain_skills_javascript_implementation,
        test_resolve_domain_skills_unknown_domain,
        test_resolve_domain_skills_unknown_profile,
        # get-workflow-skills tests
        test_get_workflow_skills,
        test_get_workflow_skills_output_format,
        # resolve-workflow-skill tests
        test_resolve_workflow_skill_java_implementation,
        test_resolve_workflow_skill_java_solution_outline,
        test_resolve_workflow_skill_java_testing,
        test_resolve_workflow_skill_plugin_solution_outline,
        test_resolve_workflow_skill_plugin_implementation,
        test_resolve_workflow_skill_generic_implementation,
        test_resolve_workflow_skill_unknown_domain,
        test_resolve_workflow_skill_unknown_phase,
        test_resolve_workflow_skill_plugin_no_testing,
    ])
    sys.exit(runner.run())
