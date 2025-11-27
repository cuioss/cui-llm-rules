#!/usr/bin/env python3
"""Tests for verify-adoc-links.py script.

Migrated from test-verify-adoc-links.sh - comprehensive link verification testing.
"""

import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-documentation-standards', 'cui-documentation', 'verify-adoc-links.py')
TEST_FIXTURES_DIR = Path(__file__).parent / 'fixtures' / 'link-verify'


# =============================================================================
# Category 1: Help Output Tests
# =============================================================================

def test_help_flag_displays_usage():
    """Test --help displays usage."""
    result = run_script(SCRIPT_PATH, '--help')
    assert 'usage:' in result.stdout.lower(), "Help flag --help displays usage"


def test_h_flag_displays_usage():
    """Test -h displays usage."""
    result = run_script(SCRIPT_PATH, '-h')
    assert 'usage:' in result.stdout.lower(), "Help flag -h displays usage"


# =============================================================================
# Category 2: Argument Validation Tests
# =============================================================================

def test_error_both_file_and_directory():
    """Test error when both --file and --directory specified."""
    result = run_script(SCRIPT_PATH, '--file', 'foo.adoc', '--directory', 'dir/')
    assert 'cannot specify both' in result.stdout.lower() or 'cannot specify both' in result.stderr.lower(), \
        "Error when both --file and --directory specified"


def test_error_file_not_found():
    """Test error when file does not exist."""
    result = run_script(SCRIPT_PATH, '--file', '/nonexistent/file.adoc')
    assert 'error' in result.stdout.lower() or 'error' in result.stderr.lower(), \
        "Error when file does not exist"


def test_error_not_adoc_file():
    """Test error when target is not .adoc file."""
    with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
        f.write(b"# Markdown file")
        temp_file = Path(f.name)

    try:
        result = run_script(SCRIPT_PATH, '--file', str(temp_file))
        error_found = 'error' in result.stdout.lower() or 'must be' in result.stdout.lower() or \
                     'error' in result.stderr.lower() or 'must be' in result.stderr.lower()
        assert error_found, "Error when target is not .adoc file"
    finally:
        temp_file.unlink(missing_ok=True)


# =============================================================================
# Category 3: File Discovery Tests
# =============================================================================

def test_single_file_processes_one():
    """Test single file mode processes one file."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'empty.adoc'))
    assert 'Processing 1 AsciiDoc files' in result.stdout, "Single file mode processes one file"


def test_empty_file_no_errors():
    """Test empty file does not cause errors."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'empty.adoc'))
    assert result.returncode == 0, "Empty file does not cause errors"


# =============================================================================
# Category 4: Link Extraction Tests
# =============================================================================

def test_cross_reference_detected():
    """Test cross-reference detection."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'valid-all-link-types.adoc'))
    assert 'Total links found:' in result.stdout, "Cross-reference detected"


def test_file_no_links_shows_zero():
    """Test file with no links shows zero links."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'no-links.adoc'))
    assert 'Total links found:' in result.stdout and '0' in result.stdout, "File with no links shows zero"


# =============================================================================
# Category 5: Link Validation Tests
# =============================================================================

def test_valid_links_pass():
    """Test valid cross-reference passes validation."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'valid-all-link-types.adoc'))
    assert 'All links valid' in result.stdout or result.returncode == 0, "Valid links pass validation"


def test_broken_cross_reference_detected():
    """Test broken cross-reference is detected."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'broken-cross-ref.adoc'))
    has_broken = 'Broken links:' in result.stdout or 'broken' in result.stdout.lower()
    assert has_broken, "Broken cross-reference detected"


# =============================================================================
# Category 6: Output Format Tests
# =============================================================================

def test_console_summary_section():
    """Test console output displays summary section."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'valid-all-link-types.adoc'))
    assert 'LINK VERIFICATION SUMMARY' in result.stdout, "Console output displays summary section"


def test_console_files_processed():
    """Test console output displays files processed count."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'valid-all-link-types.adoc'))
    assert 'Files processed:' in result.stdout, "Console output displays files processed count"


def test_console_total_links():
    """Test console output displays total links count."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'valid-all-link-types.adoc'))
    assert 'Total links found:' in result.stdout, "Console output displays total links count"


# =============================================================================
# Category 7: Exit Code Tests
# =============================================================================

def test_exit_code_zero_no_issues():
    """Test exit code 0 when no issues found."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'valid-all-link-types.adoc'))
    assert result.returncode == 0, "Exit code 0 when no issues found"


def test_exit_code_zero_no_links():
    """Test exit code 0 for file with no links."""
    result = run_script(SCRIPT_PATH, '--file', str(TEST_FIXTURES_DIR / 'no-links.adoc'))
    assert result.returncode == 0, "Exit code 0 for file with no links"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_help_flag_displays_usage,
        test_h_flag_displays_usage,
        test_error_both_file_and_directory,
        test_error_file_not_found,
        test_error_not_adoc_file,
        test_single_file_processes_one,
        test_empty_file_no_errors,
        test_cross_reference_detected,
        test_file_no_links_shows_zero,
        test_valid_links_pass,
        test_broken_cross_reference_detected,
        test_console_summary_section,
        test_console_files_processed,
        test_console_total_links,
        test_exit_code_zero_no_issues,
        test_exit_code_zero_no_links,
    ])
    sys.exit(runner.run())
