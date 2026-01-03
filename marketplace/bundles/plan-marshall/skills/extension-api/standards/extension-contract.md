# Extension API Contract

Complete specification for `extension.py` files that domain bundles implement. All extensions **must** inherit from `ExtensionBase`.

## File Location

Extensions are located at:
```
marketplace/bundles/{bundle}/skills/plan-marshall-plugin/extension.py
```

At runtime, they're discovered from the plugin cache:
```
~/.claude/plugins/cache/plan-marshall/{bundle}/1.0.0/skills/plan-marshall-plugin/extension.py
```

---

## ExtensionBase Import

All extensions must import and inherit from `ExtensionBase`:

```python
from extension_base import ExtensionBase

class Extension(ExtensionBase):
    # Implement required methods
    ...
```

The `extension_base` module is automatically injected into `sys.modules` when extensions are loaded.

---

## Required Methods (Abstract)

All extensions must implement these methods - they are abstract in `ExtensionBase`.

### is_applicable

```python
def is_applicable(self, project_root: str) -> bool:
    """Check if this bundle applies to the project.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        True if this bundle should be activated for the project.
        False otherwise.

    Examples:
        - Check for pom.xml/build.gradle for Java bundles
        - Check for package.json for JavaScript bundles
        - Check for doc/ directory for documentation bundles
    """
```

**Implementation Notes**:
- Must be deterministic (same project → same result)
- Should be fast (file existence checks, not content analysis)
- May use heuristics (e.g., check pom.xml content for specific patterns)

### get_skill_domains

```python
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
                "core": {
                    "defaults": list[str],    # Always-loaded skills
                    "optionals": list[str]    # On-demand skills
                },
                "implementation": {...},
                "testing": {...},
                "quality": {...}
            }
        }

    Profile Categories:
        - core: Foundation patterns and standards
        - implementation: Runtime patterns (CDI, frameworks)
        - testing: Test frameworks and patterns
        - quality: Documentation, code quality
    """
```

---

## Optional Methods (With Defaults)

These methods have default implementations in `ExtensionBase`. Override only when needed.

### Build System Methods

#### provides_build_systems

```python
def provides_build_systems(self) -> list:
    """Return build system keys this bundle handles (static declaration).

    Returns:
        List of build system keys (e.g., ["maven", "gradle"]).
        Empty list if bundle doesn't provide build systems.

    Valid Keys:
        - "maven" - Maven build system
        - "gradle" - Gradle build system
        - "npm" - npm/Node.js build system

    Default: []
    """
```

#### get_applicable_build_systems

```python
def get_applicable_build_systems(self, project_root: str) -> list:
    """Return build systems that are actually present in the project.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of build system keys present (e.g., ["maven"] or ["gradle"] or both).
        Empty list if no applicable build systems found.

    Default: []
    """
```

#### get_command_mappings

```python
def get_command_mappings(self) -> dict:
    """Return canonical command name to script invocation mappings.

    Returns:
        Nested dict: {build_system: {canonical_name: command_template}}
        Empty dict if bundle doesn't provide build commands.

    Template Placeholders:
        {module} - Replaced with ' --module <name>' or '' by persist

    Default: {}
    """
```

**Profile-Based Commands**: The following canonical commands are **profile-dependent** and should NOT be included in `get_command_mappings()`:
- `integration-tests` - Generated from detected profiles matching "integration", "it", "e2e", etc.
- `coverage` - Generated from detected profiles matching "coverage", "jacoco"
- `performance` - Generated from detected profiles matching "benchmark", "jmh", "perf"
- `quality-gate` - Generated from detected profiles matching "pre-commit", "sonar", "quality"

These commands are dynamically generated via `get_profiles()` + `generate_profile_command()` to ensure portability across projects with different profile naming conventions.

**Example using constants**:
```python
from extension_base import (
    ExtensionBase,
    CMD_COMPILE,
    CMD_TEST_COMPILE,
    CMD_MODULE_TESTS,
    CMD_VERIFY,
    CMD_INSTALL,
    CMD_PACKAGE,
)

class Extension(ExtensionBase):
    def get_command_mappings(self) -> dict:
        # NOTE: Profile-dependent commands (integration-tests, coverage, quality-gate)
        # are NOT included here - they are dynamically generated from detected profiles
        base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"
        return {
            "maven": {
                CMD_COMPILE: f'{base} --targets "compile"{{module}}',
                CMD_TEST_COMPILE: f'{base} --targets "test-compile"{{module}}',
                CMD_MODULE_TESTS: f'{base} --targets "clean test"{{module}}',
                CMD_VERIFY: f'{base} --targets "clean verify"{{module}}',
                CMD_INSTALL: f'{base} --targets "clean install"{{module}}',
                CMD_PACKAGE: f'{base} --targets "package"{{module}}',
            }
        }
```

### Module Discovery Methods

#### discover_modules (Primary API)

```python
def discover_modules(self, project_root: str) -> list:
    """Discover all modules with complete metadata.

    This is the primary API for module discovery. Returns comprehensive
    module information including metadata, dependencies, packages, and stats.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of module dicts with complete structure:
        [{
            "name": str,              # Module name
            "technology": str,        # Build system (e.g., "maven", "npm")
            "paths": {
                "module": str,        # Relative path from project root
                "descriptor": str,    # Path to build descriptor
                "sources": [str],     # Source directories
                "tests": [str],       # Test directories
                "readme": str | None  # Path to README if exists
            },
            "metadata": {
                "artifact_id": str | None,
                "group_id": str | None,
                "packaging": str | None,
                "description": str | None,
                "parent": str | None  # groupId:artifactId format
            },
            "packages": {
                "package.name": {
                    "path": str,
                    "package_info": str | None  # If package-info.java exists
                }
            },
            "dependencies": [str],    # groupId:artifactId:scope format
            "stats": {
                "source_files": int,
                "test_files": int
            }
        }]

    Default: []

    See: build-project-structure.md for complete output specification
    """
```

**Implementation Notes**:
- Uses `technology` field (single value per extension)
- All paths are project-relative
- Orchestrator merges results for hybrid modules (see [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md))

### Legacy Module Detection Methods

> **Deprecated**: These methods are retained for backward compatibility. New extensions should use `discover_modules()` instead.

#### get_modules

```python
def get_modules(self, project_root: str) -> list:
    """Return project modules detected by this build system.

    DEPRECATED: Use discover_modules() instead.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of module dicts:
        [{"name": str, "path": str, "build_system": str}]

    Default: []
    """
```

#### get_module_type

```python
def get_module_type(self, module_path: str) -> str:
    """Return the module type for a given module path.

    DEPRECATED: Use discover_modules() instead - returns packaging in metadata.

    Args:
        module_path: Absolute path to module directory.

    Returns:
        Module type string:
        - "unknown" - Default for non-build bundles
        - "pom" - Parent/BOM module (Maven)
        - "jar" - Library module (Java)
        - "war" - Web application
        - "quarkus" - Quarkus application
        - "npm" - npm project

    Default: "unknown"
    """
```

#### get_profiles

```python
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

    Notes:
        Use self.classify_profile() to map profile IDs to canonical names.

    Default: []
    """
```

#### classify_profile (Helper)

```python
def classify_profile(self, profile_id: str) -> str | None:
    """Classify a profile ID to its canonical command name.

    Args:
        profile_id: The profile identifier (e.g., "integration-tests", "jacoco")

    Returns:
        Canonical command name or None if not recognized.

    Notes:
        Uses PROFILE_PATTERNS vocabulary. Supports:
        - Exact match
        - Case-insensitive match
        - Substring match
    """
```

### Command Template Helpers

#### build_command_template

```python
def build_command_template(
    self,
    bundle: str,
    script: str,
    targets: str,
    include_module_placeholder: bool = True
) -> str:
    """Build a standardized command template for get_command_mappings().

    Provides consistent command template generation across all build bundles.

    Args:
        bundle: Bundle name (e.g., "pm-dev-java", "pm-dev-frontend")
        script: Script name within plan-marshall-plugin (e.g., "maven", "npm")
        targets: Build targets/goals (e.g., "clean test", "run build")
        include_module_placeholder: Whether to append {module} placeholder

    Returns:
        Command template string like:
        'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets "clean test"{module}'
    """
```

**Example usage**:
```python
def get_command_mappings(self) -> dict:
    return {
        "maven": {
            CMD_COMPILE: self.build_command_template("pm-dev-java", "maven", "compile"),
            CMD_VERIFY: self.build_command_template("pm-dev-java", "maven", "clean verify"),
        }
    }
```

### Workflow Extension Methods

#### provides_triage

```python
def provides_triage(self) -> str | None:
    """Return triage skill reference if available.

    Returns:
        Skill reference as 'bundle:skill' (e.g., 'pm-dev-java:java-triage')
        or None if no triage capability.

    Default: None
    """
```

#### provides_outline

```python
def provides_outline(self) -> str | None:
    """Return outline skill reference if available.

    Returns:
        Skill reference as 'bundle:skill'
        or None if no outline capability.

    Default: None
    """
```

---

## Canonical Constants

Import constants from `extension_base` for type-safe command references:

```python
from extension_base import (
    CMD_COMPILE,
    CMD_TEST_COMPILE,
    CMD_MODULE_TESTS,
    CMD_INTEGRATION_TESTS,
    CMD_COVERAGE,
    CMD_PERFORMANCE,
    CMD_QUALITY_GATE,
    CMD_VERIFY,
    CMD_INSTALL,
    CMD_PACKAGE,
    ALL_CANONICAL_COMMANDS,
    PROFILE_PATTERNS,
)
```

---

## Complete Extension Examples

### Minimal Extension (Skill-Only Domain)

```python
#!/usr/bin/env python3
"""Extension API for pm-documents bundle."""

from pathlib import Path
from extension_base import ExtensionBase


class Extension(ExtensionBase):
    """Documentation extension for pm-documents bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if documentation bundle applies to the project."""
        return (Path(project_root) / "doc").is_dir()

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
        return {
            "domain": {
                "key": "documentation",
                "name": "Documentation",
                "description": "AsciiDoc documentation, ADRs, and interface specifications"
            },
            "profiles": {
                "core": {
                    "defaults": ["pm-documents:cui-documentation"],
                    "optionals": []
                },
                "implementation": {
                    "defaults": [],
                    "optionals": ["pm-documents:adr-management"]
                },
                "testing": {"defaults": [], "optionals": []},
                "quality": {"defaults": [], "optionals": []}
            }
        }
```

### Build Bundle Extension (With Commands)

```python
#!/usr/bin/env python3
"""Extension API for pm-dev-java bundle."""

from pathlib import Path
from extension_base import (
    ExtensionBase,
    CMD_MODULE_TESTS,
    CMD_VERIFY,
    CMD_INSTALL,
)


class Extension(ExtensionBase):
    """Java/Maven extension for pm-dev-java bundle."""

    def is_applicable(self, project_root: str) -> bool:
        return (Path(project_root) / "pom.xml").exists()

    def provides_build_systems(self) -> list:
        return ["maven"]

    def get_applicable_build_systems(self, project_root: str) -> list:
        root = Path(project_root)
        if (root / "pom.xml").exists():
            return ["maven"]
        return []

    def get_command_mappings(self) -> dict:
        # NOTE: Profile-dependent commands (integration-tests, coverage, quality-gate)
        # are dynamically generated from detected profiles via get_profiles()
        base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"
        return {
            "maven": {
                CMD_MODULE_TESTS: f'{base} --targets "clean test"{{module}}',
                CMD_VERIFY: f'{base} --targets "clean verify"{{module}}',
                CMD_INSTALL: f'{base} --targets "clean install"{{module}}',
            }
        }

    def get_skill_domains(self) -> dict:
        return {
            "domain": {
                "key": "java",
                "name": "Java Development",
                "description": "Java code patterns, JUnit testing, Maven builds"
            },
            "profiles": {
                "core": {"defaults": ["pm-dev-java:java-core"], "optionals": []},
                "implementation": {"defaults": [], "optionals": []},
                "testing": {"defaults": ["pm-dev-java:junit-core"], "optionals": []},
                "quality": {"defaults": ["pm-dev-java:javadoc"], "optionals": []}
            }
        }

    def provides_triage(self) -> str | None:
        return "pm-dev-java:java-triage"

    def get_profiles(self, module_path: str) -> list:
        # Use inherited classify_profile() helper
        profiles = []
        for profile_id in self._detect_profiles(module_path):
            profiles.append({
                "id": profile_id,
                "canonical": self.classify_profile(profile_id),
                "activation": {"type": "command-line"}
            })
        return profiles
```

---

## Validation

Extensions are validated by `plugin-doctor extension`:

```bash
python3 .plan/execute-script.py pm-plugin-development:plugin-doctor:validate extension \
    --extension path/to/extension.py
```

Validation checks:
- Extension class exists and inherits from ExtensionBase
- Required methods implemented (is_applicable, get_skill_domains)
- No syntax errors
- get_skill_domains() returns valid structure with domain.key, domain.name, profiles
- Skill references (bundle:skill) point to existing skills
- Build bundles cover required canonical commands (module-tests, quality-gate, verify)
- provides_triage() and provides_outline() references exist if non-null

---

## Additive Bundles

Some domain bundles are **additive** - they extend a base domain bundle rather than standing alone. Additive bundles:

- Apply **in addition to** a base bundle (both `is_applicable()` return true)
- Do **not** provide their own triage - they rely on the base bundle's triage skill
- Add specialized skills for a subset of projects within the base domain

**Example**: `pm-dev-java-cui` is additive to `pm-dev-java`:
- Applies when pom.xml contains CUI dependencies
- Provides CUI-specific logging/testing skills
- Relies on `pm-dev-java:java-triage` for triage (no `provides_triage()` override)

---

## Existing Extensions

| Bundle | Domain Key | Build Systems | Triage | Outline | Notes |
|--------|------------|---------------|--------|---------|-------|
| pm-dev-java | java | maven, gradle | java-triage | - | Base Java bundle |
| pm-dev-java-cui | java-cui | - | - | - | Additive to pm-dev-java |
| pm-dev-frontend | javascript | npm | javascript-triage | - | |
| pm-documents | documentation | - | documentation-triage | - | |
| pm-requirements | requirements | - | requirements-triage | - | |
| pm-plugin-development | plan-marshall-plugin-dev | - | plugin-triage | plugin-solution-outline | |

---

## Related Specifications

- [build-execution.md](build-execution.md) - Build command execution API
- [build-return.md](build-return.md) - Build return value structure
- [build-project-structure.md](build-project-structure.md) - Project structure discovery
- [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) - Orchestrator flow and hybrid merging
- [canonical-commands.md](canonical-commands.md) - Command vocabulary
