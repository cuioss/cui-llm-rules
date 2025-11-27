# plan-refine Handoff Protocol

**Purpose**: External interface specifications for the refine phase skill

**Scope**: Phase transitions, orchestrator communication, error patterns only. Internal delegations are documented in the main specification.

---

## Incoming Handoffs

### From: Orchestrator (Start Refine)

```toon
from: orchestrator
to: plan-refine-skill
handoff_id: refine-001
workflow: requirements-analysis

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Analyze requirements and plan tasks
```

### From: plan-init (Phase Transition)

```toon
from: plan-init-skill
to: plan-refine-skill
handoff_id: transition-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

plan_status:
  previous_phase: init
  current_phase: refine
  current_task: task-1

configuration:
  technology: java
  build_system: maven
  issue_url: https://github.com/org/repo/issues/123

next_action: Begin requirements analysis
```

### From: User (Component Confirmation)

```toon
from: user-interaction
to: plan-refine-skill
handoff_id: user-001

response:
  selection: 1|2|3
  details: [optional modification details]

context:
  prompt_type: component_analysis
```

### From: User (Task Review)

```toon
from: user-interaction
to: plan-refine-skill
handoff_id: user-002

response:
  selection: 1|2|3|4
  task_number: [if viewing details]
  modifications: [if modifying]

context:
  prompt_type: task_review
```

### From: User (Documentation Decision)

```toon
from: user-interaction
to: plan-refine-skill
handoff_id: user-003

response:
  selection: 1|2|3
  adr_identifier: ADR-015
  interface_identifier: IF-042

context:
  prompt_type: adr_decision|interface_decision
```

---

## Outgoing Handoffs

### Phase Complete → Implement Phase

```toon
from: plan-refine-skill
to: plan-implement-skill
handoff_id: transition-002

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  implementation_requirements: .claude/plans/jwt-auth/implementation-requirements.md

plan_status:
  previous_phase: refine
  current_phase: implement
  current_task: task-6

implementation_tasks[5]{id,name,complexity}:
task-6,Create JwtService,medium
task-7,Create TokenValidator,medium
task-8,Implement RefreshTokenService,high
task-9,Add JWT configuration,low
task-10,Update POM dependencies,low

documentation_needs:
  adrs_created[1]: "ADR-015"
  interfaces_created[1]: "IF-042"

next_action: Begin task execution
```

### To: Orchestrator (Refine Complete)

```toon
from: plan-refine-skill
to: orchestrator
handoff_id: refine-002
workflow: requirements-analysis

task:
  description: Requirements analyzed
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  implementation_requirements: .claude/plans/jwt-auth/implementation-requirements.md

implementation_tasks[5]{id,name,complexity}:
task-6,Create JwtService,medium
task-7,Create TokenValidator,medium
task-8,Implement RefreshTokenService,high
task-9,Add JWT configuration,low
task-10,Update POM dependencies,low

next_action: Transition to implement phase
```

---

## Error Handoffs

### Error: Missing Issue Content

```toon
from: plan-refine-skill
to: caller
handoff_id: error-001

task:
  status: blocked

error:
  type: missing_issue_content
  message: Issue URL provided but content could not be fetched
  details: GitHub API timeout

alternatives[3]:
- Retry fetching issue
- Enter issue details manually
- Proceed without issue content
```

### Error: Invalid References

```toon
from: plan-refine-skill
to: caller
handoff_id: error-002

task:
  status: blocked

error:
  type: invalid_references
  message: Reference validation failed
  details[2]:
  - ADR-015: Not found
  - IF-042: File exists but format invalid

alternatives[3]:
- Create missing ADR (ADR-015)
- Remove invalid references
- Proceed anyway (mark as TODO)
```

### Error: Incomplete Analysis

```toon
from: plan-refine-skill
to: caller
handoff_id: error-003

task:
  status: blocked

error:
  type: incomplete_analysis
  message: Analysis incomplete - some components unclear
  details: Component B: Scope undefined

alternatives[3]:
- Define scope for Component B
- Remove Component B from plan
- Mark as TODO for later refinement
```

---

## Related

- [Refine Specification](refine.md) - Full workflow specification (includes internal delegations)
- [Implementation Requirements Template](implementation-requirements-template.md) - Runtime artifact template
- [Plan Types](../plan-types.md) - Init phase router
