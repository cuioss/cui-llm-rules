#!/usr/bin/env python3
"""Tests for manage-config.py script with new domains/workflow_skills API."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, PlanTestContext

# Get script path
SCRIPT_PATH = get_script_path('pm-workflow', 'manage-config', 'manage-config.py')

# Import toon_parser for output parsing
TOON_PARSER_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(TOON_PARSER_DIR))
from toon_parser import parse_toon


# Alias for backward compatibility
TestContext = PlanTestContext

# Sample workflow skills for testing
JAVA_WORKFLOW_SKILLS = '{"java":{"solution_outline":"pm-workflow:solution-outline","task_plan":"pm-workflow:task-plan","implementation":"pm-workflow:task-implementation","testing":"pm-workflow:task-testing"}}'
PLUGIN_WORKFLOW_SKILLS = '{"plugin":{"solution_outline":"pm-plugin-development:plugin-solution-outline","task_plan":"pm-plugin-development:plugin-task-plan","implementation":"pm-plugin-development:plugin-plan-implement","testing":"pm-plugin-development:plugin-testing"}}'
MULTI_DOMAIN_WORKFLOW_SKILLS = '{"java":{"solution_outline":"pm-workflow:solution-outline","task_plan":"pm-workflow:task-plan","implementation":"pm-workflow:task-implementation","testing":"pm-workflow:task-testing"},"javascript":{"solution_outline":"pm-workflow:solution-outline","task_plan":"pm-workflow:task-plan","implementation":"pm-workflow:task-implementation","testing":"pm-workflow:task-testing"}}'


# =============================================================================
# Test: Create Command (New API)
# =============================================================================

def test_create_config_single_domain():
    """Test creating a config file with single domain (java)."""
    with TestContext(plan_id='config-single'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-single',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['domains_count'] == 1
        assert data['config']['domains'] == ['java']
        assert 'java' in data['config']['workflow_skills']


def test_create_config_multiple_domains():
    """Test creating a config file with multiple domains."""
    with TestContext(plan_id='config-multi-domain'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-multi-domain',
            '--domains', 'java,javascript',
            '--workflow-skills', MULTI_DOMAIN_WORKFLOW_SKILLS
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['domains_count'] == 2
        assert 'java' in data['config']['domains']
        assert 'javascript' in data['config']['domains']


def test_create_config_plugin_domain():
    """Test creating a config file with plugin domain."""
    with TestContext(plan_id='config-plugin'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-plugin',
            '--domains', 'plugin',
            '--workflow-skills', PLUGIN_WORKFLOW_SKILLS
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['config']['domains'] == ['plugin']


def test_create_config_with_all_options():
    """Test creating a config file with all optional parameters."""
    with TestContext(plan_id='config-full-opts'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-full-opts',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS,
            '--commit-strategy', 'per_plan',
            '--create-pr', 'false',
            '--verification-required', 'true',
            '--verification-command', '/pm-dev-builder:builder-build-and-fix',
            '--branch-strategy', 'direct'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['config']['commit_strategy'] == 'per_plan'
        assert data['config']['create_pr'] == False
        assert data['config']['verification_required'] == True
        assert data['config']['verification_command'] == '/pm-dev-builder:builder-build-and-fix'
        assert data['config']['branch_strategy'] == 'direct'


def test_create_config_missing_domains():
    """Test that create fails when domains is missing required entry."""
    with TestContext(plan_id='config-missing-domain'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-missing-domain',
            '--domains', 'java,javascript',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS  # Only has java, not javascript
        )
        assert not result.success, "Expected failure for missing domain in workflow_skills"
        data = parse_toon(result.stdout)
        assert data['error'] == 'missing_domain_skills'


def test_create_config_invalid_domain():
    """Test that invalid domain format fails."""
    with TestContext(plan_id='config-invalid-domain'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-invalid-domain',
            '--domains', 'Java',  # Must be lowercase
            '--workflow-skills', '{"Java":{}}'
        )
        assert not result.success, "Expected failure for invalid domain format"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_domain'


def test_create_config_invalid_workflow_skill():
    """Test that invalid workflow skill format fails."""
    with TestContext(plan_id='config-invalid-skill'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-invalid-skill',
            '--domains', 'java',
            '--workflow-skills', '{"java":{"implementation":"invalid-skill"}}'  # Missing bundle: notation
        )
        assert not result.success, "Expected failure for invalid workflow skill format"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_workflow_skill'


def test_create_config_invalid_json():
    """Test that invalid JSON in workflow_skills fails."""
    with TestContext(plan_id='config-invalid-json'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-invalid-json',
            '--domains', 'java',
            '--workflow-skills', '{invalid json}'
        )
        assert not result.success, "Expected failure for invalid JSON"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_workflow_skills'


# =============================================================================
# Test: Get-Workflow-Skill Subcommand
# =============================================================================

def test_get_workflow_skill_java_implementation():
    """Test getting workflow skill for java + implementation profile."""
    with TestContext(plan_id='config-gws-java'):
        # Create config first
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-gws-java',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        # Get workflow skill
        result = run_script(SCRIPT_PATH, 'get-workflow-skill',
            '--plan-id', 'config-gws-java',
            '--domain', 'java',
            '--profile', 'implementation'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['domain'] == 'java'
        assert data['profile'] == 'implementation'
        assert data['workflow_skill'] == 'pm-workflow:task-implementation'


def test_get_workflow_skill_java_testing():
    """Test getting workflow skill for java + testing profile."""
    with TestContext(plan_id='config-gws-testing'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-gws-testing',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get-workflow-skill',
            '--plan-id', 'config-gws-testing',
            '--domain', 'java',
            '--profile', 'testing'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['workflow_skill'] == 'pm-workflow:task-testing'


def test_get_workflow_skill_plugin_implementation():
    """Test getting workflow skill for plugin + implementation profile."""
    with TestContext(plan_id='config-gws-plugin'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-gws-plugin',
            '--domains', 'plugin',
            '--workflow-skills', PLUGIN_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get-workflow-skill',
            '--plan-id', 'config-gws-plugin',
            '--domain', 'plugin',
            '--profile', 'implementation'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['workflow_skill'] == 'pm-plugin-development:plugin-plan-implement'


def test_get_workflow_skill_unknown_domain():
    """Test that unknown domain returns error."""
    with TestContext(plan_id='config-gws-unknown-domain'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-gws-unknown-domain',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get-workflow-skill',
            '--plan-id', 'config-gws-unknown-domain',
            '--domain', 'python',
            '--profile', 'implementation'
        )
        assert not result.success, "Expected failure for unknown domain"
        data = parse_toon(result.stdout)
        assert data['error'] == 'domain_not_found'
        assert 'available_domains' in data


def test_get_workflow_skill_unknown_profile():
    """Test that unknown profile returns error."""
    with TestContext(plan_id='config-gws-unknown-profile'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-gws-unknown-profile',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get-workflow-skill',
            '--plan-id', 'config-gws-unknown-profile',
            '--domain', 'java',
            '--profile', 'unknown_profile'
        )
        assert not result.success, "Expected failure for unknown profile"
        data = parse_toon(result.stdout)
        assert data['error'] == 'profile_not_found'
        assert 'available_profiles' in data


# =============================================================================
# Test: Get-Domains Subcommand
# =============================================================================

def test_get_domains_single():
    """Test getting domains array with single domain."""
    with TestContext(plan_id='config-gd-single'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-gd-single',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get-domains',
            '--plan-id', 'config-gd-single'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['domains'] == ['java']
        assert data['count'] == 1


def test_get_domains_multiple():
    """Test getting domains array with multiple domains."""
    with TestContext(plan_id='config-gd-multi'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-gd-multi',
            '--domains', 'java,javascript',
            '--workflow-skills', MULTI_DOMAIN_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get-domains',
            '--plan-id', 'config-gd-multi'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['count'] == 2
        assert 'java' in data['domains']
        assert 'javascript' in data['domains']


def test_get_domains_not_found():
    """Test get-domains with missing plan."""
    with TestContext():
        result = run_script(SCRIPT_PATH, 'get-domains',
            '--plan-id', 'nonexistent'
        )
        assert not result.success, "Expected failure for missing plan"
        data = parse_toon(result.stdout)
        assert data['error'] == 'file_not_found'


# =============================================================================
# Test: Nested Field Access in Get Command
# =============================================================================

def test_get_nested_workflow_skill():
    """Test getting nested workflow_skills.java.implementation via dot notation."""
    with TestContext(plan_id='config-nested-get'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-nested-get',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get',
            '--plan-id', 'config-nested-get',
            '--field', 'workflow_skills.java.implementation'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['field'] == 'workflow_skills.java.implementation'
        assert data['value'] == 'pm-workflow:task-implementation'


def test_get_domains_array():
    """Test getting domains array via get command."""
    with TestContext(plan_id='config-get-domains'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-get-domains',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get',
            '--plan-id', 'config-get-domains',
            '--field', 'domains'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['value'] == ['java']


def test_get_nested_not_found():
    """Test getting non-existent nested field."""
    with TestContext(plan_id='config-nested-not-found'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-nested-not-found',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'get',
            '--plan-id', 'config-nested-not-found',
            '--field', 'workflow_skills.python.implementation'
        )
        assert not result.success, "Expected failure for non-existent nested field"
        data = parse_toon(result.stdout)
        assert data['error'] == 'field_not_found'


# =============================================================================
# Test: Get/Set/Read Operations (Basic Functionality)
# =============================================================================

def test_set_and_get_field():
    """Test setting and getting a config field."""
    with TestContext(plan_id='config-getset'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-getset',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        # Set a field
        set_result = run_script(SCRIPT_PATH, 'set',
            '--plan-id', 'config-getset',
            '--field', 'commit_strategy',
            '--value', 'per_plan'
        )
        assert set_result.success, f"Set failed: {set_result.stderr}"

        # Get the field
        get_result = run_script(SCRIPT_PATH, 'get',
            '--plan-id', 'config-getset',
            '--field', 'commit_strategy'
        )
        assert get_result.success, f"Get failed: {get_result.stderr}"
        data = parse_toon(get_result.stdout)
        assert data['value'] == 'per_plan'


def test_read_config():
    """Test reading entire config."""
    with TestContext(plan_id='config-read'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-read',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'config-read'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert 'config' in data
        assert data['config']['domains'] == ['java']


def test_set_invalid_commit_strategy():
    """Test that setting invalid commit_strategy fails."""
    with TestContext(plan_id='config-invalid-commit'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-invalid-commit',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS
        )
        result = run_script(SCRIPT_PATH, 'set',
            '--plan-id', 'config-invalid-commit',
            '--field', 'commit_strategy',
            '--value', 'invalid_value'
        )
        assert not result.success, "Expected failure for invalid commit_strategy"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_value'
        assert 'valid_values' in data


# =============================================================================
# Test: Domain Workflow Skills Lookup (TDD - New Feature)
# =============================================================================

def test_create_config_java_domain_lookup():
    """Test creating config with java domain - workflow_skills auto-looked up."""
    with TestContext(plan_id='config-java-lookup'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-java-lookup',
            '--domains', 'java'
            # No --workflow-skills provided - should be looked up
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['config']['domains'] == ['java']
        # Verify correct workflow_skills structure
        java_skills = data['config']['workflow_skills']['java']
        assert java_skills['solution_outline'] == 'pm-workflow:solution-outline'
        assert java_skills['task_plan'] == 'pm-workflow:task-plan'
        assert java_skills['implementation'] == 'pm-workflow:task-implementation'
        assert java_skills['testing'] == 'pm-workflow:task-testing'


def test_create_config_plugin_domain_lookup():
    """Test creating config with plugin domain - workflow_skills auto-looked up."""
    with TestContext(plan_id='config-plugin-lookup'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-plugin-lookup',
            '--domains', 'plugin'
            # No --workflow-skills provided - should be looked up
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['config']['domains'] == ['plugin']
        # Verify correct plugin workflow_skills structure
        plugin_skills = data['config']['workflow_skills']['plugin']
        assert plugin_skills['solution_outline'] == 'pm-plugin-development:plugin-solution-outline'
        assert plugin_skills['task_plan'] == 'pm-plugin-development:plugin-task-plan'
        assert plugin_skills['implementation'] == 'pm-plugin-development:plugin-plan-implement'


def test_create_config_javascript_domain_lookup():
    """Test creating config with javascript domain - workflow_skills auto-looked up."""
    with TestContext(plan_id='config-js-lookup'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-js-lookup',
            '--domains', 'javascript'
            # No --workflow-skills provided - should be looked up
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['config']['domains'] == ['javascript']
        # Verify correct workflow_skills structure
        js_skills = data['config']['workflow_skills']['javascript']
        assert js_skills['solution_outline'] == 'pm-workflow:solution-outline'
        assert js_skills['task_plan'] == 'pm-workflow:task-plan'
        assert js_skills['implementation'] == 'pm-workflow:task-implementation'
        assert js_skills['testing'] == 'pm-workflow:task-testing'


def test_create_config_generic_domain_lookup():
    """Test creating config with generic domain - workflow_skills auto-looked up."""
    with TestContext(plan_id='config-generic-lookup'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-generic-lookup',
            '--domains', 'generic'
            # No --workflow-skills provided - should be looked up
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['config']['domains'] == ['generic']
        # Verify correct workflow_skills structure
        generic_skills = data['config']['workflow_skills']['generic']
        assert generic_skills['solution_outline'] == 'pm-workflow:solution-outline'
        assert generic_skills['task_plan'] == 'pm-workflow:task-plan'
        assert generic_skills['implementation'] == 'pm-workflow:task-implementation'


def test_create_config_multi_domain_lookup():
    """Test creating config with multiple domains - workflow_skills auto-looked up for each."""
    with TestContext(plan_id='config-multi-lookup'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-multi-lookup',
            '--domains', 'java,javascript'
            # No --workflow-skills provided - should be looked up for each domain
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['domains_count'] == 2
        # Both domains should have workflow_skills
        assert 'java' in data['config']['workflow_skills']
        assert 'javascript' in data['config']['workflow_skills']
        assert data['config']['workflow_skills']['java']['implementation'] == 'pm-workflow:task-implementation'
        assert data['config']['workflow_skills']['javascript']['implementation'] == 'pm-workflow:task-implementation'


def test_create_config_explicit_overrides_lookup():
    """Test that explicit --workflow-skills still works (backwards compatible)."""
    custom_skills = '{"java":{"solution_outline":"custom:outline","task_plan":"custom:plan","implementation":"custom:impl","testing":"custom:test"}}'
    with TestContext(plan_id='config-explicit-override'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-explicit-override',
            '--domains', 'java',
            '--workflow-skills', custom_skills
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        # Should use explicit value, not lookup
        assert data['config']['workflow_skills']['java']['implementation'] == 'custom:impl'


def test_create_config_unknown_domain_fails():
    """Test that unknown domain fails when no workflow-skills provided."""
    with TestContext(plan_id='config-unknown-domain'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-unknown-domain',
            '--domains', 'python'  # Unknown domain with no default
            # No --workflow-skills provided
        )
        assert not result.success, "Expected failure for unknown domain"
        data = parse_toon(result.stdout)
        assert data['error'] == 'unknown_domain'


# =============================================================================
# Test: Get Multi
# =============================================================================

def test_get_multi_fields():
    """Test getting multiple fields in one call."""
    with TestContext(plan_id='config-multi'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-multi',
            '--domains', 'java',
            '--workflow-skills', JAVA_WORKFLOW_SKILLS,
            '--commit-strategy', 'per_plan',
            '--branch-strategy', 'direct'
        )
        result = run_script(SCRIPT_PATH, 'get-multi',
            '--plan-id', 'config-multi',
            '--fields', 'commit_strategy,branch_strategy'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['commit_strategy'] == 'per_plan'
        assert data['branch_strategy'] == 'direct'


def test_get_multi_not_found():
    """Test get-multi with missing plan."""
    with TestContext():
        result = run_script(SCRIPT_PATH, 'get-multi',
            '--plan-id', 'nonexistent',
            '--fields', 'commit_strategy'
        )
        assert not result.success, "Expected failure for missing plan"


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Create command (new API)
        test_create_config_single_domain,
        test_create_config_multiple_domains,
        test_create_config_plugin_domain,
        test_create_config_with_all_options,
        test_create_config_missing_domains,
        test_create_config_invalid_domain,
        test_create_config_invalid_workflow_skill,
        test_create_config_invalid_json,
        # Get-workflow-skill
        test_get_workflow_skill_java_implementation,
        test_get_workflow_skill_java_testing,
        test_get_workflow_skill_plugin_implementation,
        test_get_workflow_skill_unknown_domain,
        test_get_workflow_skill_unknown_profile,
        # Get-domains
        test_get_domains_single,
        test_get_domains_multiple,
        test_get_domains_not_found,
        # Nested field access
        test_get_nested_workflow_skill,
        test_get_domains_array,
        test_get_nested_not_found,
        # Basic operations
        test_set_and_get_field,
        test_read_config,
        test_set_invalid_commit_strategy,
        # Get multi
        test_get_multi_fields,
        test_get_multi_not_found,
        # Domain workflow_skills lookup (TDD - new feature)
        test_create_config_java_domain_lookup,
        test_create_config_plugin_domain_lookup,
        test_create_config_javascript_domain_lookup,
        test_create_config_generic_domain_lookup,
        test_create_config_multi_domain_lookup,
        test_create_config_explicit_overrides_lookup,
        test_create_config_unknown_domain_fails,
    ])
    sys.exit(runner.run())
