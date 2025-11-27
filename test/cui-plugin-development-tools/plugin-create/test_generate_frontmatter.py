#!/usr/bin/env python3
"""Tests for generate-frontmatter.py script.

Migrated from test-generate-frontmatter.sh - tests frontmatter generation
for agents, commands, and skills with various input configurations.
"""

import json
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-plugin-development-tools', 'plugin-create', 'generate-frontmatter.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests - Agent Frontmatter
# =============================================================================

def test_agent_frontmatter_with_all_fields():
    """Test agent frontmatter with all fields."""
    fixture = FIXTURES_DIR / 'agent-answers-full.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    input_json = fixture.read_text()
    result = run_script(SCRIPT_PATH, 'agent', input_json)

    assert 'model: sonnet' in result.stdout, "Agent frontmatter should include model field"


def test_agent_tools_comma_separated():
    """Test agent tools are comma-separated, not array syntax."""
    fixture = FIXTURES_DIR / 'agent-answers-full.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    input_json = fixture.read_text()
    result = run_script(SCRIPT_PATH, 'agent', input_json)

    # Check comma-separated format
    import re
    has_comma_separated = re.search(r'tools: [A-Za-z]+(, [A-Za-z]+)*', result.stdout) is not None
    has_array_syntax = '[' in result.stdout

    assert has_comma_separated, "Tools should be comma-separated"
    assert not has_array_syntax, "Tools should not use array syntax"


def test_agent_without_optional_model():
    """Test agent without optional model field."""
    fixture = FIXTURES_DIR / 'agent-answers-no-model.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    input_json = fixture.read_text()
    result = run_script(SCRIPT_PATH, 'agent', input_json)

    assert 'name: test-agent' in result.stdout, "Agent frontmatter should include name"


def test_agent_special_characters_in_description():
    """Test special characters in description are handled."""
    fixture = FIXTURES_DIR / 'agent-answers-special-chars.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    input_json = fixture.read_text()
    result = run_script(SCRIPT_PATH, 'agent', input_json)

    assert 'quotes' in result.stdout, "Should handle special characters in description"


# =============================================================================
# Tests - Command Frontmatter
# =============================================================================

def test_command_frontmatter_no_tools():
    """Test command frontmatter has no tools field."""
    fixture = FIXTURES_DIR / 'command-answers.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    input_json = fixture.read_text()
    result = run_script(SCRIPT_PATH, 'command', input_json)

    assert 'name: test-command' in result.stdout, "Command frontmatter should include name"
    assert 'tools:' not in result.stdout, "Command frontmatter should not have tools field"


# =============================================================================
# Tests - Skill Frontmatter
# =============================================================================

def test_skill_with_allowed_tools():
    """Test skill with allowed-tools."""
    fixture = FIXTURES_DIR / 'skill-answers-with-tools.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    input_json = fixture.read_text()
    result = run_script(SCRIPT_PATH, 'skill', input_json)

    assert 'allowed-tools: Read, Grep' in result.stdout, "Skill should have allowed-tools"


def test_skill_without_tools():
    """Test skill without tools omits allowed-tools."""
    fixture = FIXTURES_DIR / 'skill-answers-no-tools.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    input_json = fixture.read_text()
    result = run_script(SCRIPT_PATH, 'skill', input_json)

    assert 'name: test-skill' in result.stdout, "Skill frontmatter should include name"
    assert 'allowed-tools:' not in result.stdout, "Skill without tools should omit allowed-tools"


# =============================================================================
# Tests - Error Handling
# =============================================================================

def test_empty_tools_array_error():
    """Test empty tools array produces error or warning."""
    input_json = '{"name": "test", "description": "Test", "tools": []}'
    result = run_script(SCRIPT_PATH, 'agent', input_json)

    output = result.stdout.lower() + result.stderr.lower()
    has_error = 'error' in output or 'warning' in output or 'at least one' in output
    assert has_error, "Should error or warn on empty tools array"


def test_invalid_component_type_error():
    """Test invalid component type produces error."""
    input_json = '{"name": "test", "description": "Test"}'
    result = run_script(SCRIPT_PATH, 'invalid-type', input_json)

    output = result.stdout.lower() + result.stderr.lower()
    has_error = 'error' in output or 'invalid' in output or 'unknown' in output
    assert has_error, "Should error on invalid component type"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_agent_frontmatter_with_all_fields,
        test_agent_tools_comma_separated,
        test_agent_without_optional_model,
        test_agent_special_characters_in_description,
        test_command_frontmatter_no_tools,
        test_skill_with_allowed_tools,
        test_skill_without_tools,
        test_empty_tools_array_error,
        test_invalid_component_type_error,
    ])
    sys.exit(runner.run())
