---
name: plan-refine
description: Refine phase skill for plan management. Delegates to plan-type skill to transform requirements into specifications and tasks. Optionally creates analysis.md for complex tasks and identifies documentation needs.
allowed-tools: Read, Write, Bash, Skill, Task, AskUserQuestion
---

# Plan Refine Skill

**Role**: Second phase skill. Delegates to plan-type skill to transform requirements into specifications and tasks.

**Execution Pattern**: Detect complexity → Delegate to plan-type:specify → Delegate to plan-type:plan → Identify documentation needs → Transition

**CRITICAL**: Use Python scripts via Bash for plan file updates (Edit/Write tools trigger permission prompts on `.plan/` directories).

---

## Script Path Resolution

**MANDATORY**: Before executing any script, resolve paths via script-runner.

```
Skill: general-tools:script-runner
Resolve: planning:manage-config/scripts/manage-config.py
Resolve: planning:manage-lifecycle/scripts/manage-lifecycle.py
Resolve: planning:manage-log/scripts/manage-work-log.py
Resolve: planning:manage-references/scripts/manage-references.py
```

Use the resolved absolute paths in all Bash commands.

---

## Plan-Type Skill API

All plan-type skills implement two operations for refinement:

**1. specify** - Transform REQ → SPEC:
```
Skill: planning:plan-type-{plan_type}
operation: specify
plan_id: {plan_id}
```

**2. plan** - Transform SPEC → TASK:
```
Skill: planning:plan-type-{plan_type}
operation: plan
plan_id: {plan_id}
```

The plan-type skills delegate to domain agents which write directly:
- Domain agents create specifications via `manage-specifications:add`
- Domain agents create tasks via `manage-tasks:add`
- Domain agents record lessons-learned on issues

**No intermediate data passing** - plan-refine only passes `plan_id`.

---

## Primary Operation: refine

**Input**: `plan_id`

**Steps**:

### Step 0: Log Phase Start

Script: `planning:manage-log/scripts/manage-work-log.py`

```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Starting refine phase"
```

### Step 1: Read Context

Script: `planning:manage-config/scripts/manage-config.py`

```bash
python3 {resolved_manage_config} read \
  --plan-id {plan_id}
```

Extract: `plan_type` (java, javascript, plugin-development, simple)

### Step 2: Detect Complexity (Optional)

For complex tasks, create analysis.md first:

| Question | If YES → Create analysis.md |
|----------|----------------------------|
| Are multiple components affected? | Yes |
| Are there breaking changes? | Yes |
| Are there architectural decisions? | Yes |
| Are there complex dependencies? | Yes |

If complexity detected → Execute `create-analysis` operation before continuing.

### Step 3: Delegate to Plan-Type Skill (specify)

```
Skill: planning:plan-type-{plan_type}
operation: specify
plan_id: {plan_id}
```

**Expected Output**:

```toon
status: success
plan_id: {plan_id}

specs_created[N]:
- SPEC-1
- SPEC-2
- SPEC-3

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

### Step 5: Log Completion

Script: `planning:manage-log/scripts/manage-work-log.py`

```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "Completed refine: {specs_created} specs, {tasks_created} tasks" \
  --detail "Specifications and tasks created via {plan_type} domain agents"
```

### Step 6: Identify Documentation Needs (Optional)

Check if ADRs or interfaces should be created:

1. **ADR triggers**: Architectural decisions, security changes, integration patterns
2. **Interface triggers**: New APIs, service contracts, external integrations

If needed, use AskUserQuestion to confirm, then:
- Invoke `cui-documentation-standards:adr-management` or `cui-documentation-standards:interface-management`
- Update references via `manage-references:add-file`

### Step 7: Phase Transition

Script: `planning:manage-lifecycle/scripts/manage-lifecycle.py`

```bash
python3 {resolved_manage_lifecycle} transition \
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
   python3 {resolved_manage_references} add-file \
     --plan-id {plan_id} \
     --file analysis.md
   ```

6. **Log**:
   ```bash
   python3 {resolved_manage_work_log} add \
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
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase refine \
  --type error \
  --summary "ERROR: {error_type}" \
  --detail "{full error context and message}"
```

### No Requirements Found

```toon
status: error
error: no_requirements
message: No requirements found. Add requirements during init phase.
```

**Resolution**: Return to init phase to add requirements.

### Plan-Type Skill Error

If plan-type skill fails, present options:
- Retry with different parameters
- Manual task creation via manage-tasks
- Skip refine (for simple tasks)

---

## Integration

### Command Integration
- **/plan-manage action=refine** - Invokes this skill

### Skills Used

| Skill | Purpose |
|-------|---------|
| `planning:manage-config` | Read plan_type |
| `planning:manage-lifecycle` | Phase transition |
| `planning:manage-references` | Track analysis.md, ADRs, interfaces |
| `planning:manage-log` | Log refine completion |
| `planning:plan-type-{type}` | **Delegate REQ→SPEC→TASK transformation** |
| `cui-documentation-standards:adr-management` | Create ADRs (optional) |
| `cui-documentation-standards:interface-management` | Create interfaces (optional) |

### Related Skills
- **plan-init** - Previous phase (creates requirements)
- **plan-execute** - Next phase (executes tasks)

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/analysis.md` | Strategic analysis for complex tasks |

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Single delegation to plan-type:refine (no intermediate data)
- [x] All file I/O delegated to manage-* skills
- [x] Optional complexity analysis for complex tasks
- [x] Optional documentation identification (ADRs, interfaces)
