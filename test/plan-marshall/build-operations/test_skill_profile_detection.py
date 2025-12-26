#!/usr/bin/env python3
"""Tests for skill profile auto-detection in build_env.py.

Tests skill domain detection via extension.py files:
- pm-documents detection when doc/ directory exists
- pm-requirements detection when Requirements.adoc exists
- Multiple profiles detected simultaneously
- Detection written to marshal.json detected_domains

Note: Skill domain detection happens via extension.py is_applicable() calls
during persist, not via detect-profiles (which is for Maven/Gradle profiles).
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
    """Context manager for skill profile detection tests."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        (self.temp_dir / '.plan').mkdir()
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def get_detected_domains(temp_dir: Path) -> list:
    """Read detected_domains from marshal.json."""
    marshal_path = temp_dir / '.plan' / 'marshal.json'
    if not marshal_path.exists():
        return []
    config = json.loads(marshal_path.read_text())
    return config.get('detected_domains', [])


def has_domain(domains: list, domain_name: str) -> bool:
    """Check if a domain is in the detected domains list.

    Handles new structure where domain is a dict: {'domain': {'key': '...', 'name': '...'}}
    """
    for d in domains:
        domain_data = d.get('domain', '')
        if isinstance(domain_data, dict):
            # New structure: domain is a dict with 'key' field
            if domain_data.get('key', '').lower() == domain_name.lower():
                return True
        elif isinstance(domain_data, str):
            # Old structure: domain is a string
            if domain_data.lower() == domain_name.lower():
                return True
    return False


# =============================================================================
# pm-documents Detection Tests
# =============================================================================

def test_detects_documents_with_doc_directory():
    """Test pm-documents is detected when doc/ directory exists."""
    with ProfileTestContext() as temp_dir:
        # Create doc/ directory
        (temp_dir / 'doc').mkdir()
        # Need at least one build file for persist to work
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        assert has_domain(domains, 'documentation'), \
            f"Should detect documentation domain: {domains}"


def test_no_documents_without_doc_directory():
    """Test pm-documents is not detected without doc/ directory."""
    with ProfileTestContext() as temp_dir:
        # No doc/ directory
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        assert not has_domain(domains, 'documentation'), \
            f"Should NOT detect documentation domain without doc/: {domains}"


# =============================================================================
# pm-requirements Detection Tests
# =============================================================================

def test_detects_requirements_with_requirements_adoc():
    """Test pm-requirements is detected when Requirements.adoc exists."""
    with ProfileTestContext() as temp_dir:
        # Create Requirements.adoc
        (temp_dir / 'Requirements.adoc').write_text('= Requirements')
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        assert has_domain(domains, 'requirements'), \
            f"Should detect requirements domain: {domains}"


def test_detects_requirements_in_doc_spec():
    """Test pm-requirements is detected when doc/spec/Requirements.adoc exists."""
    with ProfileTestContext() as temp_dir:
        # Create doc/spec/Requirements.adoc
        (temp_dir / 'doc' / 'spec').mkdir(parents=True)
        (temp_dir / 'doc' / 'spec' / 'Requirements.adoc').write_text('= Requirements')
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        assert has_domain(domains, 'requirements'), \
            f"Should detect requirements domain: {domains}"


def test_no_requirements_without_requirements_adoc():
    """Test pm-requirements is not detected without Requirements.adoc."""
    with ProfileTestContext() as temp_dir:
        # No Requirements.adoc
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        assert not has_domain(domains, 'requirements'), \
            f"Should NOT detect requirements domain: {domains}"


# =============================================================================
# Multiple Profile Detection Tests
# =============================================================================

def test_detects_multiple_profiles():
    """Test multiple skill profiles are detected simultaneously."""
    with ProfileTestContext() as temp_dir:
        # Create structures for multiple profiles
        (temp_dir / 'doc').mkdir()  # pm-documents
        (temp_dir / 'Requirements.adoc').write_text('= Requirements')  # pm-requirements
        (temp_dir / 'pom.xml').write_text('<project></project>')  # pm-dev-java

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        assert has_domain(domains, 'java'), f"Should detect java domain: {domains}"
        assert has_domain(domains, 'documentation'), f"Should detect documentation domain: {domains}"
        assert has_domain(domains, 'requirements'), f"Should detect requirements domain: {domains}"


def test_detects_java_and_frontend_profiles():
    """Test Java and frontend profiles detected for hybrid project."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('<project></project>')
        (temp_dir / 'package.json').write_text('{"name": "test"}')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        assert has_domain(domains, 'java'), f"Should detect java domain: {domains}"
        assert has_domain(domains, 'javascript'), f"Should detect javascript domain: {domains}"


# =============================================================================
# Domain Structure Tests
# =============================================================================

def test_detected_domain_includes_profiles():
    """Test detected domains include skill profiles."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        # New structure: domain is a dict with 'key' field
        java_domain = next((d for d in domains
                           if isinstance(d.get('domain'), dict) and d['domain'].get('key') == 'java'), None)

        assert java_domain is not None, f"Should have java domain: {domains}"
        assert 'profiles' in java_domain, f"Should have profiles: {java_domain}"

        profiles = java_domain['profiles']
        assert 'core' in profiles, f"Should have core profile: {profiles}"
        assert 'testing' in profiles, f"Should have testing profile: {profiles}"


def test_detected_domain_includes_bundle():
    """Test detected domains include bundle name."""
    with ProfileTestContext() as temp_dir:
        (temp_dir / 'pom.xml').write_text('<project></project>')

        result = run_script(
            SCRIPT_PATH,
            'persist',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        domains = get_detected_domains(temp_dir)
        # New structure: domain is a dict with 'key' field
        java_domain = next((d for d in domains
                           if isinstance(d.get('domain'), dict) and d['domain'].get('key') == 'java'), None)

        assert java_domain is not None, f"Should have java domain: {domains}"
        assert java_domain.get('bundle') == 'pm-dev-java', \
            f"Should have pm-dev-java bundle: {java_domain}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_detects_documents_with_doc_directory,
        test_no_documents_without_doc_directory,
        test_detects_requirements_with_requirements_adoc,
        test_detects_requirements_in_doc_spec,
        test_no_requirements_without_requirements_adoc,
        test_detects_multiple_profiles,
        test_detects_java_and_frontend_profiles,
        test_detected_domain_includes_profiles,
        test_detected_domain_includes_bundle,
    ])
    sys.exit(runner.run())
