---
name: cui-jsdoc-fix
description: Fix JSDoc errors and warnings from build/lint with content preservation
---

# CUI JSDoc Fix Command

Orchestrates systematic JSDoc violation fixing workflow with standards compliance.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-jsdoc-fix update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **files** - (Optional) Specific files to fix; if unset, analyze all JavaScript files
- **workspace** - (Optional) Workspace name for monorepo projects

## WORKFLOW

### Step 1: Identify JSDoc Violations

```
Task: jsdoc-violation-analyzer
Parameters:
- files: {files or '**/*.js'}
- scope: all

Returns structured violation list.
```

### Step 2: Prioritize Violations

Categorize by severity:
- CRITICAL: Exported/public API without JSDoc (fix first)
- WARNING: Internal functions without JSDoc
- SUGGESTION: Optional improvements

### Step 3: Fix Violations Systematically

For each violation (CRITICAL → WARNING):

```
Task: javascript-code-implementer
Parameters:
- files: {violation.file}
- description: |
  Add JSDoc documentation for {violation.target}.

  Type: {violation.type}
  Line: {violation.line}
  Fix suggestion: {violation.fix_suggestion}

  Follow cui-jsdoc standards.
```

Track: `fixes_applied`, `fixes_failed`

### Step 4: Verify Build

```
Task: npm-builder
Parameters:
- command: run lint (or run build)
- outputMode: DEFAULT

Verify no JSDoc errors remain.
```

### Step 5: Return Summary

```
JSDOC FIX COMPLETE

Violations Fixed:
- Critical: {critical_fixed}/{critical_total}
- Warnings: {warnings_fixed}/{warnings_total}

Files Modified: {count}

Build Status: {SUCCESS|PARTIAL}

Result: {summary}
```

## RELATED

- `jsdoc-violation-analyzer` - Identifies violations (Layer 3)
- `javascript-code-implementer` - Fixes violations (Layer 3)
- `npm-builder` - Verifies fixes (Layer 3)
