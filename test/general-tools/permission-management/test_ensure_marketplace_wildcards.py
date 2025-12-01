#!/usr/bin/env python3
"""
Tests for the ensure-marketplace-wildcards.py script.

TDD: Tests written FIRST before implementation.

Tests cover:
- Detection of missing bundle wildcards
- Addition of Skill() wildcards
- Addition of SlashCommand() wildcards
- Idempotency (no duplicates)
- Reading from marketplace.json
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
SCRIPT_PATH = MARKETPLACE_ROOT / 'general-tools' / 'skills' / 'permission-management' / 'scripts' / 'ensure-marketplace-wildcards.py'


class TestDetectMissingWildcards(ScriptTestCase):
    """Test detection of missing marketplace wildcards."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'ensure-marketplace-wildcards.py'

    def test_detect_missing_skill_wildcard(self):
        """Should detect when Skill() wildcard is missing for a bundle."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Skill(builder:*)"],  # Has builder, missing others
                "deny": [],
                "ask": []
            }
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"name": "builder", "skills": ["env-detection"]},
                {"name": "cui-java-expert", "skills": ["java-core"]}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('added', data)
        self.assertIn('Skill(cui-java-expert:*)', data['added'])
        self.assertNotIn('Skill(builder:*)', data['added'])  # Already present

    def test_detect_missing_slashcommand_wildcard(self):
        """Should detect when SlashCommand() wildcard is missing."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Skill(builder:*)"],  # Has skill but not command
                "deny": [],
                "ask": []
            }
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"name": "builder", "skills": ["env-detection"], "commands": ["builder-build-and-fix"]}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('SlashCommand(/builder:*)', data['added'])


class TestAddWildcards(ScriptTestCase):
    """Test addition of marketplace wildcards."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'ensure-marketplace-wildcards.py'

    def test_adds_skill_wildcards(self):
        """Should add Skill() wildcards for bundles with skills."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"name": "builder", "skills": ["env-detection", "maven-rules"]},
                {"name": "planning", "skills": ["plan-files", "phase-management"]}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file)
        )
        self.assert_success(result)

        # Verify settings file was updated
        settings = json.loads(settings_file.read_text())
        allow_list = settings['permissions']['allow']

        self.assertIn('Skill(builder:*)', allow_list)
        self.assertIn('Skill(planning:*)', allow_list)

    def test_adds_slashcommand_wildcards(self):
        """Should add SlashCommand() wildcards for bundles with commands."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"name": "builder", "commands": ["builder-build-and-fix"]},
                {"name": "planning", "commands": ["plan-manage", "plan-execute"]}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file)
        )
        self.assert_success(result)

        settings = json.loads(settings_file.read_text())
        allow_list = settings['permissions']['allow']

        self.assertIn('SlashCommand(/builder:*)', allow_list)
        self.assertIn('SlashCommand(/planning:*)', allow_list)


class TestIdempotency(ScriptTestCase):
    """Test that running twice doesn't create duplicates."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'ensure-marketplace-wildcards.py'

    def test_no_duplicates_on_second_run(self):
        """Should not add duplicates when wildcards already exist."""
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
                {"name": "builder", "skills": ["env-detection"], "commands": ["builder-build-and-fix"]}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file)
        )
        self.assert_success(result)
        data = result.json()

        # Should report already present, not added
        self.assertEqual(data['already_present'], 2)
        self.assertEqual(len(data['added']), 0)

        # Verify no duplicates in file
        settings = json.loads(settings_file.read_text())
        allow_list = settings['permissions']['allow']
        self.assertEqual(allow_list.count('Skill(builder:*)'), 1)


class TestDryRunMode(ScriptTestCase):
    """Test dry-run mode doesn't modify files."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'ensure-marketplace-wildcards.py'

    def test_dry_run_does_not_modify(self):
        """Dry-run should report changes but not apply them."""
        original_content = json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        })

        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(original_content)

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [{"name": "builder", "skills": ["env-detection"]}]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        # Should report what would be added
        self.assertIn('Skill(builder:*)', data['added'])

        # File should be unchanged
        self.assertEqual(settings_file.read_text(), original_content)


class TestBundlesWithoutSkillsOrCommands(ScriptTestCase):
    """Test handling of bundles that don't have skills or commands."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'ensure-marketplace-wildcards.py'

    def test_skip_bundle_without_skills(self):
        """Should not add Skill() for bundles without skills."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"name": "empty-bundle", "skills": [], "commands": ["some-command"]}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        # Should not add skill wildcard for bundle without skills
        added_skills = [a for a in data['added'] if a.startswith('Skill(')]
        self.assertEqual(len(added_skills), 0)

        # Should still add command wildcard
        self.assertIn('SlashCommand(/empty-bundle:*)', data['added'])


class TestOutputFormat(ScriptTestCase):
    """Test the output format and structure."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'ensure-marketplace-wildcards.py'

    def test_output_includes_totals(self):
        """Output should include total counts."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Skill(builder:*)"], "deny": [], "ask": []}
        }))

        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "bundles": [
                {"name": "builder", "skills": ["env-detection"]},
                {"name": "planning", "skills": ["plan-files"]}
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('already_present', data)
        self.assertIn('total', data)


class TestMarketplaceJsonFormats(ScriptTestCase):
    """Test handling of different marketplace.json formats."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'ensure-marketplace-wildcards.py'

    def test_handles_real_marketplace_format(self):
        """Should handle the actual marketplace.json format."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        # More realistic marketplace.json format
        marketplace_file = self.temp_dir / 'marketplace.json'
        marketplace_file.write_text(json.dumps({
            "version": "1.0",
            "marketplace": "cui-development-standards",
            "bundles": [
                {
                    "name": "builder",
                    "description": "Build tools",
                    "skills": [
                        {"name": "builder-maven-rules"},
                        {"name": "environment-detection"}
                    ],
                    "commands": [
                        {"name": "builder-build-and-fix"}
                    ]
                }
            ]
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--marketplace-json', str(marketplace_file),
            '--dry-run'
        )
        self.assert_success(result)
        data = result.json()

        # Should extract bundle names correctly
        self.assertIn('Skill(builder:*)', data['added'])


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

    suite.addTests(loader.loadTestsFromTestCase(TestDetectMissingWildcards))
    suite.addTests(loader.loadTestsFromTestCase(TestAddWildcards))
    suite.addTests(loader.loadTestsFromTestCase(TestIdempotency))
    suite.addTests(loader.loadTestsFromTestCase(TestDryRunMode))
    suite.addTests(loader.loadTestsFromTestCase(TestBundlesWithoutSkillsOrCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketplaceJsonFormats))

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
