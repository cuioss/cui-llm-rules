#!/usr/bin/env python3
"""Tests for extension.py implementations across domain bundles.

Tests that each extension:
1. Implements all required functions correctly
2. Returns properly structured data from get_skill_domains()
3. Returns valid command mappings
4. References skills that actually exist
5. Covers required canonical commands (for build bundles)

These are behavioral tests, not just structural validation.
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner, PROJECT_ROOT, MARKETPLACE_ROOT

# Required canonical commands for build-providing bundles
REQUIRED_CANONICAL_COMMANDS = ['module-tests', 'quality-gate', 'verify']

# Valid domain profile categories
VALID_PROFILE_CATEGORIES = ['core', 'implementation', 'testing', 'quality']


# =============================================================================
# Helper Functions
# =============================================================================

def _ensure_extension_base_loaded():
    """Ensure extension_base module is loaded and available for import."""
    if 'extension_base' in sys.modules:
        return

    base_path = MARKETPLACE_ROOT / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts' / 'extension_base.py'
    if not base_path.exists():
        raise FileNotFoundError(f"extension_base.py not found: {base_path}")

    spec = importlib.util.spec_from_file_location("extension_base", base_path)
    base_module = importlib.util.module_from_spec(spec)
    sys.modules['extension_base'] = base_module
    spec.loader.exec_module(base_module)


def load_extension(bundle_name: str):
    """Load an extension.py module and return Extension instance."""
    # Ensure extension_base is available for import
    _ensure_extension_base_loaded()

    extension_path = MARKETPLACE_ROOT / bundle_name / 'skills' / 'plan-marshall-plugin' / 'extension.py'

    if not extension_path.exists():
        raise FileNotFoundError(f"Extension not found: {extension_path}")

    spec = importlib.util.spec_from_file_location(f"extension_{bundle_name}", extension_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Return Extension instance (clean slate - no backward compat functions)
    if hasattr(module, 'Extension'):
        return module.Extension()

    raise ValueError(f"No Extension class found in {bundle_name}")


def skill_exists(skill_ref: str) -> bool:
    """Check if a skill reference (bundle:skill) exists."""
    if ':' not in skill_ref:
        return False

    bundle, skill = skill_ref.split(':', 1)
    skill_path = MARKETPLACE_ROOT / bundle / 'skills' / skill

    # Check for SKILL.md (primary) or at least skill directory
    return skill_path.is_dir() and (
        (skill_path / 'SKILL.md').exists() or
        len(list(skill_path.glob('*.md'))) > 0 or
        len(list(skill_path.glob('scripts/*.py'))) > 0
    )


def create_test_project(build_system: str) -> Path:
    """Create a temporary test project for a given build system."""
    temp_dir = Path(tempfile.mkdtemp())

    if build_system == 'maven':
        (temp_dir / 'pom.xml').write_text('<project></project>')
    elif build_system == 'gradle':
        (temp_dir / 'build.gradle').write_text('plugins { id "java" }')
    elif build_system == 'npm':
        (temp_dir / 'package.json').write_text('{"name": "test", "version": "1.0.0"}')
    elif build_system == 'documentation':
        (temp_dir / 'doc').mkdir()
    elif build_system == 'requirements':
        (temp_dir / 'doc' / 'spec').mkdir(parents=True)
        (temp_dir / 'doc' / 'spec' / 'Requirements.adoc').write_text('= Requirements\n')
    elif build_system == 'plugin-dev':
        (temp_dir / 'marketplace' / 'bundles').mkdir(parents=True)

    return temp_dir


def cleanup_test_project(temp_dir: Path):
    """Clean up temporary test project."""
    shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# Validation Functions
# =============================================================================

def validate_skill_domains_structure(domains: dict, bundle_name: str) -> list:
    """Validate the structure of get_skill_domains() return value."""
    issues = []

    # Must have 'domain' key
    if 'domain' not in domains:
        issues.append(f"{bundle_name}: get_skill_domains() missing 'domain' key")
        return issues

    domain = domains['domain']

    # Domain must have key and name
    if not isinstance(domain, dict):
        issues.append(f"{bundle_name}: domain must be a dict, got {type(domain)}")
        return issues

    if 'key' not in domain:
        issues.append(f"{bundle_name}: domain missing 'key'")
    elif not isinstance(domain['key'], str) or not domain['key']:
        issues.append(f"{bundle_name}: domain.key must be non-empty string")

    if 'name' not in domain:
        issues.append(f"{bundle_name}: domain missing 'name'")
    elif not isinstance(domain['name'], str) or not domain['name']:
        issues.append(f"{bundle_name}: domain.name must be non-empty string")

    # Must have 'profiles' key
    if 'profiles' not in domains:
        issues.append(f"{bundle_name}: get_skill_domains() missing 'profiles' key")
        return issues

    profiles = domains['profiles']

    if not isinstance(profiles, dict):
        issues.append(f"{bundle_name}: profiles must be a dict, got {type(profiles)}")
        return issues

    # Validate each profile category
    for category, config in profiles.items():
        if category not in VALID_PROFILE_CATEGORIES:
            issues.append(f"{bundle_name}: unknown profile category '{category}'")
            continue

        if not isinstance(config, dict):
            issues.append(f"{bundle_name}: profiles.{category} must be a dict")
            continue

        # Must have defaults and optionals
        if 'defaults' not in config:
            issues.append(f"{bundle_name}: profiles.{category} missing 'defaults'")
        elif not isinstance(config['defaults'], list):
            issues.append(f"{bundle_name}: profiles.{category}.defaults must be a list")

        if 'optionals' not in config:
            issues.append(f"{bundle_name}: profiles.{category} missing 'optionals'")
        elif not isinstance(config['optionals'], list):
            issues.append(f"{bundle_name}: profiles.{category}.optionals must be a list")

    return issues


def validate_skill_references(domains: dict, bundle_name: str) -> list:
    """Validate that all skill references in profiles actually exist."""
    issues = []

    profiles = domains.get('profiles', {})

    for category, config in profiles.items():
        if not isinstance(config, dict):
            continue

        # Check defaults
        for skill_ref in config.get('defaults', []):
            if not skill_exists(skill_ref):
                issues.append(f"{bundle_name}: skill reference '{skill_ref}' in profiles.{category}.defaults does not exist")

        # Check optionals
        for skill_ref in config.get('optionals', []):
            if not skill_exists(skill_ref):
                issues.append(f"{bundle_name}: skill reference '{skill_ref}' in profiles.{category}.optionals does not exist")

    return issues


def validate_command_mappings(mappings: dict, bundle_name: str, expected_systems: list) -> list:
    """Validate command mappings cover required canonicals."""
    issues = []

    if not expected_systems:
        # Non-build bundles should return empty mappings
        if mappings:
            issues.append(f"{bundle_name}: non-build bundle should return empty command mappings")
        return issues

    for build_system in expected_systems:
        if build_system not in mappings:
            issues.append(f"{bundle_name}: missing command mappings for '{build_system}'")
            continue

        system_mappings = mappings[build_system]

        # Check required canonical commands
        for canonical in REQUIRED_CANONICAL_COMMANDS:
            if canonical not in system_mappings:
                issues.append(f"{bundle_name}: missing required canonical command '{canonical}' for {build_system}")

        # Validate command format
        for canonical, template in system_mappings.items():
            if not isinstance(template, str):
                issues.append(f"{bundle_name}: command template for {canonical} must be string")
                continue

            # Should use execute-script.py pattern
            if 'python3 .plan/execute-script.py' not in template:
                issues.append(f"{bundle_name}: command '{canonical}' should use execute-script.py pattern")

    return issues


def validate_triage_outline_references(module, bundle_name: str) -> list:
    """Validate that provides_triage() and provides_outline() return valid refs."""
    issues = []

    if hasattr(module, 'provides_triage'):
        triage = module.provides_triage()
        if triage is not None:
            if not isinstance(triage, str):
                issues.append(f"{bundle_name}: provides_triage() must return str or None")
            elif not skill_exists(triage):
                issues.append(f"{bundle_name}: triage skill '{triage}' does not exist")

    if hasattr(module, 'provides_outline'):
        outline = module.provides_outline()
        if outline is not None:
            if not isinstance(outline, str):
                issues.append(f"{bundle_name}: provides_outline() must return str or None")
            elif not skill_exists(outline):
                issues.append(f"{bundle_name}: outline skill '{outline}' does not exist")

    return issues


# =============================================================================
# pm-dev-java Extension Tests
# =============================================================================

def test_java_extension_is_applicable_maven():
    """Test pm-dev-java is_applicable for Maven projects."""
    ext = load_extension('pm-dev-java')
    temp_dir = create_test_project('maven')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is True, "Should be applicable to Maven project"
    finally:
        cleanup_test_project(temp_dir)


def test_java_extension_is_applicable_gradle():
    """Test pm-dev-java is_applicable for Gradle projects."""
    ext = load_extension('pm-dev-java')
    temp_dir = create_test_project('gradle')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is True, "Should be applicable to Gradle project"
    finally:
        cleanup_test_project(temp_dir)


def test_java_extension_is_applicable_negative():
    """Test pm-dev-java is_applicable returns False for npm-only projects."""
    ext = load_extension('pm-dev-java')
    temp_dir = create_test_project('npm')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is False, "Should NOT be applicable to npm-only project"
    finally:
        cleanup_test_project(temp_dir)


def test_java_extension_provides_build_systems():
    """Test pm-dev-java provides_build_systems returns maven and gradle."""
    ext = load_extension('pm-dev-java')
    systems = ext.provides_build_systems()

    assert isinstance(systems, list), "Should return a list"
    assert 'maven' in systems, "Should include maven"
    assert 'gradle' in systems, "Should include gradle"


def test_java_extension_skill_domains_structure():
    """Test pm-dev-java get_skill_domains returns valid structure."""
    ext = load_extension('pm-dev-java')
    domains = ext.get_skill_domains()

    issues = validate_skill_domains_structure(domains, 'pm-dev-java')
    assert not issues, f"Structure issues: {issues}"

    # Verify domain key
    assert domains['domain']['key'] == 'java', "Domain key should be 'java'"


def test_java_extension_skill_references_exist():
    """Test pm-dev-java skill references point to existing skills."""
    ext = load_extension('pm-dev-java')
    domains = ext.get_skill_domains()

    issues = validate_skill_references(domains, 'pm-dev-java')
    assert not issues, f"Missing skills: {issues}"


def test_java_extension_command_mappings():
    """Test pm-dev-java command mappings cover required canonicals."""
    ext = load_extension('pm-dev-java')
    mappings = ext.get_command_mappings()
    systems = ext.provides_build_systems()

    issues = validate_command_mappings(mappings, 'pm-dev-java', systems)
    assert not issues, f"Command mapping issues: {issues}"


def test_java_extension_triage_reference():
    """Test pm-dev-java provides_triage returns valid reference."""
    ext = load_extension('pm-dev-java')
    issues = validate_triage_outline_references(ext, 'pm-dev-java')
    assert not issues, f"Reference issues: {issues}"


def test_java_extension_get_modules():
    """Test pm-dev-java get_modules for multi-module project."""
    ext = load_extension('pm-dev-java')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create multi-module Maven project
        (temp_dir / 'pom.xml').write_text('''<project>
            <modules>
                <module>core</module>
                <module>api</module>
            </modules>
        </project>''')
        (temp_dir / 'core').mkdir()
        (temp_dir / 'core' / 'pom.xml').write_text('<project></project>')
        (temp_dir / 'api').mkdir()
        (temp_dir / 'api' / 'pom.xml').write_text('<project></project>')

        modules = ext.get_modules(str(temp_dir))

        assert isinstance(modules, list), "Should return a list"
        assert len(modules) == 2, f"Should detect 2 modules, got {len(modules)}"

        names = [m['name'] for m in modules]
        assert 'core' in names, "Should include 'core' module"
        assert 'api' in names, "Should include 'api' module"
    finally:
        cleanup_test_project(temp_dir)


def test_java_extension_get_module_type():
    """Test pm-dev-java get_module_type detection."""
    ext = load_extension('pm-dev-java')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create jar module (default)
        (temp_dir / 'pom.xml').write_text('<project></project>')
        assert ext.get_module_type(str(temp_dir)) == 'jar', "Default should be 'jar'"

        # Create pom module
        (temp_dir / 'pom.xml').write_text('<project><packaging>pom</packaging></project>')
        assert ext.get_module_type(str(temp_dir)) == 'pom', "Should detect 'pom' packaging"

        # Create war module
        (temp_dir / 'pom.xml').write_text('<project><packaging>war</packaging></project>')
        assert ext.get_module_type(str(temp_dir)) == 'war', "Should detect 'war' packaging"

        # Create Quarkus module
        (temp_dir / 'pom.xml').write_text('<project><build><plugins><plugin><artifactId>quarkus-maven-plugin</artifactId></plugin></plugins></build></project>')
        assert ext.get_module_type(str(temp_dir)) == 'quarkus', "Should detect Quarkus"
    finally:
        cleanup_test_project(temp_dir)


# =============================================================================
# pm-dev-frontend Extension Tests
# =============================================================================

def test_frontend_extension_is_applicable():
    """Test pm-dev-frontend is_applicable for npm projects."""
    ext = load_extension('pm-dev-frontend')
    temp_dir = create_test_project('npm')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is True, "Should be applicable to npm project"
    finally:
        cleanup_test_project(temp_dir)


def test_frontend_extension_is_applicable_negative():
    """Test pm-dev-frontend is_applicable returns False for Maven-only projects."""
    ext = load_extension('pm-dev-frontend')
    temp_dir = create_test_project('maven')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is False, "Should NOT be applicable to Maven-only project"
    finally:
        cleanup_test_project(temp_dir)


def test_frontend_extension_provides_build_systems():
    """Test pm-dev-frontend provides_build_systems returns npm."""
    ext = load_extension('pm-dev-frontend')
    systems = ext.provides_build_systems()

    assert isinstance(systems, list), "Should return a list"
    assert 'npm' in systems, "Should include npm"


def test_frontend_extension_skill_domains_structure():
    """Test pm-dev-frontend get_skill_domains returns valid structure."""
    ext = load_extension('pm-dev-frontend')
    domains = ext.get_skill_domains()

    issues = validate_skill_domains_structure(domains, 'pm-dev-frontend')
    assert not issues, f"Structure issues: {issues}"

    # Verify domain key
    assert domains['domain']['key'] == 'javascript', "Domain key should be 'javascript'"


def test_frontend_extension_skill_references_exist():
    """Test pm-dev-frontend skill references point to existing skills."""
    ext = load_extension('pm-dev-frontend')
    domains = ext.get_skill_domains()

    issues = validate_skill_references(domains, 'pm-dev-frontend')
    assert not issues, f"Missing skills: {issues}"


def test_frontend_extension_command_mappings():
    """Test pm-dev-frontend command mappings cover required canonicals."""
    ext = load_extension('pm-dev-frontend')
    mappings = ext.get_command_mappings()
    systems = ext.provides_build_systems()

    issues = validate_command_mappings(mappings, 'pm-dev-frontend', systems)
    assert not issues, f"Command mapping issues: {issues}"


def test_frontend_extension_triage_reference():
    """Test pm-dev-frontend provides_triage returns valid reference."""
    ext = load_extension('pm-dev-frontend')
    issues = validate_triage_outline_references(ext, 'pm-dev-frontend')
    assert not issues, f"Reference issues: {issues}"


def test_frontend_extension_get_modules_workspaces():
    """Test pm-dev-frontend get_modules for npm workspaces."""
    ext = load_extension('pm-dev-frontend')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create workspace project
        (temp_dir / 'package.json').write_text(json.dumps({
            "name": "test",
            "workspaces": ["packages/*"]
        }))
        packages_dir = temp_dir / 'packages'
        packages_dir.mkdir()
        (packages_dir / 'ui').mkdir()
        (packages_dir / 'ui' / 'package.json').write_text('{"name": "ui"}')
        (packages_dir / 'lib').mkdir()
        (packages_dir / 'lib' / 'package.json').write_text('{"name": "lib"}')

        modules = ext.get_modules(str(temp_dir))

        assert isinstance(modules, list), "Should return a list"
        assert len(modules) == 2, f"Should detect 2 workspaces, got {len(modules)}"
    finally:
        cleanup_test_project(temp_dir)


# =============================================================================
# pm-plugin-development Extension Tests
# =============================================================================

def test_plugin_dev_extension_is_applicable():
    """Test pm-plugin-development is_applicable for marketplace projects."""
    ext = load_extension('pm-plugin-development')
    temp_dir = create_test_project('plugin-dev')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is True, "Should be applicable to marketplace project"
    finally:
        cleanup_test_project(temp_dir)


def test_plugin_dev_extension_is_applicable_negative():
    """Test pm-plugin-development is_applicable returns False for non-marketplace."""
    ext = load_extension('pm-plugin-development')
    temp_dir = create_test_project('maven')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is False, "Should NOT be applicable to Maven-only project"
    finally:
        cleanup_test_project(temp_dir)


def test_plugin_dev_extension_provides_build_systems():
    """Test pm-plugin-development provides_build_systems returns empty list."""
    ext = load_extension('pm-plugin-development')
    systems = ext.provides_build_systems()

    assert isinstance(systems, list), "Should return a list"
    assert len(systems) == 0, "Should return empty list (no build systems)"


def test_plugin_dev_extension_skill_domains_structure():
    """Test pm-plugin-development get_skill_domains returns valid structure."""
    ext = load_extension('pm-plugin-development')
    domains = ext.get_skill_domains()

    issues = validate_skill_domains_structure(domains, 'pm-plugin-development')
    assert not issues, f"Structure issues: {issues}"

    # Verify domain key
    assert domains['domain']['key'] == 'plan-marshall-plugin-dev', "Domain key should be 'plan-marshall-plugin-dev'"


def test_plugin_dev_extension_skill_references_exist():
    """Test pm-plugin-development skill references point to existing skills."""
    ext = load_extension('pm-plugin-development')
    domains = ext.get_skill_domains()

    issues = validate_skill_references(domains, 'pm-plugin-development')
    assert not issues, f"Missing skills: {issues}"


def test_plugin_dev_extension_command_mappings():
    """Test pm-plugin-development command mappings are empty (no build)."""
    ext = load_extension('pm-plugin-development')
    mappings = ext.get_command_mappings()

    assert isinstance(mappings, dict), "Should return a dict"
    assert len(mappings) == 0, "Should return empty mappings"


def test_plugin_dev_extension_triage_reference():
    """Test pm-plugin-development provides_triage returns valid reference."""
    ext = load_extension('pm-plugin-development')
    issues = validate_triage_outline_references(ext, 'pm-plugin-development')
    assert not issues, f"Reference issues: {issues}"


# =============================================================================
# pm-requirements Extension Tests
# =============================================================================

def test_requirements_extension_is_applicable():
    """Test pm-requirements is_applicable for requirements projects."""
    ext = load_extension('pm-requirements')
    temp_dir = create_test_project('requirements')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is True, "Should be applicable to requirements project"
    finally:
        cleanup_test_project(temp_dir)


def test_requirements_extension_is_applicable_negative():
    """Test pm-requirements is_applicable returns False for non-requirements."""
    ext = load_extension('pm-requirements')
    temp_dir = create_test_project('maven')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is False, "Should NOT be applicable to Maven-only project"
    finally:
        cleanup_test_project(temp_dir)


def test_requirements_extension_skill_domains_structure():
    """Test pm-requirements get_skill_domains returns valid structure."""
    ext = load_extension('pm-requirements')
    domains = ext.get_skill_domains()

    issues = validate_skill_domains_structure(domains, 'pm-requirements')
    assert not issues, f"Structure issues: {issues}"

    # Verify domain key
    assert domains['domain']['key'] == 'requirements', "Domain key should be 'requirements'"


def test_requirements_extension_skill_references_exist():
    """Test pm-requirements skill references point to existing skills."""
    ext = load_extension('pm-requirements')
    domains = ext.get_skill_domains()

    issues = validate_skill_references(domains, 'pm-requirements')
    assert not issues, f"Missing skills: {issues}"


# =============================================================================
# pm-documents Extension Tests
# =============================================================================

def test_documents_extension_is_applicable():
    """Test pm-documents is_applicable for documentation projects."""
    ext = load_extension('pm-documents')
    temp_dir = create_test_project('documentation')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is True, "Should be applicable to documentation project"
    finally:
        cleanup_test_project(temp_dir)


def test_documents_extension_is_applicable_negative():
    """Test pm-documents is_applicable returns False for non-doc projects."""
    ext = load_extension('pm-documents')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # No doc/ directory
        result = ext.is_applicable(str(temp_dir))
        assert result is False, "Should NOT be applicable without doc/ directory"
    finally:
        cleanup_test_project(temp_dir)


def test_documents_extension_skill_domains_structure():
    """Test pm-documents get_skill_domains returns valid structure."""
    ext = load_extension('pm-documents')
    domains = ext.get_skill_domains()

    issues = validate_skill_domains_structure(domains, 'pm-documents')
    assert not issues, f"Structure issues: {issues}"

    # Verify domain key
    assert domains['domain']['key'] == 'documentation', "Domain key should be 'documentation'"


def test_documents_extension_skill_references_exist():
    """Test pm-documents skill references point to existing skills."""
    ext = load_extension('pm-documents')
    domains = ext.get_skill_domains()

    issues = validate_skill_references(domains, 'pm-documents')
    assert not issues, f"Missing skills: {issues}"


# =============================================================================
# pm-dev-java-cui Extension Tests
# =============================================================================

def test_java_cui_extension_is_applicable():
    """Test pm-dev-java-cui is_applicable for CUI projects."""
    ext = load_extension('pm-dev-java-cui')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create pom.xml with cui dependency
        (temp_dir / 'pom.xml').write_text('<project><dependencies><dependency>cui-core</dependency></dependencies></project>')
        result = ext.is_applicable(str(temp_dir))
        assert result is True, "Should be applicable to CUI project"
    finally:
        cleanup_test_project(temp_dir)


def test_java_cui_extension_is_applicable_negative():
    """Test pm-dev-java-cui is_applicable returns False for non-CUI projects."""
    ext = load_extension('pm-dev-java-cui')
    temp_dir = create_test_project('maven')

    try:
        result = ext.is_applicable(str(temp_dir))
        assert result is False, "Should NOT be applicable to non-CUI Maven project"
    finally:
        cleanup_test_project(temp_dir)


def test_java_cui_extension_provides_build_systems():
    """Test pm-dev-java-cui provides_build_systems returns empty list."""
    ext = load_extension('pm-dev-java-cui')
    systems = ext.provides_build_systems()

    assert isinstance(systems, list), "Should return a list"
    assert len(systems) == 0, "Should return empty list (no build systems)"


def test_java_cui_extension_skill_domains_structure():
    """Test pm-dev-java-cui get_skill_domains returns valid structure."""
    ext = load_extension('pm-dev-java-cui')
    domains = ext.get_skill_domains()

    issues = validate_skill_domains_structure(domains, 'pm-dev-java-cui')
    assert not issues, f"Structure issues: {issues}"

    # Verify domain key
    assert domains['domain']['key'] == 'java-cui', "Domain key should be 'java-cui'"


def test_java_cui_extension_skill_references_exist():
    """Test pm-dev-java-cui skill references point to existing skills."""
    ext = load_extension('pm-dev-java-cui')
    domains = ext.get_skill_domains()

    issues = validate_skill_references(domains, 'pm-dev-java-cui')
    assert not issues, f"Missing skills: {issues}"


def test_java_cui_extension_command_mappings():
    """Test pm-dev-java-cui command mappings are empty (no build)."""
    ext = load_extension('pm-dev-java-cui')
    mappings = ext.get_command_mappings()

    assert isinstance(mappings, dict), "Should return a dict"
    assert len(mappings) == 0, "Should return empty mappings"


# =============================================================================
# pm-dev-java Profile Tests
# =============================================================================

def test_java_extension_get_profiles():
    """Test pm-dev-java get_profiles for Maven project with profiles."""
    ext = load_extension('pm-dev-java')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create pom.xml with profiles
        (temp_dir / 'pom.xml').write_text('''<project>
            <profiles>
                <profile>
                    <id>integration-tests</id>
                    <activation>
                        <property>
                            <name>run.it</name>
                        </property>
                    </activation>
                </profile>
                <profile>
                    <id>coverage</id>
                </profile>
            </profiles>
        </project>''')

        profiles = ext.get_profiles(str(temp_dir))

        assert isinstance(profiles, list), "Should return a list"
        assert len(profiles) == 2, f"Should detect 2 profiles, got {len(profiles)}"

        profile_ids = [p['id'] for p in profiles]
        assert 'integration-tests' in profile_ids, "Should include 'integration-tests' profile"
        assert 'coverage' in profile_ids, "Should include 'coverage' profile"

        # Verify canonical classification
        it_profile = next(p for p in profiles if p['id'] == 'integration-tests')
        assert it_profile['canonical'] == 'integration-tests', "Should classify as integration-tests"

        coverage_profile = next(p for p in profiles if p['id'] == 'coverage')
        assert coverage_profile['canonical'] == 'coverage', "Should classify as coverage"
    finally:
        cleanup_test_project(temp_dir)


def test_java_extension_generate_profile_command_maven():
    """Test pm-dev-java generate_profile_command for Maven."""
    ext = load_extension('pm-dev-java')

    # Test command-line profile activation
    cmd = ext.generate_profile_command(
        build_system="maven",
        canonical="integration-tests",
        profile_id="integration-tests",
        activation={"type": "command-line"}
    )

    assert cmd is not None, "Should return a command"
    assert "maven" in cmd, "Should use maven script"
    assert "-Pintegration-tests" in cmd, "Should include profile flag"

    # Test property activation
    cmd_prop = ext.generate_profile_command(
        build_system="maven",
        canonical="integration-tests",
        profile_id="it",
        activation={"type": "property", "property": "run.it", "value": "true"}
    )

    assert cmd_prop is not None, "Should return a command"
    assert "-Drun.it=true" in cmd_prop, "Should include property flag"


def test_java_extension_generate_profile_command_gradle():
    """Test pm-dev-java generate_profile_command for Gradle."""
    ext = load_extension('pm-dev-java')

    cmd = ext.generate_profile_command(
        build_system="gradle",
        canonical="integration-tests",
        profile_id="integrationTest",
        activation={"type": "task"}
    )

    assert cmd is not None, "Should return a command"
    assert "gradle" in cmd, "Should use gradle script"
    assert "integrationTest" in cmd, "Should include task name"


def test_java_extension_classify_profile():
    """Test pm-dev-java classify_profile helper."""
    ext = load_extension('pm-dev-java')

    # Test exact matches
    assert ext.classify_profile("integration-tests") == "integration-tests"
    assert ext.classify_profile("coverage") == "coverage"
    assert ext.classify_profile("jacoco") == "coverage"

    # Test case-insensitive
    assert ext.classify_profile("INTEGRATION-TESTS") == "integration-tests"

    # Test substring match
    assert ext.classify_profile("my-integration-tests-profile") == "integration-tests"

    # Test non-matching
    assert ext.classify_profile("unknown-profile") is None


# =============================================================================
# pm-dev-frontend Profile Tests
# =============================================================================

def test_frontend_extension_get_profiles():
    """Test pm-dev-frontend get_profiles for npm scripts."""
    ext = load_extension('pm-dev-frontend')
    temp_dir = Path(tempfile.mkdtemp())

    try:
        (temp_dir / 'package.json').write_text(json.dumps({
            "name": "test",
            "scripts": {
                "test": "jest",
                "test:e2e": "playwright test",
                "lint": "eslint .",
                "build": "webpack"
            }
        }))

        profiles = ext.get_profiles(str(temp_dir))

        assert isinstance(profiles, list), "Should return a list"
        # Should detect e2e and lint as profile-like scripts
        profile_ids = [p['id'] for p in profiles]
        assert 'test:e2e' in profile_ids or 'lint' in profile_ids, "Should detect some profiles"
    finally:
        cleanup_test_project(temp_dir)


def test_frontend_extension_generate_profile_command():
    """Test pm-dev-frontend generate_profile_command."""
    ext = load_extension('pm-dev-frontend')

    # Use positional args to match the API signature
    cmd = ext.generate_profile_command(
        "npm",                    # build_system
        "integration-tests",      # canonical (unused but required)
        "test:e2e",               # profile_id
        {"type": "script"}        # activation (unused but required)
    )

    assert cmd is not None, "Should return a command"
    assert "npm" in cmd, "Should use npm script"
    assert "test:e2e" in cmd, "Should include script name"


# =============================================================================
# New Triage/Outline Reference Tests
# =============================================================================

def test_requirements_extension_triage_reference():
    """Test pm-requirements provides_triage returns valid reference."""
    ext = load_extension('pm-requirements')
    issues = validate_triage_outline_references(ext, 'pm-requirements')
    assert not issues, f"Reference issues: {issues}"


def test_documents_extension_triage_reference():
    """Test pm-documents provides_triage returns valid reference."""
    ext = load_extension('pm-documents')
    issues = validate_triage_outline_references(ext, 'pm-documents')
    assert not issues, f"Reference issues: {issues}"


def test_plugin_dev_extension_outline_reference():
    """Test pm-plugin-development provides_outline returns valid reference."""
    ext = load_extension('pm-plugin-development')

    outline = ext.provides_outline()
    assert outline is not None, "Should provide outline skill"
    assert skill_exists(outline), f"Outline skill '{outline}' should exist"


# =============================================================================
# Command Template Helper Tests
# =============================================================================

def test_build_command_template_helper():
    """Test build_command_template helper method."""
    ext = load_extension('pm-dev-java')

    # Test with module placeholder
    cmd = ext.build_command_template("pm-dev-java", "maven", "clean test")
    assert 'python3 .plan/execute-script.py' in cmd
    assert 'pm-dev-java:plan-marshall-plugin:maven' in cmd
    assert '--targets "clean test"' in cmd
    assert '{module}' in cmd

    # Test without module placeholder
    cmd_no_module = ext.build_command_template("pm-dev-java", "maven", "clean", include_module_placeholder=False)
    assert '{module}' not in cmd_no_module


# =============================================================================
# Cross-Bundle Validation Tests
# =============================================================================

def test_all_extensions_have_unique_domain_keys():
    """Test that all extensions have unique domain keys."""
    bundles = ['pm-dev-java', 'pm-dev-java-cui', 'pm-dev-frontend', 'pm-plugin-development', 'pm-requirements', 'pm-documents']
    domain_keys = {}

    for bundle in bundles:
        try:
            ext = load_extension(bundle)
            domains = ext.get_skill_domains()
            key = domains['domain']['key']

            if key in domain_keys:
                raise AssertionError(f"Duplicate domain key '{key}' in {bundle} and {domain_keys[key]}")

            domain_keys[key] = bundle
        except FileNotFoundError:
            pass  # Skip bundles without extensions

    assert len(domain_keys) == 6, f"Should have 6 unique domain keys, got {len(domain_keys)}"


def test_all_extensions_have_required_functions():
    """Test that all extensions implement required functions."""
    bundles = ['pm-dev-java', 'pm-dev-java-cui', 'pm-dev-frontend', 'pm-plugin-development', 'pm-requirements', 'pm-documents']
    required = ['is_applicable', 'provides_build_systems', 'get_command_mappings', 'get_skill_domains']

    for bundle in bundles:
        try:
            ext = load_extension(bundle)

            for func_name in required:
                assert hasattr(ext, func_name), f"{bundle}: missing required function {func_name}"
                assert callable(getattr(ext, func_name)), f"{bundle}: {func_name} is not callable"
        except FileNotFoundError:
            raise AssertionError(f"{bundle}: extension.py not found")


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # pm-dev-java tests
        test_java_extension_is_applicable_maven,
        test_java_extension_is_applicable_gradle,
        test_java_extension_is_applicable_negative,
        test_java_extension_provides_build_systems,
        test_java_extension_skill_domains_structure,
        test_java_extension_skill_references_exist,
        test_java_extension_command_mappings,
        test_java_extension_triage_reference,
        test_java_extension_get_modules,
        test_java_extension_get_module_type,
        test_java_extension_get_profiles,
        test_java_extension_generate_profile_command_maven,
        test_java_extension_generate_profile_command_gradle,
        test_java_extension_classify_profile,
        # pm-dev-frontend tests
        test_frontend_extension_is_applicable,
        test_frontend_extension_is_applicable_negative,
        test_frontend_extension_provides_build_systems,
        test_frontend_extension_skill_domains_structure,
        test_frontend_extension_skill_references_exist,
        test_frontend_extension_command_mappings,
        test_frontend_extension_triage_reference,
        test_frontend_extension_get_modules_workspaces,
        test_frontend_extension_get_profiles,
        test_frontend_extension_generate_profile_command,
        # pm-plugin-development tests
        test_plugin_dev_extension_is_applicable,
        test_plugin_dev_extension_is_applicable_negative,
        test_plugin_dev_extension_provides_build_systems,
        test_plugin_dev_extension_skill_domains_structure,
        test_plugin_dev_extension_skill_references_exist,
        test_plugin_dev_extension_command_mappings,
        test_plugin_dev_extension_triage_reference,
        test_plugin_dev_extension_outline_reference,
        # pm-requirements tests
        test_requirements_extension_is_applicable,
        test_requirements_extension_is_applicable_negative,
        test_requirements_extension_skill_domains_structure,
        test_requirements_extension_skill_references_exist,
        test_requirements_extension_triage_reference,
        # pm-documents tests
        test_documents_extension_is_applicable,
        test_documents_extension_is_applicable_negative,
        test_documents_extension_skill_domains_structure,
        test_documents_extension_skill_references_exist,
        test_documents_extension_triage_reference,
        # pm-dev-java-cui tests
        test_java_cui_extension_is_applicable,
        test_java_cui_extension_is_applicable_negative,
        test_java_cui_extension_provides_build_systems,
        test_java_cui_extension_skill_domains_structure,
        test_java_cui_extension_skill_references_exist,
        test_java_cui_extension_command_mappings,
        # Command template helper test
        test_build_command_template_helper,
        # Cross-bundle tests
        test_all_extensions_have_unique_domain_keys,
        test_all_extensions_have_required_functions,
    ])
    sys.exit(runner.run())
