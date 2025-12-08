---
name: manage-tasks
description: Manage implementation tasks with sequential sub-steps within a plan
allowed-tools: Read, Glob, Bash
---

# Manage Tasks Skill

Manage implementation tasks with sequential sub-steps within a plan. Each task references a specification and contains ordered steps for execution.

## What This Skill Provides

- Individual TOON file storage for each task
- Sequential, immutable numbering (TASK-1, TASK-2, etc.)
- Required specification reference (SPEC-N) for traceability
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
specification: SPEC-1
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
| `specification` | Yes | SPEC-N reference (exactly one) |
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

Script: `planning:manage-tasks`

### add

Add a new task file (creates directory if needed).

```bash
python3 .plan/execute-script.py planning:manage-tasks:add \
  --plan-id {plan_id} \
  --specification SPEC-1 \
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
  specification: SPEC-1
  status: pending
  step_count: 3
```

### update

Update task metadata (not steps - use step operations for that).

```bash
python3 .plan/execute-script.py planning:manage-tasks:update \
  --plan-id {plan_id} \
  --number 1 \
  [--title "New title"] \
  [--description "New description"] \
  [--specification SPEC-2]
```

### remove

Remove a task file (keeps gaps in numbering).

```bash
python3 .plan/execute-script.py planning:manage-tasks:remove \
  --plan-id {plan_id} \
  --number 1
```

### list

List all tasks with summary.

```bash
python3 .plan/execute-script.py planning:manage-tasks:list \
  --plan-id {plan_id} \
  [--status pending|in_progress|done|blocked|all] \
  [--specification SPEC-1]
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

tasks[3]{number,title,specification,status,progress}:
1,Implement JWT Service,SPEC-1,done,3/3
2,Add Auth Endpoint,SPEC-1,in_progress,1/3
3,Write Integration Tests,SPEC-2,pending,0/2
```

### get

Get a single task with full details.

```bash
python3 .plan/execute-script.py planning:manage-tasks:get \
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
  specification: SPEC-1
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
python3 .plan/execute-script.py planning:manage-tasks:next \
  --plan-id {plan_id}
```

**Output (task in progress)**:
```toon
status: success
plan_id: my-feature

next:
  task_number: 2
  task_title: Add Auth Endpoint
  specification: SPEC-1
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
python3 .plan/execute-script.py planning:manage-tasks:step-start \
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
python3 .plan/execute-script.py planning:manage-tasks:step-done \
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
python3 .plan/execute-script.py planning:manage-tasks:step-skip \
  --plan-id {plan_id} \
  --task 2 \
  --step 2 \
  --reason "Already exists"
```

### add-step

Add a new step to an existing task.

```bash
python3 .plan/execute-script.py planning:manage-tasks:add-step \
  --plan-id {plan_id} \
  --task 2 \
  --title "Add error handling" \
  [--after 2]  # Insert after step 2, renumber subsequent steps
```

### remove-step

Remove a step from a task.

```bash
python3 .plan/execute-script.py planning:manage-tasks:remove-step \
  --plan-id {plan_id} \
  --task 2 \
  --step 3
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-tasks` | All CRUD and step operations via subcommands | `python3 .plan/execute-script.py planning:manage-tasks::{command} --help` |

---

## Integration Points

### With plan-refine

Tasks are created during plan refinement, after specifications are defined:

```
FOR EACH specification:
  1. READ specification via plan-specifications skill
  2. ANALYZE what implementation work is needed
  3. CREATE tasks for the specification:
     manage-task.py add --plan-id {plan_id} --specification SPEC-{n} ...
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

### With manage-specifications

Tasks reference specifications via the `specification` field, enabling:
- Forward traceability: SPEC -> TASKs
- Backward traceability: TASK -> SPEC
- Coverage analysis: Which SPECs have implementation tasks?

---

## Traceability Chain

```
REQ-1 (User can authenticate)
  |
  +-> SPEC-1 (JWT Token Format)
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
- `manage-requirement.py findAll` -> All requirements
- `manage-specification.py findByRequirement REQ-1` -> SPEC-1
- `manage-task.py list --specification SPEC-1` -> TASK-1, TASK-2
- `manage-task.py next` -> Next actionable step

---

## Relationship to Specifications

| Aspect | specifications | tasks |
|--------|----------------|-------|
| Directory | `{plan_dir}/specifications/` | `{plan_dir}/tasks/` |
| Prefix | SPEC- | TASK- |
| References | REQ references | **SPEC reference** |
| Created in | plan-refine phase | plan-refine phase |
| Purpose | What will be built | How to build it |
| Granularity | Feature-level | Step-level |

**Flow**: REQ (what) -> SPEC (how) -> TASK (steps) -> Implementation (code)
