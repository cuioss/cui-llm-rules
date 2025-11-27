#!/usr/bin/env python3
"""Tests for check-acceptable-warnings.py script.

Migrated from test-check-acceptable-warnings.sh (cui-maven-rules) - tests warning categorization
using inline JSON arguments. The script receives warnings and patterns via stdin or arguments,
not via file paths.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('builder', 'builder-maven-rules', 'check-acceptable-warnings.py')


# =============================================================================
# Tests using inline JSON (script's actual interface)
# =============================================================================

def test_acceptable_pattern_match():
    """Test categorize warning as acceptable via pattern match."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"other","message":"The POM for org.example:lib is missing","severity":"WARNING"}]',
        '--patterns', '["The POM for org.example:lib is missing"]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['acceptable'] == 1, "Should have 1 acceptable"
    assert data['fixable'] == 0, "Should have 0 fixable"


def test_javadoc_always_fixable():
    """Test javadoc warnings are always fixable (even with matching pattern)."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"javadoc_warning","message":"Missing @param tag","severity":"WARNING"}]',
        '--patterns', '["Missing @param tag"]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['fixable'] == 1, "Should have 1 fixable"
    assert data['acceptable'] == 0, "Should have 0 acceptable"


def test_unknown_warning():
    """Test unknown warning categorization."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"other","message":"Some random warning","severity":"WARNING"}]',
        '--patterns', '[]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['unknown'] == 1, "Should have 1 unknown"


def test_empty_warnings():
    """Test empty warnings array."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[]',
        '--patterns', '[]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['total'] == 0, "Should have total=0"


def test_filter_warning_severity():
    """Test filter only WARNING severity."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"other","message":"error msg","severity":"ERROR"},{"type":"other","message":"warn msg","severity":"WARNING"}]',
        '--patterns', '[]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['total'] == 1, "Should filter to only 1 WARNING"


def test_acceptable_warnings_object():
    """Test acceptable_warnings object flattening."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"other","message":"Missing POM","severity":"WARNING"}]',
        '--acceptable-warnings', '{"transitive_dependency":["Missing POM"],"plugin_compatibility":[]}'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['acceptable'] == 1, "Should have 1 acceptable"


def test_regex_pattern():
    """Test regex pattern matching."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"other","message":"Using platform encoding UTF-8","severity":"WARNING"}]',
        '--patterns', '["Using platform encoding.*"]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['acceptable'] == 1, "Should match via regex"


def test_strip_warning_prefix():
    """Test strip [WARNING] prefix from patterns."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"other","message":"Some warning text","severity":"WARNING"}]',
        '--patterns', '["[WARNING] Some warning text"]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['acceptable'] == 1, "Should match after stripping [WARNING]"


def test_openrewrite_info_acceptable():
    """Test openrewrite_info is acceptable."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"openrewrite_info","message":"Recipe applied","severity":"WARNING"}]',
        '--patterns', '[]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['acceptable'] == 1, "openrewrite_info should be acceptable"


def test_exit_code_clean():
    """Test exit code 0 when no fixable/unknown."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"other","message":"accepted warn","severity":"WARNING"}]',
        '--patterns', '["accepted warn"]'
    )

    assert result.returncode == 0, "Should exit 0 when no fixable/unknown warnings"


def test_exit_code_fixable():
    """Test exit code 1 when fixable warnings exist."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"javadoc_warning","message":"fix me","severity":"WARNING"}]',
        '--patterns', '[]'
    )

    assert result.returncode == 1, "Should exit 1 when fixable warnings exist"


def test_categorized_output_structure():
    """Test categorized output structure."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"javadoc_warning","message":"fix","severity":"WARNING"},{"type":"other","message":"accept","severity":"WARNING"}]',
        '--patterns', '["accept"]'
    )
    data = result.json()

    assert 'categorized' in data, "Should have categorized key"
    assert 'acceptable' in data['categorized'], "Should have categorized.acceptable"
    assert 'fixable' in data['categorized'], "Should have categorized.fixable"
    assert 'unknown' in data['categorized'], "Should have categorized.unknown"


def test_invalid_json_warnings():
    """Test invalid JSON error handling."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', 'not json',
        '--patterns', '[]'
    )
    data = result.json()

    assert not data['success'], "Should fail with invalid JSON"
    assert 'error' in data, "Should have error key"


def test_deprecation_warning_fixable():
    """Test deprecation warnings are always fixable."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"deprecation_warning","message":"API is deprecated","severity":"WARNING"}]',
        '--patterns', '["API is deprecated"]'  # Pattern should be ignored
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['fixable'] == 1, "Deprecation should be fixable"
    assert data['acceptable'] == 0, "Deprecation should not be acceptable"


def test_unchecked_warning_fixable():
    """Test unchecked warnings are always fixable."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '[{"type":"unchecked_warning","message":"unchecked cast","severity":"WARNING"}]',
        '--patterns', '[]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['fixable'] == 1, "Unchecked should be fixable"


def test_multiple_warnings_mixed():
    """Test categorizing multiple warnings with mixed types."""
    result = run_script(
        SCRIPT_PATH,
        '--warnings', '''[
            {"type":"javadoc_warning","message":"missing tag","severity":"WARNING"},
            {"type":"other","message":"accepted pattern","severity":"WARNING"},
            {"type":"other","message":"unknown warn","severity":"WARNING"}
        ]''',
        '--patterns', '["accepted pattern"]'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['total'] == 3, "Should have 3 total warnings"
    assert data['fixable'] == 1, "Should have 1 fixable (javadoc)"
    assert data['acceptable'] == 1, "Should have 1 acceptable (pattern match)"
    assert data['unknown'] == 1, "Should have 1 unknown"


def test_stdin_input():
    """Test stdin input method."""
    result = run_script(
        SCRIPT_PATH,
        input_data='{"warnings":[{"type":"other","message":"test warn","severity":"WARNING"}],"patterns":["test warn"]}'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['acceptable'] == 1, "Should have 1 acceptable"


def test_stdin_with_acceptable_warnings_object():
    """Test stdin with acceptable_warnings object."""
    result = run_script(
        SCRIPT_PATH,
        input_data='{"warnings":[{"type":"other","message":"dep warn","severity":"WARNING"}],"acceptable_warnings":{"transitive_dependency":["dep warn"]}}'
    )
    data = result.json()

    assert data['success'], "Should succeed"
    assert data['acceptable'] == 1, "Should have 1 acceptable"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_acceptable_pattern_match,
        test_javadoc_always_fixable,
        test_unknown_warning,
        test_empty_warnings,
        test_filter_warning_severity,
        test_acceptable_warnings_object,
        test_regex_pattern,
        test_strip_warning_prefix,
        test_openrewrite_info_acceptable,
        test_exit_code_clean,
        test_exit_code_fixable,
        test_categorized_output_structure,
        test_invalid_json_warnings,
        test_deprecation_warning_fixable,
        test_unchecked_warning_fixable,
        test_multiple_warnings_mixed,
        test_stdin_input,
        test_stdin_with_acceptable_warnings_object,
    ])
    sys.exit(runner.run())
