---
name: plan-type-plugin
description: Plugin development plan type for marketplace components
allowed-tools: Read, Bash

# Detection patterns and keywords
patterns:
  - "marketplace/bundles/**/SKILL.md"
  - "marketplace/bundles/**/plugin.json"
  - "**/agents/*.md"
  - "**/commands/*.md"
keywords:
  - plugin
  - marketplace
  - skill
  - agent
  - command
  - bundle

# Agent routing
domain:
  solution_outline_agent: pm-plugin-development:plugin-solution-outline-agent
  task_plan_agent: pm-plugin-development:plugin-task-plan-agent
  implement_agent: pm-plugin-development:plugin-implement-agent

# Plan defaults for this type
plan_defaults:
  verification_command: /pm-plugin-development:plugin-doctor
  pr_workflow: false
  standards:
    - pm-plugin-development:plugin-architecture
    - pm-plugin-development:plugin-script-architecture
---

# Plan Type: Plugin Development (`pm-workflow:plan-type-plugin`)

**Use Cases**:
- Creating new marketplace components (agents, commands, skills)
- Updating existing marketplace components
- Plugin maintenance and refactoring
- Bundle restructuring

**API**: Implements `pm-workflow:plan-type-api` contract.

## Domain Configuration

The `domain:` frontmatter provides structured routing information for commands:

| Field | Value | Purpose |
|-------|-------|---------|
| `solution_outline_agent` | `pm-plugin-development:plugin-solution-outline-agent` | Creates solution outline with deliverables |
| `task_plan_agent` | `pm-plugin-development:plugin-task-plan-agent` | Creates tasks from deliverables |
| `implement_agent` | `pm-plugin-development:plugin-implement-agent` | Executes tasks from plan |

The `plan_defaults:` frontmatter is automatically read by `manage-config create` during plan initialization:

| Field | Value | Config Field |
|-------|-------|--------------|
| `verification_command` | `/pm-plugin-development:plugin-doctor` | `verification_command`, `verification_required` |
| `pr_workflow` | `false` | `create_pr`, `branch_strategy` |
| `standards` | Plugin architecture, Script architecture | (informational) |

---

## Agent Behavior

### plugin-solution-outline-agent

Analyzes marketplace structure and creates deliverables with:
- Component type (skill, command, agent, script)
- Target bundle location
- Frontmatter requirements
- Standards to follow
- Integration points

**Returns**: `{status, deliverable_count, solution_document, lessons_recorded}`

### plugin-task-plan-agent

Creates tasks with plugin-specific steps:

| Component Type | Key Steps |
|----------------|-----------|
| skill | Create SKILL.md, Add standards/, Add scripts/, Register in plugin.json |
| command | Create command.md, Define workflow, Add delegation |
| agent | Create agent.md, Select tools, Define focus |
| script | Create test file first (TDD), Implement script, Verify tests pass |

**Templates** (in `templates/` directory):

| Template | Purpose |
|----------|---------|
| `script-task.md` | TDD workflow for Python scripts |
| `skill-task.md` | Skill creation with SKILL.md structure |
| `command-task.md` | Command orchestration patterns |
| `agent-task.md` | Agent frontmatter and tool selection |

**Returns**: `{status, task_ids[], lessons_recorded}`

### plugin-implement-agent

Executes tasks by delegating to `plugin-plan-execute` skill:
- Loads task from plan via manage-tasks API
- Loads domain and context skills
- Iterates through steps (each step is a file path)
- Applies changes per step using Edit/Write tools
- Runs verification command
- Returns structured execution result

**Returns**: `{status, plan_id, task_number, execution_summary, verification, next_action}`
