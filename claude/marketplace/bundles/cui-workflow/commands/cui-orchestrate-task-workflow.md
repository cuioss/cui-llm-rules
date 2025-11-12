---
name: cui-orchestrate-task-workflow
description: Verify, plan, and implement issues through end-to-end workflow with agent coordination
---

# Implement Task Command

End-to-end issue implementation workflow coordinating multiple specialized agents for review, planning, building, and implementation.

## PARAMETERS

**issue** - GitHub issue number or URL (optional, prompts if not provided)

**continueFrom** - Resume from specific task number (optional)

**push** - Auto-push after successful implementation (optional flag)

## WORKFLOW

### Step 1: Validate and Get Issue

**Parameter validation:**
1. If `issue` parameter provided:
   - Validate format: must be number (e.g., `123`) or GitHub URL (e.g., `https://github.com/org/repo/issues/123`)
   - Extract issue number from URL if needed
   - If invalid format: Display error "Invalid issue format. Provide issue number or GitHub URL" and abort
2. If `issue` not provided: Prompt user for GitHub issue number or URL
3. If `continueFrom` parameter provided:
   - Store for later use (will validate bounds after plan is created in Step 3)

**Error handling:** If issue cannot be determined or is invalid, abort with clear error message.

### Step 2: Review Issue with task-reviewer Agent

```
Task:
  subagent_type: task-reviewer
  description: Review issue for implementation
  prompt: Review issue {issue} for correctness, completeness, ambiguities
```

**Handle results:**
- SUCCESS: Continue to Step 3
- PARTIAL: Prompt user "[C]ontinue/[R]etry review/[A]bort" - increment retry_attempts if retry chosen
- FAILURE: Prompt user "[R]etry review/[A]bort" - increment retry_attempts if retry chosen

**Error handling:** If task-reviewer agent fails to execute, increment agent_failures counter and prompt user "[R]etry/[A]bort".

### Step 3: Plan Implementation with task-breakdown-agent

```
Task:
  subagent_type: task-breakdown-agent
  description: Break down issue into tasks
  prompt: Analyze issue and create implementation plan with task breakdown
```

**Store tasks list for iteration.**

**Validate continueFrom parameter:**
- If `continueFrom` was provided in Step 1:
  - Verify `continueFrom` is <= total_tasks
  - If out of bounds: Display error "continueFrom={continueFrom} exceeds total tasks ({total_tasks})" and abort
  - If valid: Set starting task index to continueFrom

**Error handling:** If task-breakdown-agent fails to execute, increment agent_failures counter and prompt user "[R]etry/[A]bort".

### Step 4: Verify Build

```
SlashCommand: /cui-maven-build-and-fix
```

Self-contained command that runs build, fixes issues if found, verifies, and commits fixes.

**Error handling:** If command fails, increment build_failures counter and prompt user "[R]etry/[A]bort".

### Step 5: Implement Tasks

**Pattern Decision: Determine if atomic or batch:**
- If plan has 1 task (atomic): Use task-executor directly + verify
- If plan has multiple tasks (batch): Delegate to /cui-execute-single-task for each

**For atomic (single task):**
```
Task:
  subagent_type: task-executor
  description: Implement task
  prompt: Implement task: {task_description}
```

Then verify with SlashCommand(/cui-maven-build-and-fix).

**For batch (multiple tasks):**
```
For each task in plan:
  SlashCommand: /cui-execute-single-task task="{task_description}"
```

Each /cui-execute-single-task is self-contained (implements + verifies + iterates).

Track: tasks_completed, tasks_failed, tasks_skipped.

### Step 6: Verify Completion

Check all tasks completed. Prompt for incomplete items.

### Step 7: Final Verification and Commit

```
SlashCommand: /cui-maven-build-and-fix push={push parameter}
```

Self-contained command: runs build, fixes issues if found, verifies, commits all changes, and pushes if push=true.

**Error handling:** If command fails during final verification, increment build_failures counter and prompt user "[F]ix manually/[R]etry/[A]bort".

### Step 8: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║          Implementation Summary                            ║
╚════════════════════════════════════════════════════════════╝

Issue: #{issue}
Tasks completed: {count}/{total}
Build status: {SUCCESS/FAILURE}
Committed: {yes/no}
Pushed: {yes/no}
```

## STATISTICS TRACKING

Track throughout workflow:
- `agent_failures`: Count of agent execution failures
- `retry_attempts`: Count of user-initiated retries
- `build_time_ms`: Time taken for build operations
- `tasks_completed`: Successful task implementations
- `tasks_failed`: Failed task implementations
- `tasks_skipped`: Skipped tasks

Display all statistics in final summary.

## CRITICAL RULES

**Command Orchestration:**
- Delegate to self-contained commands for build/verify/commit operations
- Pattern Decision: atomic tasks use task-executor + verify, batch uses /cui-execute-single-task per task
- Wait for each operation to complete before next step
- Handle failures gracefully

**User Interaction:**
- Prompt on PARTIAL results
- Allow user to skip/retry/abort
- Clear decision points

**Quality Gates:**
- Must pass build before implementing
- Must pass build after implementing
- Review issue before planning

**Statistics:**
- Track all task outcomes
- Display comprehensive summary
- Report agent execution results

## USAGE EXAMPLES

**Interactive mode:**
```
/cui-orchestrate-task-workflow
```

**With issue:**
```
/cui-orchestrate-task-workflow issue=123
```

**Resume from task:**
```
/cui-orchestrate-task-workflow issue=123 continueFrom=5
```

**Auto-push:**
```
/cui-orchestrate-task-workflow issue=123 push
```

## ARCHITECTURE

Orchestrates agents and commands:
- task-reviewer agent - Issue validation
- task-breakdown-agent - Planning
- task-executor agent - Focused implementation (for atomic tasks)
- `/cui-execute-single-task` command - Self-contained (for batch tasks)
- `/cui-maven-build-and-fix` command - Build + verify + fix + commit

## RELATED

- task-reviewer agent
- task-breakdown-agent
- task-executor agent
- `/cui-execute-single-task` command (self-contained)
- `/cui-maven-build-and-fix` command

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL: Every time you execute this command and discover a more precise, better, or more efficient approach, YOU MUST immediately update this file** using /cui-update-command command-name=cui-orchestrate-task-workflow update="[your improvement]"

**Areas for continuous improvement:**
1. Agent coordination patterns and retry strategies
2. Error recovery and failure handling optimization
3. Task breakdown quality and granularity improvements
4. Build verification efficiency and integration
5. User interaction patterns and decision prompts
