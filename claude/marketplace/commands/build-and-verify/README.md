# build-and-verify

Executes comprehensive project verification workflow by orchestrating specialized agents to run Maven build, fix issues, and optionally commit/push changes.

## Purpose

Provides a simple command interface for complete project verification by delegating to:
- **maven-project-builder** agent: Runs Maven build with `-Ppre-commit clean install`, analyzes all output, fixes errors/warnings
- **commit-changes** agent: Commits and pushes changes following Git standards (optional)

## Usage

```bash
# Basic verification - run build and fix all issues
/build-and-verify

# Verification with auto-commit/push
/build-and-verify push
```

## What It Does

The command orchestrates a 4-step workflow:

1. **Parse Parameters** - Check if `push` parameter provided
2. **Invoke maven-project-builder** - Delegate to specialized agent for complete Maven verification
3. **Commit & Push** (optional) - Delegate to commit-changes agent if `push` parameter provided
4. **Display Summary** - Show consolidated report from all agents

## Key Features

- **Clean Delegation Pattern**: No duplication of verification or commit logic
- **Single Source of Truth**: maven-project-builder handles all build verification
- **Optional Push**: Controlled by `push` parameter
- **Comprehensive Reporting**: Consolidated summary from all agents
- **Failure Handling**: Stops on failure, displays error report
- **Time Tracking**: Updates .claude/run-configuration.md with execution duration

## Parameters

### push (Optional)
- **Format**: `push` (flag)
- **Description**: Automatically commits and pushes changes after successful verification
- **Usage**: `/build-and-verify push`
- **Default**: Changes remain uncommitted for manual review

## Workflow Detail

### Step 1: Parse Parameters

**Check User Intent:**
- Parse command arguments
- Store `push` flag as boolean for later use

### Step 2: Invoke maven-project-builder Agent

**Delegation:**
- Uses Task tool with `subagent_type: "maven-project-builder"`
- Provides clear prompt:
  ```
  Execute comprehensive project verification by running ./mvnw -Ppre-commit clean install.
  Analyze all output, fix all errors and warnings, and track execution time in .claude/run-configuration.md.
  ```

**Agent Responsibilities:**
- Read configuration from .claude/run-configuration.md
- Execute Maven build with proper timeout
- Analyze all errors, warnings, JavaDoc issues, OpenRewrite markers
- Fix all issues and repeat until clean
- Update execution duration if changed >10%

**Success Criteria:**
- Agent reports "✅ SUCCESS" status
- Build is completely clean

**Failure Handling:**
- If agent reports failure, display error report to user
- **STOP** - do not proceed to commit/push

### Step 3: Commit and Push (Optional)

**Decision Point:**
- If `push` parameter NOT provided → Skip to Step 4
- If `push` parameter provided → Continue

**Delegation:**
- Uses Task tool with `subagent_type: "commit-changes"`
- Provides clear prompt:
  ```
  Commit all changes from project verification and push to remote repository.
  Analyze the changes to create an appropriate commit message following Git Commit Standards.
  Include both code fixes and any .claude/run-configuration.md updates in the commit.
  After committing, push the changes to the remote repository.
  ```

**Agent Responsibilities:**
- Check for uncommitted changes
- Clean any build artifacts
- Create commit with proper Git Commit Standards format
- Push to remote repository
- Report commit hash and push status

**Success Criteria:**
- Agent reports "✅ SUCCESS"
- Commit created and pushed

**Failure Handling:**
- If agent reports failure, display error to user

### Step 4: Display Summary Report

**Consolidated Report:**
```
## /build-and-verify Complete

**Verification Status**: {status from maven-project-builder agent}
**Commit/Push Status**: {status from commit-changes agent, or "N/A - not requested"}

**Project Verification Summary**:
{Key metrics from maven-project-builder agent report}

{If push was performed:}
**Commit Details**:
{Key details from commit-changes agent report}
```

## Agent Delegation Benefits

### No Duplication
- **maven-project-builder**: Single source of truth for all verification logic
- **commit-changes**: Single source of truth for commit/push logic
- Other commands can reuse same agents

### Maintainability
- Updates to verification logic only in maven-project-builder agent
- Updates to commit logic only in commit-changes agent
- Changes automatically benefit all calling commands

### Reusability
- maven-project-builder can be invoked directly or from other commands
- commit-changes can be invoked directly or from other commands
- Consistent behavior regardless of invocation method

### Consistency
- All verification follows same standards
- All commits follow same format
- Predictable behavior across workflows

## Expected Duration

- **Basic Verification** (no push): 2-5 minutes
  - Maven build: 1-4 min (depends on project size)
  - Issue analysis and fixing: 30 sec - 1 min
  - Repeat cycles: variable (until clean)

- **Verification with Push**: +30-60 seconds
  - Change analysis: 10-20 sec
  - Commit creation: 10-20 sec
  - Push to remote: 10-20 sec

**Note**: First run may take longer if many issues found. Subsequent runs faster with fewer issues.

## Integration

Use this command:
- Before committing changes manually (sanity check)
- As part of pre-commit workflow
- In CI/CD pipelines for automated verification
- After significant code changes
- Before creating pull requests

Often used with:
- `/implement-task` - After implementing issue, verify project
- `/handle-pull-request` - After PR review changes, verify project
- Manual development workflows - Quick verification before commit

## Success Criteria

**maven-project-builder agent must report:**
- ✅ Maven build completed successfully
- ✅ Zero compilation errors
- ✅ Zero test failures
- ✅ Zero JavaDoc errors
- ✅ Zero OpenRewrite markers
- ✅ All quality gates passed

**commit-changes agent must report (if push provided):**
- ✅ Changes detected and analyzed
- ✅ Commit created with proper format
- ✅ Pushed to remote repository
- ✅ Commit hash provided

## Failure Scenarios

### Build Failure
**Symptom**: maven-project-builder reports errors/warnings that couldn't be fixed
**Outcome**: Command stops, displays error report, does NOT proceed to commit
**Resolution**: User must review errors and fix manually

### No Changes to Commit
**Symptom**: commit-changes reports no uncommitted changes
**Outcome**: Informational message, not treated as failure
**Resolution**: Normal scenario if build didn't modify files

### Push Failure
**Symptom**: commit-changes reports push failed (network, auth, etc.)
**Outcome**: Commit created locally but not pushed
**Resolution**: User can manually push or re-run with connectivity fixed

## Example Output

### Basic Verification (No Push)
```
Delegating to maven-project-builder agent...

[maven-project-builder agent output]
✅ SUCCESS: Project build completed successfully
- Build time: 2m 15s
- Issues fixed: 3 warnings
- Quality gates: All passed

## /build-and-verify Complete

**Verification Status**: ✅ SUCCESS
**Commit/Push Status**: N/A - not requested

**Project Verification Summary**:
- Build completed in 2m 15s
- Fixed 3 compilation warnings
- All tests passed (142 tests)
- All quality gates passed
```

### Verification with Push
```
Delegating to maven-project-builder agent...

[maven-project-builder agent output]
✅ SUCCESS: Project build completed successfully

Delegating to commit-changes agent...

[commit-changes agent output]
✅ SUCCESS: Changes committed and pushed
- Commit: abc1234
- Push status: Successful

## /build-and-verify Complete

**Verification Status**: ✅ SUCCESS
**Commit/Push Status**: ✅ SUCCESS

**Project Verification Summary**:
- Build completed in 2m 15s
- Fixed 3 compilation warnings
- All tests passed (142 tests)

**Commit Details**:
- Commit hash: abc1234
- Changes: 5 files modified
- Push: Successful to origin/main
```

## Notes

- **Delegation Only**: Command never implements verification or commit logic directly
- **Wait for Agents**: Always waits for agent completion before proceeding
- **Respect User Intent**: Only commits/pushes if explicitly requested via `push` parameter
- **Display Reports**: Always shows user what agents accomplished
- **Failure Safety**: Stops on failure, never commits broken code
- **Time Tracking**: Automatically updates .claude/run-configuration.md with execution duration
- **Artifact Cleanup**: commit-changes agent cleans build artifacts before committing

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
