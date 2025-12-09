# Task File Format Specification

This document defines the TOON format for task files in the plan-task-manager skill.

## File Naming Convention

```
TASK-{NNN}-{slug}.toon
```

- `{NNN}`: Zero-padded 3-digit number (001, 002, etc.)
- `{slug}`: Kebab-case derived from title (max 40 characters)

Examples:
- `TASK-001-implement-jwt-service.toon`
- `TASK-002-add-auth-endpoint.toon`
- `TASK-015-write-integration-tests.toon`

## File Structure

```toon
number: {integer}
title: {string}
status: {task_status}
specification: SPEC-{n}
created: {iso_timestamp}
updated: {iso_timestamp}

description: |
  {multiline_text}

steps[{count}]{number,title,status}:
{step_number},{step_title},{step_status}
...

current_step: {integer}
```

## Field Definitions

### number
- Type: Integer
- Required: Yes
- Description: Unique task identifier within the plan
- Constraints: Positive integer, assigned at creation, immutable
- Example: `number: 1`

### title
- Type: String
- Required: Yes
- Description: Short descriptive title for the task
- Constraints: Non-empty, used to generate filename slug
- Example: `title: Implement JWT Service`

### status
- Type: Enum
- Required: Yes
- Description: Current state of the task
- Values: `pending`, `in_progress`, `done`, `blocked`
- Example: `status: in_progress`

### goal
- Type: String (GOAL reference)
- Required: Yes
- Description: The goal this task implements
- Format: `GOAL-{n}` where n is a positive integer
- Example: `goal: GOAL-1`

### created
- Type: ISO 8601 timestamp
- Required: Yes
- Description: When the task was created
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `created: 2025-12-02T10:30:00Z`

### updated
- Type: ISO 8601 timestamp
- Required: Yes
- Description: When the task was last modified
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `updated: 2025-12-02T11:00:00Z`

### description
- Type: Multiline string
- Required: Yes
- Description: Detailed description of what the task entails
- Format: YAML-style block scalar with `|` indicator
- Example:
  ```toon
  description: |
    Create the JWT service class with token generation
    and validation methods.
  ```

### steps
- Type: Uniform array
- Required: Yes
- Description: Ordered list of steps to complete the task
- Format: `steps[{count}]{number,title,status}:` followed by CSV rows
- Constraints: At least one step required

### current_step
- Type: Integer
- Required: Yes
- Description: The step number currently being executed
- Constraints: 1 <= current_step <= step_count
- Example: `current_step: 2`

## Status Values

### Task Status

| Value | Description |
|-------|-------------|
| `pending` | Task has not been started |
| `in_progress` | Task is currently being worked on |
| `done` | All steps are completed or skipped |
| `blocked` | Task cannot proceed due to dependency or issue |

### Step Status

| Value | Description |
|-------|-------------|
| `pending` | Step has not been started |
| `in_progress` | Step is currently being executed |
| `done` | Step has been completed successfully |
| `skipped` | Step was intentionally skipped |

## Example File

```toon
number: 2
title: Add Auth Endpoint
status: in_progress
goal: GOAL-1
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T11:00:00Z

description: |
  Create REST endpoint for user authentication.
  Endpoint should accept username/password and
  return JWT token on successful auth.

steps[3]{number,title,status}:
1,Create AuthController class,done
2,Add request/response DTOs,in_progress
3,Write integration tests,pending

current_step: 2
```

## Numbering Rules

### Task Numbers
- Assigned incrementally (next available number)
- Numbers are immutable once assigned
- Removing a task creates a gap (numbers are not reused)
- References use `TASK-{n}` format (without zero-padding)

### Step Numbers
- Numbered 1 to N within each task
- Renumbered when steps are added or removed
- Always sequential (no gaps)

## State Transitions

### Task State Machine

```
pending ──► in_progress ──► done
   │             │
   │             ▼
   └──────► blocked
```

### Step State Machine

```
pending ──► in_progress ──► done
   │
   └──────► skipped
```

## Validation Rules

1. `specification` must match pattern `SPEC-{n}`
2. At least one step is required
3. `current_step` must be within valid step range
4. Task `done` status requires all steps to be `done` or `skipped`
5. Task `in_progress` requires at least one step `in_progress` or `pending`
