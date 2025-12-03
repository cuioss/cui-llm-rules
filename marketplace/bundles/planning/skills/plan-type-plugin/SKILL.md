---
name: plan-type-plugin
description: Plugin development plan type providing domain-specific configuration and refinement with /plugin-doctor verification
allowed-tools: Read, Bash
---

# Plan Type: Plugin Development

**Use Cases**:
- Creating new marketplace components (agents, commands, skills)
- Updating existing marketplace components
- Plugin maintenance and refactoring
- Bundle restructuring

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | none |
| Verification | `/plugin-doctor` |
| PR Workflow | false |

---

## Operation: configure

**Input**: `plan_id`

**References fields added**:

| Field | Value |
|-------|-------|
| `target_bundle` | `null` (populated during specify) |
| `bundle_path` | `null` (populated during specify) |
| `components` | `{"add": [], "modify": []}` |
| `verification_commands` | `["/plugin-doctor"]` |

**Config fields added**:

| Field | Value |
|-------|-------|
| `create_pr` | `false` |
| `verification_required` | `true` |
| `verification_command` | `/plugin-doctor` |
| `branch_strategy` | `direct` |

---

## Operation: specify

**Input**: `plan_id`

**Plugin-Specific Content** (included in specifications):
- Component type (skill, command, agent, script)
- Target bundle location
- Frontmatter requirements
- Standards to follow
- Integration points

---

## Operation: plan

**Input**: `plan_id`

**Task Steps by Component Type**:

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
