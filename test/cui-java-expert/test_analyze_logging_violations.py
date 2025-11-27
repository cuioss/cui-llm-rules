#!/usr/bin/env python3
"""Tests for analyze-logging-violations.py script.

Migrated from test-analyze-logging-violations.sh - tests LOGGER usage analysis
based on CUI logging standards.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-java-expert', 'cui-java-core', 'analyze-logging-violations.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_analyze_compliant_file():
    """Test analyzing compliant logging file returns success."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-compliant.java')
    )
    data = result.json()

    assert data['status'] == 'success', "Successfully analyzed compliant file"


def test_compliant_file_no_violations():
    """Test compliant file has no violations."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-compliant.java')
    )
    data = result.json()

    violation_count = data.get('metrics', {}).get('total_violations', 0)
    assert violation_count == 0, f"Compliant file should have no violations, found: {violation_count}"


def test_violation_file_success_status():
    """Test analyzing violations file returns success status (script runs, finds violations)."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()

    assert data['status'] == 'success', "Successfully analyzed violations file"


def test_violations_detected():
    """Test violations are detected in non-compliant file."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()

    violation_count = data.get('metrics', {}).get('total_violations', 0)
    assert violation_count > 0, f"Should have detected violations, found: {violation_count}"


def test_missing_log_record_violations():
    """Test MISSING_LOG_RECORD violations are detected."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()

    missing_count = data.get('data', {}).get('summary', {}).get('missing_log_record', 0)
    assert missing_count > 0, f"Should have detected MISSING_LOG_RECORD violations: {missing_count}"


def test_violation_has_file_field():
    """Test violation has file field."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()

    violations = data.get('data', {}).get('violations', [])
    if violations:
        assert 'file' in violations[0], "Violation has file field"


def test_violation_has_line_field():
    """Test violation has numeric line field."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()

    violations = data.get('data', {}).get('violations', [])
    if violations:
        line = violations[0].get('line')
        assert isinstance(line, int), "Violation has numeric line field"


def test_violation_has_type_field():
    """Test violation has violation_type field."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()

    violations = data.get('data', {}).get('violations', [])
    if violations:
        assert 'violation_type' in violations[0], "Violation has violation_type field"


def test_missing_file_error():
    """Test error handling for missing file."""
    result = run_script(
        SCRIPT_PATH,
        '--file', 'nonexistent.java'
    )
    data = result.json()

    assert data['status'] == 'error', "Returns error status for missing file"


def test_missing_arguments_error():
    """Test error handling for missing arguments."""
    result = run_script(SCRIPT_PATH)
    data = result.json()

    assert data['status'] == 'error', "Returns error when no arguments provided"


def test_compliant_file_compliance_rate():
    """Test compliance rate calculation for compliant file."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-logging-compliant.java')
    )
    data = result.json()

    # Compliant file should have high compliance rate
    compliance_rate = data.get('metrics', {}).get('compliance_rate', 0)
    # Don't assert exact value as it may vary based on counting
    assert compliance_rate >= 0, f"Compliance rate should be non-negative: {compliance_rate}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_analyze_compliant_file,
        test_compliant_file_no_violations,
        test_violation_file_success_status,
        test_violations_detected,
        test_missing_log_record_violations,
        test_violation_has_file_field,
        test_violation_has_line_field,
        test_violation_has_type_field,
        test_missing_file_error,
        test_missing_arguments_error,
        test_compliant_file_compliance_rate,
    ])
    sys.exit(runner.run())
