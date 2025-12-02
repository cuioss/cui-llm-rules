#!/usr/bin/env python3
"""Tests for analyze-tool-coverage.py script.

Migrated from test-analyze-tool-coverage.sh - tests tool coverage analysis
including perfect coverage, unused tools, missing tools, and critical violations.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner, run_script, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-plugin-development-tools', 'plugin-doctor', 'analyze-tool-coverage.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures' / 'tool-coverage'


def parse_json(output):
    """Parse JSON from output."""
    import json
    return json.loads(output)


# =============================================================================
# Tests - Perfect Coverage
# =============================================================================

def test_perfect_coverage_score():
    """Test perfect coverage returns score 100.0."""
    fixture = FIXTURES_DIR / 'perfect-coverage.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    score = data.get('tool_coverage', {}).get('tool_fit_score')
    assert score == 100.0, f"Perfect coverage should have score 100.0, got {score}"


def test_perfect_coverage_rating():
    """Test perfect coverage returns Excellent rating."""
    fixture = FIXTURES_DIR / 'perfect-coverage.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    rating = data.get('tool_coverage', {}).get('rating')
    assert rating == 'Excellent', f"Perfect coverage should have rating 'Excellent', got '{rating}'"


def test_perfect_coverage_missing_count():
    """Test perfect coverage has 0 missing tools."""
    fixture = FIXTURES_DIR / 'perfect-coverage.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    missing_count = data.get('tool_coverage', {}).get('missing_count')
    assert missing_count == 0, f"Perfect coverage should have 0 missing, got {missing_count}"


def test_perfect_coverage_unused_count():
    """Test perfect coverage has 0 unused tools."""
    fixture = FIXTURES_DIR / 'perfect-coverage.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    unused_count = data.get('tool_coverage', {}).get('unused_count')
    assert unused_count == 0, f"Perfect coverage should have 0 unused, got {unused_count}"


# =============================================================================
# Tests - Unused Tools Detection
# =============================================================================

def test_unused_tools_count():
    """Test detection of unused tools count."""
    fixture = FIXTURES_DIR / 'unused-tools.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    unused_count = data.get('tool_coverage', {}).get('unused_count')
    assert unused_count == 3, f"Should have 3 unused tools, got {unused_count}"


def test_unused_tools_declared_count():
    """Test declared tools count."""
    fixture = FIXTURES_DIR / 'unused-tools.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    declared_count = data.get('tool_coverage', {}).get('declared_count')
    assert declared_count == 5, f"Should have 5 declared tools, got {declared_count}"


def test_unused_tools_used_count():
    """Test used tools count."""
    fixture = FIXTURES_DIR / 'unused-tools.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    used_count = data.get('tool_coverage', {}).get('used_count')
    assert used_count == 2, f"Should have 2 used tools, got {used_count}"


# =============================================================================
# Tests - Missing Tools Detection
# =============================================================================

def test_missing_tools_count():
    """Test detection of missing tools count."""
    fixture = FIXTURES_DIR / 'missing-tools.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    missing_count = data.get('tool_coverage', {}).get('missing_count')
    assert missing_count == 3, f"Should have 3 missing tools, got {missing_count}"


def test_missing_tools_declared_count():
    """Test declared tools count with missing tools."""
    fixture = FIXTURES_DIR / 'missing-tools.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    declared_count = data.get('tool_coverage', {}).get('declared_count')
    assert declared_count == 2, f"Should have 2 declared tools, got {declared_count}"


# =============================================================================
# Tests - Critical Violations
# =============================================================================

def test_critical_has_task_tool():
    """Test detection of Task tool in frontmatter."""
    fixture = FIXTURES_DIR / 'critical-violations.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    has_task = data.get('critical_violations', {}).get('has_task_tool')
    assert has_task is True, f"Should detect Task tool, got {has_task}"


def test_critical_has_task_calls():
    """Test detection of Task calls in content."""
    fixture = FIXTURES_DIR / 'critical-violations.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    has_task_calls = data.get('critical_violations', {}).get('has_task_calls')
    assert has_task_calls is True, f"Should detect Task calls, got {has_task_calls}"


def test_critical_maven_calls_detected():
    """Test detection of Maven calls."""
    fixture = FIXTURES_DIR / 'critical-violations.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    maven_calls = data.get('critical_violations', {}).get('maven_calls', [])
    assert len(maven_calls) > 0, f"Should detect Maven calls, found {len(maven_calls)}"


def test_critical_backup_patterns_detected():
    """Test detection of backup file patterns."""
    fixture = FIXTURES_DIR / 'critical-violations.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, str(fixture))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    backup_patterns = data.get('critical_violations', {}).get('backup_file_patterns', [])
    assert len(backup_patterns) > 0, f"Should detect backup patterns, found {len(backup_patterns)}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_perfect_coverage_score,
        test_perfect_coverage_rating,
        test_perfect_coverage_missing_count,
        test_perfect_coverage_unused_count,
        test_unused_tools_count,
        test_unused_tools_declared_count,
        test_unused_tools_used_count,
        test_missing_tools_count,
        test_missing_tools_declared_count,
        test_critical_has_task_tool,
        test_critical_has_task_calls,
        test_critical_maven_calls_detected,
        test_critical_backup_patterns_detected,
    ])
    sys.exit(runner.run())
