#!/usr/bin/env python3
"""
Tests for the determine-mode.py script.

Tests the operational mode determination:
- wizard mode: When executor or marshal.json is missing
- menu mode: When both executor and marshal.json exist
"""

import sys
from pathlib import Path

# Add test root to path for conftest imports
TEST_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TEST_ROOT))

from conftest import ScriptTestCase, run_script, MARKETPLACE_ROOT


# Script path to determine-mode.py
SCRIPT_PATH = MARKETPLACE_ROOT / 'plan-marshall' / 'skills' / 'plan-marshall' / 'scripts' / 'determine-mode.py'


class TestDetermineMode(ScriptTestCase):
    """Test determine-mode.py operational mode detection."""

    bundle = 'plan-marshall'
    skill = 'plan-marshall'
    script = 'determine-mode.py'

    def test_wizard_mode_when_executor_missing(self):
        """Should return wizard mode when executor is missing."""
        plan_dir = self.temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        # Create marshal.json but not executor
        (plan_dir / 'marshal.json').write_text('{}')

        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir))

        self.assert_success(result)
        self.assertIn('mode\twizard', result.stdout)
        self.assertIn('reason\texecutor_missing', result.stdout)

    def test_wizard_mode_when_marshal_missing(self):
        """Should return wizard mode when marshal.json is missing."""
        plan_dir = self.temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        # Create executor but not marshal.json
        (plan_dir / 'execute-script.py').write_text('# executor script')

        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir))

        self.assert_success(result)
        self.assertIn('mode\twizard', result.stdout)
        self.assertIn('reason\tmarshal_missing', result.stdout)

    def test_wizard_mode_when_both_missing(self):
        """Should return wizard mode when both are missing."""
        plan_dir = self.temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        # Neither executor nor marshal.json exists

        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir))

        self.assert_success(result)
        self.assertIn('mode\twizard', result.stdout)
        self.assertIn('reason\texecutor_missing', result.stdout)

    def test_menu_mode_when_both_exist(self):
        """Should return menu mode when both exist."""
        plan_dir = self.temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        # Create both executor and marshal.json
        (plan_dir / 'execute-script.py').write_text('# executor script')
        (plan_dir / 'marshal.json').write_text('{}')

        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir))

        self.assert_success(result)
        self.assertIn('mode\tmenu', result.stdout)
        self.assertIn('reason\tboth_exist', result.stdout)

    def test_default_plan_dir(self):
        """Should use .plan as default directory."""
        # Run from temp dir where .plan doesn't exist
        result = run_script(SCRIPT_PATH, cwd=self.temp_dir)

        self.assert_success(result)
        self.assertIn('mode\twizard', result.stdout)

    def test_nonexistent_plan_dir(self):
        """Should return wizard mode for non-existent plan directory."""
        nonexistent_dir = self.temp_dir / 'nonexistent'

        result = run_script(SCRIPT_PATH, '--plan-dir', str(nonexistent_dir))

        self.assert_success(result)
        self.assertIn('mode\twizard', result.stdout)
        self.assertIn('reason\texecutor_missing', result.stdout)

    def test_toon_output_format(self):
        """Output should be valid TOON format (tab-separated key-value pairs)."""
        plan_dir = self.temp_dir / '.plan'
        plan_dir.mkdir(parents=True)

        result = run_script(SCRIPT_PATH, '--plan-dir', str(plan_dir))

        self.assert_success(result)

        lines = result.stdout.strip().split('\n')
        self.assertEqual(len(lines), 2)

        # Each line should be tab-separated key-value
        for line in lines:
            parts = line.split('\t')
            self.assertEqual(len(parts), 2, f"Line should have exactly 2 parts: {line}")


if __name__ == '__main__':
    import unittest
    unittest.main()
