#!/usr/bin/env python3
"""Tests for profile detection in build-env.py.

Tests detect-profiles subcommand, profile classification, and profile-based command generation.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    run_script, TestRunner, get_script_path,
    BuildTestContext, MARSHAL_KEY_MODULE_CONFIG
)

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'extension-api', 'build_env.py')


# =============================================================================
# detect-profiles Tests - Maven
# =============================================================================

def test_detect_profiles_maven_integration_tests():
    """Test detection of integration-tests profile."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<project>
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
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'count: 1' in result.stdout, "Should detect 1 profile"
        assert 'integration-tests' in result.stdout, "Should detect integration-tests"
        # Should classify to canonical name
        assert 'integration-tests' in result.stdout, "Should classify as integration-tests"


def test_detect_profiles_maven_coverage():
    """Test detection of coverage profile."""
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['coverage'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'coverage' in result.stdout, "Should detect coverage profile"


def test_detect_profiles_maven_benchmark():
    """Test detection of benchmark profile as performance."""
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['benchmark'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'benchmark' in result.stdout, "Should detect benchmark profile"
        assert 'performance' in result.stdout, "Should classify as performance"


def test_detect_profiles_maven_property_activation():
    """Test detection of profile with property activation."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<project>
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
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'property' in result.stdout, "Should detect property activation"


def test_detect_profiles_maven_multiple():
    """Test detection of multiple profiles."""
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['integration-tests', 'coverage', 'benchmark', 'pre-commit'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'count: 4' in result.stdout, "Should detect 4 profiles"


def test_detect_profiles_no_profiles():
    """Test detection when no profiles exist."""
    with BuildTestContext() as ctx:
        ctx.create_pom()

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'count: 0' in result.stdout, "Should detect 0 profiles"


# =============================================================================
# persist Tests - Profile-based Commands
# =============================================================================

def test_persist_no_diagnostic_fields_stored():
    """Test persist does NOT store diagnostic fields in marshal.json (architectural change)."""
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['integration-tests', 'coverage'])

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        default_config = config[MARSHAL_KEY_MODULE_CONFIG]['default']

        # Diagnostic fields should NOT be stored in marshal.json
        # They are now only reported in stdout for user action via run-config profile mappings
        assert 'detected_profiles' not in default_config, "Should NOT store detected_profiles"
        assert 'unclassified_profiles' not in default_config, "Should NOT store unclassified_profiles"
        assert 'missing_profile_commands' not in default_config, "Should NOT store missing_profile_commands"

        # But commands should still be generated from detected profiles
        assert 'integration-tests' in default_config['commands'], "Should generate integration-tests command"
        assert 'coverage' in default_config['commands'], "Should generate coverage command"


def test_persist_generates_profile_commands():
    """Test persist generates commands for detected profiles."""
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['integration-tests'])

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # Should have integration-tests command generated from profile
        assert 'integration-tests' in commands, \
            f"Should generate integration-tests command. Commands: {list(commands.keys())}"
        assert '-Pintegration-tests' in commands['integration-tests'], \
            f"Should use -P activation: {commands['integration-tests']}"


def test_persist_generates_property_activated_command():
    """Test persist generates command with property activation."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<project>
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
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

        # Should have integration-tests command with property activation
        assert 'integration-tests' in commands, "Should generate integration-tests command"
        assert '-Drun.it=true' in commands['integration-tests'], \
            f"Should use -D activation: {commands['integration-tests']}"


def test_persist_generates_quality_gate_from_profile():
    """Test persist generates quality-gate command from detected profile.

    Profile-based commands like quality-gate are now dynamically generated
    from detected profiles, not hardcoded.
    """
    with BuildTestContext() as ctx:
        # Create a project with quality profile
        ctx.create_pom(profiles=['quality'])

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        config = ctx.load_marshal_json()
        commands = config[MARSHAL_KEY_MODULE_CONFIG]['default']['commands']

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
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['coverage'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert 'coverage' in result.stdout, "Should classify as coverage"


def test_classify_profile_partial_match():
    """Test profile classification with partial match."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile><id>my-integration-tests</id></profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert 'integration-tests' in result.stdout, \
            f"Should classify as integration-tests (partial match): {result.stdout}"


def test_classify_profile_unknown():
    """Test profile classification with unknown profile."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile><id>custom-unknown-profile</id></profile>
            </profiles>
        </project>''')

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        # Unknown profiles should show - for canonical
        assert 'custom-unknown-profile' in result.stdout, "Should list the profile"


def test_classify_profile_quality_gate_aliases():
    """Test profile classification for quality-gate aliases.

    Tests that aliases defined in CANONICAL_COMMANDS are correctly mapped.
    """
    with BuildTestContext() as ctx:
        # Test 'pre-commit' alias -> quality-gate
        ctx.create_pom(profiles=['pre-commit'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'quality-gate' in result.stdout, \
            f"pre-commit should classify as quality-gate: {result.stdout}"


def test_classify_profile_performance_aliases():
    """Test profile classification for performance aliases.

    Tests that aliases defined in CANONICAL_COMMANDS are correctly mapped.
    """
    with BuildTestContext() as ctx:
        # Test 'benchmark' alias -> performance
        ctx.create_pom(profiles=['benchmark'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'performance' in result.stdout, \
            f"benchmark should classify as performance: {result.stdout}"


def test_classify_profile_coverage_jacoco_alias():
    """Test profile classification for coverage jacoco alias.

    Tests that 'jacoco' alias maps to coverage canonical command.
    """
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['jacoco'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'coverage' in result.stdout, \
            f"jacoco should classify as coverage: {result.stdout}"


def test_classify_profile_integration_e2e_alias():
    """Test profile classification for integration-tests e2e alias.

    Tests that 'e2e' alias maps to integration-tests canonical command.
    """
    with BuildTestContext() as ctx:
        ctx.create_pom(profiles=['e2e'])

        result = run_script(
            SCRIPT_PATH,
            'detect-profiles',
            '--project-dir', str(ctx.temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        assert 'integration-tests' in result.stdout, \
            f"e2e should classify as integration-tests: {result.stdout}"


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
        test_persist_no_diagnostic_fields_stored,
        test_persist_generates_profile_commands,
        test_persist_generates_property_activated_command,
        test_persist_generates_quality_gate_from_profile,
        # classification tests
        test_classify_profile_direct_match,
        test_classify_profile_partial_match,
        test_classify_profile_unknown,
        # alias tests (one per canonical command)
        test_classify_profile_quality_gate_aliases,
        test_classify_profile_performance_aliases,
        test_classify_profile_coverage_jacoco_alias,
        test_classify_profile_integration_e2e_alias,
    ])
    sys.exit(runner.run())
