---
name: plan-refine
description: Refine phase skill for GENERIC plan types only
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Refine Skill

**SCOPE**: This skill is ONLY for **generic plan types** without domain-specific agents.

**Role**: Fallback refine phase for generic plans. Creates goals and tasks using inline logic.

**CRITICAL**: Use Python scripts via Bash for plan file updates.

---

## Scripts

| Script | Notation |
|--------|----------|
| manage-config | `planning:manage-config` |
| manage-lifecycle | `planning:manage-lifecycle` |
| manage-work-log | `planning:manage-log` |
| manage-goals | `planning:manage-goals` |
| manage-tasks | `planning:manage-tasks` |

---

## Skill-Based Routing

The `/plan-manage` command uses **skill-based routing**:

1. Loads plan-type skill (e.g., `planning:plan-type-java`)
2. Reads `domain:` frontmatter for agent references
3. Invokes domain agents directly via Task tool

**This skill is the fallback** when plan-type has `domain.goals_agent: null` (generic plans).

```
/plan-manage action=refine plan=X
  │
  ├─ Load plan-type skill, read domain: frontmatter
  │
  ├─ If domain.goals_agent is NOT null:
  │    → Task: {skill.domain.goals_agent}
  │    → Task: {skill.domain.plan_agent}
  │
  └─ If domain.goals_agent IS null (generic):
       → Task: plan-refine-agent
         → Skill: plan-refine ← THIS SKILL
           → manage-goal add (Bash)
           → manage-task add (Bash)
```

---

## Primary Operation: refine

**Input**: `plan_id`

### Step 1: Log Phase Start

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Starting refine phase"
```

### Step 2: Validate Plan Type

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config get \
  --plan-id {plan_id} --field plan_type
```

**IF plan_type is domain-specific** (java, javascript, plugin):
```toon
status: error
error_type: wrong_routing
message: "Domain-specific plans must be refined via /plan-manage command, not plan-refine skill"
context:
  plan_type: {plan_type}
  correct_command: "/plan-manage action=refine plan={plan_id}"
```
Return this error. Do NOT proceed.

**IF plan_type is generic**: Continue to Step 3.

### Step 3: Create Goal

For generic plans, create a single goal from request text:

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal add \
  --plan-id {plan_id} \
  --title "Complete task" \
  --body "{request_summary}"
```

### Step 4: Create Tasks

Create execution tasks:

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --goal GOAL-1 \
  --title "Execute request" \
  --description "Complete the requested task" \
  --steps "Analyze requirements" "Implement solution" "Verify result"
```

### Step 5: Validate Goals Coverage

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal check \
  --plan-id {plan_id}
```

Returns coverage status. If `without_tasks > 0`, log a warning.

### Step 6: Log Completion

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "Completed refine: {goals_created} goals, {tasks_created} tasks"
```

### Step 7: Phase Transition

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed refine
```

---

## Error Handling

On any error, **first log the error** to work-log:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type error \
  --summary "ERROR: {error_type}" \
  --detail "{full error context and message}"
```

---

## Integration

### Command Integration
- **/plan-manage action=refine** - Routes to this skill for generic plans

### Scripts Used

| Script | Command | Purpose |
|--------|---------|---------|
| `planning:manage-config` | `get` | Read plan_type |
| `planning:manage-goals` | `add`, `check` | Create goals, verify coverage |
| `planning:manage-tasks` | `add` | Create tasks |
| `planning:manage-lifecycle` | `transition` | Phase transition |
| `planning:manage-log` | `add` | Log progress and completion |

### Related Skills
- **plan-init** - Previous phase (creates request.md, config, status)
- **plan-execute** - Next phase (executes tasks)
- **plan-type-*** - Domain configuration (loaded by command for agent routing)
