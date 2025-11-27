---
name: maven-build-and-fix
description: Execute Maven build, analyze errors, delegate fixes to appropriate commands, and iterate until clean
---

# Build and Fix Command

Orchestrates Maven builds, routes issues to fix commands, iterates until clean.

## PARAMETERS

| Parameter | Default | Description |
|-----------|---------|-------------|
| `goals` | `clean install` | Maven goals to execute |
| `profile` | `pre-commit` | Maven profile (-P flag) |
| `module` | (none) | Specific module (-pl flag) |
| `push` | `false` | Auto-commit on clean build |

## WORKFLOW

### Step 1: Parse Parameters

Extract from user input. Apply defaults for missing values.

### Step 2: Load Previous Execution Data

Read previous execution duration for timeout calculation:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: commands.maven-build-and-fix.last_execution
```

**Calculate timeout:**
- If previous duration exists: `timeout = duration_ms * 1.25` (25% safety margin)
- If no previous data: use default timeout (120000ms for standard builds)

### Step 3: Build Loop (max 5 iterations)

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters: goals, profile, module, output_mode=structured
```

**On SUCCESS with 0 issues:** Proceed to Step 4 (Record Results)

**On issues:** Route to fix commands, then re-run build (without `clean`):

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/java-implement-code files="{file}" task="Fix: {message}"` |
| `test_failure` | `/java-implement-tests files="{file}" task="Fix: {message}"` |
| `javadoc_warning` | `/java-fix-javadoc files="{file}"` |
| `dependency_error` | Report to user (manual POM fix required) |

**Iteration limits:**
- issues_remaining > 0 AND iteration < 5 → re-run fixes
- issues_remaining == 0 → Proceed to Step 4
- iteration >= 5 → Report partial (skip Step 4)

### Step 4: Record Execution Results

On successful build (0 issues), record execution data:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: commands.maven-build-and-fix.last_execution
Value: {
  "date": "{current-date}",
  "status": "SUCCESS",
  "duration_ms": {total-duration},
  "duration_human": "{formatted-duration}"
}
```

**Note:** Only record duration for successful builds. Failed builds have unpredictable durations.

### Step 5: Report Results

**Success:**
```
BUILD SUCCESS
Goals: {profile} {goals} | Iterations: {n} | Fixed: {n}
```
If `push=true`: Invoke `/cui-task-workflow:commit-changes`

**Partial (max iterations reached):**
```
BUILD PARTIAL
Resolved: {n}/{total} | Remaining: compilation({n}), test({n}), javadoc({n})
```
Do NOT commit if issues remain.

## CRITICAL RULES

- NEVER execute `./mvnw` directly - use skill workflow
- Maximum 5 iterations to prevent infinite loops
- Dependency errors require manual intervention

## RELATED

- Skill: `cui-maven:cui-maven-rules` - Build execution and parsing
- Skill: `cui-utilities:claude-run-configuration` - Execution history and timeout calculation
- Command: `/java-implement-code` - Compilation fixes
- Command: `/java-implement-tests` - Test fixes
- Command: `/java-fix-javadoc` - JavaDoc fixes
