---
name: implement-task
description: Verify, plan, and implement issues through end-to-end workflow with agent coordination
---

# Implement Issue - Full Issue Verification, Planning, and Implementation

Fully verify, plan, and implement a given issue through an end-to-end workflow involving issue review, planning, project verification, and sequential task implementation.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** with:
1. Better agent coordination patterns
2. More effective verification strategies
3. Improved task iteration logic
4. Better error recovery approaches
5. Enhanced user prompt patterns
6. Lessons learned about workflow optimization

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

### issue (Optional)
- **Format**: `issue=<path_or_github_issue>`
- **Description**: Path to local directory/file containing issue description, or GitHub issue reference
- **Examples**:
  - `issue=http-client-plan/` (directory)
  - `issue=http-client-plan/plan-http-client-extension.md` (file)
  - `issue=#123` (GitHub issue number)
  - `issue=https://github.com/owner/repo/issues/123` (GitHub URL)
- **Default**: If not provided, command will prompt user interactively

### continueFrom (Optional)
- **Format**: `continueFrom=<task_identifier>`
- **Description**: Jump directly to a specific task in an existing plan
- **Examples**:
  - `continueFrom="Task 5"` (by task number)
  - `continueFrom="Create HttpMethod Enum"` (by task name substring)
- **Default**: Start from first incomplete task
- **Use Case**: Resume implementation after interruption or skip completed tasks

### push (Optional)
- **Format**: `push`
- **Description**: Automatically commit and push changes after successful completion
- **Default**: Do not push (user must manually commit)
- **Note**: Only applies if all tasks complete successfully

## PARAMETER VALIDATION

### Validate issue Parameter

**If issue parameter provided:**
1. Check format:
   - If starts with `#` → GitHub issue number
   - If starts with `http://` or `https://` → GitHub issue URL
   - Otherwise → Treat as local path
2. Validate existence:
   - For local path: Use Read or Glob to verify file/directory exists
   - For GitHub issue: Use `gh issue view` to verify it exists
3. If validation fails:
   - Display error: "Invalid issue reference: {issue}"
   - Prompt user for correct reference
   - Continue with user-provided value

**If issue parameter NOT provided:**
- Proceed to Step 1 (will prompt user interactively)

### Validate continueFrom Parameter

**If continueFrom parameter provided:**
1. Value must be a non-empty string
2. Validation deferred until plan file is loaded (Step 3)
3. If task not found in plan:
   - Display error: "Task not found: {continueFrom}"
   - List available tasks from plan
   - Prompt user to select from list

**If continueFrom parameter NOT provided:**
- Start with first incomplete task (default behavior)

### Validate push Parameter

**If push parameter provided:**
- Simply note that push is enabled for final step
- No validation needed (flag parameter)

## WORKFLOW INSTRUCTIONS

### PRE-CONDITIONS

Before starting workflow, verify:
1. ✅ Git repository: Project is a git repository (check `.git/` exists)
2. ✅ GitHub CLI: `gh` command available if GitHub issue references used
3. ✅ Agent files: Required agents exist:
   - `../../agents/task-reviewer/AGENT.md`
   - `../../agents/task-breakdown-agent/AGENT.md`
   - `../../agents/task-executor/AGENT.md`
   - Agent from cui-project-quality-gates bundle: maven-project-builder
4. ✅ Clean state: No merge conflicts or unrecoverable git state

**Failure Handling**:
- If git not initialized: ERROR - "This command requires a git repository"
- If `gh` missing and GitHub issue used: ERROR - "Install GitHub CLI: brew install gh"
- If required agent missing: ERROR - "Missing agent: {name}. Run /create-agent to create it."
- If merge conflicts exist: ERROR - "Resolve merge conflicts before running this command"

### Step 1: Obtain Issue Reference

**Objective**: Ensure we have a valid issue reference to work with.

**Actions**:

1. Check if `issue` parameter was provided:
   - **YES** → Use provided value, skip to Step 2
   - **NO** → Continue with user prompt

2. Prompt user for issue reference:
   ```
   No issue reference provided.

   Please provide one of the following:
   1. Path to directory containing issue documentation
   2. Path to specific issue file (.md, .adoc)
   3. GitHub issue number (e.g., #123)
   4. GitHub issue URL

   Issue reference:
   ```

3. Store user input as `issue_reference`

4. Validate the provided reference (see PARAMETER VALIDATION above)

**Tools**: AskUserQuestion (if issue not provided), Read, Bash

**Success Criteria**: Valid issue reference obtained and verified

**Failure Handling**: If validation fails 3 times, exit with error

---

### Step 2: Review Issue with task-reviewer Agent

**Objective**: Ensure issue is ready for implementation (correct, complete, unambiguous).

**Actions**:

1. Display to user:
   ```
   ╔════════════════════════════════════════════════════════╗
   ║  Phase 1: Issue Review                                 ║
   ╚════════════════════════════════════════════════════════╝

   Reviewing issue for implementation readiness...
   ```

2. Invoke task-reviewer agent using Task tool:
   - **Subagent Type**: task-reviewer
   - **Prompt**: "Review issue at {issue_reference} for implementation readiness. Ensure correctness, completeness, and lack of ambiguities."
   - **Wait**: For agent completion

3. Parse task-reviewer response:
   - Extract Status: SUCCESS, FAILURE, or PARTIAL
   - Extract Issues Found: Count of problems identified
   - Extract Quality Assessment: Pass/fail for each criterion

4. **Decision Point - Review Results**:

   **If Status = SUCCESS AND all quality criteria pass:**
   - Display: "✅ Issue review complete - ready for planning"
   - Proceed to Step 3

   **If Status = PARTIAL OR high/critical findings exist:**
   - Display task-reviewer findings to user
   - Ask user:
     ```
     Issue review found {count} issues requiring attention.

     High/Critical Issues:
     {list of high/critical issues}

     Options:
     1. Re-run review (agent will attempt fixes)
     2. Continue anyway (risky - may cause implementation problems)
     3. Abort (fix issues manually)

     Choice [1/2/3]:
     ```
   - If 1: Return to beginning of Step 2 (re-invoke task-reviewer)
   - If 2: Display warning and proceed to Step 3
   - If 3: Exit command with message "Please fix issues and re-run /implement-task"

   **If Status = FAILURE:**
   - Display: "❌ Issue review failed: {error message}"
   - Exit command with error

5. **Loop Limit**: Maximum 3 review iterations
   - If 3 iterations reached without SUCCESS:
     - Display: "⚠️ Unable to achieve issue review success after 3 attempts"
     - Ask user: "Continue anyway? [y/N]:"
     - If N or no response: Exit command
     - If y: Proceed to Step 3 with warning

**Tools**: Task (task-reviewer agent), AskUserQuestion

**Success Criteria**: Issue review complete with acceptable quality OR user explicitly approved continuation

**Failure Handling**: Exit on FAILURE status or user abort

---

### Step 3: Generate Implementation Plan with task-breakdown-agent Agent

**Objective**: Create detailed task plan for implementing the issue.

**Actions**:

1. Display to user:
   ```
   ╔════════════════════════════════════════════════════════╗
   ║  Phase 2: Implementation Planning                      ║
   ╚════════════════════════════════════════════════════════╝

   Generating implementation plan...
   ```

2. Invoke task-breakdown-agent agent using Task tool:
   - **Subagent Type**: task-breakdown-agent
   - **Prompt**: "Create implementation plan for issue at {issue_reference}. Generate structured task list with checklists and acceptance criteria."
   - **Wait**: For agent completion

3. Parse task-breakdown-agent response:
   - Extract Plan File Path: Where the plan was created
   - Extract Task Count: Total number of tasks in plan
   - Extract Status: SUCCESS or FAILURE

4. **Decision Point - Planning Results**:

   **If Status = SUCCESS:**
   - Store `plan_file_path` for use in later steps
   - Display: "✅ Implementation plan created: {plan_file_path}"
   - Display: "📋 Total tasks: {task_count}"
   - Proceed to Step 4

   **If Status = FAILURE:**
   - Display: "❌ Plan generation failed: {error message}"
   - Ask user:
     ```
     Planning failed. Options:
     1. Retry planning
     2. Provide existing plan file manually
     3. Abort

     Choice [1/2/3]:
     ```
   - If 1: Return to beginning of Step 3
   - If 2: Prompt for plan file path, validate, store as `plan_file_path`, proceed to Step 4
   - If 3: Exit command

5. Read the generated plan file using Read tool:
   - Parse task structure
   - Count total tasks
   - Identify first incomplete task
   - Store task list in memory for iteration

**Tools**: Task (task-breakdown-agent agent), Read, AskUserQuestion

**Success Criteria**: Valid implementation plan created and loaded

**Failure Handling**: Retry once, then allow manual plan or abort

---

### Step 4: Verify Project Build Status

**Objective**: Ensure project is in good shape before implementation begins.

**Actions**:

1. Display to user:
   ```
   ╔════════════════════════════════════════════════════════╗
   ║  Phase 3: Project Verification                         ║
   ╚════════════════════════════════════════════════════════╝

   Verifying project build and tests...
   ```

2. Invoke maven-project-builder agent using Task tool:
   - **Subagent Type**: maven-project-builder
   - **Prompt**: "Verify project build with tests. Ensure clean baseline before implementation."
   - **Wait**: For agent completion

3. Parse maven-project-builder response:
   - Extract Status: SUCCESS, FAILURE, or PARTIAL
   - Extract Build Result: Passing or failing
   - Extract Test Result: Pass count and fail count
   - Extract Issues Found: Compilation errors, test failures, warnings

4. **Decision Point - Build Verification**:

   **If Status = SUCCESS AND build passing AND tests passing:**
   - Display: "✅ Project verification complete - ready for implementation"
   - Proceed to Step 5

   **If Status = FAILURE OR build failing OR test failures exist:**
   - Display maven-project-builder findings
   - Display:
     ```
     ❌ Project verification failed:
     - Build: {PASS/FAIL}
     - Tests: {pass_count} passed, {fail_count} failed
     - Issues: {issue_count}

     Cannot proceed with implementation on failing build.

     Options:
     1. Retry verification (in case of transient failure)
     2. Abort and fix issues manually

     Choice [1/2]:
     ```
   - If 1: Return to beginning of Step 4 (max 2 retries)
   - If 2: Exit command with message "Fix build issues and re-run /implement-task"

   **If Status = PARTIAL (warnings but passing):**
   - Display warnings
   - Ask user: "Warnings found but build passing. Continue? [Y/n]:"
   - If Y or no response: Proceed to Step 5
   - If n: Exit command

**Tools**: Task (maven-project-builder agent), AskUserQuestion

**Success Criteria**: Clean build achieved OR user approves continuation with warnings

**Failure Handling**: Exit on failing build, retry on transient failures

**CRITICAL**: NEVER proceed to implementation (Step 5) with a failing build

---

### Step 5: Determine Starting Task

**Objective**: Identify which task to start implementing (first incomplete or user-specified).

**Actions**:

1. Check if `continueFrom` parameter was provided:

   **If continueFrom PROVIDED:**
   - Search plan for matching task:
     - Try exact match on task number (e.g., "Task 5")
     - Try substring match on task name (e.g., "HttpMethod" matches "Create HttpMethod Enum")
   - If found: Set `current_task` to matched task
   - If not found:
     ```
     Task not found: {continueFrom}

     Available tasks:
     {list all tasks from plan with numbers and names}

     Which task should I start with? (enter number or name):
     ```
     - Store user response and find matching task

   **If continueFrom NOT PROVIDED:**
   - Scan plan for first incomplete task (has `[ ]` items)
   - Set `current_task` to first incomplete task
   - If ALL tasks complete:
     - Display: "✅ All tasks already complete!"
     - Skip to POST-CONDITIONS verification
     - Exit with success

2. Display to user:
   ```
   ╔════════════════════════════════════════════════════════╗
   ║  Phase 4: Sequential Task Implementation               ║
   ╚════════════════════════════════════════════════════════╝

   Starting with: Task {N}: {Task Name}
   Total remaining tasks: {count}
   ```

3. Initialize task iteration state:
   - `tasks_completed`: 0
   - `tasks_failed`: 0
   - `tasks_skipped`: 0
   - `current_task_index`: Index of current_task in plan

**Tools**: Read (to scan plan), AskUserQuestion (if task not found)

**Success Criteria**: Valid starting task identified

**Failure Handling**: If no tasks to implement, skip to success

---

### Step 6: Implement Current Task with task-executor Agent

**⚠️ LOOP START POINT** - Return here for each task in the plan

**Objective**: Implement ONE task from the plan using task-executor agent.

**Actions**:

1. Display task header:
   ```
   ──────────────────────────────────────────────────────────
   Implementing Task {N}/{total}: {Task Name}
   ──────────────────────────────────────────────────────────
   ```

2. Invoke task-executor agent using Task tool:
   - **Subagent Type**: task-executor
   - **Prompt**: "Implement Task {N} from plan at {plan_file_path}. Execute all checklist items sequentially and mark each as done."
   - **Parameters**:
     - taskPlanPath: {plan_file_path}
     - taskIdentifier: "Task {N}" (use task number for precision)
   - **Wait**: For agent completion (this may take significant time)

3. Parse task-executor response:
   - Extract Status: SUCCESS, FAILURE, or PARTIAL
   - Extract Checklist Items Completed: count/total
   - Extract Acceptance Criteria Met: Which criteria passed
   - Extract Build Status: Passing or failing
   - Extract Files Created: List of new files
   - Extract Files Modified: List of changed files

4. **Decision Point - Task Implementation Result**:

   **If Status = SUCCESS AND all checklist items [x] AND all acceptance criteria met:**
   - Display: "✅ Task {N} complete"
   - Increment `tasks_completed`
   - Proceed to Step 7

   **If Status = PARTIAL OR some checklist items incomplete:**
   - Display task-executor findings
   - Display:
     ```
     ⚠️ Task {N} partially complete:
     - Checklist: {completed}/{total} items done
     - Acceptance Criteria: {met}/{total} met
     - Build: {PASS/FAIL}

     Incomplete Items:
     {list unchecked items}

     Unmet Criteria:
     {list failed criteria}

     Options:
     1. Retry task (agent will attempt to complete remaining items)
     2. Skip task (risky - may affect subsequent tasks)
     3. Abort implementation

     Choice [1/2/3]:
     ```
   - If 1: Return to beginning of Step 6 for same task (max 3 retries per task)
   - If 2: Increment `tasks_skipped`, display warning, proceed to Step 7
   - If 3: Exit command with summary of progress

   **If Status = FAILURE:**
   - Display: "❌ Task {N} failed: {error message}"
   - Ask user:
     ```
     Task implementation failed. Options:
     1. Retry task
     2. Skip task
     3. Abort implementation

     Choice [1/2/3]:
     ```
   - If 1: Return to beginning of Step 6 for same task (max 3 retries)
   - If 2: Increment `tasks_failed`, proceed to Step 7
   - If 3: Exit command with summary

5. **Retry Limit Handling**:
   - If 3 retries exhausted for current task:
     - Display: "⚠️ Maximum retries reached for Task {N}"
     - Force user decision: Skip or Abort (no retry option)

**Tools**: Task (task-executor agent), AskUserQuestion

**Success Criteria**: Task successfully implemented OR user approved skip

**Failure Handling**: Retry up to 3 times, then force skip or abort decision

---

### Step 7: Verify Task Completion and Update Plan

**Objective**: Confirm task implementation is complete and update plan tracking.

**Actions**:

1. Re-read plan file using Read tool at `plan_file_path`

2. Verify current task status:
   - Check all checklist items for current task are `[x]`
   - Count incomplete items (should be 0)

3. **Verification Decision**:

   **If all items [x]:**
   - Display: "✅ Verified: Task {N} all items marked done"
   - Continue to next task determination

   **If some items NOT [x]:**
   - Display:
     ```
     ⚠️ WARNING: Task {N} has {count} incomplete items despite SUCCESS status

     This suggests task-executor did not mark all items as done.

     Incomplete items:
     {list items still [ ]}

     Options:
     1. Manually mark items as done (I'll update the plan)
     2. Return to task implementation
     3. Continue anyway

     Choice [1/2/3]:
     ```
   - If 1: Use Edit tool to mark all items `[x]`, then continue
   - If 2: Return to Step 6 for same task
   - If 3: Display warning and continue

4. Determine next task:
   - Find next task in plan after `current_task_index`
   - If next task found:
     - Set `current_task` to next task
     - Increment `current_task_index`
     - **LOOP BACK to Step 6** for next task
   - If NO more tasks:
     - Display: "✅ All tasks in plan completed"
     - Proceed to Step 8 (Final Summary)

**Tools**: Read, Edit (if manual marking needed), AskUserQuestion

**Success Criteria**: Task verified complete, next task determined OR all tasks done

**Loop Condition**: Continue Step 6 → Step 7 loop until all tasks complete

---

### Step 8: Final Summary and Push (if enabled)

**Objective**: Provide comprehensive implementation summary and optionally push changes.

**Actions**:

1. Display comprehensive summary:
   ```
   ╔════════════════════════════════════════════════════════╗
   ║  Implementation Complete                               ║
   ╚════════════════════════════════════════════════════════╝

   Issue: {issue_reference}
   Plan: {plan_file_path}

   Task Summary:
   - Total tasks: {total}
   - Completed: {tasks_completed} ✅
   - Failed: {tasks_failed} ❌
   - Skipped: {tasks_skipped} ⚠️

   Overall Status: {✅ SUCCESS if all completed, ⚠️ PARTIAL if skipped/failed exist}

   Files Changed:
   {aggregated list of all files created/modified across all tasks}

   {if push parameter enabled:}
   Preparing to commit and push changes...
   {end if}
   ```

2. **If push parameter enabled:**

   a. Invoke commit-changes agent to commit and push:
      - **Subagent Type**: commit-changes
      - **Prompt**: "Commit all changes from issue implementation: {issue_reference}, and push"
      - Wait for completion

   b. Display agent's final report showing commit and push status:
      - If SUCCESS: Display "✅ Changes committed and pushed"
      - If FAILURE: Display "❌ Commit/push failed: {error from agent report}"

3. **If push parameter NOT enabled:**
   - Display:
     ```
     Changes not committed. To commit and push:
     1. Review changes: git status
     2. Commit: git add . && git commit -m "Implement {issue_reference}"
     3. Push: git push
     ```

**Tools**: Task (commit-changes agent), Read

**Success Criteria**: Summary displayed, push completed (if enabled)

**Failure Handling**: Report commit/push failures but don't abort (implementation is done)

---

### POST-CONDITIONS

After workflow completion, verify:

1. ✅ **All tasks implemented**: tasks_completed = total_tasks (or user approved skips)
2. ✅ **Plan file updated**: All checklist items marked `[x]`
3. ✅ **Build passing**: Final project state has clean build (verify with maven-project-builder if time allows)
4. ✅ **Changes tracked**: All file modifications recorded in git (staged or committed)
5. ✅ **Documentation updated**: If issue included docs, they are updated
6. ✅ **No orphaned work**: No partially implemented tasks left in ambiguous state

**Verification Actions**:
- Read plan file final state: Confirm all items checked
- Run `git status`: Show working tree state
- Optionally: Quick maven-project-builder run to verify final state

**Post-Condition Failures**:
- If tasks skipped: Display warning about incomplete implementation
- If build broken: ERROR - "Implementation broke the build. Manual fix required."
- If plan not fully updated: Display warning and offer to fix

## CRITICAL RULES

**Agent Coordination**:
- **NEVER run agents in parallel** - Always sequential: review → plan → verify → implement tasks one by one
- **ALWAYS wait for agent completion** - Do not proceed to next step until current agent finishes
- **NEVER skip verification** - Build must pass before implementation starts

**Task Implementation**:
- **ONE task at a time** - task-executor implements exactly one task per invocation
- **SEQUENTIAL execution** - Tasks must be implemented in order (cannot parallelize)
- **VERIFY after each task** - Re-read plan to confirm items marked done

**Error Handling**:
- **BUILD FAILURES BLOCK PROGRESS** - Never proceed to implementation with failing build
- **RETRY LIMITS** - Maximum 3 retries per task, 3 retries per review iteration
- **USER DECISIONS** - On ambiguous failures, always ask user (skip vs retry vs abort)

**State Management**:
- **TRACK PROGRESS** - Maintain counts: tasks_completed, tasks_failed, tasks_skipped
- **PRESERVE PLAN** - Plan file is source of truth, keep it updated
- **NO CONCURRENT MODIFICATION** - Only one agent modifies plan at a time

**Tool Coverage**:
- Read: Load issue, plan, verify task status
- Edit: Fix plan if items not marked (rare)
- Write: (Not used - agents create files)
- Bash: Git operations (status, push)
- Task: Invoke all agents (task-reviewer, task-breakdown-agent, task-executor, maven-project-builder, commit-changes)

## USAGE EXAMPLES

### Example 1: Implement from local directory
```
/implement-task issue=http-client-plan/
```
Reads issue from directory, reviews, plans, implements all tasks.

### Example 2: Implement GitHub issue
```
/implement-task issue=#123
```
Loads GitHub issue #123, reviews, plans, implements.

### Example 3: Continue from specific task
```
/implement-task issue=http-client-plan/ continueFrom="Task 5"
```
Skips to Task 5 in existing plan, implements remaining tasks.

### Example 4: Full implementation with auto-push
```
/implement-task issue=#123 push
```
Complete workflow, commits and pushes changes at end.

### Example 5: Resume interrupted implementation
```
/implement-task continueFrom="Create HttpMethod Enum"
```
No issue needed (plan already exists), finds task by name, continues.

## IMPORTANT NOTES

**Performance Expectations**:
- This command orchestrates multiple agents and can take 1-3 hours for complex issues
- Each task implementation may take 10-30 minutes depending on complexity
- User should monitor progress but doesn't need to interact unless errors occur

**Interruption Handling**:
- If command is interrupted (Ctrl+C, timeout, crash):
  - Progress is saved in plan file (completed tasks marked `[x]`)
  - Use `continueFrom` parameter to resume
  - Example: `/implement-task continueFrom="Task 8"`

**Agent Dependencies**:
- Requires task-reviewer, task-breakdown-agent, task-executor, maven-project-builder agents
- If agents missing, command will fail in PRE-CONDITIONS
- Use `/create-agent` to create missing agents

**Plan File Location**:
- task-breakdown-agent agent creates plan in issue directory or project root
- Plan file name: typically `plan-{issue-name}.md`
- Plan file is preserved for resumption and audit trail

**Build Verification**:
- Step 4 verifies build BEFORE implementation
- Each task's build verification is handled by task-executor
- Final build state should be verified manually if concerned

**Conflict Resolution**:
- If git conflicts arise during implementation, command will pause
- Resolve conflicts manually, then re-run with `continueFrom`
- task-executor agent may detect conflicts and report them
