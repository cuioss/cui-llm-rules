---
name: plugin-verify
description: Verify complete marketplace health
---

# Verify Marketplace

Run comprehensive marketplace verification checking all components.

## Usage

```
/plugin-verify
```

## Workflow

When you invoke this command, I will:

1. **Load plugin-diagnose skill**:
   ```
   Skill: cui-plugin-development-tools:plugin-diagnose
   ```

2. **Invoke validate-marketplace workflow**:
   - Diagnoses all agents, commands, skills, metadata, and scripts
   - Reports comprehensive health status
   - Categorizes all issues found

3. **Display comprehensive report**:
   - Summary of all component types
   - Issue counts by severity
   - Recommendations for fixes

4. **Offer fix option**: "Run /plugin-fix to apply fixes"

## Parameter Validation

**Required**: None
**Optional**: None

## Report Structure

```
Marketplace Verification Summary
================================
Agents: X issues (Y critical)
Commands: X issues (Y critical)
Skills: X issues (Y critical)
Metadata: X issues (Y critical)
Scripts: X issues (Y critical)

Total: X issues across Y components

Run /plugin-fix to apply fixes
```

## Examples

```
User: /plugin-verify
Result: Invokes plugin-diagnose:validate-marketplace
        Displays comprehensive health report for entire marketplace
```

## Related

- `/plugin-diagnose` - Diagnose specific component types
- `/plugin-fix` - Apply fixes to verified issues
