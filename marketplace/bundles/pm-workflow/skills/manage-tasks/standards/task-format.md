# Task File Format Specification

This document provides a quick reference for the TOON format used by task files.

> **Complete Specification**: See [design-for-manage-tasks.md](/.plan/task-management/design-for-manage-tasks.md) for the full specification including all field definitions, status values, state transitions, and validation rules.

## File Naming Convention

```
TASK-{NNN}-{slug}.toon
```

- `{NNN}`: Zero-padded 3-digit number (001, 002, etc.)
- `{slug}`: Kebab-case derived from title (max 40 characters)

## File Structure

```toon
number: {integer}
title: {string}
status: {task_status}
created: {iso_timestamp}
updated: {iso_timestamp}

deliverables[{count}]:
- {deliverable_number_1}
- {deliverable_number_2}

description: |
  {multiline_text}

delegation:
  skill: {bundle}:{skill-name}
  workflow: {workflow-name}

steps[{count}]{number,title,status}:
{step_number},{step_title},{step_status}
...

verification:
  commands[{count}]:
  - {command_1}
  - {command_2}
  criteria: {success_criteria}
  manual: {true|false}

current_step: {integer}
```

## Status Values

**Task Status**: `pending`, `in_progress`, `done`, `blocked`

**Step Status**: `pending`, `in_progress`, `done`, `skipped`

## Example

```toon
number: 2
title: Add Auth Endpoint
status: in_progress
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T11:00:00Z

deliverables[2]:
- 1
- 4

description: |
  Create REST endpoint for user authentication.
  Endpoint should accept username/password and
  return JWT token on successful auth.

delegation:
  skill: pm-dev-java:java-implement
  workflow: implement

steps[3]{number,title,status}:
1,Create AuthController class,done
2,Add request/response DTOs,in_progress
3,Write integration tests,pending

verification:
  commands[2]:
  - ./gradlew test --tests *AuthController*
  - curl -s http://localhost:8080/auth | jq .status
  criteria: All tests pass and endpoint responds
  manual: false

current_step: 2
```

## Numbering Rules

- Task numbers: Assigned incrementally, immutable, gaps allowed on removal
- Step numbers: Always sequential 1-N, renumbered on add/remove
