#!/usr/bin/env python3
"""Tests for parse-config.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_file, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'plan-files', 'parse-config.py')


# =============================================================================
# Test Fixtures
# =============================================================================

BASIC_CONFIG = """# Task Configuration

**Plan Type**: Implementation

---

## Build Configuration

| Property | Value |
|----------|-------|
| Technology | Java |
| Build System | Maven |

## Workflow Configuration

| Property | Value |
|----------|-------|
| Compatibility | deprecations |
| Commit Strategy | fine-granular |
| Finalizing | pr-workflow |

## Context

| Property | Value |
|----------|-------|
| Branch | feature/jwt-auth |
| Issue | [PROJ-123](https://github.com/org/repo/issues/123) |
"""

SIMPLE_PLAN_CONFIG = """# Task Configuration

**Plan Type**: Simple

---

## Build Configuration

| Property | Value |
|----------|-------|
| Technology | JavaScript |
| Build System | npm |

## Context

| Property | Value |
|----------|-------|
| Branch | fix/bug-123 |
"""

MINIMAL_CONFIG = """# Task Configuration

**Plan Type**: Implementation

## Context

| Property | Value |
|----------|-------|
| Branch | main |
"""

ISSUE_LINK_CONFIG = """# Task Configuration

**Plan Type**: Implementation

## Context

| Property | Value |
|----------|-------|
| Branch | feature/test |
| Issue | [#456](https://github.com/org/repo/issues/456) |
"""

ISSUE_PLAIN_CONFIG = """# Task Configuration

**Plan Type**: Implementation

## Context

| Property | Value |
|----------|-------|
| Branch | feature/test |
| Issue | JIRA-789 |
"""

CUSTOM_PROPERTY_CONFIG = """# Task Configuration

**Plan Type**: Implementation

## Build Configuration

| Property | Value |
|----------|-------|
| Technology | Java |
| Build System | Gradle |
| Custom Property | custom-value |

## Context

| Property | Value |
|----------|-------|
| Branch | main |
"""


# =============================================================================
# Tests
# =============================================================================

def test_parse_basic_config():
    """Test parsing a basic config with all sections."""
    temp_file = create_temp_file(BASIC_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        # Check configuration
        config = data['configuration']
        assert config['plan_type'] == 'implementation'
        assert config['technology'] == 'java'
        assert config['build_system'] == 'maven'
        assert config['compatibility'] == 'deprecations'
        assert config['commit_strategy'] == 'fine-granular'
        assert config['finalizing'] == 'pr-workflow'
        assert config['branch'] == 'feature/jwt-auth'
        assert config['issue'] == 'PROJ-123'
        assert config['issue_url'] == 'https://github.com/org/repo/issues/123'

        # Check validation
        validation = data['validation']
        assert validation['has_plan_type'] is True
        assert validation['has_technology'] is True
        assert validation['has_build_system'] is True
        assert validation['has_branch'] is True
        assert validation['has_issue'] is True
        assert validation['is_complete'] is True
    finally:
        temp_file.unlink()


def test_parse_simple_plan_type():
    """Test parsing simple plan type."""
    temp_file = create_temp_file(SIMPLE_PLAN_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert data['configuration']['plan_type'] == 'simple'
        assert data['configuration']['technology'] == 'javascript'
        assert data['configuration']['build_system'] == 'npm'
        assert data['configuration']['branch'] == 'fix/bug-123'
    finally:
        temp_file.unlink()


def test_parse_minimal_config():
    """Test parsing a minimal config."""
    temp_file = create_temp_file(MINIMAL_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        config = data['configuration']
        assert config['plan_type'] == 'implementation'
        assert config['technology'] == 'none'
        assert config['build_system'] == 'none'
        assert config['branch'] == 'main'
        assert config['issue'] == 'none'

        validation = data['validation']
        assert validation['has_plan_type'] is True
        assert validation['has_technology'] is False
        assert validation['has_build_system'] is False
        assert validation['has_branch'] is True
        assert validation['is_complete'] is True
    finally:
        temp_file.unlink()


def test_parse_issue_formats():
    """Test parsing different issue formats."""
    # Test markdown link format
    temp_file = create_temp_file(ISSUE_LINK_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        data = result.json()
        assert data['configuration']['issue'] == '#456'
        assert data['configuration']['issue_url'] == 'https://github.com/org/repo/issues/456'
    finally:
        temp_file.unlink()

    # Test plain text format
    temp_file2 = create_temp_file(ISSUE_PLAIN_CONFIG)
    try:
        result2 = run_script(SCRIPT_PATH, str(temp_file2))
        data2 = result2.json()
        assert data2['configuration']['issue'] == 'JIRA-789'
        assert data2['configuration']['issue_url'] == ''
    finally:
        temp_file2.unlink()


def test_file_not_found():
    """Test error handling for missing file."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path/config.md')
    assert not result.success
    assert result.returncode == 1

    data = result.json()
    assert 'error' in data
    assert data['error']['type'] == 'file_not_found'


def test_raw_section_data():
    """Test that raw section data is preserved."""
    temp_file = create_temp_file(CUSTOM_PROPERTY_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        # Check raw data includes custom property
        raw = data['raw']
        assert 'build_configuration' in raw
        assert raw['build_configuration'].get('custom_property') == 'custom-value'
    finally:
        temp_file.unlink()


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_basic_config,
        test_parse_simple_plan_type,
        test_parse_minimal_config,
        test_parse_issue_formats,
        test_file_not_found,
        test_raw_section_data,
    ])
    sys.exit(runner.run())
