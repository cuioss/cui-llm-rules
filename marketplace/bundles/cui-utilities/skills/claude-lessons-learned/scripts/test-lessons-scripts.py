#!/usr/bin/env python3
"""
Test suite for lessons-learned scripts (write-lesson.py, update-lesson.py).

Usage:
    python3 test-lessons-scripts.py
"""

import json
import os
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
WRITE_LESSON = SCRIPT_DIR / 'write-lesson.py'
UPDATE_LESSON = SCRIPT_DIR / 'update-lesson.py'


def run_script(script_path: Path, args: list[str]) -> tuple[int, str, str]:
    """Run a script and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(script_path)] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


# write-lesson.py tests

def test_write_lesson_creates_file():
    """Test write-lesson.py creates file with correct content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'lessons'

        returncode, stdout, stderr = run_script(WRITE_LESSON, [
            '--component-type', 'command',
            '--component-name', 'test-cmd',
            '--component-bundle', 'test-bundle',
            '--category', 'bug',
            '--title', 'Test Title',
            '--detail', 'Test detail content.',
            '--lessons-dir', str(lessons_dir)
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['success'] is True, "Should succeed"
        assert 'file' in result, "Should have file path"
        assert 'id' in result, "Should have id"

        # Verify file exists
        file_path = Path(result['file'])
        assert file_path.exists(), "File should exist"

        # Verify content
        content = file_path.read_text()
        assert 'id=' in content, "Should have id metadata"
        assert 'component.type=command' in content, "Should have component type"
        assert 'component.name=test-cmd' in content, "Should have component name"
        assert 'category=bug' in content, "Should have category"
        assert 'applied=false' in content, "Should have applied=false"
        assert '# Test Title' in content, "Should have title"
        assert 'Test detail content.' in content, "Should have detail"


def test_write_lesson_generates_unique_ids():
    """Test write-lesson.py generates unique IDs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'lessons'

        # Create first lesson
        returncode1, stdout1, _ = run_script(WRITE_LESSON, [
            '--component-type', 'command',
            '--component-name', 'cmd1',
            '--component-bundle', 'bundle',
            '--category', 'bug',
            '--title', 'First',
            '--detail', 'First lesson.',
            '--lessons-dir', str(lessons_dir)
        ])

        # Create second lesson
        returncode2, stdout2, _ = run_script(WRITE_LESSON, [
            '--component-type', 'command',
            '--component-name', 'cmd2',
            '--component-bundle', 'bundle',
            '--category', 'bug',
            '--title', 'Second',
            '--detail', 'Second lesson.',
            '--lessons-dir', str(lessons_dir)
        ])

        assert returncode1 == 0 and returncode2 == 0, "Both should succeed"

        result1 = json.loads(stdout1)
        result2 = json.loads(stdout2)

        assert result1['id'] != result2['id'], "IDs should be unique"
        assert result1['id'].endswith('-001'), "First ID should end with 001"
        assert result2['id'].endswith('-002'), "Second ID should end with 002"


def test_write_lesson_with_example_and_related():
    """Test write-lesson.py includes optional sections."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'lessons'

        returncode, stdout, _ = run_script(WRITE_LESSON, [
            '--component-type', 'agent',
            '--component-name', 'test-agent',
            '--component-bundle', 'test-bundle',
            '--category', 'pattern',
            '--title', 'Good Pattern',
            '--detail', 'Detail here.',
            '--example', 'Code example here',
            '--related', 'Related info',
            '--lessons-dir', str(lessons_dir)
        ])

        assert returncode == 0, "Should succeed"

        result = json.loads(stdout)
        file_path = Path(result['file'])
        content = file_path.read_text()

        assert '## Example' in content, "Should have Example section"
        assert 'Code example here' in content, "Should have example content"
        assert '## Related' in content, "Should have Related section"
        assert 'Related info' in content, "Should have related content"


def test_write_lesson_creates_directory():
    """Test write-lesson.py creates directory if not exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'nested' / 'deeply' / 'lessons'

        returncode, stdout, _ = run_script(WRITE_LESSON, [
            '--component-type', 'skill',
            '--component-name', 'test-skill',
            '--component-bundle', 'bundle',
            '--category', 'improvement',
            '--title', 'Title',
            '--detail', 'Detail',
            '--lessons-dir', str(lessons_dir)
        ])

        assert returncode == 0, "Should succeed"
        assert lessons_dir.exists(), "Directory should be created"


def test_write_lesson_validates_category():
    """Test write-lesson.py validates category values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'lessons'

        returncode, _, stderr = run_script(WRITE_LESSON, [
            '--component-type', 'command',
            '--component-name', 'cmd',
            '--component-bundle', 'bundle',
            '--category', 'invalid-category',
            '--title', 'Title',
            '--detail', 'Detail',
            '--lessons-dir', str(lessons_dir)
        ])

        assert returncode != 0, "Should fail with invalid category"


# update-lesson.py tests

def test_update_lesson_updates_field():
    """Test update-lesson.py updates a single field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'lessons'

        # Create lesson first
        run_script(WRITE_LESSON, [
            '--component-type', 'command',
            '--component-name', 'cmd',
            '--component-bundle', 'bundle',
            '--category', 'bug',
            '--title', 'Title',
            '--detail', 'Detail',
            '--lessons-dir', str(lessons_dir)
        ])

        # Get created file
        lesson_file = list(lessons_dir.glob('*.md'))[0]

        # Update applied field
        returncode, stdout, _ = run_script(UPDATE_LESSON, [
            '--file', str(lesson_file),
            '--set', 'applied=true'
        ])

        assert returncode == 0, "Should succeed"

        result = json.loads(stdout)
        assert result['success'] is True
        assert 'applied' in result['updated_fields']

        # Verify content
        content = lesson_file.read_text()
        assert 'applied=true' in content, "Should have updated value"
        assert 'applied=false' not in content, "Should not have old value"


def test_update_lesson_preserves_content():
    """Test update-lesson.py preserves non-metadata content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'lessons'

        # Create lesson with specific content
        run_script(WRITE_LESSON, [
            '--component-type', 'command',
            '--component-name', 'cmd',
            '--component-bundle', 'bundle',
            '--category', 'bug',
            '--title', 'Specific Title',
            '--detail', 'Specific detail content that must be preserved.',
            '--lessons-dir', str(lessons_dir)
        ])

        lesson_file = list(lessons_dir.glob('*.md'))[0]

        # Update field
        run_script(UPDATE_LESSON, [
            '--file', str(lesson_file),
            '--set', 'applied=true'
        ])

        content = lesson_file.read_text()
        assert '# Specific Title' in content, "Title should be preserved"
        assert 'Specific detail content that must be preserved.' in content, "Detail should be preserved"


def test_update_lesson_multiple_fields():
    """Test update-lesson.py updates multiple fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lessons_dir = Path(tmpdir) / 'lessons'

        run_script(WRITE_LESSON, [
            '--component-type', 'command',
            '--component-name', 'cmd',
            '--component-bundle', 'bundle',
            '--category', 'bug',
            '--title', 'Title',
            '--detail', 'Detail',
            '--lessons-dir', str(lessons_dir)
        ])

        lesson_file = list(lessons_dir.glob('*.md'))[0]

        returncode, stdout, _ = run_script(UPDATE_LESSON, [
            '--file', str(lesson_file),
            '--set', 'applied=true',
            '--set', 'category=pattern'
        ])

        assert returncode == 0, "Should succeed"

        result = json.loads(stdout)
        assert len(result['updated_fields']) == 2, "Should have 2 updated fields"

        content = lesson_file.read_text()
        assert 'applied=true' in content
        assert 'category=pattern' in content


def test_update_lesson_file_not_found():
    """Test update-lesson.py handles missing file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent = Path(tmpdir) / 'nonexistent.md'

        returncode, _, stderr = run_script(UPDATE_LESSON, [
            '--file', str(nonexistent),
            '--set', 'applied=true'
        ])

        assert returncode != 0, "Should fail for missing file"

        result = json.loads(stderr)
        assert result['success'] is False
        assert 'not found' in result['error'].lower()


def test_update_lesson_invalid_format():
    """Test update-lesson.py validates KEY=VALUE format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy file
        dummy = Path(tmpdir) / 'dummy.md'
        dummy.write_text("id=test\n\n# Title\n")

        returncode, _, stderr = run_script(UPDATE_LESSON, [
            '--file', str(dummy),
            '--set', 'invalid-format-no-equals'
        ])

        assert returncode != 0, "Should fail for invalid format"


def main():
    """Run all tests."""
    print("=" * 50)
    print("Test Suite: lessons-learned scripts")
    print("=" * 50)
    print()

    runner = TestRunner()

    # write-lesson.py tests
    print("write-lesson.py:")
    runner.run_test("creates file", test_write_lesson_creates_file)
    runner.run_test("generates unique IDs", test_write_lesson_generates_unique_ids)
    runner.run_test("with example and related", test_write_lesson_with_example_and_related)
    runner.run_test("creates directory", test_write_lesson_creates_directory)
    runner.run_test("validates category", test_write_lesson_validates_category)

    # update-lesson.py tests
    print("\nupdate-lesson.py:")
    runner.run_test("updates field", test_update_lesson_updates_field)
    runner.run_test("preserves content", test_update_lesson_preserves_content)
    runner.run_test("multiple fields", test_update_lesson_multiple_fields)
    runner.run_test("file not found", test_update_lesson_file_not_found)
    runner.run_test("invalid format", test_update_lesson_invalid_format)

    return runner.summary()


if __name__ == '__main__':
    sys.exit(main())
