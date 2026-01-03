#!/usr/bin/env python3
"""Tests for discover_modules() in Maven extension.

Tests the unified module discovery API for Maven projects including
metadata extraction, dependency parsing, package discovery, and stats.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    TestRunner,
    BuildTestContext
)

# Add extension directories to path for import
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
EXTENSION_BASE_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'
EXTENSION_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'pm-dev-java' / 'skills' / 'plan-marshall-plugin'
sys.path.insert(0, str(EXTENSION_BASE_DIR))
sys.path.insert(0, str(EXTENSION_DIR))

# Import Extension class directly from the file
import importlib.util
spec = importlib.util.spec_from_file_location("java_extension", EXTENSION_DIR / "extension.py")
java_extension = importlib.util.module_from_spec(spec)
spec.loader.exec_module(java_extension)
Extension = java_extension.Extension


# =============================================================================
# Test: Basic Module Discovery
# =============================================================================

def test_discover_modules_single_module():
    """Test discover_modules with single-module Maven project."""
    with BuildTestContext() as ctx:
        # Create a single-module Maven project
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>
    <description>My sample application</description>
    <packaging>jar</packaging>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(pom_content)

        # Create source directory
        src_main = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        src_main.mkdir(parents=True)
        (src_main / 'App.java').write_text('public class App {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        module = modules[0]

        assert module['name'] == 'my-app'
        assert module['path'] == '.'
        assert 'maven' in module['build_systems']
        assert module['metadata']['artifactId'] == 'my-app'
        assert module['metadata']['groupId'] == 'com.example'
        assert module['metadata']['description'] == 'My sample application'
        assert module['metadata']['packaging'] == 'jar'


def test_discover_modules_multi_module():
    """Test discover_modules with multi-module Maven project."""
    with BuildTestContext() as ctx:
        # Create parent pom with modules
        parent_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>parent</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    <modules>
        <module>core</module>
        <module>web</module>
    </modules>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(parent_pom)

        # Create core module
        core_dir = ctx.temp_dir / 'core'
        core_dir.mkdir()
        core_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
    </parent>
    <artifactId>core</artifactId>
    <description>Core library module</description>
</project>'''
        (core_dir / 'pom.xml').write_text(core_pom)

        # Create web module
        web_dir = ctx.temp_dir / 'web'
        web_dir.mkdir()
        web_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
    </parent>
    <artifactId>web</artifactId>
    <packaging>war</packaging>
</project>'''
        (web_dir / 'pom.xml').write_text(web_pom)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 2

        # Find modules by name
        core_module = next(m for m in modules if m['name'] == 'core')
        web_module = next(m for m in modules if m['name'] == 'web')

        assert core_module['path'] == 'core'
        assert core_module['metadata']['description'] == 'Core library module'
        assert core_module['metadata']['parent']['name'] == 'parent'

        assert web_module['path'] == 'web'
        assert web_module['metadata']['packaging'] == 'war'


def test_discover_modules_no_pom():
    """Test discover_modules with no pom.xml."""
    with BuildTestContext() as ctx:
        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 0


# =============================================================================
# Test: Source Directory Discovery
# =============================================================================

def test_discover_sources():
    """Test source directory discovery."""
    with BuildTestContext() as ctx:
        # Create pom
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        # Create standard Maven layout
        (ctx.temp_dir / 'src' / 'main' / 'java' / 'com').mkdir(parents=True)
        (ctx.temp_dir / 'src' / 'test' / 'java' / 'com').mkdir(parents=True)
        (ctx.temp_dir / 'src' / 'main' / 'resources').mkdir(parents=True)
        (ctx.temp_dir / 'src' / 'test' / 'resources').mkdir(parents=True)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        sources = modules[0]['sources']

        assert 'src/main/java' in sources['main']
        assert 'src/test/java' in sources['test']
        assert 'src/main/resources' in sources['resources']
        assert 'src/test/resources' in sources['resources']


# =============================================================================
# Test: Dependency Extraction
# =============================================================================

def test_extract_dependencies():
    """Test dependency extraction from pom.xml."""
    with BuildTestContext() as ctx:
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <artifactId>test</artifactId>
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
        </dependency>
    </dependencies>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(pom_content)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        deps = modules[0]['dependencies']
        assert len(deps) == 2

        junit_dep = next(d for d in deps if d['artifactId'] == 'junit-jupiter')
        assert junit_dep['groupId'] == 'org.junit.jupiter'
        assert junit_dep['scope'] == 'test'

        guava_dep = next(d for d in deps if d['artifactId'] == 'guava')
        assert guava_dep['scope'] == 'compile'  # Default scope


def test_extract_dependencies_skips_management():
    """Test that dependencyManagement dependencies are skipped."""
    with BuildTestContext() as ctx:
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <artifactId>test</artifactId>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>managed.group</groupId>
                <artifactId>managed-artifact</artifactId>
            </dependency>
        </dependencies>
    </dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>actual.group</groupId>
            <artifactId>actual-artifact</artifactId>
        </dependency>
    </dependencies>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(pom_content)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        deps = modules[0]['dependencies']
        # Should only have the actual dependency, not the managed one
        assert len(deps) == 1
        assert deps[0]['artifactId'] == 'actual-artifact'


# =============================================================================
# Test: Package Discovery
# =============================================================================

def test_discover_packages():
    """Test Java package discovery."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        # Create package with source files
        pkg_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        pkg_dir.mkdir(parents=True)
        (pkg_dir / 'Foo.java').write_text('public class Foo {}')
        (pkg_dir / 'Bar.java').write_text('public class Bar {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        packages = modules[0]['packages']
        assert len(packages) >= 1

        com_example = next(p for p in packages if p['name'] == 'com.example')
        assert com_example['source_files'] == 2


def test_discover_packages_with_package_info():
    """Test package discovery with package-info.java."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        pkg_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example' / 'util'
        pkg_dir.mkdir(parents=True)
        (pkg_dir / 'Helper.java').write_text('public class Helper {}')

        # Create package-info with JavaDoc
        package_info = '''/**
 * Utility classes for common operations.
 */
package com.example.util;'''
        (pkg_dir / 'package-info.java').write_text(package_info)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        packages = modules[0]['packages']
        util_pkg = next(p for p in packages if p['name'] == 'com.example.util')
        assert util_pkg['description'] == 'Utility classes for common operations.'


# =============================================================================
# Test: Stats
# =============================================================================

def test_stats_file_counts():
    """Test source and test file counting."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        # Create source files
        src_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        src_dir.mkdir(parents=True)
        (src_dir / 'Foo.java').write_text('public class Foo {}')
        (src_dir / 'Bar.java').write_text('public class Bar {}')
        (src_dir / 'Baz.java').write_text('public class Baz {}')

        # Create test files
        test_dir = ctx.temp_dir / 'src' / 'test' / 'java' / 'com' / 'example'
        test_dir.mkdir(parents=True)
        (test_dir / 'FooTest.java').write_text('public class FooTest {}')
        (test_dir / 'BarTest.java').write_text('public class BarTest {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        stats = modules[0]['stats']
        assert stats['source_files'] == 3
        assert stats['test_files'] == 2


def test_stats_has_readme():
    """Test README detection."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')
        (ctx.temp_dir / 'README.md').write_text('# My Project')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['stats']['has_readme'] is True


def test_stats_no_readme():
    """Test README detection when none exists."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['stats']['has_readme'] is False


# =============================================================================
# Test: Hybrid Modules
# =============================================================================

def test_hybrid_maven_npm_module():
    """Test detection of hybrid Maven + npm module."""
    with BuildTestContext() as ctx:
        # Create Maven project
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>frontend</artifactId></project>')

        # Add package.json (hybrid)
        (ctx.temp_dir / 'package.json').write_text('{"name": "frontend", "version": "1.0.0"}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        assert 'maven' in modules[0]['build_systems']
        assert 'npm' in modules[0]['build_systems']
        assert modules[0]['descriptors']['pom'] == 'pom.xml'
        assert modules[0]['descriptors']['package'] == 'package.json'


# =============================================================================
# Test: Nested Module Discovery
# =============================================================================

def test_discover_nested_modules():
    """Test discovery of nested modules (grandchildren).

    Structure:
    root/
      pom.xml (modules: child-parent)
      child-parent/
        pom.xml (modules: grandchild-a, grandchild-b)
        grandchild-a/
          pom.xml
        grandchild-b/
          pom.xml

    All grandchildren should be discovered, not just first-level modules.
    This is the structure used by OAuth-Sheriff with oauth-sheriff-quarkus-parent.
    """
    with BuildTestContext() as ctx:
        # Create root pom with child-parent module
        root_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>root</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    <modules>
        <module>child-parent</module>
    </modules>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(root_pom)

        # Create child-parent module (also a parent POM with nested modules)
        child_parent_dir = ctx.temp_dir / 'child-parent'
        child_parent_dir.mkdir()
        child_parent_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>root</artifactId>
    </parent>
    <artifactId>child-parent</artifactId>
    <packaging>pom</packaging>
    <modules>
        <module>grandchild-a</module>
        <module>grandchild-b</module>
    </modules>
</project>'''
        (child_parent_dir / 'pom.xml').write_text(child_parent_pom)

        # Create grandchild-a
        grandchild_a_dir = child_parent_dir / 'grandchild-a'
        grandchild_a_dir.mkdir()
        grandchild_a_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>child-parent</artifactId>
    </parent>
    <artifactId>grandchild-a</artifactId>
    <description>First grandchild module</description>
</project>'''
        (grandchild_a_dir / 'pom.xml').write_text(grandchild_a_pom)

        # Create grandchild-b
        grandchild_b_dir = child_parent_dir / 'grandchild-b'
        grandchild_b_dir.mkdir()
        grandchild_b_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>child-parent</artifactId>
    </parent>
    <artifactId>grandchild-b</artifactId>
    <description>Second grandchild module</description>
</project>'''
        (grandchild_b_dir / 'pom.xml').write_text(grandchild_b_pom)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        # Should discover both grandchildren (not child-parent which is pom packaging)
        module_names = [m['name'] for m in modules]
        assert 'grandchild-a' in module_names, f"Should find grandchild-a, got: {module_names}"
        assert 'grandchild-b' in module_names, f"Should find grandchild-b, got: {module_names}"
        assert len(modules) == 2, f"Expected 2 modules, got {len(modules)}: {module_names}"

        # Verify paths are correct (relative to project root)
        grandchild_a = next(m for m in modules if m['name'] == 'grandchild-a')
        grandchild_b = next(m for m in modules if m['name'] == 'grandchild-b')
        assert grandchild_a['path'] == 'child-parent/grandchild-a'
        assert grandchild_b['path'] == 'child-parent/grandchild-b'


def test_discover_deeply_nested_modules():
    """Test discovery of deeply nested modules (3+ levels).

    Structure:
    root/
      pom.xml (modules: level1)
      level1/
        pom.xml (modules: level2)
        level2/
          pom.xml (modules: level3)
          level3/
            pom.xml (actual jar module)

    The level3 module should be discovered.
    """
    with BuildTestContext() as ctx:
        # Create root pom
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>root</artifactId>
    <packaging>pom</packaging>
    <modules><module>level1</module></modules>
</project>''')

        # Create level1
        level1 = ctx.temp_dir / 'level1'
        level1.mkdir()
        (level1 / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>level1</artifactId>
    <packaging>pom</packaging>
    <modules><module>level2</module></modules>
</project>''')

        # Create level2
        level2 = level1 / 'level2'
        level2.mkdir()
        (level2 / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>level2</artifactId>
    <packaging>pom</packaging>
    <modules><module>level3</module></modules>
</project>''')

        # Create level3 (actual jar module)
        level3 = level2 / 'level3'
        level3.mkdir()
        (level3 / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>level3</artifactId>
    <packaging>jar</packaging>
    <description>Deep module</description>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        module_names = [m['name'] for m in modules]
        assert 'level3' in module_names, f"Should find level3, got: {module_names}"
        assert len(modules) == 1, f"Expected 1 jar module, got {len(modules)}: {module_names}"

        level3_module = modules[0]
        assert level3_module['path'] == 'level1/level2/level3'


# =============================================================================
# Test: Module Type Detection
# =============================================================================

def test_module_type_quarkus():
    """Test Quarkus module type detection."""
    with BuildTestContext() as ctx:
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <artifactId>quarkus-app</artifactId>
    <build>
        <plugins>
            <plugin>
                <groupId>io.quarkus</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(pom_content)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['metadata']['type'] == 'quarkus'


def test_module_type_pom():
    """Test POM module type detection."""
    with BuildTestContext() as ctx:
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <artifactId>parent</artifactId>
    <packaging>pom</packaging>
    <modules>
        <module>child</module>
    </modules>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(pom_content)

        # Create child module
        child_dir = ctx.temp_dir / 'child'
        child_dir.mkdir()
        (child_dir / 'pom.xml').write_text('<project><artifactId>child</artifactId></project>')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        # Should discover child, not parent (multi-module behavior)
        child = modules[0]
        assert child['name'] == 'child'


# =============================================================================
# Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Basic module discovery
        test_discover_modules_single_module,
        test_discover_modules_multi_module,
        test_discover_modules_no_pom,

        # Source directory discovery
        test_discover_sources,

        # Dependency extraction
        test_extract_dependencies,
        test_extract_dependencies_skips_management,

        # Package discovery
        test_discover_packages,
        test_discover_packages_with_package_info,

        # Stats
        test_stats_file_counts,
        test_stats_has_readme,
        test_stats_no_readme,

        # Hybrid modules
        test_hybrid_maven_npm_module,

        # Nested module discovery
        test_discover_nested_modules,
        test_discover_deeply_nested_modules,

        # Module type detection
        test_module_type_quarkus,
        test_module_type_pom,
    ])
    sys.exit(runner.run())
