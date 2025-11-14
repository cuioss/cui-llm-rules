---
name: plugin-diagnose-marketplace
description: Diagnose and fix marketplace plugin configuration errors and obsolete entries
---

# Diagnose Marketplace Command

Comprehensive diagnostic tool for marketplace plugin configuration, detecting obsolete entries, schema violations, and configuration drift across marketplace.json, installed_plugins.json, and settings.json.

## Overview

This command diagnoses and fixes issues across **two configuration layers**:

### 1. Marketplace Config (Repository)
**Location**: `/marketplace/`
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

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-marketplace update="[your improvement]"` with:
1. Enhanced detection patterns for obsolete plugin references
2. Improved schema validation for plugin.json manifests
3. Better categorization of safe vs risky fixes
4. More comprehensive cross-file consistency checks
5. Any lessons learned about marketplace configuration issues

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes

## WORKFLOW

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-6)**
- Load diagnostic standards
- Initialize diagnostics
- Validate marketplace.json
- Check installed plugins registry
- Check settings.json configuration
- Validate bundle manifests
- Report summary

**PHASE 2: Fix Workflow (Steps 7-10)**
- Categorize issues (safe vs risky)
- Apply safe fixes automatically
- Prompt user for risky fixes
- Verify all fixes worked

**CRITICAL: Do not stop after Step 6. Continue to Step 7.**

### Step 1: Load Diagnostic Standards

**CRITICAL**: Load non-prompting tool patterns:

```
Skill: cui-utilities:cui-diagnostic-patterns
```

**Optionally load marketplace architecture standards**:

You may optionally load the marketplace architecture skill for additional architectural context:
```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components that may be useful for understanding marketplace structure and plugin configuration.

### Step 2: Initialize Diagnostics

Track statistics:
- `files_checked`: Count of configuration files examined
- `issues_found`: Count of total issues detected
- `issues_fixed`: Count of issues successfully resolved

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
Read: /Users/oliver/git/cui-llm-rules/marketplace/.claude-plugin/marketplace.json
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
Glob: marketplace/bundles/*/.claude-plugin/plugin.json
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

==================================================
⚠️ CRITICAL: ANALYSIS PHASE COMPLETE
==================================================

You have completed PHASE 1 (Analysis).

**YOU MUST NOW PROCEED TO PHASE 2 (Fix Workflow)**

DO NOT STOP HERE. The analysis is useless without fixes.

If any issues were found (warnings or suggestions):
→ Continue to Step 7: Categorize Issues
→ Continue to Step 8: Apply Safe Fixes
→ Continue to Step 9: Prompt for Risky Fixes
→ Continue to Step 10: Verification

If zero issues found:
→ Skip to completion message

==================================================

### Step 7: Categorize Issues for Fixing ⚠️ PHASE 2 STARTS HERE

**Categorize all issues into Safe vs Risky:**

**Safe fixes** (auto-apply when auto-fix=true):
- Remove obsolete plugin definitions from marketplace.json
- Remove orphaned plugin entries from installed_plugins.json
- Remove obsolete Skill() permissions from settings.json
- Remove obsolete enabledPlugins entries from settings.json
- Remove invalid schema fields from bundle plugin.json (displayName, category, components, dependencies, engines)
- Convert repository object to string in plugin.json

**Risky fixes** (always prompt user):
- Remove plugins that might still be in use (if uncertain)
- Structural changes to marketplace.json that affect multiple bundles
- Changes that might break user workflows

**Note**: Most marketplace diagnostics issues are safe to auto-fix because they involve removing obsolete/invalid entries.

### Step 8: Apply Safe Fixes

**When to execute**: If auto-fix=true (default) AND safe fixes exist

**CRITICAL: If you reached Step 6, you MUST execute this step if safe fixes exist. This is not optional.**

**For each safe fix:**

**Fix marketplace.json:**
```
Edit: marketplace/.claude-plugin/marketplace.json
- Remove obsolete plugin definitions
- Update plugins array
```

**Fix installed_plugins.json:**
```
Edit: ~/.claude/plugins/installed_plugins.json
- Remove orphaned plugin entries from plugins object
```

**Fix settings.json:**
```
Edit: ~/.claude/settings.json
- Remove obsolete Skill() permissions from permissions.allow array
- Remove obsolete entries from enabledPlugins object
```

**Fix bundle plugin.json manifests:**
```
Edit: marketplace/bundles/{bundle-name}/.claude-plugin/plugin.json
- Remove invalid schema fields (displayName, category, components, dependencies, engines)
- Convert repository object to string format
```

**Track fixes applied:**
```json
{
  "safe_fixes_applied": {count},
  "by_type": {
    "marketplace_json_fixes": {count},
    "installed_plugins_fixes": {count},
    "settings_json_fixes": {count},
    "plugin_json_schema_fixes": {count}
  }
}
```

Display progress:
```
[INFO] Applying fixes...
  ✓ Removed 2 obsolete plugins from marketplace.json
  ✓ Removed 3 orphaned entries from installed_plugins.json
  ✓ Removed 4 obsolete Skill permissions from settings.json
  ✓ Removed 3 obsolete enabledPlugins from settings.json
  ✓ Fixed cui-maven plugin.json schema
```

### Step 9: Prompt for Risky Fixes

**When to execute**: If risky fixes exist (regardless of auto-fix setting)

**Group risky fixes by category:**

1. **Configuration Changes** (settings.json modifications with potential user impact)
2. **Uncertain Removals** (entries that might still be in use)

**For each category with issues, use AskUserQuestion:**

Use the AskUserQuestion tool with this structure:
- questions: Array with one question per category
- question: "Apply fixes for {category} issues?"
- header: "{Category}"
- multiSelect: true
- options: Array containing:
  - For each specific issue: label="Fix: {specific-issue}", description="Impact: {what-changes}. File: {file}. Reason: {why-risky}"
  - Final option: label="Skip all {category} fixes", description="Continue without fixing this category"

**Process user selections:**
- For each selected fix: Apply using Edit tool, increment `risky_fixes_applied`
- For unselected fixes: Skip, increment `risky_fixes_skipped`
- If "Skip all" selected: Skip entire category, increment `risky_fixes_skipped` by count

**Track risky fixes:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "fixes_by_category": {
    "configuration": {applied: count, skipped: count},
    "uncertain_removals": {applied: count, skipped: count}
  }
}
```

### Step 10: Verification

**When to execute**: After any fixes applied (Step 8 or Step 9)

**Re-run all checks from Steps 2-5**

**Compare before/after:**
```json
{
  "verification": {
    "original_issues": {count},
    "issues_resolved": {count},
    "issues_remaining": {count},
    "new_issues": {count}  // Should be 0!
  }
}
```

**Report verification results:**
```
Verification Complete:
✅ {issues_resolved} issues resolved
{if issues_remaining > 0}
⚠️ {issues_remaining} issues remain (require manual intervention)
{endif}
{if new_issues > 0}
❌ {new_issues} NEW issues introduced (fixes need review!)
{endif}
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

Configuration Status: {✓ HEALTHY | ⚠ NEEDS ATTENTION | ✗ ERRORS REMAIN}

Next Steps:
1. Restart Claude Code to apply plugin changes
2. Review changes with git diff if needed
3. Run /plugin-diagnose-bundle for individual bundle checks
```

## CRITICAL RULES

**Validation:**
- Check ALL three configuration files (marketplace.json, installed_plugins.json, settings.json)
- Validate plugin.json schema for ALL bundles
- Cross-reference plugin names across all configuration files

**Autofix:**
- When auto-fix=true (default), automatically fix safe issues without prompts
- Always prompt user for risky fixes, even when auto-fix=true
- Most marketplace issues are safe to auto-fix (obsolete entries, invalid schema fields)

**Safety:**
- Verify fixes by re-running diagnostics
- Git provides version control - no separate backups needed

**User Experience:**
- Clear severity indicators: ✓ (valid), ⚠ (warning), ✗ (error)
- Grouped findings by configuration file
- Statistics tracking throughout workflow
- Option to selectively fix issues

**Error Handling:**
- If Read fails: Report file not found, skip that check
- If Edit fails: Report error, mark issue as unfixed
- Non-blocking failures: Continue checking other files

**Schema Validation:**
- Only flag fields that are NOT in Claude Code plugin schema
- Valid fields: name, version, description, author, license, homepage, repository (string), keywords, skills
- Invalid fields: displayName, category, components, dependencies, engines, repository (object)

## USAGE EXAMPLES

**Basic diagnostics with auto-fix (default):**
```
/plugin-diagnose-marketplace
```

**Disable auto-fix (report only):**
```
/plugin-diagnose-marketplace auto-fix=false
```

**Note:** Safe issues are auto-fixed by default. Risky fixes always prompt for confirmation.

## RELATED

- `/plugin-diagnose-bundle` - Diagnose individual bundle structure and quality
- `/plugin-diagnose-skills` - Validate skill files and standards references
- Plugin quality standards - bundles/cui-plugin-development-tools/standards/plugin-quality-standards.md (if exists)
