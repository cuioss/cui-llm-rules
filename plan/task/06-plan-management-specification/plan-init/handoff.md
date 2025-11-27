# plan-init Handoff Protocol

**Scope**: Phase transitions, orchestrator communication, error patterns only. Internal delegations are documented in the main specification.

---

## Incoming Handoffs

### From: Command / Orchestrator

```toon
from: orchestrator|task-plan-command
to: plan-init-skill
handoff_id: init-001

task:
  description: Create new task plan
  status: pending

context:
  plan_type: implementation|simple
  task_name: jwt-auth
  issue_url: https://github.com/org/repo/issues/123
  branch: feature/jwt-auth

next_action: Initialize plan with configuration
```

### From: User (Configuration Edit)

```toon
from: user-interaction
to: plan-init-skill
handoff_id: edit-001

edit_request:
  property: technology|build_system|compatibility|commit_strategy|finalizing
  new_value: [selected value]
```

---

## Outgoing Handoffs

### Phase Complete → Refine Phase

```toon
from: plan-init-skill
to: plan-refine-skill
handoff_id: transition-001

plan_type: implementation

artifacts:
  plan_directory: .claude/plans/jwt-auth/

plan_status:
  previous_phase: init
  current_phase: refine
  current_task: task-1

configuration:
  technology: java
  build_system: maven
  compatibility: deprecations
  commit_strategy: fine-granular
  finalizing: pr-workflow

next_action: Begin requirement analysis
```

### Phase Complete → Execute Phase (Simple)

```toon
from: plan-init-skill
to: plan-execute-skill
handoff_id: transition-002

plan_type: simple

artifacts:
  plan_directory: .claude/plans/quick-fix/

plan_status:
  previous_phase: init
  current_phase: execute
  current_task: task-1

configuration:
  technology: none
  build_system: none
  finalizing: commit-only

next_action: Begin task execution
```

---

## Error Handoffs

### Branch Validation Failed

```toon
from: plan-init-skill
to: caller
handoff_id: error-001

task:
  status: failed

error:
  type: branch_validation_failed
  message: Cannot use main branch for implementation plan

alternatives[2]:
- Create feature branch first
- Switch to simple plan type
```

### Configuration Invalid

```toon
from: plan-init-skill
to: caller
handoff_id: error-002

task:
  status: failed

error:
  type: configuration_invalid
  message: Invalid configuration combination
  details: Cannot use pr-workflow finalizing without a feature branch

alternatives[2]:
- Change finalizing to commit-only
- Switch to a feature branch
```

---

## Related

- [Implementation Init](implementation.md) - Full workflow specification (includes internal delegations)
- [Simple Init](simple.md) - Lightweight workflow specification
- [Plan Types](../plan-types.md) - Init phase router
