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

**Responsibilities**:
- Load `pm-workflow:manage-solution-outline` skill for structure guidance
- Read request.md for the request
- Analyze codebase with domain knowledge
- Write solution_outline.md via `pm-workflow:manage-solution-outline:manage-solution-outline write` with heredoc (includes ASCII overview diagram)
- Document deliverables as numbered `### N. Title` sections
- Validate with `pm-workflow:manage-solution-outline:manage-solution-outline validate --plan-id {plan_id}`
- Record lessons-learned on issues
- **If `feedback` provided**: Incorporate user feedback into existing solution_outline.md

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

**Purpose**: Transform deliverables into executable tasks (Solution Outline → Tasks)

**Invoked by**: `/plan-manage action=refine` command (after user approves solution outline)

**Responsibilities**:
- Read solution_outline.md for deliverables via `pm-workflow:manage-solution-outline:manage-solution-outline list-deliverables`
- Generate domain-specific task steps per deliverable
- Create tasks via `pm-workflow:manage-tasks:manage-task add --goal N` (numeric deliverable reference)
- Record lessons-learned on issues

**Returns**: `{status, task_ids[], lessons_recorded}`

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
