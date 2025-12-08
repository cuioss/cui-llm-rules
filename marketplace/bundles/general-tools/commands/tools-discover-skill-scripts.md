---
name: tools-discover-skill-scripts
description: Discovers all skill scripts from installed plugins and generates .plan/scripts-library.toon with path mappings in TOON format
---

# Discover Skill Scripts Command

Scans installed plugins to discover all skill scripts and generates the scripts library cache in TOON format.

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--force` | Regenerate cache even if it exists |

## Workflow

Run the script discovery generator:

```bash
python3 .plan/execute-script.py general-tools:script-runner:generate \
  --marketplace-root {workspace_root}
```

If `--force` is NOT specified and `.plan/scripts-library.toon` already exists, skip generation and report existing file.

## Usage Examples

**Standard usage (discover or update):**
```
/tools-discover-skill-scripts
```

**Force regeneration:**
```
/tools-discover-skill-scripts --force
```

## Output

Creates/updates `.plan/scripts-library.toon` containing:
- Script notation → absolute path mappings (TOON format)
- Marketplace identifier

Example output:
```toon
version: 2
generated: 2025-12-07T10:30:00Z
marketplace: cui-development-standards
script_count: 81

scripts[81]{notation,absolute,type}:
builder:builder-maven-rules/scripts/execute-maven-build.py,/full/path/execute-maven-build.py,python
planning:manage-files/scripts/manage-files.py,/full/path/manage-files.py,python
...
```

## Script Resolution Convention

The generated `.plan/scripts-library.toon` is used by the system convention for script resolution:

1. Skills document scripts using portable notation: `{bundle}:{skill}/scripts/{name}.{ext}`
2. When executing scripts, resolve the absolute path from `.plan/scripts-library.toon`
3. No skill loading required - resolution is a universal convention

## Related

- `/tools-setup-project-permissions` - Manages permission configuration
- `cui-plugin-development-tools:marketplace-inventory` - Provides plugin scanning
