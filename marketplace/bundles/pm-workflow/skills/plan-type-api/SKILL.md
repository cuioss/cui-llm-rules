---
name: plan-type-api
description: Defines the unified API contract for plan-type skills. Plan types provide domain-specific refinement logic and configuration.
allowed-tools: Read
---

# Plan Type API Skill

**Role**: API contract definition for plan-type skills. This skill defines the interface that all plan-type skills must implement.

**Key Principle**: Plan-type skills **document domain agents** in structured frontmatter. Commands read this frontmatter and invoke agents directly via Task tool.

## Domain Frontmatter Structure

All plan-type skills declare domain agents in YAML frontmatter:

```yaml
---
name: plan-type-{domain}
description: {Domain} plan type
allowed-tools: Read, Bash
domain:
  solution_outline_agent: {bundle}:{solution-outline-agent}  # Agent for request → solution outline
  task_plan_agent: {bundle}:{task-plan-agent}                # Agent for solution outline → tasks
  verification_command: /{verification-cmd}   # Finalize verification
  pr_workflow: true|false                     # Create PR on finalize
  standards:                                  # Domain skills to load
    - {bundle}:{skill-1}
    - {bundle}:{skill-2}
---
```

**Routing Flow**:
1. `/plan-manage` command loads plan-type skill
2. Command reads `domain:` section from skill frontmatter
3. Command invokes `domain.solution_outline_agent` and `domain.task_plan_agent` via Task tool
4. For generic plans (`domain.solution_outline_agent: null`), falls back to `plan-refine-agent`

## API Contract Overview

All plan-type skills implement these operations:

| Operation | Input | Output | Caller | When |
|-----------|-------|--------|--------|------|
| `configure` | `plan_id` | References + config updated | plan-init | During initialization |

**Note**: Solution outline creation and task planning are documented in plan-type skills but executed by domain agents invoked from commands.

**Traceability Flow**: Request → Solution Outline (with Deliverables) → Tasks (each task references its deliverable number)

---

## Operation: configure

Adds domain-specific fields to references.toon AND finalize configuration to config.toon. Called by plan-configure after plan-type detection.

**Input**: `plan_id`

**Process**:
1. Add domain fields to references.toon via `pm-workflow:manage-references:manage-references set`
2. Add finalize config to config.toon via `pm-workflow:manage-config:manage-config set`

**Finalize Configuration Fields** (all plan types set these in config.toon):

| Field | Description |
|-------|-------------|
| `create_pr` | Whether to create a pull request |
| `verification_required` | Whether verification must pass before finalize |
| `verification_command` | Command for verification (or null) |
| `branch_strategy` | `feature` or `direct` |

---

## Deliverable Contract

Deliverables in solution_outline.md provide the technical design that enables task-plan-agent optimization.

> **Full Specification**: See [standards/deliverable-contract.md](standards/deliverable-contract.md) for complete field definitions, domain values, and validation rules.

### Required Metadata

All deliverables MUST include a metadata block:

```markdown
**Metadata:**
- change_type: {create|modify|refactor|migrate|delete}
- execution_mode: {automated|manual|mixed}
- domain: {java|java-testing|javascript|javascript-testing|plugin}
- suggested_skill: {bundle}:{skill-name}
- suggested_workflow: {workflow-name}
- context_skills: []
- depends: {none | deliverable number(s)}
```

### Validation Requirements

Each deliverable MUST contain:

| Requirement | Purpose |
|-------------|---------|
| `domain` metadata | Skill loading via skill-domains |
| `suggested_skill` and `suggested_workflow` | Delegation mapping |
| `context_skills` | Optional skill loading (must be in domain's optionals) |
| `depends` field | Dependency ordering and parallelization |
| Explicit file list | Step generation (not "all files matching X") |
| Verification command | Task verification |

---

## Task Contract

Tasks are created by task-plan agents and represent committable units of work. Each task:

- References one or more deliverables (M:N relationship)
- Contains delegation information for execution
- Includes verification criteria
- Specifies dependencies on other tasks (for ordering/parallelization)
- Results in exactly one commit

> **Full Specification**: See [standards/task-contract.md](standards/task-contract.md) for the complete task contract including optimization workflow and decision tables.

### Key Fields for Task Planning

| Field | Purpose |
|-------|---------|
| `deliverables` | Track which solution outline items are covered |
| `depends_on` | Enable execution ordering and parallelization |
| `delegation.skill` | Skill to execute task |
| `delegation.workflow` | Workflow within skill |
| `delegation.domain` | Domain for loading default skills |
| `delegation.context_skills` | Optional skills from domain |
| `verification` | Consolidated from deliverable verification criteria |

### Deliverable-to-Task Relationship

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| 1:1 | One deliverable → one task | Large coherent deliverables |
| N:1 | Multiple deliverables → one task | Similar small changes (aggregation) |
| 1:N | One deliverable → multiple tasks | Mixed execution modes (split) |

---

## Domain Agent Behavior

Domain agents are invoked by commands (not by plan-type skills) via Task tool.

### Solution Outline Agent

**Purpose**: Analyze request and create solution outline document (Request → Solution Outline)

**Invoked by**: `/plan-manage action=refine` command

**Input Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `feedback` | string | No | User feedback from review (for revision iterations) |

**Key Responsibility**: Produce deliverables that follow the **Deliverable Contract** defined above. Deliverables that lack required fields (metadata, file enumeration, verification) are INVALID.

**Responsibilities**:
- Load `pm-workflow:manage-solution-outline` skill for structure guidance
- Read request.md for the request
- Analyze codebase with domain knowledge
- Write solution_outline.md via `pm-workflow:manage-solution-outline:manage-solution-outline write` with heredoc (includes ASCII overview diagram)
- Document deliverables as numbered `### N. Title` sections with **Deliverable Contract** metadata
- Validate with `pm-workflow:manage-solution-outline:manage-solution-outline validate --plan-id {plan_id}`
- Record lessons-learned on issues
- **If `feedback` provided**: Incorporate user feedback into existing solution_outline.md

**Output Validation**: The agent MUST validate that each deliverable contains:
- [ ] `change_type` metadata
- [ ] `execution_mode` metadata
- [ ] `domain` metadata (valid domain from config)
- [ ] `suggested_skill` and `suggested_workflow`
- [ ] `context_skills` (empty list or valid optionals for domain)
- [ ] `depends` field (`none` or valid deliverable references)
- [ ] Explicit file list (not "all files matching X")
- [ ] Verification command and criteria

**Returns**: `{status, deliverable_count, lessons_recorded}`

### MANDATORY User Review (Command Responsibility)

After the solution outline agent completes, the `/plan-manage` command MUST:

1. **Display the solution outline for review**:
   ```
   ## Solution Outline Created

   📄 **Review your solution outline**: .plan/plans/{plan_id}/solution_outline.md

   Please review the deliverables and architecture before proceeding.
   ```

2. **Ask user via AskUserQuestion**:
   - Option 1: "Proceed to create tasks" → Continue to task plan agent
   - Option 2: "Request changes" → Capture feedback, re-invoke solution outline agent with `feedback` parameter

3. **Loop until user approves**: This halt is NOT OPTIONAL. Task creation MUST NOT proceed without user confirmation.

**Rationale**: Solution outlines define deliverables that become tasks. User review ensures alignment before committing to implementation scope.

### Task Plan Agent

**Purpose**: Transform deliverables into optimized, committable tasks (Solution Outline → Tasks)

**Invoked by**: `/plan-manage action=refine` command (after user approves solution outline)

**Key Responsibility**: Apply optimization to package deliverables efficiently while maintaining:
1. **Atomic committability**: Each task = one coherent commit
2. **Testability**: Each task has verification
3. **Execution efficiency**: Minimize agent spawns and skill loads
4. **Dependency ordering**: Tasks execute in valid dependency order
5. **Parallelization**: Independent tasks can run concurrently

**Optimization Workflow**: Task-plan agents MUST follow the 6-step optimization workflow:
1. Load all deliverables with metadata
2. Build dependency graph
3. Analyze for aggregation opportunities
4. Analyze for split requirements
5. Create optimized tasks
6. Log optimization decisions

> **Full Workflow**: See [standards/task-contract.md](standards/task-contract.md) for the complete optimization workflow and decision tables.

**Responsibilities**:
- Read solution_outline.md for deliverables via `pm-workflow:manage-solution-outline:manage-solution-outline list-deliverables`
- Apply optimization workflow to determine task groupings
- Create tasks via `pm-workflow:manage-tasks:manage-task add --deliverables N [M ...]` (numeric deliverable references)
- Set task dependencies via `--depends-on` parameter
- Record lessons-learned on issues

**Returns**: `{status, task_ids[], optimization_summary, lessons_recorded}`

---

## Plan Types

| Plan Type | Solution Outline Agent | Task Plan Agent | Verification |
|-----------|-------------|------------|--------------|
| `java` | `pm-dev-java:java-solution-outline-agent` | `pm-dev-java:java-task-plan-agent` | `/pm-dev-builder:builder-build-and-fix` |
| `javascript` | `pm-dev-frontend:js-solution-outline-agent` | `pm-dev-frontend:js-task-plan-agent` | `/pm-dev-builder:builder-build-and-fix system=npm` |
| `plugin-development` | `pm-plugin-development:plugin-solution-outline-agent` | `pm-plugin-development:plugin-task-plan-agent` | `/pm-plugin-development:plugin-doctor` |
| `generic` | None (inline) | None (inline) | None |

---

## Implementation Requirements

Plan-type skills must:

1. Include `domain:` frontmatter with agent references (or null for generic)
2. Implement `configure` operation for plan initialization
3. Document domain agent behavior for solution outline and task plan operations
4. Return `status` field in all outputs
5. Handle errors with `status: error` and `message`

---

## Script Execution Tracing

Domain agents execute scripts via `execute-script.py`. For plan-scoped logging, agents MUST pass the plan context:

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

**Rationale**: Plan-scoped logging enables audit trail per plan. Without `--trace-plan-id`, scripts log to global `.plan/logs/` which lacks plan association.

---

## Integration

**Callers**:
- `plan-init` → calls `configure` operation
- `/plan-manage action=refine` → loads skill, reads `domain:` frontmatter, invokes agents via Task
- `plan-finalize` → reads config.toon directly (no operation call needed)

**Domain Agents** (invoked by commands):
- `pm-dev-java:java-solution-outline-agent` / `pm-dev-java:java-task-plan-agent`
- `pm-dev-frontend:js-solution-outline-agent` / `pm-dev-frontend:js-task-plan-agent`
- `pm-plugin-development:plugin-solution-outline-agent` / `pm-plugin-development:plugin-task-plan-agent`

**Data Layer** (used by domain agents):
- `pm-workflow:manage-plan-documents:manage-plan-document` (request) - Request document operations
- `pm-workflow:manage-solution-outline:manage-solution-outline` (solution_outline.md) - Solution outline validation and queries
- `pm-workflow:manage-tasks:manage-task` - Task creation with deliverable references
