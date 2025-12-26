#!/usr/bin/env python3
"""Abstract base class for extension.py implementations.

Provides default implementations for optional functions while requiring
implementation of essential functions via abstract methods.

Usage:
    from extension_base import ExtensionBase

    class Extension(ExtensionBase):
        def is_applicable(self, project_root: str) -> bool:
            return (Path(project_root) / "pom.xml").exists()

        def get_skill_domains(self) -> dict:
            return {"domain": {...}, "profiles": {...}}

        # Override other methods as needed
"""

from abc import ABC, abstractmethod
from pathlib import Path


class ExtensionBase(ABC):
    """Abstract base class for domain bundle extensions.

    Subclasses must implement:
        - is_applicable: Project detection logic
        - get_skill_domains: Domain metadata and skill profiles

    All other methods have sensible defaults for non-build bundles.
    Build bundles should override build-related methods.
    """

    # =========================================================================
    # Required Methods (must be implemented)
    # =========================================================================

    @abstractmethod
    def is_applicable(self, project_root: str) -> bool:
        """Check if this bundle applies to the project.

        Args:
            project_root: Absolute path to the project root directory.

        Returns:
            True if this bundle should be activated for the project.

        Examples:
            - Check for pom.xml/build.gradle for Java bundles
            - Check for package.json for JavaScript bundles
            - Check for doc/ directory for documentation bundles
        """
        pass

    @abstractmethod
    def get_skill_domains(self) -> dict:
        """Return domain metadata for skill loading.

        Returns:
            Dict with domain identity and profile-based skill organization:
            {
                "domain": {
                    "key": str,          # Unique domain identifier
                    "name": str,         # Human-readable name
                    "description": str   # Domain description
                },
                "profiles": {
                    "core": {"defaults": [...], "optionals": [...]},
                    "implementation": {"defaults": [...], "optionals": [...]},
                    "testing": {"defaults": [...], "optionals": [...]},
                    "quality": {"defaults": [...], "optionals": [...]}
                }
            }
        """
        pass

    # =========================================================================
    # Build System Methods (override for build bundles)
    # =========================================================================

    def provides_build_systems(self) -> list:
        """Return build system keys this bundle handles (static declaration).

        Returns:
            List of build system keys (e.g., ["maven", "gradle"]).
            Empty list if bundle doesn't provide build systems.

        Valid Keys:
            - "maven" - Maven build system
            - "gradle" - Gradle build system
            - "npm" - npm/Node.js build system
        """
        return []

    def get_applicable_build_systems(self, project_root: str) -> list:
        """Return build systems actually present in the project.

        Args:
            project_root: Absolute path to project root.

        Returns:
            List of build system keys present (e.g., ["maven"]).
            Empty list if no applicable build systems found.

        Notes:
            Override this for build bundles to check for actual build files.
            Default implementation returns empty list.
        """
        return []

    def get_command_mappings(self) -> dict:
        """Return canonical command name to script invocation mappings.

        Returns:
            Nested dict: {build_system: {canonical_name: command_template}}
            Empty dict if bundle doesn't provide build commands.

        Template Placeholders:
            {module} - Replaced with ' --module <name>' or '' by persist

        Canonical Names:
            compile, test-compile, module-tests, integration-tests,
            coverage, performance, quality-gate, verify, install, package
        """
        return {}

    # =========================================================================
    # Module Detection Methods (override for build bundles)
    # =========================================================================

    def get_modules(self, project_root: str) -> list:
        """Return project modules detected by this build system.

        Args:
            project_root: Absolute path to project root.

        Returns:
            List of module dicts:
            [{"name": str, "path": str, "build_system": str}]

        Examples:
            - Maven: Parse pom.xml <modules> section
            - Gradle: Parse settings.gradle include() statements
            - npm: Parse package.json workspaces
        """
        return []

    def get_module_type(self, module_path: str) -> str:
        """Return the module type for a given module path.

        Args:
            module_path: Absolute path to module directory.

        Returns:
            Module type string:
            - "pom" - Parent/BOM module (Maven)
            - "jar" - Library module (default)
            - "war" - Web application
            - "quarkus" - Quarkus application
            - "npm" - npm project
        """
        return "jar"

    def get_profiles(self, module_path: str) -> list:
        """Return build profiles for a module.

        Args:
            module_path: Absolute path to module directory.

        Returns:
            List of profile dicts:
            [{
                "id": str,
                "canonical": str | None,
                "activation": {"type": str, ...}
            }]

        Canonical Mappings:
            - integration-tests, it, e2e -> "integration-tests"
            - coverage, jacoco -> "coverage"
            - pre-commit, quality, sonar -> "quality-gate"
            - benchmark, jmh, perf -> "performance"
        """
        return []

    def generate_profile_command(
        self,
        build_system: str,
        canonical: str,
        profile_id: str,
        activation: dict,
        module_name: str = None
    ) -> str | None:
        """Generate a command string for a profile-based canonical command.

        Args:
            build_system: "maven", "gradle", or "npm"
            canonical: The canonical command name (e.g., "integration-tests")
            profile_id: The profile ID to activate
            activation: Dict with activation info (type, property, value)
            module_name: Optional module name for multi-module projects

        Returns:
            Command string or None if not supported
        """
        return None

    # =========================================================================
    # Workflow Extension Methods (override if providing capabilities)
    # =========================================================================

    def provides_triage(self) -> str | None:
        """Return triage skill reference if available.

        Returns:
            Skill reference as 'bundle:skill' (e.g., 'pm-dev-java:java-triage')
            or None if no triage capability.

        Purpose:
            Triage skills categorize and prioritize findings during
            the plan-finalize phase.
        """
        return None

    def provides_outline(self) -> str | None:
        """Return outline skill reference if available.

        Returns:
            Skill reference as 'bundle:skill'
            or None if no outline capability.

        Purpose:
            Outline skills guide solution design during the
            plan-init phase for domain-specific deliverables.
        """
        return None


# =============================================================================
# Singleton Instance Helper
# =============================================================================

def create_extension(extension_class: type) -> 'ExtensionBase':
    """Create and return a singleton extension instance.

    Usage in extension.py:
        class Extension(ExtensionBase):
            ...

        _instance = create_extension(Extension)

        # Module-level function wrappers for backward compatibility
        def is_applicable(project_root: str) -> bool:
            return _instance.is_applicable(project_root)
    """
    return extension_class()
