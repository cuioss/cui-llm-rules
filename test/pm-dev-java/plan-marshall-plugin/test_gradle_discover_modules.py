#!/usr/bin/env python3
"""Tests for discover_modules() Gradle support in Java extension.

Tests the unified module discovery API for Gradle projects including
metadata extraction, package discovery, and stats.
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
# Test: Basic Gradle Module Discovery
# =============================================================================

def test_discover_gradle_single_module():
    """Test discover_modules with single-module Gradle project."""
    with BuildTestContext() as ctx:
        # Create a single-module Gradle project
        build_gradle = '''
plugins {
    id 'java'
}

group = 'com.example'
version = '1.0.0'
description = 'My Gradle application'
'''
        (ctx.temp_dir / 'build.gradle').write_text(build_gradle)

        # Create source directory
        src_main = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        src_main.mkdir(parents=True)
        (src_main / 'App.java').write_text('public class App {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        module = modules[0]

        assert module['path'] == '.'
        assert 'gradle' in module['build_systems']
        assert module['metadata']['group'] == 'com.example'
        assert module['metadata']['version'] == '1.0.0'
        assert module['metadata']['description'] == 'My Gradle application'


def test_discover_gradle_multi_module():
    """Test discover_modules with multi-module Gradle project."""
    with BuildTestContext() as ctx:
        # Create settings.gradle with modules
        settings_gradle = '''
rootProject.name = 'parent'
include 'core'
include 'web'
'''
        (ctx.temp_dir / 'settings.gradle').write_text(settings_gradle)

        # Create core module
        core_dir = ctx.temp_dir / 'core'
        core_dir.mkdir()
        (core_dir / 'build.gradle').write_text('''
description = 'Core library module'
group = 'com.example'
''')

        # Create web module
        web_dir = ctx.temp_dir / 'web'
        web_dir.mkdir()
        (web_dir / 'build.gradle').write_text('''
description = 'Web application'
plugins {
    id 'war'
}
''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 2

        # Find modules by path
        core_module = next(m for m in modules if m['path'] == 'core')
        web_module = next(m for m in modules if m['path'] == 'web')

        assert core_module['metadata']['description'] == 'Core library module'
        assert core_module['metadata']['parent']['name'] == ctx.temp_dir.name

        assert web_module['metadata']['description'] == 'Web application'


def test_discover_gradle_no_build_file():
    """Test discover_modules with no build.gradle."""
    with BuildTestContext() as ctx:
        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 0


def test_discover_gradle_kotlin_dsl():
    """Test discover_modules with Kotlin DSL (build.gradle.kts)."""
    with BuildTestContext() as ctx:
        build_gradle_kts = '''
plugins {
    java
}

group = "com.example"
version = "2.0.0"
description = "Kotlin DSL project"
'''
        (ctx.temp_dir / 'build.gradle.kts').write_text(build_gradle_kts)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        assert modules[0]['metadata']['group'] == 'com.example'
        assert modules[0]['metadata']['version'] == '2.0.0'


# =============================================================================
# Test: Source Directory Discovery
# =============================================================================

def test_gradle_discover_sources():
    """Test source directory discovery for Gradle."""
    with BuildTestContext() as ctx:
        # Create build.gradle
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"')

        # Create standard Gradle/Maven layout
        (ctx.temp_dir / 'src' / 'main' / 'java' / 'com').mkdir(parents=True)
        (ctx.temp_dir / 'src' / 'test' / 'java' / 'com').mkdir(parents=True)
        (ctx.temp_dir / 'src' / 'main' / 'resources').mkdir(parents=True)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        sources = modules[0]['sources']

        assert 'src/main/java' in sources['main']
        assert 'src/test/java' in sources['test']
        assert 'src/main/resources' in sources['resources']


# =============================================================================
# Test: Stats
# =============================================================================

def test_gradle_stats_file_counts():
    """Test source and test file counting for Gradle."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"')

        # Create source files
        src_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        src_dir.mkdir(parents=True)
        (src_dir / 'Foo.java').write_text('public class Foo {}')
        (src_dir / 'Bar.java').write_text('public class Bar {}')

        # Create test files
        test_dir = ctx.temp_dir / 'src' / 'test' / 'java' / 'com' / 'example'
        test_dir.mkdir(parents=True)
        (test_dir / 'FooTest.java').write_text('public class FooTest {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        stats = modules[0]['stats']
        assert stats['source_files'] == 2
        assert stats['test_files'] == 1


def test_gradle_stats_has_readme():
    """Test README detection for Gradle."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"')
        (ctx.temp_dir / 'README.md').write_text('# My Project')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['stats']['has_readme'] is True


# =============================================================================
# Test: Module Type Detection
# =============================================================================

def test_gradle_module_type_war():
    """Test WAR module type detection for Gradle."""
    with BuildTestContext() as ctx:
        build_gradle = '''
plugins {
    id 'war'
}
'''
        (ctx.temp_dir / 'build.gradle').write_text(build_gradle)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['metadata']['type'] == 'war'


def test_gradle_module_type_quarkus():
    """Test Quarkus module type detection for Gradle."""
    with BuildTestContext() as ctx:
        build_gradle = '''
plugins {
    id 'java'
    id 'io.quarkus'
}
'''
        (ctx.temp_dir / 'build.gradle').write_text(build_gradle)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['metadata']['type'] == 'quarkus'


# =============================================================================
# Test: Hybrid Modules
# =============================================================================

def test_gradle_hybrid_npm_module():
    """Test detection of hybrid Gradle + npm module."""
    with BuildTestContext() as ctx:
        # Create Gradle project
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"')

        # Add package.json (hybrid)
        (ctx.temp_dir / 'package.json').write_text('{"name": "frontend", "version": "1.0.0"}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        assert 'gradle' in modules[0]['build_systems']
        assert 'npm' in modules[0]['build_systems']
        assert modules[0]['descriptors']['gradle'] == 'build.gradle'
        assert modules[0]['descriptors']['package'] == 'package.json'


# =============================================================================
# Test: Maven Takes Priority
# =============================================================================

def test_maven_takes_priority_over_gradle():
    """Test that Maven modules are not duplicated by Gradle discovery."""
    with BuildTestContext() as ctx:
        # Create both Maven and Gradle files
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>test-project</artifactId>
    <groupId>com.example</groupId>
</project>''')
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        # Should only have one module (Maven takes priority)
        assert len(modules) == 1
        assert 'maven' in modules[0]['build_systems']


# =============================================================================
# Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Basic module discovery
        test_discover_gradle_single_module,
        test_discover_gradle_multi_module,
        test_discover_gradle_no_build_file,
        test_discover_gradle_kotlin_dsl,

        # Source directory discovery
        test_gradle_discover_sources,

        # Stats
        test_gradle_stats_file_counts,
        test_gradle_stats_has_readme,

        # Module type detection
        test_gradle_module_type_war,
        test_gradle_module_type_quarkus,

        # Hybrid modules
        test_gradle_hybrid_npm_module,

        # Priority
        test_maven_takes_priority_over_gradle,
    ])
    sys.exit(runner.run())
