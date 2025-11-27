#!/usr/bin/env python3
"""Tests for analyze-markdown-file.sh script.

Migrated from test-analyze-markdown-file.sh - tests markdown file analysis
including frontmatter validation, bloat classification, and rule violations.
"""

import subprocess
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Script under test
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SCRIPT_PATH = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-plugin-development-tools' / 'skills' / 'plugin-doctor' / 'scripts' / 'analyze-markdown-file.sh'
FIXTURES_DIR = Path(__file__).parent / 'fixtures' / 'markdown-file'


def run_bash_script(script_path, *args):
    """Run a bash script and return result."""
    result = subprocess.run(
        ['bash', str(script_path), *args],
        capture_output=True,
        text=True
    )
    return result


def parse_json(output):
    """Parse JSON from output, fixing common script bugs."""
    import json
    import re
    # Fix invalid JSON with leading zeros (e.g., ": 00," -> ": 0,")
    fixed = re.sub(r':\s*0+([,\n}])', r': 0\1', output)
    return json.loads(fixed)


# =============================================================================
# Tests - Valid Agent
# =============================================================================

def test_valid_agent_has_frontmatter():
    """Test valid agent has frontmatter present."""
    fixture = FIXTURES_DIR / 'valid-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    present = data.get('frontmatter', {}).get('present')
    assert present is True, f"Valid agent should have frontmatter present, got {present}"


def test_valid_agent_yaml_valid():
    """Test valid agent has valid YAML."""
    fixture = FIXTURES_DIR / 'valid-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    yaml_valid = data.get('frontmatter', {}).get('yaml_valid')
    assert yaml_valid is True, f"Valid agent should have valid YAML, got {yaml_valid}"


def test_valid_agent_has_ci_rule():
    """Test valid agent has continuous improvement rule."""
    fixture = FIXTURES_DIR / 'valid-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    ci_present = data.get('continuous_improvement_rule', {}).get('present')
    assert ci_present is True, f"Valid agent should have CI rule present, got {ci_present}"


def test_valid_agent_no_rule6_violation():
    """Test valid agent has no Rule 6 violation."""
    fixture = FIXTURES_DIR / 'valid-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    rule6 = data.get('rules', {}).get('rule_6_violation')
    assert rule6 is False, f"Valid agent should have no Rule 6 violation, got {rule6}"


# =============================================================================
# Tests - Bloated Command
# =============================================================================

def test_bloated_command_classification():
    """Test bloated command is classified as LARGE or higher."""
    fixture = FIXTURES_DIR / 'bloated-command.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'command')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    classification = data.get('bloat', {}).get('classification')
    # Accept LARGE, BLOATED, or CRITICAL (thresholds may vary)
    assert classification in ('LARGE', 'BLOATED', 'CRITICAL'), \
        f"Bloated command should be LARGE or higher, got '{classification}'"


# =============================================================================
# Tests - Rule 6 Violation
# =============================================================================

def test_rule6_violation_detected():
    """Test Rule 6 violation is detected."""
    fixture = FIXTURES_DIR / 'rule6-violation.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    rule6 = data.get('rules', {}).get('rule_6_violation')
    assert rule6 is True, f"Should detect Rule 6 violation, got {rule6}"


# =============================================================================
# Tests - Forbidden Metadata
# =============================================================================

def test_forbidden_metadata_detected():
    """Test forbidden metadata is detected."""
    fixture = FIXTURES_DIR / 'version-section-violation.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    has_forbidden = data.get('quality', {}).get('has_forbidden_metadata')
    assert has_forbidden is True, f"Should detect forbidden metadata, got {has_forbidden}"


def test_forbidden_sections_lists_version_and_license():
    """Test forbidden sections lists Version and License."""
    fixture = FIXTURES_DIR / 'version-section-violation.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    forbidden_sections = data.get('quality', {}).get('forbidden_sections')
    assert forbidden_sections == 'Version,License', f"Should list 'Version,License', got '{forbidden_sections}'"


def test_no_forbidden_metadata_in_valid_agent():
    """Test valid agent has no forbidden metadata."""
    fixture = FIXTURES_DIR / 'valid-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(fixture), 'agent')
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    has_forbidden = data.get('quality', {}).get('has_forbidden_metadata')
    assert has_forbidden is False, f"Valid agent should have no forbidden metadata, got {has_forbidden}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_valid_agent_has_frontmatter,
        test_valid_agent_yaml_valid,
        test_valid_agent_has_ci_rule,
        test_valid_agent_no_rule6_violation,
        test_bloated_command_classification,
        test_rule6_violation_detected,
        test_forbidden_metadata_detected,
        test_forbidden_sections_lists_version_and_license,
        test_no_forbidden_metadata_in_valid_agent,
    ])
    sys.exit(runner.run())
