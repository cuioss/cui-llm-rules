---
name: manage-tasks
description: Manage implementation tasks with sequential sub-steps within a plan
allowed-tools: Read, Glob, Bash
---

# Manage Tasks Skill

Manage implementation tasks with sequential sub-steps within a plan. Each task references a goal and contains ordered steps for execution.

## What This Skill Provides

- Individual TOON file storage for each task
- Sequential, immutable numbering (TASK-1, TASK-2, etc.)
- Required goal reference (GOAL-N) for traceability
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

Directory created on first `add` operation.

**Filename format**: `TASK-{NNN}-{slug}.toon`
- `{NNN}` - Zero-padded 3-digit number (001, 002, etc.)
- `{slug}` - Kebab-case from title (max 40 chars)

---

## File Format

Individual TOON files with metadata and steps:

```toon
number: 1
title: Implement JWT Service
status: pending
goal: GOAL-1
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T10:30:00Z

description: |
  Create the JWT service class with token generation
  and validation methods.

steps[3]{number,title,status}:
1,Create JwtService class,pending
2,Add token generation method,pending
3,Write unit tests,pending

current_step: 1
```

### Task Fields

| Field | Required | Description |
|-------|----------|-------------|
| `number` | Yes | Unique number (assigned at creation, immutable) |
| `title` | Yes | Short descriptive title |
| `goal` | Yes | GOAL-N reference (exactly one) |
| `description` | Yes | Detailed task description |
| `status` | Yes | `pending`, `in_progress`, `done`, or `blocked` |
| `steps` | Yes | Ordered list of steps (at least one) |
| `current_step` | Yes | Current step number for execution |
| `created` | Yes | ISO timestamp when created |
| `updated` | Yes | ISO timestamp of last update |

### Status Model

**Task Status**:
| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Currently being worked on |
| `done` | All steps completed |
| `blocked` | Cannot proceed (dependency/issue) |

**Step Status**:
| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Currently executing |
| `done` | Completed |
| `skipped` | Intentionally skipped |

**Numbering Rules**:
- Task numbers assigned incrementally (next available)
- Numbers are **immutable** - removal creates gaps (1, 3, 4 if TASK-2 removed)
- References use `TASK-{n}` format (stable references)
- Steps are numbered 1-N within each task

---

## Operations

Script: `planning:manage-tasks:manage-task`

### add

Add a new task file (creates directory if needed).

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --goal GOAL-1 \
  --title "Implement JWT Service" \
  --description "Create the JWT service class..." \
  --steps "Create JwtService class" "Add token generation" "Write unit tests"
```

**Output**:
```toon
status: success
plan_id: my-feature
file: TASK-001-implement-jwt-service.toon
total_tasks: 1

task:
  number: 1
  title: Implement JWT Service
  goal: GOAL-1
  status: pending
  step_count: 3
```

### update

Update task metadata (not steps - use step operations for that).

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task update \
  --plan-id {plan_id} \
  --number 1 \
  [--title "New title"] \
  [--description "New description"] \
  [--goal GOAL-2]
```

### remove

Remove a task file (keeps gaps in numbering).

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task remove \
  --plan-id {plan_id} \
  --number 1
```

### list

List all tasks with summary.

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task list \
  --plan-id {plan_id} \
  [--status pending|in_progress|done|blocked|all] \
  [--goal GOAL-1]
```

**Output**:
```toon
status: success
plan_id: my-feature

counts:
  total: 3
  pending: 1
  in_progress: 1
  done: 1
  blocked: 0

tasks[3]{number,title,goal,status,progress}:
1,Implement JWT Service,GOAL-1,done,3/3
2,Add Auth Endpoint,GOAL-1,in_progress,1/3
3,Write Integration Tests,GOAL-2,pending,0/2
```

### get

Get a single task with full details.

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task get \
  --plan-id {plan_id} \
  --number 2
```

**Output**:
```toon
status: success
plan_id: my-feature
file: TASK-002-add-auth-endpoint.toon

task:
  number: 2
  title: Add Auth Endpoint
  goal: GOAL-1
  status: in_progress
  current_step: 2
  created: 2025-12-02T10:30:00Z
  updated: 2025-12-02T11:00:00Z
  description: Create REST endpoint for authentication...
  steps[3]{number,title,status}:
  1,Create controller,done
  2,Add request/response DTOs,in_progress
  3,Write integration tests,pending
```

### next

Get the next pending task or step (for execution).

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task next \
  --plan-id {plan_id}
```

**Output (task in progress)**:
```toon
status: success
plan_id: my-feature

next:
  task_number: 2
  task_title: Add Auth Endpoint
  goal: GOAL-1
  step_number: 2
  step_title: Add request/response DTOs

context:
  completed_steps: 1
  remaining_steps: 2
  total_tasks: 3
  completed_tasks: 1
```

**Output (all done)**:
```toon
status: success
plan_id: my-feature

next: null

context:
  total_tasks: 3
  completed_tasks: 3
  message: All tasks completed
```

---

## Step Operations

### step-start

Mark a step as in_progress (also marks task as in_progress).

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task step-start \
  --plan-id {plan_id} \
  --task 2 \
  --step 2
```

**Output**:
```toon
status: success
plan_id: my-feature
task: 2
step: 2

task_status: in_progress
step_status: in_progress
step_title: Add request/response DTOs
```

### step-done

Mark a step as completed.

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task step-done \
  --plan-id {plan_id} \
  --task 2 \
  --step 2
```

**Output**:
```toon
status: success
plan_id: my-feature
task: 2
step: 2

step_status: done
task_status: in_progress
next_step: 3
next_step_title: Write integration tests
```

**Output (last step)**:
```toon
status: success
plan_id: my-feature
task: 2
step: 3

step_status: done
task_status: done
next_step: null
message: Task completed
```

### step-skip

Skip a step (mark as skipped, move to next).

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task step-skip \
  --plan-id {plan_id} \
  --task 2 \
  --step 2 \
  --reason "Already exists"
```

### add-step

Add a new step to an existing task.

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add-step \
  --plan-id {plan_id} \
  --task 2 \
  --title "Add error handling" \
  [--after 2]  # Insert after step 2, renumber subsequent steps
```

### remove-step

Remove a step from a task.

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task remove-step \
  --plan-id {plan_id} \
  --task 2 \
  --step 3
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-tasks:manage-task` | All CRUD and step operations via subcommands | `python3 .plan/execute-script.py planning:manage-tasks:manage-task {subcommand} --help` |

---

## Integration Points

### With plan-refine

Tasks are created during plan refinement, after goals are defined:

```
FOR EACH goal:
  1. READ goal via plan-goals skill
  2. ANALYZE what implementation work is needed
  3. CREATE tasks for the goal:
     manage-task.py add --plan-id {plan_id} --goal GOAL-{n} ...
```

### With plan-execute

The plan-execute skill uses task-manager for simple iteration:

```
LOOP:
  1. QUERY next: manage-task.py next --plan-id {plan_id}
  2. IF no next: DONE
  3. MARK started: manage-task.py step-start ...
  4. EXECUTE step
  5. ON SUCCESS: manage-task.py step-done ...
  6. CONTINUE
```

### With manage-goals

Tasks reference goals via the `goal` field, enabling:
- Forward traceability: GOAL -> TASKs
- Backward traceability: TASK -> GOAL
- Coverage analysis: Which GOALs have implementation tasks?

---

## Traceability Chain

```
Request (User can authenticate)
  |
  +-> GOAL-1 (JWT Token Format)
        |
        +-> TASK-1 (Implement JWT Service)
        |     +-- Step 1: Create class
        |     +-- Step 2: Add methods
        |     +-- Step 3: Write tests
        |
        +-> TASK-2 (Add Auth Endpoint)
              +-- Step 1: Create controller
              +-- Step 2: Write tests
```

Query capabilities:
- `manage-goal.py findAll` -> All goals
- `manage-task.py list --goal GOAL-1` -> TASK-1, TASK-2
- `manage-task.py next` -> Next actionable step

---

## Relationship to Goals

| Aspect | goals | tasks |
|--------|-------|-------|
| Directory | `{plan_dir}/goals/` | `{plan_dir}/tasks/` |
| Prefix | GOAL- | TASK- |
| References | From request | **GOAL reference** |
| Created in | plan-init phase | plan-refine phase |
| Purpose | What will be built | How to build it |
| Granularity | Feature-level | Step-level |

**Flow**: Request (what) -> GOAL (how) -> TASK (steps) -> Implementation (code)
