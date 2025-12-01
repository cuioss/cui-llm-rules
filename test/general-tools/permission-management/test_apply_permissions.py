#!/usr/bin/env python3
"""
Tests for the apply-permissions.py script.

Tests cover:
- Settings file discovery (settings.json vs settings.local.json)
- Permission add/remove/ensure operations
- Script permission sync from scripts.local.json
- Global vs project target handling
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
    create_temp_dir, create_temp_file
)


SCRIPT_PATH = get_script_path('general-tools', 'permission-management', 'apply-permissions.py')


class TestAnalyzeSettings(ScriptTestCase):
    """Test the analyze action."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permissions.py'

    def test_analyze_with_no_project_settings(self):
        """Analyze should report when no project settings exist."""
        # Run from a temp directory with no .claude folder
        result = run_script(SCRIPT_PATH, '--action', 'analyze', cwd=self.temp_dir)
        self.assert_success(result)
        data = result.json()

        self.assertIn('global', data)
        self.assertIn('project', data)
        self.assertIsNone(data['project']['path'])
        self.assertFalse(data['project']['exists'])

    def test_analyze_with_settings_json(self):
        """Analyze should find .claude/settings.json (version-controlled)."""
        # Create .claude/settings.json
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        result = run_script(SCRIPT_PATH, '--action', 'analyze', cwd=self.temp_dir)
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['project']['exists'])
        self.assertEqual(data['project']['type'], 'version-controlled')
        self.assertEqual(data['project']['permissions']['allow_count'], 1)

    def test_analyze_with_settings_local_json(self):
        """Analyze should find .claude/settings.local.json when settings.json doesn't exist."""
        # Create .claude/settings.local.json only
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.local.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(npm:*)", "Edit(//test/**)"], "deny": [], "ask": []}
        }))

        result = run_script(SCRIPT_PATH, '--action', 'analyze', cwd=self.temp_dir)
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['project']['exists'])
        self.assertEqual(data['project']['type'], 'local')
        self.assertEqual(data['project']['permissions']['allow_count'], 2)

    def test_analyze_prefers_settings_json_over_local(self):
        """When both exist, analyze should prefer settings.json."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()

        # Create both files with different content
        settings_json = claude_dir / 'settings.json'
        settings_json.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        settings_local = claude_dir / 'settings.local.json'
        settings_local.write_text(json.dumps({
            "permissions": {"allow": ["Bash(npm:*)", "Bash(docker:*)"], "deny": [], "ask": []}
        }))

        result = run_script(SCRIPT_PATH, '--action', 'analyze', cwd=self.temp_dir)
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['project']['exists'])
        self.assertEqual(data['project']['type'], 'version-controlled')
        # Should report settings.json count (1), not settings.local.json count (2)
        self.assertEqual(data['project']['permissions']['allow_count'], 1)


class TestAddPermission(ScriptTestCase):
    """Test the add action."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permissions.py'

    def test_add_to_new_project_settings(self):
        """Add should create settings.local.json if neither file exists."""
        result = run_script(
            SCRIPT_PATH,
            '--action', 'add',
            '--permission', 'Bash(test:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'added')

        # Should have created settings.local.json
        settings_file = self.temp_dir / '.claude' / 'settings.local.json'
        self.assertTrue(settings_file.exists())

        settings = json.loads(settings_file.read_text())
        self.assertIn('Bash(test:*)', settings['permissions']['allow'])

    def test_add_to_existing_settings_json(self):
        """Add should update existing settings.json."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'add',
            '--permission', 'Bash(npm:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'added')

        # Should have added to settings.json (not created settings.local.json)
        settings = json.loads(settings_file.read_text())
        self.assertIn('Bash(git:*)', settings['permissions']['allow'])
        self.assertIn('Bash(npm:*)', settings['permissions']['allow'])

    def test_add_duplicate_permission(self):
        """Add should report already_exists for duplicates."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'add',
            '--permission', 'Bash(git:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'already_exists')


class TestRemovePermission(ScriptTestCase):
    """Test the remove action."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permissions.py'

    def test_remove_existing_permission(self):
        """Remove should delete existing permission."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)", "Bash(npm:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'remove',
            '--permission', 'Bash(npm:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'removed')

        settings = json.loads(settings_file.read_text())
        self.assertIn('Bash(git:*)', settings['permissions']['allow'])
        self.assertNotIn('Bash(npm:*)', settings['permissions']['allow'])

    def test_remove_nonexistent_permission(self):
        """Remove should report not_found for missing permission."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'remove',
            '--permission', 'Bash(docker:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'not_found')


class TestEnsurePermissions(ScriptTestCase):
    """Test the ensure action."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permissions.py'

    def test_ensure_adds_missing_permissions(self):
        """Ensure should add missing permissions."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'ensure',
            '--permissions', 'Bash(git:*),Bash(npm:*),Bash(docker:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['added_count'], 2)
        self.assertIn('Bash(npm:*)', data['added'])
        self.assertIn('Bash(docker:*)', data['added'])
        self.assertIn('Bash(git:*)', data['already_exists'])


class TestSyncScriptPermissions(ScriptTestCase):
    """Test the sync-scripts action."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permissions.py'

    def test_sync_adds_script_permissions(self):
        """Sync should add permissions from scripts.local.json."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()

        # Create scripts.local.json with new wildcard format (scripts/*:*)
        scripts_file = claude_dir / 'scripts.local.json'
        scripts_file.write_text(json.dumps({
            "version": 1,
            "marketplace": "test-marketplace",
            "scripts": {},
            "permissions": [
                "Bash(python3 /path/to/scripts/*:*)",
                "Bash(bash /path/to/scripts/*:*)"
            ]
        }))

        # Create empty project settings
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'sync-scripts',
            '--scripts-file', str(scripts_file),
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['added'], 2)

        settings = json.loads(settings_file.read_text())
        self.assertEqual(len(settings['permissions']['allow']), 2)

    def test_sync_replaces_old_marketplace_permissions(self):
        """Sync should remove old marketplace script permissions before adding new."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()

        # Create scripts.local.json with new wildcard format (scripts/*:*)
        scripts_file = claude_dir / 'scripts.local.json'
        scripts_file.write_text(json.dumps({
            "version": 1,
            "marketplace": "test-marketplace",
            "scripts": {},
            "permissions": [
                "Bash(python3 /new/path/marketplace/bundles/test/scripts/*:*)"
            ]
        }))

        # Create project settings with old marketplace permissions (mixed legacy formats)
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Bash(python3 /old/path/marketplace/bundles/test/scripts/*.py:*)",
                    "Bash(bash /old/path/marketplace/bundles/test/scripts/*.sh:*)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'sync-scripts',
            '--scripts-file', str(scripts_file),
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['removed'], 2)
        self.assertEqual(data['added'], 1)

        settings = json.loads(settings_file.read_text())
        # Should have git:* and the new script permission
        self.assertEqual(len(settings['permissions']['allow']), 2)
        self.assertIn('Bash(git:*)', settings['permissions']['allow'])

    def test_sync_removes_current_wildcard_format(self):
        """Sync should remove old permissions using current scripts/*:* format."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()

        # Create scripts.local.json with updated permissions
        scripts_file = claude_dir / 'scripts.local.json'
        scripts_file.write_text(json.dumps({
            "version": 1,
            "marketplace": "test-marketplace",
            "scripts": {},
            "permissions": [
                "Bash(python3 /updated/marketplace/bundles/skill-a/scripts/*:*)"
            ]
        }))

        # Create project settings with old permissions using scripts/*:* format
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Bash(python3 /old/marketplace/bundles/skill-a/scripts/*:*)",
                    "Bash(bash /old/marketplace/bundles/skill-b/scripts/*:*)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'sync-scripts',
            '--scripts-file', str(scripts_file),
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['removed'], 2)  # Both old scripts/*:* permissions removed
        self.assertEqual(data['added'], 1)

        settings = json.loads(settings_file.read_text())
        # Should have git:* and the new script permission
        self.assertEqual(len(settings['permissions']['allow']), 2)
        self.assertIn('Bash(git:*)', settings['permissions']['allow'])
        self.assertIn('Bash(python3 /updated/marketplace/bundles/skill-a/scripts/*:*)', settings['permissions']['allow'])


class TestSettingsFilePriority(ScriptTestCase):
    """Test that settings.json is preferred over settings.local.json for writes."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'apply-permissions.py'

    def test_add_writes_to_settings_json_when_exists(self):
        """When settings.json exists, add should write to it."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()

        settings_json = claude_dir / 'settings.json'
        settings_json.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        settings_local = claude_dir / 'settings.local.json'
        settings_local.write_text(json.dumps({
            "permissions": {"allow": ["Bash(npm:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'add',
            '--permission', 'Bash(test:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)

        # Should have written to settings.json
        settings = json.loads(settings_json.read_text())
        self.assertIn('Bash(test:*)', settings['permissions']['allow'])

        # settings.local.json should be unchanged
        local_settings = json.loads(settings_local.read_text())
        self.assertNotIn('Bash(test:*)', local_settings['permissions']['allow'])

    def test_add_writes_to_settings_local_when_no_settings_json(self):
        """When only settings.local.json exists, add should write to it."""
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()

        settings_local = claude_dir / 'settings.local.json'
        settings_local.write_text(json.dumps({
            "permissions": {"allow": ["Bash(npm:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--action', 'add',
            '--permission', 'Bash(test:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)

        # Should have written to settings.local.json
        settings = json.loads(settings_local.read_text())
        self.assertIn('Bash(test:*)', settings['permissions']['allow'])
        self.assertIn('Bash(npm:*)', settings['permissions']['allow'])

        # settings.json should not exist
        self.assertFalse((claude_dir / 'settings.json').exists())


# =============================================================================
# Simple function-based tests for quick validation
# =============================================================================

def test_script_exists():
    """Verify the script exists."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"


def test_help_works():
    """Script should respond to --help."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0


def test_analyze_returns_json():
    """Analyze action should return valid JSON."""
    temp_dir = create_temp_dir()
    try:
        result = run_script(SCRIPT_PATH, '--action', 'analyze', cwd=temp_dir)
        assert result.success
        data = result.json()
        assert 'global' in data
        assert 'project' in data
    finally:
        shutil.rmtree(temp_dir)


def test_add_requires_permission_arg():
    """Add action should fail without --permission."""
    result = run_script(SCRIPT_PATH, '--action', 'add')
    assert result.success  # Returns JSON with error
    data = result.json()
    assert 'error' in data


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    import unittest

    # Run unittest-based tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAnalyzeSettings))
    suite.addTests(loader.loadTestsFromTestCase(TestAddPermission))
    suite.addTests(loader.loadTestsFromTestCase(TestRemovePermission))
    suite.addTests(loader.loadTestsFromTestCase(TestEnsurePermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestSyncScriptPermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsFilePriority))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Also run simple function tests
    print("\n" + "=" * 50)
    print("Running simple function tests...")
    print("=" * 50)

    simple_tests = [
        test_script_exists,
        test_help_works,
        test_analyze_returns_json,
        test_add_requires_permission_arg,
    ]

    simple_runner = TestRunner()
    simple_runner.add_tests(simple_tests)
    simple_result = simple_runner.run()

    # Exit with combined result
    sys.exit(0 if result.wasSuccessful() and simple_result == 0 else 1)
