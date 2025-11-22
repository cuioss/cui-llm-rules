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

## WORKFLOW

When you invoke this command, I will:

1. **Load plugin-doctor skill**:
   ```
   Skill: cui-plugin-development-tools:plugin-doctor
   ```

2. **Invoke doctor-* workflows for all component types**:
   - Diagnoses all agents, commands, skills, metadata, and scripts
   - Reports comprehensive health status
   - Categorizes all issues found

3. **Display comprehensive report**:
   - Summary of all component types
   - Issue counts by severity
   - Recommendations for fixes

4. **Offer doctor option**: "Run /plugin-doctor {type} to diagnose and fix specific components"

## PARAMETERS

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

Run /plugin-doctor {type} to diagnose and fix
```

## Examples

```
User: /plugin-verify
Result: Invokes plugin-doctor workflows for all component types
        Displays comprehensive health report for entire marketplace
```

## CONTINUOUS IMPROVEMENT RULE

After executing this command, if you discover any opportunities to improve it, invoke:

`/plugin-maintain command-name=plugin-verify update="[improvement description]"`

Common improvements:
- More comprehensive verification checks
- Better report formatting
- Additional component types to verify

## Related

- `/plugin-doctor` - Diagnose and fix specific component types
- `/plugin-create` - Create new components
