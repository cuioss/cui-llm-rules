---
name: cui-implement-task
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

### Step 4: Verify Build with maven-project-builder

```
Task:
  subagent_type: maven-project-builder
  description: Verify project builds
  prompt: Run maven build and verify success
```

Handle build failures before proceeding.

**Error handling:** If maven-project-builder agent fails to execute, increment agent_failures counter and prompt user "[R]etry/[A]bort".

### Step 5: Implement Tasks with task-executor

For each task in plan:
```
Task:
  subagent_type: task-executor
  description: Implement task {n}
  prompt: Implement task: {task_description}
```

Track: tasks_completed, tasks_failed, tasks_skipped.

### Step 6: Verify Completion

Check all tasks completed. Prompt for incomplete items.

### Step 7: Build Final Verification

Run maven-project-builder again to verify implementation builds successfully.

**Error handling:** If maven-project-builder agent fails during final verification, increment agent_failures counter and prompt user "[F]ix manually/[R]etry/[A]bort".

### Step 8: Commit and Push (if requested)

Use commit-changes agent if push parameter provided.

### Step 9: Display Summary

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

**Agent Coordination:**
- Wait for each agent to complete before next step
- Handle agent failures gracefully
- Provide clear status updates

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
/cui-implement-task
```

**With issue:**
```
/cui-implement-task issue=123
```

**Resume from task:**
```
/cui-implement-task issue=123 continueFrom=5
```

**Auto-push:**
```
/cui-implement-task issue=123 push
```

## ARCHITECTURE

Orchestrates specialized agents:
- task-reviewer - Issue validation
- task-breakdown-agent - Planning
- maven-project-builder - Build verification
- task-executor - Implementation
- commit-changes - Git operations

## RELATED

- Task-reviewer agent
- Task-breakdown-agent
- Task-executor agent
