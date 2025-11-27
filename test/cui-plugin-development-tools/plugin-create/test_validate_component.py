#!/usr/bin/env python3
"""Tests for validate-component.py script.

Migrated from test-validate-component.sh - tests component validation.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-plugin-development-tools', 'plugin-create', 'validate-component.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_valid_agent():
    """Test valid agent validation."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'valid-agent.md'),
        'agent'
    )
    data = result.json()
    assert data.get('valid') is True, "Valid agent validation"


def test_valid_agent_no_model():
    """Test valid agent without model."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'valid-agent-no-model.md'),
        'agent'
    )
    data = result.json()
    assert data.get('valid') is True, "Valid agent without model"


def test_agent_prohibited_task_tool():
    """Test agent with prohibited Task tool is invalid."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'invalid-agent-task-tool.md'),
        'agent'
    )
    data = result.json()
    assert data.get('valid') is False, "Agent with prohibited Task tool should be invalid"


def test_agent_self_invocation():
    """Test agent with self-invocation pattern is invalid."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'invalid-agent-self-invoke.md'),
        'agent'
    )
    data = result.json()
    assert data.get('valid') is False, "Agent with self-invocation should be invalid"


def test_agent_missing_frontmatter():
    """Test agent missing frontmatter is invalid."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'invalid-agent-no-frontmatter.md'),
        'agent'
    )
    data = result.json()
    assert data.get('valid') is False, "Agent missing frontmatter should be invalid"


def test_valid_command():
    """Test valid command validation."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'valid-command.md'),
        'command'
    )
    data = result.json()
    assert data.get('valid') is True, "Valid command validation"


def test_command_missing_workflow():
    """Test command missing WORKFLOW section is invalid."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'invalid-command-missing-section.md'),
        'command'
    )
    data = result.json()
    assert data.get('valid') is False, "Command missing WORKFLOW should be invalid"


def test_valid_skill():
    """Test valid skill validation."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'valid-skill.md'),
        'skill'
    )
    data = result.json()
    assert data.get('valid') is True, "Valid skill validation"


def test_skill_bad_frontmatter():
    """Test skill with bad frontmatter is invalid."""
    result = run_script(
        SCRIPT_PATH,
        str(FIXTURES_DIR / 'invalid-skill-bad-frontmatter.md'),
        'skill'
    )
    data = result.json()
    assert data.get('valid') is False, "Skill with bad frontmatter should be invalid"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_valid_agent,
        test_valid_agent_no_model,
        test_agent_prohibited_task_tool,
        test_agent_self_invocation,
        test_agent_missing_frontmatter,
        test_valid_command,
        test_command_missing_workflow,
        test_valid_skill,
        test_skill_bad_frontmatter,
    ])
    sys.exit(runner.run())
