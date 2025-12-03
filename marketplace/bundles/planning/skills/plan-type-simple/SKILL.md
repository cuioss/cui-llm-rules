---
name: plan-type-simple
description: Simple plan type providing minimal configuration and refinement for documentation, config, and quick fixes
allowed-tools: Read, Bash
---

# Plan Type: Simple (`planning:plan-type-simple`)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

**API**: Implements `planning:plan-type-api` contract.

**FQN Convention**: All skill/command references use fully qualified names: `{bundle}:{component}`

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | none |
| Verification | none |
| PR Workflow | false |
| Analysis Agent | none (no codebase analysis needed) |

---

## Operation: configure

**Input**: `plan_id`

**References fields added**: none (simple plans have no domain-specific fields)

**Config fields added** (via `planning:manage-config set`):

| Field | Value |
|-------|-------|
| `create_pr` | `false` |
| `verification_required` | `false` |
| `verification_command` | `null` |
| `branch_strategy` | `direct` |

---

## Operation: specify

**Input**: `plan_id`

**Simple Behavior**: Creates 1:1 specification per requirement with minimal transformation.

---

## Operation: plan

**Input**: `plan_id`

**Simple Behavior**: Creates single task per specification with basic steps:
1. Execute task
2. Verify result
