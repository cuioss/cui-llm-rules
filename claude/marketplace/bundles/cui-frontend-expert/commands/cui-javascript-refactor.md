---
name: cui-javascript-refactor
description: Execute systematic JavaScript refactoring with standards compliance verification
---

# CUI JavaScript Refactor Command

Orchestrates systematic JavaScript code refactoring and maintenance workflow with comprehensive standards compliance verification.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-javascript-refactor update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **workspace** - (Optional) Workspace name for single workspace refactoring
- **scope** - Refactoring scope: `full` (default), `standards`, `modernize`, `documentation`
- **priority** - Priority filter: `high`, `medium`, `low`, `all` (default: `all`)

## WORKFLOW

### Step 1: Load Maintenance Standards

```
Skill: cui-javascript
Skill: cui-javascript-linting

Load standards for violation detection.
```

### Step 2: Pre-Refactoring Verification

**Build verification:**
```
Task: npm-builder
- command: run build
- outputMode: DEFAULT

Must pass before refactoring.
```

**Test verification:**
```
Task: npm-builder
- command: run test
- outputMode: DEFAULT

All tests must pass.
```

**Coverage baseline:**
```
SlashCommand: /javascript-coverage-report

Store baseline metrics.
```

### Step 3: Standards Compliance Audit

Analyze codebase for violations:
- Code organization violations
- Modern JavaScript adoption opportunities
- ESLint violations
- JSDoc gaps
- Legacy patterns (var, callbacks, etc.)
- Unused code

Use Explore agent to scan codebase.

### Step 4: Prioritize Violations

Apply prioritization framework:
- HIGH: Security, API contracts, fundamental design
- MEDIUM: Maintainability, modernization
- LOW: Style and optimization

Filter by `priority` parameter.

### Step 5: Execute Refactoring

Process violations systematically (file-by-file or workspace-by-workspace):

For each violation:
```
Task: javascript-code-implementer
Parameters:
- files: {violation.file}
- description: |
  Fix {violation.type}:
  {violation.description}

  Apply CUI JavaScript standards.
```

### Step 6: Verification After Each Fix

```
Task: npm-builder
- command: run build && run test
- outputMode: DEFAULT

Ensure no regressions.
```

### Step 7: Final Verification

**Complete build:**
```
Task: npm-builder
- command: run build
```

**Full test suite:**
```
Task: npm-builder
- command: run test
```

**Coverage verification:**
```
SlashCommand: /javascript-coverage-report

Compare to baseline.
```

### Step 8: Return Summary

```
REFACTORING SUMMARY

Scope: {scope}
Priority: {priority}

Violations Fixed:
- HIGH: {high_count}
- MEDIUM: {medium_count}
- LOW: {low_count}

Files Modified: {count}

Coverage:
- Baseline: {baseline}%
- Final: {final}%
- Change: {delta}%

Build/Test Status: {SUCCESS|FAILURE}
```

## SCOPE DEFINITIONS

- **full**: All violation types
- **standards**: Code organization, patterns, best practices
- **modernize**: ES6+ adoption, async/await, modern patterns
- **documentation**: JSDoc, comments

## RELATED

- `javascript-code-implementer` - Implements fixes (Layer 3)
- `npm-builder` - Verifies changes (Layer 3)
- `cui-javascript` skill - Standards enforced
