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
plan_type: planning:plan-type-java
current_phase: execute

phases[4]{name,status}:
init,done
refine,done
execute,in_progress
finalize,pending

created: 2025-12-02T10:00:00Z
updated: 2025-12-02T14:30:00Z
```

### Status Fields

| Field | Description |
|-------|-------------|
| `title` | Plan title |
| `plan_type` | bundle:skill notation (e.g., planning:plan-type-java) |
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

Script: `planning:manage-lifecycle`

### read

Read plan status.

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

plan:
  title: Implement JWT Authentication
  plan_type: planning:plan-type-java
  current_phase: execute
  phases[4]{name,status}:
  init,done
  refine,done
  execute,in_progress
  finalize,pending
```

### create

Initialize status.toon for a new plan.

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:create \
  --plan-id {plan_id} \
  --title "Feature Title" \
  --plan-type planning:plan-type-java \
  --phases init,refine,execute,finalize
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: status.toon
created: true

plan:
  title: Feature Title
  plan_type: planning:plan-type-java
  current_phase: init
```

### set-phase

Set the current phase.

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:set-phase \
  --plan-id {plan_id} \
  --phase execute
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
current_phase: execute
previous_phase: refine
```

### update-phase

Update a specific phase status.

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:update-phase \
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
python3 .plan/execute-script.py planning:manage-lifecycle:progress \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

progress:
  total_phases: 4
  completed_phases: 2
  current_phase: execute
  percent: 50
```

---

## Phase Management Operations

### list

Discover all plans.

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:list \
  [--filter init,execute]
```

**Output** (TOON):
```toon
status: success
total: 3

plans[3]{id,current_phase,plan_type,status}:
my-feature,execute,planning:plan-type-java,in_progress
bug-fix-123,init,planning:plan-type-generic,in_progress
plugin-update,finalize,planning:plan-type-plugin,in_progress
```

### transition

Transition to next phase.

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:transition \
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
python3 .plan/execute-script.py planning:manage-lifecycle:archive \
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
python3 .plan/execute-script.py planning:manage-lifecycle:route \
  --phase execute
```

**Output** (TOON):
```toon
status: success
phase: execute
skill: plan-execute
description: Execute implementation tasks
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-lifecycle` | All lifecycle operations via subcommands | `python3 .plan/execute-script.py planning:manage-lifecycle::{command} --help` |

---

## Plan Types and Phases

Plan types use `bundle:skill` notation and define their own phase sequences.

### planning:plan-type-java (4 phases)
init -> refine -> execute -> finalize

### planning:plan-type-javascript (4 phases)
init -> refine -> execute -> finalize

### planning:plan-type-plugin (4 phases)
init -> refine -> execute -> finalize

### planning:plan-type-generic (3 phases)
init -> execute -> finalize

**Note**: Plan types are extension points. Any bundle can define custom plan types with custom phase sequences.

---

## Phase Routing

The init phase uses a two-agent pattern; all other phases use single components.

| Phase | Component | Type | Description |
|-------|-----------|------|-------------|
| init (step 1) | `planning:plan-init-agent` | agent | Creates plan directory and task.md |
| init (step 2) | `planning:plan-configure-agent` | agent | Analyzes task, creates requirements, detects type, configures plan |
| refine | `planning:plan-refine-agent` | agent | Creates specifications and tasks from requirements |
| execute | `planning:plan-execute` | skill | Executes implementation tasks |
| finalize | `planning:plan-finalize` | skill | Git workflow, commit, PR creation |

### Init Phase Orchestration

The init phase requires two sequential agents:

```
1. plan-init-agent:
   - Creates plan directory
   - Writes task.md from input (description/lesson/issue)

2. plan-configure-agent:
   - Reads task.md
   - Analyzes task to create requirements
   - Detects plan type (or uses override)
   - Creates config.toon with base settings
   - Calls plan-type configure for domain fields
   - Transitions phase: init → refine
```

**Note**: The `plan-finalize` skill handles git workflow (commit, push, PR) separately from task execution.

---

## Error Handling

```toon
status: error
plan_id: my-feature
error: invalid_transition
message: Cannot transition from 'init' to 'execute' - must complete phases in order
```
