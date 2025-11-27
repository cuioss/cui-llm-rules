#!/usr/bin/env python3
"""Tests for analyze-cross-file-content.py script.

Migrated from test-analyze-cross-file-content.sh - tests cross-file content analysis
for detecting duplicates, extraction candidates, and content blocks.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-plugin-development-tools', 'plugin-doctor', 'analyze-cross-file-content.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures' / 'cross-file-analysis'


# =============================================================================
# Tests
# =============================================================================

def test_script_exists():
    """Test that script exists."""
    assert Path(SCRIPT_PATH).exists(), f"Script not found: {SCRIPT_PATH}"


def test_help_output():
    """Test help output is available."""
    result = run_script(SCRIPT_PATH, '--help')
    assert 'analyze-cross-file-content.py' in result.stdout or 'skill-path' in result.stdout, \
        "Help output should contain script name or skill-path option"


def test_missing_argument_error():
    """Test returns error for missing argument."""
    result = run_script(SCRIPT_PATH)
    assert result.returncode != 0, "Should return error for missing argument"
    output = result.stderr.lower() + result.stdout.lower()
    assert 'error' in output or 'required' in output, \
        "Should indicate error for missing argument"


def test_invalid_path_error():
    """Test returns error for invalid path."""
    result = run_script(SCRIPT_PATH, '--skill-path', '/nonexistent/path')
    assert result.returncode != 0, "Should return error for invalid path"
    output = result.stderr.lower() + result.stdout.lower()
    assert 'not found' in output or 'error' in output, \
        "Should indicate path not found"


def test_analyze_skill_with_duplicates_valid_json():
    """Test returns valid JSON for skill with duplicates."""
    skill_path = FIXTURES_DIR / 'skill-with-duplicates'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()
    assert data is not None, "Should return valid JSON"


def test_detect_exact_duplicates():
    """Test detection of exact duplicates."""
    skill_path = FIXTURES_DIR / 'skill-with-duplicates'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()

    exact_duplicates = data.get('exact_duplicates', [])
    assert len(exact_duplicates) >= 1, f"Should detect exact duplicates, found {len(exact_duplicates)}"


def test_extraction_candidates_field():
    """Test extraction_candidates field exists."""
    skill_path = FIXTURES_DIR / 'skill-with-duplicates'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()

    assert 'extraction_candidates' in data, "Should have extraction_candidates field"


def test_llm_review_required_flag():
    """Test contains llm_review_required flag in summary."""
    skill_path = FIXTURES_DIR / 'skill-with-duplicates'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()

    summary = data.get('summary', {})
    assert 'llm_review_required' in summary, "Should contain llm_review_required flag in summary"


def test_clean_skill_valid_json():
    """Test returns valid JSON for clean skill."""
    skill_path = FIXTURES_DIR / 'skill-clean'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()
    assert data is not None, "Should return valid JSON for clean skill"


def test_clean_skill_no_exact_duplicates():
    """Test no exact duplicates in clean skill."""
    skill_path = FIXTURES_DIR / 'skill-clean'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()

    exact_duplicates = data.get('exact_duplicates', [])
    assert len(exact_duplicates) == 0, f"Clean skill should have no exact duplicates, found {len(exact_duplicates)}"


def test_files_analyzed_count():
    """Test files_analyzed count for clean skill."""
    skill_path = FIXTURES_DIR / 'skill-clean'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()

    files_analyzed = data.get('files_analyzed', 0)
    assert files_analyzed >= 3, f"Should analyze multiple files, found {files_analyzed}"


def test_custom_similarity_threshold():
    """Test accepts custom similarity threshold."""
    skill_path = FIXTURES_DIR / 'skill-clean'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(
        SCRIPT_PATH,
        '--skill-path', str(skill_path),
        '--similarity-threshold', '0.3'
    )
    data = result.json()
    assert data is not None, "Should accept custom similarity threshold"


def test_content_blocks_extraction():
    """Test extraction of content blocks."""
    skill_path = FIXTURES_DIR / 'skill-with-duplicates'
    if not skill_path.exists():
        return  # Skip if fixture not available

    result = run_script(SCRIPT_PATH, '--skill-path', str(skill_path))
    data = result.json()

    content_blocks = data.get('content_blocks', [])
    assert len(content_blocks) >= 5, f"Should extract multiple content blocks, found {len(content_blocks)}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_script_exists,
        test_help_output,
        test_missing_argument_error,
        test_invalid_path_error,
        test_analyze_skill_with_duplicates_valid_json,
        test_detect_exact_duplicates,
        test_extraction_candidates_field,
        test_llm_review_required_flag,
        test_clean_skill_valid_json,
        test_clean_skill_no_exact_duplicates,
        test_files_analyzed_count,
        test_custom_similarity_threshold,
        test_content_blocks_extraction,
    ])
    sys.exit(runner.run())
