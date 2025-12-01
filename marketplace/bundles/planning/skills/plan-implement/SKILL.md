---
name: plan-implement
description: Implement phase skill for plan management. Executes tasks sequentially, delegates to language-specific agents (Java/JavaScript), tracks checklist completion, verifies acceptance criteria, and handles commits per strategy.
allowed-tools: Read, Write, Edit, Bash, Skill, Task, AskUserQuestion
---

# Plan Implement Skill

**EXECUTION MODE**: Execute implementation tasks immediately. Do not explain or summarize.

**OUTPUT RULES**:
- Do NOT narrate internal process or tool invocations
- Do NOT display raw script output - format as structured status
- DO show task progress and completion status
- Work silently until you have results to display

**MANDATORY PROGRESS TRACKING**:

After EVERY checklist item completion, you MUST call update-progress:
```
python3 {update-progress.py} --plan-dir {plan_directory} --phase {phase} --task-id {task_id} --complete-items "{item_text}"
```

**NEVER skip this step** - even for pre-implemented work. The plan.md is the source of truth. Phase transitions WILL FAIL with `incomplete_phase` error if checklist items are not marked as `[x]`.

**Anti-Patterns** (DO NOT DO):
- Using TodoWrite instead of update-progress
- Completing multiple items without updating progress
- Assuming pre-implemented work doesn't need progress updates
- Marking task complete without marking all checklist items first

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
Skill: planning:plan-files
operation: read-plan, read-config, get-references
```

Also: `Read {plan_directory}/implementation-requirements.md`

### Step 2: Identify Target Task

**Selection Logic**:
1. If task_id specified → Find that task
2. If in_progress task exists → Auto-resume (no user prompt)
3. Else → First pending task respecting dependencies

**Dependency Check**: All dependencies must be `completed`

**Note**: Do not prompt for task selection. Auto-select and auto-resume. Only prompt if a genuine decision is needed (e.g., dependency conflict).

### Step 3: Load Task References

Read all references for the task. If unclear, use AskUserQuestion for clarification.

### Step 3b: Check for Pre-Implemented Work

**CRITICAL**: Before executing, check if task deliverables already exist.

**Detection**:
- Check if referenced files/components exist
- Verify they meet acceptance criteria
- Compare expected vs actual state

**If pre-implemented** (deliverables exist and meet criteria):
1. Verify each acceptance criterion is satisfied
2. **STILL call update-progress** for each checklist item:
   ```
   Skill: planning:plan-files
   operation: update-progress
   phase: {phase}
   task_id: {task_id}
   complete_items: "{item1},{item2},..."
   ```
3. Skip to Step 7 (Update Progress for task completion)

**If not pre-implemented** (work needed):
- Continue to Step 4

**Important**: Even for pre-implemented tasks, progress MUST be updated. The plan.md is the source of truth for status - not the codebase.

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
Skill: planning:plan-files
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

**After agent completes**:
```
Skill: planning:work-log
operation: log-entry
plan_directory: {plan_directory}
phase: implement
task: {task_id}
action: "Implemented {task_name}"
result: "{created/modified files}"
```

### Step 6: Verify Acceptance Criteria

Present verification table. If criterion fails:
- AskUserQuestion: Continue implementing / Modify criterion / Mark partial / Skip task

### Step 7: Update Progress

```
Skill: planning:plan-files
operation: update-progress
task_id: {task_id}
status: completed
```

Update references with created files:
```
Skill: planning:plan-files
operation: write-references
action: add
reference_type: file
```

**Log task completion**:
```
Skill: planning:work-log
operation: log-entry
plan_directory: {plan_directory}
phase: implement
task: {task_id}
action: "Completed task {task_id}: {task_name}"
result: "Acceptance criteria met"
```

### Step 8: Commit (Based on Strategy)

| Strategy | Action |
|----------|--------|
| fine-granular | Commit after this task |
| phase-specific | Skip (commit after phase) |
| complete | Skip (commit in finalize) |

**For fine-granular**: Use `git-workflow` skill

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

1. **CRITICAL**: Update progress for ALL completed tasks:
   ```
   Skill: planning:plan-files
   operation: update-progress
   phase: implement
   task_id: {task_id}
   complete_items: "{all_checklist_items}"
   set_status: completed
   ```

   **Note**: This must be called for EVERY task, including pre-implemented ones. The plan.md Phase Progress table drives status detection in `discover-plans.py`.

2. **Auto-transition** to verify phase (no user prompt needed)
   - Plans execute continuously until complete or blocked
   - Do NOT ask user to confirm phase transition

**Only prompt user when**:
- An error blocks progress
- A decision is genuinely required (e.g., multiple valid approaches)
- User has explicitly requested confirmation points

**Anti-Pattern**: Using TodoWrite or manual tracking instead of update-progress. This leaves plan.md out of sync with actual progress.

---

## Integration

### Command Integration
- **/plan-execute** - Primary command invoking this skill via phase-management

### Skills Used
- **plan-files** - All file I/O operations
- **java-implement-agent** - Java implementation
- **npm-builder** - JavaScript implementation
- **git-workflow** - Commit operations
- **phase-management** - Orchestration (invokes this skill)
- **work-log** - Logging significant actions

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
