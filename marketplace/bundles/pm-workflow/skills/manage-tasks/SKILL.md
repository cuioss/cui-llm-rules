---
name: manage-tasks
description: Manage implementation tasks with sequential sub-steps within a plan
allowed-tools: Read, Glob, Bash
---

# Manage Tasks Skill

Manage implementation tasks with sequential sub-steps within a plan. Each task references deliverables from the solution document and contains ordered steps for execution.

> **Implementation Details**: See [design-for-manage-tasks.md](/.plan/task-management/design-for-manage-tasks.md) for the complete specification including file format, all commands, parameters, and validation rules.

## What This Skill Provides

- Individual TOON file storage for each task
- Sequential, immutable numbering (TASK-1, TASK-2, etc.)
- Deliverable references (M:N relationship to solution_outline.md)
- Delegation context (skill + workflow for execution)
- Verification commands and criteria
- Step management with status tracking
- Simple execution loop via `next` query

## When to Activate This Skill

Activate this skill when:
- Creating or managing implementation tasks for a plan
- Querying next actionable task/step
- Marking steps as started/completed/skipped
- Tracking implementation progress

---

## Storage Location

Tasks are stored in the plan directory:

```
{plan_dir}/tasks/
  TASK-001-implement-jwt-service.toon
  TASK-002-add-auth-endpoint.toon
  TASK-003-write-integration-tests.toon
```

**Filename format**: `TASK-{NNN}-{slug}.toon`

---

## File Format (Summary)

```toon
number: 1
title: Update misc agents to TOON output
status: pending
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T10:30:00Z

deliverables[3]:
- 1
- 2
- 4

description: |
  Migrate miscellaneous agents from JSON to TOON output format.

delegation:
  skill: pm-plugin-development:plugin-maintain
  workflow: update-component

steps[3]{number,title,status}:
1,pm-plugin-development/agents/tool-coverage-agent.md,pending
2,pm-dev-builder/agents/gradle-builder.md,pending
3,pm-dev-frontend/commands/js-generate-coverage.md,pending

verification:
  commands[1]:
  - grep -L '```json' {files} | wc -l
  criteria: No JSON blocks remain

current_step: 1
```

---

## Operations

Script: `pm-workflow:manage-tasks:manage-task`

| Command | Parameters | Description |
|---------|------------|-------------|
| `add` | `--plan-id --deliverables --title --description --steps [--delegation-*] [--verification-*]` | Add a new task |
| `update` | `--plan-id --number [--title] [--description] [--status]` | Update task metadata |
| `remove` | `--plan-id --number` | Remove a task |
| `list` | `--plan-id [--status] [--deliverable]` | List all tasks |
| `get` | `--plan-id --number` | Get single task details |
| `next` | `--plan-id [--include-context]` | Get next pending task/step |
| `step-start` | `--plan-id --task --step` | Mark step as in_progress |
| `step-done` | `--plan-id --task --step` | Mark step as done |
| `step-skip` | `--plan-id --task --step [--reason]` | Skip a step |
| `add-step` | `--plan-id --task --title [--after]` | Add step to task |
| `remove-step` | `--plan-id --task --step` | Remove step from task |

---

## Quick Examples

### Add a task

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task add \
  --plan-id my-feature \
  --deliverables 1 2 4 \
  --title "Update misc agents to TOON" \
  --description "Migrate miscellaneous agents..." \
  --steps "file1.md" "file2.md" "file3.md" \
  --delegation-skill pm-plugin-development:plugin-maintain \
  --delegation-workflow update-component
```

### Get next task/step

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task next \
  --plan-id my-feature
```

### Mark step done

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task step-done \
  --plan-id my-feature \
  --task 2 \
  --step 3
```

---

## Integration Points

### With task-plan-agent

Task-plan agents create tasks during plan refinement:
```
manage-task add --plan-id {plan_id} --deliverables {n1} {n2} ...
```

### With plan-execute

Plan-execute iterates through tasks:
```
LOOP:
  1. manage-task next --plan-id {plan_id}
  2. IF no next: DONE
  3. SPAWN implement agent
  4. CONTINUE
```

### With implement-agent

Implement agents execute steps:
```
1. manage-task get --plan-id {plan_id} --number {N}
2. FOR EACH step: step-start → execute → step-done
3. RUN verification
```

---

## Status Model

**Task Status**: `pending` → `in_progress` → `done` (or `blocked`)

**Step Status**: `pending` → `in_progress` → `done` (or `skipped`)

---

## Related Documents

- [design-for-manage-tasks.md](/.plan/task-management/design-for-manage-tasks.md) - Complete implementation specification
- [design-for-task-planning.md](/.plan/task-management/design-for-task-planning.md) - Task-plan agent workflows
- [architecture.md](/.plan/task-management/architecture.md) - Core concepts
