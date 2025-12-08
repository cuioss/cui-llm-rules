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

---

## Scripts

| Script | Purpose |
|--------|---------|
| `planning:manage-config` | Config field access |
| `planning:manage-lifecycle` | Phase routing and transitions |
| `planning:manage-log` | Work log entries |
| `planning:manage-tasks` | Task management |
| `planning:manage-references` | Reference file CRUD |
| `planning:plan-execute` | Progress updates |

---

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

### Finalize Configuration (from config.toon)

For finalize phase, read finalize configuration directly from config.toon:

Script: `planning:manage-config`

```bash
python3 .plan/execute-script.py planning:manage-config:get-multi \
  --plan-id {plan_id} \
  --fields create_pr,verification_required,verification_command,branch_strategy
```

Returns only the required finalize fields in a single call: `create_pr`, `verification_required`, `verification_command`, `branch_strategy`.

These fields are written during init by the plan-type skill's `configure` operation.

---

## Execution Loop

### Step 0: Get Routing Context (Once at start)

Get current phase, skill routing, and progress in a single call:

Script: `planning:manage-lifecycle`

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:get-routing-context \
  --plan-id {plan_id}
```

Returns:
```toon
status: success
plan_id: {plan_id}
current_phase: execute
skill: planning:plan-execute
skill_description: Execute phase skill for task implementation
total_phases: 4
completed_phases: 2
phases:
- init: complete
- refine: complete
- execute: in_progress
- finalize: pending
```

Use `current_phase` for logging, `skill` for dynamic routing, and `completed_phases/total_phases` for progress display.

### Step 0.5: Log Phase Start (Once per phase)

At the start of execute or finalize phase:

Script: `planning:manage-log`

```bash
python3 .plan/execute-script.py planning:manage-log:add \
  --plan-id {plan_id} \
  --phase {phase} \
  --type progress \
  --summary "Starting {phase} phase"
```

For each task in current phase:

### Step 1: Locate Task with Context

Script: `planning:manage-tasks`

```bash
python3 .plan/execute-script.py planning:manage-tasks:next \
  --plan-id {plan_id} \
  --include-context
```

Returns next task with status `pending` or `in_progress`, including embedded specification context (title, body, requirements) for immediate use without additional script calls.

### Step 2: Execute Steps

For each step in task's `steps[]` array:
1. Parse the step text
2. Execute the action (delegate if specified)
3. Mark step complete via `manage-tasks:step-done`

### Step 3: Update Progress

Script: `planning:plan-execute`

```bash
python3 .plan/execute-script.py planning:plan-execute:update-progress \
  --plan-dir {plan_directory} \
  --phase {phase} \
  --task-id {task_id} \
  --complete-items "{item_text}"
```

### Step 3.5: Log Task Completion

After each task completes:

```bash
python3 .plan/execute-script.py planning:manage-log:add \
  --plan-id {plan_id} \
  --phase {phase} \
  --type artifact \
  --summary "Completed {task_id}: {task_title}" \
  --detail "{steps_completed} steps executed"
```

### Step 4: Next Task or Phase

- If more tasks in phase → Continue to next task
- If phase complete → Log phase outcome and auto-transition to next phase
- If all phases complete → Mark plan complete

### Step 5: Log Phase Completion (When phase completes)

```bash
python3 .plan/execute-script.py planning:manage-log:add \
  --plan-id {plan_id} \
  --phase {phase} \
  --type outcome \
  --summary "Completed {phase} phase: {tasks_completed} tasks" \
  --detail "Transitioning to {next_phase}"
```

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

On any error, **first log the error** to work-log:

```bash
python3 .plan/execute-script.py planning:manage-log:add \
  --plan-id {plan_id} \
  --phase {phase} \
  --type error \
  --summary "ERROR: {task_id} failed - {error_type}" \
  --detail "{full error context and message}"
```

### Script Failure (Lessons-Learned Capture)

**ON SCRIPT FAILURE**: When any script execution fails (exit != 0):
1. Log error to work-log (see above)
2. Capture error context (script path, exit code, stderr)
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

| Skill | Command | Purpose |
|-------|---------|---------|
| `planning:manage-lifecycle` | `get-routing-context` | Phase, skill routing, progress |
| `planning:manage-config` | `get-multi` | Finalize config fields |
| `planning:manage-tasks` | `next --include-context` | Task with specification context |
| `planning:manage-log` | `add` | Work log entries |
| `planning:manage-references` | - | Reference file CRUD |
| `planning:git-workflow` | - | Commit operations |

### Related Skills
- **plan-init** - Creates plan structure
- **plan-refine** - Generates implementation tasks

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to manage-* skills
- [x] DUMB TASK RUNNER pattern
- [x] Handles execute and finalize phases
