# Plan Refine Workflow

**Scope**: This workflow applies to **generic plan types only**. Domain-specific plans (Java, JavaScript, Plugin) use domain agents invoked by the `/plan-manage` command. See [architecture.md](architecture.md) for the skill-based routing pattern.

## Workflow Overview

Generic plan refinement creates simple goals and tasks from the request:

```
Request from Init Phase
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ REFINE PHASE (Generic Plans Only)                   │
│                                                     │
│   1. Read context (plan_id, config)                 │
│   2. Create goal from request                       │
│   3. Create tasks for goal                          │
│   4. Validate coverage (goals have tasks)           │
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

## Step 2: Create Goal

For generic plans, create a single goal from the request:

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal add \
  --plan-id {plan_id} \
  --title "Complete task" \
  --body "{request_summary}"
```

---

## Step 3: Create Tasks

Create execution and verification tasks:

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --goal GOAL-1 \
  --title "Execute request" \
  --description "Complete the requested task" \
  --steps "Analyze requirements" "Implement solution" "Verify result"
```

---

## Step 4: Validate Coverage

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal check \
  --plan-id {plan_id}
```

Verify `without_tasks: 0` in response.

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
| `java` | `java-goals-agent`, `java-plan-agent` | Command reads skill frontmatter, invokes via Task |
| `javascript` | `js-goals-agent`, `js-plan-agent` | Command reads skill frontmatter, invokes via Task |
| `plugin-development` | `plugin-goals-agent`, `plugin-plan-agent` | Command reads skill frontmatter, invokes via Task |

**Key**: The `/plan-manage` command handles all routing. This skill is only invoked for generic plans.
