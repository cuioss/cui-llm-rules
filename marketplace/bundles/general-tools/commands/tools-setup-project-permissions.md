---
name: tools-setup-project-permissions
description: Verify and fix permissions in settings by removing duplicates, fixing formats, and ensuring proper organization
---

# Setup Project Permissions Command

Orchestrates permission setup and cleanup for `.claude/settings.json` using the `permission-management` skill operations.

## Parameters

| Parameter | Description |
|-----------|-------------|
| `dry-run` | Preview changes without applying |
| `auto-fix` | Automatically apply all safe fixes |
| `add=<permission>` | Add specific permission to allow list |

## Workflow

### Step 1: Load Skill

```
Skill: general-tools:permission-management
```

### Step 2: Resolve Paths

```
global_settings = ~/.claude/settings.json
local_settings = .claude/settings.json
marketplace_json = marketplace/marketplace.json
scripts_library = .plan/scripts-library.toon
```

### Step 3: Analyze Permissions

**A. Detect redundant permissions (local vs global):**
```bash
python3 {permission.py} detect-redundant \
  --global-settings {global_settings} \
  --local-settings {local_settings}
```

Parse result: `redundant[]`, `marketplace_in_local[]`

**B. Detect suspicious permissions:**
```bash
python3 {permission.py} detect-suspicious \
  --settings {local_settings}
```

Parse result: `suspicious[]`, `already_approved[]`

### Step 4: Display Analysis Results

```
Permission Analysis
===================

Redundant in local (also in global): {redundant_count}
{list redundant permissions}

Marketplace permissions in local (should be global): {marketplace_count}
{list marketplace permissions}

Suspicious permissions: {suspicious_count}
{list suspicious with severity}
```

### Step 5: Handle Suspicious (unless auto-fix)

For each suspicious permission not in `already_approved`:
- Display reason and severity
- Ask user via AskUserQuestion: "Remove", "Approve", "Skip"
- Track approved to run-configuration

### Step 6: Apply Fixes (unless dry-run)

**A. Consolidate build outputs:**
```bash
python3 {permission.py} consolidate \
  --settings {local_settings}
```

**B. Ensure marketplace wildcards in global:**
```bash
python3 {permission.py} ensure-wildcards \
  --settings {global_settings} \
  --marketplace-json {marketplace_json}
```

**C. Sync script permissions to global (from scripts-library.toon):**

If `scripts_library` exists, sync script permissions:
```bash
python3 {permission.py} apply \
  --action sync-scripts \
  --scripts-file {scripts_library} \
  --target global
```

This removes stale script permissions and adds current ones from the discovered scripts library.

**D. Apply safe fixes to local:**
```bash
python3 {permission.py} apply-fixes \
  --settings {local_settings}
```

**E. Apply safe fixes to global:**
```bash
python3 {permission.py} apply-fixes \
  --settings {global_settings}
```

### Step 7: Display Summary

```
Permission Setup Complete
=========================

Local Settings ({local_settings}):
  - Duplicates removed: {duplicates_removed}
  - Build outputs consolidated: {consolidated}
  - Defaults added: {defaults_added}
  - Sorted: {sorted}

Global Settings ({global_settings}):
  - Marketplace wildcards added: {wildcards_added}
  - Script permissions synced: {scripts_removed} removed, {scripts_added} added
  - Duplicates removed: {global_duplicates}
  - Defaults added: {global_defaults}

{if dry-run}
Dry-run mode: No files modified
{else}
Changes applied successfully
{endif}
```

## Script Resolution

All operations use the consolidated `permission.py` script with subcommands:
- `general-tools:permission-management` → `permission.py {subcommand}`

Subcommands: `detect-redundant`, `detect-suspicious`, `consolidate`, `ensure-wildcards`, `apply`, `apply-fixes`

## Critical Rules

- **Never remove suspicious without user confirmation** (unless auto-fix)
- **Preserve JSON formatting** (2-space indent)
- **Validate JSON before/after writes**
- **Track user-approved permissions** via run-configuration skill

## Related

- `/tools-discover-skill-scripts` - Discovers scripts and generates `scripts-library.toon`
- `/tools-audit-permission-wildcards` - Audits marketplace for permission wildcards
- `general-tools:permission-management` - Permission validation and operations
