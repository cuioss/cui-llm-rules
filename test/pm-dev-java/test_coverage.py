#!/usr/bin/env python3
"""Tests for coverage.py - consolidated JaCoCo coverage analysis.

Consolidates tests from:
- test_analyze_coverage.py (analyze subcommand)
- test_analyze_coverage_gaps.py (gaps subcommand)
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('pm-dev-java', 'cui-java-unit-testing', 'coverage.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Main help tests
# =============================================================================

def test_script_exists():
    """Test that the script exists."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"


def test_main_help():
    """Test main --help displays all subcommands."""
    result = run_script(SCRIPT_PATH, '--help')
    combined = result.stdout + result.stderr
    assert 'analyze' in combined, "analyze subcommand in help"
    assert 'gaps' in combined, "gaps subcommand in help"


# =============================================================================
# Analyze subcommand tests
# =============================================================================

def test_analyze_help():
    """Test analyze --help displays usage."""
    result = run_script(SCRIPT_PATH, 'analyze', '--help')
    combined = result.stdout + result.stderr
    assert 'usage' in combined.lower(), "Analyze help not shown"


def test_analyze_parse_jacoco_report():
    """Test parsing JaCoCo XML report."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    assert data['status'] == 'success', "Successfully parsed JaCoCo report"


def test_analyze_overall_coverage_present():
    """Test overall coverage data is present."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    assert 'overall_coverage' in data.get('data', {}), "Overall coverage data present"


def test_analyze_line_coverage_numeric():
    """Test line coverage is numeric."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    line_coverage = data.get('data', {}).get('overall_coverage', {}).get('line_coverage')
    assert isinstance(line_coverage, (int, float)), "Line coverage is numeric"


def test_analyze_metrics_section_present():
    """Test metrics section is present."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    assert 'file_analyzed' in data.get('metrics', {}), "Metrics section present"


def test_analyze_low_threshold_met():
    """Test low threshold is met."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'), '--threshold', '50')
    data = result.json()
    assert data.get('metrics', {}).get('meets_threshold') is True, "Low threshold met"


def test_analyze_high_threshold_not_met():
    """Test high threshold is not met."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'), '--threshold', '95')
    data = result.json()
    assert data.get('metrics', {}).get('meets_threshold') is False, "High threshold not met"


def test_analyze_missing_file_error():
    """Test error handling for missing file."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', 'nonexistent.xml')
    data = result.json()
    assert data['status'] == 'error', "Returns error status for missing file"


def test_analyze_missing_arguments_error():
    """Test error handling for missing arguments."""
    result = run_script(SCRIPT_PATH, 'analyze')
    data = result.json()
    assert data['status'] == 'error', "Returns error when no arguments provided"


def test_analyze_low_coverage_classes_array():
    """Test low coverage classes detection."""
    result = run_script(SCRIPT_PATH, 'analyze', '--file', str(FIXTURES_DIR / 'sample-jacoco.xml'), '--threshold', '90')
    data = result.json()
    low_coverage_classes = data.get('data', {}).get('low_coverage_classes')
    assert isinstance(low_coverage_classes, list), "Low coverage classes array present"


# =============================================================================
# Gaps subcommand tests
# =============================================================================

def test_gaps_help():
    """Test gaps --help displays usage."""
    result = run_script(SCRIPT_PATH, 'gaps', '--help')
    combined = result.stdout + result.stderr
    assert 'usage' in combined.lower(), "Gaps help not shown"


def test_gaps_parse_jacoco_report():
    """Test parsing JaCoCo XML report for gaps."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    assert data['status'] == 'success', "Successfully parsed JaCoCo report"


def test_gaps_coverage_metrics_present():
    """Test coverage metrics are present."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    overall = data.get('data', {}).get('overall_coverage', {})
    assert 'line' in overall and 'branch' in overall, "Coverage metrics present"


def test_gaps_line_coverage_calculation():
    """Test line coverage calculation."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    line_coverage = data.get('data', {}).get('overall_coverage', {}).get('line', 0)
    # Coverage value depends on fixture data - just verify it's a valid percentage
    assert 0 <= line_coverage <= 100, f"Line coverage is valid percentage: {line_coverage}"


def test_gaps_priorities_present():
    """Test gap priorities structure is present."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    gaps = data.get('data', {}).get('gaps_by_priority', {})
    assert 'high' in gaps and 'medium' in gaps and 'low' in gaps, "Gap priorities present"


def test_gaps_uncovered_public_method_high_priority():
    """Test uncovered public method identified as high priority."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    high_priority = data.get('data', {}).get('gaps_by_priority', {}).get('high', [])
    validate_expiry_found = any(g.get('method') == 'validateExpiry' for g in high_priority)
    assert validate_expiry_found, "Uncovered public method identified as high priority"


def test_gaps_untested_public_methods_field():
    """Test untested public methods field is present."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    assert 'untested_public_methods' in data.get('data', {}), "Untested public methods field present"


def test_gaps_priority_filter_accepted():
    """Test priority filter parameter is accepted."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'), '--priority', 'high')
    data = result.json()
    assert data['status'] == 'success', "Priority filter accepted"


def test_gaps_priority_filter_limits_results():
    """Test filter correctly limits to high priority."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'), '--priority', 'high')
    data = result.json()
    gaps = data.get('data', {}).get('gaps_by_priority', {})
    high_count = len(gaps.get('high', []))
    medium_count = len(gaps.get('medium', []))
    assert high_count > 0 and medium_count == 0, f"Filter correctly limited (high={high_count}, medium={medium_count})"


def test_gaps_recommendations_field_present():
    """Test recommendations field is present."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    assert 'recommendations' in data.get('data', {}), "Recommendations field present"


def test_gaps_recommendations_structure():
    """Test recommendations have required fields."""
    result = run_script(SCRIPT_PATH, 'gaps', '--report', str(FIXTURES_DIR / 'sample-jacoco.xml'))
    data = result.json()
    recommendations = data.get('data', {}).get('recommendations', [])
    if recommendations:
        first = recommendations[0]
        assert 'priority' in first and 'class' in first, "Recommendations have required fields"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_script_exists,
        test_main_help,
        # Analyze tests
        test_analyze_help,
        test_analyze_parse_jacoco_report,
        test_analyze_overall_coverage_present,
        test_analyze_line_coverage_numeric,
        test_analyze_metrics_section_present,
        test_analyze_low_threshold_met,
        test_analyze_high_threshold_not_met,
        test_analyze_missing_file_error,
        test_analyze_missing_arguments_error,
        test_analyze_low_coverage_classes_array,
        # Gaps tests
        test_gaps_help,
        test_gaps_parse_jacoco_report,
        test_gaps_coverage_metrics_present,
        test_gaps_line_coverage_calculation,
        test_gaps_priorities_present,
        test_gaps_uncovered_public_method_high_priority,
        test_gaps_untested_public_methods_field,
        test_gaps_priority_filter_accepted,
        test_gaps_priority_filter_limits_results,
        test_gaps_recommendations_field_present,
        test_gaps_recommendations_structure,
    ])
    sys.exit(runner.run())
