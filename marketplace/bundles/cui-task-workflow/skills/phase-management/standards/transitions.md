# Phase Transition Rules

Standards for phase transitions in plan-based workflows.

## Phase Order

Phases must be completed in strict sequential order:

```
init → refine → implement → verify → finalize → [complete]
```

## Phase Definitions

| Phase | Index | Purpose | Completion Criteria |
|-------|-------|---------|---------------------|
| init | 0 | Create plan, detect environment | All init tasks complete |
| refine | 1 | Analyze requirements, plan tasks | All refine tasks complete |
| implement | 2 | Execute implementation tasks | All implement tasks complete |
| verify | 3 | Build, test, quality checks | All verify tasks complete |
| finalize | 4 | Commit, PR, documentation | All finalize tasks complete |

## Transition Rules

### Rule 1: Sequential Only

Phases can only transition to the next phase in sequence.

**Allowed**:
- init → refine
- refine → implement
- implement → verify
- verify → finalize
- finalize → [complete]

**NOT Allowed**:
- init → implement (skipping refine)
- refine → verify (skipping implement)
- Any backward transition

### Rule 2: Completion Required

A phase can only transition when ALL tasks in that phase are marked complete (`[x]`).

**Validation**:
```python
def can_transition(plan, completed_phase):
    phase_tasks = get_tasks_for_phase(plan, completed_phase)
    return all(task.status == 'completed' for task in phase_tasks)
```

### Rule 3: No Skipping

Explicit phase override requests are validated:

- Override to **current phase** → Allowed (resume)
- Override to **next phase** → Allowed only if current complete
- Override to **future phase** → NOT Allowed (error)
- Override to **past phase** → NOT Allowed (error)

### Rule 4: Plan Completion

After finalize phase completes:
- Plan status → `completed`
- No further transitions
- Archive or close plan

## Phase Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Phase not yet started |
| `in_progress` | Phase is active |
| `completed` | All tasks complete |

## Transition Validation

### Pre-Transition Checks

1. **Phase exists** in plan
2. **All tasks complete** in completed phase
3. **Next phase exists** (not after finalize)
4. **Plan not already complete**

### Post-Transition Updates

1. Update `current_phase` to next phase
2. Update `current_task` to first task of new phase
3. Mark completed phase status as `completed`
4. Mark new phase status as `in_progress`
5. Update Phase Progress Table

## Error Cases

### Incomplete Phase

```json
{
  "error": "incomplete_phase",
  "message": "Cannot transition - tasks incomplete",
  "phase": "implement",
  "incomplete_tasks": ["task-7", "task-8"],
  "total_tasks": 10,
  "completed_tasks": 8
}
```

### Invalid Skip

```json
{
  "error": "invalid_skip",
  "message": "Cannot skip from 'init' to 'implement'",
  "current_phase": "init",
  "requested_phase": "implement",
  "next_valid_phase": "refine"
}
```

### Plan Already Complete

```json
{
  "error": "plan_complete",
  "message": "Plan already completed - no further transitions",
  "plan_status": "completed"
}
```

## Simple Plan Type

Simple plans have fewer phases:

```
init → execute → finalize → [complete]
```

Transition rules still apply - sequential order, completion required.

## Script Implementation

The `transition-phase.py` script implements these rules:

```python
PHASE_ORDER = ['init', 'refine', 'implement', 'verify', 'finalize']

def get_next_phase(completed_phase):
    """Get next phase in sequence."""
    try:
        index = PHASE_ORDER.index(completed_phase)
        if index == len(PHASE_ORDER) - 1:
            return None  # Plan complete
        return PHASE_ORDER[index + 1]
    except ValueError:
        return None  # Invalid phase

def validate_transition(current_phase, completed_phase):
    """Validate transition is allowed."""
    if current_phase != completed_phase:
        return False, "Can only complete current phase"
    return True, None
```

## Integration with plan-files

After transition validation:

```markdown
Skill: cui-task-workflow:plan-files
operation: update-progress
plan_directory: {path}
task_id: {last-task-of-completed-phase}
status: completed
```

This triggers:
- Phase Progress Table update
- current_phase update
- current_task update
