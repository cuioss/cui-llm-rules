---
name: tools-audit-permission-wildcards
description: Analyzes marketplace bundles to identify required permission wildcard patterns for skills and commands
---

# Audit Permission Wildcards Command

Scans all marketplace bundles to discover skills and commands, analyzes their naming patterns, and generates the minimal set of wildcard permissions needed to cover all marketplace tools.

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--dry-run` | Preview analysis without updating any files |

## Workflow

Activate the `cui-utilities:permission-management` skill and execute the **Audit Permission Wildcards** workflow.

Pass parameter: `dry_run` = true if `--dry-run` specified, false otherwise.

## Usage Examples

**Standard usage (audit and update):**
```
/tools-audit-permission-wildcards
```

**Preview without making changes:**
```
/tools-audit-permission-wildcards --dry-run
```

## Related

- `/tools-setup-project-permissions` - Uses wildcards discovered by this command
- `cui-utilities:permission-management` - Skill containing the audit workflow
- `cui-plugin-development-tools:marketplace-inventory` - Provides marketplace scanning
