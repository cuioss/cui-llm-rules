#!/usr/bin/env python3
"""Extension API for pm-dev-java bundle.

Provides build system detection and command mappings for Maven and Gradle projects.
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if Java bundle applies to the project.

    Returns True if Maven or Gradle build files exist.
    """
    root = Path(project_root)
    return (
        (root / "pom.xml").exists() or
        (root / "build.gradle").exists() or
        (root / "build.gradle.kts").exists()
    )


def provides_build_systems() -> list:
    """Build system keys this bundle handles."""
    return ["maven", "gradle"]


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Placeholders:
        {module} - replaced by persist with ' --module <name>' or ''
    """
    base_maven = "python3 .plan/execute-script.py pm-dev-java:build-operations:maven run"
    base_gradle = "python3 .plan/execute-script.py pm-dev-java:build-operations:gradle run"

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
