---
name: plan-type-generic
description: Generic plan type for documentation, config, and quick fixes
allowed-tools: Read, Bash

# Detection patterns and keywords (minimal - fallback type)
patterns: []
keywords:
  - documentation
  - config
  - fix
  - update

# Agent routing (null = use plan-refine-agent fallback)
domain:
  solution_outline_agent: null
  task_plan_agent: null

# Plan defaults for this type
plan_defaults:
  verification_command: null
  pr_workflow: false
  standards: []
---

# Plan Type: Generic (`pm-workflow:plan-type-generic`)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

**API**: Implements `pm-workflow:plan-type-api` contract.

## Domain Configuration

The `domain:` frontmatter indicates no domain agents (generic plans use inline refinement):

| Field | Value | Purpose |
|-------|-------|---------|
| `solution_outline_agent` | `null` | No domain agent - use plan-refine-agent |
| `task_plan_agent` | `null` | No domain agent - use plan-refine-agent |

The `plan_defaults:` frontmatter is automatically read by `manage-config create` during plan initialization:

| Field | Value | Config Field |
|-------|-------|--------------|
| `verification_command` | `null` | `verification_command`, `verification_required=false` |
| `pr_workflow` | `false` | `create_pr`, `branch_strategy=direct` |
| `standards` | `[]` | (none) |

When `solution_outline_agent` is `null`, the command falls back to `pm-workflow:plan-refine-agent` for inline solution outline/task creation.

---

## Fallback Behavior

Since `solution_outline_agent` and `task_plan_agent` are `null`, the `/plan-manage` command falls back to `pm-workflow:plan-refine-agent` for the refine phase.

The plan-refine-agent provides simple inline refinement:
- Creates 1:1 deliverable per request item with minimal transformation
- Creates single task per deliverable with basic steps (execute, verify)

This avoids the overhead of domain-specific agents for simple tasks.
