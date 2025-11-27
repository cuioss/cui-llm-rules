#!/usr/bin/env python3
"""Tests for search-openrewrite-markers.py script.

Migrated from test-search-openrewrite-markers.sh - tests OpenRewrite marker search and categorization.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('builder', 'builder-maven-rules', 'search-openrewrite-markers.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Tests
# =============================================================================

def test_find_markers():
    """Test finding OpenRewrite markers in source files."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Should exit 1 because there's an "ask_user" marker
    assert result.returncode == 1, "Should exit 1 with ask_user markers"
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['total_markers'] == 4, "Should find 4 markers"
    assert data['data']['files_affected'] == 2, "Should affect 2 files"


def test_categorize_auto_suppress():
    """Test categorizing auto-suppress markers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Should have 3 auto-suppress (2 CuiLogRecordPatternRecipe + 1 InvalidExceptionUsageRecipe)
    assert data['data']['auto_suppress_count'] == 3, "Should have 3 auto-suppress markers"


def test_categorize_ask_user():
    """Test categorizing ask-user markers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Should have 1 ask_user (SomeOtherRecipe)
    assert data['data']['ask_user_count'] == 1, "Should have 1 ask_user marker"


def test_no_markers():
    """Test with source containing no markers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-no-markers' / 'src')
    )
    data = result.json()

    assert result.returncode == 0, "Should exit 0 with no markers"
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['total_markers'] == 0, "Should find 0 markers"
    assert data['data']['files_affected'] == 0, "Should affect 0 files"


def test_missing_directory():
    """Test with missing source directory."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', '/nonexistent/directory'
    )
    data = result.json()

    assert result.returncode == 1, "Missing dir should exit with 1"
    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'source_not_found', "Error should be source_not_found"


def test_recipe_summary():
    """Test recipe summary contains expected recipes."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    logrecord_count = data['data']['recipe_summary'].get('CuiLogRecordPatternRecipe', 0)
    assert logrecord_count == 2, "Should have 2 CuiLogRecordPatternRecipe markers"


def test_suppression_comment():
    """Test that auto-suppress markers have suppression comment."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    auto_suppress = data['data']['by_category']['auto_suppress']
    has_comment = all('suppression_comment' in m for m in auto_suppress)
    assert has_comment, "Auto-suppress markers should have suppression_comment"


def test_marker_line_numbers():
    """Test markers have line numbers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    markers = data['data']['markers']
    has_lines = all('line' in m and isinstance(m['line'], int) for m in markers)
    assert has_lines, "All markers should have line numbers"


def test_only_auto_suppress_exit_0():
    """Test exit code 0 when only auto-suppress markers exist."""
    # Create temp dir with only auto-suppress markers
    temp_dir = Path(tempfile.mkdtemp())
    try:
        src_dir = temp_dir / 'src'
        src_dir.mkdir()

        (src_dir / 'Test.java').write_text('''public class Test {
    /*~~(TODO: CuiLogRecordPatternRecipe - test)>*/
    void method() {}
}
''')

        result = run_script(
            SCRIPT_PATH,
            '--source-dir', str(src_dir)
        )
        data = result.json()

        assert result.returncode == 0, "Only auto-suppress should exit 0"
        assert data['data']['ask_user_count'] == 0, "Should have 0 ask_user"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_file_paths_in_output():
    """Test that file paths are included in marker output."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    markers = data['data']['markers']
    has_files = all('file' in m and m['file'].endswith('.java') for m in markers)
    assert has_files, "All markers should have file paths"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_find_markers,
        test_categorize_auto_suppress,
        test_categorize_ask_user,
        test_no_markers,
        test_missing_directory,
        test_recipe_summary,
        test_suppression_comment,
        test_marker_line_numbers,
        test_only_auto_suppress_exit_0,
        test_file_paths_in_output,
    ])
    sys.exit(runner.run())
