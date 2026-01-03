# Orchestrator Integration

Specification for how `project-structure` orchestrates module discovery across domain extensions.

## Purpose

The `project-structure` skill serves as the **orchestrator** that:
- Discovers and loads applicable domain extensions
- Collects module data from each extension via `discover_modules()`
- Merges results for hybrid modules (e.g., Maven+npm in same directory)
- Resolves commands per module from templates and profiles
- Persists combined data to `.plan/raw-project-data.json`

## Orchestrator Flow

```python
def collect_raw_data(project_root: str) -> dict:
    """Collect module data from all extensions."""

    # 1. Discover available extensions
    extensions = discover_extensions(project_root)

    # 2. Collect modules from each extension
    all_modules = {}
    for ext in extensions:
        for module in ext.discover_modules(project_root):
            name = module["name"]
            if name in all_modules:
                # Hybrid module: merge data from multiple extensions
                all_modules[name] = merge_module_data(all_modules[name], module)
            else:
                all_modules[name] = module

    # 3. Commands already resolved by extensions
    # (extensions return commands as top-level field, profiles in metadata)

    # 4. Return as raw-project-data.json structure
    return {
        "project_root": project_root,
        "modules": all_modules,
        "extensions_used": [ext.name for ext in extensions]
    }
```

## Hybrid Module Merging

When multiple extensions discover the same module (by name), the orchestrator merges their data:

```python
def merge_module_data(existing: dict, new: dict) -> dict:
    """Merge module data from multiple extensions (hybrid modules)."""

    # Aggregate build systems
    build_systems = existing.get("build_systems", [existing["technology"]])
    build_systems.append(new["technology"])

    # Merge paths
    paths = {
        "module": existing["paths"]["module"],  # Same for both
        "descriptors": [existing["paths"]["descriptor"], new["paths"]["descriptor"]],
        "sources": existing["paths"]["sources"] + new["paths"]["sources"],
        "tests": existing["paths"]["tests"] + new["paths"]["tests"],
        "readme": existing["paths"].get("readme") or new["paths"].get("readme")
    }

    # Merge metadata (first extension wins for conflicts)
    metadata = {**new.get("metadata", {}), **existing.get("metadata", {})}

    # Merge packages (combine from both)
    packages = {**existing.get("packages", {}), **new.get("packages", {})}

    # Merge dependencies (deduplicate)
    dependencies = list(set(existing["dependencies"] + new["dependencies"]))

    # Merge stats (sum counts)
    stats = {
        "source_files": existing.get("stats", {}).get("source_files", 0) + new.get("stats", {}).get("source_files", 0),
        "test_files": existing.get("stats", {}).get("test_files", 0) + new.get("stats", {}).get("test_files", 0)
    }

    # Merge commands (combine from both extensions)
    commands = {**existing.get("commands", {}), **new.get("commands", {})}

    return {
        "name": existing["name"],
        "build_systems": build_systems,
        "paths": paths,
        "metadata": metadata,
        "packages": packages,
        "dependencies": dependencies,
        "stats": stats,
        "commands": commands
    }
```

## Merge Rules

| Field | Merge Rule |
|-------|------------|
| `technology` → `build_systems` | Aggregate into list |
| `paths.descriptor` → `paths.descriptors` | Convert to list |
| `paths.sources` | Concatenate lists |
| `paths.tests` | Concatenate lists |
| `paths.readme` | First non-null wins |
| `metadata` | First extension wins for conflicts |
| `packages` | Merge objects (combine from both) |
| `dependencies` | Concatenate and deduplicate |
| `stats` | Sum counts |
| `commands` | Merge objects (second extension overwrites conflicts) |

## Command Handling

Extensions return `commands` as a top-level field per module. The orchestrator merges commands from multiple extensions for hybrid modules.

**Command sources:**
- Extensions build commands from `get_command_mappings()` templates
- Profile-enhanced commands (Maven: via detected profiles in `metadata.profiles`)
- Script-based commands (npm: via package.json scripts)

**For hybrid modules**, commands from both extensions are merged. If both provide the same canonical command, the second extension's command wins.

### Required Command Validation

After resolution, validate that required commands exist:

```python
REQUIRED_COMMANDS = ["module-tests", "quality-gate", "verify"]

def validate_required_commands(module: dict) -> list:
    """Return list of missing required commands."""
    commands = module.get("commands", {})
    packaging = module.get("metadata", {}).get("packaging")

    # pom modules only require quality-gate
    if packaging == "pom":
        required = ["quality-gate"]
    else:
        required = REQUIRED_COMMANDS

    return [cmd for cmd in required if cmd not in commands]
```

## Output Location

Discovery results are persisted to `.plan/raw-project-data.json`:

```json
{
  "project_root": "/absolute/path/to/project",
  "modules": {
    "oauth-sheriff-core": {
      "name": "oauth-sheriff-core",
      "build_systems": ["maven"],
      "paths": { ... },
      "metadata": { ... },
      "packages": { ... },
      "dependencies": [ ... ],
      "stats": { ... },
      "commands": {
        "module-tests": "python3 .plan/execute-script.py ... --module oauth-sheriff-core",
        "verify": "...",
        "quality-gate": "..."
      }
    },
    "nifi-cuioss-ui": {
      "name": "nifi-cuioss-ui",
      "build_systems": ["maven", "npm"],
      "commands": {...},
      ...
    }
  },
  "extensions_used": ["pm-dev-java", "pm-dev-frontend"]
}
```

## CLI Interface

```bash
# Discover and persist project structure
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  collect-raw-data --project-root /path/to/project

# Generate from raw data
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  generate --project-root /path/to/project
```

## Extension Discovery

The orchestrator discovers extensions by:
1. Loading bundles from plugin cache
2. Checking `is_applicable(project_root)` for each extension
3. Filtering to extensions that return `True`

```python
def discover_extensions(project_root: str) -> list:
    """Discover extensions applicable to this project."""
    extensions = []
    for bundle in load_bundles():
        ext = bundle.get_extension()
        if ext and ext.is_applicable(project_root):
            extensions.append(ext)
    return extensions
```

## Known Limitations

1. **Nested modules**: Deeply nested modules (e.g., `parent/child/grandchild`) require recursive discovery
2. **Extension priority**: No explicit priority ordering - first extension wins for metadata conflicts
3. **Partial discovery**: If one extension fails, others continue (partial results possible)

## Related Specifications

- [build-project-structure.md](../../extension-api/standards/build-project-structure.md) - Extension discovery contract
- [extension-contract.md](../../extension-api/standards/extension-contract.md) - Extension API contract
