# Extension API Architecture Overview

High-level view of the extension system: how modules are discovered, enriched, and persisted.

## System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         1. EXTENSION DISCOVERY                               │
│                                                                              │
│  extension.py: discover_extensions(project_root)                            │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                 │
│  │ pm-dev-java    │  │ pm-dev-frontend│  │ pm-documents   │                 │
│  │ extension.py   │  │ extension.py   │  │ extension.py   │                 │
│  │                │  │                │  │                │                 │
│  │ is_applicable? │  │ is_applicable? │  │ is_applicable? │                 │
│  │ pom.xml exists │  │ package.json   │  │ doc/ exists    │                 │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                 │
│          │                   │                   │                           │
│          ▼                   ▼                   ▼                           │
│  [applicable extensions for this project]                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         2. MODULE DISCOVERY                                  │
│                                                                              │
│  Per applicable extension: extension.discover_modules(project_root)         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ build_discover.py (base library)                                    │    │
│  │                                                                     │    │
│  │ discover_descriptors(project_root, "pom.xml")                       │    │
│  │   → [pom.xml, mod-a/pom.xml, mod-b/pom.xml]                        │    │
│  │                                                                     │    │
│  │ build_module_base(project_root, descriptor_path)                    │    │
│  │   → ModuleBase(name, paths)                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Extension-specific enrichment                                       │    │
│  │                                                                     │    │
│  │ Maven: ./mvnw help:all-profiles dependency:tree → profiles, deps   │    │
│  │ npm:   npm pkg get name version → metadata                         │    │
│  │                                                                     │    │
│  │ Returns per module:                                                 │    │
│  │ {                                                                   │    │
│  │   name, technology, paths, metadata, packages,                      │    │
│  │   dependencies, stats, commands                                     │    │
│  │ }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         3. ORCHESTRATOR AGGREGATION                          │
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
│  │   - commands (merge, second wins on conflict)                       │    │
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
│                         4. CONFIGURATION PERSISTENCE                         │
│                                                                              │
│  build_env.py: persist --project-dir .                                       │
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
│                         5. STRUCTURE ENRICHMENT                              │
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
| 1. Extension Discovery | project_root | Check is_applicable() per bundle | List of applicable extensions |
| 2. Module Discovery | project_root | discover_descriptors() + enrichment | List of module dicts per extension |
| 3. Orchestrator | Module lists | Merge hybrid modules | `.plan/raw-project-data.json` |
| 4. Configuration | raw-project-data.json | Extract commands | `.plan/marshal.json` modules section |
| 5. Enrichment | raw-project-data.json | LLM analysis | `.plan/project-structure.json` |

## Key Files

| File | Purpose | When Created |
|------|---------|--------------|
| `.plan/raw-project-data.json` | Raw module data from all extensions | Step 3: collect-raw-data |
| `.plan/marshal.json` | Runtime config with commands | Step 4: build_env persist |
| `.plan/project-structure.json` | Enriched structure with descriptions | Step 5: generate + enrich |

## Library Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BASE LIBRARIES (extension-api)                       │
│                                                                              │
│  extension_base.py   │ Abstract base class, canonical commands              │
│  extension.py        │ Extension discovery, loading, aggregation            │
│  build_discover.py   │ Descriptor discovery, path building                  │
│  build_env.py        │ Command persistence and lookup                       │
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

## Invocation Examples

### Full Discovery Flow

```bash
# 1. Collect raw data from all extensions
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  collect-raw-data --project-root /path/to/project

# 2. Persist commands to marshal.json
python3 .plan/execute-script.py plan-marshall:extension-api:build_env \
  persist --project-dir /path/to/project

# 3. Generate enrichable structure
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  generate
```

### Command Lookup

```bash
# Look up a canonical command for a module
python3 .plan/execute-script.py plan-marshall:extension-api:build_env \
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
