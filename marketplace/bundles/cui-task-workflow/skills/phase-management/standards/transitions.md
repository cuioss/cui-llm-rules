# Phase Transition Rules

Standards for phase transitions in plan-based workflows.

## Phase Order by Plan Type

Phase sequences vary by plan type. All follow strict sequential order.

### Implementation Plan (5 phases)

```
init → refine → implement → verify → finalize → [complete]
```

Used for: Feature implementations, bug fixes with code changes, GitHub issues.

### Plugin-Development Plan (4 phases)

```
init → refine → execute → finalize → [complete]
```

Used for: Marketplace components (skills, commands, agents), documentation updates.

### Simple Plan (3 phases)

```
init → execute → finalize → [complete]
```

Used for: Quick tasks, documentation-only changes, configuration updates.

## Phase Definitions

| Phase | Purpose | Plan Types | Completion Criteria |
|-------|---------|------------|---------------------|
| init | Create plan, detect environment | All | All init tasks complete |
| refine | Analyze requirements, plan tasks | Implementation, Plugin-Development | All refine tasks complete |
| implement | Execute implementation tasks | Implementation only | All implement tasks complete |
| execute | Execute tasks (no verify step) | Plugin-Development, Simple | All execute tasks complete |
| verify | Build, test, quality checks | Implementation only | All verify tasks complete |
| finalize | Commit, PR, documentation | All | All finalize tasks complete |

**Note**: `implement` and `execute` serve similar purposes but differ in workflow:
- `implement` → followed by `verify` (separate verification phase)
- `execute` → directly to `finalize` (verification inline)

## Transition Rules

### Rule 1: Sequential Only (Plan-Type Aware)

Phases can only transition to the next phase in the plan type's sequence.

**Implementation Plan Transitions**:
- init → refine → implement → verify → finalize → [complete]

**Plugin-Development Plan Transitions**:
- init → refine → execute → finalize → [complete]

**Simple Plan Transitions**:
- init → execute → finalize → [complete]

**NOT Allowed** (examples):
- init → implement (skipping refine, except Simple plans)
- refine → verify (skipping implement/execute)
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

## Script Implementation

The `transition-phase.py` script implements these rules with plan-type awareness:

```python
PHASE_ORDERS = {
    'implementation': ['init', 'refine', 'implement', 'verify', 'finalize'],
    'plugin-development': ['init', 'refine', 'execute', 'finalize'],
    'simple': ['init', 'execute', 'finalize']
}

def get_next_phase(plan_type, completed_phase):
    """Get next phase in sequence for plan type."""
    phase_order = PHASE_ORDERS.get(plan_type, PHASE_ORDERS['implementation'])
    try:
        index = phase_order.index(completed_phase)
        if index == len(phase_order) - 1:
            return None  # Plan complete
        return phase_order[index + 1]
    except ValueError:
        return None  # Invalid phase

def validate_transition(plan_type, current_phase, completed_phase):
    """Validate transition is allowed for plan type."""
    phase_order = PHASE_ORDERS.get(plan_type, PHASE_ORDERS['implementation'])
    if current_phase != completed_phase:
        return False, "Can only complete current phase"
    if completed_phase not in phase_order:
        return False, f"Phase '{completed_phase}' not valid for {plan_type} plan"
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
