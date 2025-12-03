---
name: java-plan-agent
description: Create implementation tasks from specifications
tools: Skill
model: sonnet
---

# Java Plan Agent

Thin wrapper that delegates to `cui-java-expert:java-plan` skill. Writes tasks directly to plan storage.

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `specification_id` | string | No | Single SPEC ID (omit for batch - queries all pending) |

## Workflow

### Step 1: Load Skill

```
Skill: cui-java-expert:java-plan
```

### Step 2: Execute Plan Operation

```
operation: plan
plan_id: {plan_id}
specification_id: {specification_id}  # omit for batch
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
