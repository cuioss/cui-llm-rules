---
name: plan-execute
description: Execute phase skill for plan management. DUMB TASK RUNNER that executes checklist items from plan.md sequentially for implement, verify, and finalize phases.
allowed-tools: Read, Write, Edit, Bash, Skill, Task, AskUserQuestion
---

# Plan Execute Skill

**Role**: DUMB TASK RUNNER that executes checklist items from plan.md sequentially.

**Execution Pattern**: Locate current task → Execute checklist items → Mark progress → Next task

**Phases Handled**: implement, verify, finalize (execute for simple plans)

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
Skill: planning:plan-files
operation: read-config → get plan_type

Skill: planning:plan-type-{plan_type}
operation: get-finalize-config
plan_id: {plan_directory}
```

Returns: `commit_strategy`, `create_pr`, `verification_required`, `verification_command`

---

## Execution Loop

For each task in current phase:

### Step 1: Locate Task

```
Read plan.md
Find task with status: in_progress or first pending
```

### Step 2: Execute Checklist Items

For each unchecked item `- [ ]`:
1. Parse the item text
2. Execute the action (delegate if specified)
3. Mark item complete via `update-progress.py`

### Step 3: Update Progress

```bash
python3 {update-progress.py} --plan-dir {plan_directory} --phase {phase} --task-id {task_id} --complete-items "{item_text}"
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

When transitioning from implement/execute phases, `transition-phase.py` automatically:
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
- **plan-files** - All file I/O operations
- **plan-type-simple** - Finalize config for simple plans
- **plan-type-plugin** - Finalize config for plugin plans
- **plan-type-implementation** - Finalize config for implementation plans
- **git-workflow** - Commit operations
- **work-log** - Session logging

### Related Skills
- **plan-init** - Creates plan structure
- **plan-refine** - Generates implementation tasks

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to plan-files skill
- [x] DUMB TASK RUNNER pattern
- [x] Handles implement/verify/finalize phases
