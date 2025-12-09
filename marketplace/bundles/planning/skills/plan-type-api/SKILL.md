---
name: plan-type-api
description: Defines the unified API contract for plan-type skills. Plan types provide domain-specific refinement logic and configuration.
allowed-tools: Read
---

# Plan Type API Skill

**Role**: API contract definition for plan-type skills. This skill defines the interface that all plan-type skills must implement.

**Key Principle**: Plan-type skills are **thin orchestrators** that delegate to domain agents. Domain agents analyze the codebase and write GOALs/TASKs directly via manage-* scripts.

## API Contract Overview

All plan-type skills implement these operations:

| Operation | Input | Output | Caller | When |
|-----------|-------|--------|--------|------|
| `configure` | `plan_id` | References + config updated | plan-init | During initialization |
| `decompose` | `plan_id` | GOAL files created (via delegation) | plan-refine | Refine phase (step 1) |
| `plan` | `plan_id`, `goal_id?` | TASK files created (via delegation) | plan-refine | Refine phase (step 2) |

**Traceability Flow**: Request → Goals → Tasks (each task references its goal)

**Batch + Single Mode**:
- `plan_id` only → batch mode (processes all pending items)
- `plan_id` + item ID → single mode (processes one item)

---

## Operation: configure

Adds domain-specific fields to references.toon AND finalize configuration to config.toon. Called by plan-configure after plan-type detection.

**Input**: `plan_id`

**Process**:
1. Add domain fields to references.toon via `manage-references:set`
2. Add finalize config to config.toon via `manage-config:set`

**Finalize Configuration Fields** (all plan types set these in config.toon):

| Field | Description |
|-------|-------------|
| `create_pr` | Whether to create a pull request |
| `verification_required` | Whether verification must pass before finalize |
| `verification_command` | Command for verification (or null) |
| `branch_strategy` | `feature` or `direct` |

---

## Operation: decompose

Analyzes the request and decomposes it into goals (Request → GOALs) via domain agent delegation.

**Input**: `plan_id`

**Process**:
```
Task({domain}-goals-agent,
     plan_id={plan_id})
```

**Domain Agent Responsibility**:
- Read request.md for the request
- Analyze codebase with domain knowledge
- Create goals via `manage-goals:add`
- Record lessons-learned on issues

**Output**: `{status, goal_ids[], lessons_recorded}`

---

## Operation: plan

Transforms goals into executable tasks (GOAL → TASK) via domain agent delegation.

**Input**: `plan_id`, `goal_id?` (optional for single-item mode)

**Process**:
```
Task({domain}-plan-agent,
     plan_id={plan_id},
     goal_id={goal_id})  # omit for batch
```

**Domain Agent Responsibility**:
- Query goals via `manage-goals` script
- Generate domain-specific task steps
- Create tasks via `manage-tasks:add`
- Record lessons-learned on issues

**Output**: `{status, task_ids[], lessons_recorded}`

---

## Plan Types

| Plan Type | Goals Agent | Plan Agent | Verification |
|-----------|-------------|------------|--------------|
| `java` | `cui-java-expert:java-goals-agent` | `cui-java-expert:java-plan-agent` | `/builder:builder-build-and-fix` |
| `javascript` | `cui-frontend-expert:js-goals-agent` | `cui-frontend-expert:js-plan-agent` | `/builder:builder-build-and-fix system=npm` |
| `plugin-development` | `cui-plugin-development-tools:plugin-goals-agent` | `cui-plugin-development-tools:plugin-plan-agent` | `/cui-plugin-development-tools:plugin-doctor` |
| `generic` | None (inline) | None (inline) | None |

---

## Implementation Requirements

Plan-type skills must:

1. Implement all three operations: `configure`, `decompose`, `plan`
2. Delegate `decompose` and `plan` to domain agents (except generic)
3. Return `status` field in all outputs
4. Handle errors with `status: error` and `message`

---

## Integration

**Callers**:
- `plan-init` → calls `configure`
- `plan-refine` → calls `decompose`, then `plan`
- `plan-finalize` → reads config.toon directly (no operation call needed)

**Domain Agents** (for decompose/plan delegation):
- `cui-java-expert:java-goals-agent` / `cui-java-expert:java-plan-agent`
- `cui-frontend-expert:js-goals-agent` / `cui-frontend-expert:js-plan-agent`
- `cui-plugin-development-tools:plugin-goals-agent` / `cui-plugin-development-tools:plugin-plan-agent`

**Data Layer** (used by domain agents):
- `manage-goals` / `manage-tasks` scripts
