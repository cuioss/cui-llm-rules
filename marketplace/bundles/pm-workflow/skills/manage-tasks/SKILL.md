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
phase: execute
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T10:30:00Z

deliverables[3]:
- 1
- 2
- 4

depends_on: TASK-1, TASK-2

description: |
  Migrate miscellaneous agents from JSON to TOON output format.

delegation:
  skill: pm-plugin-development:plugin-maintain
  workflow: update-component
  domain: plugin
  context_skills:
  - pm-plugin-development:plugin-architecture

steps[3]{number,title,status}:
1,pm-plugin-development/agents/tool-coverage-agent.md,pending
2,pm-dev-builder/agents/gradle-builder.md,pending
3,pm-dev-frontend/commands/js-generate-coverage.md,pending

verification:
  commands[1]:
  - grep -L '```json' {files} | wc -l
  criteria: No JSON blocks remain
  manual: false

current_step: 1
```

---

## Operations

Script: `pm-workflow:manage-tasks:manage-task`

| Command | Parameters | Description |
|---------|------------|-------------|
| `add` | `--plan-id --deliverables --domain --title --description --steps [--phase] [--depends-on] [--delegation-*] [--verification-*]` | Add a new task |
| `update` | `--plan-id --number [--title] [--description] [--depends-on] [--status]` | Update task metadata |
| `remove` | `--plan-id --number` | Remove a task |
| `list` | `--plan-id [--status] [--phase] [--deliverable] [--ready]` | List all tasks |
| `get` | `--plan-id --number` | Get single task details |
| `next` | `--plan-id [--phase] [--include-context] [--ignore-deps]` | Get next pending task/step |
| `step-start` | `--plan-id --task --step` | Mark step as in_progress |
| `step-done` | `--plan-id --task --step` | Mark step as done |
| `step-skip` | `--plan-id --task --step [--reason]` | Skip a step |
| `add-step` | `--plan-id --task --title [--after]` | Add step to task |
| `remove-step` | `--plan-id --task --step` | Remove step from task |

### Add Command Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--deliverables` | Yes | Deliverable numbers from solution_outline.md (space-separated) |
| `--domain` | Yes | Skill domain: `java`, `java-testing`, `javascript`, `javascript-testing`, `plugin` |
| `--phase` | No | Plan phase: `init`, `refine`, `execute` (default), `finalize` |
| `--depends-on` | No | Task dependencies: `TASK-N` references or `none` |
| `--delegation-skill` | No | Skill for task execution |
| `--delegation-workflow` | No | Workflow within skill |
| `--context-skills` | No | Optional skills from domain optionals |
| `--verification-commands` | No | Commands for verification |
| `--verification-criteria` | No | Success criteria text |
| `--verification-manual` | No | Flag for manual verification |

### List/Next Filters

| Parameter | Description |
|-----------|-------------|
| `--phase` | Filter by plan phase (init/refine/execute/finalize) |
| `--deliverable` | Filter by deliverable number |
| `--ready` | Only tasks with satisfied dependencies |
| `--ignore-deps` | (next only) Ignore dependency constraints |

---

## Quick Examples

### Add a task

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task add \
  --plan-id my-feature \
  --deliverables 1 2 4 \
  --domain java \
  --title "Update misc agents to TOON" \
  --description "Migrate miscellaneous agents..." \
  --steps "file1.md" "file2.md" "file3.md" \
  --delegation-skill pm-plugin-development:plugin-maintain \
  --delegation-workflow update-component \
  --verification-commands "mvn verify"
```

### Add a task with dependencies

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task add \
  --plan-id my-feature \
  --deliverables 3 \
  --domain java-testing \
  --title "Write integration tests" \
  --description "Add integration tests for new endpoint" \
  --steps "Create test class" "Add test methods" "Run tests" \
  --depends-on TASK-1 TASK-2 \
  --verification-commands "mvn verify -Pintegration"
```

### Get next task/step (respects dependencies)

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task next \
  --plan-id my-feature
```

### Get next task in specific phase

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task next \
  --plan-id my-feature \
  --phase execute
```

### List ready tasks only

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task list \
  --plan-id my-feature \
  --ready
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

## Deliverable-to-Task Relationship

Tasks reference deliverables from `solution_outline.md` using the `--deliverables` parameter.

| Pattern | Description | Example |
|---------|-------------|---------|
| 1:1 | One task per deliverable | `--deliverables 1` - Task implements deliverable 1 |
| N:1 | Multiple deliverables in one task | `--deliverables 1 2 3` - Task implements deliverables 1, 2, 3 |
| 1:N | One deliverable split across tasks | TASK-1 and TASK-2 both have `--deliverables 1` |

**When to use N:1**: Group related deliverables that share implementation context.

**When to use 1:N**: Split large deliverables into phased implementation (e.g., init task, implement task, verify task).

---

## Dependency Management

Tasks can depend on other tasks using `--depends-on`:

```bash
# Task 3 waits for Task 1 and Task 2 to complete
--depends-on TASK-1 TASK-2

# No dependencies
--depends-on none
```

**Dependency enforcement**:
- `next` command only returns tasks with satisfied dependencies
- Use `--ignore-deps` to bypass dependency checking
- Use `--ready` filter to list only ready tasks

**Blocked output**: When tasks are blocked by dependencies, `next` returns:

```toon
next: null
blocked_tasks[2]{number,title,waiting_for}:
1,Write tests,TASK-3
2,Deploy,TASK-3, TASK-4
```

---

## Phase Filtering

Tasks belong to plan phases: `init`, `refine`, `execute`, `finalize`

**Filter by phase**:
```bash
# List execute phase tasks only
--phase execute

# Get next task in finalize phase
next --phase finalize
```

**Phase purpose**:
- `init`: Setup tasks (create directories, configs)
- `refine`: Planning tasks (analysis, design)
- `execute`: Implementation tasks (code changes)
- `finalize`: Cleanup tasks (docs, release)

---

## Status Model

**Task Status**: `pending` → `in_progress` → `done` (or `blocked`)

**Step Status**: `pending` → `in_progress` → `done` (or `skipped`)

---

## Related Documents

- [design-for-manage-tasks.md](/.plan/task-management/design-for-manage-tasks.md) - Complete implementation specification
- [design-for-task-planning.md](/.plan/task-management/design-for-task-planning.md) - Task-plan agent workflows
- [architecture.md](/.plan/task-management/architecture.md) - Core concepts
