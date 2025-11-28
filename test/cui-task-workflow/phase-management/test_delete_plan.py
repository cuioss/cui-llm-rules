#!/usr/bin/env python3
"""Tests for delete-plan.py script."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Script location
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'cui-task-workflow' / 'skills' / 'phase-management' / 'scripts'
SCRIPT_PATH = SCRIPT_DIR / 'delete-plan.py'


def run_script(*args) -> tuple:
    """Run the delete-plan.py script with arguments.

    Returns:
        Tuple of (return_code, parsed_json_output)
    """
    cmd = [sys.executable, str(SCRIPT_PATH)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        output = json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        output = {'raw_stdout': result.stdout, 'raw_stderr': result.stderr}
    return result.returncode, output


class TestDeletePlan(unittest.TestCase):
    """Test cases for delete-plan.py."""

    def setUp(self):
        """Create temporary directory structure for tests."""
        self.temp_dir = tempfile.mkdtemp()
        # Create .claude/plans/ structure
        self.plans_dir = Path(self.temp_dir) / '.claude' / 'plans'
        self.plans_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_plan(self, name: str, with_plan_md: bool = True) -> Path:
        """Create a test plan directory.

        Args:
            name: Plan name
            with_plan_md: Whether to create plan.md file

        Returns:
            Path to the plan directory
        """
        plan_dir = self.plans_dir / name
        plan_dir.mkdir(parents=True, exist_ok=True)

        if with_plan_md:
            plan_md = plan_dir / 'plan.md'
            plan_md.write_text(f'# Task Plan: {name}\n\n**Current Phase**: implement\n')

        # Add some extra files
        (plan_dir / 'config.md').write_text('# Configuration\n')
        subdir = plan_dir / 'references'
        subdir.mkdir()
        (subdir / 'notes.md').write_text('# Notes\n')

        return plan_dir

    def test_delete_valid_plan_dry_run(self):
        """Test dry-run mode doesn't delete files."""
        plan_dir = self.create_test_plan('test-plan')

        returncode, output = run_script(str(plan_dir), '--dry-run')

        self.assertEqual(returncode, 0)
        self.assertTrue(output['success'])
        self.assertTrue(output['dry_run'])
        self.assertEqual(output['plan_name'], 'test-plan')
        self.assertIn('would_delete', output)
        self.assertGreater(output['would_delete']['files'], 0)
        # Directory should still exist
        self.assertTrue(plan_dir.exists())

    def test_delete_valid_plan(self):
        """Test actual deletion of a valid plan."""
        plan_dir = self.create_test_plan('delete-me')

        # Verify it exists first
        self.assertTrue(plan_dir.exists())
        self.assertTrue((plan_dir / 'plan.md').exists())

        returncode, output = run_script(str(plan_dir))

        self.assertEqual(returncode, 0)
        self.assertTrue(output['success'])
        self.assertFalse(output.get('dry_run', False))
        self.assertEqual(output['plan_name'], 'delete-me')
        self.assertIn('deleted', output)
        # Directory should be gone
        self.assertFalse(plan_dir.exists())

    def test_delete_nonexistent_directory(self):
        """Test error when directory doesn't exist."""
        fake_path = self.plans_dir / 'nonexistent-plan'

        returncode, output = run_script(str(fake_path))

        self.assertEqual(returncode, 1)
        self.assertFalse(output['success'])
        self.assertEqual(output['error']['type'], 'validation_failed')
        self.assertIn('does not exist', output['error']['details'][0])

    def test_delete_directory_without_plan_md(self):
        """Test error when directory has no plan.md."""
        plan_dir = self.create_test_plan('no-plan-md', with_plan_md=False)

        returncode, output = run_script(str(plan_dir))

        self.assertEqual(returncode, 1)
        self.assertFalse(output['success'])
        self.assertEqual(output['error']['type'], 'validation_failed')
        self.assertIn('No plan.md found', output['error']['details'][0])
        # Directory should still exist
        self.assertTrue(plan_dir.exists())

    def test_delete_outside_plans_hierarchy(self):
        """Test error when path is outside .claude/plans/."""
        # Create a directory outside the plans hierarchy
        outside_dir = Path(self.temp_dir) / 'outside'
        outside_dir.mkdir()
        (outside_dir / 'plan.md').write_text('# Fake plan\n')

        returncode, output = run_script(str(outside_dir))

        self.assertEqual(returncode, 1)
        self.assertFalse(output['success'])
        self.assertEqual(output['error']['type'], 'validation_failed')
        self.assertIn('not within .claude/plans/', output['error']['details'][0])
        # Directory should still exist
        self.assertTrue(outside_dir.exists())

    def test_delete_file_instead_of_directory(self):
        """Test error when path is a file, not directory."""
        file_path = self.plans_dir / 'not-a-dir.txt'
        file_path.write_text('just a file')

        returncode, output = run_script(str(file_path))

        self.assertEqual(returncode, 1)
        self.assertFalse(output['success'])
        self.assertEqual(output['error']['type'], 'validation_failed')

    def test_output_contains_size_info(self):
        """Test that output includes human-readable size."""
        plan_dir = self.create_test_plan('sized-plan')

        returncode, output = run_script(str(plan_dir), '--dry-run')

        self.assertEqual(returncode, 0)
        self.assertIn('total_size_human', output['would_delete'])
        self.assertIn('message', output)

    def test_multiple_plans_independent(self):
        """Test deleting one plan doesn't affect others."""
        plan1 = self.create_test_plan('plan-one')
        plan2 = self.create_test_plan('plan-two')

        returncode, output = run_script(str(plan1))

        self.assertEqual(returncode, 0)
        self.assertFalse(plan1.exists())
        self.assertTrue(plan2.exists())  # Other plan untouched


class TestDeletePlanHelp(unittest.TestCase):
    """Test help and usage."""

    def test_help_flag(self):
        """Test --help flag works."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), '--help'],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('Delete a plan directory safely', result.stdout)
        self.assertIn('--dry-run', result.stdout)


if __name__ == '__main__':
    unittest.main()
