---
name: plan-type-api
description: Defines the unified API contract for plan-type skills. Plan types provide domain-specific refinement logic and configuration.
allowed-tools: Read
---

# Plan Type API Skill

**Role**: API contract definition for plan-type skills. This skill defines the interface that all plan-type skills must implement.

**Key Principle**: Plan-type skills are **thin orchestrators** that delegate to domain agents. Domain agents analyze the codebase and write SPECs/TASKs directly via manage-* scripts.

## API Contract Overview

All plan-type skills implement these operations:

| Operation | Input | Output | Caller | When |
|-----------|-------|--------|--------|------|
| `configure` | `plan_id` | References + config updated | plan-configure | After type detection |
| `specify` | `plan_id`, `requirement_id?` | SPEC files created (via delegation) | plan-refine | Refine phase (step 1) |
| `plan` | `plan_id`, `specification_id?` | TASK files created (via delegation) | plan-refine | Refine phase (step 2) |

**Traceability Flow**: Requirements → Specifications → Tasks (each task references its specification)

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

## Operation: specify

Transforms requirements into specifications (REQ → SPEC) via domain agent delegation.

**Input**: `plan_id`, `requirement_id?` (optional for single-item mode)

**Process**:
```
Task({domain}-specify-agent,
     plan_id={plan_id},
     requirement_id={requirement_id})  # omit for batch
```

**Domain Agent Responsibility**:
- Query requirements via `manage-requirements` script
- Analyze codebase with domain knowledge
- Create specifications via `manage-specifications:add`
- Record lessons-learned on issues

**Output**: `{status, spec_ids[], lessons_recorded}`

---

## Operation: plan

Transforms specifications into executable tasks (SPEC → TASK) via domain agent delegation.

**Input**: `plan_id`, `specification_id?` (optional for single-item mode)

**Process**:
```
Task({domain}-plan-agent,
     plan_id={plan_id},
     specification_id={specification_id})  # omit for batch
```

**Domain Agent Responsibility**:
- Query specifications via `manage-specifications` script
- Generate domain-specific task steps
- Create tasks via `manage-tasks:add`
- Record lessons-learned on issues

**Output**: `{status, task_ids[], lessons_recorded}`

---

## Plan Types

| Plan Type | Specify Agent | Plan Agent | Verification |
|-----------|---------------|------------|--------------|
| `java` | `cui-java-expert:java-specify-agent` | `cui-java-expert:java-plan-agent` | `/builder:builder-build-and-fix` |
| `javascript` | `cui-frontend-expert:js-specify-agent` | `cui-frontend-expert:js-plan-agent` | `/builder:builder-build-and-fix system=npm` |
| `plugin-development` | `cui-plugin-development-tools:plugin-specify-agent` | `cui-plugin-development-tools:plugin-plan-agent` | `/cui-plugin-development-tools:plugin-doctor` |
| `generic` | None (inline) | None (inline) | None |

---

## Implementation Requirements

Plan-type skills must:

1. Implement all three operations: `configure`, `specify`, `plan`
2. Delegate `specify` and `plan` to domain agents (except generic)
3. Return `status` field in all outputs
4. Handle errors with `status: error` and `message`

---

## Integration

**Callers**:
- `plan-configure` → calls `configure`
- `plan-refine` → calls `specify`, then `plan`
- `plan-finalize` → reads config.toon directly (no operation call needed)

**Domain Agents** (for specify/plan delegation):
- `cui-java-expert:java-specify-agent` / `cui-java-expert:java-plan-agent`
- `cui-frontend-expert:js-specify-agent` / `cui-frontend-expert:js-plan-agent`
- `cui-plugin-development-tools:plugin-specify-agent` / `cui-plugin-development-tools:plugin-plan-agent`

**Data Layer** (used by domain agents):
- `manage-requirements` / `manage-specifications` / `manage-tasks` scripts
