---
name: tools-discover-skill-scripts
description: Discovers all skill scripts from installed plugins and generates .claude/scripts.local.json with path mappings and permissions
---

# Discover Skill Scripts Command

Scans installed plugins to discover all skill scripts and generates the local scripts cache.

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--force` | Regenerate cache even if it exists |

## Workflow

Activate the `cui-utilities:script-runner` skill and execute the **Discover** workflow.

Pass parameter: `force` = true if `--force` specified, false otherwise.

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

Creates/updates `.claude/scripts.local.json` containing:
- Script notation → absolute path mappings
- Ready-to-use permission patterns
- Marketplace identifier for permission sync

## Related

- `/tools-setup-project-permissions` - Applies script permissions from scripts.local.json
- `cui-utilities:script-runner` - Skill containing the discovery workflow
- `cui-plugin-development-tools:marketplace-inventory` - Provides plugin scanning
