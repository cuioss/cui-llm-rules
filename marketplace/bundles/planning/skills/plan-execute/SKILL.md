---
name: plan-execute
description: Execute phase skill for plan management. DUMB TASK RUNNER that executes tasks from TASK-*.toon files sequentially for execute and finalize phases.
allowed-tools: Read, Write, Edit, Bash, Skill, Task, AskUserQuestion
---

# Plan Execute Skill

**Role**: DUMB TASK RUNNER that executes tasks from TASK-*.toon files sequentially.

**Execution Pattern**: Locate current task → Execute steps → Mark progress → Next task

**Phases Handled**: execute, finalize

**CRITICAL**: Use `update-progress.py` via Bash for plan file updates (Edit/Write tools trigger permission prompts on `.plan/` directories).

## Standards (Load On-Demand)

### Workflow
```
Read standards/workflow.md
```
Contains: Task execution pattern, phase transition, auto-continue behavior

### Operations
```
Read standards/operations.md
```
Contains: Delegation patterns for builds, quality checks, PR creation

### Finalize Configuration (from plan-type skill)

For finalize phase, query the plan-type skill for commit/PR behavior:

```
Skill: planning:manage-config
operation: get
plan_id: {plan_id}
field: plan_type

Skill: planning:plan-type-{plan_type}
operation: get-finalize-config
plan_id: {plan_id}
```

Returns: `commit_strategy`, `create_pr`, `verification_required`, `verification_command`

---

## Execution Loop

For each task in current phase:

### Step 1: Locate Task

```
Skill: planning:manage-tasks
operation: next
plan_id: {plan_id}
```

Returns next task with status `pending` or `in_progress`.

### Step 2: Execute Steps

For each step in task's `steps[]` array:
1. Parse the step text
2. Execute the action (delegate if specified)
3. Mark step complete via `manage-tasks:step-done`

### Step 3: Update Progress

Script: `planning:plan-execute/scripts/update-progress.py`

```bash
python3 {script_path} --plan-dir {plan_directory} --phase {phase} --task-id {task_id} --complete-items "{item_text}"
```

### Step 4: Next Task or Phase

- If more tasks in phase → Continue to next task
- If phase complete → Auto-transition to next phase
- If all phases complete → Mark plan complete

---

## Delegation

When checklist items specify delegation, invoke the appropriate agent/skill:

| Checklist Pattern | Delegation |
|-------------------|------------|
| "Run build" / "maven" / "npm" | See `standards/operations.md` |
| "Delegate to {agent}" | `Task: {agent}` |
| "Load skill: {skill}" | `Skill: {skill}` |
| "Run /command" | `SlashCommand: /command` |

---

## Auto-Continue Behavior

Execute continuously without user prompts except:
- Error blocks progress
- Decision genuinely required
- User explicitly requested confirmation

**Do NOT prompt for**:
- Phase transitions
- Task transitions
- Routine confirmations

---

## Phase Transition

When transitioning from execute phase to finalize, `transition-phase.py` automatically:
- Runs `collect-modified-files.py` to capture changes
- Updates `references.toon` with collected files

---

## Error Handling

### Script Failure (Lessons-Learned Capture)

**ON SCRIPT FAILURE**: When any script execution fails (exit != 0):
1. Capture error context (script path, exit code, stderr)
2. Follow `general-tools:script-runner` Error Handling workflow
3. Continue with normal error recovery (retry, fail task, etc.)

### Other Errors

| Error | Options |
|-------|---------|
| Build failure | Fix and retry / View log / Skip task |
| Test failure | Fix tests / View details / Skip task |
| Dependency not met | Complete dependency / Skip check |

---

## Integration

### Command Integration
- **/plan-execute** - Primary command invoking this skill

### Skills Used
- **manage-config** - Configuration CRUD
- **manage-lifecycle** - Phase transitions
- **manage-tasks** - Task and step operations
- **manage-references** - Reference file CRUD
- **manage-log** - Work log entries
- **plan-type-simple** - Finalize config for simple plans
- **plan-type-plugin** - Finalize config for plugin plans
- **plan-type-java** - Finalize config for Java plans
- **plan-type-javascript** - Finalize config for JavaScript plans
- **git-workflow** - Commit operations

### Related Skills
- **plan-init** - Creates plan structure
- **plan-refine** - Generates implementation tasks

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to manage-* skills
- [x] DUMB TASK RUNNER pattern
- [x] Handles execute and finalize phases
