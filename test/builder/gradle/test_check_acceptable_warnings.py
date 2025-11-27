#!/usr/bin/env python3
"""Tests for check-acceptable-warnings.py script (Gradle version).

Migrated from test-check-acceptable-warnings.sh - tests warning categorization using stdin input.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('builder', 'builder-gradle-rules', 'check-acceptable-warnings.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_categorize_mixed_warnings():
    """Test categorizing mixed warnings from fixture file."""
    warnings_json = (FIXTURES_DIR / 'parsed-output-with-warnings.json').read_text()
    acceptable_json = '{"platform_specific": ["*platform encoding*"], "openrewrite": ["*openrewrite*"]}'

    result = run_script(
        SCRIPT_PATH,
        '--acceptable-warnings', acceptable_json,
        input_data=warnings_json
    )
    data = result.json()

    # Should exit 1 because there are fixable warnings
    assert result.returncode == 1, "Mixed warnings should exit with 1"
    assert data['success'], "Success should be True"


def test_no_warnings():
    """Test with no warnings in input."""
    warnings_json = (FIXTURES_DIR / 'parsed-output-no-warnings.json').read_text()

    result = run_script(SCRIPT_PATH, input_data=warnings_json)
    data = result.json()

    assert result.returncode == 0, "No warnings should exit with 0"
    assert data['success'], "Success should be True"
    assert data['total'] == 0, "Should have 0 warnings"
    assert data['fixable'] == 0, "Should have 0 fixable"


def test_all_acceptable():
    """Test with all warnings being acceptable."""
    warnings_json = (FIXTURES_DIR / 'parsed-output-all-acceptable.json').read_text()
    acceptable_json = '{"platform_specific": ["*platform encoding*"], "openrewrite": ["*openrewrite*"]}'

    result = run_script(
        SCRIPT_PATH,
        '--acceptable-warnings', acceptable_json,
        input_data=warnings_json
    )
    data = result.json()

    assert result.returncode == 0, "All acceptable should exit with 0"
    assert data['success'], "Success should be True"
    assert data['fixable'] == 0, "Should have 0 fixable"


def test_javadoc_always_fixable():
    """Test javadoc warnings are always fixable (even with matching pattern)."""
    warnings_json = (FIXTURES_DIR / 'parsed-output-with-warnings.json').read_text()
    acceptable_json = '{"javadoc": ["*"]}'

    result = run_script(
        SCRIPT_PATH,
        '--acceptable-warnings', acceptable_json,
        input_data=warnings_json
    )
    data = result.json()

    # Check fixable count includes javadoc warnings
    assert data['fixable'] > 0, "JavaDoc warnings should be fixable"


def test_deprecation_always_fixable():
    """Test deprecation warnings are always fixable."""
    warnings_json = (FIXTURES_DIR / 'parsed-output-with-warnings.json').read_text()

    result = run_script(SCRIPT_PATH, input_data=warnings_json)
    data = result.json()

    # Get fixable array and check for deprecation
    fixable = data['categorized']['fixable']
    has_deprecation = any(w.get('type') == 'deprecation_warning' for w in fixable)
    assert has_deprecation, "Deprecation warnings should be in fixable list"


def test_unchecked_always_fixable():
    """Test unchecked warnings are always fixable."""
    warnings_json = (FIXTURES_DIR / 'parsed-output-with-warnings.json').read_text()

    result = run_script(SCRIPT_PATH, input_data=warnings_json)
    data = result.json()

    fixable = data['categorized']['fixable']
    has_unchecked = any(w.get('type') == 'unchecked_warning' for w in fixable)
    assert has_unchecked, "Unchecked warnings should be in fixable list"


def test_pattern_matching_contains():
    """Test contains pattern matching (*pattern*)."""
    warnings_json = '{"warnings": [{"type": "other", "message": "Using platform encoding UTF-8", "severity": "WARNING"}]}'
    acceptable_json = '{"platform": ["*platform*"]}'

    result = run_script(
        SCRIPT_PATH,
        '--acceptable-warnings', acceptable_json,
        input_data=warnings_json
    )
    data = result.json()

    assert data['acceptable'] == 1, "Contains pattern should match"


def test_pattern_matching_prefix():
    """Test prefix pattern matching (pattern*)."""
    warnings_json = '{"warnings": [{"type": "other", "message": "Could not resolve artifact", "severity": "WARNING"}]}'
    acceptable_json = '{"dependency": ["Could not resolve*"]}'

    result = run_script(
        SCRIPT_PATH,
        '--acceptable-warnings', acceptable_json,
        input_data=warnings_json
    )
    data = result.json()

    assert data['acceptable'] == 1, "Prefix pattern should match"


def test_empty_acceptable_patterns():
    """Test with empty acceptable patterns."""
    warnings_json = (FIXTURES_DIR / 'parsed-output-with-warnings.json').read_text()

    result = run_script(
        SCRIPT_PATH,
        '--acceptable-warnings', '{}',
        input_data=warnings_json
    )
    data = result.json()

    # Should still categorize - "other" types become unknown
    assert result.returncode == 1, "Should exit 1 with fixable warnings"
    assert data['success'], "Success should be True"


def test_stdin_input():
    """Test stdin input works."""
    result = run_script(
        SCRIPT_PATH,
        input_data='{"warnings": []}'
    )
    data = result.json()

    assert result.returncode == 0, "Stdin input should work"
    assert data['success'], "Success should be True"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_categorize_mixed_warnings,
        test_no_warnings,
        test_all_acceptable,
        test_javadoc_always_fixable,
        test_deprecation_always_fixable,
        test_unchecked_always_fixable,
        test_pattern_matching_contains,
        test_pattern_matching_prefix,
        test_empty_acceptable_patterns,
        test_stdin_input,
    ])
    sys.exit(runner.run())
