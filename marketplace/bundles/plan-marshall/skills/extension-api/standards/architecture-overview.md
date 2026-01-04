# Extension API Architecture Overview

High-level view of the extension system: how modules are discovered, enriched, and persisted.

## System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         1. MODULE DISCOVERY                                  │
│                                                                              │
│  Per extension: extension.discover_modules(project_root)                    │
│  Extensions that find no descriptors return empty list (no-op)              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Step 1a: Find descriptors (base library)                           │    │
│  │                                                                     │    │
│  │ build_discover.discover_descriptors(project_root, "pom.xml")        │    │
│  │   → [pom.xml, mod-a/pom.xml, mod-b/pom.xml]                        │    │
│  │                                                                     │    │
│  │ build_discover.build_module_base(project_root, descriptor_path)     │    │
│  │   → ModuleBase(name, paths)                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Step 1b: Extract metadata (extension-specific)                      │    │
│  │                                                                     │    │
│  │ Maven: ./mvnw help:all-profiles dependency:tree                     │    │
│  │   → profiles, dependencies, groupId, artifactId, packaging          │    │
│  │                                                                     │    │
│  │ npm: npm pkg get name version description                           │    │
│  │   → name, version, scripts                                          │    │
│  │                                                                     │    │
│  │ Extension scans source directories:                                 │    │
│  │   → packages (Java: from directory structure)                       │    │
│  │   → stats (source_files, test_files counts)                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Step 1c: Resolve commands (from templates)                          │    │
│  │                                                                     │    │
│  │ extension.get_command_mappings() returns templates:                 │    │
│  │   {"maven": {                                                       │    │
│  │     "module-tests": 'python3 ... --targets "clean test"{module}',   │    │
│  │     "quality-gate": 'python3 ... --targets "clean verify"{module}', │    │
│  │     "verify": 'python3 ... --targets "clean verify"{module}'        │    │
│  │   }}                                                                │    │
│  │                                                                     │    │
│  │ Extension resolves {module} placeholder per module:                 │    │
│  │   → commands: {"module-tests": "python3 ... --module mod-a", ...}  │    │
│  │                                                                     │    │
│  │ Profile-based enhancement (from detected profiles):                 │    │
│  │   quality-gate + pre-commit profile → add "-Ppre-commit" to command │    │
│  │                                                                     │    │
│  │ See: canonical-commands.md for command vocabulary                   │    │
│  │ See: extension_base.CANONICAL_COMMANDS for required/optional        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  Returns per module:                                                         │
│  { name, technology, paths, metadata, packages, dependencies, stats,        │
│    commands }                                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         2. ORCHESTRATOR AGGREGATION                          │
│                                                                              │
│  project-structure skill: collect_raw_data(project_root)                     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ For each extension:                                                 │    │
│  │   modules = extension.discover_modules(project_root)                │    │
│  │                                                                     │    │
│  │ Hybrid module detection:                                            │    │
│  │   Same directory with pom.xml + package.json                        │    │
│  │   → Merge into single module with build_systems: [maven, npm]      │    │
│  │                                                                     │    │
│  │ Merge rules:                                                        │    │
│  │   - technology → build_systems (aggregate)                          │    │
│  │   - paths.sources, paths.tests (concatenate)                        │    │
│  │   - commands (nest by build system for conflicts)                   │    │
│  │   - dependencies (deduplicate)                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  Output: .plan/raw-project-data.json                                         │
│  {                                                                           │
│    "project_root": "/path/to/project",                                       │
│    "modules": { "mod-a": {...}, "mod-b": {...} },                           │
│    "extensions_used": ["pm-dev-java", "pm-dev-frontend"]                    │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         3. CONFIGURATION PERSISTENCE                         │
│                                                                              │
│  manage_project_structure.py: persist --project-dir .                        │
│                                                                              │
│  Reads: .plan/raw-project-data.json                                          │
│  Writes: .plan/marshal.json (modules section)                                │
│                                                                              │
│  {                                                                           │
│    "modules": {                                                              │
│      "mod-a": {                                                              │
│        "path": "mod-a",                                                      │
│        "type": "jar",                                                        │
│        "build_systems": ["maven"],                                           │
│        "commands": {                                                         │
│          "module-tests": "python3 .plan/execute-script.py ... --module ...", │
│          "quality-gate": "...",                                              │
│          "verify": "..."                                                     │
│        }                                                                     │
│      }                                                                       │
│    }                                                                         │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         4. STRUCTURE ENRICHMENT                              │
│                                                                              │
│  project-structure skill: generate + LLM enrichment                          │
│                                                                              │
│  Reads: .plan/raw-project-data.json                                          │
│  Writes: .plan/project-structure.json                                        │
│                                                                              │
│  {                                                                           │
│    "project": { "name": "...", "description": "..." },                       │
│    "modules": {                                                              │
│      "mod-a": {                                                              │
│        "responsibility": "Core business logic for...",     ← LLM enriched   │
│        "key_packages": {                                                     │
│          "com.example.core": {                                               │
│            "path": "...",                                                    │
│            "description": "Provides..."                    ← LLM enriched   │
│          }                                                                   │
│        }                                                                     │
│      }                                                                       │
│    },                                                                        │
│    "placement": { ... },                                                     │
│    "conventions": { ... }                                                    │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Summary

| Step | Input | Process | Output |
|------|-------|---------|--------|
| 1a. Find Descriptors | project_root | discover_descriptors() per extension | List of descriptor paths |
| 1b. Extract Metadata | descriptors | Build tool commands + source scanning | metadata, packages, stats |
| 1c. Resolve Commands | templates + module | get_command_mappings() + placeholder resolution | commands dict |
| 2. Orchestrator | Module lists | Merge hybrid modules | `.plan/raw-project-data.json` |
| 3. Configuration | raw-project-data.json | Copy commands to config | `.plan/marshal.json` |
| 4. Enrichment | raw-project-data.json | LLM analysis | `.plan/project-structure.json` |

## Command Mapping Rules

Commands are defined and resolved at multiple levels:

| Level | Location | Purpose |
|-------|----------|---------|
| **Vocabulary** | [canonical-commands.md](canonical-commands.md) | Defines canonical names (module-tests, quality-gate, verify, etc.) |
| **Constants** | `extension_base.CANONICAL_COMMANDS` | Required/optional flags, phase assignments |
| **Templates** | `extension.get_command_mappings()` | Build-system-specific templates with `{module}` placeholder |
| **Resolution** | `extension.discover_modules()` | Replaces `{module}` placeholder, applies profile enhancements |

**Required commands** (must exist for non-pom modules):
- `module-tests` - Unit tests
- `quality-gate` - Static analysis, linting
- `verify` - Full verification

**Profile enhancement example**:
```
Template: 'python3 ... --targets "clean verify"{module}'
Detected profile: pre-commit (canonical: quality-gate)
Enhanced command: 'python3 ... --targets "clean verify -Ppre-commit" --module mod-a'
```

## Default Module

The **default module** represents the project root directory itself. It has:
- `path: "."` - The project root
- `name: "default"` - Reserved module name
- Commands without `--module` flag - Operates on entire project

For single-module projects, the default module is the only module. For multi-module projects, it represents aggregator/parent build operations.

## Key Files

| File | Owner | Purpose |
|------|-------|---------|
| `.plan/raw-project-data.json` | `project-structure` | Raw module data from all extensions |
| `.plan/marshal.json` | `project-structure` | Runtime config with resolved commands |
| `.plan/project-structure.json` | `project-structure` | Enriched structure with descriptions |

## Library Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BASE LIBRARIES (extension-api)                       │
│                                                                              │
│  extension_base.py   │ Abstract base class, canonical commands              │
│  extension.py        │ Extension discovery, loading, aggregation            │
│  build_discover.py   │ Descriptor discovery, path building                  │
│  build_result.py     │ Log file creation, result construction               │
│  build_parse.py      │ Issue structures, warning filtering                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ used by
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOMAIN EXTENSIONS                                    │
│                                                                              │
│  pm-dev-java/extension.py       │ Maven/Gradle detection, profile parsing   │
│  pm-dev-frontend/extension.py   │ npm detection, package.json parsing       │
│  pm-documents/extension.py      │ Documentation detection                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ orchestrated by
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR (project-structure skill)               │
│                                                                              │
│  manage_project_structure.py                                                 │
│    collect-raw-data  │ Discover all modules, merge hybrids                  │
│    generate          │ Create initial project-structure.json                │
│    read              │ Output structure as TOON                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Canonical Data Structure

Each extension returns modules in this format:

```json
{
  "name": "module-name",
  "technology": "maven",
  "paths": {
    "module": "relative/path",
    "descriptor": "relative/path/pom.xml",
    "sources": ["src/main/java"],
    "tests": ["src/test/java"],
    "readme": "README.adoc"
  },
  "metadata": {
    "artifact_id": "...",
    "group_id": "...",
    "packaging": "jar",
    "profiles": [{"id": "...", "canonical": "...", "activation": {...}}]
  },
  "packages": {
    "com.example.core": {"path": "...", "package_info": "..."}
  },
  "dependencies": ["groupId:artifactId:scope"],
  "stats": {"source_files": 45, "test_files": 38},
  "commands": {
    "module-tests": "python3 .plan/execute-script.py ...",
    "quality-gate": "...",
    "verify": "..."
  }
}
```

**Hybrid modules** (after orchestrator merge) have nested commands:

```json
{
  "name": "hybrid-module",
  "build_systems": ["maven", "npm"],
  "commands": {
    "module-tests": {
      "maven": "python3 ... --module hybrid-module",
      "npm": "python3 ... --package hybrid-module"
    },
    "lint": "python3 ... --package hybrid-module"
  }
}
```

Commands provided by both extensions become nested objects. Commands unique to one extension remain as strings.

## Invocation Examples

### Full Discovery Flow

```bash
# 1. Collect raw data from all extensions
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  collect-raw-data --project-root /path/to/project

# 2. Persist commands to marshal.json
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  persist --project-dir /path/to/project

# 3. Generate enrichable structure
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  generate
```

### Command Lookup

```bash
# Look up a canonical command for a module
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  lookup --canonical "module-tests" --module "my-module"
```

## Related Specifications

| Document | Purpose |
|----------|---------|
| [extension-contract.md](extension-contract.md) | Extension API methods |
| [build-project-structure.md](build-project-structure.md) | Module discovery output structure |
| [build-base-libs.md](build-base-libs.md) | Base library API reference |
| [canonical-commands.md](canonical-commands.md) | Command vocabulary |
| [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) | Orchestrator merge logic |
