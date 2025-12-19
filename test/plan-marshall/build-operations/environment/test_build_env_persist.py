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
SCRIPT_PATH = get_script_path('plan-marshall', 'build-operations', 'build_env.py')


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
        # Create .plan directory
        (self.temp_dir / '.plan').mkdir()

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
    """Test persist creates Maven commands."""
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
        assert 'modules' in config, "Should have modules section"
        assert 'default' in config['modules'], "Should have default module"
        assert 'commands' in config['modules']['default'], "Should have commands"

        commands = config['modules']['default']['commands']
        assert 'test' in commands, "Should have test command"
        assert 'verify' in commands, "Should have verify command"
        assert 'maven' in commands['test'], "Command should reference maven script"


def test_persist_gradle_creates_commands():
    """Test persist creates Gradle commands."""
    with PersistTestContext('gradle') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        assert 'gradle' in commands['test'], "Command should reference gradle script"


def test_persist_npm_creates_commands():
    """Test persist creates npm commands."""
    with PersistTestContext('npm') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        assert 'npm' in commands['test'], "Command should reference npm script"
        assert 'build' in commands, "npm should have build command"


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
        default_cmd = config['modules']['default']['commands']['test']
        assert '--module' not in default_cmd, "Default should not have --module flag"

        # Other modules SHOULD have --module flag
        core_cmd = config['modules']['core']['commands']['test']
        assert '--module core' in core_cmd, f"Core module should have --module flag: {core_cmd}"


def test_persist_pre_commit_adds_profile():
    """Test persist adds --profile pre-commit for pre-commit command."""
    with PersistTestContext('maven') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, "Should succeed"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        pre_commit_cmd = config['modules']['default']['commands']['pre-commit']

        assert '--profile pre-commit' in pre_commit_cmd, f"Should have --profile: {pre_commit_cmd}"


def test_persist_dry_run_does_not_save():
    """Test persist with --dry-run does not save marshal.json."""
    with PersistTestContext('maven') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir),
            '--dry-run'
        )

        assert result.returncode == 0, "Should succeed"
        assert 'status: success' in result.stdout, "Should report success"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        assert not marshal_path.exists(), "Should NOT create marshal.json in dry run"


def test_persist_updates_build_systems():
    """Test persist updates build_systems section."""
    with PersistTestContext('maven') as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        assert 'build_systems' in config, "Should have build_systems section"
        assert len(config['build_systems']) > 0, "Should have at least one build system"
        assert config['build_systems'][0]['system'] == 'maven', "Should be maven"
        assert config['build_systems'][0]['skill'] == 'plan-marshall:build-operations', "Should reference build-operations skill"


def test_persist_preserves_existing_config():
    """Test persist preserves existing marshal.json content."""
    with PersistTestContext('maven') as temp_dir:
        # Create existing marshal.json with custom content
        existing_config = {
            "skill_domains": {"java": {"defaults": ["pm-dev-java:java-core"]}},
            "system": {"retention": {"logs_days": 5}}
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
        assert 'modules' in config, "Should add modules"
        assert 'commands' in config['modules']['default'], "Should add commands"


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
        test_persist_pre_commit_adds_profile,
        test_persist_dry_run_does_not_save,
        test_persist_updates_build_systems,
        test_persist_preserves_existing_config,
        test_persist_help,
    ])
    sys.exit(runner.run())
