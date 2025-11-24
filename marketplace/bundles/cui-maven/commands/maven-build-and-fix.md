---
name: maven-build-and-fix
description: Execute Maven build, analyze errors, delegate fixes to appropriate commands, and iterate until clean
---

# Build and Fix Command

Orchestrates Maven builds, analyzes errors, delegates fixes to appropriate commands, and iterates until the project builds cleanly.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/plugin-update-command command-name=maven-build-and-fix update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **push** (optional): Auto-commit and push changes after successful clean build
- **goals** (optional): Maven goals to execute (default: `-Ppre-commit clean install`)

## WORKFLOW

### Step 1: Parse Parameters

Extract parameters:
- `push`: boolean flag for auto-commit (default: false)
- `goals`: Maven goals string (default: `-Ppre-commit clean install`)

### Step 2: Execute Maven Build

**Execute clean first (if goals contain clean):**
```bash
./mvnw clean
```

**Then execute build with log capture:**
```bash
./mvnw -l target/build-output.log {goals_without_clean}
```

Store the log path as `{output_file}`.

NOTE: Clean runs separately to avoid deleting `target/` after log file creation. The `-l` flag avoids shell redirection operators which require additional permissions.

### Step 3: Analyze Build Output

**Load skill and execute workflow:**
```
Skill: cui-maven:cui-maven-rules
Execute workflow: Parse Maven Build Output
```

**Parse the build log:**
```bash
python3 scripts/parse-maven-output.py \
    --log {output_file} \
    --mode structured
```

**Collect structured results:**
```json
{
  "status": "success|error",
  "data": {
    "build_status": "SUCCESS|FAILURE",
    "issues": [...],
    "summary": {
      "compilation_errors": 0,
      "test_failures": 0,
      "javadoc_warnings": 0,
      "dependency_errors": 0
    }
  }
}
```

### Step 4: Route Issues to Fix Commands

**If build_status == SUCCESS and total_issues == 0:**
- Skip to Step 6 (Report Success)

**For each issue category, delegate:**

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/java-implement-code files="{file}" task="Fix: {message}"` |
| `test_failure` | `/java-implement-tests files="{file}" task="Fix: {message}"` |
| `javadoc_warning` | `/java-fix-javadoc files="{file}"` |
| `dependency_error` | Report to user (manual POM fix required) |

### Step 5: Verify Fixes (Re-build)

**After fix attempts, re-run build (no clean needed - just verify):**
```bash
./mvnw -l target/build-output-verify.log {goals_without_clean}
```

**Re-analyze with script:**
```bash
python3 scripts/parse-maven-output.py \
    --log {verify_output_file} \
    --mode structured
```

**Iteration decision:**
- If issues_remaining > 0 AND iteration_count < 5: Repeat Step 4
- If issues_remaining == 0: Proceed to Step 6
- If iteration_count >= 5: Proceed to Step 7 (Partial Success)

### Step 6: Report Success

```
BUILD SUCCESS

Maven goals: {goals}
Build duration: {duration}
Issues fixed: {total_fixed}
Iterations: {iteration_count}
Files modified: {count}
Output: {output_file}
```

**If push=true:** Invoke `/cui-task-workflow:commit-changes`

### Step 7: Report Partial Success

```
BUILD PARTIAL

Maven goals: {goals}
Max iterations reached: 5
Issues resolved: {resolved}/{total}
Remaining: compilation({n}), test({n}), javadoc({n})
Output: {output_file}

Next: Review output file and run fix commands manually
```

**Do NOT commit if issues remain** (even if push=true)

## RELATED

- Skill: `cui-maven:cui-maven-rules` - Parse Maven Build Output workflow
- Command: `/java-implement-code` - Fix compilation errors
- Command: `/java-implement-tests` - Fix test failures
- Command: `/java-fix-javadoc` - Fix JavaDoc warnings
