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
    """Create raw-project-data.json with unified module structure.

    Args:
        fixture_dir: Directory to create file in (the .plan subdir).
        modules: List of module dicts with name, path, build_systems, packaging.
        module_details: Dict of module name -> details (packages, dependencies, etc).
                       These are merged into the corresponding module dicts.

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

    # Merge module_details into modules (unified structure)
    for module in modules:
        name = module.get('name')
        if name and name in module_details:
            module.update(module_details[name])

    data = {
        "project": {
            "root": str(fixture_dir.parent),
            "name": fixture_dir.parent.name
        },
        "documentation": {
            "readme": "",
            "doc_files": []
        },
        "modules": modules
    }
    raw_data_path = fixture_dir / 'raw-project-data.json'
    raw_data_path.write_text(json.dumps(data, indent=2))
    return raw_data_path


def create_project_structure(fixture_dir: Path, structure: dict = None) -> Path:
    """Create project-structure.json with sample content."""
    if structure is None:
        structure = {
            "modules": {
                "my-core": {
                    "responsibility": "Core business logic",
                    "key_packages": {
                        "com.example.core": {
                            "path": "my-core/src/main/java/com/example/core",
                            "package_info": "",
                            "description": "Core domain models"
                        }
                    },
                    "dependencies": [
                        "io.quarkus:quarkus-core:compile",
                        "jakarta.inject:jakarta.inject-api:compile"
                    ],
                    "tips": ["Use @ApplicationScoped"],
                    "insights": ["Heavy validation in boundary"],
                    "best_practices": ["One service per file"]
                },
                "my-ui": {
                    "responsibility": "User interface components",
                    "key_packages": {
                        "src.main.webapp": {
                            "path": "my-ui/src/main/webapp",
                            "package_info": "",
                            "description": "Frontend components"
                        }
                    },
                    "dependencies": [
                        "@angular/core:compile",
                        "jest:test"
                    ]
                }
            },
            "dependencies": {
                "my-ui": ["my-core"]
            },
            "placement": {
                "service": {
                    "module": "my-core",
                    "package": "com.example.core.{feature}",
                    "pattern": "{Name}Service.java",
                    "test_pattern": "{Name}ServiceTest.java"
                }
            },
            "conventions": {
                "naming": ["Services: {Name}Service"],
                "packages": ["com.example.core.{feature}"],
                "testing": ["Unit tests in same module"],
                "documentation": ["JavaDoc on public classes"]
            }
        }

    structure_path = fixture_dir / 'project-structure.json'
    structure_path.write_text(json.dumps(structure, indent=2))
    return structure_path


# =============================================================================
# read Command Tests
# =============================================================================

def test_read_existing_structure():
    """Test reading existing project-structure.json."""
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
        structure_path = ctx.fixture_dir / 'project-structure.json'
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
        structure_path = ctx.fixture_dir / 'project-structure.json'
        assert structure_path.exists()


def test_generate_minimal_output():
    """Test generate produces minimal output for modules."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with module facts
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-module", "path": "my-module", "build_systems": ["maven"], "packaging": "jar"}
        ])

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        # Module should exist
        assert 'my-module' in content
        # Should not have layer field (removed from schema)
        assert 'layer:' not in content


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
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        # Should include domain package (prioritized over util)
        assert 'com.example.core.domain' in content or 'com.example.core' in content


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
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        # Should NOT have empty arrays or 'none' values
        assert 'tips[0]:' not in content, "Should omit empty tips array"
        assert 'insights[0]:' not in content, "Should omit empty insights array"
        assert 'best_practices[0]:' not in content, "Should omit empty best_practices array"
        assert 'key_packages[0]:' not in content, "Should omit empty key_packages array"
        assert 'di: none' not in content, "Should omit di: none"


def test_generate_includes_project_name():
    """Test generate extracts project name from raw-project-data.json."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        create_raw_project_data(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success, f"Should succeed: {result.stderr}"
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        data = json.loads(content)
        # Project name should come from raw-project-data.json's project.name field
        assert 'project' in data
        assert 'name' in data['project']
        assert data['project']['name'], "Project name should not be empty"


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
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        data = json.loads(content)
        # Should have top-level dependencies section with api -> core (inter-module)
        assert 'dependencies' in data
        assert 'api' in data['dependencies'], "Should find api in inter-module dependencies"


def test_generate_includes_external_dependencies_per_module():
    """Test generate includes external dependencies in each module entry."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with external dependencies
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-lib", "path": "my-lib", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "my-lib": {
                "source_files": 10,
                "dependencies": [
                    "org.junit:junit:test",
                    "org.slf4j:slf4j-api:compile",
                    "com.example:utils:compile"
                ]
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        data = json.loads(content)
        # Should have dependencies in the module entry
        assert 'my-lib' in data['modules']
        module = data['modules']['my-lib']
        assert 'dependencies' in module, "Module should have dependencies field"
        assert len(module['dependencies']) == 3, "Should have 3 dependencies"
        assert 'org.junit:junit:test' in module['dependencies']


def test_generate_includes_module_readme():
    """Test generate includes readme path from raw data in module entry."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)
        # Create raw-project-data.json with readme path
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-lib", "path": "my-lib", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "my-lib": {
                "source_files": 10,
                "readme": "my-lib/README.adoc"
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        data = json.loads(content)
        # Should have readme in the module entry
        assert 'my-lib' in data['modules']
        module = data['modules']['my-lib']
        assert 'readme' in module, "Module should have readme field"
        assert module['readme'] == 'my-lib/README.adoc'


def test_generate_extracts_package_description_from_package_info():
    """Test generate extracts description from package-info.java JavaDoc."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        # Create package-info.java with JavaDoc
        # Files should be in project root (fixture_dir.parent), not in .plan dir (fixture_dir)
        project_root = ctx.fixture_dir.parent
        pkg_path = project_root / 'my-lib' / 'src' / 'main' / 'java' / 'com' / 'example' / 'core'
        pkg_path.mkdir(parents=True, exist_ok=True)
        (pkg_path / 'package-info.java').write_text('''/**
 * Provides core domain models and validation logic.
 * This package contains the main business entities.
 */
package com.example.core;
''')

        # Create raw-project-data.json with package_info path
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-lib", "path": "my-lib", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "my-lib": {
                "source_files": 10,
                "packages": {
                    "com.example.core": {
                        "path": "my-lib/src/main/java/com/example/core",
                        "package_info": "my-lib/src/main/java/com/example/core/package-info.java"
                    }
                }
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        data = json.loads(content)
        module = data['modules']['my-lib']
        assert 'key_packages' in module
        pkg = module['key_packages'].get('com.example.core', {})
        assert 'description' in pkg, "Package should have description extracted from package-info.java"
        assert 'core domain models' in pkg['description'].lower(), \
            f"Description should contain content from JavaDoc, got: {pkg['description']}"


def test_generate_extracts_description_from_class_javadoc_fallback():
    """Test generate extracts description from main class JavaDoc when no package-info.java."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        # Create package WITHOUT package-info.java but WITH a class that has JavaDoc
        # Use 'fallback-lib' to avoid conflict with other tests
        project_root = ctx.fixture_dir.parent
        pkg_path = project_root / 'fallback-lib' / 'src' / 'main' / 'java' / 'com' / 'example' / 'health'
        pkg_path.mkdir(parents=True, exist_ok=True)

        # Create a class with JavaDoc (no package-info.java)
        (pkg_path / 'HealthCheck.java').write_text('''package com.example.health;

/**
 * Provides health check endpoints for monitoring application status.
 * Supports liveness and readiness probes.
 *
 * @author Test
 */
public class HealthCheck {
    public boolean isHealthy() {
        return true;
    }
}
''')

        # Create raw-project-data.json WITHOUT package_info path
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "fallback-lib", "path": "fallback-lib", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "fallback-lib": {
                "source_files": 1,
                "packages": {
                    "com.example.health": {
                        "path": "fallback-lib/src/main/java/com/example/health"
                        # Note: no package_info field
                    }
                }
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        data = json.loads(content)
        module = data['modules']['fallback-lib']
        assert 'key_packages' in module
        pkg = module['key_packages'].get('com.example.health', {})
        assert 'description' in pkg, "Package should have description extracted from class JavaDoc as fallback"
        assert 'health check' in pkg['description'].lower(), \
            f"Description should contain content from class JavaDoc, got: {pkg['description']}"


def test_generate_extracts_responsibility_from_readme():
    """Test generate extracts module responsibility from README file."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        # Create module directory and README
        # Use 'readme-lib' to avoid conflict with other tests that create 'my-lib'
        # Files should be in project root (fixture_dir.parent), not in .plan dir (fixture_dir)
        project_root = ctx.fixture_dir.parent
        mod_path = project_root / 'readme-lib'
        mod_path.mkdir(parents=True, exist_ok=True)
        (mod_path / 'README.adoc').write_text('''= My Library

Validates OAuth tokens against configurable security policies.

== Features

* Token validation
* Caching
''')

        # Create raw-project-data.json with readme path
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "readme-lib", "path": "readme-lib", "build_systems": ["maven"], "packaging": "jar"}
        ], module_details={
            "readme-lib": {
                "source_files": 10,
                "readme": "readme-lib/README.adoc"
            }
        })

        result = run_script(SCRIPT_PATH, 'generate')

        assert result.success
        content = (ctx.fixture_dir / 'project-structure.json').read_text()
        data = json.loads(content)
        module = data['modules']['readme-lib']
        assert 'responsibility' in module, "Module should have responsibility extracted from README"
        assert 'oauth tokens' in module['responsibility'].lower() or 'validates' in module['responsibility'].lower(), \
            f"Responsibility should contain content from README, got: {module['responsibility']}"


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


def test_collect_raw_data_includes_readme_path():
    """Test collect-raw-data includes project-relative path to module README."""
    with PlanTestContext() as ctx:
        # Create module with README
        create_maven_module(ctx.fixture_dir, "my-core", readme="README.adoc")

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        content = (ctx.fixture_dir / 'raw-project-data.json').read_text()
        data = json.loads(content)

        # Find the my-core module
        my_core = next((m for m in data['modules'] if m['name'] == 'my-core'), None)
        assert my_core is not None, "Should find my-core module"
        assert 'readme' in my_core, "Module should have readme field"

        # Should be project-relative path starting with module name
        readme_path = my_core['readme']
        assert readme_path.startswith('my-core/'), \
            f"README should be project-relative path, got: {readme_path}"
        assert 'README' in readme_path, \
            f"README path should contain README, got: {readme_path}"


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


def test_collect_raw_data_hybrid_module_dependencies():
    """Test collect-raw-data extracts Maven dependencies from hybrid modules.

    Note: npm dependencies require the pm-dev-frontend extension which may not
    be loaded in all test environments. This test focuses on Maven dependencies.
    """
    with PlanTestContext() as ctx:
        # Create hybrid module with pom.xml and package.json
        mod_dir = ctx.fixture_dir / 'hybrid-module'
        mod_dir.mkdir(parents=True)

        # Create parent pom.xml
        create_root_pom(ctx.fixture_dir, ['hybrid-module'])

        # Create module pom.xml with maven dependency
        (mod_dir / 'pom.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>hybrid-module</artifactId>
  <version>1.0.0</version>
  <packaging>jar</packaging>
  <dependencies>
    <dependency>
      <groupId>io.quarkus</groupId>
      <artifactId>quarkus-core</artifactId>
      <scope>compile</scope>
    </dependency>
  </dependencies>
</project>
''')

        # Create package.json (for hybrid detection)
        (mod_dir / 'package.json').write_text(json.dumps({
            "name": "hybrid-devui",
            "devDependencies": {
                "lit": "^3.0.0"
            }
        }))

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        content = (ctx.fixture_dir / 'raw-project-data.json').read_text()
        data = json.loads(content)

        hybrid = next((m for m in data['modules'] if m['name'] == 'hybrid-module'), None)
        assert hybrid is not None, "Should find hybrid-module"

        # Dependencies are now strings in "groupId:artifactId:scope" format
        deps = hybrid.get('dependencies', [])
        assert len(deps) > 0, "Should have dependencies"
        assert any('quarkus-core' in d for d in deps), "Should have quarkus-core dependency"


def test_collect_raw_data_hybrid_module_package_json_path():
    """Test collect-raw-data discovers hybrid modules with both pom.xml and package.json.

    Note: package_json path detection requires the pm-dev-frontend extension.
    In isolation (Maven-only discovery), the module is discovered via Maven
    but may not have package_json path unless frontend extension is loaded.
    This test verifies the module is discovered; package_json is optional.
    """
    with PlanTestContext() as ctx:
        # Create hybrid module
        mod_dir = ctx.fixture_dir / 'ui-module'
        mod_dir.mkdir(parents=True)

        create_root_pom(ctx.fixture_dir, ['ui-module'])
        (mod_dir / 'pom.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>ui-module</artifactId>
  <version>1.0.0</version>
</project>
''')
        (mod_dir / 'package.json').write_text('{"name": "ui"}')

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        data = json.loads((ctx.fixture_dir / 'raw-project-data.json').read_text())

        ui_mod = next((m for m in data['modules'] if m['name'] == 'ui-module'), None)
        assert ui_mod is not None, "Should find ui-module"

        # Module should be discovered via Maven
        assert 'maven' in ui_mod.get('build_systems', []), \
            f"Should be discovered as maven module, got: {ui_mod.get('build_systems')}"


def test_collect_raw_data_detects_ui_path():
    """Test collect-raw-data detects UI components path for Quarkus dev-ui."""
    with PlanTestContext() as ctx:
        # Create module with dev-ui components
        mod_dir = ctx.fixture_dir / 'devui-module'
        mod_dir.mkdir(parents=True)

        create_root_pom(ctx.fixture_dir, ['devui-module'])
        (mod_dir / 'pom.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>devui-module</artifactId>
  <version>1.0.0</version>
</project>
''')
        (mod_dir / 'package.json').write_text('{"name": "devui"}')

        # Create dev-ui components directory with JS files
        ui_path = mod_dir / 'src' / 'main' / 'resources' / 'dev-ui' / 'components'
        ui_path.mkdir(parents=True)
        (ui_path / 'my-component.js').write_text('export class MyComponent {}')

        result = run_script(SCRIPT_PATH, 'collect-raw-data', cwd=ctx.fixture_dir)

        assert result.success
        data = json.loads((ctx.fixture_dir / 'raw-project-data.json').read_text())

        devui_mod = next((m for m in data['modules'] if m['name'] == 'devui-module'), None)
        assert devui_mod is not None
        assert 'ui_path' in devui_mod, "Should have ui_path for module with dev-ui components"
        assert 'dev-ui/components' in devui_mod['ui_path'], \
            f"ui_path should point to dev-ui/components, got: {devui_mod.get('ui_path')}"


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
        structure = {"modules": {"incomplete-module": {"key_packages": {}}}}
        (ctx.fixture_dir / 'project-structure.json').write_text(json.dumps(structure, indent=2))

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
            '--responsibility', 'Updated responsibility'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify update persisted
        verify = run_script(SCRIPT_PATH, 'module', 'get', '--module', 'my-core')
        assert 'Updated responsibility' in verify.stdout


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


def test_module_add_package_with_description():
    """Test module add-package with description."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'module', 'add-package',
            '--module', 'my-core',
            '--package', 'com.example.service',
            '--description', 'Business services for processing'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'package_added' in result.stdout
        assert 'Business services' in result.stdout


def test_module_set_package_description():
    """Test module set-package-description updates package description."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        # First add a package
        run_script(
            SCRIPT_PATH, 'module', 'add-package',
            '--module', 'my-core',
            '--package', 'com.example.domain'
        )

        # Then set its description
        result = run_script(
            SCRIPT_PATH, 'module', 'set-package-description',
            '--module', 'my-core',
            '--package', 'com.example.domain',
            '--description', 'Domain models and entities'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'Domain models' in result.stdout


def test_module_set_package_description_unknown_package():
    """Test set-package-description fails for unknown package."""
    with PlanTestContext() as ctx:
        create_project_structure(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'module', 'set-package-description',
            '--module', 'my-core',
            '--package', 'com.example.nonexistent',
            '--description', 'Some description'
        )

        assert 'error' in result.stdout.lower()
        assert 'not found' in result.stdout.lower()


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
# raw-data-as-toon Command Tests
# =============================================================================

def test_raw_data_as_toon_outputs_toon():
    """Test raw-data-as-toon outputs valid TOON format."""
    with PlanTestContext() as ctx:
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "my-ui", "path": "my-ui", "build_systems": ["maven", "npm"], "packaging": "jar"}
        ])

        result = run_script(SCRIPT_PATH, 'raw-data-as-toon')

        assert result.success, f"Should succeed: {result.stderr}"
        # TOON format should have key: value pairs
        assert 'project:' in result.stdout
        assert 'modules[' in result.stdout  # uniform array syntax


def test_raw_data_as_toon_contains_modules():
    """Test raw-data-as-toon output contains module data."""
    with PlanTestContext() as ctx:
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "my-ui", "path": "ui-module", "build_systems": ["npm"], "packaging": "war"}
        ])

        result = run_script(SCRIPT_PATH, 'raw-data-as-toon')

        assert result.success
        # Module names should appear in output
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout
        # Build systems should appear
        assert 'maven' in result.stdout
        assert 'npm' in result.stdout


def test_raw_data_as_toon_fails_if_missing():
    """Test raw-data-as-toon fails if raw-project-data.json doesn't exist."""
    with PlanTestContext() as ctx:
        # Don't create raw-project-data.json

        result = run_script(SCRIPT_PATH, 'raw-data-as-toon')

        assert not result.success
        assert 'error' in result.stdout.lower()
        assert 'collect-raw-data' in result.stdout.lower()


def test_raw_data_as_toon_includes_module_details():
    """Test raw-data-as-toon includes module_details in output."""
    with PlanTestContext() as ctx:
        create_raw_project_data(
            ctx.fixture_dir,
            modules=[
                {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"}
            ],
            module_details={
                "my-core": {
                    "packages": ["com.example.core", "com.example.service"],
                    "source_files": 15,
                    "test_files": 8
                }
            }
        )

        result = run_script(SCRIPT_PATH, 'raw-data-as-toon')

        assert result.success
        # Module details should appear
        assert 'com.example.core' in result.stdout
        assert '15' in result.stdout  # source_files


# =============================================================================
# modules-for-commands Command Tests
# =============================================================================

def test_modules_for_commands_outputs_toon():
    """Test modules-for-commands outputs module data for command generation."""
    with PlanTestContext() as ctx:
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "my-ui", "path": "my-ui", "build_systems": ["maven", "npm"], "packaging": "war"}
        ])

        result = run_script(SCRIPT_PATH, 'modules-for-commands')

        assert result.success, f"Should succeed: {result.stderr}"
        # Should have uniform array format
        assert 'modules[' in result.stdout
        # Should contain module names
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout


def test_modules_for_commands_includes_build_systems():
    """Test modules-for-commands includes build_systems for each module."""
    with PlanTestContext() as ctx:
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "hybrid-mod", "path": "hybrid-mod", "build_systems": ["maven", "npm"], "packaging": "jar"}
        ])

        result = run_script(SCRIPT_PATH, 'modules-for-commands')

        assert result.success
        # Build systems should be present
        assert 'maven' in result.stdout
        assert 'npm' in result.stdout


def test_modules_for_commands_fails_if_missing():
    """Test modules-for-commands fails if raw-project-data.json doesn't exist."""
    with PlanTestContext() as ctx:
        # Don't create raw-project-data.json

        result = run_script(SCRIPT_PATH, 'modules-for-commands')

        assert not result.success
        assert 'error' in result.stdout.lower()
        assert 'collect-raw-data' in result.stdout.lower()


def test_modules_for_commands_single_module_filter():
    """Test modules-for-commands with --module filter."""
    with PlanTestContext() as ctx:
        create_raw_project_data(ctx.fixture_dir, modules=[
            {"name": "my-core", "path": "my-core", "build_systems": ["maven"], "packaging": "jar"},
            {"name": "my-ui", "path": "my-ui", "build_systems": ["npm"], "packaging": "war"}
        ])

        result = run_script(SCRIPT_PATH, 'modules-for-commands', '--module', 'my-core')

        assert result.success
        assert 'my-core' in result.stdout
        # Should NOT contain my-ui when filtered
        lines = [l for l in result.stdout.split('\n') if 'my-ui' in l and not l.strip().startswith('#')]
        assert len(lines) == 0, "Should not contain my-ui in data rows"


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
        test_generate_minimal_output,
        test_generate_uses_raw_data_for_packages,
        test_generate_omits_empty_fields,
        test_generate_includes_project_name,
        test_generate_extracts_module_dependencies,
        test_generate_includes_external_dependencies_per_module,
        test_generate_includes_module_readme,
        test_generate_extracts_package_description_from_package_info,
        test_generate_extracts_description_from_class_javadoc_fallback,
        test_generate_extracts_responsibility_from_readme,
        test_generate_fails_if_exists,
        test_generate_force_overwrites,
        # collect-raw-data tests
        test_collect_raw_data_basic,
        test_collect_raw_data_finds_documentation,
        test_collect_raw_data_scans_packages,
        test_collect_raw_data_extracts_dependencies,
        test_collect_raw_data_counts_files,
        test_collect_raw_data_includes_readme_path,
        test_collect_raw_data_outputs_valid_json,
        test_collect_raw_data_hybrid_module_dependencies,
        test_collect_raw_data_hybrid_module_package_json_path,
        test_collect_raw_data_detects_ui_path,
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
        test_module_add_package,
        test_module_add_package_with_description,
        test_module_set_package_description,
        test_module_set_package_description_unknown_package,
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
        # raw-data-as-toon tests
        test_raw_data_as_toon_outputs_toon,
        test_raw_data_as_toon_contains_modules,
        test_raw_data_as_toon_fails_if_missing,
        test_raw_data_as_toon_includes_module_details,
        # modules-for-commands tests
        test_modules_for_commands_outputs_toon,
        test_modules_for_commands_includes_build_systems,
        test_modules_for_commands_fails_if_missing,
        test_modules_for_commands_single_module_filter,
    ])
    sys.exit(runner.run())
