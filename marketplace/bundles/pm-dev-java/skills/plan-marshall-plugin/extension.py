#!/usr/bin/env python3
"""Extension API for pm-dev-java bundle.

Provides build system detection, module discovery, and command mappings
for Maven and Gradle projects.
"""

import re
from pathlib import Path


# Build file constants
POM_XML = "pom.xml"
BUILD_GRADLE = "build.gradle"
BUILD_GRADLE_KTS = "build.gradle.kts"
SETTINGS_GRADLE = "settings.gradle"
SETTINGS_GRADLE_KTS = "settings.gradle.kts"

# Profile pattern to canonical name mapping
PROFILE_TO_CANONICAL = {
    # Integration test patterns -> "integration-tests"
    "integration-tests": "integration-tests",
    "integration-test": "integration-tests",
    "integrationTest": "integration-tests",
    "it": "integration-tests",
    "e2e": "integration-tests",
    "acceptance": "integration-tests",

    # Coverage patterns -> "coverage"
    "coverage": "coverage",
    "jacoco": "coverage",

    # Quality patterns -> "quality-gate"
    "sonar": "quality-gate",
    "pre-commit": "quality-gate",
    "precommit": "quality-gate",
    "lint": "quality-gate",
    "check": "quality-gate",
    "quality": "quality-gate",

    # Performance patterns -> "performance"
    "benchmark": "performance",
    "benchmarks": "performance",
    "jmh": "performance",
    "perf": "performance",
    "performance": "performance",
    "stress": "performance",
    "load": "performance",
}


def is_applicable(project_root: str) -> bool:
    """Check if Java bundle applies to the project.

    Returns True if Maven or Gradle build files exist.
    """
    root = Path(project_root)
    return (
        (root / POM_XML).exists() or
        (root / BUILD_GRADLE).exists() or
        (root / BUILD_GRADLE_KTS).exists() or
        (root / SETTINGS_GRADLE).exists() or
        (root / SETTINGS_GRADLE_KTS).exists()
    )


def provides_build_systems() -> list:
    """Build system keys this bundle handles."""
    return ["maven", "gradle"]


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Placeholders:
        {module} - replaced by persist with ' --module <name>' or ''
    """
    base_maven = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"
    base_gradle = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run"

    return {
        "maven": {
            "compile": f'{base_maven} --targets "compile"{{module}}',
            "test-compile": f'{base_maven} --targets "test-compile"{{module}}',
            "module-tests": f'{base_maven} --targets "clean test"{{module}}',
            "integration-tests": f'{base_maven} --targets "clean verify -Pintegration-tests"{{module}}',
            "coverage": f'{base_maven} --targets "clean verify -Pcoverage"{{module}}',
            "quality-gate": f'{base_maven} --targets "clean verify -Ppre-commit"{{module}}',
            "verify": f'{base_maven} --targets "clean verify"{{module}}',
            "install": f'{base_maven} --targets "clean install"{{module}}',
            "package": f'{base_maven} --targets "package"{{module}}',
        },
        "gradle": {
            "compile": f'{base_gradle} --targets "compileJava"{{module}}',
            "test-compile": f'{base_gradle} --targets "testClasses"{{module}}',
            "module-tests": f'{base_gradle} --targets "clean test"{{module}}',
            "integration-tests": f'{base_gradle} --targets "clean integrationTest"{{module}}',
            "coverage": f'{base_gradle} --targets "clean test jacocoTestReport"{{module}}',
            "quality-gate": f'{base_gradle} --targets "clean check"{{module}}',
            "verify": f'{base_gradle} --targets "clean build"{{module}}',
            "install": f'{base_gradle} --targets "clean publishToMavenLocal"{{module}}',
            "package": f'{base_gradle} --targets "clean assemble"{{module}}',
        }
    }


def get_skill_domains() -> dict:
    """Domain metadata for skill loading.

    Returns profile-based skill organization for Java development.
    """
    return {
        "domain": {
            "key": "java",
            "name": "Java Development",
            "description": "Java code patterns, CDI, JUnit testing, Maven/Gradle builds"
        },
        "profiles": {
            "core": {
                "defaults": ["pm-dev-java:java-core"],
                "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok"]
            },
            "implementation": {
                "defaults": [],
                "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
            },
            "testing": {
                "defaults": ["pm-dev-java:junit-core"],
                "optionals": ["pm-dev-java:junit-integration"]
            },
            "quality": {
                "defaults": ["pm-dev-java:javadoc"],
                "optionals": []
            }
        }
    }


def provides_triage() -> str | None:
    """Return triage skill reference if available.

    Returns:
        Skill reference like 'bundle:skill' or None if not provided.
    """
    return "pm-dev-java:java-triage"


def provides_outline() -> str | None:
    """Return outline skill reference if available.

    Returns:
        Skill reference like 'bundle:skill' or None if not provided.
    """
    return None


# =============================================================================
# Build System Extensions
# =============================================================================

def get_modules(project_root: str) -> list:
    """Return project modules detected by Maven or Gradle.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of module dicts: {name, path, build_system}
    """
    modules = []
    root = Path(project_root)

    # Detect Maven modules
    modules.extend(_detect_maven_modules(root))

    # Detect Gradle modules
    modules.extend(_detect_gradle_modules(root))

    return modules


def get_module_type(module_path: str) -> str:
    """Return the module type for a given module path.

    Args:
        module_path: Absolute path to module directory.

    Returns:
        Module type: "pom", "jar", "war", or "quarkus"
    """
    path = Path(module_path)

    # Check Maven pom.xml
    pom_path = path / POM_XML
    if pom_path.exists():
        return _detect_maven_module_type(pom_path)

    # Check Gradle build files
    for build_file in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
        gradle_path = path / build_file
        if gradle_path.exists():
            return _detect_gradle_module_type(gradle_path)

    return "jar"  # Default


def get_profiles(module_path: str) -> list:
    """Return build profiles for a module.

    Args:
        module_path: Absolute path to module directory.

    Returns:
        List of profile dicts: {id, canonical, activation}
    """
    path = Path(module_path)
    profiles = []

    # Detect Maven profiles
    pom_path = path / POM_XML
    if pom_path.exists():
        profiles.extend(_detect_maven_profiles(pom_path))

    # Detect Gradle profiles (limited support)
    for settings_file in [SETTINGS_GRADLE_KTS, SETTINGS_GRADLE]:
        settings_path = path / settings_file
        if settings_path.exists():
            profiles.extend(_detect_gradle_profiles(settings_path))
            break

    return profiles


# =============================================================================
# Maven Detection Helpers
# =============================================================================

def _detect_maven_modules(project_dir: Path) -> list:
    """Detect Maven modules from pom.xml."""
    modules = []
    pom_path = project_dir / POM_XML

    if not pom_path.exists():
        return modules

    content = pom_path.read_text()

    # Extract <modules> section
    modules_match = re.search(r'<modules>(.*?)</modules>', content, re.DOTALL)
    if modules_match:
        module_content = modules_match.group(1)
        for module in re.findall(r'<module>([^<]+)</module>', module_content):
            module_path = project_dir / module
            if module_path.exists():
                modules.append({
                    "name": module,
                    "path": module,
                    "build_system": "maven"
                })

    return modules


def _detect_maven_module_type(pom_path: Path) -> str:
    """Detect module type from Maven pom.xml."""
    if not pom_path.exists():
        return "jar"

    content = pom_path.read_text()

    # Check packaging element
    packaging_match = re.search(r'<packaging>([^<]+)</packaging>', content)
    if packaging_match:
        packaging = packaging_match.group(1).strip().lower()
        if packaging == "pom":
            return "pom"
        if packaging == "war":
            return "war"

    # Detect Quarkus from quarkus-maven-plugin
    if "quarkus-maven-plugin" in content:
        return "quarkus"

    return "jar"


def _detect_maven_profiles(pom_path: Path) -> list:
    """Detect Maven profiles from pom.xml."""
    if not pom_path.exists():
        return []

    content = pom_path.read_text()
    profiles = []

    # Find all <profile><id>...</id> patterns
    profile_pattern = re.compile(r'<profile>\s*<id>([^<]+)</id>', re.MULTILINE)
    matches = profile_pattern.findall(content)

    for profile_id in matches:
        profile_id = profile_id.strip()
        canonical = _classify_profile(profile_id)
        activation = _detect_profile_activation(content, profile_id)

        profiles.append({
            "id": profile_id,
            "canonical": canonical,
            "activation": activation,
        })

    return profiles


def _classify_profile(profile_id: str) -> str | None:
    """Classify a profile ID to its canonical name."""
    profile_lower = profile_id.lower()

    # Direct match
    if profile_id in PROFILE_TO_CANONICAL:
        return PROFILE_TO_CANONICAL[profile_id]

    # Case-insensitive match
    for pattern, canonical in PROFILE_TO_CANONICAL.items():
        if pattern.lower() == profile_lower:
            return canonical

    # Partial match (profile contains pattern)
    for pattern, canonical in PROFILE_TO_CANONICAL.items():
        if pattern.lower() in profile_lower:
            return canonical

    return None


def _detect_profile_activation(pom_content: str, profile_id: str) -> dict:
    """Detect how a Maven profile is activated."""
    # Find the profile block
    profile_start = pom_content.find(f'<id>{profile_id}</id>')
    if profile_start == -1:
        return {"type": "command-line"}

    # Find the activation block within this profile
    profile_end = pom_content.find('</profile>', profile_start)
    if profile_end == -1:
        profile_end = len(pom_content)

    profile_block = pom_content[profile_start:profile_end]

    # Check for property activation
    prop_match = re.search(r'<activation>[\s\S]*?<property>[\s\S]*?<name>([^<]+)</name>', profile_block)
    if prop_match:
        prop_name = prop_match.group(1).strip()
        value_match = re.search(r'<property>[\s\S]*?<value>([^<]+)</value>', profile_block)
        value = value_match.group(1).strip() if value_match else None
        return {
            "type": "property",
            "property": prop_name,
            "value": value,
        }

    # Check for activeByDefault
    if '<activeByDefault>true</activeByDefault>' in profile_block:
        return {"type": "default"}

    # Check for JDK activation
    jdk_match = re.search(r'<activation>\s*<jdk>([^<]+)</jdk>', profile_block)
    if jdk_match:
        return {"type": "jdk", "version": jdk_match.group(1).strip()}

    # Check for OS activation
    if '<os>' in profile_block:
        return {"type": "os"}

    # Default: command-line activation via -P
    return {"type": "command-line"}


# =============================================================================
# Gradle Detection Helpers
# =============================================================================

def _detect_gradle_modules(project_dir: Path) -> list:
    """Detect Gradle modules from settings.gradle."""
    modules = []

    for settings_file in [SETTINGS_GRADLE_KTS, SETTINGS_GRADLE]:
        settings_path = project_dir / settings_file
        if settings_path.exists():
            content = settings_path.read_text()

            # Match include("module") or include ':module' patterns
            for match in re.finditer(r'include\s*[(\'"]+:?([^)\'\"]+)[)\'"]+', content):
                module_name = match.group(1).replace(':', '/')
                module_path = project_dir / module_name
                if module_path.exists():
                    modules.append({
                        "name": module_name.replace('/', '-'),
                        "path": module_name,
                        "build_system": "gradle"
                    })
            break

    return modules


def _detect_gradle_module_type(build_file: Path) -> str:
    """Detect module type from Gradle build file."""
    if not build_file.exists():
        return "jar"

    content = build_file.read_text()

    # Check for war plugin
    if "war" in content and ("apply plugin:" in content or "plugins {" in content):
        if "'war'" in content or '"war"' in content:
            return "war"

    # Check for Quarkus
    if "quarkus" in content.lower():
        return "quarkus"

    return "jar"


def _detect_gradle_profiles(_settings_path: Path) -> list:
    """Detect Gradle profiles from settings.gradle.

    Note: Gradle doesn't have native profiles like Maven.
    Returns empty list as Gradle uses tasks, not profiles.
    """
    # Gradle doesn't have Maven-style profiles
    # Profile-like behavior is achieved through tasks and build variants
    return []
