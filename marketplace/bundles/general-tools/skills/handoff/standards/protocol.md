# Handoff Protocol Specification

This document specifies the TOON-based handoff protocol for workflow state transfer between components.

## Overview

A **handoff** is a structured state transfer between workflow components that includes:
- Source/destination tracking (`from`/`to`)
- Task status and progress
- Artifacts and context
- Next action guidance
- Error handling with alternatives

## TOON Format

Handoffs use TOON (Token-Oriented Object Notation) for 30-60% token savings vs JSON.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Source component identifier |
| `to` | string | Target component identifier |
| `plan_id` | string | Plan identifier for context loading |
| `task.status` | enum | `pending` \| `in_progress` \| `completed` \| `failed` \| `blocked` |

## Auto-Generated Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | Auto-generated if not provided |
| `handoff_id` | string | Auto-generated as `{plan_id}-{step}-{timestamp}` |

## Optional Fields

### Task Fields

| Field | Type | Description |
|-------|------|-------------|
| `task.description` | string | What needs to be done |
| `task.progress` | int (0-100) | Completion percentage |

### Context Fields

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Specific task within phase (e.g., `task-6`) |
| `requirements` | string list | REQ IDs being worked on (e.g., `REQ-1, REQ-3`) |
| `specification` | string | SPEC ID if applicable |
| `notes` | string | Additional context |

### Navigation Fields

| Field | Type | Description |
|-------|------|-------------|
| `next_action` | string | What to do next |
| `next_focus` | string | Specific focus area |

### Artifact Fields

| Field | Type | Description |
|-------|------|-------------|
| `artifacts.files_created` | array | Files created during task |
| `artifacts.files_modified` | array | Files modified during task |

### Error Fields (when status=failed)

| Field | Type | Description |
|-------|------|-------------|
| `error.type` | string | Error category |
| `error.message` | string | Human-readable message |
| `error.details` | string | Detailed information |
| `alternatives` | array | Recovery options |

## Transport Mechanism

Handoffs use a **hybrid approach**:

| Content Type | Transport | Rationale |
|--------------|-----------|-----------|
| Coordination metadata | In handoff | Small (~50 lines), routing decisions |
| Large context | Load via `plan_id` | Task details, requirements, history |

### What Travels in Handoff (Direct)

- `from`/`to` - routing information
- `plan_id` - reference key for large context
- `task_id` - specific task within phase
- `task.status` - outcome
- `next_action`/`next_focus` - guidance
- `error` + `alternatives` - decision context
- `artifacts` - file references
- `requirements` - REQ ID references

### What Loads via plan_id (On-Demand)

- Full task description (task.md)
- All requirements (requirements/*.md)
- Configuration details (config.toon)
- Implementation history
- Full file contents

## Validation

### On Save

| Scenario | Behavior | Exit Code |
|----------|----------|-----------|
| Missing required field | Error with missing fields list | 1 |
| Invalid `task.status` | Error with valid options | 1 |
| Invalid `task.progress` | Warning, clamp to 0-100 | 0 |
| Unknown optional field | Accept silently | 0 |
| Malformed TOON | Error with line context | 1 |

### Error Output Format

```toon
status: error
error:
  type: validation_error
  message: Missing required fields
  missing_fields[2]: from, plan_id
```

## Examples

### Phase Transition

```toon
from: plan-init-skill
to: plan-configure-skill
handoff_id: jwt-auth-init-complete-20251202T103000Z
timestamp: 2025-12-02T10:30:00Z

task:
  description: Initialize plan from issue
  status: completed
  progress: 100

plan_id: jwt-auth

artifacts:
  files_created[1]{path,type}:
  task.md,markdown

plan_status:
  previous_phase: init
  current_phase: configure
  progress: 20

next_action: Configure plan type and technology
next_focus: Extract requirements from task.md
```

### Error with Alternatives

```toon
from: build-verify-agent
to: java-fix-build-agent
handoff_id: jwt-auth-error-20251202T110000Z
timestamp: 2025-12-02T11:00:00Z

task:
  description: Verify build
  status: failed

plan_id: jwt-auth
task_id: task-6

error:
  type: build_failure
  message: Compilation failed
  details: |
    src/auth/JwtService.java:45
    cannot find symbol: class Algorithm

alternatives[3]:
- Fix build error and retry
- View full build log
- Skip to next task (mark as blocked)

context:
  iteration: 1
  max_iterations: 3
```

### Completion

```toon
from: plan-finalize-skill
to: caller
handoff_id: jwt-auth-complete-20251202T150000Z
timestamp: 2025-12-02T15:00:00Z

task:
  description: Finalize implementation
  status: completed
  progress: 100

plan_id: jwt-auth

summary:
  tasks_completed: 8
  tests_passed: 24
  coverage: 85

deliverables:
  pr_url: https://github.com/org/repo/pull/123
  branch: feature/jwt-auth
  commit: abc123def
```

## File Storage

### Location

```
.plan/memory/handoffs/
```

### Naming Convention

```
{plan_id}-{step}-{timestamp}.toon
```

- `plan_id`: Plan identifier (sanitized for filesystem)
- `step`: Step name (e.g., `init-complete`, `verify-error`)
- `timestamp`: ISO timestamp without punctuation (`YYYYMMDDTHHMMSSZ`)

### Examples

```
jwt-auth-init-complete-20251202T103000Z.toon
jwt-auth-configure-complete-20251202T104500Z.toon
jwt-auth-verify-error-20251202T110000Z.toon
```

## Design Rationale

Based on patterns from Anthropic, AWS Step Functions, Temporal, and LangGraph:

| Pattern | Source | Application |
|---------|--------|-------------|
| Reference-based state | AWS, Anthropic | Large context via `plan_id` |
| Shared state graph | LangGraph, CrewAI | Handoff is shared state |
| Progressive disclosure | Anthropic | Incremental context loading |
| Durable execution | Temporal | Persisted handoffs |
| Orchestration | Temporal | Orchestrator routing |

Key insight: "Find the smallest set of high-signal tokens that maximize likelihood of desired outcome" (Anthropic). Handoffs contain coordination metadata; large context loads on-demand.
