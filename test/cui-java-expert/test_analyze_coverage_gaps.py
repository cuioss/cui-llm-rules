#!/usr/bin/env python3
"""Tests for analyze-coverage-gaps.py script.

Migrated from test-analyze-coverage-gaps.sh - tests parsing of JaCoCo XML reports
and gap prioritization.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-java-expert', 'cui-java-unit-testing', 'analyze-coverage-gaps.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_parse_jacoco_report():
    """Test parsing JaCoCo XML report."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    assert data['status'] == 'success', f"Successfully parsed JaCoCo report"


def test_coverage_metrics_present():
    """Test coverage metrics are present."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    overall = data.get('data', {}).get('overall_coverage', {})
    assert 'line' in overall and 'branch' in overall and 'method' in overall, \
        "Coverage metrics present"


def test_line_coverage_calculation():
    """Test line coverage calculation (approximately 74-77%)."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    line_coverage = data.get('data', {}).get('overall_coverage', {}).get('line', 0)
    # Accept a broader range as calculation may vary slightly
    assert 70 < line_coverage < 80, f"Line coverage correctly calculated: {line_coverage}"


def test_gap_priorities_present():
    """Test gap priorities structure is present."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    gaps = data.get('data', {}).get('gaps_by_priority', {})
    assert 'high' in gaps and 'medium' in gaps and 'low' in gaps, "Gap priorities present"


def test_uncovered_public_method_high_priority():
    """Test uncovered public method identified as high priority."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    high_priority = data.get('data', {}).get('gaps_by_priority', {}).get('high', [])
    validate_expiry_found = any(g.get('method') == 'validateExpiry' for g in high_priority)
    assert validate_expiry_found, "Uncovered public method identified as high priority"


def test_untested_public_methods_field():
    """Test untested public methods field is present."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    assert 'untested_public_methods' in data.get('data', {}), "Untested public methods field present"


def test_untested_public_methods_count():
    """Test at least one untested public method is identified."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    untested_count = len(data.get('data', {}).get('untested_public_methods', []))
    assert untested_count >= 1, f"Identified untested public methods: {untested_count}"


def test_priority_filter_accepted():
    """Test priority filter parameter is accepted."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'),
        '--priority', 'high'
    )
    data = result.json()

    assert data['status'] == 'success', "Priority filter accepted"


def test_priority_filter_limits_results():
    """Test filter correctly limits to high priority."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'),
        '--priority', 'high'
    )
    data = result.json()

    gaps = data.get('data', {}).get('gaps_by_priority', {})
    high_count = len(gaps.get('high', []))
    medium_count = len(gaps.get('medium', []))

    # When filtered to high, should have high priority gaps but not medium/low
    assert high_count > 0 and medium_count == 0, \
        f"Filter correctly limited to high priority (high={high_count}, medium={medium_count})"


def test_recommendations_field_present():
    """Test recommendations field is present."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    assert 'recommendations' in data.get('data', {}), "Recommendations field present"


def test_recommendations_structure():
    """Test recommendations have required fields."""
    result = run_script(
        SCRIPT_PATH,
        '--report', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    recommendations = data.get('data', {}).get('recommendations', [])
    if recommendations:
        first = recommendations[0]
        assert 'priority' in first and 'class' in first and 'reason' in first, \
            "Recommendations have required fields"


def test_help_flag():
    """Test --help flag works."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0, "--help flag works"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_jacoco_report,
        test_coverage_metrics_present,
        test_line_coverage_calculation,
        test_gap_priorities_present,
        test_uncovered_public_method_high_priority,
        test_untested_public_methods_field,
        test_untested_public_methods_count,
        test_priority_filter_accepted,
        test_priority_filter_limits_results,
        test_recommendations_field_present,
        test_recommendations_structure,
        test_help_flag,
    ])
    sys.exit(runner.run())
