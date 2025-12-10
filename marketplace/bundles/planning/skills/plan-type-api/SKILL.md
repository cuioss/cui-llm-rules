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
  solution_outline_agent: {bundle}:{goals-agent-name}    # Agent for request → goals
  plan_agent: {bundle}:{plan-agent-name}      # Agent for goals → tasks
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
3. Command invokes `domain.solution_outline_agent` and `domain.plan_agent` via Task tool
4. For generic plans (`domain.solution_outline_agent: null`), falls back to `plan-refine-agent`

## API Contract Overview

All plan-type skills implement these operations:

| Operation | Input | Output | Caller | When |
|-----------|-------|--------|--------|------|
| `configure` | `plan_id` | References + config updated | plan-init | During initialization |

**Note**: The `decompose` and `plan` operations are documented in plan-type skills but executed by domain agents invoked from commands.

**Traceability Flow**: Request → Solution (with goals) → Tasks (each task references its goal number)

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

## Domain Agent Behavior

Domain agents are invoked by commands (not by plan-type skills) via Task tool.

### Solution Outline Agent

**Purpose**: Analyze request and create solution document (Request → Solution)

**Invoked by**: `/plan-manage action=refine` command

**Responsibilities**:
- Read request.md for the request
- Analyze codebase with domain knowledge
- Write solution_outline.md directly via Write tool, then validate with `manage-plan-documents:solution validate`
- Document goals as numbered sections in solution document
- Record lessons-learned on issues

**Returns**: `{status, goal_count, lessons_recorded}`

### Plan Agent

**Purpose**: Transform goals into executable tasks (Solution → TASKs)

**Invoked by**: `/plan-manage action=refine` command (after solution outline agent completes)

**Responsibilities**:
- Read solution_outline.md for goals
- Generate domain-specific task steps
- Create tasks via `manage-tasks:add --goal N` (numeric reference)
- Record lessons-learned on issues

**Returns**: `{status, task_ids[], lessons_recorded}`

---

## Plan Types

| Plan Type | Solution Outline Agent | Plan Agent | Verification |
|-----------|-------------|------------|--------------|
| `java` | `cui-java-expert:java-solution-outline-agent` | `cui-java-expert:java-plan-agent` | `/builder:builder-build-and-fix` |
| `javascript` | `cui-frontend-expert:js-solution-outline-agent` | `cui-frontend-expert:js-plan-agent` | `/builder:builder-build-and-fix system=npm` |
| `plugin-development` | `cui-plugin-development-tools:plugin-solution-outline-agent` | `cui-plugin-development-tools:plugin-plan-agent` | `/cui-plugin-development-tools:plugin-doctor` |
| `generic` | None (inline) | None (inline) | None |

---

## Implementation Requirements

Plan-type skills must:

1. Include `domain:` frontmatter with agent references (or null for generic)
2. Implement `configure` operation for plan initialization
3. Document domain agent behavior for goals and plan operations
4. Return `status` field in all outputs
5. Handle errors with `status: error` and `message`

---

## Integration

**Callers**:
- `plan-init` → calls `configure` operation
- `/plan-manage action=refine` → loads skill, reads `domain:` frontmatter, invokes agents via Task
- `plan-finalize` → reads config.toon directly (no operation call needed)

**Domain Agents** (invoked by commands):
- `cui-java-expert:java-solution-outline-agent` / `cui-java-expert:java-plan-agent`
- `cui-frontend-expert:js-solution-outline-agent` / `cui-frontend-expert:js-plan-agent`
- `cui-plugin-development-tools:plugin-solution-outline-agent` / `cui-plugin-development-tools:plugin-plan-agent`

**Data Layer** (used by domain agents):
- `manage-plan-documents` (request/solution) / `manage-tasks` scripts
