---
name: plugin-task-plan
description: Create implementation tasks from deliverables using skill delegation
allowed-tools: Read, Bash
---

# Plugin Task Plan Skill

**Role**: Domain planning skill for plugin development tasks. Transforms solution outline deliverables into optimized, executable tasks that delegate to existing skills for implementation.

**Key Pattern**: Skill delegation with optimization - reads deliverables with metadata from `solution_outline.md`, applies aggregation/split analysis, creates tasks with delegation blocks and dependencies.

> **Contract Reference**: See [plan-type-api/standards/task-contract.md](../../pm-workflow/skills/plan-type-api/standards/task-contract.md) for the optimization workflow and decision tables.

## Operation: plan

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `deliverable_number` | number | No | Single deliverable number (omit to process all deliverables) |

**Process**:

### Step 1: Load All Deliverables

Read the solution document to get all deliverables with metadata:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline \
  list-deliverables \
  --plan-id {plan_id}
```

For each deliverable, extract:
- `metadata.change_type`, `metadata.execution_mode`, `metadata.domain`
- `metadata.suggested_skill`, `metadata.suggested_workflow`
- `metadata.context_skills`, `metadata.depends`
- `affected_files`, `verification`

### Step 2: Build Dependency Graph

Parse `depends` field for each deliverable:
- Identify independent deliverables (`depends: none`)
- Identify dependency chains
- Detect cycles (INVALID - reject)

### Step 3: Analyze for Aggregation

For each pair of deliverables, check if they can be aggregated:
- Same `change_type`?
- Same `suggested_skill`?
- Same `execution_mode` (must be `automated`)?
- Combined file count < 10?
- **NO dependency between them?** (CRITICAL - cannot aggregate if one depends on other)

### Step 4: Analyze for Splits

For each deliverable, check for split requirements:
- `execution_mode: mixed` → MUST split
- Different concerns within → SHOULD split
- File count > 15 → CONSIDER splitting

### Step 5: Create Optimized Tasks

For aggregated deliverables or single deliverables, create tasks using heredoc:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task add \
  --plan-id {plan_id} <<'EOF'
title: {action} {component-type}: {name}
deliverables: [{n1}, {n2}, {n3}]
domain: plugin
phase: execute
description: |
  {combined description}

steps:
  - {file1}
  - {file2}
  - {file3}

depends_on: TASK-1, TASK-2

delegation:
  skill: pm-plugin-development:{plugin-create|plugin-maintain}
  workflow: {workflow-name}

verification:
  commands:
    - {cmd}
  criteria: {criteria}
EOF
```

**Stdin format fields**:
- `deliverables`: Array of deliverable numbers from solution_outline.md
- `domain`: Always `plugin` for marketplace components
- `depends_on`: Task dependencies computed from deliverable dependencies

### Step 6: Record Issues as Lessons

On ambiguous deliverable or planning issues:

```bash
python3 .plan/execute-script.py plan-marshall:lessons-learned:manage-lesson add \
  --component-type skill \
  --component-name plugin-task-plan \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 7: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}

optimization_summary:
  deliverables_processed: {N}
  tasks_created: {M}
  aggregations: {count of deliverable groups}
  splits: {count of split deliverables}

tasks_created[M]{number,title,deliverables,depends_on}:
1,Create skill: java-logging-patterns,[1],none
2,Update plugin-maintain,[2 3],TASK-1
3,Refactor bundle structure,[4],none

lessons_recorded: {count}
```

---

## Delegation Mapping

When creating tasks, map from deliverable metadata to stdin TOON fields:

| Deliverable Metadata | TOON Field |
|---------------------|------------|
| `domain` | `domain:` |
| `suggested_skill` | `delegation: skill:` |
| `suggested_workflow` | `delegation: workflow:` |
| `context_skills` | `delegation: context_skills:` (merged from all aggregated deliverables) |
| `affected_files` | `steps:` (one per file) |
| `verification.command` | `verification: commands:` (may consolidate) |
| `verification.criteria` | `verification: criteria:` |

### Plugin-Specific Skill Mapping

| Change Type | Component Type | Skill | Workflow |
|-------------|----------------|-------|----------|
| create | skill | pm-plugin-development:plugin-create | create-skill |
| create | command | pm-plugin-development:plugin-create | create-command |
| create | agent | pm-plugin-development:plugin-create | create-agent |
| create | bundle | pm-plugin-development:plugin-create | create-bundle |
| modify | any | pm-plugin-development:plugin-maintain | update-component |
| refactor | any | pm-plugin-development:plugin-maintain | refactor-structure |
| migrate | format | pm-plugin-development:plugin-maintain | update-component |
| delete | any | pm-plugin-development:plugin-maintain | remove-component |

---

## Task Generation Patterns

### Create Component Task

**Deliverable**: "Create new {skill|command|agent} for {purpose}"

**Task Structure**:
```
Title: Create {component-type}: {name}
Steps:
1. Load skill: pm-plugin-development:plugin-create
2. Execute workflow: create-{component-type}
3. Parameters:
   - bundle: {target-bundle}
   - name: {component-name}
   - description: {from goal}
   - type: {component-specific type}
```

**Example**:
```
Title: Create skill: java-logging-patterns
Steps:
1. Load skill: pm-plugin-development:plugin-create
2. Execute workflow: create-skill
3. Parameters:
   - bundle: pm-dev-java
   - name: java-logging-patterns
   - description: "Java logging standards for CUI projects"
   - type: standards
```

### Modify Component Task

**Deliverable**: "Update {component} to {change description}"

**Task Structure**:
```
Title: Update {component-type}: {name}
Steps:
1. Load skill: pm-plugin-development:plugin-maintain
2. Execute workflow: update-component
3. Parameters:
   - component_path: {path}
   - improvements: {change description}
```

### Refactor Task

**Deliverable**: "Refactor {scope} using {strategy}"

**Task Structure**:
```
Title: Refactor {scope}
Steps:
1. Load skill: pm-plugin-development:plugin-maintain
2. Execute workflow: refactor-structure
3. Parameters:
   - scope: {component|bundle|marketplace}
   - strategy: {consolidate|split|extract|reorganize}
```

### Script Task (Special Case)

Scripts are created within skills, so delegate to plugin-create with skill context:

**Task Structure**:
```
Title: Create script: {script-name}
Steps:
1. Load skill: pm-plugin-development:plugin-create
2. Execute workflow: create-skill (if new skill needed)
3. Create script file at {skill}/scripts/{script-name}.py
4. Add test in test/{bundle}/{skill}/
5. Update SKILL.md with script documentation
```

---

## Parameter Extraction

When analyzing deliverables, extract these parameters:

### For Create Operations

| Parameter | Source |
|-----------|--------|
| `bundle` | Explicit in deliverable OR inferred from context |
| `name` | Explicit in deliverable OR derived from purpose |
| `description` | Extracted from deliverable body |
| `type` | Component-specific (agent type, skill type, etc.) |

### For Modify Operations

| Parameter | Source |
|-----------|--------|
| `component_path` | Explicit path OR resolve from component name |
| `improvements` | Description from deliverable body |

---

## Multi-Task Deliverables

Some deliverables require multiple tasks in sequence:

### Skill with Scripts
```
TASK-1: Create skill structure
  - Delegate to: plugin-create → create-skill

TASK-2: Create script(s)
  - Create Python script in skill/scripts/
  - Add test file
  - Update SKILL.md
```

### Command with New Skill
```
TASK-1: Create supporting skill
  - Delegate to: plugin-create → create-skill

TASK-2: Create command
  - Delegate to: plugin-create → create-command
  - Reference skill from TASK-1
```

---

## Task Dependencies

When creating multiple tasks:

| Dependency | Ordering |
|------------|----------|
| Scripts within skill | Create skill first, then scripts |
| Command referencing skill | Create skill first |
| Agent referencing skill | Create skill first |
| Refactor before create | Complete refactor first |

---

## Error Handling

### Ambiguous Deliverable

If deliverable doesn't specify:
- **Target bundle** → Ask for clarification
- **Component type** → Infer from keywords or ask
- **Operation type** → Default to create unless "update/modify/fix" present

### Missing Information

If deliverable lacks required parameters:
- Generate task with available info
- Note missing parameters in task description
- Record lesson for future reference

---

## Integration

**Caller**: `pm-plugin-development:plugin-task-plan-agent`

**Script Notations** (use EXACTLY as shown):
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Read solution and list deliverables (list-deliverables, read)
- `pm-workflow:manage-tasks:manage-task` - Create tasks (add --plan-id X <<'EOF' ... EOF)
- `plan-marshall:lessons-learned:manage-lesson` - Record lessons on issues (add)
- `plan-marshall:logging:manage-log` - Log progress (work)

**Skills Delegated To**:
- `pm-plugin-development:plugin-create` - Component creation (handles validation and verification internally)
- `pm-plugin-development:plugin-maintain` - Component updates and refactoring (handles verification internally)

**Contract Reference**:
- [plan-type-api/standards/task-contract.md](../../pm-workflow/skills/plan-type-api/standards/task-contract.md) - Optimization workflow and decision tables
