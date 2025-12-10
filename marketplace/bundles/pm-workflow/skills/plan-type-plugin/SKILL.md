---
name: plan-type-plugin
description: Plugin development plan type for marketplace components
allowed-tools: Read, Bash
domain:
  solution_outline_agent: pm-plugin-development:plugin-solution-outline-agent
  task_plan_agent: pm-plugin-development:plugin-task-plan-agent
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
| `verification_command` | `/pm-plugin-development:plugin-doctor` | Plugin validation |
| `pr_workflow` | `false` | No PR (direct to main) |
| `standards` | Plugin architecture, Script architecture | Skills to load |

---

## Operation: configure

**Input**: `plan_id`

### Step 1: Add References Fields

Use `pm-workflow:manage-references:manage-references` to add domain-specific fields:

```bash
# Set target_bundle (populated during specify)
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field target_bundle \
  --value null

# Set bundle_path (populated during specify)
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field bundle_path \
  --value null

# Set components tracking
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field components \
  --value '{"add": [], "modify": []}'

# Set verification commands
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field verification_commands \
  --value '["/pm-plugin-development:plugin-doctor"]'
```

### Step 2: Add Config Fields

Use `pm-workflow:manage-config:manage-config` to add finalize configuration:

```bash
# Set create_pr
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field create_pr \
  --value false

# Set verification_required
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field verification_required \
  --value true

# Set verification_command
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field verification_command \
  --value "/pm-plugin-development:plugin-doctor"

# Set branch_strategy
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field branch_strategy \
  --value direct
```

### Summary

**References fields added**:

| Field | Value |
|-------|-------|
| `target_bundle` | `null` (populated during specify) |
| `bundle_path` | `null` (populated during specify) |
| `components` | `{"add": [], "modify": []}` |
| `verification_commands` | `["/pm-plugin-development:plugin-doctor"]` |

**Config fields added**:

| Field | Value |
|-------|-------|
| `create_pr` | `false` |
| `verification_required` | `true` |
| `verification_command` | `/pm-plugin-development:plugin-doctor` |
| `branch_strategy` | `direct` |

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
