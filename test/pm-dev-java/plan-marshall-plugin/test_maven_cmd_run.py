#!/usr/bin/env python3
"""Tests for maven_cmd_run.py format functions.

Tests TOON format compliance per build-return.md specification:
- Tab-separated key-value pairs
- Field name 'command' (not 'command_executed')
- Warning filtering by mode
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Add script path for direct import
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'pm-dev-java' / 'skills' / 'plan-marshall-plugin' / 'scripts'
sys.path.insert(0, str(SCRIPT_DIR))

from maven_cmd_run import (
    format_toon_success,
    format_toon_error,
    format_json_success,
    format_json_error,
    filter_warnings,
    is_warning_accepted
)


# =============================================================================
# Test: format_toon_success
# =============================================================================

def test_format_toon_success_uses_tab_separator():
    """Test that success format uses tab-separated key-value pairs."""
    result = format_toon_success(
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=0,
        duration_seconds=45,
        command="./mvnw clean verify"
    )

    # Verify tab separation
    lines = result.split('\n')
    for line in lines:
        assert '\t' in line, f"Line missing tab separator: {line}"
        parts = line.split('\t')
        assert len(parts) == 2, f"Expected key-value pair: {line}"


def test_format_toon_success_field_name_is_command():
    """Test that field name is 'command' not 'command_executed'."""
    result = format_toon_success(
        log_file="test.log",
        exit_code=0,
        duration_seconds=10,
        command="./mvnw test"
    )

    assert 'command_executed' not in result, "Should not use 'command_executed'"
    assert 'command\t' in result, "Should use 'command' field"


def test_format_toon_success_contains_required_fields():
    """Test that success output contains all 5 core fields."""
    result = format_toon_success(
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=0,
        duration_seconds=45,
        command="./mvnw clean verify"
    )

    assert 'status\tsuccess' in result
    assert 'exit_code\t0' in result
    assert 'duration_seconds\t45' in result
    assert 'log_file\t.plan/temp/build-output/default/maven-2026-01-04.log' in result
    assert 'command\t./mvnw clean verify' in result


def test_format_toon_success_no_colon_separator():
    """Test that success format does not use colon separator for core fields."""
    result = format_toon_success(
        log_file="test.log",
        exit_code=0,
        duration_seconds=10,
        command="./mvnw test"
    )

    # Check that core fields don't use colon format
    assert 'status: success' not in result, "Should not use colon separator"
    assert 'log_file: ' not in result, "Should not use colon separator"
    assert 'exit_code: ' not in result, "Should not use colon separator"


# =============================================================================
# Test: format_toon_error
# =============================================================================

def test_format_toon_error_uses_tab_separator():
    """Test that error format uses tab-separated key-value pairs for core fields."""
    result = format_toon_error(
        error_type="build_failed",
        message="Build failed",
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=1,
        duration_seconds=23,
        command="./mvnw clean verify"
    )

    # Core fields should be tab-separated
    lines = result.split('\n')
    core_lines = [l for l in lines if l and not l.startswith(' ') and not l.startswith('errors') and not l.startswith('warnings') and not l.startswith('tests')]
    for line in core_lines:
        if line:  # Skip empty lines
            assert '\t' in line, f"Core field missing tab separator: {line}"


def test_format_toon_error_field_name_is_command():
    """Test that error format uses 'command' not 'command_executed'."""
    result = format_toon_error(
        error_type="build_failed",
        message="Build failed",
        log_file="test.log",
        exit_code=1,
        duration_seconds=10,
        command="./mvnw test"
    )

    assert 'command_executed' not in result, "Should not use 'command_executed'"
    assert 'command\t' in result, "Should use 'command' field"


def test_format_toon_error_contains_required_fields():
    """Test that error output contains all required fields."""
    result = format_toon_error(
        error_type="build_failed",
        message="Build failed",
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=1,
        duration_seconds=23,
        command="./mvnw clean verify"
    )

    assert 'status\terror' in result
    assert 'exit_code\t1' in result
    assert 'duration_seconds\t23' in result
    assert 'log_file\t.plan/temp/build-output/default/maven-2026-01-04.log' in result
    assert 'command\t./mvnw clean verify' in result
    assert 'error\tbuild_failed' in result


def test_format_toon_error_no_colon_separator_for_core_fields():
    """Test that error format does not use colon separator for core fields."""
    result = format_toon_error(
        error_type="build_failed",
        message="Build failed",
        log_file="test.log",
        exit_code=1,
        duration_seconds=10,
        command="./mvnw test"
    )

    # Check that core fields don't use colon format
    assert 'status: error' not in result, "Should not use colon separator"
    assert 'error: build_failed' not in result, "Should not use colon separator"


def test_format_toon_error_with_issues():
    """Test error format includes issues correctly."""
    issues = [
        {'severity': 'ERROR', 'file': 'src/Main.java', 'line': 42, 'message': 'cannot find symbol', 'type': 'compile'},
        {'severity': 'WARNING', 'file': 'pom.xml', 'line': None, 'message': 'deprecated API', 'type': 'deprecation'}
    ]

    result = format_toon_error(
        error_type="build_failed",
        message="Build failed",
        log_file="test.log",
        exit_code=1,
        duration_seconds=10,
        command="./mvnw test",
        issues=issues,
        mode="actionable"
    )

    assert 'errors[1]' in result
    assert 'src/Main.java' in result
    assert 'warnings[1]' in result


def test_format_toon_error_structured_mode_shows_accepted():
    """Test that structured mode shows accepted status for warnings."""
    issues = [
        {'severity': 'WARNING', 'file': 'pom.xml', 'line': None, 'message': 'deprecated API', 'accepted': True}
    ]

    result = format_toon_error(
        error_type="build_failed",
        message="Build failed",
        log_file="test.log",
        exit_code=1,
        duration_seconds=10,
        command="./mvnw test",
        issues=issues,
        mode="structured"
    )

    assert '[accepted]' in result


def test_format_toon_error_errors_mode_no_warnings():
    """Test that errors mode excludes warnings."""
    issues = [
        {'severity': 'ERROR', 'file': 'src/Main.java', 'line': 42, 'message': 'cannot find symbol', 'type': 'compile'},
        {'severity': 'WARNING', 'file': 'pom.xml', 'line': None, 'message': 'deprecated API', 'type': 'deprecation'}
    ]

    result = format_toon_error(
        error_type="build_failed",
        message="Build failed",
        log_file="test.log",
        exit_code=1,
        duration_seconds=10,
        command="./mvnw test",
        issues=issues,
        mode="errors"
    )

    assert 'errors[1]' in result
    assert 'warnings' not in result


# =============================================================================
# Test: filter_warnings
# =============================================================================

def test_filter_warnings_actionable_mode_removes_accepted():
    """Test that actionable mode filters out accepted warnings."""
    warnings = [
        {'message': 'deprecated API usage', 'file': 'Foo.java'},
        {'message': 'unchecked cast', 'file': 'Bar.java'},
        {'message': 'raw type usage', 'file': 'Baz.java'}
    ]
    acceptable = {'deprecation': ['deprecated API']}

    result = filter_warnings(warnings, acceptable, mode='actionable')

    assert len(result) == 2
    assert all('deprecated' not in w['message'] for w in result)


def test_filter_warnings_structured_mode_marks_accepted():
    """Test that structured mode marks accepted warnings."""
    warnings = [
        {'message': 'deprecated API usage', 'file': 'Foo.java'},
        {'message': 'unchecked cast', 'file': 'Bar.java'}
    ]
    acceptable = {'deprecation': ['deprecated API']}

    result = filter_warnings(warnings, acceptable, mode='structured')

    assert len(result) == 2
    deprecated_warning = next(w for w in result if 'deprecated' in w['message'])
    assert deprecated_warning['accepted'] is True
    unchecked_warning = next(w for w in result if 'unchecked' in w['message'])
    assert unchecked_warning['accepted'] is False


def test_filter_warnings_errors_mode_returns_empty():
    """Test that errors mode returns empty list."""
    warnings = [
        {'message': 'some warning', 'file': 'Foo.java'}
    ]

    result = filter_warnings(warnings, {}, mode='errors')

    assert result == []


def test_is_warning_accepted_substring_match():
    """Test substring matching for acceptable patterns."""
    warning = {'message': 'This uses deprecated API method'}
    acceptable = {'deprecation': ['deprecated API']}

    assert is_warning_accepted(warning, acceptable) is True


def test_is_warning_accepted_regex_match():
    """Test regex matching for acceptable patterns."""
    warning = {'message': 'Warning: unchecked cast from Object to List<String>'}
    acceptable = {'unchecked': [r'unchecked cast.*List']}

    assert is_warning_accepted(warning, acceptable) is True


def test_is_warning_accepted_no_match():
    """Test warning not matching any pattern."""
    warning = {'message': 'Something entirely different'}
    acceptable = {'deprecation': ['deprecated API']}

    assert is_warning_accepted(warning, acceptable) is False


# =============================================================================
# Test: format_json_success
# =============================================================================

def test_format_json_success_is_valid_json():
    """Test that JSON success format produces valid JSON."""
    import json as json_module
    result = format_json_success(
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=0,
        duration_seconds=45,
        command="./mvnw clean verify"
    )

    # Should parse as valid JSON
    parsed = json_module.loads(result)
    assert isinstance(parsed, dict)


def test_format_json_success_contains_required_fields():
    """Test that JSON success output contains all 5 core fields."""
    import json as json_module
    result = format_json_success(
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=0,
        duration_seconds=45,
        command="./mvnw clean verify"
    )

    parsed = json_module.loads(result)
    assert parsed['status'] == 'success'
    assert parsed['exit_code'] == 0
    assert parsed['duration_seconds'] == 45
    assert parsed['log_file'] == ".plan/temp/build-output/default/maven-2026-01-04.log"
    assert parsed['command'] == "./mvnw clean verify"


def test_format_json_success_field_name_is_command():
    """Test that JSON format uses 'command' not 'command_executed'."""
    import json as json_module
    result = format_json_success(
        log_file="test.log",
        exit_code=0,
        duration_seconds=10,
        command="./mvnw test"
    )

    parsed = json_module.loads(result)
    assert 'command_executed' not in parsed
    assert 'command' in parsed


# =============================================================================
# Test: format_json_error
# =============================================================================

def test_format_json_error_is_valid_json():
    """Test that JSON error format produces valid JSON."""
    import json as json_module
    result = format_json_error(
        error_type="build_failed",
        message="Build failed",
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=1,
        duration_seconds=23,
        command="./mvnw clean verify"
    )

    # Should parse as valid JSON
    parsed = json_module.loads(result)
    assert isinstance(parsed, dict)


def test_format_json_error_contains_required_fields():
    """Test that JSON error output contains all required fields."""
    import json as json_module
    result = format_json_error(
        error_type="build_failed",
        message="Build failed",
        log_file=".plan/temp/build-output/default/maven-2026-01-04.log",
        exit_code=1,
        duration_seconds=23,
        command="./mvnw clean verify"
    )

    parsed = json_module.loads(result)
    assert parsed['status'] == 'error'
    assert parsed['exit_code'] == 1
    assert parsed['duration_seconds'] == 23
    assert parsed['log_file'] == ".plan/temp/build-output/default/maven-2026-01-04.log"
    assert parsed['command'] == "./mvnw clean verify"
    assert parsed['error'] == "build_failed"


def test_format_json_error_with_issues():
    """Test JSON error format includes issues correctly."""
    import json as json_module
    issues = [
        {'severity': 'ERROR', 'file': 'src/Main.java', 'line': 42, 'message': 'cannot find symbol', 'type': 'compile'},
        {'severity': 'WARNING', 'file': 'pom.xml', 'line': None, 'message': 'deprecated API', 'type': 'deprecation'}
    ]

    result = format_json_error(
        error_type="build_failed",
        message="Build failed",
        log_file="test.log",
        exit_code=1,
        duration_seconds=10,
        command="./mvnw test",
        issues=issues,
        mode="actionable"
    )

    parsed = json_module.loads(result)
    assert 'errors' in parsed
    assert len(parsed['errors']) == 1
    assert parsed['errors'][0]['file'] == 'src/Main.java'
    assert 'warnings' in parsed
    assert len(parsed['warnings']) == 1


def test_formats_produce_equivalent_data():
    """Test that TOON and JSON formats contain equivalent data."""
    import json as json_module

    log_file = ".plan/temp/build-output/default/maven-2026-01-04.log"
    exit_code = 0
    duration = 45
    command = "./mvnw clean verify"

    toon_result = format_toon_success(log_file, exit_code, duration, command)
    json_result = format_json_success(log_file, exit_code, duration, command)

    # Parse TOON to dict
    toon_dict = {}
    for line in toon_result.split('\n'):
        if '\t' in line:
            key, value = line.split('\t', 1)
            toon_dict[key] = value

    # Parse JSON
    json_dict = json_module.loads(json_result)

    # Compare key fields
    assert toon_dict['status'] == json_dict['status']
    assert int(toon_dict['exit_code']) == json_dict['exit_code']
    assert int(toon_dict['duration_seconds']) == json_dict['duration_seconds']
    assert toon_dict['log_file'] == json_dict['log_file']
    assert toon_dict['command'] == json_dict['command']


# =============================================================================
# Run tests
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # TOON format tests
        test_format_toon_success_uses_tab_separator,
        test_format_toon_success_field_name_is_command,
        test_format_toon_success_contains_required_fields,
        test_format_toon_success_no_colon_separator,
        test_format_toon_error_uses_tab_separator,
        test_format_toon_error_field_name_is_command,
        test_format_toon_error_contains_required_fields,
        test_format_toon_error_no_colon_separator_for_core_fields,
        test_format_toon_error_with_issues,
        test_format_toon_error_structured_mode_shows_accepted,
        test_format_toon_error_errors_mode_no_warnings,
        # JSON format tests
        test_format_json_success_is_valid_json,
        test_format_json_success_contains_required_fields,
        test_format_json_success_field_name_is_command,
        test_format_json_error_is_valid_json,
        test_format_json_error_contains_required_fields,
        test_format_json_error_with_issues,
        test_formats_produce_equivalent_data,
        # Warning filter tests
        test_filter_warnings_actionable_mode_removes_accepted,
        test_filter_warnings_structured_mode_marks_accepted,
        test_filter_warnings_errors_mode_returns_empty,
        test_is_warning_accepted_substring_match,
        test_is_warning_accepted_regex_match,
        test_is_warning_accepted_no_match,
    ])
    sys.exit(runner.run())
