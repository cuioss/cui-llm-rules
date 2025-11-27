#!/usr/bin/env python3
"""Tests for analyze-skill-structure.sh script (plugin-doctor version).

Migrated from test-analyze-skill-structure.sh - tests skill structure analysis
with improved reference detection including table-format refs, code block examples,
and cross-skill references.
"""

import subprocess
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Script under test
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SCRIPT_PATH = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-plugin-development-tools' / 'skills' / 'plugin-doctor' / 'scripts' / 'analyze-skill-structure.sh'
FIXTURES_DIR = Path(__file__).parent / 'fixtures' / 'skill-structure'


def run_bash_script(script_path, *args):
    """Run a bash script and return result."""
    result = subprocess.run(
        ['bash', str(script_path), *args],
        capture_output=True,
        text=True
    )
    return result


def parse_json(output):
    """Parse JSON from output."""
    import json
    return json.loads(output)


# =============================================================================
# Tests - Table-Format References
# =============================================================================

def test_table_refs_no_unreferenced_files():
    """Test that table-referenced files are detected (no unreferenced files)."""
    test_dir = FIXTURES_DIR / 'table-references'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    unreferenced = data.get('standards_files', {}).get('unreferenced_files', [])
    assert len(unreferenced) == 0, f"Should have no unreferenced files, found {len(unreferenced)}"


def test_table_refs_no_missing_files():
    """Test that all referenced files exist (no missing files)."""
    test_dir = FIXTURES_DIR / 'table-references'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    missing = data.get('standards_files', {}).get('missing_files', [])
    assert len(missing) == 0, f"Should have no missing files, found {len(missing)}"


def test_table_refs_perfect_score():
    """Test perfect score for table-referenced files."""
    test_dir = FIXTURES_DIR / 'table-references'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    score = data.get('structure_score', 0)
    assert score >= 100, f"Score should be 100, got {score}"


# =============================================================================
# Tests - Code Block Examples
# =============================================================================

def test_code_block_no_false_positive_missing():
    """Test that example paths in code blocks are NOT detected as missing files."""
    test_dir = FIXTURES_DIR / 'code-block-examples'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    missing = data.get('standards_files', {}).get('missing_files', [])
    assert len(missing) == 0, f"Should not flag code block examples as missing, found {len(missing)}"


def test_code_block_no_unreferenced():
    """Test that actual references are detected alongside code blocks."""
    test_dir = FIXTURES_DIR / 'code-block-examples'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    unreferenced = data.get('standards_files', {}).get('unreferenced_files', [])
    assert len(unreferenced) == 0, f"Should have no unreferenced files, found {len(unreferenced)}"


def test_code_block_perfect_score():
    """Test perfect score when code blocks are handled correctly."""
    test_dir = FIXTURES_DIR / 'code-block-examples'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    score = data.get('structure_score', 0)
    assert score >= 100, f"Score should be 100, got {score}"


# =============================================================================
# Tests - Cross-Skill References
# =============================================================================

def test_cross_skill_no_false_positive_missing():
    """Test that cross-skill references are NOT flagged as missing."""
    test_dir = FIXTURES_DIR / 'cross-skill-references'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    missing = data.get('standards_files', {}).get('missing_files', [])
    assert len(missing) == 0, f"Cross-skill refs should not be flagged as missing, found {len(missing)}"


def test_cross_skill_no_unreferenced():
    """Test that local references are detected with cross-skill refs."""
    test_dir = FIXTURES_DIR / 'cross-skill-references'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    unreferenced = data.get('standards_files', {}).get('unreferenced_files', [])
    assert len(unreferenced) == 0, f"Should have no unreferenced files, found {len(unreferenced)}"


def test_cross_skill_perfect_score():
    """Test perfect score when cross-skill refs are handled correctly."""
    test_dir = FIXTURES_DIR / 'cross-skill-references'
    if not test_dir.exists():
        return  # Skip if fixture not available

    result = run_bash_script(SCRIPT_PATH, str(test_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    score = data.get('structure_score', 0)
    assert score >= 100, f"Score should be 100, got {score}"


# =============================================================================
# Tests - Real Skills Validation
# =============================================================================

def test_real_plugin_architecture_skill():
    """Test plugin-architecture skill (has example code blocks)."""
    skill_dir = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-plugin-development-tools' / 'skills' / 'plugin-architecture'
    if not skill_dir.exists():
        return  # Skip if not found

    result = run_bash_script(SCRIPT_PATH, str(skill_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    score = data.get('structure_score', 0)
    assert score >= 90, f"plugin-architecture should score >= 90, got {score}"


def test_real_plugin_doctor_skill():
    """Test plugin-doctor skill (has table-format refs and cross-skill refs)."""
    skill_dir = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-plugin-development-tools' / 'skills' / 'plugin-doctor'
    if not skill_dir.exists():
        return  # Skip if not found

    result = run_bash_script(SCRIPT_PATH, str(skill_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    score = data.get('structure_score', 0)
    assert score >= 90, f"plugin-doctor should score >= 90, got {score}"


def test_real_plugin_create_skill():
    """Test plugin-create skill (has template files in assets)."""
    skill_dir = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-plugin-development-tools' / 'skills' / 'plugin-create'
    if not skill_dir.exists():
        return  # Skip if not found

    result = run_bash_script(SCRIPT_PATH, str(skill_dir))
    assert result.returncode == 0, f"Script returned error: {result.stderr}"

    data = parse_json(result.stdout)
    score = data.get('structure_score', 0)
    # Note: plugin-create has some documented-only files, score 80 is acceptable
    assert score >= 80, f"plugin-create should score >= 80, got {score}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_table_refs_no_unreferenced_files,
        test_table_refs_no_missing_files,
        test_table_refs_perfect_score,
        test_code_block_no_false_positive_missing,
        test_code_block_no_unreferenced,
        test_code_block_perfect_score,
        test_cross_skill_no_false_positive_missing,
        test_cross_skill_no_unreferenced,
        test_cross_skill_perfect_score,
        test_real_plugin_architecture_skill,
        test_real_plugin_doctor_skill,
        test_real_plugin_create_skill,
    ])
    sys.exit(runner.run())
