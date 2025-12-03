---
name: plan-refine-agent
description: Create specifications and tasks from requirements
tools: Skill
---

# Plan Refine Agent

Thin wrapper that delegates to `planning:plan-refine` skill.

## Parameters

- **plan_id** (required): Plan identifier

## Workflow

Invoke skill with parameters:

```
Skill: planning:plan-refine
operation: refine
plan_id: {plan_id}
```

Return the skill output as agent result.

## Output

```json
{
  "status": "success|failed",
  "plan_id": "my-feature",
  "specifications_created": 5,
  "tasks_created": 8,
  "next_phase": "execute"
}
```
