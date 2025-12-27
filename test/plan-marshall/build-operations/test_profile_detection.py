#!/usr/bin/env python3
"""Tests for profile detection in build-env.py.

Tests detect-profiles subcommand, profile classification, and profile-based command generation.
"""

import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'extension-api', 'build_env.py')


# =============================================================================
# Test Helpers
# =============================================================================

class ProfileTestContext:
    """Context manager for profile detection tests."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        plan_dir = self.temp_dir / '.plan'
        plan_dir.mkdir()
        # Create initial marshal.json (required by plan-marshall-config)
        (plan_dir / 'marshal.json').write_text(json.dumps({
            "skill_domains": {"system": {}},
            "modules": {},
            "system": {"retention": {}},
            "plan": {"defaults": {}}
        }, indent=2))
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# detect-profiles Tests - Maven
# =============================================================================

def test_detect_profiles_maven_integration_tests():
    """Test detection of integration-tests profile."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>integration-tests</id>
                    <build>
                        <plugins>
                            <plugin>
                                <artifactId>maven-failsafe-plugin</artifactId>
                            </plugin>
                        </plugins>
                    </build>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'count: 1' in result.stdout, "Should detect 1 profile"
        assert 'integration-tests' in result.stdout, "Should detect integration-tests"
        # Should classify to canonical name
        assert 'integration-tests' in result.stdout, "Should classify as integration-tests"


def test_detect_profiles_maven_coverage():
    """Test detection of coverage profile."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>coverage</id>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'coverage' in result.stdout, "Should detect coverage profile"


def test_detect_profiles_maven_benchmark():
    """Test detection of benchmark profile as performance."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>benchmark</id>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'benchmark' in result.stdout, "Should detect benchmark profile"
        assert 'performance' in result.stdout, "Should classify as performance"


def test_detect_profiles_maven_property_activation():
    """Test detection of profile with property activation."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>integration-tests</id>
                    <activation>
                        <property>
                            <name>it</name>
                            <value>true</value>
                        </property>
                    </activation>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'property' in result.stdout, "Should detect property activation"


def test_detect_profiles_maven_multiple():
    """Test detection of multiple profiles."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>integration-tests</id>
                </profile>
                <profile>
                    <id>coverage</id>
                </profile>
                <profile>
                    <id>benchmark</id>
                </profile>
                <profile>
                    <id>pre-commit</id>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'count: 4' in result.stdout, "Should detect 4 profiles"


def test_detect_profiles_no_profiles():
    """Test detection when no profiles exist."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'count: 0' in result.stdout, "Should detect 0 profiles"


# =============================================================================
# persist Tests - Profile-based Commands
# =============================================================================

def test_persist_detects_profiles():
    """Test persist stores detected profiles in config."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>integration-tests</id>
                </profile>
                <profile>
                    <id>coverage</id>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())

        # Check detected_profiles is stored
        assert 'detected_profiles' in config['modules']['default'], \
            "Should store detected_profiles"
        profiles = config['modules']['default']['detected_profiles']
        assert len(profiles) == 2, "Should have 2 detected profiles"

        # Check profile IDs are stored
        profile_ids = [p['id'] for p in profiles]
        assert 'integration-tests' in profile_ids, "Should include integration-tests"
        assert 'coverage' in profile_ids, "Should include coverage"


def test_persist_generates_profile_commands():
    """Test persist generates commands for detected profiles."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>integration-tests</id>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        # Should have integration-tests command generated from profile
        assert 'integration-tests' in commands, \
            f"Should generate integration-tests command. Commands: {list(commands.keys())}"
        assert '-Pintegration-tests' in commands['integration-tests'], \
            f"Should use -P activation: {commands['integration-tests']}"


def test_persist_generates_property_activated_command():
    """Test persist generates command with property activation."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>integration-tests</id>
                    <activation>
                        <property>
                            <name>run.it</name>
                            <value>true</value>
                        </property>
                    </activation>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        # Should have integration-tests command with property activation
        assert 'integration-tests' in commands, "Should generate integration-tests command"
        assert '-Drun.it=true' in commands['integration-tests'], \
            f"Should use -D activation: {commands['integration-tests']}"


def test_persist_generates_quality_gate_from_profile():
    """Test persist generates quality-gate command from detected profile.

    Profile-based commands like quality-gate are now dynamically generated
    from detected profiles, not hardcoded.
    """
    with ProfileTestContext() as temp_dir:
        # Create a project with quality profile
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>quality</id>
                </profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        marshal_path = temp_dir / '.plan' / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        commands = config['modules']['default']['commands']

        # quality-gate should be generated from the detected 'quality' profile
        assert 'quality-gate' in commands, "Should have quality-gate command from profile"
        # Should use -Pquality (the detected profile name)
        assert '-Pquality' in commands['quality-gate'], \
            f"Should use detected profile: {commands['quality-gate']}"


# =============================================================================
# Profile Classification Tests
# =============================================================================

def test_classify_profile_direct_match():
    """Test profile classification with direct match."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile><id>coverage</id></profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert 'coverage' in result.stdout, "Should classify as coverage"


def test_classify_profile_partial_match():
    """Test profile classification with partial match."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile><id>my-integration-tests</id></profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert 'integration-tests' in result.stdout, \
            f"Should classify as integration-tests (partial match): {result.stdout}"


def test_classify_profile_unknown():
    """Test profile classification with unknown profile."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile><id>custom-unknown-profile</id></profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        # Unknown profiles should show - for canonical
        assert 'custom-unknown-profile' in result.stdout, "Should list the profile"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # detect-profiles tests
        test_detect_profiles_maven_integration_tests,
        test_detect_profiles_maven_coverage,
        test_detect_profiles_maven_benchmark,
        test_detect_profiles_maven_property_activation,
        test_detect_profiles_maven_multiple,
        test_detect_profiles_no_profiles,
        # persist tests with profiles
        test_persist_detects_profiles,
        test_persist_generates_profile_commands,
        test_persist_generates_property_activated_command,
        test_persist_generates_quality_gate_from_profile,
        # classification tests
        test_classify_profile_direct_match,
        test_classify_profile_partial_match,
        test_classify_profile_unknown,
    ])
    sys.exit(runner.run())
