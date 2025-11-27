---
name: npm-build-and-fix
description: Execute npm build, analyze errors, delegate fixes to appropriate commands, and iterate until clean
---

# npm Build and Fix Command

Orchestrates npm/npx builds, routes issues to fix commands, iterates until clean.

## PARAMETERS

| Parameter | Default | Description |
|-----------|---------|-------------|
| `command` | `run test` | npm/npx command to execute |
| `workspace` | (none) | Specific workspace package to target |
| `push` | `false` | Auto-commit on clean build |

## WORKFLOW

### Step 1: Parse Parameters

Extract from user input. Apply defaults for missing values.

### Step 2: Load Previous Execution Data

Read previous execution duration for timeout calculation:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: commands.npm-build-and-fix.last_execution
```

**Calculate timeout:**
- If previous duration exists: `timeout = duration_ms * 1.25` (25% safety margin)
- If no previous data: use default timeout (120000ms)

### Step 3: Build Loop (max 5 iterations)

```
Skill: builder:builder-npm-rules
Workflow: Execute npm Build
Parameters: command, workspace, output_mode=structured
```

**On SUCCESS with 0 issues:** Proceed to Step 4 (Record Results)

**On issues:** Route to fix commands, then re-run build:

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/js-implement-code files="{file}" task="Fix: {message}"` |
| `test_failure` | `/js-implement-tests files="{file}" task="Fix: {message}"` |
| `lint_error` | `/js-enforce-eslint files="{file}"` |
| `playwright_error` | `/js-implement-tests files="{file}" task="Fix: {message}"` |
| `dependency_error` | Report to user (manual package.json fix required) |

**Iteration limits:**
- issues_remaining > 0 AND iteration < 5 → re-run fixes
- issues_remaining == 0 → Proceed to Step 4
- iteration >= 5 → Report partial (skip Step 4)

### Step 4: Record Execution Results

On successful build (0 issues), record execution data:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: commands.npm-build-and-fix.last_execution
Value: {
  "date": "{current-date}",
  "status": "SUCCESS",
  "duration_ms": {total-duration},
  "duration_human": "{formatted-duration}"
}
```

### Step 5: Report Results

**Success:**
```
BUILD SUCCESS
Command: {command} | Iterations: {n} | Fixed: {n}
```
If `push=true`: Invoke `/cui-task-workflow:commit-changes`

**Partial (max iterations reached):**
```
BUILD PARTIAL
Resolved: {n}/{total} | Remaining: compilation({n}), test({n}), lint({n})
```
Do NOT commit if issues remain.

## CRITICAL RULES

- NEVER execute `npm` or `npx` directly - use skill workflow
- Maximum 5 iterations to prevent infinite loops
- Dependency errors require manual intervention

## RELATED

- Skill: `builder:builder-npm-rules` - Build execution and parsing
- Skill: `cui-utilities:claude-run-configuration` - Execution history
- Command: `/js-implement-code` - Compilation fixes
- Command: `/js-implement-tests` - Test fixes
- Command: `/js-enforce-eslint` - Lint fixes
