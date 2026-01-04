#!/usr/bin/env python3
"""Extension API for pm-dev-java bundle.

Minimal wrapper providing build system detection, module discovery,
and command mappings for Maven and Gradle projects.

Implementation logic resides in scripts/ directory.
"""

import sys
from pathlib import Path

from extension_base import ExtensionBase

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# Build file constants
POM_XML = "pom.xml"
BUILD_GRADLE = "build.gradle"
BUILD_GRADLE_KTS = "build.gradle.kts"
SETTINGS_GRADLE = "settings.gradle"
SETTINGS_GRADLE_KTS = "settings.gradle.kts"


class Extension(ExtensionBase):
    """Java/Maven/Gradle extension for pm-dev-java bundle."""

    def provides_build_systems(self) -> list:
        """Build system keys this bundle handles."""
        return ["maven", "gradle"]

    def get_applicable_build_systems(self, project_root: str) -> list:
        """Return build systems actually present in the project."""
        root = Path(project_root)
        systems = []

        if (root / POM_XML).exists():
            systems.append("maven")

        if any((root / f).exists() for f in [BUILD_GRADLE, BUILD_GRADLE_KTS, SETTINGS_GRADLE, SETTINGS_GRADLE_KTS]):
            systems.append("gradle")

        return systems

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
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

    def provides_triage(self) -> str | None:
        """Return triage skill reference."""
        return "pm-dev-java:java-triage"

    def discover_modules(self, project_root: str) -> list:
        """Discover all modules with complete metadata.

        Delegates to maven_cmd_discover.py and gradle discovery.
        """
        modules = []
        root = Path(project_root)

        # Maven modules
        if (root / POM_XML).exists():
            from maven_cmd_discover import discover_maven_modules
            modules.extend(discover_maven_modules(project_root))

        # Gradle modules (only if no Maven at same path)
        maven_paths = {m['paths']['module'] for m in modules}
        gradle_modules = self._discover_gradle_modules(root)
        for gm in gradle_modules:
            if gm['paths']['module'] not in maven_paths:
                modules.append(gm)

        return modules

    def get_profiles(self, module_path: str) -> list:
        """Return build profiles for a module."""
        path = Path(module_path)
        profiles = []

        pom_path = path / POM_XML
        if pom_path.exists():
            from maven_cmd_discover import _extract_profiles
            content = pom_path.read_text()
            profiles.extend(_extract_profiles(content))

        return profiles

    def generate_profile_command(
        self,
        build_system: str,
        canonical: str,
        profile_id: str,
        activation: dict,
        module_name: str = None
    ) -> str | None:
        """Generate a command string for a profile-based canonical command."""
        if build_system == "maven":
            from maven_cmd_discover import _generate_profile_command
            return _generate_profile_command(profile_id, activation, module_name)
        return None

    # =========================================================================
    # Gradle Discovery
    # =========================================================================

    def _discover_gradle_modules(self, project_dir: Path) -> list:
        """Discover Gradle modules with contract-compliant structure."""
        import re
        modules = []

        # Check for settings.gradle
        settings_path = None
        for sf in [SETTINGS_GRADLE_KTS, SETTINGS_GRADLE]:
            if (project_dir / sf).exists():
                settings_path = project_dir / sf
                break

        if settings_path:
            content = settings_path.read_text()
            for match in re.finditer(r'include\s*[(\'"]+:?([^)\'\"]+)[)\'"]+', content):
                module_name = match.group(1).replace(':', '/')
                module_path = project_dir / module_name
                if module_path.exists():
                    module_data = self._extract_gradle_module(module_path, project_dir, module_name)
                    if module_data:
                        modules.append(module_data)
        else:
            # Single-module
            for bf in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
                if (project_dir / bf).exists():
                    module_data = self._extract_gradle_module(project_dir, project_dir, "")
                    if module_data:
                        modules.append(module_data)
                    break

        return modules

    def _extract_gradle_module(self, module_path: Path, _project_root: Path, relative_path: str) -> dict | None:
        """Extract Gradle module with contract-compliant structure."""
        import re
        from build_discover import find_readme

        build_file = None
        for bf in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
            if (module_path / bf).exists():
                build_file = module_path / bf
                break

        if not build_file:
            return None

        content = build_file.read_text()

        # Extract name
        name = module_path.name
        for pattern in [r'archivesBaseName\s*=\s*[\'"]([^\'"]+)[\'"]']:
            match = re.search(pattern, content)
            if match:
                name = match.group(1)
                break

        # Source directories
        sources = {"main": [], "test": []}
        if (module_path / "src" / "main" / "java").exists():
            sources["main"].append("src/main/java")
        if (module_path / "src" / "test" / "java").exists():
            sources["test"].append("src/test/java")

        source_paths = [f"{relative_path}/{s}" if relative_path else s for s in sources["main"]]
        test_paths = [f"{relative_path}/{t}" if relative_path else t for t in sources["test"]]

        readme = find_readme(str(module_path))
        readme_path = f"{relative_path}/{readme}" if readme and relative_path else readme

        # Commands
        base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run"
        if name and name != ".":
            commands = {
                "module-tests": f'{base} --targets "clean test" --module {name}',
                "verify": f'{base} --targets "clean build" --module {name}'
            }
        else:
            commands = {
                "module-tests": f'{base} --targets "clean test"',
                "verify": f'{base} --targets "clean build"'
            }

        return {
            "name": name,
            "technology": "gradle",
            "paths": {
                "module": relative_path if relative_path else ".",
                "descriptor": f"{relative_path}/{build_file.name}" if relative_path else build_file.name,
                "sources": source_paths,
                "tests": test_paths,
                "readme": readme_path
            },
            "metadata": {
                "artifact_id": name,
                "group_id": None,
                "packaging": "jar",
                "description": None,
                "parent": None,
                "profiles": None
            },
            "packages": {},
            "dependencies": [],
            "stats": {
                "source_files": sum(len(list((module_path / s).rglob("*.java"))) for s in sources["main"] if (module_path / s).exists()),
                "test_files": sum(len(list((module_path / t).rglob("*.java"))) for t in sources["test"] if (module_path / t).exists())
            },
            "commands": commands
        }
