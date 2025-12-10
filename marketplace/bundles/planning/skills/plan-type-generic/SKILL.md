---
name: plan-type-generic
description: Generic plan type for documentation, config, and quick fixes
allowed-tools: Read, Bash
domain:
  solution_outline_agent: null
  task_plan_agent: null
  verification_command: null
  pr_workflow: false
  standards: []
---

# Plan Type: Generic (`planning:plan-type-generic`)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

**API**: Implements `planning:plan-type-api` contract.

## Domain Configuration

The `domain:` frontmatter indicates no domain agents (generic plans use inline refinement):

| Field | Value | Purpose |
|-------|-------|---------|
| `solution_outline_agent` | `null` | No domain agent - use plan-refine-agent |
| `task_plan_agent` | `null` | No domain agent - use plan-refine-agent |
| `verification_command` | `null` | No verification required |
| `pr_workflow` | `false` | No PR (direct to main) |
| `standards` | `[]` | No domain-specific standards |

When `solution_outline_agent` is `null`, the command falls back to `planning:plan-refine-agent` for inline solution outline/task creation.

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

## Fallback Behavior

Since `solution_outline_agent` and `task_plan_agent` are `null`, the `/plan-manage` command falls back to `planning:plan-refine-agent` for the refine phase.

The plan-refine-agent provides simple inline refinement:
- Creates 1:1 deliverable per request item with minimal transformation
- Creates single task per deliverable with basic steps (execute, verify)

This avoids the overhead of domain-specific agents for simple tasks.
