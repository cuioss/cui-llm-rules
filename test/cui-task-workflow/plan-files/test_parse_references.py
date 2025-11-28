#!/usr/bin/env python3
"""Tests for parse-references.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_file, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-task-workflow', 'plan-files', 'parse-references.py')


# =============================================================================
# Test Fixtures
# =============================================================================

BASIC_REFERENCES = """# Task References

---

## Loaded Standards

- [Java Core](../../standards/java/core.adoc)
- [CDI Standards](../../standards/java/cdi.adoc)
- [Testing Standards](../../standards/testing/core.adoc)

## Related ADRs

- [ADR-001](../adr/ADR-001-jwt-implementation.md) - Status: accepted
- [ADR-002](../adr/ADR-002-token-storage.md) - Status: proposed

## Related Interfaces

- [IF-AUTH-001](../interfaces/IF-AUTH-001-authentication.md)
- [IF-AUTH-002](../interfaces/IF-AUTH-002-authorization.md)

## Related Files

- [JwtService.java](src/main/java/com/example/JwtService.java) - Main JWT service
- [SecurityConfig.java](src/main/java/com/example/SecurityConfig.java) - Security configuration

## External Links

- [JWT Introduction](https://jwt.io/introduction)
- [RFC 7519](https://tools.ietf.org/html/rfc7519)
"""

EMPTY_REFERENCES = """# Task References

---

No references loaded yet.
"""

STANDARDS_ONLY = """# Task References

## Standards

- [JavaScript Core](../../standards/javascript/core.adoc)
- [CSS Standards](../../standards/css/core.adoc)
"""

ADR_NO_STATUS = """# Task References

## ADRs

- [ADR-001](../adr/ADR-001.md)
- [ADR-002](../adr/ADR-002.md)
"""

ALL_TYPES = """# Task References

## Standards

- [Standard 1](path1.adoc)

## ADRs

- [ADR-001](adr1.md) - Status: accepted

## Interfaces

- [IF-001](if1.md)

## Related Files

- [File.java](File.java) - Description

## External Links

- [Link](https://example.com)
"""

ALTERNATIVE_NAMES = """# Task References

## Loaded Standards

- [Standard 1](path1.adoc)

## Related ADR

- [ADR-001](adr1.md)

## Related Interface

- [IF-001](if1.md)

## Related File

- [File.java](File.java)

## External References

- [Link](https://example.com)
"""


# =============================================================================
# Tests
# =============================================================================

def test_parse_basic_references():
    """Test parsing a references file with all sections."""
    temp_file = create_temp_file(BASIC_REFERENCES)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        # Check standards
        assert len(data['standards']) == 3
        assert data['standards'][0]['name'] == 'Java Core'
        assert data['standards'][0]['path'] == '../../standards/java/core.adoc'
        assert data['standards'][0]['type'] == 'standard'

        # Check ADRs
        assert len(data['adrs']) == 2
        assert data['adrs'][0]['id'] == 'ADR-001'
        assert data['adrs'][0]['status'] == 'accepted'
        assert data['adrs'][1]['status'] == 'proposed'

        # Check interfaces
        assert len(data['interfaces']) == 2
        assert data['interfaces'][0]['name'] == 'IF-AUTH-001'

        # Check related files
        assert len(data['related_files']) == 2
        assert data['related_files'][0]['name'] == 'JwtService.java'
        assert data['related_files'][0]['description'] == 'Main JWT service'

        # Check external links
        assert len(data['external_links']) == 2
        assert data['external_links'][0]['name'] == 'JWT Introduction'
        assert data['external_links'][0]['url'] == 'https://jwt.io/introduction'

        # Check summary
        assert data['summary']['total_references'] == 11
        assert data['summary']['standards_count'] == 3
        assert data['summary']['adrs_count'] == 2
    finally:
        temp_file.unlink()


def test_parse_empty_references():
    """Test parsing an empty references file."""
    temp_file = create_temp_file(EMPTY_REFERENCES)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert len(data['standards']) == 0
        assert len(data['adrs']) == 0
        assert len(data['interfaces']) == 0
        assert len(data['related_files']) == 0
        assert len(data['external_links']) == 0
        assert data['summary']['total_references'] == 0

        # Check validation
        assert data['validation']['has_standards'] is False
        assert data['validation']['has_adrs'] is False
    finally:
        temp_file.unlink()


def test_parse_standards_only():
    """Test parsing a file with only standards."""
    temp_file = create_temp_file(STANDARDS_ONLY)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert len(data['standards']) == 2
        assert data['standards'][0]['name'] == 'JavaScript Core'
        assert data['validation']['has_standards'] is True
        assert data['validation']['has_adrs'] is False
    finally:
        temp_file.unlink()


def test_parse_adr_without_status():
    """Test parsing ADRs without status."""
    temp_file = create_temp_file(ADR_NO_STATUS)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert len(data['adrs']) == 2
        assert data['adrs'][0]['status'] == 'unknown'
        assert data['adrs'][1]['status'] == 'unknown'
    finally:
        temp_file.unlink()


def test_all_references_combined():
    """Test that all_references contains all items."""
    temp_file = create_temp_file(ALL_TYPES)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        # all_references should contain all 5 items
        assert len(data['all_references']) == 5

        # Check types are preserved
        types = [r['type'] for r in data['all_references']]
        assert 'standard' in types
        assert 'adr' in types
        assert 'interface' in types
        assert 'file' in types
        assert 'external' in types
    finally:
        temp_file.unlink()


def test_file_not_found():
    """Test error handling for missing file."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path/references.md')
    assert not result.success
    assert result.returncode == 1

    data = result.json()
    assert 'error' in data
    assert data['error']['type'] == 'file_not_found'


def test_parse_alternative_section_names():
    """Test parsing with alternative section naming."""
    temp_file = create_temp_file(ALTERNATIVE_NAMES)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        # Should still parse with singular/alternative names
        assert len(data['standards']) == 1
        assert len(data['adrs']) == 1
        assert len(data['interfaces']) == 1
        assert len(data['related_files']) == 1
        assert len(data['external_links']) == 1
    finally:
        temp_file.unlink()


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_basic_references,
        test_parse_empty_references,
        test_parse_standards_only,
        test_parse_adr_without_status,
        test_all_references_combined,
        test_file_not_found,
        test_parse_alternative_section_names,
    ])
    sys.exit(runner.run())
