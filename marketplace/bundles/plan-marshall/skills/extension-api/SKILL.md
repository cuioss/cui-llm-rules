---
name: extension-api
description: Extension API for domain bundle discovery, build system detection, and command generation
allowed-tools: Read, Bash
---

# Extension API Skill

Unified API for domain bundle extensions, build system detection, and command generation. Provides the `ExtensionBase` abstract base class that all domain extensions must inherit from.

## Purpose

- **ExtensionBase ABC** - Abstract base class with required/optional methods
- **Canonical constants** - `CMD_*` constants for command names
- **Profile patterns** - `PROFILE_PATTERNS` vocabulary for classification
- **Discovery utilities** - Loading and discovering extensions

## When to Reference This Skill

Reference when:
- Creating a new `extension.py` for a domain bundle
- Detecting build systems in a project
- Generating or looking up build commands
- Understanding canonical command names

## Skill Structure

```
extension-api/
├── SKILL.md                        # This file
├── scripts/
│   ├── extension_base.py           # ExtensionBase ABC (REQUIRED)
│   ├── extension.py                # Extension discovery utilities
│   └── build_env.py                # Build detection and command generation
└── standards/
    ├── extension-contract.md       # Class specification and contracts
    └── canonical-commands.md       # Canonical command vocabulary
```

---

## Quick Reference

All extensions **must** inherit from `ExtensionBase` and implement required methods.

### Required Methods (Abstract)

| Method | Purpose |
|--------|---------|
| `is_applicable(project_root: str) -> bool` | Detect if bundle applies to project |
| `get_skill_domains() -> dict` | Return domain metadata with profiles |

### Optional Methods (With Defaults)

| Method | Default | Purpose |
|--------|---------|---------|
| `provides_build_systems() -> list` | `[]` | Return build system keys |
| `get_command_mappings() -> dict` | `{}` | Return command templates |
| `get_applicable_build_systems(project_root) -> list` | `[]` | Detect build systems |
| `provides_triage() -> str \| None` | `None` | Return triage skill reference |
| `provides_outline() -> str \| None` | `None` | Return outline skill reference |
| `get_modules(project_root: str) -> list` | `[]` | Return project modules |
| `get_module_type(module_path: str) -> str` | `"unknown"` | Return module type |
| `get_profiles(module_path: str) -> list` | `[]` | Return build profiles |
| `classify_profile(profile_id: str) -> str \| None` | Pattern match | Classify profile to canonical |

---

## Scripts

| Script | Type | Purpose |
|--------|------|---------|
| extension_base.py | Library | ExtensionBase ABC, constants, helpers |
| extension.py | Library | Extension discovery functions |
| build_env.py | CLI | Build detection and command generation |

### Build Environment CLI

```bash
# Detect build systems in a project
python3 .plan/execute-script.py plan-marshall:extension-api:build_env detect \
    --project-dir /path/to/project

# Detect project modules
python3 .plan/execute-script.py plan-marshall:extension-api:build_env detect-modules \
    --project-dir /path/to/project

# Generate and persist commands to marshal.json
python3 .plan/execute-script.py plan-marshall:extension-api:build_env persist \
    --project-dir /path/to/project

# Look up canonical command for a module
python3 .plan/execute-script.py plan-marshall:extension-api:build_env lookup \
    --canonical module-tests --module default

# List available commands for a module
python3 .plan/execute-script.py plan-marshall:extension-api:build_env get-available-commands \
    --module default
```

### Python Import Usage

Scripts can import discovery functions directly:

```python
import sys
from pathlib import Path

# Add extension-api scripts to path
extension_api_path = Path(__file__).parent.parent.parent / "extension-api" / "scripts"
sys.path.insert(0, str(extension_api_path))

from extension import (
    discover_extensions,
    discover_all_extensions,
    get_build_systems_from_extensions,
    get_command_mappings_from_extensions,
    get_skill_domains_from_extensions,
    get_modules_from_extensions,
)

# Usage
extensions = discover_extensions(Path("/path/to/project"))
build_systems = get_build_systems_from_extensions(extensions)
```

---

## Canonical Command Constants

Import from `extension_base` for type-safe command references:

```python
from extension_base import (
    CMD_COMPILE,           # "compile"
    CMD_TEST_COMPILE,      # "test-compile"
    CMD_MODULE_TESTS,      # "module-tests"
    CMD_INTEGRATION_TESTS, # "integration-tests"
    CMD_COVERAGE,          # "coverage"
    CMD_PERFORMANCE,       # "performance"
    CMD_QUALITY_GATE,      # "quality-gate"
    CMD_VERIFY,            # "verify"
    CMD_INSTALL,           # "install"
    CMD_PACKAGE,           # "package"
    ALL_CANONICAL_COMMANDS,
    PROFILE_PATTERNS,      # Profile ID to canonical mapping
)
```

| Constant | Value | Required | Description |
|----------|-------|----------|-------------|
| `CMD_MODULE_TESTS` | `module-tests` | Yes | Unit tests for the module |
| `CMD_QUALITY_GATE` | `quality-gate` | Yes | Static analysis, linting |
| `CMD_VERIFY` | `verify` | Yes | Full verification |
| `CMD_COMPILE` | `compile` | No | Compile production sources |
| `CMD_INTEGRATION_TESTS` | `integration-tests` | No | Integration tests |
| `CMD_COVERAGE` | `coverage` | No | Coverage measurement |
| `CMD_INSTALL` | `install` | No | Install to local repository |
| `CMD_PACKAGE` | `package` | No | Create deployable artifact |

---

## Minimal Extension Template

```python
#!/usr/bin/env python3
"""Extension API for {bundle-name} bundle."""

from pathlib import Path
from extension_base import ExtensionBase


class Extension(ExtensionBase):
    """Extension for {bundle-name} bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if this bundle applies to the project."""
        return (Path(project_root) / "indicator-file").exists()

    def get_skill_domains(self) -> dict:
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
```

---

## Integration Points

- **plan-marshall-config** - Uses `discover_all_extensions()` for domain configuration
- **plugin-doctor** - Uses extension discovery for validation
- **Domain bundles** - Implement `extension.py` inheriting from `ExtensionBase`

---

## References

- `standards/extension-contract.md` - Complete class specification and contracts
- `standards/canonical-commands.md` - Canonical command vocabulary
