#!/usr/bin/env python3
"""Tests for documentation-stats.py script.

Migrated from test-documentation-stats.sh - tests the documentation statistics
generator including output formats, metrics collection, and error handling.
"""

import json
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner, run_script

# Test directories
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent.parent.parent
SCRIPT_PATH = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-documentation-standards' / 'skills' / 'cui-documentation' / 'scripts' / 'documentation-stats.py'
FIXTURES_DIR = TEST_DIR / 'fixtures'
STANDARDS_DIR = PROJECT_ROOT / 'standards'


# =============================================================================
# Tests
# =============================================================================

def test_script_exists():
    """Test that the script exists."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"


def test_fixtures_exist():
    """Test that fixtures directory exists."""
    assert FIXTURES_DIR.exists(), f"Fixtures not found: {FIXTURES_DIR}"


def test_help_flag():
    """Test --help flag displays usage."""
    result = run_script(SCRIPT_PATH, '--help')
    combined = result.stdout + result.stderr
    assert 'usage' in combined.lower(), f"Help not shown: {combined}"


def test_h_flag():
    """Test -h flag displays usage."""
    result = run_script(SCRIPT_PATH, '-h')
    combined = result.stdout + result.stderr
    assert 'usage' in combined.lower(), f"Help not shown with -h flag"


def test_console_format_default():
    """Test default console output format."""
    result = run_script(SCRIPT_PATH, str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    assert 'Documentation Statistics' in combined, \
        f"Console format didn't produce expected output: {combined}"


def test_json_format_produced():
    """Test JSON output format is valid JSON."""
    result = run_script(SCRIPT_PATH, '-f', 'json', str(FIXTURES_DIR))
    try:
        data = json.loads(result.stdout)
        assert 'metadata' in data, "JSON missing metadata"
    except json.JSONDecodeError:
        raise AssertionError(f"Invalid JSON produced: {result.stdout}")


def test_json_has_metadata():
    """Test JSON output has metadata with directory."""
    result = run_script(SCRIPT_PATH, '-f', 'json', str(FIXTURES_DIR))
    data = json.loads(result.stdout)
    assert 'metadata' in data, "JSON missing metadata"
    assert 'directory' in data['metadata'], "JSON metadata missing directory"
    assert data['metadata']['directory'] is not None, "directory is null"


def test_csv_format_valid():
    """Test CSV output format has header."""
    result = run_script(SCRIPT_PATH, '-f', 'csv', str(FIXTURES_DIR))
    first_line = result.stdout.split('\n')[0]
    assert 'Directory' in first_line, f"CSV header missing Directory: {first_line}"


def test_markdown_format_valid():
    """Test Markdown output format has header."""
    result = run_script(SCRIPT_PATH, '-f', 'markdown', str(FIXTURES_DIR))
    assert '# Documentation Statistics' in result.stdout, \
        f"Markdown header not found: {result.stdout[:200]}"


def test_details_flag_includes_files():
    """Test details flag includes file names."""
    result = run_script(SCRIPT_PATH, '-d', str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    assert 'valid.adoc' in combined, \
        f"Details flag didn't include valid.adoc: {combined}"


def test_counts_files_correctly():
    """Test that files are counted correctly."""
    result = run_script(SCRIPT_PATH, '-f', 'json', str(FIXTURES_DIR))
    data = json.loads(result.stdout)
    file_count = data['metadata']['total_files']
    # We have at least 3 fixture files
    assert file_count >= 3, f"Expected at least 3 files, got {file_count}"


def test_produces_summary_stats():
    """Test that summary statistics are produced."""
    result = run_script(SCRIPT_PATH, '-f', 'json', str(FIXTURES_DIR))
    data = json.loads(result.stdout)
    assert 'summary' in data, "JSON missing summary"
    assert 'lines' in data['summary'], "Summary missing lines"


def test_has_directory_stats():
    """Test that directory statistics are produced."""
    result = run_script(SCRIPT_PATH, '-f', 'json', str(FIXTURES_DIR))
    data = json.loads(result.stdout)
    assert 'directories' in data, "JSON missing directories"
    assert data['directories'] is not None, "directories is null"


def test_details_flag_accepted():
    """Test details flag is accepted."""
    result = run_script(SCRIPT_PATH, '-d', str(FIXTURES_DIR))
    assert len(result.stdout) > 0, "Details flag produced no output"


def test_all_formats_work():
    """Test that all format flags are accepted."""
    formats = ['console', 'json', 'csv', 'markdown']
    for fmt in formats:
        result = run_script(SCRIPT_PATH, '-f', fmt, str(FIXTURES_DIR))
        assert result.returncode == 0, f"Format {fmt} failed: {result.stderr}"


def test_real_standards_directory():
    """Test with real standards directory."""
    if not STANDARDS_DIR.exists():
        return  # Skip if standards directory doesn't exist

    result = run_script(SCRIPT_PATH, '-f', 'json', str(STANDARDS_DIR))
    data = json.loads(result.stdout)
    file_count = data['metadata']['total_files']
    assert file_count > 0, f"Expected files in standards, got {file_count}"


def test_invalid_format_rejected():
    """Test that invalid format is rejected."""
    result = run_script(SCRIPT_PATH, '-f', 'invalid_format')
    assert result.returncode != 0, "Invalid format should be rejected"


def test_empty_directory_handled():
    """Test that empty directory is handled."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = run_script(SCRIPT_PATH, temp_dir)
        assert result.returncode == 0, f"Empty directory failed: {result.stderr}"


def test_nonexistent_dir_handled():
    """Test that nonexistent directory is handled."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path')
    assert result.returncode != 0, "Nonexistent path should fail"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_script_exists,
        test_fixtures_exist,
        test_help_flag,
        test_h_flag,
        test_console_format_default,
        test_json_format_produced,
        test_json_has_metadata,
        test_csv_format_valid,
        test_markdown_format_valid,
        test_details_flag_includes_files,
        test_counts_files_correctly,
        test_produces_summary_stats,
        test_has_directory_stats,
        test_details_flag_accepted,
        test_all_formats_work,
        test_real_standards_directory,
        test_invalid_format_rejected,
        test_empty_directory_handled,
        test_nonexistent_dir_handled,
    ])
    sys.exit(runner.run())
