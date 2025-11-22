---
name: plugin-fix
description: Fix identified quality issues in marketplace components
---

# Fix Marketplace Issues

Apply fixes to quality issues identified by /plugin-diagnose command.

## Usage

```
/plugin-fix
```

## Workflow

When you invoke this command, I will:

1. **Check for previous diagnosis**:
   - If recent /plugin-diagnose was run: Use those results
   - If no recent diagnosis: Prompt user to run /plugin-diagnose first

2. **Load plugin-fix skill**:
   ```
   Skill: cui-plugin-development-tools:plugin-fix
   ```

3. **Invoke fix workflow**:
   - Categorize issues (safe vs risky)
   - Apply safe fixes automatically
   - Present risky fixes for confirmation
   - Verify fixes applied correctly

4. **Display results** with fixes applied and verification status

## Parameter Validation

**Required**: None (uses context from previous /plugin-diagnose)
**Optional**: None

**Error Handling**:
- No previous diagnosis → Prompt to run /plugin-diagnose first

## Fix Categorization

**Safe Fixes** (applied automatically):
- Missing frontmatter
- Array syntax for tools
- Missing required fields
- Trailing whitespace

**Risky Fixes** (require confirmation):
- Unused tool removal
- Rule 6/7 violations
- Pattern 22 violations

## Examples

```
User: /plugin-diagnose agents
[Results shown with 5 issues]
User: /plugin-fix
Result: Applies 3 safe fixes, prompts for 2 risky fixes

User: /plugin-fix
[No recent /plugin-diagnose]
Result: Error: No recent diagnosis found. Run /plugin-diagnose first.
```

## Related

- `/plugin-diagnose` - Find issues before fixing
- `/plugin-verify` - Verify marketplace after fixes
