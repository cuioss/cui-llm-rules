# Plan Refine Workflow

**Scope**: This workflow applies to **generic plan types only**. Domain-specific plans (Java, JavaScript, Plugin) use domain agents invoked by the `/plan-manage` command. See [architecture.md](architecture.md) for the skill-based routing pattern.

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
python3 .plan/execute-script.py planning:manage-config:manage-config get \
  --plan-id {plan_id} --field plan_type
```

**Guard**: If `plan_type` is NOT `generic`, return error - domain-specific plans must use `/plan-manage` command.

---

## Step 2: Read Request

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request read \
  --plan-id {plan_id}
```

---

## Step 3: Create Solution Document

For generic plans, write the solution document directly using Claude Code's Write tool to: `.plan/plans/{plan_id}/solution_outline.md`

See plan-refine SKILL.md for the template content.

Then validate the structure:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution validate \
  --plan-id {plan_id}
```

**Why direct Write?** Solution outlines can contain ASCII diagrams and rich content that don't fit CLI parameter passing.

---

## Step 4: Create Tasks

Create execution tasks referencing the goal number:

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --goal 1 \
  --title "Execute request" \
  --description "Complete the requested task" \
  --steps "Analyze requirements" "Implement solution" "Verify result"
```

**Note**: The `--goal` parameter is numeric, referencing the goal section number in solution_outline.md.

---

## Step 5: Transition

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed refine
```

---

## Domain Routing Summary

| Plan Type | Handler | Routing |
|-----------|---------|---------|
| `generic` | `plan-refine-agent` → this workflow | Command invokes agent via Task |
| `java` | `java-solution-plan-agent`, `java-plan-agent` | Command reads skill frontmatter, invokes via Task |
| `javascript` | `js-solution-plan-agent`, `js-plan-agent` | Command reads skill frontmatter, invokes via Task |
| `plugin-development` | `plugin-solution-plan-agent`, `plugin-plan-agent` | Command reads skill frontmatter, invokes via Task |

**Key**: The `/plan-manage` command handles all routing. This skill is only invoked for generic plans.
