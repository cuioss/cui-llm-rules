#!/usr/bin/env python3
"""Tests for plugin-fix scripts.

Migrated from test-all-scripts.sh - tests plugin-fix scripts including
extract-fixable-issues.py, categorize-fixes.py, apply-fix.py, and verify-fix.sh.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Scripts under test (these scripts are in plugin-doctor, not plugin-fix)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'cui-plugin-development-tools' / 'skills'
PLUGIN_DOCTOR_DIR = SKILLS_DIR / 'plugin-doctor'
FIXTURES_DIR = Path(__file__).parent / 'fixtures'

EXTRACT_SCRIPT = PLUGIN_DOCTOR_DIR / 'scripts' / 'extract-fixable-issues.py'
CATEGORIZE_SCRIPT = PLUGIN_DOCTOR_DIR / 'scripts' / 'categorize-fixes.py'
APPLY_SCRIPT = PLUGIN_DOCTOR_DIR / 'scripts' / 'apply-fix.py'
VERIFY_SCRIPT = PLUGIN_DOCTOR_DIR / 'scripts' / 'verify-fix.py'


def parse_json(output):
    """Parse JSON from output."""
    import json
    return json.loads(output)


# =============================================================================
# Tests - extract-fixable-issues.py
# =============================================================================

def test_extract_from_mixed_diagnosis():
    """Test extraction from mixed diagnosis (has both fixable and non-fixable)."""
    fixture = FIXTURES_DIR / 'diagnosis' / 'diagnosis-with-fixable.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(EXTRACT_SCRIPT, str(fixture))
    data = result.json()

    total_count = data.get('total_count', 0)
    assert total_count == 6, f"Should extract 6 fixable issues, got {total_count}"


def test_extract_from_no_fixable_diagnosis():
    """Test extraction from no-fixable diagnosis."""
    fixture = FIXTURES_DIR / 'diagnosis' / 'diagnosis-no-fixable.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(EXTRACT_SCRIPT, str(fixture))
    data = result.json()

    total_count = data.get('total_count', 0)
    assert total_count == 0, f"Should extract 0 from no-fixable, got {total_count}"


def test_extract_from_all_fixable_diagnosis():
    """Test extraction from all-fixable diagnosis."""
    fixture = FIXTURES_DIR / 'diagnosis' / 'diagnosis-all-fixable.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(EXTRACT_SCRIPT, str(fixture))
    data = result.json()

    total_count = data.get('total_count', 0)
    assert total_count == 4, f"Should extract 4 from all-fixable, got {total_count}"


def test_extract_from_empty_diagnosis():
    """Test extraction from empty diagnosis."""
    fixture = FIXTURES_DIR / 'diagnosis' / 'diagnosis-empty.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(EXTRACT_SCRIPT, str(fixture))
    data = result.json()

    total_count = data.get('total_count', 0)
    assert total_count == 0, f"Should extract 0 from empty, got {total_count}"


def test_extract_stdin_input():
    """Test extraction from stdin input."""
    fixture = FIXTURES_DIR / 'diagnosis' / 'diagnosis-with-fixable.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    content = fixture.read_text()
    proc = subprocess.run(
        ['python3', str(EXTRACT_SCRIPT), '-'],
        input=content,
        capture_output=True,
        text=True
    )

    assert 'fixable_issues' in proc.stdout, "Stdin input should work"


def test_extract_invalid_json_error():
    """Test extraction returns error for invalid JSON."""
    proc = subprocess.run(
        ['python3', str(EXTRACT_SCRIPT), '-'],
        input='not json',
        capture_output=True,
        text=True
    )

    combined = proc.stdout.lower() + proc.stderr.lower()
    assert 'invalid json' in combined or 'error' in combined, "Should return error for invalid JSON"


# =============================================================================
# Tests - categorize-fixes.py
# =============================================================================

def test_categorize_safe_only():
    """Test categorization of safe-only issues."""
    fixture = FIXTURES_DIR / 'categorization' / 'extracted-safe-only.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(CATEGORIZE_SCRIPT, str(fixture))
    data = result.json()

    safe_count = data.get('summary', {}).get('safe_count', 0)
    risky_count = data.get('summary', {}).get('risky_count', 0)

    assert safe_count == 3, f"Should have 3 safe, got {safe_count}"
    assert risky_count == 0, f"Should have 0 risky, got {risky_count}"


def test_categorize_risky_only():
    """Test categorization of risky-only issues."""
    fixture = FIXTURES_DIR / 'categorization' / 'extracted-risky-only.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(CATEGORIZE_SCRIPT, str(fixture))
    data = result.json()

    safe_count = data.get('summary', {}).get('safe_count', 0)
    risky_count = data.get('summary', {}).get('risky_count', 0)

    assert safe_count == 0, f"Should have 0 safe, got {safe_count}"
    assert risky_count == 3, f"Should have 3 risky, got {risky_count}"


def test_categorize_mixed():
    """Test categorization of mixed issues."""
    fixture = FIXTURES_DIR / 'categorization' / 'extracted-mixed.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(CATEGORIZE_SCRIPT, str(fixture))
    data = result.json()

    safe_count = data.get('summary', {}).get('safe_count', 0)
    risky_count = data.get('summary', {}).get('risky_count', 0)

    assert safe_count == 3, f"Should have 3 safe, got {safe_count}"
    assert risky_count == 2, f"Should have 2 risky, got {risky_count}"


def test_categorize_empty():
    """Test categorization of empty issues."""
    fixture = FIXTURES_DIR / 'categorization' / 'extracted-empty.json'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(CATEGORIZE_SCRIPT, str(fixture))
    data = result.json()

    total_count = data.get('summary', {}).get('total_count', 0)
    assert total_count == 0, f"Should have 0 total, got {total_count}"


# =============================================================================
# Tests - apply-fix.py
# =============================================================================

class ApplyFixContext:
    """Context manager for apply-fix tests."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        # Copy fixtures to temp dir
        src_dir = FIXTURES_DIR / 'apply-fix'
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.temp_dir / item.name)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def test_apply_missing_frontmatter_fix():
    """Test applying missing frontmatter fix."""
    with ApplyFixContext() as temp_dir:
        fix_json = '{"type": "missing-frontmatter", "file": "agent-missing-frontmatter.md"}'

        proc = subprocess.run(
            ['python3', str(APPLY_SCRIPT), '-', str(temp_dir)],
            input=fix_json,
            capture_output=True,
            text=True
        )

        data = parse_json(proc.stdout)
        success = data.get('success', False)
        assert success is True, f"Should succeed applying missing-frontmatter fix"


def test_apply_frontmatter_actually_added():
    """Test frontmatter is actually added to file."""
    with ApplyFixContext() as temp_dir:
        fix_json = '{"type": "missing-frontmatter", "file": "agent-missing-frontmatter.md"}'

        subprocess.run(
            ['python3', str(APPLY_SCRIPT), '-', str(temp_dir)],
            input=fix_json,
            capture_output=True,
            text=True
        )

        target_file = temp_dir / 'agent-missing-frontmatter.md'
        if target_file.exists():
            content = target_file.read_text()
            assert content.startswith('---'), "Frontmatter should be added to file"


def test_apply_array_syntax_fix():
    """Test applying array syntax fix."""
    with ApplyFixContext() as temp_dir:
        fix_json = '{"type": "array-syntax-tools", "file": "agent-array-syntax.md"}'

        proc = subprocess.run(
            ['python3', str(APPLY_SCRIPT), '-', str(temp_dir)],
            input=fix_json,
            capture_output=True,
            text=True
        )

        data = parse_json(proc.stdout)
        success = data.get('success', False)
        assert success is True, f"Should succeed applying array-syntax fix"


def test_apply_rule6_fix():
    """Test applying rule-6 fix (remove Task tool)."""
    with ApplyFixContext() as temp_dir:
        fix_json = '{"type": "rule-6-violation", "file": "agent-task-tool.md"}'

        proc = subprocess.run(
            ['python3', str(APPLY_SCRIPT), '-', str(temp_dir)],
            input=fix_json,
            capture_output=True,
            text=True
        )

        data = parse_json(proc.stdout)
        success = data.get('success', False)
        assert success is True, f"Should succeed applying rule-6 fix"


def test_apply_missing_file_graceful():
    """Test handling missing file gracefully."""
    with ApplyFixContext() as temp_dir:
        fix_json = '{"type": "missing-frontmatter", "file": "nonexistent.md"}'

        proc = subprocess.run(
            ['python3', str(APPLY_SCRIPT), '-', str(temp_dir)],
            input=fix_json,
            capture_output=True,
            text=True
        )

        data = parse_json(proc.stdout)
        success = data.get('success', False)
        assert success is False, f"Should fail for missing file"


def test_apply_creates_backup():
    """Test backup files are created."""
    with ApplyFixContext() as temp_dir:
        fix_json = '{"type": "missing-frontmatter", "file": "agent-missing-frontmatter.md"}'

        subprocess.run(
            ['python3', str(APPLY_SCRIPT), '-', str(temp_dir)],
            input=fix_json,
            capture_output=True,
            text=True
        )

        backup_files = list(temp_dir.glob('*.fix-backup'))
        assert len(backup_files) > 0, "Should create backup files"


# =============================================================================
# Tests - verify-fix.sh
# =============================================================================

def test_verify_frontmatter_on_perfect_file():
    """Test verify frontmatter on perfect file."""
    fixture = FIXTURES_DIR / 'apply-fix' / 'perfect-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(VERIFY_SCRIPT, 'missing-frontmatter', str(fixture))
    data = parse_json(result.stdout)

    resolved = data.get('issue_resolved', False)
    assert resolved is True, f"Should be resolved on perfect file, got {resolved}"


def test_verify_frontmatter_on_broken_file():
    """Test verify frontmatter on broken file."""
    fixture = FIXTURES_DIR / 'apply-fix' / 'agent-missing-frontmatter.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(VERIFY_SCRIPT, 'missing-frontmatter', str(fixture))
    data = parse_json(result.stdout)

    resolved = data.get('issue_resolved', False)
    assert resolved is False, f"Should not be resolved on broken file, got {resolved}"


def test_verify_array_syntax_on_good_file():
    """Test verify array-syntax on good file."""
    fixture = FIXTURES_DIR / 'apply-fix' / 'perfect-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(VERIFY_SCRIPT, 'array-syntax-tools', str(fixture))
    data = parse_json(result.stdout)

    resolved = data.get('issue_resolved', False)
    assert resolved is True, f"Should be resolved on good file, got {resolved}"


def test_verify_rule6_on_good_file():
    """Test verify rule-6 on good file."""
    fixture = FIXTURES_DIR / 'apply-fix' / 'perfect-agent.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(VERIFY_SCRIPT, 'rule-6-violation', str(fixture))
    data = parse_json(result.stdout)

    resolved = data.get('issue_resolved', False)
    assert resolved is True, f"Should be resolved on good file, got {resolved}"


def test_verify_rule6_on_violating_file():
    """Test verify rule-6 on violating file."""
    fixture = FIXTURES_DIR / 'apply-fix' / 'agent-task-tool.md'
    if not fixture.exists():
        return  # Skip if fixture not available

    result = run_script(VERIFY_SCRIPT, 'rule-6-violation', str(fixture))
    data = parse_json(result.stdout)

    resolved = data.get('issue_resolved', False)
    assert resolved is False, f"Should not be resolved on violating file, got {resolved}"


def test_verify_missing_file_error():
    """Test verify handles missing file."""
    result = run_script(VERIFY_SCRIPT, 'missing-frontmatter', '/nonexistent/file.md')

    combined = result.stdout.lower() + result.stderr.lower()
    assert 'not found' in combined or 'error' in combined, "Should indicate file not found"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_extract_from_mixed_diagnosis,
        test_extract_from_no_fixable_diagnosis,
        test_extract_from_all_fixable_diagnosis,
        test_extract_from_empty_diagnosis,
        test_extract_stdin_input,
        test_extract_invalid_json_error,
        test_categorize_safe_only,
        test_categorize_risky_only,
        test_categorize_mixed,
        test_categorize_empty,
        test_apply_missing_frontmatter_fix,
        test_apply_frontmatter_actually_added,
        test_apply_array_syntax_fix,
        test_apply_rule6_fix,
        test_apply_missing_file_graceful,
        test_apply_creates_backup,
        test_verify_frontmatter_on_perfect_file,
        test_verify_frontmatter_on_broken_file,
        test_verify_array_syntax_on_good_file,
        test_verify_rule6_on_good_file,
        test_verify_rule6_on_violating_file,
        test_verify_missing_file_error,
    ])
    sys.exit(runner.run())
