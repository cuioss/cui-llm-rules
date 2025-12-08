#!/usr/bin/env python3
"""
Tests for the permission.py consolidated script.

Tests all subcommands:
- generate-wildcards: Generate permission wildcards from marketplace inventory
- detect-redundant: Detect redundant permissions between global/local
- detect-suspicious: Detect suspicious permissions (security anti-patterns)
- consolidate: Consolidate timestamped build output permissions
- ensure-wildcards: Ensure marketplace wildcards exist in settings
- apply-fixes: Apply safe permission fixes (dedup, sort, defaults)
- apply: Apply permission changes to settings files
"""

import json
import sys
from pathlib import Path

# Add test root to path for conftest imports
TEST_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TEST_ROOT))

from conftest import (
    ScriptTestCase, TestRunner, run_script,
    MARKETPLACE_ROOT
)


# Script path to consolidated permission.py
SCRIPT_PATH = MARKETPLACE_ROOT / 'general-tools' / 'skills' / 'permission-management' / 'scripts' / 'permission.py'


# =============================================================================
# Tests for generate-wildcards subcommand
# =============================================================================

class TestGenerateWildcards(ScriptTestCase):
    """Test permission.py generate-wildcards subcommand."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'permission.py'

    def test_generates_skill_wildcards(self):
        """Should generate Skill() wildcards from inventory."""
        inventory = {
            "bundles": [
                {
                    "name": "builder",
                    "skills": [{"name": "builder-gradle-rules"}, {"name": "builder-maven-rules"}],
                    "commands": []
                }
            ]
        }

        result = run_script(
            SCRIPT_PATH,
            'generate-wildcards',
            input_data=json.dumps(inventory)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('permissions', data)
        self.assertIn('skill_wildcards', data['permissions'])
        self.assertIn('Skill(builder:*)', data['permissions']['skill_wildcards'])

    def test_generates_command_wildcards(self):
        """Should generate SlashCommand() wildcards from inventory."""
        inventory = {
            "bundles": [
                {
                    "name": "planning",
                    "skills": [],
                    "commands": [{"name": "plan-manage"}, {"name": "task-implement"}]
                }
            ]
        }

        result = run_script(
            SCRIPT_PATH,
            'generate-wildcards',
            input_data=json.dumps(inventory)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('permissions', data)
        self.assertIn('command_bundle_wildcards', data['permissions'])
        self.assertIn('SlashCommand(/planning:*)', data['permissions']['command_bundle_wildcards'])

    def test_includes_statistics(self):
        """Should include statistics in output."""
        inventory = {
            "bundles": [
                {
                    "name": "test-bundle",
                    "skills": [{"name": "skill1"}],
                    "commands": [{"name": "cmd1"}]
                }
            ]
        }

        result = run_script(
            SCRIPT_PATH,
            'generate-wildcards',
            input_data=json.dumps(inventory)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('statistics', data)
        self.assertIn('bundles_scanned', data['statistics'])


# =============================================================================
# Tests for detect-redundant subcommand
# =============================================================================

class TestDetectRedundant(ScriptTestCase):
    """Test permission.py detect-redundant subcommand."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'permission.py'

    def test_detect_exact_duplicate(self):
        """Should detect when same permission exists in both global and local."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Bash(npm:*)", "Read(//~/git/**)"],
                "deny": [],
                "ask": []
            }
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Edit(.plan/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'detect-redundant',
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('redundant', data)
        redundant_perms = [r['permission'] for r in data['redundant']]
        self.assertIn('Bash(git:*)', redundant_perms)
        self.assertNotIn('Edit(.plan/**)', redundant_perms)

    def test_detect_marketplace_in_local(self):
        """Should flag marketplace permissions in local as belonging in global."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {"allow": ["Skill(builder:*)"], "deny": [], "ask": []}
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Skill(cui-java-expert:*)", "Edit(.plan/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'detect-redundant',
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('marketplace_in_local', data)
        marketplace_perms = [m['permission'] for m in data['marketplace_in_local']]
        self.assertIn('Skill(cui-java-expert:*)', marketplace_perms)

    def test_output_includes_summary(self):
        """Output should include summary counts."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)", "Skill(builder:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            'detect-redundant',
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('summary', data)
        self.assertIn('redundant_count', data['summary'])
        self.assertIn('marketplace_in_local_count', data['summary'])


# =============================================================================
# Tests for detect-suspicious subcommand
# =============================================================================

class TestDetectSuspicious(ScriptTestCase):
    """Test permission.py detect-suspicious subcommand."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'permission.py'

    def test_detect_sudo_permission(self):
        """Should flag sudo permissions as suspicious."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(sudo:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'detect-suspicious',
            '--settings', str(settings_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('suspicious', data)
        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Bash(sudo:*)', suspicious_perms)

    def test_detect_system_path_access(self):
        """Should flag system path access as suspicious."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Write(/etc/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'detect-suspicious',
            '--settings', str(settings_file)
        )
        self.assert_success(result)
        data = result.json()

        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Write(/etc/**)', suspicious_perms)

    def test_output_includes_severity(self):
        """Suspicious permissions should include severity."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(rm:-rf:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'detect-suspicious',
            '--settings', str(settings_file)
        )
        self.assert_success(result)
        data = result.json()

        if data['suspicious']:
            for item in data['suspicious']:
                self.assertIn('severity', item)


# =============================================================================
# Tests for consolidate subcommand
# =============================================================================

class TestConsolidate(ScriptTestCase):
    """Test permission.py consolidate subcommand."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'permission.py'

    def test_detect_timestamped_build_output(self):
        """Should detect permissions with timestamp patterns."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Read(target/build-output-2025-11-20-174411.log)",
                    "Read(target/build-output-2025-11-21-093000.log)",
                    "Read(target/build-output-2025-11-22-120000.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'consolidate',
            '--settings', str(settings_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('consolidated', data)
        self.assertEqual(data['consolidated'], 3)

    def test_generates_correct_wildcard(self):
        """Should generate correct wildcard pattern."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(target/build-output-2025-11-20-174411.log)",
                    "Read(target/build-output-2025-11-21-093000.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'consolidate',
            '--settings', str(settings_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('wildcards_added', data)
        self.assertIn('Read(target/build-output-*.log)', data['wildcards_added'])

    def test_dry_run_does_not_modify_file(self):
        """Dry-run should not modify the settings file."""
        original_content = json.dumps({
            "permissions": {
                "allow": ["Read(target/build-output-2025-11-20-174411.log)"],
                "deny": [],
                "ask": []
            }
        })

        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(original_content)

        result = run_script(
            SCRIPT_PATH,
            'consolidate',
            '--settings', str(settings_file),
            '--dry-run'
        )
        self.assert_success(result)

        self.assertEqual(settings_file.read_text(), original_content)


# =============================================================================
# Tests for ensure-wildcards subcommand
# =============================================================================

class TestEnsureWildcards(ScriptTestCase):
    """Test permission.py ensure-wildcards subcommand."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'permission.py'

    def test_adds_missing_wildcards(self):
        """Should add missing marketplace wildcards."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)"],
                "deny": [],
                "ask": []
            }
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"path": "bundles/builder"},
                {"path": "bundles/planning"}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            'ensure-wildcards',
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('added', data)
        # Should suggest adding wildcards for bundles

    def test_reports_already_present(self):
        """Should report wildcards already present."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Skill(builder:*)", "SlashCommand(/builder:*)"],
                "deny": [],
                "ask": []
            }
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"path": "bundles/builder"}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            'ensure-wildcards',
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('already_present', data)


# =============================================================================
# Tests for apply-fixes subcommand
# =============================================================================

class TestApplyFixes(ScriptTestCase):
    """Test permission.py apply-fixes subcommand."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'permission.py'

    def test_removes_duplicates(self):
        """Should remove duplicate permissions."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Bash(git:*)", "Bash(npm:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'apply-fixes',
            '--settings', str(settings_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('duplicates_removed', data)
        self.assertEqual(data['duplicates_removed'], 1)

    def test_sorts_permissions(self):
        """Should sort permissions alphabetically."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Write(**)", "Bash(git:*)", "Edit(**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'apply-fixes',
            '--settings', str(settings_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('sorted', data)
        self.assertTrue(data['sorted'])


# =============================================================================
# Tests for apply subcommand
# =============================================================================

class TestApply(ScriptTestCase):
    """Test permission.py apply subcommand."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'permission.py'

    def test_add_permission(self):
        """Should add a new permission."""
        # Create .claude/settings.json in temp directory
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'apply',
            '--action', 'add',
            '--permission', 'Bash(npm:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)

        settings = json.loads(settings_file.read_text())
        self.assertIn('Bash(npm:*)', settings['permissions']['allow'])

    def test_remove_permission(self):
        """Should remove an existing permission."""
        # Create .claude/settings.json in temp directory
        claude_dir = self.temp_dir / '.claude'
        claude_dir.mkdir()
        settings_file = claude_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Bash(npm:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            'apply',
            '--action', 'remove',
            '--permission', 'Bash(npm:*)',
            '--target', 'project',
            cwd=self.temp_dir
        )
        self.assert_success(result)

        settings = json.loads(settings_file.read_text())
        self.assertNotIn('Bash(npm:*)', settings['permissions']['allow'])
        self.assertIn('Bash(git:*)', settings['permissions']['allow'])


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


def test_generate_wildcards_help():
    """generate-wildcards subcommand should have help."""
    result = run_script(SCRIPT_PATH, 'generate-wildcards', '--help')
    assert result.returncode == 0


def test_detect_redundant_help():
    """detect-redundant subcommand should have help."""
    result = run_script(SCRIPT_PATH, 'detect-redundant', '--help')
    assert result.returncode == 0


def test_detect_suspicious_help():
    """detect-suspicious subcommand should have help."""
    result = run_script(SCRIPT_PATH, 'detect-suspicious', '--help')
    assert result.returncode == 0


def test_consolidate_help():
    """consolidate subcommand should have help."""
    result = run_script(SCRIPT_PATH, 'consolidate', '--help')
    assert result.returncode == 0


def test_ensure_wildcards_help():
    """ensure-wildcards subcommand should have help."""
    result = run_script(SCRIPT_PATH, 'ensure-wildcards', '--help')
    assert result.returncode == 0


def test_apply_fixes_help():
    """apply-fixes subcommand should have help."""
    result = run_script(SCRIPT_PATH, 'apply-fixes', '--help')
    assert result.returncode == 0


def test_apply_help():
    """apply subcommand should have help."""
    result = run_script(SCRIPT_PATH, 'apply', '--help')
    assert result.returncode == 0


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    import unittest

    # Check if script exists first
    if not SCRIPT_PATH.exists():
        print(f"ERROR: Script not found: {SCRIPT_PATH}")
        sys.exit(1)

    # Run unittest-based tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestGenerateWildcards))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectRedundant))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectSuspicious))
    suite.addTests(loader.loadTestsFromTestCase(TestConsolidate))
    suite.addTests(loader.loadTestsFromTestCase(TestEnsureWildcards))
    suite.addTests(loader.loadTestsFromTestCase(TestApplyFixes))
    suite.addTests(loader.loadTestsFromTestCase(TestApply))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Also run simple function tests
    print("\n" + "=" * 50)
    print("Running simple function tests...")
    print("=" * 50)

    simple_tests = [
        test_script_exists,
        test_help_works,
        test_generate_wildcards_help,
        test_detect_redundant_help,
        test_detect_suspicious_help,
        test_consolidate_help,
        test_ensure_wildcards_help,
        test_apply_fixes_help,
        test_apply_help,
    ]

    simple_runner = TestRunner()
    simple_runner.add_tests(simple_tests)
    simple_result = simple_runner.run()

    # Exit with combined result
    sys.exit(0 if result.wasSuccessful() and simple_result == 0 else 1)
