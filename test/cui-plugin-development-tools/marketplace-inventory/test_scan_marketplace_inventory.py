#!/usr/bin/env python3
"""Tests for scan-marketplace-inventory.py script.

Migrated from test-scan-marketplace-inventory.sh - tests marketplace inventory
scanning including basic discovery, resource filtering, description extraction,
JSON validity, bundle structure, script discovery, and error handling.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner, run_script, get_script_path

# Script under test
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SCRIPT_PATH = get_script_path('cui-plugin-development-tools', 'marketplace-inventory', 'scan-marketplace-inventory.py')


def parse_json(output):
    """Parse JSON from output."""
    import json
    return json.loads(output)


# =============================================================================
# Tests - Basic Discovery
# =============================================================================

def test_default_scan_finds_bundles():
    """Test default scan finds at least 5 bundles."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_bundles = data.get('statistics', {}).get('total_bundles', 0)
    assert total_bundles >= 5, f"Should find at least 5 bundles, found {total_bundles}"


def test_default_scan_finds_agents():
    """Test default scan finds at least 1 agent."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_agents = data.get('statistics', {}).get('total_agents', 0)
    assert total_agents >= 1, f"Should find at least 1 agent, found {total_agents}"


def test_default_scan_finds_commands():
    """Test default scan finds at least 30 commands."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_commands = data.get('statistics', {}).get('total_commands', 0)
    assert total_commands >= 30, f"Should find at least 30 commands, found {total_commands}"


def test_default_scan_finds_skills():
    """Test default scan finds at least 20 skills."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_skills = data.get('statistics', {}).get('total_skills', 0)
    assert total_skills >= 20, f"Should find at least 20 skills, found {total_skills}"


def test_default_scope_is_marketplace():
    """Test default scope is marketplace."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    scope = data.get('scope')
    assert scope == 'marketplace', f"Default scope should be 'marketplace', got '{scope}'"


# =============================================================================
# Tests - Resource Filtering
# =============================================================================

def test_agents_only_no_commands():
    """Test agents-only filter has no commands."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'agents')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_commands = data.get('statistics', {}).get('total_commands', 0)
    assert total_commands == 0, f"Agents-only should have 0 commands, found {total_commands}"


def test_agents_only_no_skills():
    """Test agents-only filter has no skills."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'agents')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_skills = data.get('statistics', {}).get('total_skills', 0)
    assert total_skills == 0, f"Agents-only should have 0 skills, found {total_skills}"


def test_agents_only_has_agents():
    """Test agents-only filter has agents."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'agents')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_agents = data.get('statistics', {}).get('total_agents', 0)
    assert total_agents >= 1, f"Agents-only should have at least 1 agent, found {total_agents}"


def test_commands_only_no_agents():
    """Test commands-only filter has no agents."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'commands')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_agents = data.get('statistics', {}).get('total_agents', 0)
    assert total_agents == 0, f"Commands-only should have 0 agents, found {total_agents}"


def test_commands_only_has_commands():
    """Test commands-only filter has commands."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'commands')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_commands = data.get('statistics', {}).get('total_commands', 0)
    assert total_commands >= 30, f"Commands-only should have at least 30 commands, found {total_commands}"


def test_skills_only_no_agents():
    """Test skills-only filter has no agents."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'skills')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_agents = data.get('statistics', {}).get('total_agents', 0)
    assert total_agents == 0, f"Skills-only should have 0 agents, found {total_agents}"


def test_skills_only_has_skills():
    """Test skills-only filter has skills."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'skills')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_skills = data.get('statistics', {}).get('total_skills', 0)
    assert total_skills >= 20, f"Skills-only should have at least 20 skills, found {total_skills}"


def test_multiple_types_has_both():
    """Test multiple types filter has both agents and commands."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'agents,commands')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    total_agents = data.get('statistics', {}).get('total_agents', 0)
    assert total_agents >= 1, f"Multiple types should have at least 1 agent, found {total_agents}"


# =============================================================================
# Tests - Description Extraction
# =============================================================================

def test_no_descriptions_returns_null():
    """Test default mode has no description fields."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)

    # Check if any agent has description field
    has_desc_count = sum(
        1 for bundle in data.get('bundles', [])
        for agent in bundle.get('agents', [])
        if 'description' in agent
    )
    assert has_desc_count == 0, f"Should have no description fields without --include-descriptions, found {has_desc_count}"


def test_with_descriptions_extracts_desc():
    """Test --include-descriptions extracts descriptions."""
    result = run_script(SCRIPT_PATH, '--include-descriptions')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)

    # Count agents with descriptions
    desc_count = sum(
        1 for bundle in data.get('bundles', [])
        for agent in bundle.get('agents', [])
        if agent.get('description') is not None
    )
    assert desc_count > 0, f"Should find descriptions with --include-descriptions, found {desc_count}"


# =============================================================================
# Tests - JSON Validity
# =============================================================================

def test_default_produces_valid_json():
    """Test default mode produces valid JSON."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    try:
        parse_json(result.stdout)
    except Exception as e:
        raise AssertionError(f"Default mode should produce valid JSON: {e}")


def test_with_descriptions_produces_valid_json():
    """Test --include-descriptions produces valid JSON."""
    result = run_script(SCRIPT_PATH, '--include-descriptions')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    try:
        parse_json(result.stdout)
    except Exception as e:
        raise AssertionError(f"With descriptions should produce valid JSON: {e}")


def test_filtered_produces_valid_json():
    """Test filtered mode produces valid JSON."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'agents')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    try:
        parse_json(result.stdout)
    except Exception as e:
        raise AssertionError(f"Filtered mode should produce valid JSON: {e}")


# =============================================================================
# Tests - Bundle Structure
# =============================================================================

def test_bundles_have_required_fields():
    """Test bundles have required fields."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    bundles = data.get('bundles', [])
    assert len(bundles) > 0, "Should have at least one bundle"

    first_bundle = bundles[0]
    assert 'name' in first_bundle, "Bundle should have name"
    assert 'path' in first_bundle, "Bundle should have path"
    assert 'agents' in first_bundle, "Bundle should have agents"
    assert 'commands' in first_bundle, "Bundle should have commands"
    assert 'skills' in first_bundle, "Bundle should have skills"
    assert 'statistics' in first_bundle, "Bundle should have statistics"


# =============================================================================
# Tests - Script Discovery
# =============================================================================

def test_script_count_matches_filesystem():
    """Test script count matches filesystem count."""
    import subprocess

    # Count scripts on filesystem
    find_result = subprocess.run(
        ['find', str(PROJECT_ROOT / 'marketplace' / 'bundles'), '-path', '*/skills/*/scripts/*', '-type', 'f', '(', '-name', '*.sh', '-o', '-name', '*.py', ')'],
        capture_output=True,
        text=True
    )
    expected_count = len([l for l in find_result.stdout.strip().split('\n') if l])

    # Get count from inventory
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    actual_count = data.get('statistics', {}).get('total_scripts', 0)

    assert actual_count == expected_count, f"Script count mismatch: expected {expected_count}, got {actual_count}"


def test_scripts_have_path_formats():
    """Test scripts have path_formats structure."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)

    # Count scripts with path_formats.absolute
    scripts_with_paths = sum(
        1 for bundle in data.get('bundles', [])
        for script in bundle.get('scripts', [])
        if script.get('path_formats', {}).get('absolute') is not None
    )
    total_scripts = data.get('statistics', {}).get('total_scripts', 0)

    assert scripts_with_paths == total_scripts and total_scripts != 0, \
        f"All scripts should have path_formats: {scripts_with_paths} vs {total_scripts}"


# =============================================================================
# Tests - Error Handling
# =============================================================================

def test_invalid_scope_returns_error():
    """Test invalid scope returns error."""
    result = run_script(SCRIPT_PATH, '--scope', 'invalid')
    assert result.returncode != 0, "Invalid scope should return error"


def test_invalid_resource_type_returns_error():
    """Test invalid resource type returns error."""
    result = run_script(SCRIPT_PATH, '--resource-types', 'invalid')
    assert result.returncode != 0, "Invalid resource type should return error"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_default_scan_finds_bundles,
        test_default_scan_finds_agents,
        test_default_scan_finds_commands,
        test_default_scan_finds_skills,
        test_default_scope_is_marketplace,
        test_agents_only_no_commands,
        test_agents_only_no_skills,
        test_agents_only_has_agents,
        test_commands_only_no_agents,
        test_commands_only_has_commands,
        test_skills_only_no_agents,
        test_skills_only_has_skills,
        test_multiple_types_has_both,
        test_no_descriptions_returns_null,
        test_with_descriptions_extracts_desc,
        test_default_produces_valid_json,
        test_with_descriptions_produces_valid_json,
        test_filtered_produces_valid_json,
        test_bundles_have_required_fields,
        test_script_count_matches_filesystem,
        test_scripts_have_path_formats,
        test_invalid_scope_returns_error,
        test_invalid_resource_type_returns_error,
    ])
    sys.exit(runner.run())
