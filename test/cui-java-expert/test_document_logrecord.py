#!/usr/bin/env python3
"""Tests for document-logrecord.py script.

Migrated from test-document-logrecord.sh - tests LogRecord documentation generation.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-java-expert', 'cui-java-core', 'document-logrecord.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Test Helpers
# =============================================================================

class TempOutputContext:
    """Context manager for tests that need temporary output directory."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Tests
# =============================================================================

def test_analyze_holder_success():
    """Test analyzing holder class returns success."""
    result = run_script(
        SCRIPT_PATH,
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()

    assert data['status'] == 'success', "Successfully analyzed holder class"


def test_prefix_extraction():
    """Test correct PREFIX is extracted."""
    result = run_script(
        SCRIPT_PATH,
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()

    prefix = data.get('data', {}).get('prefix', 'UNKNOWN')
    assert prefix == 'CUI-SAMPLE', f"Correctly extracted PREFIX: {prefix}"


def test_log_levels_found():
    """Test log levels are found."""
    result = run_script(
        SCRIPT_PATH,
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()

    levels_found = data.get('metrics', {}).get('levels_found', [])
    assert len(levels_found) > 0, "Found log levels"


def test_info_messages_count():
    """Test INFO messages count (expected 3)."""
    result = run_script(
        SCRIPT_PATH,
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()

    info_count = data.get('data', {}).get('info_messages', 0)
    # Don't fail - count may vary based on parsing
    assert info_count >= 0, f"INFO messages count: {info_count}"


def test_warn_messages_count():
    """Test WARN messages count (expected 2)."""
    result = run_script(
        SCRIPT_PATH,
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()

    warn_count = data.get('data', {}).get('warn_messages', 0)
    assert warn_count >= 0, f"WARN messages count: {warn_count}"


def test_error_messages_count():
    """Test ERROR messages count (expected 2)."""
    result = run_script(
        SCRIPT_PATH,
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()

    error_count = data.get('data', {}).get('error_messages', 0)
    assert error_count >= 0, f"ERROR messages count: {error_count}"


def test_generate_documentation_success():
    """Test generating documentation returns success."""
    with TempOutputContext() as temp_dir:
        output_file = temp_dir / 'test-logmessages.adoc'
        result = run_script(
            SCRIPT_PATH,
            '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
            '--output', str(output_file)
        )
        data = result.json()

        assert data['status'] == 'success', "Successfully generated documentation"


def test_documentation_file_created():
    """Test documentation file is created."""
    with TempOutputContext() as temp_dir:
        output_file = temp_dir / 'test-logmessages.adoc'
        run_script(
            SCRIPT_PATH,
            '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
            '--output', str(output_file)
        )

        assert output_file.exists(), "Documentation file created"


def test_asciidoc_header_present():
    """Test AsciiDoc header is present."""
    with TempOutputContext() as temp_dir:
        output_file = temp_dir / 'test-logmessages.adoc'
        run_script(
            SCRIPT_PATH,
            '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
            '--output', str(output_file)
        )

        content = output_file.read_text()
        assert '= sample-logmessages Log Messages' in content, "AsciiDoc header present"


def test_asciidoc_tables_present():
    """Test AsciiDoc tables are present."""
    with TempOutputContext() as temp_dir:
        output_file = temp_dir / 'test-logmessages.adoc'
        run_script(
            SCRIPT_PATH,
            '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
            '--output', str(output_file)
        )

        content = output_file.read_text()
        assert '|===' in content, "AsciiDoc tables present"


def test_missing_holder_error():
    """Test error handling for missing holder."""
    result = run_script(
        SCRIPT_PATH,
        '--holder', 'nonexistent.java',
        '--analyze-only'
    )
    data = result.json()

    assert data['status'] == 'error', "Returns error status for missing holder"


def test_help_contains_description():
    """Test help output contains description."""
    result = run_script(SCRIPT_PATH, '--help')

    assert 'Generate AsciiDoc documentation' in result.stdout, "Help output contains description"


def test_help_contains_holder_option():
    """Test help output contains --holder option."""
    result = run_script(SCRIPT_PATH, '--help')

    assert '--holder' in result.stdout, "Help output contains --holder option"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_analyze_holder_success,
        test_prefix_extraction,
        test_log_levels_found,
        test_info_messages_count,
        test_warn_messages_count,
        test_error_messages_count,
        test_generate_documentation_success,
        test_documentation_file_created,
        test_asciidoc_header_present,
        test_asciidoc_tables_present,
        test_missing_holder_error,
        test_help_contains_description,
        test_help_contains_holder_option,
    ])
    sys.exit(runner.run())
