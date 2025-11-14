---
name: cui-maven-build-and-fix
description: Execute Maven build, analyze errors, delegate fixes to appropriate commands, and iterate until clean
---

# Build and Fix Command

Comprehensive project verification command that orchestrates Maven builds, analyzes errors, delegates fixes to appropriate commands, and iterates until the project builds cleanly. Renamed from `/cui-build-and-verify` to reflect its active fix-and-iterate workflow.

## CONTINUOUS IMPROVEMENT RULE

**This command should be improved using**: `/plugin-update-command cui-maven-build-and-fix`

**Improvement areas**:
- Improved issue categorization and routing strategies
- Better error analysis and fix delegation patterns
- Enhanced iteration logic and convergence detection
- More effective command orchestration and result aggregation
- Improved performance tracking and reporting

## PARAMETERS

- **push** (optional): Auto-commit and push changes after successful clean build
- **goals** (optional): Maven goals to execute (default: `-Ppre-commit clean install`)

## WORKFLOW

### Step 1: Parse Parameters

**Extract parameters:**
- `push`: boolean flag for auto-commit (default: false)
- `goals`: Maven goals string (default: `-Ppre-commit clean install`)

**Validate:**
- Goals string must not include `./mvnw` prefix (added automatically by maven-builder)
- Push flag must be boolean

### Step 2: Initial Build Execution

**Invoke maven-builder agent:**
```
Task:
  subagent_type: maven-builder
  description: Execute Maven build
  prompt: |
    Execute Maven build with goals: {goals}

    Return structured results with:
    - Build status (SUCCESS/FAILURE)
    - Categorized issues (compilation_error, test_failure, javadoc_warning, etc.)
    - File locations and line numbers
    - Error messages
```

**Collect structured results:**
```json
{
  "status": "SUCCESS|FAILURE",
  "output_file": "target/build-output-{timestamp}.log",
  "issues": [
    {
      "type": "compilation_error|test_failure|javadoc_warning|...",
      "file": "path/to/File.java",
      "line": 123,
      "message": "error message",
      "severity": "ERROR|WARNING"
    }
  ],
  "summary": {
    "compilation_errors": count,
    "test_failures": count,
    "javadoc_warnings": count,
    "other_warnings": count
  }
}
```

**Error handling:**
```
If maven-builder fails to execute:
  ❌ Error: Maven build execution failed
  Error: {error_message}

  Options:
  - [R]etry build
  - [A]bort command

  Do NOT proceed with fix attempts.
```

### Step 3: Analyze Build Results

**If status == SUCCESS and issues count == 0:**
- Skip to Step 6 (Report Success)

**If status == FAILURE or issues count > 0:**
- Continue to Step 4 (Fix Issues)

**Categorize issues by type:**
```
Java Issues:
- compilation_error: Java compilation failures
- test_failure: JUnit test failures
- javadoc_warning: JavaDoc documentation issues

Other Issues:
- dependency_conflict: Maven dependency issues
- resource_error: Missing resource files
- configuration_error: POM/Maven config issues
```

**Route to fix strategies:**
- Java issues → Delegate to /cui-orchestrate-java-task
- Dependency issues → Report to user (manual intervention)
- Configuration errors → Report to user (manual intervention)

### Step 4: Delegate Fixes (Iteration Loop)

**For each issue category with fixes available:**

**Java Issues (compilation, test, javadoc):**
```
SlashCommand: /cui-java-expert:cui-orchestrate-java-task task="Fix {issue_category}: {issue_details}"
```

Parameters to pass:
- Issue type (compilation_error, test_failure, javadoc_warning)
- Affected files list
- Error messages
- Line numbers

**Collect fix results:**
- Files modified
- Changes made
- Fix status (success/partial/failure)

**Error handling:**
```
If /cui-orchestrate-java-task fails:
  ⚠️  Fix attempt failed: {issue_category}
  Error: {error_message}

  Options:
  - [R]etry fix
  - [S]kip this category
  - [A]bort command

  Track failure for final report.
```

### Step 5: Verify Fixes (Re-build)

**After all fix attempts, re-run maven-builder:**
```
Task:
  subagent_type: maven-builder
  description: Verify fixes
  prompt: |
    Execute Maven build with goals: {goals}

    Verify that previous issues are resolved.
    Return structured results.
```

**Compare results:**
- Issues remaining vs issues resolved
- New issues introduced (regression check)
- Overall status improvement

**Iteration decision:**
```
If issues_remaining > 0 AND iteration_count < max_iterations:
  → Repeat Step 4 (Delegate Fixes)

If issues_remaining == 0:
  → Proceed to Step 6 (Report Success)

If iteration_count >= max_iterations:
  → Proceed to Step 7 (Report Partial Success)
```

**Max iterations:** 5 (configurable)

### Step 6: Report Success (Clean Build)

**Display success report:**
```
╔════════════════════════════════════════════════════════════╗
║          Build and Fix - SUCCESS                           ║
╚════════════════════════════════════════════════════════════╝

✅ Build Status: CLEAN

Build Details:
- Maven goals: {goals}
- Output file: {output_file}
- Build duration: {duration}

Issues Resolved:
- Compilation errors: {count_fixed}
- Test failures: {count_fixed}
- JavaDoc warnings: {count_fixed}
- Total issues fixed: {total_fixed}

Iterations: {iteration_count}
Files modified: {files_modified_count}
```

**If push parameter is true:**
- Proceed to Step 8 (Commit Changes)

**Otherwise:**
- End command

### Step 7: Report Partial Success (Issues Remaining)

**Display partial success report:**
```
╔════════════════════════════════════════════════════════════╗
║          Build and Fix - PARTIAL SUCCESS                   ║
╚════════════════════════════════════════════════════════════╝

⚠️  Build Status: ISSUES REMAIN

Build Details:
- Maven goals: {goals}
- Output file: {output_file}
- Build duration: {duration}
- Max iterations reached: {max_iterations}

Progress:
- Issues resolved: {issues_resolved}
- Issues remaining: {issues_remaining}
- Iterations completed: {iteration_count}

Remaining Issues by Type:
- Compilation errors: {count}
- Test failures: {count}
- JavaDoc warnings: {count}

Files modified: {files_modified_count}

Next Steps:
- Review remaining issues in: {output_file}
- Run /cui-orchestrate-java-task manually for specific fixes
- Run /cui-maven-build-and-fix again to retry
```

**Do NOT commit if issues remain** (even if push=true)

### Step 8: Commit Changes (Optional)

**If push parameter is true AND build is clean:**

```
Task:
  subagent_type: commit-changes
  description: Commit build fixes
  prompt: |
    Commit all changes from build fix iterations.

    Generate commit message describing:
    - Issues fixed (compilation, test, javadoc)
    - Files modified
    - Iteration count

    Format: "fix(build): resolve {issue_count} build issues

    - Compilation errors: {count}
    - Test failures: {count}
    - JavaDoc warnings: {count}

    Iterations: {count}
    Files modified: {files_modified_count}"

    Push to remote repository.
```

**Error handling:**
```
If commit-changes fails:
  ❌ Error: Commit failed
  Error: {error_message}

  Note: Changes remain uncommitted in working directory.
  You can commit manually or run /cui-maven-build-and-fix push again.
```

## STATISTICS TRACKING

Track throughout workflow:
- `iteration_count`: Number of build-fix cycles
- `issues_resolved`: Total issues fixed
- `issues_remaining`: Issues not resolved
- `files_modified_count`: Files changed during fixes
- `build_duration_total`: Cumulative build time
- `fix_attempts_count`: Number of fix delegation calls

Display all statistics in final report.

## CRITICAL RULES

**Command Orchestration:**
- This command orchestrates maven-builder and fix commands
- Uses Task tool to invoke maven-builder (agent)
- Uses SlashCommand to invoke /cui-orchestrate-java-task (command)
- Commands CAN invoke other commands (Rule 6 compliant)

**No Direct Fixes:**
- This command NEVER fixes code directly
- Always delegates to appropriate fix commands
- Analyzes and routes issues only
- Orchestration, not implementation

**Iteration Logic:**
- Max 5 iterations to prevent infinite loops
- Each iteration: build → analyze → fix → verify
- Stop when clean OR max iterations reached
- Report partial success if issues remain

**Commit Strategy:**
- ONLY commit if build is CLEAN
- ONLY commit if push parameter is true
- If issues remain: do NOT commit (even with push=true)
- Preserve partial progress for inspection

**Error Resilience:**
- Continue fix attempts even if one category fails
- Track all failures for final report
- Allow user decisions (retry/skip/abort)
- Never rollback partial progress automatically

## USAGE EXAMPLES

**Basic build and fix:**
```
/cui-maven-build-and-fix
```

**Build, fix, and commit:**
```
/cui-maven-build-and-fix push
```

**Custom Maven goals:**
```
/cui-maven-build-and-fix goals="clean test -Pcoverage"
```

**Build, fix with custom goals, and commit:**
```
/cui-maven-build-and-fix goals="clean verify" push
```

## ARCHITECTURE

**Pattern**: Command Orchestrator (delegates to both agents and commands)

```
/cui-maven-build-and-fix (THIS COMMAND)
  ├─> Task(maven-builder) [agent: executes build, returns structured results]
  ├─> Analyze results and categorize issues
  ├─> SlashCommand(/cui-orchestrate-java-task) [command: delegates fixes]
  ├─> Task(maven-builder) [agent: verify fixes]
  ├─> Iterate until clean or max iterations
  └─> Task(commit-changes) [agent: commit if push=true and clean]
```

**Why This Works:**
- ✅ Commands can invoke agents (Task tool available)
- ✅ Commands can invoke other commands (SlashCommand available)
- ✅ No agent nesting (agents never call Task)
- ✅ maven-builder is focused (just builds, no fixes)
- ✅ /cui-orchestrate-java-task orchestrates Java fixes
- ✅ This command orchestrates the overall workflow

**Reference**: See architecture-rules.md Rule 6 (Agent Delegation Constraints)

## MIGRATION NOTES

**Renamed from /cui-build-and-verify:**
- Old name implied passive verification
- New name reflects active fix-and-iterate workflow
- Better describes what command actually does

**Removed maven-project-builder agent:**
- Old workflow: command → maven-project-builder → maven-builder (FAILED - agents can't delegate)
- New workflow: command → maven-builder + fix commands (SUCCESS - commands can orchestrate)
- Orchestration moved from agent to this command

**Related Migration:**
- commit 6e3e026: Removed maven-project-builder agent
- This commit: Implements new orchestration pattern

## RELATED

- `maven-builder` - Maven build execution agent (Layer 3)
- `/cui-orchestrate-java-task` - Java implementation orchestrator (Layer 1/2)
- `commit-changes` - Git commit utility agent
