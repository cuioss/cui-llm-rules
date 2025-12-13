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
- Delete operations (via manage-files)
- Archive operations

## When to Activate This Skill

Activate this skill when:
- Creating or updating plan status
- Transitioning between phases
- Discovering all plans
- Deleting plans (to replace or abandon)
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
plan_type: pm-workflow:plan-type-java
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
| `plan_type` | bundle:skill notation (e.g., pm-workflow:plan-type-java) |
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

Script: `pm-workflow:manage-lifecycle:manage-lifecycle`

### read

Read plan status.

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

plan:
  title: Implement JWT Authentication
  plan_type: pm-workflow:plan-type-java
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
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle create \
  --plan-id {plan_id} \
  --title "Feature Title" \
  --plan-type pm-workflow:plan-type-java \
  --phases init,refine,execute,finalize \
  [--force]
```

**Parameters**:
- `--plan-id` (required): Plan identifier (kebab-case)
- `--title` (required): Plan title
- `--plan-type` (required): Plan type in `bundle:skill` notation
- `--phases` (required): Comma-separated phase names
- `--force`: Overwrite existing status.toon

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: status.toon
created: true

plan:
  title: Feature Title
  plan_type: pm-workflow:plan-type-java
  current_phase: init
```

### set-phase

Set the current phase.

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle set-phase \
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
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle update-phase \
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
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle progress \
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
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle list \
  [--filter init,execute]
```

**Parameters**:
- `--filter`: Filter by phases (comma-separated)

**Output** (TOON):
```toon
status: success
total: 3
plans:
  - id: my-feature
    current_phase: execute
    plan_type: pm-workflow:plan-type-java
    status: in_progress
  - id: bug-fix-123
    current_phase: init
    plan_type: pm-workflow:plan-type-generic
    status: in_progress
```

### transition

Transition to next phase.

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle transition \
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
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle archive \
  --plan-id {plan_id} \
  [--dry-run]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
archived_to: .plan/archived-plans/2025-12-02-my-feature/
```

---

## Delete Operations

Delete operations use `pm-workflow:manage-files:manage-files` (not manage-lifecycle) because deletion involves removing plan directories, not just status management.

### delete-plan

Delete an entire plan directory. Use when:
- Replacing an existing plan with a fresh one
- Abandoning a plan that's no longer needed
- Cleaning up failed or corrupted plans

```bash
python3 .plan/execute-script.py pm-workflow:manage-files:manage-files delete-plan \
  --plan-id {plan_id}
```

**Parameters**:
- `--plan-id` (required): Plan identifier to delete

**Output** (TOON):
```toon
status: success
plan_id: my-feature
action: deleted
path: .plan/plans/my-feature
files_removed: 7
```

**Error Output**:
```toon
status: error
plan_id: my-feature
error: plan_not_found
message: Plan directory does not exist
```

**Safety Notes**:
- Only deletes directories under `.plan/plans/`
- Validates plan_id format (kebab-case)
- Does NOT prompt for confirmation (caller handles user confirmation)
- Cannot be undone - ensure user confirms before calling

### Delete vs Archive

| Operation | Use Case | Recoverable |
|-----------|----------|-------------|
| `delete-plan` | Replace, abandon, cleanup | No |
| `archive` | Completed plans for reference | Yes (moved to archived-plans) |

---

### route

Get skill for a phase.

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle route \
  --phase execute
```

**Parameters**:
- `--phase` (required): Phase name

**Output** (TOON):
```toon
status: success
phase: execute
skill: plan-execute
description: Execute implementation tasks
```

### get-routing-context

Get combined routing context (phase, skill, and progress) in one call.

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle get-routing-context \
  --plan-id {plan_id}
```

**Parameters**:
- `--plan-id` (required): Plan identifier

**Output** (TOON):
```toon
status: success
plan_id: my-feature
title: Implement JWT Authentication
plan_type: pm-workflow:plan-type-java
current_phase: execute
skill: plan-execute
skill_description: Execute implementation tasks
total_phases: 4
completed_phases: 2
phases:
  - name: init
    status: done
  - name: refine
    status: done
  - name: execute
    status: in_progress
  - name: finalize
    status: pending
```

---

## Scripts

**Script**: `pm-workflow:manage-lifecycle:manage-lifecycle`

| Command | Parameters | Description |
|---------|------------|-------------|
| `read` | `--plan-id` | Read plan status |
| `create` | `--plan-id --title --plan-type --phases [--force]` | Initialize status.toon |
| `set-phase` | `--plan-id --phase` | Set current phase |
| `update-phase` | `--plan-id --phase --status` | Update phase status |
| `progress` | `--plan-id` | Calculate plan progress |
| `list` | `[--filter]` | Discover all plans |
| `transition` | `--plan-id --completed` | Transition to next phase |
| `archive` | `--plan-id [--dry-run]` | Archive completed plan |
| `route` | `--phase` | Get skill for phase |
| `get-routing-context` | `--plan-id` | Get combined routing context |

**Script**: `pm-workflow:manage-files:manage-files` (delete operations)

| Command | Parameters | Description |
|---------|------------|-------------|
| `delete-plan` | `--plan-id` | Delete entire plan directory |

---

## Plan Types and Phases

Plan types use `bundle:skill` notation and define their own phase sequences.

### pm-workflow:plan-type-java (4 phases)
init -> refine -> execute -> finalize

### pm-workflow:plan-type-javascript (4 phases)
init -> refine -> execute -> finalize

### pm-workflow:plan-type-plugin (4 phases)
init -> refine -> execute -> finalize

### pm-workflow:plan-type-generic (3 phases)
init -> execute -> finalize

**Note**: Plan types are extension points. Any bundle can define custom plan types with custom phase sequences.

---

## Phase Routing

The `route` command returns skill names for each phase (from script `PHASE_ROUTING`):

| Phase | Skill | Description |
|-------|-------|-------------|
| init | `plan-init` | Initialize plan |
| refine | `plan-refine` | Refine requirements and specifications |
| execute | `plan-execute` | Execute implementation tasks |
| finalize | `plan-finalize` | Finalize with commit/PR |

**Note**: These are skill names, not full bundle:skill notation. The actual components used:

| Phase | Component | Type | Description |
|-------|-----------|------|-------------|
| init | `pm-workflow:plan-init-agent` | agent | Creates plan, analyzes task, creates solution outline |
| refine | `pm-workflow:plan-refine-agent` | agent | Creates tasks from deliverables |
| execute | `pm-workflow:plan-execute` | skill | Executes implementation tasks |
| finalize | `pm-workflow:plan-finalize` | skill | Git workflow, commit, PR creation |

### Init Phase

The init phase handles complete plan initialization:

```
plan-init-agent:
   - Creates plan directory
   - Writes request.md from input (description/lesson/issue)
   - Analyzes task to create solution outline with deliverables
   - Detects plan type (or uses override)
   - Creates config.toon and status.toon
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
