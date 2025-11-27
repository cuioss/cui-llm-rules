#!/usr/bin/env python3
"""Tests for search-openrewrite-markers.py script (Gradle version).

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
SCRIPT_PATH = get_script_path('builder', 'builder-gradle-rules', 'search-openrewrite-markers.py')
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

    assert data['status'] == 'success', "Status should be success"
    assert data['data']['total_markers'] > 0, "Should find some markers"


def test_no_markers_found():
    """Test with source containing no markers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-no-markers' / 'src')
    )
    data = result.json()

    assert result.returncode == 0, "No markers should exit with 0"
    assert data['status'] == 'success', "Status should be success"
    assert data['data']['total_markers'] == 0, "Should find 0 markers"


def test_categorize_auto_suppress():
    """Test categorizing auto-suppress markers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Check auto_suppress count
    auto_suppress_count = data['data']['auto_suppress_count']
    assert auto_suppress_count > 0, "Should have auto-suppressible markers"


def test_categorize_ask_user():
    """Test categorizing ask-user markers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Check ask_user count
    ask_user_count = data['data']['ask_user_count']
    assert ask_user_count > 0, "Should have ask_user markers"


def test_recipe_summary():
    """Test recipe summary exists."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Check recipe_summary exists
    recipe_summary = data['data']['recipe_summary']
    assert recipe_summary, "Should have recipe summary"


def test_files_affected_count():
    """Test files affected count."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    files_affected = data['data']['files_affected']
    assert files_affected > 0, "Should report affected files"


def test_suppression_comment_generated():
    """Test suppression comments are generated for auto-suppress markers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Check auto_suppress entries have suppression_comment
    auto_suppress = data['data']['by_category']['auto_suppress']
    if auto_suppress:
        has_comment = all('suppression_comment' in m for m in auto_suppress)
        assert has_comment, "Auto-suppress markers should have suppression_comment"


def test_directory_not_found():
    """Test error when source directory doesn't exist."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', '/nonexistent/directory'
    )
    data = result.json()

    assert data['status'] == 'error', "Status should be error"
    assert data['error'] == 'directory_not_found', "Error should be directory_not_found"


def test_custom_extensions():
    """Test custom file extensions parameter."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src'),
        '--extensions', '.java'
    )
    data = result.json()

    assert data['status'] == 'success', "Status should be success"


def test_marker_has_line_number():
    """Test markers have line numbers."""
    result = run_script(
        SCRIPT_PATH,
        '--source-dir', str(FIXTURES_DIR / 'source-with-markers' / 'src')
    )
    data = result.json()

    # Check markers have line field
    markers = data['data']['markers']
    if markers:
        has_line = all('line' in m for m in markers)
        assert has_line, "Markers should have line number"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_find_markers,
        test_no_markers_found,
        test_categorize_auto_suppress,
        test_categorize_ask_user,
        test_recipe_summary,
        test_files_affected_count,
        test_suppression_comment_generated,
        test_directory_not_found,
        test_custom_extensions,
        test_marker_has_line_number,
    ])
    sys.exit(runner.run())
