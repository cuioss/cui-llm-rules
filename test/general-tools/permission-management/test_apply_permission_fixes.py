#!/usr/bin/env python3
"""
Tests for the apply-permission-fixes.py script.

TDD: Tests written FIRST before implementation.

Tests cover:
- Removal of duplicate permissions
- Path format normalization
- Sorting of permission lists
- Addition of default project permissions
- Dry-run mode
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Add test root to path for conftest imports
TEST_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TEST_ROOT))

from conftest import (
    ScriptTestCase, TestRunner, run_script, get_script_path,
    create_temp_dir, create_temp_file, MARKETPLACE_ROOT
)


# Script path - will fail until script is created
SCRIPT_PATH = MARKETPLACE_ROOT / 'general-tools' / 'skills' / 'permission-management' / 'scripts' / 'apply-permission-fixes.py'


class TestRemoveDuplicates(ScriptTestCase):
    """Test removal of duplicate permissions."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_remove_exact_duplicates(self):
        """Should remove exact duplicate permissions."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Bash(npm:*)",
                    "Bash(git:*)",  # Duplicate
                    "Bash(npm:*)"   # Duplicate
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        self.assertEqual(data['duplicates_removed'], 2)

        # Verify file was updated
        settings = json.loads(settings_file.read_text())
        allow_list = settings['permissions']['allow']
        # 2 original + 2 defaults (Edit(.plan/**), Write(.plan/**))
        self.assertEqual(len(allow_list), 4)
        self.assertEqual(allow_list.count('Bash(git:*)'), 1)
        self.assertEqual(allow_list.count('Bash(npm:*)'), 1)

    def test_remove_duplicates_across_lists(self):
        """Should handle duplicates that appear in allow and ask."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Bash(git:*)"],
                "deny": ["Write(/tmp/**)", "Write(/tmp/**)"],
                "ask": ["Bash(sudo:*)", "Bash(sudo:*)"]
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        self.assertEqual(data['duplicates_removed'], 3)


class TestPathNormalization(ScriptTestCase):
    """Test normalization of path formats."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_normalize_double_slash_paths(self):
        """Should normalize //~ paths to proper format."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(//~/git/project/**)",  # Correct format
                    "Read(/Users/test/git/**)"   # Absolute path that could be normalized
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        # Should report paths that were examined
        self.assertIn('paths_fixed', data)

    def test_remove_trailing_slashes(self):
        """Should normalize permissions with inconsistent trailing slashes."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(.plan/)",   # Has trailing slash
                    "Write(.plan)"    # No trailing slash
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)

        # Verify normalization
        settings = json.loads(settings_file.read_text())
        # Paths should be consistent (either all with or all without trailing slash)


class TestSorting(ScriptTestCase):
    """Test sorting of permission lists."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_sorts_allow_list(self):
        """Should sort permissions alphabetically."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Write(.plan/**)",
                    "Bash(git:*)",
                    "Edit(.plan/**)",
                    "Bash(npm:*)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['sorted'])

        settings = json.loads(settings_file.read_text())
        allow_list = settings['permissions']['allow']
        self.assertEqual(allow_list, sorted(allow_list))


class TestDefaultPermissions(ScriptTestCase):
    """Test addition of default project permissions."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_add_plan_permissions(self):
        """Should add default .plan permissions if missing."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        self.assertIn('defaults_added', data)

        settings = json.loads(settings_file.read_text())
        allow_list = settings['permissions']['allow']

        # Should have added plan permissions
        self.assertIn('Edit(.plan/**)', allow_list)
        self.assertIn('Write(.plan/**)', allow_list)

    def test_no_duplicate_defaults(self):
        """Should not add defaults that already exist."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Edit(.plan/**)", "Write(.plan/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        # Should not have added any defaults
        self.assertEqual(len(data.get('defaults_added', [])), 0)


class TestDryRunMode(ScriptTestCase):
    """Test dry-run mode doesn't modify files."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_dry_run_reports_changes(self):
        """Dry-run should report what would change but not modify."""
        original_content = json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Bash(git:*)"],
                "deny": [],
                "ask": []
            }
        })

        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(original_content)

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        # Should report changes
        self.assertEqual(data['duplicates_removed'], 1)

        # File should be unchanged
        self.assertEqual(settings_file.read_text(), original_content)


class TestNoChangesNeeded(ScriptTestCase):
    """Test behavior when no changes are needed."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_reports_no_changes(self):
        """Should report no changes when settings are already clean."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Edit(.plan/**)",
                    "Write(.plan/**)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        self.assertEqual(data['duplicates_removed'], 0)
        self.assertFalse(data['changes_made'])


class TestOutputFormat(ScriptTestCase):
    """Test the output format and structure."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_output_includes_all_fields(self):
        """Output should include all expected fields."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Bash(git:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        # Should have all expected fields
        self.assertIn('duplicates_removed', data)
        self.assertIn('paths_fixed', data)
        self.assertIn('defaults_added', data)
        self.assertIn('sorted', data)
        self.assertIn('changes_made', data)


class TestErrorHandling(ScriptTestCase):
    """Test error handling."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permission-fixes.py'

    def test_handles_missing_file(self):
        """Should handle missing settings file gracefully."""
        result = run_script(SCRIPT_PATH, '--settings', '/nonexistent/settings.json')
        data = result.json()
        self.assertIn('error', data)

    def test_handles_invalid_json(self):
        """Should handle invalid JSON gracefully."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text("{ invalid }")

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        data = result.json()
        self.assertIn('error', data)

    def test_handles_missing_permissions_key(self):
        """Should handle settings without permissions key."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({"other": "data"}))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)

        # Should create permissions structure
        settings = json.loads(settings_file.read_text())
        self.assertIn('permissions', settings)


# =============================================================================
# Simple function-based tests for quick validation
# =============================================================================

def test_script_exists():
    """Verify the script exists (will fail until implemented)."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"


def test_help_works():
    """Script should respond to --help."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    import unittest

    # Check if script exists first
    if not SCRIPT_PATH.exists():
        print(f"ERROR: Script not yet implemented: {SCRIPT_PATH}")
        print("TDD: Implement the script to make these tests pass.")
        sys.exit(1)

    # Run unittest-based tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestRemoveDuplicates))
    suite.addTests(loader.loadTestsFromTestCase(TestPathNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestSorting))
    suite.addTests(loader.loadTestsFromTestCase(TestDefaultPermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestDryRunMode))
    suite.addTests(loader.loadTestsFromTestCase(TestNoChangesNeeded))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Also run simple function tests
    print("\n" + "=" * 50)
    print("Running simple function tests...")
    print("=" * 50)

    simple_tests = [
        test_script_exists,
        test_help_works,
    ]

    simple_runner = TestRunner()
    simple_runner.add_tests(simple_tests)
    simple_result = simple_runner.run()

    # Exit with combined result
    sys.exit(0 if result.wasSuccessful() and simple_result == 0 else 1)
