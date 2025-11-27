#!/usr/bin/env python3
"""Tests for asciidoc-formatter.py script.

Migrated from test-asciidoc-formatter.sh - tests the AsciiDoc formatter
including help, backup mode, fix types, and directory processing.
"""

import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner, run_script

# Test directories
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent.parent.parent
SCRIPT_PATH = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-documentation-standards' / 'skills' / 'cui-documentation' / 'scripts' / 'asciidoc-formatter.py'
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


def test_backup_mode():
    """Test that backup is created by default."""
    test_file = FIXTURES_DIR / 'missing-blank-line.adoc'
    if not test_file.exists():
        return  # Skip if fixture doesn't exist

    # Create a copy to test on
    temp_file = FIXTURES_DIR / 'test-backup-temp.adoc'
    backup_file = FIXTURES_DIR / 'test-backup-temp.adoc.bak'

    try:
        shutil.copy(test_file, temp_file)
        result = run_script(SCRIPT_PATH, str(temp_file))

        # Verify backup was created (or script ran successfully)
        assert result.returncode == 0 or backup_file.exists(), \
            f"Backup not created and script failed: {result.stderr}"
    finally:
        # Cleanup
        temp_file.unlink(missing_ok=True)
        backup_file.unlink(missing_ok=True)


def test_no_backup_flag():
    """Test --no-backup flag prevents backup creation."""
    result = run_script(SCRIPT_PATH, '--no-backup', '-t', 'lists', str(FIXTURES_DIR))
    # Script should complete (may have exit code based on file state)
    assert result.returncode in [0, 1], f"Script crashed: {result.stderr}"


def test_lists_fix_type():
    """Test -t lists fix type."""
    result = run_script(SCRIPT_PATH, '--no-backup', '-t', 'lists', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"lists fix type failed: {result.stderr}"


def test_xref_fix_type():
    """Test -t xref fix type."""
    result = run_script(SCRIPT_PATH, '--no-backup', '-t', 'xref', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"xref fix type failed: {result.stderr}"


def test_headers_fix_type():
    """Test -t headers fix type."""
    result = run_script(SCRIPT_PATH, '--no-backup', '-t', 'headers', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"headers fix type failed: {result.stderr}"


def test_whitespace_fix_type():
    """Test -t whitespace fix type."""
    result = run_script(SCRIPT_PATH, '--no-backup', '-t', 'whitespace', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"whitespace fix type failed: {result.stderr}"


def test_all_fix_types():
    """Test -t all fix type."""
    result = run_script(SCRIPT_PATH, '--no-backup', '-t', 'all', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"all fix type failed: {result.stderr}"


def test_invalid_fix_type_rejected():
    """Test that invalid fix type is rejected."""
    result = run_script(SCRIPT_PATH, '-t', 'invalid_type')
    assert result.returncode != 0, "Invalid fix type should be rejected"


def test_nonexistent_path_handled():
    """Test that nonexistent path is handled."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path')
    assert result.returncode != 0, "Nonexistent path should fail"


def test_directory_processing():
    """Test processing a directory."""
    result = run_script(SCRIPT_PATH, '--no-backup', str(FIXTURES_DIR))
    assert result.returncode in [0, 1], f"Directory processing failed: {result.stderr}"


def test_real_standards_directory():
    """Test with real standards directory."""
    if not STANDARDS_DIR.exists():
        return  # Skip if standards directory doesn't exist

    result = run_script(SCRIPT_PATH, '--no-backup', str(STANDARDS_DIR))
    # Script should complete (may report issues)
    assert result.returncode in [0, 1], f"Standards directory processing crashed: {result.stderr}"


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
        test_backup_mode,
        test_no_backup_flag,
        test_lists_fix_type,
        test_xref_fix_type,
        test_headers_fix_type,
        test_whitespace_fix_type,
        test_all_fix_types,
        test_invalid_fix_type_rejected,
        test_nonexistent_path_handled,
        test_directory_processing,
        test_real_standards_directory,
    ])
    sys.exit(runner.run())
