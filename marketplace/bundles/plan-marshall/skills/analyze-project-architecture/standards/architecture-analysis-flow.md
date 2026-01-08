# Architecture Analysis Flow

How to analyze a project's architecture starting from module discovery.

## Overview

```
+------------------------------------------------------------------+
|                    ARCHITECTURE ANALYSIS FLOW                      |
+------------------------------------------------------------------+

  Step 1: Module Discovery
  ========================

  +-----------------------+
  |  discover_project_    |
  |  modules(project_root)|
  +-----------------------+
            |
            v
  +-----------------------+
  | Raw module data:      |
  | - paths               |
  | - commands            |
  | - metadata            |
  | - build_systems       |
  +-----------------------+
            |
            | See: extension-api/standards/architecture-overview.md
            | for discovery internals
            |
            v
  Step 2: Documentation Gathering
  ================================

  For each module in result:

  +-------------------+     +-------------------+     +-------------------+
  | README.md/adoc    |     | package-info.java |     | Source samples    |
  +-------------------+     +-------------------+     +-------------------+
            |                        |                        |
            +------------------------+------------------------+
                                     |
                                     v
  +------------------------------------------------------------------+
  | Documentation findings per module:                                |
  | - responsibility (from README)                                    |
  | - key_packages (from package-info.java)                          |
  | - tips (from source patterns)                                     |
  +------------------------------------------------------------------+
            |
            | See: documentation-sources.md
            | for reading priorities
            |
            v
  Step 3: Structure Enrichment
  ============================

  +------------------------------------------------------------------+
  | project-structure.json                                            |
  |                                                                   |
  | {                                                                 |
  |   "project": { "name": "...", "description": "..." },            |
  |   "modules": {                                                    |
  |     "mod-a": {                                                    |
  |       "responsibility": "...",   <-- from Step 2                 |
  |       "key_packages": {...},     <-- from Step 2                 |
  |       "commands": {...},         <-- from Step 1                 |
  |       "paths": {...}             <-- from Step 1                 |
  |     }                                                             |
  |   }                                                               |
  | }                                                                 |
  +------------------------------------------------------------------+
```

## Step 1: Module Discovery

Call `discover_project_modules()` to get raw module data.

```python
from extension import discover_project_modules

result = discover_project_modules(project_root)
modules = result["modules"]
extensions_used = result["extensions_used"]
```

**Output structure reference**: See [extension-api architecture-overview.md](../../extension-api/standards/architecture-overview.md#module-data-structure)

### What You Get

| Field | Source | Use |
|-------|--------|-----|
| `paths.module` | Extension | Module location |
| `paths.sources` | Extension | Where to look for code |
| `paths.descriptor` | Extension | Build file type |
| `technology`/`build_systems` | Extension | Build system(s) |
| `commands` | Extension | Available commands |
| `metadata` | Extension | Packaging, profiles |

## Step 2: Documentation Gathering

For each module, gather documentation following priority order.

```
+------------------------------------------------------------------+
|                    DOCUMENTATION PRIORITY                          |
+------------------------------------------------------------------+

  Project Level                    Module Level
  =============                    ============

  Priority 1:                      Priority 1:
  README.md/adoc                   {module}/README.md
       |                                |
       v                                v
  Priority 2:                      Priority 2:
  doc/architecture/*.adoc          package-info.java
       |                                |
       v                                v
  Priority 3:                      Priority 3:
  doc/adr/*.adoc                   Source samples (2-3 files)
```

**Reading strategy reference**: See [documentation-sources.md](documentation-sources.md)

### Information to Extract

| Source | Extract | Maps To |
|--------|---------|---------|
| Module README | First paragraph, overview section | `responsibility` |
| package-info.java | Package-level JavaDoc | `key_packages.{pkg}.description` |
| Source files | Framework annotations, patterns | `tips`, `conventions` |
| ADRs | Design decisions | `notes` |

## Step 3: Structure Enrichment

Combine discovery data with documentation findings.

```
+------------------------------------------------------------------+
|                     ENRICHMENT MERGE                               |
+------------------------------------------------------------------+

  From discover_project_modules():

  {                                     {
    "name": "core",                       "name": "core",
    "technology": "maven",      +         "technology": "maven",
    "paths": {...},             |         "paths": {...},
    "commands": {...}           |         "commands": {...},
  }                             |
                                |    =    "responsibility": "Core...",
  From documentation:           |         "key_packages": {
                                |           "com.example.core": {
  {                             |             "description": "..."
    "responsibility": "Core...",+           }
    "key_packages": {...}                 }
  }                                     }
```

### Enrichment Rules

| Discovery Field | Enrichment Field | Merge Rule |
|-----------------|------------------|------------|
| `paths` | - | Keep as-is |
| `commands` | - | Keep as-is |
| `technology` | - | Keep as-is |
| - | `responsibility` | Add from README |
| - | `key_packages` | Add from package-info |
| `metadata` | `metadata` | Preserve, add enrichments |

## Analysis Workflow

```
+------------------------------------------------------------------+
|                    COMPLETE WORKFLOW                               |
+------------------------------------------------------------------+

  1. discover_project_modules(project_root)
        |
        v
  2. For each module:
        |
        +---> Read module README
        |         |
        |         v
        +---> Find package-info.java files
        |         |
        |         v
        +---> Sample source files (2-3)
        |         |
        |         v
        +---> Check doc/ for ADRs
                  |
                  v
  3. Merge findings into structure
        |
        v
  4. Write project-structure.json
```

### Invocation

```bash
# Step 1: Discover and persist (slow - invokes build tools)
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  collect-raw-data --project-root /path/to/project
# Output: .plan/raw-project-data.json

# Step 2-4: Generate enriched structure from cache (fast - reads JSON)
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  generate
# Output: .plan/project-structure.json
```

**Why two steps?**
- `collect-raw-data` is expensive (invokes Maven, Gradle, npm for metadata)
- Persisting to JSON enables: run once, consume many times
- `generate` and other commands read from cache

## Related Documents

| Document | Purpose |
|----------|---------|
| [extension-api/architecture-overview.md](../../extension-api/standards/architecture-overview.md) | Module discovery internals |
| [documentation-sources.md](documentation-sources.md) | Documentation reading priorities |
