---
name: js-fix-jsdoc
description: Fix JSDoc errors and warnings from build/lint with content preservation
---

# CUI JSDoc Fix Command

Orchestrates systematic JSDoc violation fixing workflow with standards compliance.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=js-fix-jsdoc update="[your improvement]"` with:

**Improvement areas**:
- Enhanced violation detection for TypeScript JSDoc patterns
- Better prioritization based on API surface and public exports
- Improved fix suggestions leveraging type inference
- Expanded content preservation during complex documentation updates
- Advanced integration with ESLint JSDoc plugins and rules

## PARAMETERS

- **files** - (Optional) Specific files to fix; if unset, analyze all JavaScript files
- **workspace** - (Optional) Workspace name for monorepo projects

## WORKFLOW

### Step 1: Identify JSDoc Violations

**Load skill and execute workflow:**
```
Skill: cui-frontend-expert:cui-jsdoc
Execute workflow: Analyze JSDoc Violations
```

Or run script directly:
```bash
# Analyze directory
python3 scripts/analyze-jsdoc-violations.py --directory src/

# Analyze specific file
python3 scripts/analyze-jsdoc-violations.py --file {files}
```

Script returns structured JSON with violations categorized by severity (CRITICAL, WARNING, SUGGESTION).

### Step 2: Prioritize Violations

Categorize by severity:
- CRITICAL: Exported/public API without JSDoc (fix first)
- WARNING: Internal functions without JSDoc
- SUGGESTION: Optional improvements

### Step 3: Fix Violations Systematically

For each violation (CRITICAL → WARNING):

```
SlashCommand: /cui-frontend-expert:js-implement-code task="Add JSDoc documentation for {violation.target}.

Type: {violation.type}
Line: {violation.line}
Fix suggestion: {violation.fix_suggestion}

Follow cui-jsdoc standards.
Verify build after changes." files="{violation.file}"
```

Track: `fixes_applied`, `fixes_failed`

### Step 4: Verify Build

**Execute lint command:**
```bash
npm run lint > target/npm-lint-output.log 2>&1
```

**Parse output to verify no JSDoc errors remain:**
```bash
python3 skills/cui-javascript-project/scripts/parse-npm-output.py \
    --log target/npm-lint-output.log --mode errors
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

- Skill: `cui-frontend-expert:cui-jsdoc` - Analyze JSDoc Violations workflow
- Skill: `cui-frontend-expert:cui-javascript-project` - Parse npm Build Output workflow
- Command: `/js-implement-code` - Fixes violations
