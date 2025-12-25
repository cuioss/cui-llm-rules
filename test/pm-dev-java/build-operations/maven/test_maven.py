#!/usr/bin/env python3
"""Tests for pm-dev-java:build-operations Maven scripts.

Tests all Maven build operations:
- execute: Execute Maven builds
- parse: Parse Maven build output
- find-module: Find Maven module paths
- search-markers: Search OpenRewrite markers
- check-warnings: Categorize build warnings
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test - pm-dev-java bundle
SCRIPT_PATH = get_script_path('pm-dev-java', 'build-operations', 'maven.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'
MOCKS_DIR = Path(__file__).parent / 'mocks'


class TempDirContext:
    """Context manager for tests that need a temporary directory."""

    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Execute Subcommand Tests
# =============================================================================

def test_execute_successful_build():
    """Test successful Maven build."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--goals', 'clean install',
            '--mvnw', str(MOCKS_DIR / 'mvnw-success.sh')
        )

        assert result.returncode == 0, f"Successful build should exit with 0, got {result.returncode}"
        data = result.json()
        assert data['status'] == 'success', "Status should be success"
        assert data['data']['exit_code'] == 0, "Exit code should be 0"
        assert 'log_file' in data['data'], "Output should contain log_file"


def test_execute_failed_build():
    """Test failed Maven build."""
    with TempDirContext():
        result = run_script(
            SCRIPT_PATH,
            'execute',
            '--goals', 'clean install',
            '--mvnw', str(MOCKS_DIR / 'mvnw-failure.sh')
        )

        assert result.returncode == 1, "Failed build should exit with 1"
        data = result.json()
        assert data['status'] == 'error', "Status should be error"
        assert data['error'] == 'build_failed', "Error type should be build_failed"


# =============================================================================
# Parse Subcommand Tests
# =============================================================================

def test_parse_successful_build():
    """Test parsing successful Maven build output."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-maven-success.log'),
        '--mode', 'structured'
    )
    assert result.success, f"Script failed: {result.stderr}"
    data = result.json()

    assert data['status'] == 'success', "Status should be success"
    assert data['data']['build_status'] == 'SUCCESS', "Build status should be SUCCESS"


def test_parse_compilation_errors():
    """Test parsing build with compilation errors."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', str(FIXTURES_DIR / 'sample-maven-failure.log'),
        '--mode', 'structured'
    )
    data = result.json()

    assert data['data']['build_status'] == 'FAILURE', "Build status should be FAILURE"
    assert data['data']['summary'].get('compilation_errors', 0) > 0, "Should detect compilation errors"


def test_parse_missing_file():
    """Test missing file handling."""
    result = run_script(
        SCRIPT_PATH,
        'parse',
        '--log', 'nonexistent.log',
        '--mode', 'structured'
    )
    data = result.json()

    assert data['status'] == 'error', "Should return error status for missing file"


# =============================================================================
# Find-Module Subcommand Tests
# =============================================================================

def test_find_module_by_artifact_id():
    """Test finding module by artifactId."""
    with TempDirContext() as temp_dir:
        module_dir = temp_dir / 'modules' / 'auth-service'
        module_dir.mkdir(parents=True)
        pom = module_dir / 'pom.xml'
        pom.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>auth-service</artifactId>
    <version>1.0.0</version>
</project>''')

        result = run_script(
            SCRIPT_PATH,
            'find-module',
            '--artifact-id', 'auth-service',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'success', f"Should find module: {data}"
        assert 'auth-service' in data['data']['module_path'], "Module path should contain auth-service"


def test_find_module_not_found():
    """Test finding non-existent module."""
    with TempDirContext() as temp_dir:
        result = run_script(
            SCRIPT_PATH,
            'find-module',
            '--artifact-id', 'nonexistent',
            '--root', str(temp_dir)
        )
        data = result.json()

        assert data['status'] == 'error', "Should return error for non-existent module"


# =============================================================================
# Search-Markers Subcommand Tests
# =============================================================================

def test_search_markers_no_markers():
    """Test searching when no markers exist."""
    with TempDirContext() as temp_dir:
        src_dir = temp_dir / 'src' / 'main' / 'java'
        src_dir.mkdir(parents=True)
        java_file = src_dir / 'Test.java'
        java_file.write_text('public class Test {}')

        result = run_script(
            SCRIPT_PATH,
            'search-markers',
            '--source-dir', str(temp_dir / 'src')
        )
        data = result.json()

        assert data['status'] == 'success', "Should succeed with no markers"
        assert data['data']['total_markers'] == 0, "Should find no markers"


# =============================================================================
# Check-Warnings Subcommand Tests
# =============================================================================

def test_check_warnings_empty():
    """Test with no warnings."""
    warnings = json.dumps([])
    acceptable = json.dumps({})

    result = run_script(
        SCRIPT_PATH,
        'check-warnings',
        '--warnings', warnings,
        '--acceptable-warnings', acceptable
    )
    data = result.json()

    assert data['success'] is True, "Should succeed with no warnings"
    assert data['total'] == 0, "Total should be 0"


# =============================================================================
# Help Tests
# =============================================================================

def test_help_main():
    """Test main --help output."""
    result = run_script(SCRIPT_PATH, '--help')
    assert 'execute' in result.stdout, "Should show execute subcommand"
    assert 'parse' in result.stdout, "Should show parse subcommand"
    assert 'find-module' in result.stdout, "Should show find-module subcommand"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_execute_successful_build,
        test_execute_failed_build,
        test_parse_successful_build,
        test_parse_compilation_errors,
        test_parse_missing_file,
        test_find_module_by_artifact_id,
        test_find_module_not_found,
        test_search_markers_no_markers,
        test_check_warnings_empty,
        test_help_main,
    ])
    sys.exit(runner.run())
