# Phase Management Skill Updates

## Overview

Updates required to `cui-task-workflow:phase-management` skill to support the split into `/plan-manage` and `/plan-execute` commands.

## Current State

The skill currently has one main workflow:
- **Orchestrate Task** - Handles all phases via unified routing

## Target State

Add two focused workflows:
- **Manage Workflow** - For `/plan-manage` (list, cleanup, init, refine)
- **Execute Workflow** - For `/plan-execute` (implement, verify, finalize)

Keep existing operations but extend with new capabilities.

---

## New Workflow: Manage Plans

**Purpose**: Handle plan lifecycle management operations.

### Input Parameters

```
- action: list|cleanup|init|refine
- plan_path: (optional) Specific plan directory
- task_description: (optional) For init action
- issue_url: (optional) For init action
```

### Step 1: Route by Action

```python
def route_action(action, params):
    if action == 'list' or not action:
        return 'operation_list'
    elif action == 'cleanup':
        return 'operation_cleanup'
    elif action == 'init':
        return 'operation_init'
    elif action == 'refine':
        return 'operation_refine'
    else:
        return 'error_invalid_action'
```

### Step 2: Execute Operation

**list** → `Operation: list-plans`
**cleanup** → `Operation: cleanup-plans`
**init** → `Operation: init-plan`
**refine** → `Operation: refine-plan`

---

## New Workflow: Execute Plans

**Purpose**: Handle plan execution phases.

### Input Parameters

```
- plan_path: (optional) Specific plan directory
- explicit_phase: (optional) Force implement|verify|finalize
```

### Step 1: Determine Plan

```
If plan_path provided:
    → Validate and load plan
Else:
    → Run Operation: discover-executable
    → Present numbered selection
    → Load selected plan
```

### Step 2: Validate Phase

```
If current_phase in [init, refine]:
    → Error: "Use /plan-manage for init/refine phases"

If explicit_phase provided:
    → Validate reachable from current_phase
```

### Step 3: Execute Phase

```
Match current_phase:
    implement → Skill: cui-task-workflow:plan-implement
    verify → Skill: cui-task-workflow:plan-verify
    finalize → Skill: cui-task-workflow:plan-finalize
```

### Step 4: Handle Completion

Same as current "Handle Phase Completion" logic.

---

## New Operation: list-plans

**Purpose**: List all plans with interactive selection.

**Input**: None

**Steps**:

1. Run discovery:
   ```bash
   python3 scripts/discover-plans.py .claude/plans/
   ```

2. Format output for display:
   ```
   plans_display[N]{number,name,phase,progress}:
     1,jwt-authentication,implement,3/12
     2,user-profile,refine,requirements
     3,database-migration,finalize,ready

   options:
     0: Create new plan
     c: Cleanup completed
     q: Quit
   ```

3. Return formatted data for AskUserQuestion

**Output**:
```
plans_found[N]{name,phase,status}:
  ...

display_format: numbered_list
prompt: "Select plan (number) or action (c/n/q):"
```

---

## New Operation: cleanup-plans

**Purpose**: Find and remove completed plans.

**Input**: None (or `confirm: true` to skip confirmation)

**Steps**:

1. Find completed plans:
   ```bash
   python3 scripts/discover-plans.py .claude/plans/ --filter=completed
   ```

2. If no completed plans:
   ```
   result: no_completed_plans
   message: "No completed plans found"
   ```

3. Return list for confirmation

**Output**:
```
completed_plans[N]{name,path,completed_date}:
  old-feature,.claude/plans/old-feature/,2024-01-15
  ...

prompt: "Select plans to delete (all/numbers/cancel):"
```

---

## New Operation: init-plan

**Purpose**: Create new plan with existing init-phase plan detection.

**Input**:
- `task_description` (optional)
- `issue_url` (optional)

**Steps**:

1. Check for existing init-phase plans:
   ```bash
   python3 scripts/discover-plans.py .claude/plans/ --filter=init
   ```

2. If init-phase plans exist:
   - Return list for user selection
   - Include option "0: Create new"

3. On selection or new:
   - Delegate to `Skill: cui-task-workflow:plan-init`

4. On init completion:
   - Return handoff for refine prompt

**Output**:
```
existing_init_plans[N]{name,path,created}:
  draft-feature,.claude/plans/draft-feature/,2024-01-20
  ...

# Or after init complete:
plan_created:
  path: .claude/plans/new-feature/

prompt: "Continue with refine phase? (yes/no)"
```

---

## New Operation: refine-plan

**Purpose**: Refine specific plan or select from refine-phase plans.

**Input**: `plan_path` (optional)

**Steps**:

1. If plan_path provided:
   - Validate plan exists
   - Validate phase allows refine
   - Delegate to `Skill: cui-task-workflow:plan-refine`

2. If no plan_path:
   - Find refine-phase plans:
     ```bash
     python3 scripts/discover-plans.py .claude/plans/ --filter=init,refine
     ```
   - Return list for user selection

**Output**:
```
refine_candidates[N]{name,path,phase}:
  jwt-auth,.claude/plans/jwt-auth/,refine
  new-feature,.claude/plans/new-feature/,init
  ...

prompt: "Select plan to refine:"
```

---

## New Operation: discover-executable

**Purpose**: Find plans in executable phases (implement, verify, finalize).

**Input**: None

**Steps**:

1. Run discovery with filter:
   ```bash
   python3 scripts/discover-plans.py .claude/plans/ --filter=implement,verify,finalize
   ```

2. Format for numbered selection

**Output**:
```
executable_plans[N]{name,path,phase,current_task}:
  jwt-auth,.claude/plans/jwt-auth/,implement,task-3
  migration,.claude/plans/migration/,verify,build-check
  ...

prompt: "Select plan to execute:"
```

---

## Script Updates

### discover-plans.py

**Add `--filter` parameter**:

```python
parser.add_argument(
    '--filter',
    type=str,
    help='Filter by phase or status (comma-separated): init,refine,implement,verify,finalize,completed,in_progress'
)
```

**Filter logic**:

```python
def filter_plans(plans: list, filter_spec: str) -> list:
    if not filter_spec:
        return plans

    filters = [f.strip().lower() for f in filter_spec.split(',')]

    # Phase filters
    phase_filters = {'init', 'refine', 'implement', 'verify', 'finalize'}
    status_filters = {'completed', 'in_progress', 'pending'}

    active_phases = phase_filters & set(filters)
    active_statuses = status_filters & set(filters)

    result = []
    for plan in plans:
        phase_match = not active_phases or plan['phase'] in active_phases
        status_match = not active_statuses or plan['status'] in active_statuses

        if phase_match and status_match:
            result.append(plan)

    return result
```

**Updated output**:

```json
{
  "plans": [...],
  "count": 5,
  "filter_applied": "implement,verify,finalize",
  "filtered_count": 3,
  "recommendation": "jwt-auth"
}
```

---

## Updated SKILL.md Structure

```markdown
## Workflow: Manage Plans (NEW)

Invoked by `/plan-manage` command.

### Input Parameters
- action: list|cleanup|init|refine
- plan_path: (optional)
- task_description: (optional)
- issue_url: (optional)

### Step 1: Route by Action
...

---

## Workflow: Execute Plans (NEW)

Invoked by `/plan-execute` command.

### Input Parameters
- plan_path: (optional)
- explicit_phase: (optional)

### Step 1: Determine Plan
...

---

## Workflow: Orchestrate Task (DEPRECATED)

Kept for backwards compatibility. Will be removed after migration.
Routes to Manage or Execute workflow based on parameters.
```

---

## Migration Notes

1. Keep "Orchestrate Task" workflow temporarily for `/task` compatibility
2. Add deprecation notice in `/task` command
3. After migration period, remove:
   - "Orchestrate Task" workflow
   - `/task` command
   - Legacy routing logic
