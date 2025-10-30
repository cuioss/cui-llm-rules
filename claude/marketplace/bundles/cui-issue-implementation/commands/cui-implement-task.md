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

### Step 1: Get Issue (if not provided)

Prompt user for GitHub issue number or URL if not provided as parameter.

### Step 2: Review Issue with task-reviewer Agent

```
Task:
  subagent_type: task-reviewer
  description: Review issue for implementation
  prompt: Review issue {issue} for correctness, completeness, ambiguities
```

Handle results: SUCCESS (continue), PARTIAL (user choice), FAILURE (abort or retry).

### Step 3: Plan Implementation with task-breakdown-agent

```
Task:
  subagent_type: task-breakdown-agent
  description: Break down issue into tasks
  prompt: Analyze issue and create implementation plan with task breakdown
```

Store tasks list for iteration.

### Step 4: Verify Build with maven-project-builder

```
Task:
  subagent_type: maven-project-builder
  description: Verify project builds
  prompt: Run maven build and verify success
```

Handle build failures before proceeding.

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
