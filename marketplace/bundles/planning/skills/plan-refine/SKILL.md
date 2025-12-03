---
name: plan-refine
description: Refine phase skill for plan management. Delegates to plan-type skill to transform requirements into specifications and tasks. Optionally creates analysis.md for complex tasks and identifies documentation needs.
allowed-tools: Read, Write, Bash, Skill, AskUserQuestion
---

# Plan Refine Skill

**Role**: Second phase skill. Delegates to plan-type skill to transform requirements into specifications and tasks.

**Execution Pattern**: Detect complexity → Delegate to plan-type:refine → Identify documentation needs → Transition

**CRITICAL**: Use Python scripts via Bash for plan file updates (Edit/Write tools trigger permission prompts on `.plan/` directories).

## Plan-Type Skill API

All plan-type skills implement a uniform `refine` operation:

```
Skill: planning:plan-type-{plan_type}
operation: refine
plan_id: {plan_id}
```

The plan-type skill handles the full REQ → SPEC → TASK transformation:
1. Loads requirements via `manage-requirements:findAll`
2. Creates specifications via `manage-specifications:add`
3. Creates tasks via `manage-tasks:add`
4. Returns confirmation with counts

**No intermediate data passing** - plan-refine only passes `plan_id`.

---

## Primary Operation: refine

**Input**: `plan_id`

**Steps**:

### Step 1: Read Context

```
Skill: planning:manage-config
operation: get
plan_id: {plan_id}
field: plan_type
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

### Step 3: Delegate to Plan-Type Skill

```
Skill: planning:plan-type-{plan_type}
operation: refine
plan_id: {plan_id}
```

**Expected Output**:

```toon
status: success
plan_id: {plan_id}

phase_1:
  requirements_processed: N
  specs_created: N

phase_2:
  specs_processed: N
  tasks_created: N

specifications[N]{number,title,requirements,file}:
...

tasks[N]{number,title,specification,file}:
...
```

**For simple plans**: Returns `status: skipped` (tasks generated during init).

### Step 4: Log Completion

```
Skill: planning:manage-log
operation: add
plan_id: {plan_id}
phase: refine
summary: "Refined plan: {specs_created} specs, {tasks_created} tasks"
```

### Step 5: Identify Documentation Needs (Optional)

Check if ADRs or interfaces should be created:

1. **ADR triggers**: Architectural decisions, security changes, integration patterns
2. **Interface triggers**: New APIs, service contracts, external integrations

If needed, use AskUserQuestion to confirm, then:
- Invoke `cui-documentation-standards:adr-management` or `cui-documentation-standards:interface-management`
- Update references via `manage-references:add-file`

### Step 6: Phase Transition

```
Skill: planning:manage-lifecycle
operation: transition
plan_id: {plan_id}
completed: refine
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
   ```
   Skill: planning:manage-references
   operation: add-file
   plan_id: {plan_id}
   file: analysis.md
   ```

6. **Log**:
   ```
   Skill: planning:manage-log
   operation: add
   plan_id: {plan_id}
   phase: refine
   summary: "Created strategic analysis - analysis.md"
   ```

---

## Error Handling

### No Requirements Found

```toon
status: error
error: no_requirements
message: No requirements found. Add requirements during init phase.
```

**Resolution**: Return to init phase to add requirements.

### Plan-Type Skill Error

If plan-type:refine fails, present options:
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
