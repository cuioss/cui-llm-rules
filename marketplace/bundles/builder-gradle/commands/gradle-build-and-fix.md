---
description: Execute Gradle build, analyze errors, delegate fixes to appropriate commands, and iterate until clean
allowed_tools:
  - Skill
  - SlashCommand
  - Read
  - Grep
  - Glob
---

# /gradle-build-and-fix Command

Iterative build-and-fix loop with automatic issue routing for Gradle projects.

## Parameters

| Parameter | Default | Type | Description |
|-----------|---------|------|-------------|
| `tasks` | `clean build` | string | Gradle tasks to execute |
| `project` | none | string | Specific subproject (-p flag) |
| `push` | `false` | boolean | Auto-commit on clean build |

## Workflow

### Step 1: Parse Parameters

Apply defaults:
- `tasks` defaults to `clean build`
- `project` is optional (builds root if not specified)
- `push` defaults to `false`

### Step 2: Load Previous Execution Duration

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: commands.gradle-build-and-fix.last_execution
```

Calculate timeout: `duration_ms * 1.25` (25% safety margin)

### Step 3: Build Loop (Max 5 Iterations)

For each iteration:

1. **Execute Gradle Build**:
   ```
   Skill: builder-gradle:builder-gradle-rules
   Workflow: Execute Gradle Build
   Parameters:
     tasks: {tasks}
     project: {project}
     timeout: {calculated_timeout}
     output_mode: structured
   ```

2. **Check Results**:
   - If `issues.total == 0`: Go to Step 4
   - If `issues.total > 0`: Route issues for fixing

3. **Route Issues to Fix Commands**:
   | Issue Type | Fix Command |
   |------------|-------------|
   | `compilation_error` | `/java-implement-code files="{file}" task="Fix: {message}"` |
   | `test_failure` | `/java-implement-tests files="{file}" task="Fix: {message}"` |
   | `javadoc_warning` | `/java-fix-javadoc files="{file}"` |
   | `dependency_error` | Report to user (manual fix required) |

4. **Re-run Build**:
   - Remove `clean` from tasks for subsequent iterations
   - Continue loop

### Step 4: Record Execution Results

Only for successful builds:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: commands.gradle-build-and-fix.last_execution
Value: {
  "date": "{ISO-8601}",
  "status": "SUCCESS",
  "duration_ms": {duration},
  "duration_human": "{formatted}"
}
```

### Step 5: Report Results

**Success Format**:
```
BUILD SUCCESS
Tasks: {tasks} | Iterations: {n} | Fixed: {n}
```

If `push=true`, invoke: `/cui-task-workflow:commit-changes`

**Partial Format**:
```
BUILD PARTIAL
Resolved: {n}/{total} | Remaining: compilation({n}), test({n}), javadoc({n})
```

## Exit Conditions

- `issues_remaining > 0 AND iteration < 5`: Re-run fixes
- `issues_remaining == 0`: Report SUCCESS
- `iteration >= 5`: Report PARTIAL (skip step 4)

## Issue Routing Table

| Issue Type | Target Command | Reason |
|------------|----------------|--------|
| `compilation_error` | `/java-implement-code` | Source code fixes |
| `test_failure` | `/java-implement-tests` | Test code fixes |
| `javadoc_warning` | `/java-fix-javadoc` | Documentation fixes |
| `dependency_error` | User | Build configuration issues |
| `deprecation_warning` | `/java-implement-code` | Code modernization |
| `unchecked_warning` | `/java-implement-code` | Type safety fixes |

## Example Usage

```bash
# Basic build
/gradle-build-and-fix

# Specific tasks
/gradle-build-and-fix tasks="build test"

# Build specific subproject
/gradle-build-and-fix project=":api" tasks="build"

# Build and commit on success
/gradle-build-and-fix push=true
```
