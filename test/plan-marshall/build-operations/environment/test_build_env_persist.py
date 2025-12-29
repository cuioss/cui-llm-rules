#!/usr/bin/env python3
"""Tests for build-env.py persist and detect-modules subcommands.

Tests command generation and persistence to marshal.json.
"""

import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'extension-api', 'build_env.py')


# =============================================================================
# Test Helpers
# =============================================================================

class PersistTestContext:
    """Context manager for persist tests that need temporary project fixtures."""

    def __init__(self, build_system='maven', with_modules=False):
        self.temp_dir = None
        self.build_system = build_system
        self.with_modules = with_modules

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self._setup_project()
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _setup_project(self):
        """Create test project with build files."""
        # Create .plan directory with initial marshal.json
        plan_dir = self.temp_dir / '.plan'
        plan_dir.mkdir()

        # Create initial marshal.json (required by plan-marshall-config)
        # Uses module_config for command configuration (new architecture)
        (plan_dir / 'marshal.json').write_text(json.dumps({
            "skill_domains": {"system": {}},
            "module_config": {},
            "system": {"retention": {}},
            "plan": {"defaults": {}}
        }, indent=2))

        if self.build_system == 'maven':
            self._create_maven_project()
        elif self.build_system == 'gradle':
            self._create_gradle_project()
        elif self.build_system == 'npm':
            self._create_npm_project()
        elif self.build_system == 'mixed':
            self._create_maven_project()
            self._create_npm_project()

    def _create_maven_project(self):
        """Create Maven project structure."""
        if self.with_modules:
            pom_content = '''<project>
                <modules>
                    <module>core</module>
                    <module>api</module>
                </modules>
            </project>'''
            (self.temp_dir / 'pom.xml').write_text(pom_content)
            (self.temp_dir / 'core').mkdir()
            (self.temp_dir / 'core' / 'pom.xml').write_text('<project></project>')
            (self.temp_dir / 'api').mkdir()
            (self.temp_dir / 'api' / 'pom.xml').write_text('<project></project>')
        else:
            (self.temp_dir / 'pom.xml').write_text('<project></project>')

    def _create_gradle_project(self):
        """Create Gradle project structure."""
        if self.with_modules:
            (self.temp_dir / 'settings.gradle.kts').write_text('''
                rootProject.name = "test"
                include(":core")
                include(":api")
            ''')
            (self.temp_dir / 'core').mkdir()
            (self.temp_dir / 'core' / 'build.gradle.kts').write_text('plugins { java }')
            (self.temp_dir / 'api').mkdir()
            (self.temp_dir / 'api' / 'build.gradle.kts').write_text('plugins { java }')
        else:
            (self.temp_dir / 'build.gradle.kts').write_text('plugins { java }')

    def _create_npm_project(self):
        """Create npm project structure."""
        if self.with_modules:
            (self.temp_dir / 'package.json').write_text(json.dumps({
                "name": "test",
                "workspaces": ["packages/*"]
            }))
            packages_dir = self.temp_dir / 'packages'
            packages_dir.mkdir()
            (packages_dir / 'ui').mkdir()
            (packages_dir / 'ui' / 'package.json').write_text('{"name": "ui"}')
            (packages_dir / 'lib').mkdir()
            (packages_dir / 'lib' / 'package.json').write_text('{"name": "lib"}')
        else:
            (self.temp_dir / 'package.json').write_text('{"name": "test", "version": "1.0.0"}')


# =============================================================================
# detect-modules Tests
# =============================================================================

def test_detect_modules_maven():
    """Test Maven module detection."""
    with PersistTestContext('maven', with_modules=True) as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'detect-modules',
            '--project-dir', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', "Should succeed"
        assert data['count'] == 2, f"Should detect 2 modules, got {data['count']}"
        module_names = [m['name'] for m in data['modules']]
        assert 'core' in module_names, "Should detect core module"
        assert 'api' in module_names, "Should detect api module"


def test_detect_modules_gradle():
    """Test Gradle module detection."""
    with PersistTestContext('gradle', with_modules=True) as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'detect-modules',
            '--project-dir', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', "Should succeed"
        assert data['count'] == 2, f"Should detect 2 modules, got {data['count']}"


def test_detect_modules_npm_workspaces():
    """Test npm workspace detection."""
    with PersistTestContext('npm', with_modules=True) as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'detect-modules',
            '--project-dir', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', "Should succeed"
        assert data['count'] == 2, f"Should detect 2 workspaces, got {data['count']}"


def test_detect_modules_none():
    """Test detection when no modules exist."""
    with PersistTestContext('maven', with_modules=False) as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'detect-modules',
            '--project-dir', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', "Should succeed"
        assert data['count'] == 0, "Should detect 0 modules"


# =============================================================================
# persist Tests
# =============================================================================

def test_persist_maven_creates_commands():
    """Test persist creates Maven commands with canonical names."""
    with PersistTestContext('maven') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'status: success' in result.stdout, "Should report success"
        assert 'modules_updated: 1' in result.stdout, "Should update 1 module (default)"

        # Verify marshal.json was created
        marshal_path = temp_dir / '.plan' / 'marshal.json'
        assert marshal_path.exists(), "Should create marshal.json"

        config = json.loads(marshal_path.read_text())
        assert 'module_config' in config, "Should have module_config section"
        assert 'default' in config['module_config'], "Should have default module"
        assert 'commands' in config['module_config']['default'], "Should have commands"

        commands = config['module_config']['default']['commands']
        assert 'module-tests' in commands, "Should have module-tests command (canonical name)"
        assert 'verify' in commands, "Should have verify command"
        assert 'maven' in commands['module-tests'], "Command should reference maven script"

        # Verify module type is detected
        assert 'type' in config['module_config']['default'], "Should have type field"
        assert config['module_config']['default']['type'] == 'jar', "Default should be jar type"


def test_persist_gradle_creates_commands():
    """Test persist creates Gradle commands with canonical names."""
    with PersistTestContext('gradle') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['module_config']['default']['commands']

        assert 'module-tests' in commands, "Should have module-tests command"
        assert 'gradle' in commands['module-tests'], "Command should reference gradle script"


def test_persist_npm_creates_commands():
    """Test persist creates npm commands with canonical names."""
    with PersistTestContext('npm') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['module_config']['default']['commands']

        assert 'module-tests' in commands, "Should have module-tests command"
        assert 'npm' in commands['module-tests'], "Command should reference npm script"
        assert 'package' in commands, "npm should have package command (canonical name for build)"


def test_persist_with_modules_adds_module_flag():
    """Test persist adds --module flag for non-default modules."""
    with PersistTestContext('maven', with_modules=True) as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"
        assert 'modules_updated: 3' in result.stdout, "Should update 3 modules (default + 2)"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Default module should NOT have --module flag
        default_cmd = config['module_config']['default']['commands']['module-tests']
        assert '--module' not in default_cmd, "Default should not have --module flag"

        # Other modules SHOULD have --module flag
        core_cmd = config['module_config']['core']['commands']['module-tests']
        assert '--module core' in core_cmd, f"Core module should have --module flag: {core_cmd}"


def test_persist_profile_based_commands_from_detection():
    """Test persist generates profile-based commands from detected profiles.

    Profile-dependent commands (integration-tests, coverage, quality-gate) are
    dynamically generated from detected Maven profiles, not hardcoded.
    """
    with PersistTestContext('maven') as temp_dir:
        # Create pom.xml with profiles
        pom_content = '''<project>
            <profiles>
                <profile>
                    <id>pre-commit</id>
                </profile>
                <profile>
                    <id>integration-tests</id>
                </profile>
                <profile>
                    <id>jacoco</id>
                </profile>
            </profiles>
        </project>'''
        (temp_dir / 'pom.xml').write_text(pom_content)

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['module_config']['default']['commands']

        # Should have profile-based commands generated from detected profiles
        assert 'quality-gate' in commands, "Should have quality-gate from pre-commit profile"
        assert '-Ppre-commit' in commands['quality-gate'], "Should use detected pre-commit profile"

        assert 'integration-tests' in commands, "Should have integration-tests from profile"
        assert '-Pintegration-tests' in commands['integration-tests'], "Should use detected profile"

        assert 'coverage' in commands, "Should have coverage from jacoco profile"
        assert '-Pjacoco' in commands['coverage'], "Should use detected jacoco profile"


def test_persist_reports_missing_profile_commands():
    """Test persist reports missing profile-based commands when no matching profiles found."""
    with PersistTestContext('maven') as temp_dir:
        # Create pom.xml without profiles
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['module_config']['default']['commands']

        # Should NOT have profile-based commands without profiles
        assert 'quality-gate' not in commands, "Should not have quality-gate without profile"
        assert 'integration-tests' not in commands, "Should not have integration-tests without profile"
        assert 'coverage' not in commands, "Should not have coverage without profile"

        # Should report missing profile commands
        missing = config['module_config']['default'].get('missing_profile_commands', [])
        assert 'quality-gate' in missing, "Should report quality-gate as missing"
        assert 'integration-tests' in missing, "Should report integration-tests as missing"
        assert 'coverage' in missing, "Should report coverage as missing"


def test_persist_dry_run_does_not_modify():
    """Test persist with --dry-run does not modify marshal.json."""
    with PersistTestContext('maven') as temp_dir:
        marshal_path = temp_dir / '.plan' / 'marshal.json'
        original_content = marshal_path.read_text()

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir),
            '--dry-run'
        )

        assert result.returncode == 0, "Should succeed"
        assert 'status: success' in result.stdout, "Should report success"

        # Verify marshal.json was NOT modified
        assert marshal_path.read_text() == original_content, "Should NOT modify marshal.json in dry run"


def test_persist_preserves_existing_config():
    """Test persist preserves existing marshal.json content."""
    with PersistTestContext('maven') as temp_dir:
        # Create existing marshal.json with custom content
        existing_config = {
            "skill_domains": {"java": {"defaults": ["pm-dev-java:java-core"]}},
            "system": {"retention": {"logs_days": 5}},
            "module_config": {}
        }
        marshal_path = temp_dir / '.plan' / 'marshal.json'
        marshal_path.write_text(json.dumps(existing_config))

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        config = json.loads(marshal_path.read_text())

        # Verify existing content preserved
        assert 'skill_domains' in config, "Should preserve skill_domains"
        assert config['skill_domains']['java']['defaults'] == ["pm-dev-java:java-core"], "Should preserve defaults"
        assert config['system']['retention']['logs_days'] == 5, "Should preserve retention"

        # Verify new content added
        assert 'module_config' in config, "Should add module_config"
        assert 'commands' in config['module_config']['default'], "Should add commands"


def test_persist_help():
    """Test persist --help."""
    result = run_script(SCRIPT_PATH, 'persist', '--help')

    assert '--project-dir' in result.stdout, "Help should show --project-dir option"
    assert '--dry-run' in result.stdout, "Help should show --dry-run option"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # detect-modules tests
        test_detect_modules_maven,
        test_detect_modules_gradle,
        test_detect_modules_npm_workspaces,
        test_detect_modules_none,
        # persist tests
        test_persist_maven_creates_commands,
        test_persist_gradle_creates_commands,
        test_persist_npm_creates_commands,
        test_persist_with_modules_adds_module_flag,
        test_persist_profile_based_commands_from_detection,
        test_persist_reports_missing_profile_commands,
        test_persist_dry_run_does_not_modify,
        test_persist_preserves_existing_config,
        test_persist_help,
    ])
    sys.exit(runner.run())
