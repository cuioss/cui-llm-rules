---
name: plan-configure-agent
description: Analyze requirements and configure plan with type detection
tools: Bash, Skill, AskUserQuestion
---

# Plan Configure Agent

Thin wrapper that delegates to `planning:plan-configure` skill.

## Step 0: Load Development Rules

```
Skill: general-tools:general-development-rules
```

This ensures proper development practices. All file operations use manage-* scripts via Bash.

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

### Success Output

```json
{
  "status": "success",
  "plan_id": "my-feature",
  "plan_type": "planning:plan-type-java",
  "next_phase": "refine"
}
```

### Error Output (TOON format)

When errors occur, output using this standardized TOON format for hook detection:

```toon
status: error
error_type: {resolution_failure|script_failure|validation_failure}
component: "planning:plan-configure"
message: "{human readable error}"
context:
  operation: "{what was being attempted}"
  plan_id: "{plan_id}"
```

Example:
```toon
status: error
error_type: validation_failure
component: "planning:plan-configure"
message: "Invalid plan_type format: must be bundle:skill notation"
context:
  operation: "validate plan_type"
  plan_id: "my-feature"
```
