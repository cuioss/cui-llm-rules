---
name: plan-type-api
description: Defines the unified API contract for plan-type skills. Plan types provide domain-specific refinement logic and configuration.
allowed-tools: Read
---

# Plan Type API Skill

**Role**: API contract definition for plan-type skills. This skill defines the interface that all plan-type skills must implement.

**Key Principle**: Plan-type skills provide **domain knowledge only**. Base file creation is handled by manage-* skills; plan-types add domain-specific fields via `configure`.

## API Contract Overview

All plan-type skills implement these operations:

| Operation | Input | Output | Caller | When |
|-----------|-------|--------|--------|------|
| `configure` | `plan_id` | References + config updated | plan-configure | After type detection |
| `specify` | `plan_id` | SPEC files created | plan-refine | Refine phase (step 1) |
| `plan` | `plan_id` | TASK files created | plan-refine | Refine phase (step 2) |

**Traceability Flow**: Requirements → Specifications → Tasks (each task references its specification)

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

Transforms requirements into specifications (REQ → SPEC).

**Input**: `plan_id`

**Process**:
1. Load all requirements via `manage-requirements:findAll`
2. For each requirement, apply domain-specific logic to create specification(s)
3. Create via `manage-specifications:add` with traceability (`--requirements REQ-n`)

**Domain-Specific Logic** (provided by each plan-type):
- Spec title derivation from requirements
- Technical content based on domain (classes for Java, modules for JS, etc.)
- Standards references to load during execution

---

## Operation: plan

Transforms specifications into executable tasks (SPEC → TASK).

**Input**: `plan_id`

**Process**:
1. Load all specifications via `manage-specifications:findAll`
2. For each specification, apply domain-specific logic to create task(s)
3. Create via `manage-tasks:add` with traceability (`--specification SPEC-n`)

**Domain-Specific Logic** (provided by each plan-type):
- Task generation: how many tasks per spec, what steps
- Task ordering: dependencies and execution sequence
- Verification steps: domain-specific quality checks

---

## Plan Types

| Plan Type | Verification | PR | Use Case |
|-----------|--------------|----|----|
| `java` | `/builder-build-and-fix` | yes | Java/Maven/Gradle |
| `javascript` | `/builder-build-and-fix system=npm` | yes | JavaScript/npm |
| `plugin-development` | `/plugin-doctor` | no | Marketplace components |
| `simple` | none | no | Documentation, config, quick fixes |

---

## Implementation Requirements

Plan-type skills must:

1. Implement all three operations: `configure`, `specify`, `plan`
2. Use manage-* tools for all data I/O
3. Return `status` field in all outputs
4. Handle errors with `status: error` and `message`

---

## Integration

**Callers**:
- `plan-configure` → calls `configure`
- `plan-refine` → calls `specify`, then `plan`
- `plan-finalize` → reads config.toon directly (no operation call needed)

**Data Layer Tools**:
- `manage-requirements:findAll` / `manage-specifications:add` (for specify)
- `manage-specifications:findAll` / `manage-tasks:add` (for plan)
- `manage-references:set` / `manage-config:set` (for configure)
