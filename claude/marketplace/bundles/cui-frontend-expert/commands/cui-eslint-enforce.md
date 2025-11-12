---
name: cui-eslint-enforce
description: Enforce ESLint standards by fixing violations systematically
---

# CUI ESLint Enforce Command

Orchestrates systematic ESLint violation fixing workflow with standards compliance.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-eslint-enforce update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **files** - (Optional) Specific files to fix; if unset, analyze all lintable files
- **workspace** - (Optional) Workspace name for monorepo projects
- **fix-mode** - `auto` (ESLint --fix) or `manual` (agent fixes); default: `auto`

## WORKFLOW

### Step 1: Run ESLint

```
Task: npm-builder
Parameters:
- command: run lint (or npx eslint .)
- outputMode: STRUCTURED
- workspace: {if specified}

Get structured lint violations.
```

### Step 2: Auto-Fix (if fix-mode=auto)

```
Task: npm-builder
Parameters:
- command: run lint -- --fix
- outputMode: DEFAULT

Let ESLint auto-fix violations.
```

Re-run lint to check remaining issues.

### Step 3: Manual Fix (for unfixable violations)

For each remaining violation:

```
SlashCommand: /cui-javascript-implement-code task="Fix ESLint violation: {violation.message}

Rule: {violation.rule}
Line: {violation.line}

Apply appropriate fix following ESLint and CUI standards.
Verify build after changes." files="{violation.file}"
```

### Step 4: Verify Clean Lint

```
Task: npm-builder
Parameters:
- command: run lint
- outputMode: DEFAULT

Verify zero violations.
```

### Step 5: Return Summary

```
ESLINT ENFORCE COMPLETE

Violations Fixed:
- Auto-fixed: {auto_count}
- Manually fixed: {manual_count}
- Total: {total_count}

Files Modified: {count}

Lint Status: {CLEAN|PARTIAL}
```

## RELATED

- `npm-builder` - Executes ESLint (Layer 3)
- `/cui-javascript-implement-code` - Fixes manual violations (Layer 2)
