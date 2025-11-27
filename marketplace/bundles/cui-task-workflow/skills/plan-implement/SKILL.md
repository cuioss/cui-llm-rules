---
name: plan-implement
description: Implement phase skill for plan management. Executes tasks sequentially, delegates to language-specific agents (Java/JavaScript), tracks checklist completion, verifies acceptance criteria, and handles commits per strategy.
allowed-tools: Read, Write, Edit, Bash, Skill, Task, AskUserQuestion
---

# Plan Implement Skill

**EXECUTION MODE**: Execute implementation tasks immediately. Do not explain or summarize.

**Role**: Third phase skill in the plan management system. Executes tasks from the refine phase, delegating to appropriate language agents. Delegates all file I/O to `plan-files` skill.

## Standards (Load On-Demand)

### Workflow
```
Read standards/workflow.md
```
Contains: Phase overview, task patterns, agent delegation, progress tracking, commit strategy

---

## Operation: execute-tasks

**Input**: `plan_directory`, `task_id` (optional)

**Steps**:

### Step 1: Read Context

```
Skill: cui-task-workflow:plan-files
operation: read-plan, read-config, get-references
```

Also: `Read {plan_directory}/implementation-requirements.md`

### Step 2: Identify Target Task

**Selection Logic**:
1. If task_id specified → Find that task
2. If in_progress task exists → Resume (AskUserQuestion: Continue/Restart/Skip)
3. Else → First pending task respecting dependencies

**Dependency Check**: All dependencies must be `completed`

### Step 3: Load Task References

Read all references for the task. If unclear, use AskUserQuestion for clarification.

### Step 4: Execute Checklist Items

For each item:

| Type | Action | Tool |
|------|--------|------|
| implement | Write/Edit code | Edit, Write |
| test | Write/Edit tests | Edit, Write + Bash |
| document | Write/Edit docs | Edit, Write |
| verify | Run build/tests | Delegate to agent |
| commit | Git operations | Bash |

After each item:
```
Skill: cui-task-workflow:plan-files
operation: update-progress
checklist_items: [{item_index}]
```

### Step 5: Delegate to Language Agents

**For Java**:
```
Task:
  subagent_type: cui-java-expert:java-implement-agent
  prompt: Execute Task {N}: {name}, Goal: {goal}, Criteria: {list}
```

**For JavaScript**:
```
Task:
  subagent_type: builder:npm-builder
  prompt: Execute Task {N}: {name}, Goal: {goal}, Criteria: {list}
```

### Step 6: Verify Acceptance Criteria

Present verification table. If criterion fails:
- AskUserQuestion: Continue implementing / Modify criterion / Mark partial / Skip task

### Step 7: Update Progress

```
Skill: cui-task-workflow:plan-files
operation: update-progress
task_id: {task_id}
status: completed
```

Update references with created files:
```
Skill: cui-task-workflow:plan-files
operation: write-references
action: add
reference_type: file
```

### Step 8: Commit (Based on Strategy)

| Strategy | Action |
|----------|--------|
| fine-granular | Commit after this task |
| phase-specific | Skip (commit after phase) |
| complete | Skip (commit in finalize) |

**For fine-granular**: Use `cui-git-workflow` skill

---

## Error Handling

### Build Failure
Options: Fix and retry / View log / Skip task / Abort phase

### Test Failure
Options: Fix tests / View details / Mark partial / Skip task

### Coverage Below Threshold
Options: Add tests / Accept current / Adjust target

### Dependency Not Met
Options: Complete dependency / Skip check / Choose different task

---

## Phase Transition

When all implement tasks complete:

AskUserQuestion:
- Proceed to verify phase
- Review implementation
- Add additional tasks

```
Skill: cui-task-workflow:plan-files
operation: update-progress
task_id: {last-task}
status: completed
```

---

## Integration

### Skills Used
- **plan-files** - All file I/O operations
- **java-implement-agent** - Java implementation
- **npm-builder** - JavaScript implementation
- **cui-git-workflow** - Commit operations

### Related Skills
- **plan-init** - Init phase
- **plan-refine** - Previous phase
- **plan-verify** - Next phase
- **plan-finalize** - Finalization phase

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to plan-files skill
- [x] Language agent delegation patterns
- [x] Task dependency checking
- [x] Commit strategy support
