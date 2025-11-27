---
name: plan-refine
description: Refine phase skill for plan management. Analyzes requirements into components, creates detailed implementation tasks with acceptance criteria, and identifies documentation needs (ADRs, interfaces). Generates implementation-requirements.md artifact.
allowed-tools: Read, Write, Edit, Skill, AskUserQuestion
---

# Plan Refine Skill

**EXECUTION MODE**: Execute refine operations immediately. Do not explain or summarize.

**Role**: Second phase skill in the plan management system. Breaks down requirements into implementable tasks with acceptance criteria. Delegates all file I/O to `plan-files` skill.

## Standards (Load On-Demand)

### Workflow
```
Read standards/workflow.md
```
Contains: Phase overview, operations, component analysis, task planning, documentation triggers

### Templates

| Template | Purpose |
|----------|---------|
| `templates/implementation-requirements.md` | Implementation requirements artifact |

---

## Operation: analyze

**Input**: `plan_directory`

**Steps**:

1. **Read context**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-plan, read-config, get-references
   ```

2. **Fetch issue** (if URL): `gh issue view {number} --json title,body,labels`

3. **Identify components**:
   - Functional components (features, APIs, services)
   - Technical boundaries (modules, packages, layers)
   - Dependencies between components
   - Complexity estimates (low/medium/high)

4. **Present analysis** (AskUserQuestion):
   - Component list with scope and complexity
   - Dependency mapping
   - Options: Proceed / Modify / Re-analyze

**Output**: `components[N]: {name, scope, complexity, dependencies}`

---

## Operation: plan-tasks

**Input**: `plan_directory`, `components`

**Steps**:

1. **Generate tasks per component**:
   - Create implementation task(s)
   - Add technology-specific checklist (see `standards/workflow.md`)
   - Define acceptance criteria
   - Add quality checklist items

2. **Order by dependencies**

3. **Present task list** (AskUserQuestion):
   - Task table with complexity and dependencies
   - Options: Proceed / View details / Modify / Adjust granularity

4. **Add tasks to plan**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: write-plan
   ```

**Output**: `tasks[N]: {id, name, complexity, dependencies, acceptance_criteria}`

---

## Operation: identify-docs

**Input**: `plan_directory`, `tasks`

**Steps**:

1. **Analyze for ADR needs** (architectural decisions, security, integration, performance)

2. **Prompt for ADR** (AskUserQuestion):
   - Create new ADR (invoke adr-management)
   - Link existing ADR
   - Skip

3. **Analyze for interface needs** (new APIs, service interfaces, external integrations)

4. **Prompt for interface** (AskUserQuestion):
   - Create new Interface (invoke interface-management)
   - Link existing Interface
   - Skip

5. **Update references**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: write-references
   action: add
   reference_type: adr|interface
   ```

**Output**: `adrs_linked[N]`, `interfaces_linked[N]`

---

## Generate Implementation Requirements

After all refine tasks complete:

1. **Read template**: `Read templates/implementation-requirements.md`

2. **Populate**:
   - Component summary table
   - Task details with acceptance criteria
   - Dependency graph
   - Quality gates

3. **Write**: `Write {plan_directory}/implementation-requirements.md`

---

## Phase Transition

After all refine tasks complete:

```
Skill: cui-task-workflow:plan-files
operation: update-progress
plan_directory: {plan_directory}
task_id: {last-refine-task}
status: completed
```

This updates: current_phase → implement, current_task → first implement task

---

## Error Handling

### Missing Issue Content
Options: Retry / Enter manually / Proceed without

### Invalid References
Options: Create missing / Remove reference / Mark as TODO

### Incomplete Analysis
Options: Define scope / Remove component / Mark as TODO

---

## Integration

### Skills Used
- **plan-files** - All file I/O operations
- **adr-management** - ADR creation and verification
- **interface-management** - Interface creation and verification

### Related Skills
- **plan-init** - Previous phase
- **plan-implement** - Next phase
- **plan-verify** - Verification phase
- **plan-finalize** - Finalization phase

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Progressive disclosure (load on-demand)
- [x] All file I/O delegated to plan-files skill
- [x] User confirmation for all decisions
- [x] Implementation requirements artifact generated
