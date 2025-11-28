# Phase Management Skill Specification

## Overview

The `phase-management` skill is the **orchestration layer** that coordinates phase execution for both commands:

- **`/plan-manage`** → Manage Plans workflow
- **`/plan-execute`** → Execute Plans workflow

It handles:
1. Plan discovery and selection
2. Phase routing based on plan state
3. Phase transition logic
4. User interaction coordination

**Key Principle**: Orchestration only - delegates all phase work to phase-specific skills.

---

## Skill Identity

```yaml
name: phase-management
bundle: cui-task-workflow
type: skill
workflows:
  - manage-plans      # For /plan-manage
  - execute-plans     # For /plan-execute
operations:
  - list-plans
  - cleanup-plans
  - init-plan
  - refine-plan
  - discover-executable
  - route-phase
  - transition-phase
  - get-status
```

---

## Workflow: Manage Plans

Invoked by `/plan-manage` command. Handles plan lifecycle operations.

### Operations

| Operation | Purpose | Python Script |
|-----------|---------|---------------|
| list-plans | Find and display all plans | `discover-plans.py` |
| cleanup-plans | Find and remove completed plans | `discover-plans.py --filter=completed` |
| init-plan | Create new plan (with existing check) | `discover-plans.py --filter=init` |
| refine-plan | Refine requirements | `discover-plans.py --filter=init,refine` |

### list-plans Operation

**Input**:
```toon
from: plan-manage-command
to: phase-management-skill
handoff_id: list-001

operation: list-plans
```

**Output**:
```toon
from: phase-management-skill
to: plan-manage-command
handoff_id: list-002

plans_found[4]{name,path,phase,status,progress}:
jwt-auth,.claude/plans/jwt-auth/,implement,in_progress,3/12
user-profile,.claude/plans/user-profile/,refine,in_progress,1/3
migration,.claude/plans/migration/,finalize,in_progress,0/2
old-feature,.claude/plans/old-feature/,finalize,completed,2/2

display_format: numbered_list
prompt: "Select plan (number) or action (c/n/q):"
```

### cleanup-plans Operation

**Input**:
```toon
from: plan-manage-command
to: phase-management-skill
handoff_id: cleanup-001

operation: cleanup-plans
```

**Output**:
```toon
from: phase-management-skill
to: plan-manage-command
handoff_id: cleanup-002

completed_plans[2]{name,path,completed_date}:
old-feature,.claude/plans/old-feature/,2024-01-15
api-refactor,.claude/plans/api-refactor/,2024-01-10

prompt: "Select plans to delete (all/numbers/cancel):"
```

### init-plan Operation

**Input**:
```toon
from: plan-manage-command
to: phase-management-skill
handoff_id: init-001

operation: init-plan
task_description: "Implement JWT authentication"
issue_url: "https://github.com/org/repo/issues/123"
```

**Step 1**: Check for existing init-phase plans:
```bash
python3 scripts/discover-plans.py .claude/plans/ --filter=init
```

**Step 2**: If init-phase plans exist, return for selection:
```toon
existing_init_plans[2]{name,path,created}:
draft-feature,.claude/plans/draft-feature/,2024-01-20
wip-api,.claude/plans/wip-api/,2024-01-19

prompt: "Continue with existing or create new? (number/new)"
```

**Step 3**: On selection or new, delegate to plan-init skill:
```toon
delegate_to: plan-init-skill
handoff_id: init-002
```

### refine-plan Operation

**Input**:
```toon
from: plan-manage-command
to: phase-management-skill
handoff_id: refine-001

operation: refine-plan
plan_path: null  # Or specific path
```

**If no plan_path**:
```bash
python3 scripts/discover-plans.py .claude/plans/ --filter=init,refine
```

**Output**:
```toon
refine_candidates[2]{name,path,phase}:
jwt-auth,.claude/plans/jwt-auth/,refine
new-feature,.claude/plans/new-feature/,init

prompt: "Select plan to refine:"
```

---

## Workflow: Execute Plans

Invoked by `/plan-execute` command. Handles execution phases.

### Operations

| Operation | Purpose | Python Script |
|-----------|---------|---------------|
| discover-executable | Find executable plans | `discover-plans.py --filter=implement,verify,finalize` |
| route-phase | Determine target phase skill | `route-phase.py` |
| transition-phase | Handle phase completion | `transition-phase.py` |
| get-status | Return comprehensive plan status | `get-status.py` |

### discover-executable Operation

**Input**:
```toon
from: plan-execute-command
to: phase-management-skill
handoff_id: exec-001

operation: discover-executable
```

**Output**:
```toon
from: phase-management-skill
to: plan-execute-command
handoff_id: exec-002

executable_plans[3]{name,path,phase,current_task}:
jwt-auth,.claude/plans/jwt-auth/,implement,task-7
user-profile,.claude/plans/user-profile/,verify,build-check
migration,.claude/plans/migration/,finalize,commit

prompt: "Select plan to execute:"
```

### route-phase Operation

**Input**:
```toon
from: plan-execute-command
to: phase-management-skill
handoff_id: route-001

operation: route-phase
plan_directory: .claude/plans/jwt-auth/
explicit_phase: null  # Or override
```

**Validation**:
- If current phase is `init` or `refine`, return error:
```toon
error:
  type: phase_not_executable
  message: "Plan is in 'init' phase - use /plan-manage"
```

**Output**:
```toon
from: phase-management-skill
to: plan-execute-command
handoff_id: route-002

routing:
  plan_directory: .claude/plans/jwt-auth/
  current_phase: implement
  current_task: task-7
  target_skill: plan-implement

phase_status:
  completed_phases[2]: init, refine
  current_phase: implement
  pending_phases[2]: verify, finalize

tasks_remaining: 5
```

**Routing Logic**:
```python
def route_phase(plan_directory, explicit_phase=None):
    plan = plan_files.read_plan(plan_directory)

    # Validate executable phase
    if plan.current_phase in ['init', 'refine']:
        return error("Use /plan-manage for init/refine phases")

    if explicit_phase:
        if not can_execute_phase(plan, explicit_phase):
            return error("Cannot skip to phase")
        target_phase = explicit_phase
    else:
        target_phase = plan.current_phase

    skill_map = {
        'implement': 'plan-implement',
        'verify': 'plan-verify',
        'finalize': 'plan-finalize'
    }

    return {
        'target_skill': skill_map[target_phase],
        'current_phase': target_phase,
        'plan_directory': plan_directory
    }
```

### transition-phase Operation

**Input**:
```toon
from: phase-skill
to: phase-management-skill
handoff_id: transition-001

operation: transition-phase
plan_directory: .claude/plans/jwt-auth/
completed_phase: implement
```

**Output**:
```toon
from: phase-management-skill
to: phase-skill
handoff_id: transition-002

transition:
  from_phase: implement
  to_phase: verify
  success: true

plan_status:
  current_phase: verify
  current_task: task-11
  overall_progress: 60%

next_action: Execute verify phase tasks
```

**Transition Rules**:
```python
PHASE_ORDER = ['init', 'refine', 'implement', 'verify', 'finalize']

def transition_phase(plan_directory, completed_phase):
    plan = plan_files.read_plan(plan_directory)
    if not all_tasks_complete(plan, completed_phase):
        return error("Cannot transition - tasks incomplete")

    current_index = PHASE_ORDER.index(completed_phase)
    if current_index == len(PHASE_ORDER) - 1:
        return plan_complete(plan_directory)

    next_phase = PHASE_ORDER[current_index + 1]

    plan_files.update_progress(plan_directory, {
        'phase_status': {completed_phase: 'completed', next_phase: 'in_progress'},
        'current_phase': next_phase,
        'current_task': first_task_of(next_phase)
    })

    return success(next_phase)
```

### get-status Operation

**Input**:
```toon
from: command
to: phase-management-skill
handoff_id: status-001

operation: get-status
plan_directory: .claude/plans/jwt-auth/
```

**Output**:
```toon
from: phase-management-skill
to: command
handoff_id: status-002

plan_status:
  name: jwt-auth
  plan_type: implementation
  overall_status: in_progress
  overall_progress: 65%

phase_progress[5]{phase,status,tasks,completed}:
init,completed,5,5/5
refine,completed,3,3/3
implement,in_progress,7,5/7
verify,pending,4,0/4
finalize,pending,3,0/3

current_focus:
  phase: implement
  task: task-12
  task_name: "Implement RefreshTokenService"
```

---

## Skill Structure

```
cui-task-workflow/
└── skills/
    └── phase-management/
        ├── SKILL.md              # Skill definition with both workflows
        ├── standards/
        │   ├── orchestration.md  # Orchestration patterns
        │   └── transitions.md    # Phase transition rules
        ├── scripts/
        │   ├── discover-plans.py # With --filter support
        │   ├── route-phase.py
        │   ├── transition-phase.py
        │   └── get-status.py
        └── README.md
```

---

## Integration Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        COMMANDS                                  │
│                                                                  │
│   /plan-manage                        /plan-execute              │
│   ┌─────────────────────┐            ┌─────────────────────┐    │
│   │ list, cleanup,      │            │ execute implement/   │    │
│   │ init, refine        │            │ verify/finalize      │    │
│   └──────────┬──────────┘            └──────────┬──────────┘    │
└──────────────┼───────────────────────────────────┼───────────────┘
               │                                   │
               │ Manage Plans workflow             │ Execute Plans workflow
               │                                   │
               ▼                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    phase-management skill                        │
│                                                                  │
│  ┌─────────────────────────┐    ┌─────────────────────────┐    │
│  │ Manage Plans            │    │ Execute Plans           │    │
│  │ • list-plans            │    │ • discover-executable   │    │
│  │ • cleanup-plans         │    │ • route-phase           │    │
│  │ • init-plan             │    │ • transition-phase      │    │
│  │ • refine-plan           │    │ • get-status            │    │
│  └────────────┬────────────┘    └────────────┬────────────┘    │
└───────────────┼───────────────────────────────┼─────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Phase Skills                                │
│                                                                  │
│  plan-init  plan-refine  plan-implement  plan-verify  plan-final│
│      │           │            │              │            │      │
└──────┼───────────┼────────────┼──────────────┼────────────┼──────┘
       │           │            │              │            │
       └───────────┴────────────┴──────────────┴────────────┘
                                │
                                ▼
                          plan-files (persistence)
```

---

## Error Handling

### Plan Not Found

```toon
error:
  type: plan_not_found
  message: No plans found in .claude/plans/

suggestion: Create a new plan with /plan-manage action=init task="description"
```

### No Executable Plans

```toon
error:
  type: no_executable_plans
  message: No plans ready for execution

details: All plans are in init/refine phases or completed

suggestion: Use /plan-manage to create or refine plans
```

### Phase Not Executable

```toon
error:
  type: phase_not_executable
  message: Plan 'jwt-auth' is in 'init' phase

details: This command handles execution phases only (implement, verify, finalize)

suggestion: Use /plan-manage to complete init/refine phases first
```

### Invalid Phase Transition

```toon
error:
  type: invalid_transition
  message: Cannot transition from 'implement' to 'finalize'
  reason: 'verify' phase not completed

current_state:
  phase: implement
  tasks_remaining: 2

suggestion: Complete remaining implement tasks first
```

### Incomplete Phase

```toon
error:
  type: incomplete_phase
  message: Phase 'implement' has incomplete tasks

incomplete_tasks[2]{id,name}:
task-12,Implement RefreshTokenService
task-13,Add configuration properties

suggestion: Complete tasks or mark as skipped
```

---

## Related Documents

- [Architecture](architecture.md) - Two-command architecture design
- [API Specification](api.md) - Complete skill API
- [Migration Plan](updated-plan/migration.md) - Implementation checklist

**Command Specifications**:
- [plan-manage.md](updated-plan/plan-manage.md)
- [plan-execute.md](updated-plan/plan-execute.md)

**Implemented Skills** (in `cui-task-workflow/skills/`):
- `phase-management` (this skill)
- `plan-init`, `plan-refine`, `plan-implement`, `plan-verify`, `plan-finalize`, `plan-files`
