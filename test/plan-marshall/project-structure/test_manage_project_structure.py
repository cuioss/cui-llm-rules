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


def create_marshal_json(fixture_dir: Path, module_config: dict = None) -> Path:
    """Create marshal.json with module_config for command configuration.

    Note: Module facts (name, path, build_systems) are now discovered from
    the filesystem by collect_raw_project_data and stored in raw-project-data.json.
    This function only sets up module_config for commands.
    """
    if module_config is None:
        module_config = {
            "default": {
                "commands": {
                    "test": "mvn test",
                    "verify": "mvn verify"
                }
            }
        }

    config = {
        "skill_domains": {
            "java": {"defaults": ["pm-dev-java:java-core"]}
        },
        "module_config": module_config,
        "system": {"retention": {"logs_days": 1}}
    }
    marshal_path = fixture_dir / 'marshal.json'
    marshal_path.write_text(json.dumps(config, indent=2))
    return marshal_path


def create_raw_project_data(fixture_dir: Path, modules: list = None,
                            module_details: dict = None) -> Path:
    """Create raw-project-data.json with module facts.

    Args:
        fixture_dir: Directory to create file in (the .plan subdir).
        modules: List of module dicts with name, path, build_systems, packaging.
        module_details: Dict of module name -> details (packages, dependencies, etc).

    Returns:
        Path to created raw-project-data.json.
    """
    if modules is None:
        modules = [
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "my-ui", "path": "my-ui", "build_systems": ["maven"], "packaging": "jar"}
        ]

    if module_details is None:
        module_details = {}

    data = {
        "project": {
            "root": str(fixture_dir.parent),
            "name": fixture_dir.parent.name
        },
        "frameworks": [],
        "documentation": {
            "readme": "",
            "doc_files": []
        },
        "modules": modules,
        "module_details": module_details
    }
    raw_data_path = fixture_dir / 'raw-project-data.json'
    raw_data_path.write_text(json.dumps(data, indent=2))
    return raw_data_path


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
        # Create raw-project-data.json with module facts
        create_raw_project_data(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'read')

        assert result.success, f"Should succeed: {result.stderr}"
        # Should have generated modules from raw-project-data.json
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout

        # File should now exist
        structure_path = ctx.fixture_dir / 'project-structure.toon'
        assert structure_path.exists()


def test_read_fails_without_data():
    """Test read fails when no raw-project-data.json exists."""
    with PlanTestContext() as ctx:
        # Don't create raw-project-data.json or structure
        result = run_script(SCRIPT_PATH, 'read')

        assert 'error' in result.stdout.lower()
        # Should mention collect-raw-data command
        assert 'collect-raw-data' in result.stdout.lower() or 'no module data' in result.stdout.lower()


# =============================================================================
# generate Command Tests
# =============================================================================

def test_generate_creates_structure():
    """Test generate creates structure from raw-project-data.json."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        create_raw_project_data(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'modules_generated' in result.stdout

        # Verify file created
        structure_path = ctx.fixture_dir / 'project-structure.toon'
        assert structure_path.exists()


def test_generate_infers_layers():
    """Test generate infers layers from module names."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with module facts
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-ui", "path": "my-ui", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "my-api", "path": "my-api", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "integration-testing", "path": "integration-testing", "build_systems": ["maven"], "packaging": "jar"}
        ])

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        assert 'presentation' in content  # my-ui -> presentation
        assert 'api' in content  # my-api -> api
        assert 'testing' in content  # integration-testing -> testing


def test_generate_core_does_not_infer_service():
    """Test generate does NOT map *-core to service layer.

    *-core modules require LLM analysis to determine if they're 'library'.
    Script inference should NOT output a layer for unknown modules.
    """
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with module facts
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "oauth-sheriff-core", "path": "oauth-sheriff-core", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "my-service", "path": "my-service", "build_systems": ["maven"], "packaging": "jar"}
        ])

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        # my-service should be 'service'
        assert 'service' in content
        # oauth-sheriff-core should NOT have a layer assigned (unknown is omitted)
        # Parse the modules section to find oauth-sheriff-core's content
        lines = content.split('\n')
        in_core_module = False
        core_has_layer = False
        core_indent = None
        for line in lines:
            if 'oauth-sheriff-core:' in line:
                in_core_module = True
                # Determine the indentation of module names (e.g., 2 spaces)
                core_indent = len(line) - len(line.lstrip())
            elif in_core_module:
                # Skip empty lines
                if not line.strip():
                    continue
                # Check if we've moved to a different module at same indentation
                line_indent = len(line) - len(line.lstrip())
                if line_indent == core_indent and line.strip().endswith(':'):
                    break  # New module at same level, exit
                if line_indent <= core_indent and not line.startswith(' ' * (core_indent + 1)):
                    break  # Back to parent level, exit
                # Check if this module has a layer
                if 'layer:' in line:
                    core_has_layer = True
                    break
        assert not core_has_layer, "*-core should not have layer assigned (requires LLM analysis)"


def test_generate_minimal_output_for_unknown_layer():
    """Test generate produces minimal output for modules with unknown layer."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with module facts
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-module", "path": "my-module", "build_systems": ["maven"], "packaging": "jar"}
        ])

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        # Should not have layer_rules (removed)
        assert 'layer_rules' not in content, "layer_rules should be removed"
        # Module should exist but may not have layer
        assert 'my-module' in content


def test_generate_pom_packaging_infers_parent_layer():
    """Test generate uses packaging='pom' to infer parent layer."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with packaging info (JSON format)
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "bom", "path": "bom", "build_systems": ["maven"], "packaging": "pom"},
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"}
        ])

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        # bom with packaging=pom should have 'parent' layer
        lines = content.split('\n')
        in_bom = False
        bom_layer = None
        for line in lines:
            if 'bom:' in line and not 'build' in line:
                in_bom = True
            elif in_bom and 'layer:' in line:
                bom_layer = line.strip()
                break
            elif in_bom and line.strip() and not line.startswith(' '):
                break
        assert bom_layer is not None, "Should find layer for bom"
        assert 'parent' in bom_layer, f"POM modules should have 'parent' layer, got: {bom_layer}"


def test_generate_uses_raw_data_for_packages():
    """Test generate extracts key_packages from raw-project-data.json."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with package info (JSON format)
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "my-core": {
                "packages": ["com.example.core", "com.example.core.domain", "com.example.core.util"],
                "source_files": 10,
                "test_files": 5
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        # Should include domain package (prioritized over util)
        assert 'com.example.core.domain' in content or 'com.example.core' in content


def test_generate_detects_framework_from_dependencies():
    """Test generate detects framework from raw-project-data.json dependencies."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with Quarkus dependencies (JSON format)
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-quarkus", "path": "my-quarkus", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "my-quarkus": {
                "dependencies": ["io.quarkus:quarkus-core:compile", "io.quarkus:quarkus-arc:compile"],
                "source_files": 10,
                "test_files": 5
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        # Should detect quarkus framework
        assert 'quarkus' in content, "Should detect quarkus framework from dependencies"


def test_generate_omits_empty_fields():
    """Test generate omits empty arrays, 'none' values, and empty strings."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with no packages/dependencies (JSON format)
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "my-core": {
                "source_files": 0,
                "test_files": 0
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        # Should NOT have empty arrays or 'none' values
        assert 'tips[0]:' not in content, "Should omit empty tips array"
        assert 'insights[0]:' not in content, "Should omit empty insights array"
        assert 'best_practices[0]:' not in content, "Should omit empty best_practices array"
        assert 'key_packages[0]:' not in content, "Should omit empty key_packages array"
        assert 'di: none' not in content, "Should omit di: none"


def test_generate_extracts_module_dependencies():
    """Test generate extracts inter-module dependencies from raw data."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json where api depends on core (JSON format)
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "core", "path": "core", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "api", "path": "api", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "core": {
                "source_files": 10,
                "test_files": 5
            },
            "api": {
                "source_files": 5,
                "test_files": 3,
                "dependencies": ["com.example:core:compile"]
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.toon').read_text()
        # Should have dependencies section with api -> core (flat structure)
        assert 'dependencies:' in content
        # The api module should be listed in dependencies with core as its dependency
        lines = content.split('\n')
        in_dependencies = False
        found_api_dep = False
        for line in lines:
            if line.strip() == 'dependencies:':
                in_dependencies = True
            elif in_dependencies and 'api' in line:
                found_api_dep = True
            elif in_dependencies and line.strip() and not line.startswith(' '):
                break  # Exited dependencies section
        assert found_api_dep, "Should find api in dependencies section"


# =============================================================================
# collect-raw-data Command Tests
# =============================================================================

def create_root_pom(fixture_dir: Path, modules: list) -> Path:
    """Create a parent pom.xml with modules section.

    Args:
        fixture_dir: Directory to create pom.xml in.
        modules: List of module names to include.

    Returns:
        Path to created pom.xml.
    """
    modules_xml = "\n".join(f"    <module>{m}</module>" for m in modules)
    pom_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>parent</artifactId>
  <version>1.0.0</version>
  <packaging>pom</packaging>
  <modules>
{modules_xml}
  </modules>
</project>
"""
    pom_path = fixture_dir / 'pom.xml'
    pom_path.write_text(pom_content)
    return pom_path


def create_maven_module(fixture_dir: Path, name: str, packages: list = None,
                        dependencies: list = None, readme: str = None,
                        create_parent: bool = True):
    """Create a Maven module with source files and pom.xml.

    Args:
        fixture_dir: Parent directory.
        name: Module name.
        packages: List of Java packages to create.
        dependencies: List of dependencies in "groupId:artifactId:scope" format.
        readme: README filename to create.
        create_parent: If True, creates or updates parent pom.xml with this module.
    """
    mod_dir = fixture_dir / name
    mod_dir.mkdir(parents=True, exist_ok=True)

    # Create or update parent pom.xml if requested
    if create_parent:
        parent_pom = fixture_dir / 'pom.xml'
        if parent_pom.exists():
            # Update existing parent pom to include this module
            content = parent_pom.read_text()
            if f'<module>{name}</module>' not in content:
                # Insert module before </modules>
                content = content.replace(
                    '</modules>',
                    f'    <module>{name}</module>\n  </modules>'
                )
                parent_pom.write_text(content)
        else:
            create_root_pom(fixture_dir, [name])

    # Create module pom.xml
    deps_xml = ""
    if dependencies:
        deps_xml = "<dependencies>\n"
        for dep in dependencies:
            parts = dep.split(':')
            group_id = parts[0] if len(parts) > 0 else 'com.example'
            artifact_id = parts[1] if len(parts) > 1 else 'dep'
            scope = parts[2] if len(parts) > 2 else 'compile'
            deps_xml += f"""    <dependency>
      <groupId>{group_id}</groupId>
      <artifactId>{artifact_id}</artifactId>
      <scope>{scope}</scope>
    </dependency>
"""
        deps_xml += "  </dependencies>"

    pom_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>{name}</artifactId>
  <version>1.0.0</version>
  <packaging>jar</packaging>
  {deps_xml}
</project>
"""
    (mod_dir / 'pom.xml').write_text(pom_content)

    # Create source files with packages
    if packages:
        for pkg in packages:
            pkg_path = mod_dir / 'src' / 'main' / 'java' / pkg.replace('.', '/')
            pkg_path.mkdir(parents=True, exist_ok=True)
            (pkg_path / 'Example.java').write_text(f"package {pkg};\npublic class Example {{}}")

    # Create test files
    test_dir = mod_dir / 'src' / 'test' / 'java' / 'com' / 'example'
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / 'ExampleTest.java').write_text("package com.example;\npublic class ExampleTest {}")

    # Create README if specified
    if readme:
        (mod_dir / readme).write_text(f"# {name}\n\nModule documentation.")


def test_collect_raw_data_basic():
    """Test collect-raw-data discovers modules from filesystem."""
    with PlanTestContext() as ctx:
        # Create the module directory with source files (creates parent pom.xml automatically)
        create_maven_module(ctx.fixture_dir, "my-core",
                           packages=["com.example.core", "com.example.core.util"])

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'modules_discovered' in result.stdout
        assert '1' in result.stdout or 'my-core' in result.stdout

        # Verify file created
        raw_data_path = ctx.fixture_dir / 'raw-project-data.json'
        assert raw_data_path.exists(), "Should create raw-project-data.json"


def test_collect_raw_data_finds_documentation():
    """Test collect-raw-data finds project and module documentation."""
    with PlanTestContext() as ctx:
        # Create project README
        (ctx.fixture_dir / 'README.adoc').write_text("= Project Title\n\nDescription.")

        # Create doc directory with files
        doc_dir = ctx.fixture_dir / 'doc'
        doc_dir.mkdir()
        (doc_dir / 'Requirements.adoc').write_text("= Requirements")
        (doc_dir / 'Architecture.md').write_text("# Architecture")

        # Create doc subdirectory
        (doc_dir / 'security').mkdir()

        # Create module (creates parent pom.xml automatically)
        create_maven_module(ctx.fixture_dir, "my-core", readme="README.md")

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        content = (ctx.fixture_dir / 'raw-project-data.json').read_text()
        assert 'README.adoc' in content, "Should find project README"
        assert 'Requirements.adoc' in content or 'doc_files' in content


def test_collect_raw_data_scans_packages():
    """Test collect-raw-data scans Java packages."""
    with PlanTestContext() as ctx:
        # Create module with packages (creates parent pom.xml automatically)
        create_maven_module(ctx.fixture_dir, "my-core",
                           packages=["com.example.core", "com.example.core.service"])

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        content = (ctx.fixture_dir / 'raw-project-data.json').read_text()
        assert 'com.example.core' in content, "Should find packages"


def test_collect_raw_data_extracts_dependencies():
    """Test collect-raw-data extracts dependencies with scope."""
    with PlanTestContext() as ctx:
        # Create module with dependencies (creates parent pom.xml automatically)
        create_maven_module(ctx.fixture_dir, "my-core",
                           dependencies=["org.example:lib:compile", "org.junit:junit:test"])

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        content = (ctx.fixture_dir / 'raw-project-data.json').read_text()
        # Check dependencies are captured with scope
        assert 'org.example:lib:compile' in content or 'dependencies' in content


def test_collect_raw_data_counts_files():
    """Test collect-raw-data counts source and test files."""
    with PlanTestContext() as ctx:
        # Create module with packages (creates parent pom.xml automatically)
        create_maven_module(ctx.fixture_dir, "my-core",
                           packages=["com.example.core"])

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        content = (ctx.fixture_dir / 'raw-project-data.json').read_text()
        assert 'source_files' in content
        assert 'test_files' in content


def test_collect_raw_data_outputs_valid_json():
    """Test collect-raw-data outputs valid JSON format."""
    with PlanTestContext() as ctx:
        # Create module (creates parent pom.xml automatically)
        create_maven_module(ctx.fixture_dir, "my-core")

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        raw_data_path = ctx.fixture_dir / 'raw-project-data.json'
        content = raw_data_path.read_text()

        # Validate JSON structure
        import json
        data = json.loads(content)
        assert 'project' in data
        assert 'root' in data['project']
        assert 'modules' in data
        assert 'documentation' in data


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
        create_raw_project_data(ctx.fixture_dir)
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
        test_read_fails_without_data,
        # generate tests
        test_generate_creates_structure,
        test_generate_infers_layers,
        test_generate_core_does_not_infer_service,
        test_generate_minimal_output_for_unknown_layer,
        test_generate_pom_packaging_infers_parent_layer,
        test_generate_uses_raw_data_for_packages,
        test_generate_detects_framework_from_dependencies,
        test_generate_omits_empty_fields,
        test_generate_extracts_module_dependencies,
        test_generate_fails_if_exists,
        test_generate_force_overwrites,
        # collect-raw-data tests
        test_collect_raw_data_basic,
        test_collect_raw_data_finds_documentation,
        test_collect_raw_data_scans_packages,
        test_collect_raw_data_extracts_dependencies,
        test_collect_raw_data_counts_files,
        test_collect_raw_data_outputs_valid_json,
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
