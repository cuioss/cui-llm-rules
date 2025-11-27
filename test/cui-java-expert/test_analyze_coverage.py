#!/usr/bin/env python3
"""Tests for analyze-coverage.py script.

Migrated from test-analyze-coverage.sh - tests JaCoCo XML report parsing and coverage analysis.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-java-expert', 'cui-java-unit-testing', 'analyze-coverage.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_parse_jacoco_report():
    """Test parsing JaCoCo XML report."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    assert data['status'] == 'success', "Successfully parsed JaCoCo report"


def test_overall_coverage_present():
    """Test overall coverage data is present."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    assert 'overall_coverage' in data.get('data', {}), "Overall coverage data present"


def test_line_coverage_numeric():
    """Test line coverage is numeric."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    line_coverage = data.get('data', {}).get('overall_coverage', {}).get('line_coverage')
    assert isinstance(line_coverage, (int, float)), "Line coverage is numeric"


def test_metrics_section_present():
    """Test metrics section is present."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-jacoco.xml')
    )
    data = result.json()

    assert 'file_analyzed' in data.get('metrics', {}), "Metrics section present"


def test_low_threshold_met():
    """Test low threshold is met."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'),
        '--threshold', '50'
    )
    data = result.json()

    assert data.get('metrics', {}).get('meets_threshold') is True, "Low threshold met correctly"


def test_high_threshold_not_met():
    """Test high threshold is not met."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'),
        '--threshold', '95'
    )
    data = result.json()

    assert data.get('metrics', {}).get('meets_threshold') is False, "High threshold not met correctly"


def test_missing_file_error():
    """Test error handling for missing file."""
    result = run_script(
        SCRIPT_PATH,
        '--file', 'nonexistent.xml'
    )
    data = result.json()

    assert data['status'] == 'error', "Returns error status for missing file"


def test_missing_arguments_error():
    """Test error handling for missing arguments."""
    result = run_script(SCRIPT_PATH)
    data = result.json()

    assert data['status'] == 'error', "Returns error when no arguments provided"


def test_low_coverage_classes_array():
    """Test low coverage classes detection."""
    result = run_script(
        SCRIPT_PATH,
        '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'),
        '--threshold', '90'
    )
    data = result.json()

    low_coverage_classes = data.get('data', {}).get('low_coverage_classes')
    assert isinstance(low_coverage_classes, list), "Low coverage classes array present"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_jacoco_report,
        test_overall_coverage_present,
        test_line_coverage_numeric,
        test_metrics_section_present,
        test_low_threshold_met,
        test_high_threshold_not_met,
        test_missing_file_error,
        test_missing_arguments_error,
        test_low_coverage_classes_array,
    ])
    sys.exit(runner.run())
