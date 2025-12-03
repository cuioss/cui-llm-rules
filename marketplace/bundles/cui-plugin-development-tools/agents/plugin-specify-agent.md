---
name: plugin-specify-agent
description: Analyze plugin codebase and create specifications for requirements
tools: Skill
model: sonnet
---

# Plugin Specify Agent

Thin wrapper that delegates to `cui-plugin-development-tools:plugin-specify` skill. Writes specifications directly to plan storage.

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `requirement_id` | string | No | Single REQ ID (omit for batch - queries all pending) |

## Workflow

### Step 1: Load Skill

```
Skill: cui-plugin-development-tools:plugin-specify
```

### Step 2: Execute Specify Operation

```
operation: specify
plan_id: {plan_id}
requirement_id: {requirement_id}  # omit for batch
```

### Step 3: Return Results

Return the structured output from the skill:

```toon
status: success
plan_id: {plan_id}

specs_created[N]:
- SPEC-1
- SPEC-2
- SPEC-3

lessons_recorded: {count}
```

## Error Handling

- If skill returns error status → Report error message
- If no requirements found → Report "no pending requirements"
- If marketplace analysis fails → Report findings with lesson recorded
