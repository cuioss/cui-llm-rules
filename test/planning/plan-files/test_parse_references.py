#!/usr/bin/env python3
"""Tests for parse-references.py script (TOON format)."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_file, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'plan-files', 'parse-references.py')


# =============================================================================
# Test Fixtures (TOON format)
# =============================================================================

BASIC_REFERENCES = """# Plan References

issue: #123
issue_url: https://github.com/org/repo/issues/123
issue_title: Implement JWT Authentication
branch: feature/jwt-auth
base_branch: main

implementation_files[3]:
- src/main/java/JwtService.java
- src/main/java/TokenValidator.java
- src/main/java/SecurityConfig.java

config_files[1]:
- src/main/resources/application.properties

test_files[2]:
- src/test/java/JwtServiceTest.java
- src/test/java/TokenValidatorTest.java

adrs[2]{id,path,status}:
ADR-001,../adr/ADR-001-jwt-implementation.md,accepted
ADR-002,../adr/ADR-002-token-storage.md,proposed

interfaces[2]{name,path}:
IF-AUTH-001,../interfaces/IF-AUTH-001-authentication.md
IF-AUTH-002,../interfaces/IF-AUTH-002-authorization.md

external_docs[2]{name,url}:
JWT Introduction,https://jwt.io/introduction
RFC 7519,https://tools.ietf.org/html/rfc7519

dependencies[1]:
- io.jsonwebtoken:jjwt:0.11.5

related_plans[0]:
"""

EMPTY_REFERENCES = """# Plan References

issue: (not set)
issue_url: (not set)
issue_title: (not set)
branch: (not set)
base_branch: main

implementation_files[0]:

config_files[0]:

test_files[0]:

adrs[0]{id,path,status}:

interfaces[0]{name,path}:

external_docs[0]{name,url}:

dependencies[0]:

related_plans[0]:
"""

FILES_ONLY = """# Plan References

issue: (not set)
issue_url: (not set)
issue_title: (not set)
branch: feature/test
base_branch: main

implementation_files[2]:
- src/main/java/Foo.java
- src/main/java/Bar.java

config_files[0]:

test_files[1]:
- src/test/java/FooTest.java

adrs[0]{id,path,status}:

interfaces[0]{name,path}:

external_docs[0]{name,url}:

dependencies[0]:

related_plans[0]:
"""

ALL_TYPES = """# Plan References

issue: #456
issue_url: https://github.com/org/repo/issues/456
issue_title: Feature Request
branch: feature/all-types
base_branch: main

implementation_files[1]:
- src/main/java/Service.java

config_files[1]:
- config.yaml

test_files[1]:
- src/test/java/ServiceTest.java

adrs[1]{id,path,status}:
ADR-001,../adr/ADR-001.md,accepted

interfaces[1]{name,path}:
IF-001,../interfaces/IF-001.md

external_docs[1]{name,url}:
Documentation,https://docs.example.com

dependencies[1]:
- com.example:library:1.0.0

related_plans[1]:
- jwt-auth
"""


# =============================================================================
# Tests
# =============================================================================

def test_parse_basic_references():
    """Test parsing a TOON references file with all sections."""
    temp_file = create_temp_file(BASIC_REFERENCES, suffix='.toon')
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        # Check issue
        assert data['issue']['id'] == '#123'
        assert data['issue']['url'] == 'https://github.com/org/repo/issues/123'
        assert data['issue']['title'] == 'Implement JWT Authentication'

        # Check branch
        assert data['branch'] == 'feature/jwt-auth'
        assert data['base_branch'] == 'main'

        # Check implementation files
        assert len(data['implementation_files']) == 3
        assert 'src/main/java/JwtService.java' in data['implementation_files']

        # Check config files
        assert len(data['config_files']) == 1

        # Check test files
        assert len(data['test_files']) == 2

        # Check ADRs
        assert len(data['adrs']) == 2
        assert data['adrs'][0]['id'] == 'ADR-001'
        assert data['adrs'][0]['status'] == 'accepted'
        assert data['adrs'][1]['status'] == 'proposed'

        # Check interfaces
        assert len(data['interfaces']) == 2
        assert data['interfaces'][0]['name'] == 'IF-AUTH-001'

        # Check external links
        assert len(data['external_links']) == 2
        assert data['external_links'][0]['name'] == 'JWT Introduction'
        assert data['external_links'][0]['url'] == 'https://jwt.io/introduction'

        # Check dependencies
        assert len(data['dependencies']) == 1

        # Check summary
        assert data['summary']['implementation_files_count'] == 3
        assert data['summary']['adrs_count'] == 2

        # Check format
        assert data['format'] == 'toon'
    finally:
        temp_file.unlink()


def test_parse_empty_references():
    """Test parsing an empty TOON references file."""
    temp_file = create_temp_file(EMPTY_REFERENCES, suffix='.toon')
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        # Issue should be empty (not set values filtered)
        assert data['issue']['id'] == ''
        assert data['issue']['url'] == ''

        # Lists should be empty
        assert len(data['implementation_files']) == 0
        assert len(data['adrs']) == 0
        assert len(data['interfaces']) == 0
        assert len(data['external_links']) == 0
        assert data['summary']['total_references'] == 0

        # Check validation
        assert data['validation']['has_implementation_files'] is False
        assert data['validation']['has_adrs'] is False
    finally:
        temp_file.unlink()


def test_parse_files_only():
    """Test parsing a TOON file with only files."""
    temp_file = create_temp_file(FILES_ONLY, suffix='.toon')
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert len(data['implementation_files']) == 2
        assert len(data['test_files']) == 1
        assert data['validation']['has_implementation_files'] is True
        assert data['validation']['has_test_files'] is True
        assert data['validation']['has_adrs'] is False
    finally:
        temp_file.unlink()


def test_all_references_combined():
    """Test that all_references contains all items."""
    temp_file = create_temp_file(ALL_TYPES, suffix='.toon')
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        # related_files combines implementation, config, test files
        assert len(data['related_files']) == 3

        # all_references contains files + adrs + interfaces + external
        # 3 files + 1 adr + 1 interface + 1 external = 6
        assert len(data['all_references']) == 6

        # Check types are preserved
        types = [r['type'] for r in data['all_references']]
        assert 'implementation' in types
        assert 'config' in types
        assert 'test' in types
        assert 'adr' in types
        assert 'interface' in types
        assert 'external' in types
    finally:
        temp_file.unlink()


def test_file_not_found():
    """Test error handling for missing file."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path/references.toon')
    assert not result.success
    assert result.returncode == 1

    data = result.json()
    assert 'error' in data
    assert data['error']['type'] == 'file_not_found'


def test_directory_input():
    """Test that script accepts directory and finds references.toon."""
    import tempfile
    import os

    # Create temp directory with references.toon
    with tempfile.TemporaryDirectory() as tmpdir:
        refs_file = Path(tmpdir) / 'references.toon'
        refs_file.write_text(FILES_ONLY)

        result = run_script(SCRIPT_PATH, tmpdir)
        assert result.success
        data = result.json()

        assert len(data['implementation_files']) == 2
        assert data['branch'] == 'feature/test'


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_basic_references,
        test_parse_empty_references,
        test_parse_files_only,
        test_all_references_combined,
        test_file_not_found,
        test_directory_input,
    ])
    sys.exit(runner.run())
