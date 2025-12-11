#!/usr/bin/env python3
"""Tests for cleanup-temp.py script."""

import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('plan-marshall', 'plan-marshall', 'cleanup-temp.py')


def test_clean_with_files():
    """Happy path - clean directory with files."""
    # Create temp .plan structure
    plan_dir = Path('.plan/temp/test-cleanup')
    plan_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = plan_dir.parent

    # Create test files
    (temp_dir / 'file1.txt').write_text('content1')
    (temp_dir / 'file2.json').write_text('{"key": "value"}')
    subdir = temp_dir / 'subdir'
    subdir.mkdir(exist_ok=True)
    (subdir / 'nested.txt').write_text('nested content')

    try:
        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir.parent.parent), 'clean')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'status\tsuccess' in result.stdout
        assert 'files_deleted\t' in result.stdout

        # Verify files were deleted
        remaining = list(temp_dir.iterdir())
        # Only test-cleanup should remain (we created it after listing)
        assert len([f for f in remaining if f.name != 'test-cleanup']) == 0, f"Files remain: {remaining}"
    finally:
        if plan_dir.exists():
            shutil.rmtree(plan_dir.parent.parent / 'temp', ignore_errors=True)


def test_clean_empty_directory():
    """Edge case - clean already empty directory."""
    plan_dir = Path('.plan/temp/test-cleanup-empty')
    temp_dir = plan_dir.parent
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir.parent.parent), 'clean')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'status\tsuccess' in result.stdout
        assert 'files_deleted\t0' in result.stdout
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_clean_nonexistent_directory():
    """Edge case - clean nonexistent temp directory."""
    result = run_script(SCRIPT_PATH, '--plan-dir', '/nonexistent/path', 'clean')
    assert result.success, "Should succeed even if directory doesn't exist"
    assert 'status\tsuccess' in result.stdout
    assert 'files_deleted\t0' in result.stdout


def test_clean_dry_run():
    """Dry run - show what would be deleted without deleting."""
    plan_dir = Path('.plan/temp/test-cleanup-dry')
    temp_dir = plan_dir.parent
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create test file
    test_file = temp_dir / 'keep-me.txt'
    test_file.write_text('should not be deleted')

    try:
        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir.parent.parent), 'clean', '--dry-run')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'status\tdry_run' in result.stdout
        assert 'files_deleted\t1' in result.stdout

        # Verify file was NOT deleted
        assert test_file.exists(), "File should not be deleted in dry-run mode"
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_status_with_files():
    """Status command - show directory statistics."""
    plan_dir = Path('.plan/temp/test-cleanup-status')
    temp_dir = plan_dir.parent
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create test files
    (temp_dir / 'file1.txt').write_text('12345')  # 5 bytes
    (temp_dir / 'file2.txt').write_text('1234567890')  # 10 bytes

    try:
        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir.parent.parent), 'status')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'exists\ttrue' in result.stdout
        assert 'file_count\t2' in result.stdout
        assert 'total_bytes\t15' in result.stdout
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_status_nonexistent():
    """Status command - nonexistent directory."""
    result = run_script(SCRIPT_PATH, '--plan-dir', '/nonexistent/path', 'status')
    assert result.success, f"Script failed: {result.stderr}"
    assert 'exists\tfalse' in result.stdout
    assert 'file_count\t0' in result.stdout


def test_missing_subcommand():
    """Invalid input - missing required subcommand."""
    result = run_script(SCRIPT_PATH)
    assert not result.success, "Should fail without subcommand"
    assert 'required' in result.stderr.lower() or 'error' in result.stderr.lower()


if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_clean_with_files,
        test_clean_empty_directory,
        test_clean_nonexistent_directory,
        test_clean_dry_run,
        test_status_with_files,
        test_status_nonexistent,
        test_missing_subcommand,
    ])
    sys.exit(runner.run())
