# Plan Refine Workflow

**Scope**: This workflow applies to **generic domain only**. Domain-specific plans (Java, JavaScript, Plugin) use domain agents invoked by the `/plan-manage` command. See [architecture.md](architecture.md) for the skill-based routing pattern.

## Workflow Overview

Generic plan refinement creates a solution document and tasks from the request:

```
Request from Init Phase
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ REFINE PHASE (Generic Plans Only)                   │
│                                                     │
│   1. Read context (plan_id, config)                 │
│   2. Read request document                          │
│   3. Create solution document with goal(s)          │
│   4. Create tasks referencing goals                 │
│   5. Transition to execute phase                    │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Execute Phase
```

---

## Step 1: Read Context

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} --field domain
```

**Guard**: If `domain` is NOT `generic`, return error - domain-specific plans must use `/plan-manage` command.

---

## Step 2: Read Request

```bash
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-documents \
  request read \
  --plan-id {plan_id}
```

---

## Step 3: Create Solution Document

For generic plans, write the solution document directly using Claude Code's Write tool to: `.plan/plans/{plan_id}/solution_outline.md`

See plan-refine SKILL.md for the template content.

Then validate the structure:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline validate \
  --plan-id {plan_id}
```

**Why direct Write?** Solution outlines can contain ASCII diagrams and rich content that don't fit CLI parameter passing.

---

## Step 4: Create Tasks

Create execution tasks referencing the deliverable number using heredoc:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
  --plan-id {plan_id} <<'EOF'
title: Execute request
deliverables: [1]
domain: generic
description: |
  Complete the requested task

steps:
  - Analyze requirements
  - Implement solution
  - Verify result
EOF
```

**Note**: The `deliverables` array contains numeric references to deliverable numbers in solution_outline.md.

---

## Step 5: Transition

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed refine
```

---

## Thin Agent Architecture

The refine phase uses thin agents that load domain-specific skills dynamically:

| Agent | Purpose | Skill Source |
|-------|---------|--------------|
| `solution-outline-agent` | Create deliverables | `config.workflow_skills.{domain}.solution_outline` |
| `task-plan-agent` | Create tasks | `config.workflow_skills.{domain}.task_plan` |

**Key**: The `/plan-manage` command invokes the thin agents, which load domain skills from config.toon's workflow_skills block.
