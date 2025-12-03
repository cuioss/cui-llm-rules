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
scripts_local = .claude/scripts.local.json
```

### Step 3: Analyze Permissions

**A. Detect redundant permissions (local vs global):**
```bash
python3 {detect-redundant-permissions.py} \
  --global-settings {global_settings} \
  --local-settings {local_settings}
```

Parse result: `redundant[]`, `marketplace_in_local[]`

**B. Detect suspicious permissions:**
```bash
python3 {detect-suspicious-permissions.py} \
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
python3 {consolidate-build-outputs.py} \
  --settings {local_settings}
```

**B. Ensure marketplace wildcards in global:**
```bash
python3 {ensure-marketplace-wildcards.py} \
  --settings {global_settings} \
  --marketplace-json {marketplace_json}
```

**C. Sync script permissions to global (from scripts.local.json):**

If `scripts_local` exists, sync script permissions:
```bash
python3 {apply-permissions.py} \
  --action sync-scripts \
  --scripts-file {scripts_local} \
  --target global
```

This removes stale script permissions and adds current ones from the discovered scripts cache.

**D. Apply safe fixes to local:**
```bash
python3 {apply-permission-fixes.py} \
  --settings {local_settings}
```

**E. Apply safe fixes to global:**
```bash
python3 {apply-permission-fixes.py} \
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

Scripts are resolved via the skill's scripts directory:
- `general-tools:permission-management/scripts/detect-redundant-permissions.py`
- `general-tools:permission-management/scripts/detect-suspicious-permissions.py`
- `general-tools:permission-management/scripts/consolidate-build-outputs.py`
- `general-tools:permission-management/scripts/ensure-marketplace-wildcards.py`
- `general-tools:permission-management/scripts/apply-permissions.py`
- `general-tools:permission-management/scripts/apply-permission-fixes.py`

Use `scripts.local.json` to resolve absolute paths.

## Critical Rules

- **Never remove suspicious without user confirmation** (unless auto-fix)
- **Preserve JSON formatting** (2-space indent)
- **Validate JSON before/after writes**
- **Track user-approved permissions** via run-configuration skill

## Related

- `/tools-discover-skill-scripts` - Discovers scripts and generates `scripts.local.json`
- `/tools-audit-permission-wildcards` - Audits marketplace for permission wildcards
- `general-tools:permission-management` - Permission validation and operations
