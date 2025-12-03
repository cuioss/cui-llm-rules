---
name: plan-init-agent
description: Initialize a plan from description, lesson, or issue
tools: Skill
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

```json
{
  "status": "success|failed",
  "plan_id": "my-feature",
  "source": {"type": "description|lesson|issue", "id": "..."}
}
```
