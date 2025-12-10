#!/usr/bin/env python3
"""Unit tests for execute-script.py executor (template)."""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Path to templates and scripts
SKILL_DIR = Path(__file__).parent.parent.parent.parent / "marketplace/bundles/plan-marshall-core/skills/script-executor"
TEMPLATE_DIR = SKILL_DIR / "templates"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def load_executor_module():
    """Load the execute-script module from template for testing."""
    template_path = TEMPLATE_DIR / "execute-script.py.template"
    with open(template_path) as f:
        code = f.read()

    # Replace the placeholders with test values
    code = code.replace(
        '{{SCRIPT_MAPPINGS}}',
        '''
    "planning:manage-files": "/test/path/manage-files.py",
    "builder:builder-maven-rules": "/test/path/maven.py",
    "test:skill": "/test/path/test-skill.py",
'''
    )
    code = code.replace('{{EXECUTION_LOG_DIR}}', str(SCRIPTS_DIR))

    # Add scripts dir to path so execution_log can be imported
    sys.path.insert(0, str(SCRIPTS_DIR))

    # Create a module and provide __file__
    import types
    module = types.ModuleType('execute_script')
    module.__dict__['__file__'] = str(template_path)

    exec(code, module.__dict__)
    return module


# =============================================================================
# TESTS: resolve_notation
# =============================================================================

def test_resolve_exact_match():
    """Resolve exact notation match."""
    executor = load_executor_module()
    result = executor.resolve_notation('planning:manage-files')
    assert result == '/test/path/manage-files.py', f"Expected '/test/path/manage-files.py', got {result}"


def test_resolve_partial_match():
    """Resolve partial notation match."""
    executor = load_executor_module()
    result = executor.resolve_notation('planning')
    # Should find planning:manage-files
    assert result is not None, "Expected a result for partial match"
    assert 'manage-files' in result, f"Expected 'manage-files' in result, got {result}"


def test_resolve_unknown_notation():
    """Return None for unknown notation."""
    executor = load_executor_module()
    result = executor.resolve_notation('unknown:script')
    assert result is None, f"Expected None for unknown notation, got {result}"


def test_resolve_all_mappings():
    """All mappings are available in SCRIPTS dict."""
    executor = load_executor_module()
    assert 'planning:manage-files' in executor.SCRIPTS
    assert 'builder:builder-maven-rules' in executor.SCRIPTS
    assert 'test:skill' in executor.SCRIPTS


# =============================================================================
# TESTS: Script execution via subprocess
# =============================================================================

def test_successful_script_execution():
    """Successful script execution returns correct exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        test_script = Path(tmp) / 'test-script.py'
        test_script.write_text('''#!/usr/bin/env python3
import sys
print("Hello from test script")
print(f"Args: {sys.argv[1:]}")
sys.exit(0)
''')

        # Execute directly via subprocess
        result = subprocess.run(
            ['python3', str(test_script), 'arg1', 'arg2'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert 'Hello from test script' in result.stdout


def test_failed_script_returns_exit_code():
    """Failed script execution returns script's exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        test_script = Path(tmp) / 'test-script.py'
        test_script.write_text('''#!/usr/bin/env python3
import sys
print("Error occurred", file=sys.stderr)
sys.exit(42)
''')

        result = subprocess.run(
            ['python3', str(test_script)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 42, f"Expected exit code 42, got {result.returncode}"
        assert 'Error occurred' in result.stderr


def test_argument_forwarding():
    """Arguments are correctly forwarded to script."""
    with tempfile.TemporaryDirectory() as tmp:
        test_script = Path(tmp) / 'test-script.py'
        test_script.write_text('''#!/usr/bin/env python3
import sys
import json
print(json.dumps(sys.argv[1:]))
''')

        args = ['verb', '--plan-id', 'my-plan', '--flag', 'value']
        result = subprocess.run(
            ['python3', str(test_script)] + args,
            capture_output=True,
            text=True
        )

        import json
        received_args = json.loads(result.stdout.strip())
        assert received_args == args, f"Expected {args}, got {received_args}"


# =============================================================================
# TESTS: generate-executor.py script
# =============================================================================

def test_generate_script_help():
    """Generate script shows help."""
    script_path = SCRIPTS_DIR / "generate-executor.py"

    if script_path.exists():
        result = subprocess.run(
            ['python3', str(script_path), '--help'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert 'generate' in result.stdout, "Missing 'generate' subcommand in help"


def test_verify_script_help():
    """Verify script shows help."""
    script_path = SCRIPTS_DIR / "verify-executor.py"

    if script_path.exists():
        result = subprocess.run(
            ['python3', str(script_path), '--help'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert 'check' in result.stdout, "Missing 'check' subcommand in help"


if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_resolve_exact_match,
        test_resolve_partial_match,
        test_resolve_unknown_notation,
        test_resolve_all_mappings,
        test_successful_script_execution,
        test_failed_script_returns_exit_code,
        test_argument_forwarding,
        test_generate_script_help,
        test_verify_script_help,
    ])
    sys.exit(runner.run())
