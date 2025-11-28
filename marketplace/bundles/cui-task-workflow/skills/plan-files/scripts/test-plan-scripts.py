#!/usr/bin/env python3
"""
Test suite for plan-files scripts (write-plan.py, write-config.py,
write-references.py, update-progress.py).

Usage:
    python3 test-plan-scripts.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


class TestRunner:
    """Simple test runner for stdlib-only testing."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def run_test(self, name: str, test_func):
        """Run a single test function."""
        self.tests_run += 1
        try:
            test_func()
            self.tests_passed += 1
            print(f"  ✓ {name}")
        except AssertionError as e:
            self.tests_failed += 1
            self.failures.append((name, str(e)))
            print(f"  ✗ {name}: {e}")
        except Exception as e:
            self.tests_failed += 1
            self.failures.append((name, f"Exception: {e}"))
            print(f"  ✗ {name}: Exception: {e}")

    def summary(self):
        """Print test summary and return exit code."""
        print("\n" + "=" * 50)
        print(f"Tests: {self.tests_run}, Passed: {self.tests_passed}, Failed: {self.tests_failed}")

        if self.failures:
            print("\nFailures:")
            for name, msg in self.failures:
                print(f"  - {name}: {msg}")

        return 0 if self.tests_failed == 0 else 1


SCRIPT_DIR = Path(__file__).parent
WRITE_PLAN = SCRIPT_DIR / 'write-plan.py'
WRITE_CONFIG = SCRIPT_DIR / 'write-config.py'
WRITE_REFERENCES = SCRIPT_DIR / 'write-references.py'
UPDATE_PROGRESS = SCRIPT_DIR / 'update-progress.py'


def run_script(script_path: Path, args: list[str]) -> tuple[int, str, str]:
    """Run a script and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(script_path)] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


# write-plan.py tests

def test_write_plan_creates_file():
    """Test write-plan.py creates plan file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        phases_json = json.dumps([
            {"name": "init", "status": "in_progress", "tasks": 3},
            {"name": "implement", "status": "pending", "tasks": 5}
        ])

        returncode, stdout, stderr = run_script(WRITE_PLAN, [
            '--plan-dir', str(plan_dir),
            '--title', 'Test Plan',
            '--current-phase', 'init',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['success'] is True

        file_path = plan_dir / 'plan.md'
        assert file_path.exists(), "Plan file should exist"

        content = file_path.read_text()
        assert '# Task Plan: Test Plan' in content
        assert '**Current Phase**: init' in content
        assert '| init | in_progress | 3 | 0/3 |' in content


def test_write_plan_with_detailed_tasks():
    """Test write-plan.py with task details."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        phases_json = json.dumps([{
            "name": "init",
            "status": "in_progress",
            "tasks": [{
                "name": "Setup",
                "phase": "init",
                "goal": "Setup environment",
                "checklist": ["Install deps", "Configure tools"]
            }]
        }])

        returncode, stdout, _ = run_script(WRITE_PLAN, [
            '--plan-dir', str(plan_dir),
            '--title', 'Detailed Plan',
            '--current-phase', 'init',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        ])

        assert returncode == 0

        content = (plan_dir / 'plan.md').read_text()
        assert '### Task 1: Setup' in content
        assert '- [ ] Install deps' in content
        assert '- [ ] Configure tools' in content


# write-config.py tests

def test_write_config_creates_file():
    """Test write-config.py creates config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        returncode, stdout, stderr = run_script(WRITE_CONFIG, [
            '--plan-dir', str(plan_dir),
            '--plan-type', 'implementation',
            '--technology', 'java',
            '--build-system', 'maven',
            '--compatibility', 'deprecations',
            '--commit-strategy', 'phase-specific',
            '--finalizing', 'pr-workflow'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['success'] is True

        file_path = plan_dir / 'config.md'
        assert file_path.exists()

        content = file_path.read_text()
        assert '**Plan Type**: implementation' in content
        assert '| Technology | java |' in content
        assert '| Build System | maven |' in content


def test_write_config_with_context():
    """Test write-config.py with branch and issue."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        returncode, stdout, _ = run_script(WRITE_CONFIG, [
            '--plan-dir', str(plan_dir),
            '--plan-type', 'simple',
            '--technology', 'javascript',
            '--build-system', 'npm',
            '--compatibility', 'breaking',
            '--commit-strategy', 'complete',
            '--finalizing', 'commit-only',
            '--branch', 'feature/test',
            '--issue', '#123'
        ])

        assert returncode == 0

        content = (plan_dir / 'config.md').read_text()
        assert '| Branch | feature/test |' in content
        assert '| Issue | #123 |' in content


def test_write_config_validates_enums():
    """Test write-config.py validates enum values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        returncode, _, _ = run_script(WRITE_CONFIG, [
            '--plan-dir', str(plan_dir),
            '--plan-type', 'invalid',
            '--technology', 'java',
            '--build-system', 'maven',
            '--compatibility', 'deprecations',
            '--commit-strategy', 'phase-specific',
            '--finalizing', 'pr-workflow'
        ])

        assert returncode != 0, "Should fail with invalid plan-type"


# write-references.py tests

def test_write_references_creates_file():
    """Test write-references.py creates file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        returncode, stdout, stderr = run_script(WRITE_REFERENCES, [
            '--plan-dir', str(plan_dir),
            '--action', 'set',
            '--section', 'branch',
            '--value', 'feature/test'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['success'] is True
        assert result['created'] is True

        file_path = plan_dir / 'references.md'
        assert file_path.exists()

        content = file_path.read_text()
        assert '**Branch**: `feature/test`' in content


def test_write_references_adds_implementation_file():
    """Test write-references.py adds to list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        # Create initial file
        run_script(WRITE_REFERENCES, [
            '--plan-dir', str(plan_dir),
            '--action', 'set',
            '--section', 'branch',
            '--value', 'main'
        ])

        # Add implementation file
        returncode, stdout, _ = run_script(WRITE_REFERENCES, [
            '--plan-dir', str(plan_dir),
            '--action', 'add',
            '--section', 'implementation_files',
            '--value', 'src/main/java/Foo.java'
        ])

        assert returncode == 0

        content = (plan_dir / 'references.md').read_text()
        assert '- src/main/java/Foo.java' in content


def test_write_references_removes_item():
    """Test write-references.py removes from list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        # Create and add
        run_script(WRITE_REFERENCES, [
            '--plan-dir', str(plan_dir),
            '--action', 'add',
            '--section', 'implementation_files',
            '--value', 'FileA.java'
        ])
        run_script(WRITE_REFERENCES, [
            '--plan-dir', str(plan_dir),
            '--action', 'add',
            '--section', 'implementation_files',
            '--value', 'FileB.java'
        ])

        # Remove
        run_script(WRITE_REFERENCES, [
            '--plan-dir', str(plan_dir),
            '--action', 'remove',
            '--section', 'implementation_files',
            '--value', 'FileA.java'
        ])

        content = (plan_dir / 'references.md').read_text()
        assert '- FileA.java' not in content
        assert '- FileB.java' in content


# update-progress.py tests

def test_update_progress_completes_items():
    """Test update-progress.py marks items complete."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        # Create plan with tasks
        phases_json = json.dumps([{
            "name": "init",
            "status": "in_progress",
            "tasks": [{
                "name": "Setup",
                "phase": "init",
                "goal": "Setup",
                "checklist": ["Item A", "Item B", "Item C"]
            }]
        }])

        run_script(WRITE_PLAN, [
            '--plan-dir', str(plan_dir),
            '--title', 'Test',
            '--current-phase', 'init',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        ])

        # Complete items
        returncode, stdout, stderr = run_script(UPDATE_PROGRESS, [
            '--plan-dir', str(plan_dir),
            '--phase', 'init',
            '--task-id', '1',
            '--complete-items', 'Item A,Item B'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['success'] is True
        assert result['items_completed'] == 2

        content = (plan_dir / 'plan.md').read_text()
        assert '- [x] Item A' in content
        assert '- [x] Item B' in content
        assert '- [ ] Item C' in content


def test_update_progress_updates_table():
    """Test update-progress.py updates progress table."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'plan'

        phases_json = json.dumps([{
            "name": "init",
            "status": "pending",
            "tasks": [{
                "name": "Task1",
                "phase": "init",
                "goal": "Goal",
                "checklist": ["A", "B"]
            }]
        }])

        run_script(WRITE_PLAN, [
            '--plan-dir', str(plan_dir),
            '--title', 'Test',
            '--current-phase', 'init',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        ])

        # Complete all items
        run_script(UPDATE_PROGRESS, [
            '--plan-dir', str(plan_dir),
            '--phase', 'init',
            '--task-id', '1',
            '--complete-items', 'A,B'
        ])

        content = (plan_dir / 'plan.md').read_text()
        # Should show 2/2 completed
        assert '| init | completed | 2 | 2/2 |' in content


def test_update_progress_file_not_found():
    """Test update-progress.py handles missing file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'nonexistent'

        returncode, _, stderr = run_script(UPDATE_PROGRESS, [
            '--plan-dir', str(plan_dir),
            '--phase', 'init',
            '--task-id', '1',
            '--complete-items', 'Item'
        ])

        assert returncode != 0
        result = json.loads(stderr)
        assert result['success'] is False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Test Suite: plan-files scripts")
    print("=" * 50)
    print()

    runner = TestRunner()

    # write-plan.py tests
    print("write-plan.py:")
    runner.run_test("creates file", test_write_plan_creates_file)
    runner.run_test("with detailed tasks", test_write_plan_with_detailed_tasks)

    # write-config.py tests
    print("\nwrite-config.py:")
    runner.run_test("creates file", test_write_config_creates_file)
    runner.run_test("with context", test_write_config_with_context)
    runner.run_test("validates enums", test_write_config_validates_enums)

    # write-references.py tests
    print("\nwrite-references.py:")
    runner.run_test("creates file", test_write_references_creates_file)
    runner.run_test("adds implementation file", test_write_references_adds_implementation_file)
    runner.run_test("removes item", test_write_references_removes_item)

    # update-progress.py tests
    print("\nupdate-progress.py:")
    runner.run_test("completes items", test_update_progress_completes_items)
    runner.run_test("updates table", test_update_progress_updates_table)
    runner.run_test("file not found", test_update_progress_file_not_found)

    return runner.summary()


if __name__ == '__main__':
    sys.exit(main())
