# Build Base Libraries

Complete specification for shared base libraries in the extension-api.

## Purpose

The extension-api provides shared infrastructure for domain bundle extensions (pm-dev-java, pm-dev-frontend). These libraries centralize:

- **Extension system**: Abstract base class, discovery, loading
- **Build environment**: Detection, command generation, persistence
- **Module discovery**: Finding descriptors, building paths
- **Execution support**: Log file creation, result dict construction
- **Issue parsing**: Shared data structures, warning filtering

## Library Summary

### Existing Libraries (Implemented)

| Library | Location | Responsibility |
|---------|----------|----------------|
| `extension_base.py` | extension-api/scripts | Abstract base class, canonical commands, profile patterns |
| `extension.py` | extension-api/scripts | Extension discovery, loading, aggregation |
| `build_env.py` | extension-api/scripts | CLI for detection, persistence, command lookup |

### Planned Libraries

Additional base libraries are planned. See `.plan/improve-project-structure/plan/refactor-build-system-plan.md` for implementation details.

### External Dependencies

| Library | Location | Responsibility |
|---------|----------|----------------|
| `toon_parser.py` | toon-usage/scripts | TOON serialization |
| `run_config.py` | run-config/scripts | Timeout get/set, adaptive learning |

**Output formatting**: Use `toon_parser.serialize_toon()` for TOON output, `json.dumps(data, indent=2)` for JSON.

**Not in base libraries** (build-system-specific):
- Wrapper detection (`./mvnw`, `./gradlew`, npm/npx)
- Command flag construction (`-l`, `-P`, `--workspace`)
- Log level marker parsing (`[INFO]`, `[WARNING]`, `[ERROR]`)
- Stack trace extraction and association
- Error/warning regex patterns (compilation errors, test failures)
- Log output format handling
- Descriptor content parsing (pom.xml, package.json, build.gradle)
- Source/test directory conventions (src/main/java vs src/)
- Package discovery (Java packages vs npm exports)
- Dependency extraction

---

## Existing Libraries

### 1. extension_base.py - Abstract Base Class

Defines the extension contract that all domain bundles must implement.

**Location**: `plan-marshall/skills/extension-api/scripts/extension_base.py`

**Responsibility**:
- Define canonical command constants and metadata
- Profile classification patterns (derived from command aliases)
- Abstract methods extensions must implement
- Default implementations for optional methods

#### Canonical Command Constants

Exports command constants (`CMD_COMPILE`, `CMD_MODULE_TESTS`, etc.), the `CANONICAL_COMMANDS` metadata dict, and `PROFILE_PATTERNS` for profile classification.

See [canonical-commands.md](canonical-commands.md) for the complete command vocabulary and definitions.

#### Abstract Base Class

```python
class ExtensionBase(ABC):
    """Abstract base class for domain bundle extensions."""

    # Required - must be implemented
    @abstractmethod
    def is_applicable(self, project_root: str) -> bool: ...

    @abstractmethod
    def get_skill_domains(self) -> dict: ...

    # Build system methods - override for build bundles
    def provides_build_systems(self) -> list: ...
    def get_applicable_build_systems(self, project_root: str) -> list: ...
    def get_command_mappings(self) -> dict: ...

    # Module discovery - primary API
    def discover_modules(self, project_root: str) -> list: ...

    # Legacy module detection - for backward compatibility
    def get_modules(self, project_root: str) -> list: ...
    def get_module_type(self, module_path: str) -> str: ...
    def get_profiles(self, module_path: str) -> list: ...

    # Helper methods
    def classify_profile(self, profile_id: str) -> str | None: ...
    def generate_profile_command(...) -> str | None: ...
    def build_command_template(...) -> str: ...

    # Workflow extension methods
    def provides_triage(self) -> str | None: ...
    def provides_outline(self) -> str | None: ...
```

### 2. extension.py - Extension Discovery

Single source of truth for discovering and loading extension.py files from domain bundles.

**Location**: `plan-marshall/skills/extension-api/scripts/extension.py`

**Responsibility**:
- Find extension.py files in bundles (source and cache structures)
- Load extension modules and instantiate Extension classes
- Inject `extension_base` into sys.modules for import
- Aggregate data from multiple extensions

#### API

```python
def get_plugin_cache_path() -> Path:
    """Get plugin cache path from environment or default."""

def get_marketplace_bundles_path() -> Path:
    """Get path to marketplace bundles directory (source or cache)."""

def load_extension_module(extension_path: Path, bundle_name: str):
    """Load an extension.py module and instantiate the Extension class."""

def find_extension_path(bundle_dir: Path) -> Path | None:
    """Find extension.py path in a bundle directory."""

def discover_all_extensions() -> list:
    """Discover all extension.py files in bundles (no applicability check)."""

def discover_extensions(project_root: Path) -> list:
    """Discover applicable extensions for a project."""

# Aggregation functions
def get_build_systems_from_extensions(extensions: list, project_root: Path = None) -> list:
def get_command_mappings_from_extensions(extensions: list) -> dict:
def get_skill_domains_from_extensions(extensions: list) -> list:
def get_modules_from_extensions(extensions: list, project_root: Path) -> list:
def get_workflow_extensions_from_extensions(extensions: list) -> dict:
def generate_profile_command_from_extensions(...) -> str | None:
```

### 3. build_env.py - Build Environment CLI

CLI for build system detection, command generation, and persistence.

**Location**: `plan-marshall/skills/extension-api/scripts/build_env.py`

**Responsibility**:
- Detect available build systems in a project
- Detect modules, module types, and profiles
- Generate and persist module commands to marshal.json
- Command lookup API for canonical → executable mapping

#### Subcommands

```
build-env.py detect --project-dir <dir> [--format <format>]
build-env.py detect-modules --project-dir <dir>
build-env.py detect-module-type --module <module>
build-env.py detect-profiles --module <module>
build-env.py persist --project-dir <dir> [--dry-run] [--minimal]
build-env.py lookup --canonical <name> --module <module>
build-env.py get-available-commands --module <module>
build-env.py validate-required --module <module>
```

#### Key Functions

```python
def detect_build_systems(project_dir: Path) -> dict:
    """Detect all available build systems via extensions."""

def detect_all_modules(project_dir: Path) -> list:
    """Detect all modules from all build systems via extensions."""

def detect_module_type_for_path(module_path: Path) -> str:
    """Detect module type via extensions (prioritizes specific types)."""

def detect_profiles_for_module(module_path: Path) -> list:
    """Detect profiles for a module via extensions."""

def lookup_command(canonical: str, module: str, config: dict, build_system: str = None) -> str | dict | None:
    """Look up executable command for a canonical name and module."""

def validate_required_commands(module: str, config: dict) -> list:
    """Validate that required commands are configured for a module."""
```

---

## Integration Pattern

### Layer Separation

```
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Extensions                           │
│  pm-dev-java/extension.py         pm-dev-frontend/extension.py  │
│  - Descriptor parsing (pom.xml)   - Descriptor parsing (pkg)    │
│  - Source dir conventions         - Source dir conventions      │
│  - Metadata extraction            - Metadata extraction         │
│  pm-dev-java/direct_command.py    pm-dev-frontend/direct_command.py │
│  - Wrapper detection (./mvnw)     - npm/npx detection           │
│  - Maven flags (-l, -P, -pl)      - Workspace flags (--workspace)│
│  - Module targeting               - Package targeting            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 extension-api Base Libraries                     │
│                                                                  │
│  extension_base.py  - Abstract base class, canonical commands   │
│  extension.py       - Extension discovery, loading, aggregation │
│  build_env.py       - CLI: detect, persist, lookup              │
│                                                                  │
│  See .plan/improve-project-structure/plan/refactor-build-system-plan.md │
│  for planned execution support libraries                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   External Dependencies                          │
│  toon_parser.py (toon-usage)    - TOON serialization            │
│  run_config.py (run-config)     - Timeout get/set               │
└─────────────────────────────────────────────────────────────────┘
```

The `module` parameter (Maven) or `package` parameter (npm) scopes builds to specific project modules. Log files are organized by module scope.

## Import Resolution

Base libraries live in `extension-api/scripts/` and are imported by domain extensions.

### From Domain Extensions

```python
# pm-dev-java/skills/plan-marshall-plugin/scripts/extension.py

import sys
from pathlib import Path

# Add extension-api scripts to path
SCRIPT_DIR = Path(__file__).parent
BUNDLES_DIR = SCRIPT_DIR.parent.parent.parent.parent
EXTENSION_API_DIR = BUNDLES_DIR / "plan-marshall" / "skills" / "extension-api" / "scripts"
sys.path.insert(0, str(EXTENSION_API_DIR))

# Now import base libraries
from extension_base import ExtensionBase, CMD_MODULE_TESTS, CMD_VERIFY
```

## Testing Requirements

Tests for extension-api libraries are in `test/plan-marshall/extension-api/`:

```
test/plan-marshall/extension-api/
├── test_extension_base.py
├── test_extension.py
└── test_build_env.py
```

Key test scenarios:
1. **extension_base**: Canonical command constants, profile pattern matching, classify_profile()
2. **extension**: Bundle discovery, extension loading, aggregation functions
3. **build_env**: Detection subcommands, command generation, lookup API

Note: `toon_parser.py` has its own tests in `test/plan-marshall/toon-usage/`.

## Compliance

Implementations must:

- [ ] Inherit from `ExtensionBase` for domain extensions
- [ ] Use canonical command constants from `extension_base`
- [ ] Use `extension.py` for discovery and aggregation
- [ ] Use `build_env.py` for detection and persistence

## Related Specifications

- [build-execution.md](build-execution.md) - Execution API contract
- [build-return.md](build-return.md) - Return value structure
- [build-project-structure.md](build-project-structure.md) - Module discovery
- [extension-contract.md](extension-contract.md) - Extension API
