# Domain Frontmatter Contract

Standard structure for YAML frontmatter in plan-type skills.

## Purpose

All plan-type skills declare domain agents and configuration in YAML frontmatter. Commands read this frontmatter to route operations to appropriate agents.

## Required Structure

```yaml
---
name: plan-type-{domain}
description: {Domain} plan type
allowed-tools: Read, Bash

# Agent routing
domain:
  solution_outline_agent: {bundle}:{solution-outline-agent}  # Agent for request → solution outline
  task_plan_agent: {bundle}:{task-plan-agent}                # Agent for solution outline → tasks
  implement_agent: {bundle}:{implement-agent}                # Agent for task execution

# Plan defaults (read by manage-config create)
plan_defaults:
  verification_command: /{verification-cmd}   # Finalize verification
  pr_workflow: true|false                     # Create PR on finalize
  standards:                                  # Domain skills to load (informational)
    - {bundle}:{skill-1}
    - {bundle}:{skill-2}
---
```

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Skill name (format: `plan-type-{domain}`) |
| `description` | string | Yes | Human-readable description |
| `allowed-tools` | string | Yes | Tools the skill may reference |
| `domain.solution_outline_agent` | string\|null | Yes | Agent for Request → Solution Outline |
| `domain.task_plan_agent` | string\|null | Yes | Agent for Solution Outline → Tasks |
| `domain.implement_agent` | string\|null | Yes | Agent for Task Execution |
| `plan_defaults.verification_command` | string\|null | Yes | Command for finalize verification |
| `plan_defaults.pr_workflow` | boolean | Yes | Whether to create PR on finalize |
| `plan_defaults.standards` | array | Yes | Domain skills (informational, can be empty) |

**Note**: `plan_defaults` fields are automatically read by `manage-config create` during plan initialization and written to config.toon as finalize configuration fields.

## Agent Reference Format

Agent references use the format `{bundle}:{agent-name}`:

```yaml
solution_outline_agent: pm-dev-java:java-solution-outline-agent
task_plan_agent: pm-dev-java:java-task-plan-agent
implement_agent: pm-dev-java:java-implement-agent
```

For generic plans (no domain agents), use `null`:

```yaml
solution_outline_agent: null
task_plan_agent: null
implement_agent: null
```

## Routing Flow

1. `/plan-manage` command loads plan-type skill
2. Command reads `domain:` section from skill frontmatter
3. Command invokes `domain.solution_outline_agent` via Task tool
4. After user review, command invokes `domain.task_plan_agent` via Task tool
5. `/plan-execute` invokes `domain.implement_agent` for each task
6. For generic plans (`solution_outline_agent: null`), falls back to `plan-refine-agent`

## Plan Type Examples

### Java Plan Type

```yaml
---
name: plan-type-java
description: Java plan type for CUI projects
allowed-tools: Read, Bash
domain:
  solution_outline_agent: pm-dev-java:java-solution-outline-agent
  task_plan_agent: pm-dev-java:java-task-plan-agent
  implement_agent: pm-dev-java:java-implement-agent
plan_defaults:
  verification_command: /pm-dev-builder:builder-build-and-fix
  pr_workflow: true
  standards:
    - pm-dev-java:cui-java-core
    - pm-dev-java:cui-java-unit-testing
---
```

### JavaScript Plan Type

```yaml
---
name: plan-type-javascript
description: JavaScript plan type for CUI projects
allowed-tools: Read, Bash
domain:
  solution_outline_agent: pm-dev-frontend:js-solution-outline-agent
  task_plan_agent: pm-dev-frontend:js-task-plan-agent
  implement_agent: pm-dev-frontend:js-implement-agent
plan_defaults:
  verification_command: /pm-dev-builder:builder-build-and-fix system=npm
  pr_workflow: true
  standards:
    - pm-dev-frontend:cui-javascript
    - pm-dev-frontend:cui-javascript-unit-testing
---
```

### Plugin Development Plan Type

```yaml
---
name: plan-type-plugin-development
description: Plugin development plan type
allowed-tools: Read, Bash
domain:
  solution_outline_agent: pm-plugin-development:plugin-solution-outline-agent
  task_plan_agent: pm-plugin-development:plugin-task-plan-agent
  implement_agent: pm-plugin-development:plugin-implement-agent
plan_defaults:
  verification_command: /pm-plugin-development:plugin-doctor
  pr_workflow: false
  standards:
    - pm-plugin-development:plugin-architecture
---
```

### Generic Plan Type

```yaml
---
name: plan-type-generic
description: Generic plan type for non-domain tasks
allowed-tools: Read, Bash
domain:
  solution_outline_agent: null
  task_plan_agent: null
  implement_agent: null
plan_defaults:
  verification_command: null
  pr_workflow: false
  standards: []
---
```

## Validation Rules

| Rule | Description |
|------|-------------|
| `name` format | Must match `plan-type-{domain}` pattern |
| Agent format | Must be `{bundle}:{agent}` or `null` |
| Standards format | Each entry must be `{bundle}:{skill}` |
| `standards` array | Can be empty but must be present |
| Null agents | All domain agents null for generic plans |

## Integration

**Readers**:
- `/plan-manage action=refine` → reads `domain:` frontmatter for agent routing
- `manage-config create` → reads `plan_defaults:` frontmatter for finalize configuration

**Producers**: Plan-type skill authors

**Related**:
- [Solution Outline Agent Contract](solution-outline-agent-contract.md)
- [Task Plan Agent Contract](task-plan-agent-contract.md)
- [Implement Agent Contract](implement-agent-contract.md)
