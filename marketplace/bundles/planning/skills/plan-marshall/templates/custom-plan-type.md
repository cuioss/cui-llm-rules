---
name: plan-type-{{NAME}}
description: Custom plan-type for {{DESCRIPTION}}
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Type: {{NAME}}

**Role**: Custom plan-type for {{DESCRIPTION}}.

**File Patterns**: {{FILE_PATTERNS}}

---

## When to Use

Use this plan-type when:
- Task primarily involves files matching: {{FILE_PATTERNS}}
- {{ADDITIONAL_CRITERIA}}

---

## Configuration

### Domain Agents

| Role | Agent |
|------|-------|
| Goals | {{GOALS_AGENT}} |
| Plan | {{PLAN_AGENT}} |

### Defaults

| Setting | Value |
|---------|-------|
| verification_required | true |
| verification_command | {{VERIFICATION_COMMAND}} |
| create_pr | false |
| branch_strategy | direct |

---

## Operation: configure

Called during plan initialization to set domain-specific defaults.

**Input**:
- `plan_id`: The plan identifier

**Actions**:
1. Set verification command
2. Configure PR workflow
3. Set branch strategy

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --key verification_command \
  --value "{{VERIFICATION_COMMAND}}"
```

---

## Operation: decompose

Decompose request into goals. Custom implementation or delegate to agent.

**If goals_agent is set**:
```
Task(subagent_type="{{GOALS_AGENT}}")
```

**If no goals_agent**:
Manual decomposition following these guidelines:
- {{DECOMPOSITION_GUIDELINE_1}}
- {{DECOMPOSITION_GUIDELINE_2}}

---

## Operation: create-tasks

Create implementation tasks from goals. Custom implementation or delegate to agent.

**If plan_agent is set**:
```
Task(subagent_type="{{PLAN_AGENT}}")
```

**If no plan_agent**:
Manual task creation following these guidelines:
- {{TASK_CREATION_GUIDELINE_1}}
- {{TASK_CREATION_GUIDELINE_2}}

---

## Customization

Edit this file to customize:
- Verification command
- Decomposition guidelines
- Task creation patterns
- Domain-specific workflows

---

## Notes

This is a project-local plan-type created by `/plan-marshall`.

Location: `.claude/plan-types/{{NAME}}/SKILL.md`

Registered in: `.plan/marshal.json` under `custom_plan_types`
