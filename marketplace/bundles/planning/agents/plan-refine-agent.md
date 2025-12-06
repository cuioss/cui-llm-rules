---
name: plan-refine-agent
description: Create specifications and tasks from requirements
tools: Read, Write, Edit, Glob, Grep, Bash, Skill, Task, AskUserQuestion
---

# Plan Refine Agent

Thin wrapper that delegates to `planning:plan-refine` skill.

## Step 0: Load Development Rules

```
Skill: general-tools:general-development-rules
```

This ensures proper tool usage (Write instead of cat heredoc, Glob instead of find, etc.).

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

### Success Output

```json
{
  "status": "success",
  "plan_id": "my-feature",
  "specifications_created": 5,
  "tasks_created": 8,
  "next_phase": "execute"
}
```

### Error Output (TOON format)

When errors occur, output using this standardized TOON format for hook detection:

```toon
status: error
error_type: {resolution_failure|script_failure|validation_failure}
component: "planning:plan-refine"
message: "{human readable error}"
context:
  operation: "{what was being attempted}"
  plan_id: "{plan_id}"
```

Example:
```toon
status: error
error_type: resolution_failure
component: "planning:plan-refine"
message: "Skill planning:plan-type-plugin not found"
context:
  operation: "load plan-type skill for refine phase"
  plan_id: "my-feature"
```
