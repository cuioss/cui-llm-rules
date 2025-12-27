#!/usr/bin/env python3
"""Tests for manage_project_structure.py script.

Tests project structure operations including read, generate, validate,
module commands, placement commands, and more.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, PlanTestContext

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'project-structure', 'manage_project_structure.py')


def create_marshal_json(fixture_dir: Path, modules: dict = None) -> Path:
    """Create marshal.json with module configuration."""
    if modules is None:
        modules = {
            "default": {
                "path": ".",
                "domains": ["java"],
                "build_systems": ["maven"]
            },
            "my-core": {
                "path": "my-core",
                "domains": ["java"],
                "build_systems": ["maven"]
            },
            "my-ui": {
                "path": "my-ui",
                "domains": ["java", "javascript"],
                "build_systems": ["maven", "npm"]
            },
            "integration-testing": {
                "path": "integration-testing",
                "domains": ["java"],
                "build_systems": ["maven"]
            }
        }

    config = {
        "skill_domains": {
            "java": {"defaults": ["pm-dev-java:java-core"]}
        },
        "modules": modules,
        "system": {"retention": {"logs_days": 1}}
    }
    marshal_path = fixture_dir / 'marshal.json'
    marshal_path.write_text(json.dumps(config, indent=2))
    return marshal_path


def create_project_structure(fixture_dir: Path, structure: dict = None) -> Path:
    """Create project-structure.toon with sample content.

    Note: Uses explicit array syntax [N]{fields}: for uniform arrays
    because the TOON parser has issues with nested - list syntax.
    """
    if structure is None:
        content = """modules:
  my-core:
    responsibility: Core business logic
    layer: service
    technology:
      framework: quarkus
      di: cdi
      testing: junit5
    key_packages[1]{value}:
    com.example.core
    tips[1]{value}:
    Use @ApplicationScoped
    insights[1]{value}:
    Heavy validation in boundary
    best_practices[1]{value}:
    One service per file

  my-ui:
    responsibility: User interface components
    layer: presentation
    technology:
      framework: angular
      testing: jest
    key_packages[1]{value}:
    src/main/webapp

dependencies:
  module_deps:
    my-ui[1]{value}:
    my-core
  layer_rules:
    presentation:
      allowed[1]{value}:
      service
      forbidden[1]{value}:
      testing

placement:
  service:
    module: my-core
    package: com.example.core.{feature}
    pattern: "{Name}Service.java"
    test_pattern: "{Name}ServiceTest.java"

conventions:
  naming[1]{value}:
  "Services: {Name}Service"
  packages[1]{value}:
  "com.example.core.{feature}"
  testing[1]{value}:
  Unit tests in same module
  documentation[1]{value}:
  JavaDoc on public classes
"""
    else:
        # Simple serialization for tests
        content = ""
        for key, value in structure.items():
            content += f"{key}: {value}\n"

    structure_path = fixture_dir / 'project-structure.toon'
    structure_path.write_text(content)
    return structure_path


# =============================================================================
# read Command Tests
# =============================================================================

def test_read_existing_structure():
    """Test reading existing project-structure.toon."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'read')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout
        assert 'responsibility' in result.stdout


def test_read_generates_if_missing():
    """Test read auto-generates structure when missing."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'read')

        assert result.success, f"Should succeed: {result.stderr}"
        # Should have generated modules from marshal.json
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout

        # File should now exist
        structure_path = ctx.fixture_dir / 'project-structure.toon'
        assert structure_path.exists()


def test_read_fails_without_marshal():
    """Test read fails when no marshal.json exists."""
    with PlanTestContext() as ctx:
        # Don't create marshal.json or structure
        result = run_script(SCRIPT_PATH, 'read')

        assert 'error' in result.stdout.lower()
        assert 'marshal.json' in result.stdout.lower()


# =============================================================================
# generate Command Tests
# =============================================================================

def test_generate_creates_structure():
    """Test generate creates structure from marshal.json."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'modules_generated' in result.stdout

        # Verify file created
        structure_path = ctx.fixture_dir / 'project-structure.toon'
        assert structure_path.exists()


def test_generate_infers_layers():
    """Test generate infers layers from module names."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir, modules={
            "my-ui": {"path": "my-ui", "build_systems": ["maven"]},
            "my-api": {"path": "my-api", "build_systems": ["maven"]},
            "integration-testing": {"path": "integration-testing", "build_systems": ["maven"]}
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        assert 'presentation' in content  # my-ui -> presentation
        assert 'api' in content  # my-api -> api
        assert 'testing' in content  # integration-testing -> testing


def test_generate_fails_if_exists():
    """Test generate fails when structure exists without --force."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'generate')

        assert 'error' in result.stdout.lower()
        assert 'exists' in result.stdout.lower() or 'force' in result.stdout.lower()


def test_generate_force_overwrites():
    """Test generate --force overwrites existing structure."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'generate', '--force')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'modules_generated' in result.stdout


# =============================================================================
# validate Command Tests
# =============================================================================

def test_validate_valid_structure():
    """Test validate passes for valid structure."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'validate')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'modules_count' in result.stdout


def test_validate_reports_warnings():
    """Test validate reports warnings for incomplete modules."""
    with PlanTestContext() as ctx:
        # Create structure with missing responsibility
        content = """modules:
  incomplete-module:
    layer: service
"""
        (ctx.fixture_dir / 'project-structure.toon').write_text(content)

        result = run_script(SCRIPT_PATH, 'validate')

        assert result.success  # Validation passes but with warnings
        assert 'warning' in result.stdout.lower() or 'responsibility' in result.stdout.lower()


# =============================================================================
# module Command Tests
# =============================================================================

def test_module_get():
    """Test module get returns module metadata."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'module', 'get', '--module', 'my-core')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'responsibility' in result.stdout
        assert 'Core business logic' in result.stdout


def test_module_get_unknown():
    """Test module get fails for unknown module."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'module', 'get', '--module', 'nonexistent')

        assert 'error' in result.stdout.lower()
        assert 'nonexistent' in result.stdout


def test_module_list():
    """Test module list returns all modules."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'module', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout


def test_module_update():
    """Test module update modifies metadata."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'module', 'update',
            '--module', 'my-core',
            '--responsibility', 'Updated responsibility',
            '--layer', 'extension'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify update persisted
        verify = run_script(SCRIPT_PATH, 'module', 'get', '--module', 'my-core')
        assert 'Updated responsibility' in verify.stdout
        assert 'extension' in verify.stdout


def test_module_add_tip():
    """Test module add-tip adds implementation tip."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'module', 'add-tip',
            '--module', 'my-core',
            '--tip', 'New implementation tip'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'tip_added' in result.stdout


def test_module_add_insight():
    """Test module add-insight adds learned insight."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'module', 'add-insight',
            '--module', 'my-core',
            '--insight', 'New learned insight'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'insight_added' in result.stdout


def test_module_set_technology():
    """Test module set-technology updates tech stack."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'module', 'set-technology',
            '--module', 'my-core',
            '--framework', 'spring',
            '--di', 'spring'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        verify = run_script(SCRIPT_PATH, 'module', 'get', '--module', 'my-core')
        assert 'spring' in verify.stdout


def test_module_add_package():
    """Test module add-package adds key package."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'module', 'add-package',
            '--module', 'my-core',
            '--package', 'com.example.newpackage'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'package_added' in result.stdout


# =============================================================================
# placement Command Tests
# =============================================================================

def test_placement_query():
    """Test placement query returns rule."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'placement', 'query',
            '--component-type', 'service'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'my-core' in result.stdout
        assert 'pattern' in result.stdout


def test_placement_query_unknown():
    """Test placement query fails for unknown type."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'placement', 'query',
            '--component-type', 'nonexistent'
        )

        assert 'error' in result.stdout.lower()


def test_placement_list():
    """Test placement list returns all rules."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'placement', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'service' in result.stdout


def test_placement_set():
    """Test placement set creates new rule."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'placement', 'set',
            '--component-type', 'processor',
            '--module', 'my-core',
            '--package', 'com.example.processors.{feature}',
            '--pattern', '{Name}Processor.java',
            '--test-pattern', '{Name}ProcessorTest.java'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify rule created
        verify = run_script(
            SCRIPT_PATH, 'placement', 'query',
            '--component-type', 'processor'
        )
        assert 'my-core' in verify.stdout
        assert 'Processor' in verify.stdout


# =============================================================================
# convention Command Tests
# =============================================================================

def test_convention_list():
    """Test convention list returns all conventions."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'convention', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'naming' in result.stdout


def test_convention_add():
    """Test convention add creates new convention."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'convention', 'add',
            '--category', 'naming',
            '--convention', 'Controllers: {Name}Controller'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'convention_added' in result.stdout


# =============================================================================
# dependency Command Tests
# =============================================================================

def test_dependency_list():
    """Test dependency list returns dependencies."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'dependency', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'module_deps' in result.stdout


def test_dependency_add():
    """Test dependency add creates module dependency."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'dependency', 'add',
            '--from-module', 'my-core',
            '--to-module', 'my-api'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify dependency added
        verify = run_script(SCRIPT_PATH, 'dependency', 'list')
        assert 'my-core' in verify.stdout


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # read tests
        test_read_existing_structure,
        test_read_generates_if_missing,
        test_read_fails_without_marshal,
        # generate tests
        test_generate_creates_structure,
        test_generate_infers_layers,
        test_generate_fails_if_exists,
        test_generate_force_overwrites,
        # validate tests
        test_validate_valid_structure,
        test_validate_reports_warnings,
        # module tests
        test_module_get,
        test_module_get_unknown,
        test_module_list,
        test_module_update,
        test_module_add_tip,
        test_module_add_insight,
        test_module_set_technology,
        test_module_add_package,
        # placement tests
        test_placement_query,
        test_placement_query_unknown,
        test_placement_list,
        test_placement_set,
        # convention tests
        test_convention_list,
        test_convention_add,
        # dependency tests
        test_dependency_list,
        test_dependency_add,
    ])
    sys.exit(runner.run())
