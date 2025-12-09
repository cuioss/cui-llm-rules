---
name: plan-refine
description: Refine phase skill for plan management. Delegates to plan-type skill to decompose request into goals and create tasks. Optionally creates analysis.md for complex tasks and identifies documentation needs.
allowed-tools: Read, Write, Bash, Skill, Task, AskUserQuestion
---

# Plan Refine Skill

**Role**: Second phase skill. Delegates to plan-type skill to decompose request into goals and create tasks.

**Execution Pattern**: Detect complexity → Delegate to plan-type:decompose → Delegate to plan-type:plan → Identify documentation needs → Transition

**CRITICAL**: Use Python scripts via Bash for plan file updates (Edit/Write tools trigger permission prompts on `.plan/` directories).

---

## Scripts

| Script | Notation |
|--------|----------|
| manage-config | `planning:manage-config` |
| manage-lifecycle | `planning:manage-lifecycle` |
| manage-work-log | `planning:manage-log` |
| manage-references | `planning:manage-references` |
| manage-goals | `planning:manage-goals` |
| manage-tasks | `planning:manage-tasks` |

---

## Plan-Type Skill API

All plan-type skills implement two operations for refinement:

**1. decompose** - Analyze request and create GOALs:
```
Skill: planning:plan-type-{plan_type}
operation: decompose
plan_id: {plan_id}
```

**2. plan** - Transform GOAL → TASK:
```
Skill: planning:plan-type-{plan_type}
operation: plan
plan_id: {plan_id}
```

The plan-type skills delegate to domain agents which write directly:
- Domain agents create goals via `manage-goals:add`
- Domain agents create tasks via `manage-tasks:add`
- Domain agents record lessons-learned on issues

**No intermediate data passing** - plan-refine only passes `plan_id`.

---

## Primary Operation: refine

**Input**: `plan_id`

**Steps**:

### Step 0: Log Phase Start

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Starting refine phase"
```

### Step 1: Read Context

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config get-multi \
  --plan-id {plan_id} \
  --fields plan_type,compatibility
```

Returns only the required fields: `plan_type` (java, javascript, plugin-development, generic) and `compatibility`.

### Step 2: Detect Complexity (Optional)

For complex tasks, create analysis.md first:

| Question | If YES → Create analysis.md |
|----------|----------------------------|
| Are multiple components affected? | Yes |
| Are there breaking changes? | Yes |
| Are there architectural decisions? | Yes |
| Are there complex dependencies? | Yes |

If complexity detected → Execute `create-analysis` operation before continuing.

### Step 3: Delegate to Plan-Type Skill (decompose)

```
Skill: planning:plan-type-{plan_type}
operation: decompose
plan_id: {plan_id}
```

**Expected Output**:

```toon
status: success
plan_id: {plan_id}

goals_created[N]:
- GOAL-1
- GOAL-2
- GOAL-3

lessons_recorded: {count}
```

### Step 4: Delegate to Plan-Type Skill (plan)

```
Skill: planning:plan-type-{plan_type}
operation: plan
plan_id: {plan_id}
```

**Expected Output**:

```toon
status: success
plan_id: {plan_id}

tasks_created[N]:
- TASK-1
- TASK-2
- TASK-3

lessons_recorded: {count}
```

**For generic plans**: Plan-type handles inline (no domain agent delegation).

### Step 5: Validate Goals Coverage

Verify all goals have tasks assigned:

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal check \
  --plan-id {plan_id}
```

Returns coverage status:
```toon
status: success
total_goals: 3
with_tasks: 3
without_tasks: 0
coverage_percent: 100
```

If `without_tasks > 0`, log a warning and optionally alert the user.

### Step 6: Log Completion

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "Completed refine: {goals_created} goals, {tasks_created} tasks" \
  --detail "Goals and tasks created via {plan_type} domain agents. Coverage: {coverage_percent}%"
```

### Step 7: Identify Documentation Needs (Optional)

Check if ADRs or interfaces should be created:

1. **ADR triggers**: Architectural decisions, security changes, integration patterns
2. **Interface triggers**: New APIs, service contracts, external integrations

If needed, use AskUserQuestion to confirm, then:
- Invoke `cui-documentation-standards:adr-management` or `cui-documentation-standards:interface-management`
- Update references via `manage-references:add-file`

### Step 8: Phase Transition

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed refine
```

---

## Operation: create-analysis

**Input**: `plan_id`, `complexity_factors`

**Purpose**: Create analysis.md for complex tasks before refinement.

**Steps**:

1. **Read template**: `Read templates/analysis.md`

2. **Explore codebase** to gather information:
   - Current State: Search for existing implementations
   - Affected Components: Identify files/modules that will change
   - Design Decisions: Document key choices
   - Breaking Changes: Identify compatibility impacts
   - Risks: Assess potential issues

3. **Write**: `Write {plan_directory}/analysis.md`

4. **Present to user** (AskUserQuestion):
   - Show analysis summary
   - Options: Approve / Edit / Add details

5. **Update references**:
   ```bash
   python3 .plan/execute-script.py planning:manage-references:manage-references add-file \
     --plan-id {plan_id} \
     --file analysis.md
   ```

6. **Log**:
   ```bash
   python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
     --plan-id {plan_id} \
     --phase refine \
     --type artifact \
     --summary "Created analysis.md" \
     --detail "Strategic analysis for complex task: {complexity_factors}"
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

### No Task Found

```toon
status: error
error: no_request
message: No request.md found. Re-run init phase.
```

**Resolution**: Return to init phase to create request.md.

### Plan-Type Skill Error

If plan-type skill fails, present options:
- Retry with different parameters
- Manual goal/task creation via manage-goals/manage-tasks
- Skip refine (for simple tasks)

---

## Integration

### Command Integration
- **/plan-manage action=refine** - Invokes this skill

### Skills Used

| Skill | Command | Purpose |
|-------|---------|---------|
| `planning:manage-config` | `get-multi` | Read plan_type, compatibility |
| `planning:manage-goals` | `check` | Verify goal coverage |
| `planning:manage-lifecycle` | `transition` | Phase transition |
| `planning:manage-references` | `add-file` | Track analysis.md, ADRs, interfaces |
| `planning:manage-log` | `add` | Log refine completion |
| `planning:plan-type-{type}` | `decompose`, `plan` | **Delegate Request→GOAL→TASK transformation** |
| `cui-documentation-standards:adr-management` | - | Create ADRs (optional) |
| `cui-documentation-standards:interface-management` | - | Create interfaces (optional) |

### Related Skills
- **plan-init** - Previous phase (creates request.md, config, status)
- **plan-execute** - Next phase (executes tasks)

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/analysis.md` | Strategic analysis for complex tasks |

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Delegates to plan-type:decompose then plan-type:plan
- [x] All file I/O delegated to manage-* scripts
- [x] Optional complexity analysis for complex tasks
- [x] Optional documentation identification (ADRs, interfaces)
