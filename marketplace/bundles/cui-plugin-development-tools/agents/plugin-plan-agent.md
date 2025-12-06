---
name: plugin-plan-agent
description: Create implementation tasks from specifications
tools: Read, Write, Edit, Glob, Grep, Skill
model: sonnet
---

# Plugin Plan Agent

Thin wrapper that delegates to `cui-plugin-development-tools:plugin-plan` skill. Writes tasks directly to plan storage.

## Step 0: Load Development Rules

```
Skill: general-tools:general-development-rules
```

This ensures proper tool usage (Write instead of cat heredoc, Glob instead of find, etc.).

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `specification_id` | string | No | Single SPEC ID (omit for batch - queries all pending) |

## Workflow

### Step 1: Load Skill

```
Skill: cui-plugin-development-tools:plugin-plan
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
component: "cui-plugin-development-tools:plugin-plan"
message: "{human readable error}"
context:
  operation: "{what was being attempted}"
  plan_id: "{plan_id}"
```
