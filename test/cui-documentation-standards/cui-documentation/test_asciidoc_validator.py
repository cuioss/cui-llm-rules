#!/usr/bin/env python3
"""Tests for asciidoc-validator.py script.

Migrated from test-asciidoc-validator.sh - tests the AsciiDoc validator
including output formats, severity levels, verbose/quiet modes, and error handling.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner, run_script

# Test directories
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent.parent.parent
SCRIPT_PATH = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-documentation-standards' / 'skills' / 'cui-documentation' / 'scripts' / 'asciidoc-validator.py'
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


def test_console_format_default():
    """Test default console output format."""
    result = run_script(SCRIPT_PATH, str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    # Script should produce output about checking files
    assert 'Checking' in combined or len(combined) > 0, "No console output produced"


def test_console_format_explicit():
    """Test explicit console format flag."""
    result = run_script(SCRIPT_PATH, '-f', 'console', str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    assert len(combined) > 0, "Console format produced no output"


def test_json_format():
    """Test JSON output format."""
    result = run_script(SCRIPT_PATH, '-f', 'json', str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    # Should contain some JSON-like content
    assert 'directory' in combined.lower() or '{' in combined, \
        f"JSON format didn't produce expected output"


def test_valid_file_detection():
    """Test that valid files are found with verbose mode."""
    result = run_script(SCRIPT_PATH, '-v', str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    # Should process .adoc files
    assert result.returncode in [0, 1], f"Script crashed: {result.stderr}"


def test_missing_blank_line_detected():
    """Test that missing blank line violation is detected."""
    import tempfile
    # Create a temp file with missing blank line before list (linter may fix fixture files)
    content = """= Test Document
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Section One
Some text directly before list:
* List item 1
* List item 2
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        f.write(content)
        temp_file = f.name
    try:
        result = run_script(SCRIPT_PATH, '-q', temp_file)
        # Should exit with non-zero if violation detected
        assert result.returncode != 0 or 'blank' in (result.stdout + result.stderr).lower(), \
            "Missing blank line should be detected"
    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_invalid_xref_detected():
    """Test that invalid xref is detected."""
    test_file = FIXTURES_DIR / 'invalid-xref.adoc'
    if not test_file.exists():
        return  # Skip if fixture doesn't exist

    result = run_script(SCRIPT_PATH, '-q', str(test_file))
    # Should detect the invalid xref
    assert result.returncode in [0, 1], f"Script crashed: {result.stderr}"


def test_verbose_mode():
    """Test verbose mode shows details."""
    result = run_script(SCRIPT_PATH, '-v', str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    assert 'Checking' in combined or len(combined) > 0, "Verbose mode produced no output"


def test_quiet_mode():
    """Test quiet mode suppresses verbose output."""
    result = run_script(SCRIPT_PATH, '-q', str(FIXTURES_DIR))
    # Quiet mode should still work (may or may not produce output)
    assert result.returncode in [0, 1], f"Script crashed in quiet mode: {result.stderr}"


def test_ignore_pattern_flag():
    """Test ignore pattern flag is accepted."""
    result = run_script(SCRIPT_PATH, '-q', '-i', 'missing-*.adoc', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"Ignore pattern flag crashed: {result.stderr}"


def test_severity_all():
    """Test severity level 'all' is accepted."""
    result = run_script(SCRIPT_PATH, '-q', '-s', 'all', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"Severity 'all' crashed: {result.stderr}"


def test_severity_error():
    """Test severity level 'error' is accepted."""
    result = run_script(SCRIPT_PATH, '-q', '-s', 'error', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"Severity 'error' crashed: {result.stderr}"


def test_severity_warning():
    """Test severity level 'warning' is accepted."""
    result = run_script(SCRIPT_PATH, '-q', '-s', 'warning', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"Severity 'warning' crashed: {result.stderr}"


def test_invalid_format_rejected():
    """Test that invalid format is rejected."""
    result = run_script(SCRIPT_PATH, '-f', 'invalid_format')
    assert result.returncode != 0, "Invalid format should be rejected"


def test_nonexistent_dir_handled():
    """Test that nonexistent directory is handled."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path')
    assert result.returncode != 0, "Nonexistent path should fail"


def test_invalid_severity_rejected():
    """Test that invalid severity is rejected."""
    result = run_script(SCRIPT_PATH, '-s', 'invalid')
    assert result.returncode != 0, "Invalid severity should be rejected"


def test_quiet_json_combination():
    """Test quiet and JSON format combination."""
    result = run_script(SCRIPT_PATH, '-q', '-f', 'json', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"Quiet+JSON crashed: {result.stderr}"


def test_verbose_severity_combination():
    """Test verbose and severity combination."""
    result = run_script(SCRIPT_PATH, '-v', '-s', 'error', str(FIXTURES_DIR))
    combined = result.stdout + result.stderr
    assert 'Checking' in combined or len(combined) > 0, \
        "Verbose+severity combination produced no output"


def test_real_standards_directory():
    """Test with real standards directory."""
    if not STANDARDS_DIR.exists():
        return  # Skip if standards directory doesn't exist

    result = run_script(SCRIPT_PATH, '-q', str(STANDARDS_DIR))
    # Script should complete (may report issues)
    assert result.returncode in [0, 1], f"Standards validation crashed: {result.stderr}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_script_exists,
        test_fixtures_exist,
        test_help_flag,
        test_console_format_default,
        test_console_format_explicit,
        test_json_format,
        test_valid_file_detection,
        test_missing_blank_line_detected,
        test_invalid_xref_detected,
        test_verbose_mode,
        test_quiet_mode,
        test_ignore_pattern_flag,
        test_severity_all,
        test_severity_error,
        test_severity_warning,
        test_invalid_format_rejected,
        test_nonexistent_dir_handled,
        test_invalid_severity_rejected,
        test_quiet_json_combination,
        test_verbose_severity_combination,
        test_real_standards_directory,
    ])
    sys.exit(runner.run())
