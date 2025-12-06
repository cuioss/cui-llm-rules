---
name: plan-init-agent
description: Initialize a plan from description, lesson, or issue
tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Init Agent

Thin wrapper that delegates to `planning:plan-init` skill.

## Parameters

- **description** (optional): Task description text
- **lesson_id** (optional): Lesson learned ID (e.g., "2025-12-02-001")
- **issue** (optional): GitHub issue URL or identifier

## Workflow

Invoke skill with parameters:

```
Skill: planning:plan-init
operation: create
description: {description if provided}
lesson_id: {lesson_id if provided}
issue: {issue if provided}
```

Return the skill output as agent result.

## Output

### Success Output

```json
{
  "status": "success",
  "plan_id": "my-feature",
  "source": {"type": "description|lesson|issue", "id": "..."}
}
```

### Error Output (TOON format)

When errors occur, output using this standardized TOON format for hook detection:

```toon
status: error
error_type: {resolution_failure|script_failure|validation_failure}
component: "planning:plan-init"
message: "{human readable error}"
context:
  operation: "{what was being attempted}"
  plan_id: "{plan_id if known}"
```

Example:
```toon
status: error
error_type: resolution_failure
component: "planning:plan-init"
message: "Skill planning:plan-init not found"
context:
  operation: "load plan-init skill"
```
