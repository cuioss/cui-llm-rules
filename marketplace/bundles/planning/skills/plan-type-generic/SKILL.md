---
name: plan-type-generic
description: Generic plan type providing minimal configuration and refinement for documentation, config, and quick fixes
allowed-tools: Read, Bash
---

# Plan Type: Generic (`planning:plan-type-generic`)

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

## Operation: decompose

**Input**: `plan_id`

**Simple Behavior**: Creates 1:1 goal per request item with minimal transformation.

---

## Operation: plan

**Input**: `plan_id`

**Simple Behavior**: Creates single task per goal with basic steps:
1. Execute task
2. Verify result
