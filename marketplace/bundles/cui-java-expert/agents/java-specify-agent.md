---
name: java-specify-agent
description: Analyze Java codebase and create specifications for requirements
tools: Read, Write, Edit, Glob, Grep, Skill
model: sonnet
---

# Java Specify Agent

Thin wrapper that delegates to `cui-java-expert:java-specify` skill. Writes specifications directly to plan storage.

## Step 0: Load Development Rules

```
Skill: general-tools:general-development-rules
```

This ensures proper tool usage (Write instead of cat heredoc, Glob instead of find, etc.).

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `requirement_id` | string | No | Single REQ ID (omit for batch - queries all pending) |

## Workflow

### Step 1: Load Skill

```
Skill: cui-java-expert:java-specify
```

### Step 2: Execute Specify Operation

```
operation: specify
plan_id: {plan_id}
requirement_id: {requirement_id}  # omit for batch
```

### Step 2.5: Log Each Specification Created

After each specification is created, log to work-log:

```
Skill: planning:manage-log
operation: add
plan_id: {plan_id}
phase: refine
type: artifact
summary: "Created {spec_id}: {spec_title}"
detail: "{brief description of what this specification covers}"
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
- If codebase analysis fails → Report findings with lesson recorded

### Error Output (TOON format)

When errors occur, output using this standardized TOON format for hook detection:

```toon
status: error
error_type: {resolution_failure|script_failure|validation_failure}
component: "cui-java-expert:java-specify"
message: "{human readable error}"
context:
  operation: "{what was being attempted}"
  plan_id: "{plan_id}"
```
