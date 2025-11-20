---
name: plugin-diagnose-metadata
description: Diagnose and fix all metadata files (bundle plugin.json and marketplace.json)
---

# Diagnose Metadata Command

Comprehensive metadata validation and repair for the entire marketplace. Validates and fixes:
- Bundle plugin.json component inventories (agents/commands/skills arrays)
- Bundle plugin.json schema compliance (removes invalid fields)
- Marketplace.json registry (ensures all bundles properly registered)

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-metadata update="[your improvement]"` with:
1. Enhanced metadata validation patterns for detecting inconsistencies
2. Improved schema validation rules aligned with Claude Code plugin spec
3. Better categorization of safe vs risky metadata fixes
4. More comprehensive cross-file consistency checks
5. Any lessons learned about marketplace metadata management workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes

## TOOL USAGE REQUIREMENTS

```
Skill: cui-utilities:cui-diagnostic-patterns
```

**Optionally load marketplace architecture standards**:

You may optionally load the marketplace architecture skill for additional architectural context:
```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components that may be useful for understanding metadata structure and plugin configuration.

✅ Use `Glob`, `Read`, `Edit`, `SlashCommand` (never Bash alternatives)

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-3)**
- Discover all bundles via plugin-inventory
- Validate all bundle metadata (component inventory + schema) in single pass
- Validate marketplace registry
- Generate comprehensive report

**PHASE 2: Fix Workflow (Steps 4-7)**
- Categorize issues (safe vs risky)
- Apply safe fixes automatically
- Prompt user for risky fixes
- Verify all fixes worked

**CRITICAL: Do not stop after Step 3. Continue to fix workflow.**

## WORKFLOW INSTRUCTIONS

### Step 1: Initialize and Discover Bundles

**Initialize statistics tracking:**
- `bundles_discovered`: Total bundles found
- `bundles_analyzed`: Bundles successfully analyzed
- `plugin_json_issues`: Component inventory + schema issues found
- `marketplace_json_issues`: Registry issues found
- `total_issues`: Aggregate count
- `total_fixes`: Count of fixes applied

**Display:**
```
╔════════════════════════════════════════════════════════════╗
║          Metadata Diagnostics Starting                     ║
╚════════════════════════════════════════════════════════════╝

Discovering marketplace bundles...
```

**Run scan-marketplace-inventory.sh script to discover all bundles:**
```
Bash: ./.claude/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh --scope marketplace
```

Parse JSON output from script:
- Extract `bundles[]` array
- For each bundle: Extract name, path, agents[], commands[], skills[]
- Track `bundles_discovered` count

**Error handling:**
- If agent fails: Display "Failed to discover bundles: {error}" and abort
- If JSON parse fails: Display "Invalid inventory format" and abort

### Step 2: Validate All Bundle Metadata

**For each bundle discovered in Step 1, perform all validation checks in single pass:**

#### 2.1: Read Bundle plugin.json

```
Read: {bundle.path}/.claude-plugin/plugin.json
```

Parse JSON and extract:
- `registered_agents` = plugin.json["agents"] or []
- `registered_commands` = plugin.json["commands"] or []
- `registered_skills` = plugin.json["skills"] or []

Convert paths to names:
- `"./agents/foo.md"` → `"foo"`
- `"./commands/bar.md"` → `"bar"`
- `"./skills/baz"` → `"baz"` (note: skills are directories, not .md files)

**Error handling:**
- If Read fails: Log error for this bundle, mark as "Not Analyzed", continue with next bundle
- If JSON parse fails: Log error, mark as "Invalid JSON", continue

#### 2.2: Compare with Discovered Components

Build expected arrays from inventory data and compare with registered components.

Identify missing registrations (in discovered but not registered) and orphaned entries (registered but not discovered).

Track issues: Increment `plugin_json_issues` for each mismatch and store per bundle.

#### 2.3: Display Inventory Findings

For bundles with inventory issues:
```
Bundle: {bundle-name}
  Component Inventory:
    Agents: {expected_count} expected, {registered_count} registered
      ✗ Not registered: {missing_agents} (if any)
      ✗ Orphaned: {orphaned_agents} (if any)
    Commands: {expected_count} expected, {registered_count} registered
      ✗ Not registered: {missing_commands} (if any)
      ✗ Orphaned: {orphaned_commands} (if any)
    Skills: {expected_count} expected, {registered_count} registered
      ✗ Not registered: {missing_skills} (if any)
      ✗ Orphaned: {orphaned_skills} (if any)
```

#### 2.4: Validate Schema Compliance

Using plugin.json from Step 2.1, validate against Claude Code plugin schema (see cui-diagnostic-patterns skill for valid/invalid field lists).

Flag invalid fields: displayName, category, components, dependencies, engines, repository (if object).

Track issues and display findings per bundle.

### Step 3: Validate Marketplace Registry

**Read marketplace registry:**
```
Read: /Users/oliver/git/cui-llm-rules/marketplace/.claude-plugin/marketplace.json
```

Parse JSON and extract `plugins[]` array.

**For each plugin in marketplace.json:**
- Extract `source` path
- Verify bundle exists in discovered bundles from Step 1
- Validate required fields: name, description, source

**For each bundle discovered in Step 1:**
- Verify bundle is registered in marketplace.json
- Check if source path matches bundle path

**Detect issues:**
- `obsolete_plugins`: Plugins in marketplace.json with non-existent source paths
- `missing_registrations`: Bundles not registered in marketplace.json
- `invalid_plugins`: Plugins missing required fields

**Track issues:**
- Increment `marketplace_json_issues` for each issue

**Display marketplace findings:**
```
Marketplace Registry:
  ✗ Obsolete plugin: old-bundle (source doesn't exist)
  ✗ Missing registration: new-bundle
  ✗ Invalid plugin: broken-bundle (missing description)
```

### Step 3.5: Analysis Phase Complete ⚠️ END OF PHASE 1

Display complete analysis results:

```
╔════════════════════════════════════════════════════════════╗
║          Metadata Analysis Complete                        ║
╚════════════════════════════════════════════════════════════╝

Statistics:
- Bundles discovered: {bundles_discovered}
- Bundles analyzed: {bundles_analyzed}
- Total issues found: {total_issues}

Issues by Category:
  Bundle plugin.json:
    • Component inventory: {inventory_issue_count} bundles
    • Schema validation: {schema_issue_count} bundles
    Total: {plugin_json_issues}

  Marketplace registry:
    • Obsolete plugins: {obsolete_count}
    • Missing registrations: {missing_count}
    • Invalid entries: {invalid_count}
    Total: {marketplace_json_issues}

{detailed_issue_list}
```

**CRITICAL**: Continue to PHASE 2 (Fix Workflow) - Steps 5-8.

==================================================
⚠️ CRITICAL: ANALYSIS PHASE COMPLETE
==================================================

You have completed PHASE 1 (Analysis).

**YOU MUST NOW PROCEED TO PHASE 2 (Fix Workflow)**

DO NOT STOP HERE. The analysis is useless without fixes.

If any issues were found:
→ Continue to Step 4: Categorize Issues
→ Continue to Step 5: Apply Safe Fixes
→ Continue to Step 6: Prompt for Risky Fixes
→ Continue to Step 7: Verify Fixes

If zero issues found:
→ Skip to completion message

==================================================

### Steps 4-7: Apply Fix Workflow ⚠️ PHASE 2 STARTS HERE

Load and apply fix workflow:
```
Skill: cui-plugin-development-tools:diagnose-reporting-templates
```

Use "Fix Workflow Pattern" with metadata-specific configuration:

**Metadata-specific safe fixes** (auto-apply when auto-fix=true):
- Update component inventory arrays in bundle plugin.json
- Remove invalid schema fields (displayName, category, components, dependencies, engines)
- Convert repository object to string in bundle plugin.json
- Remove obsolete plugin definitions from marketplace.json
- Fix malformed plugin entries in marketplace.json

**Metadata-specific risky fixes** (always prompt):
- Add new bundle registrations to marketplace.json
- Remove plugins that might be in development
- Structural changes affecting multiple bundles

**Verification** (after fixes):
1. Re-run Steps 2-3 validations
2. Compare with initial analysis
3. Report: issues_resolved, issues_remaining, new_issues (should be 0)

### Step 8: Display Final Summary

```
╔════════════════════════════════════════════════════════════╗
║          Metadata Diagnostics Summary                      ║
╚════════════════════════════════════════════════════════════╝

Results:
- Bundles analyzed: {bundles_analyzed}
- Issues found: {total_issues}
- Issues fixed: {total_fixes}

Configuration Status: {✓ HEALTHY | ⚠ NEEDS ATTENTION | ✗ ERRORS REMAIN}

{if total_fixes > 0:
  "Fixes Applied:"
  - Component inventories updated: {inventory_fix_count}
  - Schema issues resolved: {schema_fix_count}
  - Marketplace registry corrected: {marketplace_fix_count}
}

{if remaining_issues > 0:
  "Next Steps:"
  1. Review remaining issues above
  2. Review remaining issues manually
  3. Manually fix complex issues
}

{if total_fixes == total_issues:
  "✅ All metadata is now consistent and valid!"
}
```

## CRITICAL RULES

**Discovery:**
- Use scan-marketplace-inventory.sh script as source of truth for component discovery
- Never use Bash for file discovery - only Glob for validation

**Validation:**
- Check component inventory accuracy (agents/commands/skills arrays)
- Validate schema compliance (remove invalid fields)
- Verify marketplace registry consistency
- Cross-reference all metadata files

**Autofix:**
- When auto-fix=true (default), automatically fix safe issues without prompts
- Always prompt user for risky fixes, even when auto-fix=true
- Component inventory mismatches are safe to auto-fix
- Invalid schema fields are safe to auto-fix
- Obsolete marketplace entries (non-existent sources) are safe to auto-fix

**Safety:**
- Git provides version control - no backup files needed
- Verify fixes by re-running all validations
- Report failed fixes clearly
- Continue processing even if individual bundles fail

**Error Handling:**
- If scan-marketplace-inventory.sh script fails: Abort (can't proceed without discovery)
- If individual bundle Read fails: Log error, skip bundle, continue
- If Edit fails: Log error, mark fix as failed, continue
- Non-blocking failures for individual bundles

**User Experience:**
- Clear severity indicators: ✓ (valid), ⚠ (warning), ✗ (error)
- Grouped findings by file type
- Statistics tracking throughout workflow
- Comprehensive before/after reporting

## STATISTICS TRACKING

Track throughout workflow:
- `bundles_discovered`: Count from scan-marketplace-inventory.sh script
- `bundles_analyzed`: Bundles successfully examined
- `plugin_json_issues`: Component + schema issues found
- `marketplace_json_issues`: Registry issues found
- `total_issues`: Aggregate issue count
- `total_fixes`: Count of fixes successfully applied
- `safe_fixes`: Count of auto-applied fixes
- `risky_fixes`: Count of user-confirmed fixes
- `failed_fixes`: Count of fixes that failed

Display all statistics in final summary.

## USAGE EXAMPLES

**Basic diagnostics with auto-fix (default):**
```
/plugin-diagnose-metadata
```

**Disable auto-fix (report only):**
```
/plugin-diagnose-metadata auto-fix=false
```

**Note:** Safe issues are auto-fixed by default. Risky fixes always prompt for confirmation.

## RELATED COMMANDS

- `scan-marketplace-inventory.sh` script - Discovers all marketplace resources (used internally)
- `/plugin-diagnose-skills` - Validates skill quality and standards
- `/plugin-diagnose-commands` - Validates command quality and structure
- `/plugin-diagnose-agents` - Validates agent quality and tool usage
- `/plugin-create-bundle` - Creates new bundles with correct metadata

## PURPOSE

**This command provides centralized metadata validation:**
- Validates all bundle plugin.json files (component inventory + schema compliance)
- Validates marketplace.json registry
- Ensures metadata consistency across the entire marketplace
- Auto-fixes safe metadata issues without user prompts