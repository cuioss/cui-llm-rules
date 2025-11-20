---
name: cui-fix-workflow
description: Common fix workflow patterns for diagnosis commands including categorization, safe fixes, prompting, and verification
allowed-tools: [Read, Edit, Grep, Glob]
---

# Fix Workflow - Common Patterns for Diagnosis Commands

Provides reusable patterns for categorizing, applying, and verifying fixes across diagnosis commands (skills, agents, commands).

## Purpose

This skill extracts the common fix workflow (Steps 7-9) shared across all diagnosis commands to eliminate duplication and ensure consistent fix application.

**Use this skill when:**
- Implementing or updating diagnosis commands
- Building fix workflows for marketplace components
- Ensuring consistent fix categorization and prompting patterns

## Standards Files

This skill provides patterns for:

1. **categorization-patterns.md** - Safe vs Risky fix categorization logic
2. **prompting-patterns.md** - AskUserQuestion structure for risky fixes
3. **verification-patterns.md** - Re-run analysis and before/after comparison
4. **tracking-patterns.md** - JSON structures for tracking fixes

## Workflow

### Step 1: Load Fix Workflow Skill

When a diagnosis command reaches the fix workflow phase:

```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

### Step 2: Apply Categorization Pattern

Read the categorization patterns:

```
Read: standards/categorization-patterns.md
```

Use the safe vs risky categorization logic to classify all issues found.

### Step 3: Load Tracking Patterns

Read the tracking patterns for fix lifecycle management:

```
Read: standards/tracking-patterns.md
```

Use these JSON structures throughout the fix workflow to track:
- Safe fixes applied
- Risky fixes prompted
- Risky fixes applied vs skipped
- Verification results

### Step 4: Apply Safe Fixes (if auto-fix=true)

If auto-fix parameter is true AND safe fixes exist:
- Apply component-specific safe fixes
- Track fixes applied using tracking patterns
- Use Edit tool for actual modifications

### Step 5: Prompt for Risky Fixes

If risky fixes exist (regardless of auto-fix setting):

Read the prompting patterns:

```
Read: standards/prompting-patterns.md
```

Use AskUserQuestion with the standard structure to present fixes to user.

### Step 6: Verify Fixes

After any fixes applied:

Read the verification patterns:

```
Read: standards/verification-patterns.md
```

Re-run component analysis and compare before/after results.

## Component-Specific Customization

Each diagnosis command defines:
- **Safe fix types** specific to that component (skills, agents, commands)
- **Risky fix categories** specific to that component
- **Re-analysis invocation** specific to that component (diagnose-skill, diagnose-agent, diagnose-command)

The workflow patterns remain consistent across all commands.

## Integration with Diagnosis Commands

Diagnosis commands reference this skill in their Step 7 (Categorize Issues):

```markdown
### Step 7: Categorize Issues for Fixing

**ALWAYS execute this step if any issues were found.**

Load fix workflow skill:
```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

Follow categorization patterns from skill.
```

## Quality Standards

- Fix workflow must be consistent across all diagnosis commands
- Categorization logic must clearly distinguish safe vs risky
- Prompting must use standard AskUserQuestion structure
- Verification must always compare before/after metrics
- Tracking must use consistent JSON structures

## See Also

- `/plugin-diagnose-skills` - Uses this workflow for skill fixes
- `/plugin-diagnose-agents` - Uses this workflow for agent fixes
- `/plugin-diagnose-commands` - Uses this workflow for command fixes
