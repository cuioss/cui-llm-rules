---
name: plan-configure-agent
description: Analyze requirements and configure plan with type detection
tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Configure Agent

Thin wrapper that delegates to `planning:plan-configure` skill.

## Parameters

- **plan_id** (required): Plan identifier
- **plan_type** (optional): Override auto-detection (bundle:skill notation, e.g., planning:plan-type-java)

## Workflow

Invoke skill with parameters:

```
Skill: planning:plan-configure
operation: configure
plan_id: {plan_id}
plan_type: {plan_type if provided}
```

Return the skill output as agent result.

## Output

```json
{
  "status": "success|failed",
  "plan_id": "my-feature",
  "plan_type": "planning:plan-type-java",
  "next_phase": "refine"
}
```
