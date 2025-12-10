---
name: plan-type-{{NAME}}
description: Custom plan-type for {{DESCRIPTION}}
allowed-tools: Read, Bash
domain:
  solution_outline_agent: {{SOLUTION_OUTLINE_AGENT}}
  plan_agent: {{PLAN_AGENT}}
  verification_command: {{VERIFICATION_COMMAND}}
  pr_workflow: false
  standards: []
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

## Domain Configuration

### Frontmatter Fields

| Field | Value |
|-------|-------|
| `solution_outline_agent` | {{SOLUTION_OUTLINE_AGENT}} |
| `plan_agent` | {{PLAN_AGENT}} |
| `verification_command` | {{VERIFICATION_COMMAND}} |
| `pr_workflow` | false |

**Note**: Domain agents are invoked by the `/plan-manage` command via Task tool, not by operations in this skill.

---

## Operation: configure

Called during plan initialization to set domain-specific defaults in config.toon.

**Input**: `plan_id`

**Process**:
1. Set finalize configuration fields in config.toon

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --key create_pr \
  --value "false"
```

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --key verification_required \
  --value "true"
```

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --key verification_command \
  --value "{{VERIFICATION_COMMAND}}"
```

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --key branch_strategy \
  --value "direct"
```

---

## Integration

### Routing Flow

```
/plan-manage action=refine
   │
   ├─ Loads this skill
   ├─ Reads domain: frontmatter
   │
   ├─ Task: {{SOLUTION_OUTLINE_AGENT}}  → Creates goals from request
   └─ Task: {{PLAN_AGENT}}   → Creates tasks from goals
```

### Generic Fallback

If `solution_outline_agent` is `null`, the command falls back to `plan-refine-agent` for inline goal/task creation.

---

## Customization

Edit this file to customize:
- Domain agents (in frontmatter)
- Verification command
- PR workflow setting
- Configure operation defaults

---

## Notes

This is a project-local plan-type created by `/plan-marshall`.

Location: `.claude/plan-types/{{NAME}}/SKILL.md`

Registered in: `.plan/marshal.json` under `custom_plan_types`
