# Extension API Contract

Complete specification for `extension.py` files that domain bundles implement.

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

## Required Functions

All bundles with an `extension.py` must implement these functions.

### is_applicable

```python
def is_applicable(project_root: str) -> bool:
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
- Supplements may use heuristics (e.g., check pom.xml content)

### provides_build_systems

```python
def provides_build_systems() -> list:
    """Return build system keys this bundle handles (static declaration).

    Returns:
        List of build system keys (e.g., ["maven", "gradle"]).
        Empty list if bundle doesn't provide build systems.

    Valid Keys:
        - "maven" - Maven build system
        - "gradle" - Gradle build system
        - "npm" - npm/Node.js build system
    """
```

**Implementation Notes**:
- Return `[]` for bundles that don't provide build capabilities
- Keys must match values expected by `build_env.py`
- This is a static declaration; use `get_applicable_build_systems()` for dynamic detection

### get_applicable_build_systems

```python
def get_applicable_build_systems(project_root: str) -> list:
    """Return build systems that are actually present in the project.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of build system keys present (e.g., ["maven"] or ["gradle"] or both).
        Empty list if no applicable build systems found.

    Notes:
        This function performs file checks to determine which build systems
        are actually present, unlike provides_build_systems() which is static.
    """
```

**Example** (Java):
```python
def get_applicable_build_systems(project_root: str) -> list:
    root = Path(project_root)
    systems = []
    if (root / "pom.xml").exists():
        systems.append("maven")
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        systems.append("gradle")
    return systems
```

**Implementation Notes**:
- Preferred over `provides_build_systems()` when detecting actual build systems
- Called with project_root to check file existence
- Return only build systems with actual files present

### get_command_mappings

```python
def get_command_mappings() -> dict:
    """Return canonical command name to script invocation mappings.

    Returns:
        Nested dict: {build_system: {canonical_name: command_template}}
        Empty dict if bundle doesn't provide build commands.

    Template Placeholders:
        {module} - Replaced with ' --module <name>' or '' by persist

    Canonical Names:
        - compile, test-compile
        - module-tests, integration-tests, coverage, performance
        - quality-gate, verify, install, package
    """
```

**Example**:
```python
def get_command_mappings() -> dict:
    base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"
    return {
        "maven": {
            "module-tests": f'{base} --targets "clean test"{{module}}',
            "quality-gate": f'{base} --targets "clean verify -Ppre-commit"{{module}}',
            "verify": f'{base} --targets "clean verify"{{module}}',
        }
    }
```

---

## Domain Functions

Every extension must implement **exactly one** of these functions.

### get_skill_domains (Primary Domains)

Use for bundles that define a new domain (pm-dev-java, pm-dev-frontend, pm-documents).

```python
def get_skill_domains() -> dict:
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

**Example**:
```python
def get_skill_domains() -> dict:
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
            "testing": {
                "defaults": ["pm-dev-java:junit-core"],
                "optionals": ["pm-dev-java:junit-integration"]
            }
        }
    }
```

### get_domain_supplements (Supplement Bundles)

Use for bundles that extend an existing domain (pm-dev-java-cui extending java).

```python
def get_domain_supplements() -> dict:
    """Return supplementary skills to merge into a parent domain.

    Returns:
        Dict with parent domain reference and additional skills:
        {
            "domain": str,        # Parent domain key to extend
            "description": str,   # Supplement description
            "profiles": {
                "core": {
                    "defaults": list[str],
                    "optionals": list[str]
                },
                ...
            }
        }

    Notes:
        - Skills are merged into the parent domain's profiles
        - Supplement's is_applicable() determines if it activates
        - A project can have multiple supplements for same domain
    """
```

**Example**:
```python
def get_domain_supplements() -> dict:
    return {
        "domain": "java",  # Extends the java domain
        "description": "CUI-specific Java patterns for logging, testing, and HTTP",
        "profiles": {
            "core": {
                "defaults": [],
                "optionals": ["pm-dev-java-cui:cui-logging"]
            },
            "testing": {
                "defaults": [],
                "optionals": ["pm-dev-java-cui:cui-testing"]
            }
        }
    }
```

---

## Optional Functions

These functions enable workflow extensions and build system discovery.

### Workflow Extensions

Return `None` if not provided.

#### provides_triage

```python
def provides_triage() -> str | None:
    """Return triage skill reference if available.

    Returns:
        Skill reference as 'bundle:skill' (e.g., 'pm-dev-java:java-triage')
        or None if no triage capability.

    Purpose:
        Triage skills categorize and prioritize findings during
        the plan-finalize phase.
    """
```

#### provides_outline

```python
def provides_outline() -> str | None:
    """Return outline skill reference if available.

    Returns:
        Skill reference as 'bundle:skill' (e.g., 'pm-plugin-development:plugin-solution-outline')
        or None if no outline capability.

    Purpose:
        Outline skills guide solution design during the
        plan-init phase for domain-specific deliverables.
    """
```

### Build System Extensions

These functions enable domain-specific build detection. Return empty list or "jar" defaults if not applicable.

#### get_modules

```python
def get_modules(project_root: str) -> list:
    """Return project modules detected by this build system.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of module dicts:
        [
            {
                "name": str,           # Module name
                "path": str,           # Relative path from project root
                "build_system": str    # Build system (maven, gradle, npm)
            }
        ]

    Examples:
        - Maven: Parse pom.xml <modules> section
        - Gradle: Parse settings.gradle include() statements
        - npm: Parse package.json workspaces
    """
```

**Example** (Maven):
```python
def get_modules(project_root: str) -> list:
    import re
    from pathlib import Path

    modules = []
    pom_path = Path(project_root) / "pom.xml"

    if not pom_path.exists():
        return modules

    content = pom_path.read_text()
    modules_match = re.search(r'<modules>(.*?)</modules>', content, re.DOTALL)
    if modules_match:
        for module in re.findall(r'<module>([^<]+)</module>', modules_match.group(1)):
            if (Path(project_root) / module).exists():
                modules.append({
                    "name": module,
                    "path": module,
                    "build_system": "maven"
                })

    return modules
```

#### get_module_type

```python
def get_module_type(module_path: str) -> str:
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

    Notes:
        - Check packaging element in pom.xml
        - Check for Quarkus plugin
        - Default to "jar" if unknown
    """
```

**Example** (Maven):
```python
def get_module_type(module_path: str) -> str:
    import re
    from pathlib import Path

    pom_path = Path(module_path) / "pom.xml"
    if not pom_path.exists():
        return "jar"

    content = pom_path.read_text()

    # Check packaging
    match = re.search(r'<packaging>([^<]+)</packaging>', content)
    if match:
        packaging = match.group(1).strip().lower()
        if packaging in ("pom", "war"):
            return packaging

    # Check for Quarkus
    if "quarkus-maven-plugin" in content:
        return "quarkus"

    return "jar"
```

#### get_profiles

```python
def get_profiles(module_path: str) -> list:
    """Return build profiles for a module.

    Args:
        module_path: Absolute path to module directory.

    Returns:
        List of profile dicts:
        [
            {
                "id": str,                    # Profile ID
                "canonical": str | None,      # Canonical command name or None
                "activation": {
                    "type": str,              # command-line, property, jdk, os, default
                    "property": str | None,   # Property name (if type=property)
                    "value": str | None       # Property value (if type=property)
                }
            }
        ]

    Canonical Mappings:
        - integration-tests, it, e2e → "integration-tests"
        - coverage, jacoco → "coverage"
        - pre-commit, quality, sonar → "quality-gate"
        - benchmark, jmh, perf → "performance"
    """
```

**Example** (Maven):
```python
def get_profiles(module_path: str) -> list:
    import re
    from pathlib import Path

    PROFILE_TO_CANONICAL = {
        "integration-tests": "integration-tests",
        "coverage": "coverage",
        "jacoco": "coverage",
        "pre-commit": "quality-gate",
        "benchmark": "performance",
    }

    profiles = []
    pom_path = Path(module_path) / "pom.xml"

    if not pom_path.exists():
        return profiles

    content = pom_path.read_text()
    for profile_id in re.findall(r'<profile>\s*<id>([^<]+)</id>', content):
        canonical = None
        for pattern, name in PROFILE_TO_CANONICAL.items():
            if pattern in profile_id.lower():
                canonical = name
                break
        profiles.append({
            "id": profile_id.strip(),
            "canonical": canonical,
            "activation": {"type": "command-line"}
        })

    return profiles
```

#### generate_profile_command

```python
def generate_profile_command(
    build_system: str,
    canonical: str,
    profile_id: str,
    activation: dict,
    module_name: str = None
) -> str | None:
    """Generate a command string for a profile-based canonical command.

    Args:
        build_system: "maven" or "gradle"
        canonical: The canonical command name (e.g., "integration-tests")
        profile_id: The profile ID to activate
        activation: Dict with activation info (type, property, value)
        module_name: Optional module name for multi-module projects

    Returns:
        Command string or None if build system not supported

    Notes:
        This is called by build_env.py to generate commands for profiles
        that have canonical mappings. It encapsulates build-system-specific
        command generation logic.
    """
```

**Example** (Java):
```python
def generate_profile_command(
    build_system: str,
    canonical: str,
    profile_id: str,
    activation: dict,
    module_name: str = None
) -> str | None:
    if build_system == "maven":
        if activation.get("type") == "property":
            prop_name = activation.get("property", "")
            prop_value = activation.get("value")
            if prop_value:
                targets = f"clean verify -D{prop_name}={prop_value}"
            else:
                targets = f"clean verify -D{prop_name}"
        else:
            targets = f"clean verify -P{profile_id}"

        cmd = f'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets "{targets}"'

    elif build_system == "gradle":
        cmd = f'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run --targets "clean {profile_id}"'

    else:
        return None

    if module_name and module_name != "default":
        cmd += f" --module {module_name}"

    return cmd
```

---

## Complete Extension Template

```python
#!/usr/bin/env python3
"""Extension API for {bundle-name} bundle.

{Description of what this bundle provides.}
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if this bundle applies to the project."""
    root = Path(project_root)
    # Implement detection logic
    return (root / "indicator-file").exists()


def provides_build_systems() -> list:
    """Build system keys this bundle handles."""
    return []  # or ["maven", "gradle", "npm"]


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template."""
    return {}  # or nested dict with templates


def get_skill_domains() -> dict:
    """Domain metadata for skill loading."""
    return {
        "domain": {
            "key": "domain-key",
            "name": "Domain Name",
            "description": "Domain description"
        },
        "profiles": {
            "core": {"defaults": [], "optionals": []},
            "implementation": {"defaults": [], "optionals": []},
            "testing": {"defaults": [], "optionals": []},
            "quality": {"defaults": [], "optionals": []}
        }
    }


def provides_triage() -> str | None:
    """Return triage skill reference if available."""
    return None  # or "bundle:triage-skill"


def provides_outline() -> str | None:
    """Return outline skill reference if available."""
    return None  # or "bundle:outline-skill"
```

---

## Validation

Extensions are validated by `plugin-doctor extension`:

```bash
python3 .plan/execute-script.py pm-plugin-development:plugin-doctor:validate extension \
    --extension path/to/extension.py
```

Validation checks:
- All required functions present
- Exactly one domain function present (get_skill_domains OR get_domain_supplements)
- Functions are callable
- No syntax errors
- get_skill_domains() returns valid structure with domain.key, domain.name, profiles
- Skill references (bundle:skill) point to existing skills
- Build bundles cover required canonical commands (module-tests, quality-gate, verify)
- provides_triage() and provides_outline() references exist if non-null

---

## Existing Extensions

| Bundle | Domain Key | Build Systems | Triage | Outline |
|--------|------------|---------------|--------|---------|
| pm-dev-java | java | maven, gradle | java-triage | - |
| pm-dev-frontend | javascript | npm | javascript-triage | - |
| pm-documents | documentation | - | - | - |
| pm-requirements | requirements | - | - | - |
| pm-plugin-development | plan-marshall-plugin-dev | - | plugin-triage | - |
