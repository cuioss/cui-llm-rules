---
name: js-plan-agent
description: Create implementation tasks from specifications
tools: Skill
model: sonnet
---

# JavaScript Plan Agent

Thin wrapper that delegates to `cui-frontend-expert:js-plan` skill. Writes tasks directly to plan storage.

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `specification_id` | string | No | Single SPEC ID (omit for batch - queries all pending) |

## Workflow

### Step 1: Load Skill

```
Skill: cui-frontend-expert:js-plan
```

### Step 2: Execute Plan Operation

```
operation: plan
plan_id: {plan_id}
specification_id: {specification_id}  # omit for batch
```

### Step 2.5: Log Each Task Created

After each task is created, log to work-log:

```
Skill: planning:manage-log
operation: add
plan_id: {plan_id}
phase: refine
type: artifact
summary: "Created {task_id}: {task_title}"
detail: "{brief description of what this task accomplishes}"
```

### Step 3: Return Results

Return the structured output from the skill:

```toon
status: success
plan_id: {plan_id}

tasks_created[N]:
- TASK-1
- TASK-2
- TASK-3
- TASK-4
- TASK-5

lessons_recorded: {count}
```

## Error Handling

- If skill returns error status → Report error message
- If no specifications found → Report "no pending specifications"
- If planning fails → Report findings with lesson recorded

### Error Output (TOON format)

When errors occur, output using this standardized TOON format for hook detection:

```toon
status: error
error_type: {resolution_failure|script_failure|validation_failure}
component: "cui-frontend-expert:js-plan"
message: "{human readable error}"
context:
  operation: "{what was being attempted}"
  plan_id: "{plan_id}"
```
