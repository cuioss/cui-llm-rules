---
name: extension-api
description: Extension API for domain bundle discovery, build system detection, and command generation
allowed-tools: Read, Bash
---

# Extension API Skill

Unified API for domain bundle extensions, build system detection, and command generation. Provides the contract specification for `extension.py` files and shared utilities.

## Purpose

- **Contract specification** for extension.py function signatures
- **Build system detection** across Maven, Gradle, and npm projects
- **Command generation** from canonical vocabulary to executable commands
- **Shared discovery** utilities for loading extensions

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
│   ├── extension.py                # Extension discovery utilities
│   └── build_env.py                # Build detection and command generation
└── standards/
    ├── extension-contract.md       # Function signatures and contracts
    └── canonical-commands.md       # Canonical command vocabulary
```

---

## Quick Reference

### Required Functions (All Bundles)

| Function | Purpose |
|----------|---------|
| `is_applicable(project_root: str) -> bool` | Detect if bundle applies to project |
| `provides_build_systems() -> list` | Return build system keys (or `[]`) |
| `get_command_mappings() -> dict` | Return command templates (or `{}`) |

### Domain Function

| Function | Purpose |
|----------|---------|
| `get_skill_domains() -> dict` | Return domain metadata with profiles |

### Optional Functions

| Function | Purpose |
|----------|---------|
| `provides_triage() -> str \| None` | Return triage skill reference |
| `provides_outline() -> str \| None` | Return outline skill reference |
| `get_modules(project_root: str) -> list` | Return project modules |
| `get_module_type(module_path: str) -> str` | Return module type (jar, npm, etc.) |
| `get_profiles(module_path: str) -> list` | Return build profiles |

---

## Scripts

| Script | Notation | Purpose |
|--------|----------|---------|
| extension | `plan-marshall:extension-api:extension` | Extension discovery utilities |
| build_env | `plan-marshall:extension-api:build_env` | Build detection and command generation |

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

### Extension Discovery CLI

```bash
# List applicable extensions for a project
python3 .plan/execute-script.py plan-marshall:extension-api:extension list \
    --project-dir /path/to/project

# List all available extensions
python3 .plan/execute-script.py plan-marshall:extension-api:extension list-all

# Get build systems from applicable extensions
python3 .plan/execute-script.py plan-marshall:extension-api:extension get-build-systems \
    --project-dir /path/to/project

# Get skill domains
python3 .plan/execute-script.py plan-marshall:extension-api:extension get-skill-domains
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

## Canonical Commands

Standard command names that extensions implement. See `standards/canonical-commands.md` for full specification.

| Canonical Name | Required | Description |
|----------------|----------|-------------|
| `module-tests` | Yes | Unit tests for the module |
| `quality-gate` | Yes | Static analysis, linting |
| `verify` | Yes | Full verification |
| `compile` | No | Compile production sources |
| `integration-tests` | No | Integration tests |
| `coverage` | No | Coverage measurement |
| `install` | No | Install to local repository |
| `package` | No | Create deployable artifact |

---

## Integration Points

- **plan-marshall-config** - Uses `discover_all_extensions()` for domain configuration
- **plugin-doctor** - Uses extension discovery for validation
- **Domain bundles** - Implement `extension.py` per contract specification

---

## References

- `standards/extension-contract.md` - Complete function signatures and contracts
- `standards/canonical-commands.md` - Canonical command vocabulary
