---
name: plan-type-plugin
description: Plugin development plan type providing domain-specific configuration and refinement with /plugin-doctor verification
allowed-tools: Read, Bash, Task
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

## Scripts

| Script | Purpose |
|--------|---------|
| `planning:manage-log` | Work log entries |
| `planning:manage-config` | Config field access |
| `planning:manage-references` | Reference file CRUD |

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | none |
| Verification | `/cui-plugin-development-tools:plugin-doctor` |
| PR Workflow | false |
| Goals Agent | `cui-plugin-development-tools:plugin-goals-agent` |
| Plan Agent | `cui-plugin-development-tools:plugin-plan-agent` |

---

## Operation: configure

**Input**: `plan_id`

### Step 1: Add References Fields

Use `planning:manage-references` to add domain-specific fields:

```bash
# Set target_bundle (populated during specify)
python3 .plan/execute-script.py planning:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field target_bundle \
  --value null

# Set bundle_path (populated during specify)
python3 .plan/execute-script.py planning:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field bundle_path \
  --value null

# Set components tracking
python3 .plan/execute-script.py planning:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field components \
  --value '{"add": [], "modify": []}'

# Set verification commands
python3 .plan/execute-script.py planning:manage-references:manage-references set \
  --plan-id {plan_id} \
  --field verification_commands \
  --value '["/cui-plugin-development-tools:plugin-doctor"]'
```

### Step 2: Add Config Fields

Use `planning:manage-config` to add finalize configuration:

```bash
# Set create_pr
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field create_pr \
  --value false

# Set verification_required
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field verification_required \
  --value true

# Set verification_command
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field verification_command \
  --value "/cui-plugin-development-tools:plugin-doctor"

# Set branch_strategy
python3 .plan/execute-script.py planning:manage-config:manage-config set \
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
| `verification_commands` | `["/cui-plugin-development-tools:plugin-doctor"]` |

**Config fields added**:

| Field | Value |
|-------|-------|
| `create_pr` | `false` |
| `verification_required` | `true` |
| `verification_command` | `/cui-plugin-development-tools:plugin-doctor` |
| `branch_strategy` | `direct` |

---

## Operation: decompose

**Input**: `plan_id`

**Before delegation**, log:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to plugin-goals-agent" \
  --detail "decomposing request into goals"
```

**Delegation**:
```
Task(cui-plugin-development-tools:plugin-goals-agent,
     plan_id={plan_id})
```

**After delegation**, log outcome:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "plugin-goals-agent completed: {goal_count} goals created" \
  --detail "lessons_recorded={count}"
```

**Returns**: `{status, goal_ids[], lessons_recorded}`

The agent analyzes marketplace structure, creates goals with:
- Component type (skill, command, agent, script)
- Target bundle location
- Frontmatter requirements
- Standards to follow
- Integration points

---

## Operation: plan

**Input**: `plan_id`, `goal_id?` (optional for single-item mode)

**Before delegation**, log:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to plugin-plan-agent" \
  --detail "goal_id={goal_id|batch}"
```

**Delegation**:
```
Task(cui-plugin-development-tools:plugin-plan-agent,
     plan_id={plan_id},
     goal_id={goal_id})  # omit for batch
```

**After delegation**, log outcome:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "plugin-plan-agent completed: {task_count} tasks created" \
  --detail "lessons_recorded={count}"
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
