---
name: manage-lifecycle
description: Manage plan lifecycle with status.toon and phase operations
allowed-tools: Read, Glob, Bash
---

# Manage Lifecycle Skill

Manage plan lifecycle with status.toon and phase operations. Replaces plan.md and absorbs phase-management skill functionality.

## What This Skill Provides

- Status.toon CRUD operations
- Phase management (transitions, progress)
- Plan discovery (list all plans)
- Phase routing (skill mapping)
- Archive operations

## When to Activate This Skill

Activate this skill when:
- Creating or updating plan status
- Transitioning between phases
- Discovering all plans
- Archiving completed plans

---

## Storage Location

Status is stored in the plan directory:

```
.plan/plans/{plan_id}/status.toon
```

Archived plans:

```
.plan/archived-plans/{yyyy-mm-dd}-{plan-name}/
```

---

## File Format

TOON format with phases table:

```toon
title: Implement JWT Authentication
plan_type: implementation
current_phase: implement

phases[5]{name,status}:
init,done
refine,done
implement,in_progress
verify,pending
finalize,pending

created: 2025-12-02T10:00:00Z
updated: 2025-12-02T14:30:00Z
```

### Status Fields

| Field | Description |
|-------|-------------|
| `title` | Plan title |
| `plan_type` | implementation, plugin-development, simple |
| `current_phase` | Current active phase |
| `phases` | Table of phase names and statuses |
| `created` | ISO timestamp when created |
| `updated` | ISO timestamp of last update |

### Phase Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Currently active |
| `done` | Completed |

---

## Status Operations

Script: `planning:manage-lifecycle/scripts/manage-lifecycle.py`

### read

Read plan status.

```bash
python3 {script_path} read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

plan:
  title: Implement JWT Authentication
  plan_type: implementation
  current_phase: implement
  phases[5]{name,status}:
  init,done
  refine,done
  implement,in_progress
  verify,pending
  finalize,pending
```

### create

Initialize status.toon for a new plan.

```bash
python3 {script_path} create \
  --plan-id {plan_id} \
  --title "Feature Title" \
  --plan-type implementation
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: status.toon
created: true

plan:
  title: Feature Title
  plan_type: implementation
  current_phase: init
```

### set-phase

Set the current phase.

```bash
python3 {script_path} set-phase \
  --plan-id {plan_id} \
  --phase implement
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
current_phase: implement
previous_phase: refine
```

### update-phase

Update a specific phase status.

```bash
python3 {script_path} update-phase \
  --plan-id {plan_id} \
  --phase init \
  --status done
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
phase: init
phase_status: done
```

### progress

Calculate plan progress.

```bash
python3 {script_path} progress \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

progress:
  total_phases: 5
  completed_phases: 2
  current_phase: implement
  percent: 40
```

---

## Phase Management Operations

### list

Discover all plans.

```bash
python3 {script_path} list \
  [--filter init,implement]
```

**Output** (TOON):
```toon
status: success
total: 3

plans[3]{id,current_phase,plan_type,status}:
my-feature,implement,implementation,in_progress
bug-fix-123,init,simple,in_progress
plugin-update,finalize,plugin-development,in_progress
```

### transition

Transition to next phase.

```bash
python3 {script_path} transition \
  --plan-id {plan_id} \
  --completed init
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
completed_phase: init
next_phase: refine
```

### archive

Archive a completed plan.

```bash
python3 {script_path} archive \
  --plan-id {plan_id} \
  [--dry-run]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
archived_to: .plan/archived-plans/2025-12-02-my-feature/
```

### route

Get skill for a phase.

```bash
python3 {script_path} route \
  --phase implement
```

**Output** (TOON):
```toon
status: success
phase: implement
skill: plan-execute
description: Execute implementation tasks
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-lifecycle/scripts/manage-lifecycle.py` | All lifecycle operations via subcommands | `python3 {script_path} {command} --help` |

---

## Plan Types and Phases

### implementation (5 phases)
init -> refine -> implement -> verify -> finalize

### plugin-development (4 phases)
init -> implement -> verify -> finalize

### simple (3 phases)
init -> implement -> finalize

---

## Phase Routing

| Phase | Skill |
|-------|-------|
| init | plan-init |
| refine | plan-refine |
| implement | plan-execute |
| verify | plan-execute |
| finalize | plan-finalize |

---

## Error Handling

```toon
status: error
plan_id: my-feature
error: invalid_transition
message: Cannot transition from 'init' to 'implement' - must complete phases in order
```
