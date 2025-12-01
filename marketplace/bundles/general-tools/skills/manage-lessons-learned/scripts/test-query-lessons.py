#!/usr/bin/env python3
"""
test-query-lessons.py

Test script for query-lessons.py.

Creates sample lesson files and tests various query scenarios.

Usage:
    python3 test-query-lessons.py

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestQueryLessons(unittest.TestCase):
    """Test cases for query-lessons.py."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.lessons_dir = cls.test_dir / '.plan' / 'lessons-learned'
        cls.lessons_dir.mkdir(parents=True)

        # Script location
        cls.script_dir = Path(__file__).parent
        cls.query_script = cls.script_dir / 'query-lessons.py'

        # Create sample lessons
        cls.create_test_lessons()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    @classmethod
    def create_test_lessons(cls):
        """Create sample lesson files for testing."""
        lessons = [
            # Lesson 1: Bug in maven-build-and-fix (unapplied)
            ('2025-11-27-001.md', '''id=2025-11-27-001
component.type=command
component.name=maven-build-and-fix
component.bundle=builder-maven
date=2025-11-27
category=bug
applied=false

# Paths with spaces cause failures

## Detail

Bash calls fail when paths contain spaces.
'''),
            # Lesson 2: Improvement in maven-build-and-fix (unapplied)
            ('2025-11-27-002.md', '''id=2025-11-27-002
component.type=command
component.name=maven-build-and-fix
component.bundle=builder-maven
date=2025-11-27
category=improvement
applied=false

# Add progress indicator

## Detail

Show progress for long operations.
'''),
            # Lesson 3: Pattern in builder-maven-rules (applied)
            ('2025-11-27-003.md', '''id=2025-11-27-003
component.type=skill
component.name=builder-maven-rules
component.bundle=builder-maven
date=2025-11-27
category=pattern
applied=true

# Validate inputs early

## Detail

Check inputs in Step 1.
'''),
            # Lesson 4: Bug in java-create (unapplied)
            ('2025-11-26-001.md', '''id=2025-11-26-001
component.type=command
component.name=java-create
component.bundle=cui-java-expert
date=2025-11-26
category=bug
applied=false

# Missing package validation

## Detail

Need to validate package names.
'''),
            # Lesson 5: Anti-pattern in java-refactor (applied)
            ('2025-11-25-001.md', '''id=2025-11-25-001
component.type=command
component.name=java-refactor
component.bundle=cui-java-expert
date=2025-11-25
category=anti-pattern
applied=true

# Don't modify during iteration

## Detail

Collect files first, then process.
'''),
        ]

        for filename, content in lessons:
            (cls.lessons_dir / filename).write_text(content)

    def run_query(self, *args):
        """Run query-lessons.py with arguments and return output."""
        cmd = [sys.executable, str(self.query_script), '--lessons-dir', str(self.lessons_dir)]
        cmd.extend(args)

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode

    def assert_json_valid(self, output):
        """Assert output is valid JSON."""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            self.fail(f'Invalid JSON: {output}')

    def test_query_all_lessons(self):
        """Test querying all lessons."""
        stdout, stderr, code = self.run_query('--all')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 5)

    def test_filter_by_component_name(self):
        """Test filtering by component name."""
        stdout, stderr, code = self.run_query('--component', 'maven-build-and-fix')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 2)

    def test_filter_by_applied_false(self):
        """Test filtering by applied status (false)."""
        stdout, stderr, code = self.run_query('--applied', 'false')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 3)

    def test_filter_by_applied_true(self):
        """Test filtering by applied status (true)."""
        stdout, stderr, code = self.run_query('--applied', 'true')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 2)

    def test_filter_by_category(self):
        """Test filtering by category."""
        stdout, stderr, code = self.run_query('--category', 'bug')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 2)

    def test_filter_by_bundle(self):
        """Test filtering by bundle."""
        stdout, stderr, code = self.run_query('--bundle', 'builder-maven')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 3)

    def test_combine_filters(self):
        """Test combining multiple filters."""
        stdout, stderr, code = self.run_query(
            '--component', 'maven-build-and-fix',
            '--applied', 'false'
        )
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 2)

    def test_filter_by_type(self):
        """Test filtering by component type."""
        stdout, stderr, code = self.run_query('--type', 'command')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 4)

    def test_no_matches(self):
        """Test query with no matches."""
        stdout, stderr, code = self.run_query('--component', 'nonexistent')
        data = self.assert_json_valid(stdout)
        self.assertEqual(len(data), 0)

    def test_empty_directory(self):
        """Test handling empty lessons directory."""
        empty_dir = self.test_dir / '.claude' / 'empty-lessons'
        empty_dir.mkdir(parents=True)

        cmd = [sys.executable, str(self.query_script),
               '--lessons-dir', str(empty_dir), '--all']
        result = subprocess.run(cmd, capture_output=True, text=True)

        data = self.assert_json_valid(result.stdout)
        self.assertEqual(len(data), 0)

    def test_nonexistent_directory(self):
        """Test handling non-existent directory."""
        nonexistent = self.test_dir / '.claude' / 'nonexistent'

        cmd = [sys.executable, str(self.query_script),
               '--lessons-dir', str(nonexistent), '--all']
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Should contain error message
        self.assertIn('not found', result.stdout.lower() + result.stderr.lower())


def main():
    """Run tests and report results."""
    # Check if query-lessons.py exists
    script_dir = Path(__file__).parent
    query_script = script_dir / 'query-lessons.py'

    if not query_script.exists():
        print(f'ERROR: Script not found: {query_script}', file=sys.stderr)
        return 1

    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestQueryLessons)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return appropriate exit code
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
