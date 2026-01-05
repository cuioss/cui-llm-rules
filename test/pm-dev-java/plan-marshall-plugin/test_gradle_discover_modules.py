#!/usr/bin/env python3
"""Tests for discover_modules() Gradle support in Java extension.

Tests the unified module discovery API for Gradle projects against
the contract defined in build-project-structure.md.

Contract requirements:
- technology: single string (not build_systems array)
- paths: object with module, descriptor, sources, tests, readme
- metadata: snake_case fields (artifact_id, group_id)
- stats: only source_files, test_files
- commands: resolved canonical command strings
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

        # Contract: use paths.module not path
        assert module['paths']['module'] == '.'
        # Contract: use technology not build_systems
        assert module['technology'] == 'gradle'
        # Contract: packaging not group/version (those aren't extracted for Gradle)
        assert module['metadata']['packaging'] == 'jar'


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
        (core_dir / 'build.gradle').write_text('apply plugin: "java"')

        # Create web module
        web_dir = ctx.temp_dir / 'web'
        web_dir.mkdir()
        (web_dir / 'build.gradle').write_text('apply plugin: "java"')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 2

        # Find modules by paths.module
        core_module = next(m for m in modules if m['paths']['module'] == 'core')
        web_module = next(m for m in modules if m['paths']['module'] == 'web')

        assert core_module['technology'] == 'gradle'
        assert web_module['technology'] == 'gradle'


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
        # Contract: technology is gradle
        assert modules[0]['technology'] == 'gradle'
        # Contract: descriptor path
        assert modules[0]['paths']['descriptor'] == 'build.gradle.kts'


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

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        # Contract: use paths.sources and paths.tests
        paths = modules[0]['paths']

        assert 'src/main/java' in paths['sources']
        assert 'src/test/java' in paths['tests']


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


def test_gradle_kotlin_sources_detected():
    """Test Kotlin source files are detected and counted."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle.kts').write_text('plugins { kotlin("jvm") }')

        # Create Kotlin source files
        src_dir = ctx.temp_dir / 'src' / 'main' / 'kotlin' / 'com' / 'example'
        src_dir.mkdir(parents=True)
        (src_dir / 'App.kt').write_text('class App')
        (src_dir / 'Service.kt').write_text('class Service')

        # Create Kotlin test files
        test_dir = ctx.temp_dir / 'src' / 'test' / 'kotlin' / 'com' / 'example'
        test_dir.mkdir(parents=True)
        (test_dir / 'AppTest.kt').write_text('class AppTest')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        paths = modules[0]['paths']
        stats = modules[0]['stats']

        # Kotlin sources should be detected
        assert 'src/main/kotlin' in paths['sources'], "Kotlin source dir not in paths.sources"
        assert 'src/test/kotlin' in paths['tests'], "Kotlin test dir not in paths.tests"
        assert stats['source_files'] == 2, f"Expected 2 Kotlin source files, got {stats['source_files']}"
        assert stats['test_files'] == 1, f"Expected 1 Kotlin test file, got {stats['test_files']}"


def test_gradle_groovy_sources_detected():
    """Test Groovy source files are detected and counted."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "groovy"')

        # Create Groovy source files
        src_dir = ctx.temp_dir / 'src' / 'main' / 'groovy' / 'com' / 'example'
        src_dir.mkdir(parents=True)
        (src_dir / 'Script.groovy').write_text('class Script {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        paths = modules[0]['paths']
        stats = modules[0]['stats']

        assert 'src/main/groovy' in paths['sources'], "Groovy source dir not in paths.sources"
        assert stats['source_files'] == 1, f"Expected 1 Groovy source file, got {stats['source_files']}"


def test_gradle_scala_sources_detected():
    """Test Scala source files are detected and counted."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "scala"')

        # Create Scala source files
        src_dir = ctx.temp_dir / 'src' / 'main' / 'scala' / 'com' / 'example'
        src_dir.mkdir(parents=True)
        (src_dir / 'App.scala').write_text('object App')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        paths = modules[0]['paths']
        stats = modules[0]['stats']

        assert 'src/main/scala' in paths['sources'], "Scala source dir not in paths.sources"
        assert stats['source_files'] == 1, f"Expected 1 Scala source file, got {stats['source_files']}"


def test_gradle_mixed_jvm_languages():
    """Test mixed Java/Kotlin/Groovy project counts all files."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"\napply plugin: "kotlin"')

        # Create Java source
        java_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com'
        java_dir.mkdir(parents=True)
        (java_dir / 'JavaClass.java').write_text('public class JavaClass {}')

        # Create Kotlin source
        kotlin_dir = ctx.temp_dir / 'src' / 'main' / 'kotlin' / 'com'
        kotlin_dir.mkdir(parents=True)
        (kotlin_dir / 'KotlinClass.kt').write_text('class KotlinClass')

        # Create Groovy source
        groovy_dir = ctx.temp_dir / 'src' / 'main' / 'groovy' / 'com'
        groovy_dir.mkdir(parents=True)
        (groovy_dir / 'GroovyClass.groovy').write_text('class GroovyClass {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        paths = modules[0]['paths']
        stats = modules[0]['stats']

        # All source directories should be listed
        assert 'src/main/java' in paths['sources']
        assert 'src/main/kotlin' in paths['sources']
        assert 'src/main/groovy' in paths['sources']

        # Total source count should include all languages
        assert stats['source_files'] == 3, f"Expected 3 mixed source files, got {stats['source_files']}"


def test_gradle_kotlin_only_module_has_compile_command():
    """Test Kotlin-only module gets compile command."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle.kts').write_text('plugins { kotlin("jvm") }')

        # Create Kotlin source (no Java)
        src_dir = ctx.temp_dir / 'src' / 'main' / 'kotlin' / 'com'
        src_dir.mkdir(parents=True)
        (src_dir / 'App.kt').write_text('class App')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        commands = modules[0]['commands']

        # Compile should be present because there are sources
        assert 'compile' in commands, "Kotlin-only module should have compile command"


def test_gradle_stats_readme_in_paths():
    """Test README is in paths.readme, not stats."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"')
        (ctx.temp_dir / 'README.md').write_text('# My Project')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        # Contract: readme is in paths, not stats
        assert 'has_readme' not in modules[0]['stats']
        assert modules[0]['paths']['readme'] == 'README.md'


# =============================================================================
# Test: Commands
# =============================================================================

def test_gradle_module_has_commands():
    """Test Gradle module has canonical commands."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'build.gradle').write_text('apply plugin: "java"')

        # Create source and test files
        src_dir = ctx.temp_dir / 'src' / 'main' / 'java'
        src_dir.mkdir(parents=True)
        (src_dir / 'App.java').write_text('public class App {}')
        test_dir = ctx.temp_dir / 'src' / 'test' / 'java'
        test_dir.mkdir(parents=True)
        (test_dir / 'AppTest.java').write_text('public class AppTest {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        commands = modules[0]['commands']

        # Contract: canonical commands (clean is separate per canonical-commands.md)
        assert 'clean' in commands, "clean should be a separate command"
        assert 'quality-gate' in commands
        assert 'verify' in commands
        assert 'install' in commands
        assert 'clean-install' in commands, "clean-install should be available"
        assert 'package' in commands
        assert 'compile' in commands
        assert 'module-tests' in commands

        # Verify clean is NOT embedded in other commands (except clean-install)
        assert 'clean' not in commands['verify'], "verify should not include clean"
        assert 'clean' not in commands['module-tests'], "module-tests should not include clean"


# =============================================================================
# Test: No Duplicate Modules
# =============================================================================

def test_no_duplicate_modules_with_both_build_files():
    """Test that modules are not duplicated when both pom.xml and build.gradle exist.

    Note: Maven discovery requires Maven commands to succeed. In a test environment
    without a valid Maven setup, Maven modules are skipped and Gradle takes over.
    This test verifies no duplication occurs in either case.
    """
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

        # Should only have one module (no duplication)
        assert len(modules) == 1
        # Technology depends on whether Maven is available
        # In test environment, Maven fails so Gradle is used
        assert modules[0]['technology'] in ['maven', 'gradle']


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
        test_gradle_kotlin_sources_detected,
        test_gradle_groovy_sources_detected,
        test_gradle_scala_sources_detected,
        test_gradle_mixed_jvm_languages,
        test_gradle_kotlin_only_module_has_compile_command,
        test_gradle_stats_readme_in_paths,

        # Commands
        test_gradle_module_has_commands,

        # No duplication
        test_no_duplicate_modules_with_both_build_files,
    ])
    sys.exit(runner.run())
