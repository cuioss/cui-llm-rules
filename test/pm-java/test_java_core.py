#!/usr/bin/env python3
"""Tests for java-core.py - consolidated Java core analysis tools.

Consolidates tests from:
- test_analyze_logging_violations.py (analyze-logging subcommand)
- test_document_logrecord.py (document-logrecord subcommand)
- test_verify_implementation_params.py (verify-params subcommand)
"""

import shutil
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('pm-java', 'cui-java-core', 'java-core.py')
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


# =============================================================================
# Main help tests
# =============================================================================

def test_script_exists():
    """Test that the script exists."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"


def test_main_help():
    """Test main --help displays all subcommands."""
    result = run_script(SCRIPT_PATH, '--help')
    combined = result.stdout + result.stderr
    assert 'analyze-logging' in combined, "analyze-logging subcommand in help"
    assert 'document-logrecord' in combined, "document-logrecord subcommand in help"
    assert 'verify-params' in combined, "verify-params subcommand in help"


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
# Analyze-logging subcommand tests
# =============================================================================

def test_analyze_logging_help():
    """Test analyze-logging --help displays usage."""
    result = run_script(SCRIPT_PATH, 'analyze-logging', '--help')
    combined = result.stdout + result.stderr
    assert 'usage' in combined.lower(), "Analyze-logging help not shown"


def test_analyze_compliant_file():
    """Test analyzing compliant logging file returns success."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-compliant.java')
    )
    data = result.json()
    assert data['status'] == 'success', "Successfully analyzed compliant file"


def test_compliant_file_no_violations():
    """Test compliant file has no violations."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-compliant.java')
    )
    data = result.json()
    violation_count = data.get('metrics', {}).get('total_violations', 0)
    assert violation_count == 0, f"Compliant file should have no violations, found: {violation_count}"


def test_violation_file_success_status():
    """Test analyzing violations file returns success status (script runs, finds violations)."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()
    assert data['status'] == 'success', "Successfully analyzed violations file"


def test_violations_detected():
    """Test violations are detected in non-compliant file."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()
    violation_count = data.get('metrics', {}).get('total_violations', 0)
    assert violation_count > 0, f"Should have detected violations, found: {violation_count}"


def test_missing_log_record_violations():
    """Test MISSING_LOG_RECORD violations are detected."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()
    missing_count = data.get('data', {}).get('summary', {}).get('missing_log_record', 0)
    assert missing_count > 0, f"Should have detected MISSING_LOG_RECORD violations: {missing_count}"


def test_violation_has_file_field():
    """Test violation has file field."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()
    violations = data.get('data', {}).get('violations', [])
    if violations:
        assert 'file' in violations[0], "Violation has file field"


def test_violation_has_line_field():
    """Test violation has numeric line field."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()
    violations = data.get('data', {}).get('violations', [])
    if violations:
        line = violations[0].get('line')
        assert isinstance(line, int), "Violation has numeric line field"


def test_violation_has_type_field():
    """Test violation has violation_type field."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-violations.java')
    )
    data = result.json()
    violations = data.get('data', {}).get('violations', [])
    if violations:
        assert 'violation_type' in violations[0], "Violation has violation_type field"


def test_analyze_logging_missing_file_error():
    """Test error handling for missing file."""
    result = run_script(SCRIPT_PATH, 'analyze-logging', '--file', 'nonexistent.java')
    data = result.json()
    assert data['status'] == 'error', "Returns error status for missing file"


def test_analyze_logging_missing_arguments_error():
    """Test error handling for missing arguments."""
    result = run_script(SCRIPT_PATH, 'analyze-logging')
    data = result.json()
    assert data['status'] == 'error', "Returns error when no arguments provided"


def test_compliant_file_compliance_rate():
    """Test compliance rate calculation for compliant file."""
    result = run_script(
        SCRIPT_PATH,
        'analyze-logging',
        '--file', str(FIXTURES_DIR / 'sample-logging-compliant.java')
    )
    data = result.json()
    compliance_rate = data.get('metrics', {}).get('compliance_rate', 0)
    assert compliance_rate >= 0, f"Compliance rate should be non-negative: {compliance_rate}"


# =============================================================================
# Document-logrecord subcommand tests
# =============================================================================

def test_document_logrecord_help():
    """Test document-logrecord --help displays usage."""
    result = run_script(SCRIPT_PATH, 'document-logrecord', '--help')
    combined = result.stdout + result.stderr
    assert '--holder' in combined, "Help output contains --holder option"


def test_analyze_holder_success():
    """Test analyzing holder class returns success."""
    result = run_script(
        SCRIPT_PATH,
        'document-logrecord',
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()
    assert data['status'] == 'success', "Successfully analyzed holder class"


def test_prefix_extraction():
    """Test correct PREFIX is extracted."""
    result = run_script(
        SCRIPT_PATH,
        'document-logrecord',
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
        'document-logrecord',
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()
    levels_found = data.get('metrics', {}).get('levels_found', [])
    assert len(levels_found) > 0, "Found log levels"


def test_info_messages_count():
    """Test INFO messages count."""
    result = run_script(
        SCRIPT_PATH,
        'document-logrecord',
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()
    info_count = data.get('data', {}).get('info_messages', 0)
    assert info_count >= 0, f"INFO messages count: {info_count}"


def test_warn_messages_count():
    """Test WARN messages count."""
    result = run_script(
        SCRIPT_PATH,
        'document-logrecord',
        '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
        '--analyze-only'
    )
    data = result.json()
    warn_count = data.get('data', {}).get('warn_messages', 0)
    assert warn_count >= 0, f"WARN messages count: {warn_count}"


def test_error_messages_count():
    """Test ERROR messages count."""
    result = run_script(
        SCRIPT_PATH,
        'document-logrecord',
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
            'document-logrecord',
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
            'document-logrecord',
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
            'document-logrecord',
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
            'document-logrecord',
            '--holder', str(FIXTURES_DIR / 'sample-logmessages.java'),
            '--output', str(output_file)
        )
        content = output_file.read_text()
        assert '|===' in content, "AsciiDoc tables present"


def test_missing_holder_error():
    """Test error handling for missing holder."""
    result = run_script(
        SCRIPT_PATH,
        'document-logrecord',
        '--holder', 'nonexistent.java',
        '--analyze-only'
    )
    data = result.json()
    assert data['status'] == 'error', "Returns error status for missing holder"


# =============================================================================
# Verify-params subcommand tests
# =============================================================================

def test_verify_params_help():
    """Test verify-params --help displays usage."""
    result = run_script(SCRIPT_PATH, 'verify-params', '--help')
    combined = result.stdout + result.stderr
    assert '--description' in combined, "Help output contains --description option"


def test_clear_description_passes():
    """Test clear task description passes validation."""
    description = "Add JWT token validation to the authentication service. The validator should check token expiry, issuer, and signature using RS256 algorithm."
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    assert data.get('data', {}).get('verification_passed') is True, \
        "Clear description passes validation"


def test_clear_description_high_score():
    """Test clear description has high clarity score."""
    description = "Add JWT token validation to the authentication service. The validator should check token expiry, issuer, and signature using RS256 algorithm."
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    score = data.get('data', {}).get('clarity_score', 0)
    assert score >= 70, f"Clarity score is high: {score}"


def test_vague_description_fails():
    """Test vague description fails validation."""
    description = "Fix the thing"
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    assert data.get('data', {}).get('verification_passed') is False, \
        "Vague description fails validation"


def test_vague_scope_detected():
    """Test vague scope is detected."""
    description = "Fix the thing"
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    assert data.get('data', {}).get('vague_scope') is True, "Vague scope detected"


def test_ambiguities_detected():
    """Test ambiguous requirements are detected."""
    description = "Add validation to the service. It should probably optionally validate tokens."
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    ambiguities = data.get('data', {}).get('ambiguities', [])
    assert len(ambiguities) > 0, "Ambiguities detected"


def test_missing_information_identified():
    """Test missing information is identified or verification fails."""
    description = "Update the authentication"
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    missing_info = data.get('data', {}).get('missing_information', [])
    verification_passed = data.get('data', {}).get('verification_passed', True)
    assert len(missing_info) > 0 or not verification_passed, \
        "Missing information identified or verification failed"


def test_missing_info_fails_validation():
    """Test missing information fails validation."""
    description = "Update the authentication"
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    assert data.get('data', {}).get('verification_passed') is False, \
        "Fails validation due to missing info"


def test_json_top_level_fields():
    """Test JSON has required top-level fields."""
    description = "Add token validation"
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    assert 'status' in data and 'data' in data, "JSON has required top-level fields"


def test_json_data_structure():
    """Test JSON data has required fields."""
    description = "Add token validation"
    result = run_script(SCRIPT_PATH, 'verify-params', '--description', description)
    data = result.json()
    data_section = data.get('data', {})
    assert 'verification_passed' in data_section and 'clarity_score' in data_section, \
        "JSON data has required fields"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Main tests
        test_script_exists,
        test_main_help,
        # Analyze-logging tests
        test_analyze_logging_help,
        test_analyze_compliant_file,
        test_compliant_file_no_violations,
        test_violation_file_success_status,
        test_violations_detected,
        test_missing_log_record_violations,
        test_violation_has_file_field,
        test_violation_has_line_field,
        test_violation_has_type_field,
        test_analyze_logging_missing_file_error,
        test_analyze_logging_missing_arguments_error,
        test_compliant_file_compliance_rate,
        # Document-logrecord tests
        test_document_logrecord_help,
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
        # Verify-params tests
        test_verify_params_help,
        test_clear_description_passes,
        test_clear_description_high_score,
        test_vague_description_fails,
        test_vague_scope_detected,
        test_ambiguities_detected,
        test_missing_information_identified,
        test_missing_info_fails_validation,
        test_json_top_level_fields,
        test_json_data_structure,
    ])
    sys.exit(runner.run())
