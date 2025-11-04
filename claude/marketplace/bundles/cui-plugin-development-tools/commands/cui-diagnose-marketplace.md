---
name: cui-diagnose-marketplace
description: Diagnose and fix marketplace plugin configuration errors and obsolete entries
---

# Diagnose Marketplace Command

Comprehensive diagnostic tool for marketplace plugin configuration, detecting obsolete entries, schema violations, and configuration drift across marketplace.json, installed_plugins.json, and settings.json.

## Overview

This command diagnoses and fixes issues across **two configuration layers**:

### 1. Marketplace Config (Repository)
**Location**: `/claude/marketplace/`
**Purpose**: Defines WHAT plugins exist and WHERE they are
**Scope**: Project-wide, version controlled, shared across users

**Files**:
- `marketplace/.claude-plugin/marketplace.json` - Available plugins in marketplace
- `bundles/*/plugin.json` - Each bundle's metadata

### 2. User Config (Local)
**Location**: `~/.claude/`
**Purpose**: User's personal settings - WHICH plugins are installed/enabled
**Scope**: User-specific, local machine only, NOT version controlled

**Files**:
- `plugins/installed_plugins.json` - Installed plugins cache
- `plugins/known_marketplaces.json` - Tracked marketplaces
- `settings.json` - Permissions and enabled plugins

### Why Both Layers Matter

When plugins are removed from marketplace, user's local cache still references them, causing errors. This command checks and fixes **both layers** to ensure consistency.

**Common Issues Detected**:

| Issue Type | Layer | File | Example |
|------------|-------|------|---------|
| Obsolete plugin definitions | Marketplace | `marketplace.json` | Plugin references non-existent `/skills/` directory |
| Orphaned installations | User Config | `installed_plugins.json` | Cached plugin no longer in marketplace |
| Obsolete permissions | User Config | `settings.json` | `Skill(removed-plugin:*)` still allowed |
| Obsolete enabled plugins | User Config | `settings.json` | `removed-plugin@marketplace: true` |
| Invalid schema | Marketplace | `bundle/plugin.json` | Invalid fields like `displayName`, `category` |

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-diagnose-marketplace update="[your improvement]"` with:
1. Enhanced detection patterns for obsolete plugin references
2. Improved schema validation for plugin.json manifests
3. Better backup and rollback strategies for configuration fixes
4. More comprehensive cross-file consistency checks
5. Any lessons learned about marketplace configuration issues

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**auto-fix** (optional, default: false) - Automatically fix issues without prompting user
**backup** (optional, default: true) - Create timestamped backups before making changes

## WORKFLOW

### Step 1: Initialize Diagnostics

Track statistics:
- `files_checked`: Count of configuration files examined
- `issues_found`: Count of total issues detected
- `issues_fixed`: Count of issues successfully resolved
- `backups_created`: Count of backup files created

Display:
```
╔════════════════════════════════════════════════════════════╗
║          Marketplace Diagnostics Starting                  ║
╚════════════════════════════════════════════════════════════╝

Checking marketplace configuration...
```

### Step 2: Validate marketplace.json

**A. Read marketplace definition:**
```
Read: /Users/oliver/git/cui-llm-rules/claude/marketplace/.claude-plugin/marketplace.json
```

**B. Verify each plugin definition:**
- Extract `plugins[]` array
- For each plugin entry:
  - Check `source` path exists (Glob)
  - If source is relative (`./bundles/...`), verify bundle directory exists
  - If source references `./skills/...`, flag as obsolete (skills should be in bundles)

**C. Detect issues:**
- **Missing bundle**: `source` points to non-existent directory
- **Obsolete skills reference**: Plugin defines standalone skills outside bundles
- **Invalid structure**: Missing required fields (name, description, source)

**D. Report findings:**
```
[INFO] Checking marketplace.json definitions...
  ✓ cui-java-expert: Valid bundle
  ✗ cui-old-skills: Source not found (./skills/cui-old-skills)
  ✗ cui-frontend-skills: Obsolete skills reference
```

Increment `issues_found` for each problem detected.

### Step 3: Check Installed Plugins Registry

**A. Read installed plugins:**
```
Read: ~/.claude/plugins/installed_plugins.json
```

**B. Verify each installed plugin:**
- Extract `plugins` object keys
- For each `plugin-name@marketplace`:
  - Check if plugin exists in marketplace.json
  - Check if `installPath` exists (Bash ls)
  - Verify gitCommitSha is recent (optional warning)

**C. Detect issues:**
- **Orphaned plugin**: Plugin in installed_plugins.json but NOT in marketplace.json
- **Missing install path**: installPath directory doesn't exist
- **Stale installation**: Very old gitCommitSha (>6 months warning)

**D. Report findings:**
```
[INFO] Checking installed plugins registry...
  ✓ cui-java-expert@cui-development-standards: Valid
  ✗ cui-old-skills@cui-development-standards: Not in marketplace
  ⚠ cui-maven@cui-development-standards: Old commit (6 months)
```

Increment `issues_found` for orphaned plugins.

### Step 4: Check settings.json Configuration

**A. Read user settings:**
```
Read: ~/.claude/settings.json
```

**B. Verify Skill permissions in allowedToolUse:**
- Extract `permissions.allow[]` array
- Find all entries matching `Skill(plugin-name:*)`
- For each Skill permission:
  - Check if plugin exists in marketplace.json
  - Flag obsolete if plugin no longer defined

**C. Verify enabledPlugins section:**
- Extract `enabledPlugins` object keys
- For each `plugin-name@marketplace`:
  - Check if plugin exists in marketplace.json
  - Flag if NOT found (obsolete enabled plugin)

**D. Detect issues:**
- **Obsolete Skill permission**: `Skill(old-plugin:*)` but plugin not in marketplace
- **Obsolete enabled plugin**: Entry in enabledPlugins but plugin removed from marketplace
- **Inconsistency**: Plugin in enabledPlugins but NOT in installed_plugins

**E. Report findings:**
```
[INFO] Checking settings.json configuration...
  Permissions (allowedToolUse):
    ✗ Skill(cui-old-skills:*): Obsolete permission
    ✗ Skill(cui-frontend-skills:*): Obsolete permission

  Enabled Plugins:
    ✗ cui-old-skills@cui-development-standards: Plugin not found
    ✓ cui-java-expert@cui-development-standards: Valid
```

Increment `issues_found` for each obsolete entry.

### Step 5: Validate Bundle Manifests

**A. Find all bundle plugin.json files:**
```
Glob: claude/marketplace/bundles/*/.claude-plugin/plugin.json
```

**B. Validate each manifest against schema:**
- Read each plugin.json
- Check required fields: name, version, description
- Check optional fields: author, license, homepage, repository, keywords
- Detect invalid fields:
  - `displayName` (not in schema)
  - `category` (not in schema)
  - `components` (not in schema - auto-discovered)
  - `dependencies` (not in schema)
  - `engines` (not in schema)
  - `repository` as object instead of string

**C. Report findings:**
```
[INFO] Validating bundle manifests...
  ✓ cui-java-expert: Valid schema
  ✗ cui-maven: Invalid fields (displayName, category, components, dependencies, engines)
  ✗ cui-old-bundle: repository must be string, not object
```

Increment `issues_found` for each schema violation.

### Step 6: Report Summary

Display complete findings:
```
╔════════════════════════════════════════════════════════════╗
║          Marketplace Diagnostics Complete                  ║
╚════════════════════════════════════════════════════════════╝

Statistics:
- Files checked: {files_checked}
- Issues found: {issues_found}

Issues by Category:
  marketplace.json:
    • 2 obsolete plugin definitions
    • 1 missing bundle reference

  installed_plugins.json:
    • 3 orphaned plugin entries

  settings.json:
    • 4 obsolete Skill permissions
    • 3 obsolete enabled plugins

  Bundle Manifests:
    • 1 schema validation error (cui-maven)

{issues_list}
```

### Step 7: Offer Fixes

**If auto-fix=false:**
```
[PROMPT] Fix issues automatically? [Y]es/[N]o/[S]elective
```

**If auto-fix=true or user selects Yes:**
- Skip prompt, proceed to Step 8

**If user selects Selective:**
- Show each issue with [F]ix/[S]kip option
- Track user choices

**If user selects No:**
- Display: "Run /cui-diagnose-marketplace auto-fix=true to apply fixes"
- Exit

### Step 8: Create Backups (if backup=true)

For each file that will be modified:
```
Bash: cp {file} {file}.backup-{timestamp}
```

Example:
- `~/.claude/settings.json` → `~/.claude/settings.json.backup-20250104-143022`
- `~/.claude/plugins/installed_plugins.json` → `~/.claude/plugins/installed_plugins.json.backup-20250104-143022`

Increment `backups_created` for each backup.

Display:
```
[INFO] Created backups:
  • ~/.claude/settings.json.backup-20250104-143022
  • ~/.claude/plugins/installed_plugins.json.backup-20250104-143022
```

### Step 9: Apply Fixes

**A. Fix marketplace.json:**
- Remove obsolete plugin definitions
- Update with Edit tool

**B. Fix installed_plugins.json:**
- Remove orphaned plugin entries
- Update with Edit tool or jq via Bash

**C. Fix settings.json:**
- Remove obsolete Skill() permissions from allowedToolUse
- Remove obsolete entries from enabledPlugins
- Update with Edit tool

**D. Fix bundle plugin.json manifests:**
- Remove invalid fields
- Convert repository object to string if needed
- Update with Edit tool

Increment `issues_fixed` for each successful fix.

Display progress:
```
[INFO] Applying fixes...
  ✓ Removed 2 obsolete plugins from marketplace.json
  ✓ Removed 3 orphaned entries from installed_plugins.json
  ✓ Removed 4 obsolete Skill permissions from settings.json
  ✓ Removed 3 obsolete enabledPlugins from settings.json
  ✓ Fixed cui-maven plugin.json schema
```

### Step 10: Verification

**A. Re-run all checks from Steps 2-5**

**B. Compare issues_found:**
- Before: {original_issues}
- After: {remaining_issues}

**C. Display verification:**
```
[INFO] Verification complete:
  • Original issues: {original_issues}
  • Remaining issues: {remaining_issues}
  • Fixed: {issues_fixed}
```

If `remaining_issues > 0`:
```
[WARN] Some issues could not be fixed automatically:
{list_of_remaining_issues}
```

### Step 11: Display Final Summary

```
╔════════════════════════════════════════════════════════════╗
║          Marketplace Diagnostics Summary                   ║
╚════════════════════════════════════════════════════════════╝

Results:
- Files checked: {files_checked}
- Issues found: {issues_found}
- Issues fixed: {issues_fixed}
- Backups created: {backups_created}

Configuration Status: {✓ HEALTHY | ⚠ NEEDS ATTENTION | ✗ ERRORS REMAIN}

Next Steps:
1. Restart Claude Code to apply plugin changes
2. Review backup files in ~/.claude/*.backup-*
3. Run /cui-diagnose-bundle for individual bundle checks
```

## CRITICAL RULES

**Validation:**
- Check ALL three configuration files (marketplace.json, installed_plugins.json, settings.json)
- Validate plugin.json schema for ALL bundles
- Cross-reference plugin names across all configuration files

**Safety:**
- ALWAYS create backups before modifications (unless backup=false)
- Timestamp backups for traceability: `{filename}.backup-{YYYYMMDD-HHMMSS}`
- Verify fixes by re-running diagnostics

**User Experience:**
- Clear severity indicators: ✓ (valid), ⚠ (warning), ✗ (error)
- Grouped findings by configuration file
- Statistics tracking throughout workflow
- Option to selectively fix issues

**Error Handling:**
- If Read fails: Report file not found, skip that check
- If Edit fails: Report error, mark issue as unfixed
- If Bash backup fails: Abort fixes, warn user
- Non-blocking failures: Continue checking other files

**Schema Validation:**
- Only flag fields that are NOT in Claude Code plugin schema
- Valid fields: name, version, description, author, license, homepage, repository (string), keywords, skills
- Invalid fields: displayName, category, components, dependencies, engines, repository (object)

## USAGE EXAMPLES

**Basic diagnostics (report only):**
```
/cui-diagnose-marketplace
```

**Auto-fix all issues:**
```
/cui-diagnose-marketplace auto-fix=true
```

**Fix without backups (not recommended):**
```
/cui-diagnose-marketplace auto-fix=true backup=false
```

**Selective fix mode:**
```
/cui-diagnose-marketplace
→ [User chooses Selective]
→ For each issue: [F]ix or [S]kip
```

## RELATED

- `/cui-diagnose-bundle` - Diagnose individual bundle structure and quality
- `/cui-diagnose-skills` - Validate skill files and standards references
- Plugin quality standards - bundles/cui-plugin-development-tools/standards/plugin-quality-standards.md (if exists)
