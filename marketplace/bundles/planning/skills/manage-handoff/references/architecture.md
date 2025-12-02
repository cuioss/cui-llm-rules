# Handoff Architecture

This document covers the architectural patterns and interaction flows for the handoff system.

## Orchestrator Interaction Pattern

Handoffs travel through an orchestrator that makes routing decisions based on status and alternatives:

```
┌─────────────┐                              ┌─────────────────────┐
│  Phase A    │ ─── save(handoff) ─────────► │  .plan/memory/      │
│  (init)     │                              │  handoffs/          │
└─────────────┘                              └─────────────────────┘
       │
       │ returns handoff (small)
       ▼
┌─────────────┐
│ Orchestrator│ ◄── receives handoff directly
│             │     (status, next_action, plan_id)
└─────────────┘
       │
       │ passes handoff to next phase
       ▼
┌─────────────┐     load(plan_id)      ┌─────────────────────┐
│  Phase B    │ ◄───────────────────── │  .plan/plans/       │
│ (configure) │     (large context)    │  jwt-auth/          │
└─────────────┘                        └─────────────────────┘
```

The orchestrator receives the handoff content to make routing decisions (check status, read alternatives, determine next phase). Large context is loaded on-demand by the receiving phase using `plan_id`.

## Use Cases

### User Interaction

Capturing user decisions for workflow branching:

```toon
from: user-interaction
to: plan-refine-skill
handoff_id: user-001

response:
  selection: 1
  details: Use JWT with 24h expiry

context:
  prompt_type: technology_decision
```

### Build Verification Loop

Handoffs between build tools and fix agents with iteration tracking:

```toon
from: build-verify-agent
to: java-fix-build-agent
handoff_id: fix-001
iteration: 1

errors[1]{file,line,message}:
src/auth/JwtService.java,42,cannot find symbol: class Algorithm

context:
  max_iterations: 3
  current_iteration: 1
```

### Cross-Bundle Communication

Handoffs between orchestration and language-specific bundles:

```toon
from: task-implement-command
to: java-implement-agent
handoff_id: implement-001

task:
  description: Implement JWT authentication
  status: pending

plan_id: jwt-auth
task_id: task-6
requirements: REQ-1, REQ-2
```

## Integration Example: Requirements Skill

The requirements skill outputs can be handoff-compatible:

```toon
from: plan-requirements-skill
to: plan-configure-agent
timestamp: 2025-12-02T10:30:00Z

status: success
plan_id: my-feature

task:
  description: Requirements analysis
  status: completed
  progress: 100

counts:
  total: 3
  pending: 3
  done: 0

requirements[3]{number,title,status}:
1,Implement user auth,pending
2,Add session management,pending
3,Create logout flow,pending

next_action: Configure plan type
next_focus: Determine technology from requirements
```

## Benefits

| Benefit | Description |
|---------|-------------|
| Token efficiency | TOON format saves 30-60% vs JSON |
| Structured protocol | Consistent handoff structure across all components |
| Progress tracking | Task status and percentage |
| Error handling | Structured errors with alternatives |
| Traceability | from/to/plan_id fields for debugging |
| Recovery | Persisted handoffs enable session resumption |
| Type safety | Validation of required fields |

## Related

- [protocol.md](../standards/protocol.md) - Full protocol specification
- [Templates](../templates/) - Phase transition, error, and completion templates
