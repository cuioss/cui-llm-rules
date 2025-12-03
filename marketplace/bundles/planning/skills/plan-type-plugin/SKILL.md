---
name: plan-type-plugin
description: Plugin development plan type providing domain-specific configuration and refinement with /plugin-doctor verification
allowed-tools: Read, Bash
---

# Plan Type: Plugin Development (`planning:plan-type-plugin`)

**Use Cases**:
- Creating new marketplace components (agents, commands, skills)
- Updating existing marketplace components
- Plugin maintenance and refactoring
- Bundle restructuring

**API**: Implements `planning:plan-type-api` contract.

**FQN Convention**: All skill/command references use fully qualified names: `{bundle}:{component}`

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | none |
| Verification | `/cui-plugin-development-tools:plugin-doctor` |
| PR Workflow | false |
| Specify Agent | `cui-plugin-development-tools:plugin-specify-agent` |
| Plan Agent | `cui-plugin-development-tools:plugin-plan-agent` |

---

## Operation: configure

**Input**: `plan_id`

**References fields added** (via `planning:manage-references set`):

| Field | Value |
|-------|-------|
| `target_bundle` | `null` (populated during specify) |
| `bundle_path` | `null` (populated during specify) |
| `components` | `{"add": [], "modify": []}` |
| `verification_commands` | `["/cui-plugin-development-tools:plugin-doctor"]` |

**Config fields added** (via `planning:manage-config set`):

| Field | Value |
|-------|-------|
| `create_pr` | `false` |
| `verification_required` | `true` |
| `verification_command` | `/cui-plugin-development-tools:plugin-doctor` |
| `branch_strategy` | `direct` |

---

## Operation: specify

**Input**: `plan_id`, `requirement_id?` (optional for single-item mode)

**Delegation**:
```
Task(cui-plugin-development-tools:plugin-specify-agent,
     plan_id={plan_id},
     requirement_id={requirement_id})  # omit for batch
```

**Returns**: `{status, spec_ids[], lessons_recorded}`

The agent analyzes marketplace structure, creates specifications with:
- Component type (skill, command, agent, script)
- Target bundle location
- Frontmatter requirements
- Standards to follow
- Integration points

---

## Operation: plan

**Input**: `plan_id`, `specification_id?` (optional for single-item mode)

**Delegation**:
```
Task(cui-plugin-development-tools:plugin-plan-agent,
     plan_id={plan_id},
     specification_id={specification_id})  # omit for batch
```

**Returns**: `{status, task_ids[], lessons_recorded}`

The agent creates tasks with plugin-specific steps:

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
