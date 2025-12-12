---
name: plan-type-api
description: Defines the unified API contract for plan-type skills. Plan types provide domain-specific refinement logic and configuration.
allowed-tools: Read
---

# Plan Type API Skill

**Role**: API contract definition for plan-type skills. This skill defines the interface that all plan-type skills must implement.

**Key Principle**: Plan-type skills **document domain agents** in structured frontmatter. Commands read this frontmatter and invoke agents directly via Task tool.

## Contract Standards

| Contract | Purpose | Document |
|----------|---------|----------|
| **Domain Frontmatter** | Required YAML frontmatter structure | [standards/domain-frontmatter-contract.md](standards/domain-frontmatter-contract.md) |
| **Solution Outline Agent** | Request → Solution Outline | [standards/solution-outline-agent-contract.md](standards/solution-outline-agent-contract.md) |
| **User Review Protocol** | Mandatory review before task creation | [standards/user-review-protocol.md](standards/user-review-protocol.md) |
| **Task Plan Agent** | Solution Outline → Tasks | [standards/task-plan-agent-contract.md](standards/task-plan-agent-contract.md) |
| **Deliverable Contract** | Deliverable structure in solution outline | [standards/deliverable-contract.md](standards/deliverable-contract.md) |
| **Task Contract** | Task structure and optimization | [standards/task-contract.md](standards/task-contract.md) |

## Routing Flow

```
Request → [Solution Outline Agent] → User Review → [Task Plan Agent] → Tasks
            ↓                           ↓
     solution_outline.md          [User Review Protocol]
```

1. `/plan-manage` command loads plan-type skill
2. Command reads `domain:` section from skill frontmatter
3. Command invokes `domain.solution_outline_agent` via Task tool
4. Command triggers [User Review Protocol](standards/user-review-protocol.md) (mandatory)
5. After approval, command invokes `domain.task_plan_agent` via Task tool
6. For generic plans (`solution_outline_agent: null`), falls back to `plan-refine-agent`

## Plan Types

| Plan Type | Solution Outline Agent | Task Plan Agent | Verification |
|-----------|------------------------|-----------------|--------------|
| `java` | `pm-dev-java:java-solution-outline-agent` | `pm-dev-java:java-task-plan-agent` | `/pm-dev-builder:builder-build-and-fix` |
| `javascript` | `pm-dev-frontend:js-solution-outline-agent` | `pm-dev-frontend:js-task-plan-agent` | `/pm-dev-builder:builder-build-and-fix system=npm` |
| `plugin-development` | `pm-plugin-development:plugin-solution-outline-agent` | `pm-plugin-development:plugin-task-plan-agent` | `/pm-plugin-development:plugin-doctor` |
| `generic` | None (inline) | None (inline) | None |

## Traceability Flow

```
Request → Solution Outline (with Deliverables) → Tasks (each task references its deliverable number)
```

Each task maintains traceability to its source deliverable(s), enabling M:N relationships between deliverables and tasks.

---

## Implementation Requirements

Plan-type skills must:

1. Include `domain:` frontmatter per [Domain Frontmatter Contract](standards/domain-frontmatter-contract.md)
2. Include `plan_defaults:` frontmatter with `verification_command`, `pr_workflow`, `standards`
3. Document domain agent behavior for solution outline and task plan operations
4. Return `status` field in all outputs
5. Handle errors with `status: error` and `message`

**Note**: The `plan_defaults:` frontmatter is automatically read by `manage-config create` during plan initialization. No separate configure operation is needed.

---

## Script Execution Tracing

Domain agents execute scripts via `execute-script.py`. For plan-scoped logging, agents MUST pass the plan context.

### Scripts with `--plan-id` Parameter

Scripts that accept `--plan-id` (manage-* scripts) use it for both logic AND logging:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task add \
  --plan-id {plan_id} --title "Task title"
```

### Scripts without `--plan-id` Parameter

Scripts that don't accept `--plan-id` (scan-*, analyze-*) use `--trace-plan-id` for logging only:

```bash
python3 .plan/execute-script.py plan-marshall:marketplace-inventory:scan-marketplace-inventory \
  --trace-plan-id {plan_id} --include-descriptions
```

The `--trace-plan-id` parameter is:
- Extracted by the executor for logging purposes
- Stripped before passing to the script (script never sees it)
- Enables plan-scoped logging in `.plan/plans/{plan_id}/script-execution.log`

---

## Integration

**Callers**:
- `plan-init` → `manage-config create` reads `plan_defaults:` from frontmatter automatically
- `/plan-manage action=refine` → loads skill, reads `domain:` frontmatter, invokes agents via Task
- `plan-finalize` → reads config.toon directly

**Domain Agents** (invoked by commands):
- `pm-dev-java:java-solution-outline-agent` / `pm-dev-java:java-task-plan-agent`
- `pm-dev-frontend:js-solution-outline-agent` / `pm-dev-frontend:js-task-plan-agent`
- `pm-plugin-development:plugin-solution-outline-agent` / `pm-plugin-development:plugin-task-plan-agent`

**Data Layer** (used by domain agents):
- `pm-workflow:manage-plan-documents:manage-plan-document` (request) - Request document operations
- `pm-workflow:manage-solution-outline:manage-solution-outline` (solution_outline.md) - Solution outline validation and queries
- `pm-workflow:manage-tasks:manage-task` - Task creation with deliverable references
