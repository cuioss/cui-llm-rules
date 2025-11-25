---
name: maven-build-and-fix
description: Execute Maven build, analyze errors, delegate fixes to appropriate commands, and iterate until clean
---

# Build and Fix Command

Thin orchestrator that delegates Maven builds to cui-maven-rules skill, routes issues to fix commands, and iterates until clean.

## PARAMETERS

- **goals** (optional): Maven goals to execute (default: `-Ppre-commit clean install`)
- **push** (optional): Auto-commit changes after successful clean build (default: false)
- **module** (optional): Specific module to build (-pl flag)

## WORKFLOW

### Step 1: Load Skill and Parse Parameters

```
Skill: cui-maven:cui-maven-rules
```

Extract parameters from user input:
- `goals`: String (default: `-Ppre-commit clean install`)
- `push`: Boolean (default: false)
- `module`: String (optional)

### Step 2: Execute Maven Build via Skill Workflow

Invoke skill workflow:
```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: {goals}
  module: {module} (if specified)
  output_mode: structured
```

The skill handles:
- Clean goal separation (if needed)
- Log capture with `-l` flag
- Output parsing via script

### Step 3: Check Results and Route Issues

**If build_status == SUCCESS and total_issues == 0:**
- Skip to Step 5 (Report Success)

**Route issues to fix commands (max 5 iterations):**

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/java-implement-code files="{file}" task="Fix: {message}"` |
| `test_failure` | `/java-implement-tests files="{file}" task="Fix: {message}"` |
| `javadoc_warning` | `/java-fix-javadoc files="{file}"` |
| `dependency_error` | Report to user (manual POM fix required) |

### Step 4: Verify Fixes (Iterate)

After fix attempts, repeat Step 2 (without clean):
```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: {goals_without_clean}
  module: {module}
  output_mode: structured
```

**Iteration decision:**
- If issues_remaining > 0 AND iteration < 5: Repeat Step 3
- If issues_remaining == 0: Proceed to Step 5
- If iteration >= 5: Proceed to Step 6

### Step 5: Report Success

```
BUILD SUCCESS

Maven goals: {goals}
Iterations: {iteration_count}
Issues fixed: {total_fixed}
Output: target/maven-build.log
```

**If push=true:** Invoke `/cui-task-workflow:commit-changes`

### Step 6: Report Partial Success

```
BUILD PARTIAL

Max iterations: 5
Issues resolved: {resolved}/{total}
Remaining: compilation({n}), test({n}), javadoc({n})
Output: target/maven-build.log

Next: Review output file and run fix commands manually
```

**Do NOT commit if issues remain** (even if push=true)

## CRITICAL RULES

- NEVER execute `./mvnw` directly - always use skill workflow
- All build logic lives in cui-maven-rules skill
- This command only orchestrates: parse → delegate → iterate → report
- Maximum 5 iterations to prevent infinite loops
- Dependency errors require manual user intervention

## RELATED

- Skill: `cui-maven:cui-maven-rules` - Execute Maven Build workflow
- Command: `/java-implement-code` - Fix compilation errors
- Command: `/java-implement-tests` - Fix test failures
- Command: `/java-fix-javadoc` - Fix JavaDoc warnings
