---
name: plan-wf-skill-api
description: Defines the unified API contracts for workflow skills. Workflow skills provide domain-agnostic operations that load domain knowledge from marshal.json.
allowed-tools: Read
---

# Plan Workflow Skill API

**Role**: API contract definition for workflow skills. This skill defines the interface contracts for solution outline, task planning, and task execution operations.

**Key Principle**: Workflow skills are **domain-agnostic**. Domain knowledge comes from `marshal.json` (via `resolve-workflow-skill`) which specifies which workflow skills to load during execution.

## Contract Standards

| Contract | Purpose | Document |
|----------|---------|----------|
| **Config TOON Format** | config.toon structure with domains and settings | [standards/config-toon-format.md](standards/config-toon-format.md) |
| **Solution Outline Skill** | Request → Solution Outline with deliverables | [standards/solution-outline-skill-contract.md](standards/solution-outline-skill-contract.md) |
| **User Review Protocol** | Mandatory review before task creation | [standards/user-review-protocol.md](standards/user-review-protocol.md) |
| **Task Plan Skill** | Solution Outline → Tasks with domain/profile | [standards/task-plan-skill-contract.md](standards/task-plan-skill-contract.md) |
| **Deliverable Contract** | Deliverable structure in solution outline | [standards/deliverable-contract.md](standards/deliverable-contract.md) |
| **Task Contract** | Task structure with domain, profile, skills | [standards/task-contract.md](standards/task-contract.md) |
| **Task Execution Skill** | Task execution with two-tier skill loading | [standards/task-execution-skill-contract.md](standards/task-execution-skill-contract.md) |

## Routing Flow

```
Request → [plan-init-agent] → [solution-outline-agent] → User Review → [task-plan-agent] → Tasks → [task-execute-agent]
              ↓                        ↓                      ↓                ↓                      ↓
         config.toon           solution_outline.md    [User Review]      task files          two-tier skills
         (domains)               (deliverables)        Protocol           (domain,            1. system
                                                                          profile,            2. task.skills
                                                                          skills)
```

1. `plan-init-agent` creates plan, detects domains, writes config.toon (domains + settings)
2. `solution-outline-agent` resolves workflow skill from `marshal.json` via `resolve-workflow-skill --domain {domain} --phase solution_outline`
3. `/plan-manage` triggers [User Review Protocol](standards/user-review-protocol.md) (mandatory)
4. After approval, `task-plan-agent` creates tasks with domain, profile, skills fields
5. `task-execute-agent` resolves workflow skill from `marshal.json` based on `task.profile`, loads `task.skills` array

## Thin Agent Pattern

| Agent | Purpose | Skill Loading |
|-------|---------|---------------|
| `pm-workflow:plan-init-agent` | Init plan, detect domains, write config.toon | System skills only |
| `pm-workflow:solution-outline-agent` | Create deliverables | `resolve-workflow-skill --domain {domain} --phase solution_outline` |
| `pm-workflow:task-plan-agent` | Create tasks from deliverables | `resolve-workflow-skill --domain {domain} --phase task_plan` |
| `pm-workflow:task-execute-agent` | Execute single task | `resolve-workflow-skill --domain {domain} --phase {profile}` + `task.skills` |

## Domain Configuration

Domains and workflow skills are stored in `config.toon`:

```toon
domains: [java]

workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
```

For multi-domain plans (e.g., fullstack):
```toon
domains: [java, javascript]

workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
  javascript:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
```

## Traceability Flow

```
Request → Solution Outline (with Deliverables) → Tasks (each task references its deliverable number)
```

Each task maintains traceability to its source deliverable(s), enabling M:N relationships between deliverables and tasks.

---

## Implementation Requirements

Workflow skills must:

1. Be domain-agnostic (no hardcoded domain references)
2. Load domain knowledge from config.toon at runtime
3. Return `status` field in all outputs
4. Handle errors with `status: error` and `message`

---

## Script Execution Tracing

Workflow skills execute scripts via `execute-script.py`. For plan-scoped logging, skills MUST pass the plan context.

### Scripts with `--plan-id` Parameter

Scripts that accept `--plan-id` (manage-* scripts) use it for both logic AND logging:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
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
- `plan-init-agent` → writes domains and settings to config.toon
- `/plan-manage action=refine` → spawns solution-outline-agent then task-plan-agent
- `/plan-execute` → spawns task-execute-agent for each task
- `plan-finalize` → reads config.toon directly

**Workflow Skill Resolution**:
- Workflow skills resolved from `marshal.json` via `plan-marshall-config resolve-workflow-skill`
- NOT stored in config.toon (only domains and plan settings)

**Thin Agents** (4 generic agents):
- `pm-workflow:plan-init-agent` - Plan creation and domain detection
- `pm-workflow:solution-outline-agent` - Loads workflow skill, creates deliverables
- `pm-workflow:task-plan-agent` - Loads workflow skill, creates tasks
- `pm-workflow:task-execute-agent` - Loads workflow skill and task.skills, executes

**Data Layer** (used by workflow skills):
- `pm-workflow:manage-plan-documents:manage-plan-documents` (request) - Request document operations
- `pm-workflow:manage-solution-outline:manage-solution-outline` (solution_outline.md) - Solution outline validation and queries
- `pm-workflow:manage-tasks:manage-tasks` - Task creation with deliverable references
- `pm-workflow:manage-config:manage-config` - Config.toon field access
