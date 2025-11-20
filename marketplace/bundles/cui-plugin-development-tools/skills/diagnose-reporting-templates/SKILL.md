---
name: diagnose-reporting-templates
description: Common reporting templates for plugin-diagnose-* orchestrator commands
---

# Diagnose Command Reporting Templates

This skill provides common templates used by all plugin-diagnose-* orchestrator commands to ensure consistent reporting format and reduce duplication.

## Summary Report Template

Use this template for final cross-bundle summary reports in all diagnose commands.

### Template Format

```
==================================================
{Component Type} Doctor - All Bundles Complete
==================================================

Bundles Processed: {total_bundles}
Total {Components}: {total_components}

Overall Statistics:
- {Components} clean: {count} ✅
- {Components} with warnings: {count} ⚠️
- {Components} with critical issues: {count} ❌

Total Issues:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}

Fixes Applied:
- Safe fixes: {count}
- Risky fixes: {count}
- Issues resolved: {count}

By Bundle:
- {bundle-1}: {count} {components} | {issues} issues | {fixes} fixed
- {bundle-2}: {count} {components} | {issues} issues | {fixes} fixed
...

{if all clean}
✅ All {components} across all bundles are high quality!
{endif}
```

### Variables

Replace these variables when using the template:

- `{Component Type}` → "Agents", "Commands", "Skills", or "Metadata"
- `{Components}` (plural capitalized) → "Agents", "Commands", "Skills", or "Bundles"
- `{components}` (plural lowercase) → "agents", "commands", "skills", or "bundles"
- `{total_bundles}` → Number of bundles processed
- `{total_components}` → Total count across all bundles
- `{count}` → Specific count for each category
- `{bundle-N}` → Bundle name
- `{issues}` → Issue count for bundle
- `{fixes}` → Fix count for bundle

### Usage in Commands

In your diagnose command's final summary step:

```markdown
**Display final summary using template:**

```
Skill: cui-plugin-development-tools:diagnose-reporting-templates
```

Use "Summary Report Template" with variables:
- Component Type: "Agents"
- Components: "agents"

Populate with aggregated metrics from all bundles processed.
```

### Example Output

For plugin-diagnose-agents:

```
==================================================
Agents Doctor - All Bundles Complete
==================================================

Bundles Processed: 8
Total Agents: 15

Overall Statistics:
- Agents clean: 12 ✅
- Agents with warnings: 2 ⚠️
- Agents with critical issues: 1 ❌

Total Issues:
- Critical: 3
- Warnings: 5
- Suggestions: 8

Fixes Applied:
- Safe fixes: 7
- Risky fixes: 2
- Issues resolved: 9

By Bundle:
- cui-plugin-development-tools: 8 agents | 10 issues | 6 fixed
- cui-java-expert: 3 agents | 3 issues | 2 fixed
- cui-frontend-expert: 4 agents | 3 issues | 1 fixed

✅ All agents across all bundles are high quality!
```

## Fix Workflow Pattern

Common workflow pattern for categorizing and applying fixes across all diagnose commands.

### Step X: Categorize Issues

**Safe fixes** (auto-apply without prompting):
- Formatting corrections (whitespace, indentation)
- Adding missing blank lines before lists
- Fixing obvious typos in field names
- Standardizing naming patterns
- Adding missing YAML fields with default values
- Fixing broken cross-references to existing content

**Risky fixes** (require user approval):
- Content restructuring or reorganization
- Removing content or sections
- Changing logic or behavior
- Modifying YAML structure significantly
- Renaming files or major refactoring
- Deleting deprecated but still-used content

### Step X+1: Apply Safe Fixes

For each safe issue:
1. Apply fix using Edit tool
2. Increment counter: `safe_fixes_applied`
3. Log to console: "✅ Fixed: {description}"
4. Track file path for verification

### Step X+2: Handle Risky Fixes

For each risky issue:
1. Use AskUserQuestion to present fix description and get approval
2. If approved:
   - Apply fix using Edit tool
   - Increment counter: `risky_fixes_applied`
   - Log: "✅ Fixed (with approval): {description}"
3. If rejected:
   - Skip fix
   - Increment counter: `risky_fixes_skipped`
   - Log: "⏭️  Skipped: {description}"

### Step X+3: Verify Fixes

After all fixes applied:
1. Re-run diagnostic agent on each modified file
2. Verify issues resolved:
   - Compare before/after issue lists
   - Check no new issues introduced
   - Confirm expected issue count reduction
3. Report verification results:
   - `{fixes_succeeded}` - Fixes that resolved issues
   - `{fixes_failed}` - Fixes that didn't resolve issues or introduced new ones
   - `{new_issues}` - Any new issues detected after fixes

### Usage in Commands

Reference this pattern in your diagnose command's fix workflow phase:

```markdown
### Step 7: Categorize and Apply Fixes

**Follow fix workflow pattern:**

```
Skill: cui-plugin-development-tools:diagnose-reporting-templates
```

Use "Fix Workflow Pattern" to:
1. Categorize issues as safe vs risky
2. Auto-apply safe fixes
3. Prompt for risky fix approval
4. Verify all fixes resolved issues

Track metrics: `safe_fixes_applied`, `risky_fixes_applied`, `risky_fixes_skipped`
```

## Benefits

**Consistency**: All diagnose commands produce identical report formats

**Maintainability**: Update templates in one place, affects all commands

**Reduced Duplication**: Eliminates 200+ lines of duplicated template code

**Token Efficiency**: Commands reference templates instead of embedding full examples
