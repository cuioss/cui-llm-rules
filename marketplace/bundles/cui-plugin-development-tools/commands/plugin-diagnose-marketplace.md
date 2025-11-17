---
name: plugin-diagnose-marketplace
description: Diagnose and fix marketplace plugin configuration errors and obsolete entries
---

# Diagnose Marketplace Command

Validates marketplace configuration (marketplace.json, bundle plugin.json manifests) and user config (installed_plugins.json, settings.json), detecting obsolete entries, schema violations, and configuration drift.

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

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-7)**
- Load diagnostic standards
- Initialize diagnostics
- Validate marketplace.json
- Check installed plugins registry
- Check settings.json configuration
- Validate bundle manifests
- Report summary

**PHASE 2: Fix Workflow (Steps 8-11)**
- Categorize issues (safe vs risky)
- Apply safe fixes automatically
- Prompt user for risky fixes
- Verify all fixes worked

**CRITICAL: Do not stop after Step 7. Continue to Step 8.**

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

### Step 3: Validate marketplace.json

**Read and verify marketplace definition:**
```
Read: /Users/oliver/git/cui-llm-rules/marketplace/.claude-plugin/marketplace.json
```

**Check each plugin in `plugins[]` array:**
- Verify `source` path exists (missing bundles, obsolete skills references)
- Validate required fields (name, description, source)
- Report findings with ✓/✗ indicators

### Step 4: Check Installed Plugins Registry

**Read and verify installed plugins:**
```
Read: ~/.claude/plugins/installed_plugins.json
```

**Check each plugin in `plugins` object:**
- Verify plugin exists in marketplace.json (orphaned plugins)
- Check installPath exists
- Report findings with ✓/✗/⚠ indicators

### Step 5: Check settings.json Configuration

**Read and verify user settings:**
```
Read: ~/.claude/settings.json
```

**Check permissions and enabled plugins:**
- Verify `Skill(plugin-name:*)` permissions in `permissions.allow[]` (obsolete permissions)
- Verify `enabledPlugins` entries (obsolete enabled plugins)
- Cross-reference with marketplace.json
- Report findings with ✓/✗ indicators

### Step 6: Validate Bundle Manifests

**Discover and validate bundles:**
```
SlashCommand: /plugin-inventory --json
```

**For each bundle:**
- Read `{bundle.path}/.claude-plugin/plugin.json`
- Validate schema (required: name, version, description)
- Detect invalid fields (displayName, category, components, dependencies, engines, repository as object)
- Report findings with ✓/✗ indicators

### Step 7: Report Summary

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

**CRITICAL**: If issues found, continue to PHASE 2 (Fix Workflow) - Steps 8-11.

### Step 8: Categorize Issues for Fixing ⚠️ PHASE 2 STARTS HERE

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

### Step 9: Apply Safe Fixes

**When to execute**: If auto-fix=true (default) AND safe fixes exist

**Apply fixes using Edit tool:**
- marketplace.json: Remove obsolete plugin definitions
- installed_plugins.json: Remove orphaned entries
- settings.json: Remove obsolete Skill() permissions and enabledPlugins
- bundle plugin.json: Remove invalid schema fields, fix repository format

Track and display fixes applied with ✓ indicators.

### Step 10: Prompt for Risky Fixes

**When to execute**: If risky fixes exist (regardless of auto-fix setting)

**Risky fix categories:**
1. Configuration Changes (settings.json with potential user impact)
2. Uncertain Removals (entries that might still be in use)

Use AskUserQuestion with multiSelect for each category. For selected fixes, apply using Edit tool. Track applied vs skipped counts.

### Step 11: Verification

**When to execute**: After any fixes applied (Step 9 or Step 10)

Re-run all checks from Steps 3-6. Report: issues resolved, issues remaining, any new issues (should be 0).

### Step 12: Display Final Summary

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
