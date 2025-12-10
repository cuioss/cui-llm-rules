---
name: plugin-task-plan
description: Create implementation tasks from goals using skill delegation
allowed-tools: Read, Bash
---

# Plugin Plan Skill

**Role**: Domain planning skill for plugin development tasks. Transforms solution goals into executable tasks that delegate to existing skills for implementation.

**Key Pattern**: Skill delegation - reads goals from `solution_outline.md` via `manage-plan-documents`, creates tasks that specify which skill to load and execute. The delegated skills handle validation, creation, and verification internally.

## Operation: plan

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `goal_number` | number | No | Single goal number (omit to process all goals) |

**Process**:

### Step 1: Load Solution Document

Read the solution document to get all goals:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution read \
  --plan-id {plan_id}
```

The output contains:
- `sections.goals` - Markdown with numbered goal sections (`### 1.`, `### 2.`, etc.)
- Parse each `### N. {Title}` section to extract individual goals

### Step 2: For Each Goal

#### 2a. Analyze Goal Content

Parse the goal body to determine:
- **Operation type**: create or modify
- **Component type**: skill, command, agent, script, bundle
- **Target bundle and path**
- **Parameters** for skill delegation

#### 2b. Determine Delegation Target

| Operation | Component | Delegate To |
|-----------|-----------|-------------|
| create | skill | `cui-plugin-development-tools:plugin-create` → create-skill |
| create | command | `cui-plugin-development-tools:plugin-create` → create-command |
| create | agent | `cui-plugin-development-tools:plugin-create` → create-agent |
| create | bundle | `cui-plugin-development-tools:plugin-create` → create-bundle |
| modify | any | `cui-plugin-development-tools:plugin-maintain` → update-component |
| refactor | any | `cui-plugin-development-tools:plugin-maintain` → refactor-structure |

**Note**: Verification is handled internally by the delegated skills - no separate doctor call needed.

#### 2c. Create Task(s)

Generate task(s) with skill delegation steps:

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --goal {n} \
  --title "{action} {component-type}: {name}" \
  --description "{goal description}" \
  --steps \
    "Load skill: {delegated-skill}" \
    "Execute workflow: {workflow-name}" \
    "Parameters: {extracted parameters}"
```

**Note**: The `--goal` parameter is now numeric (e.g., `--goal 1`) referencing the goal section number in solution_outline.md.

#### 2d. Record Issues as Lessons

On ambiguous goal or planning issues:

```bash
python3 .plan/execute-script.py plan-marshall-core:lessons-learned:manage-lesson add \
  --component-type skill \
  --component-name plugin-task-plan \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 3: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}

tasks_created[N]:
- TASK-1: {title}
- TASK-2: {title}

lessons_recorded: {count}
```

---

## Task Generation Patterns

### Create Component Task

**Goal**: "Create new {skill|command|agent} for {purpose}"

**Task Structure**:
```
Title: Create {component-type}: {name}
Steps:
1. Load skill: cui-plugin-development-tools:plugin-create
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
1. Load skill: cui-plugin-development-tools:plugin-create
2. Execute workflow: create-skill
3. Parameters:
   - bundle: cui-java-expert
   - name: java-logging-patterns
   - description: "Java logging standards for CUI projects"
   - type: standards
```

### Modify Component Task

**Goal**: "Update {component} to {change description}"

**Task Structure**:
```
Title: Update {component-type}: {name}
Steps:
1. Load skill: cui-plugin-development-tools:plugin-maintain
2. Execute workflow: update-component
3. Parameters:
   - component_path: {path}
   - improvements: {change description}
```

### Refactor Task

**Goal**: "Refactor {scope} using {strategy}"

**Task Structure**:
```
Title: Refactor {scope}
Steps:
1. Load skill: cui-plugin-development-tools:plugin-maintain
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
1. Load skill: cui-plugin-development-tools:plugin-create
2. Execute workflow: create-skill (if new skill needed)
3. Create script file at {skill}/scripts/{script-name}.py
4. Add test in test/{bundle}/{skill}/
5. Update SKILL.md with script documentation
```

---

## Parameter Extraction

When analyzing goals, extract these parameters:

### For Create Operations

| Parameter | Source |
|-----------|--------|
| `bundle` | Explicit in goal OR inferred from context |
| `name` | Explicit in goal OR derived from purpose |
| `description` | Extracted from goal body |
| `type` | Component-specific (agent type, skill type, etc.) |

### For Modify Operations

| Parameter | Source |
|-----------|--------|
| `component_path` | Explicit path OR resolve from component name |
| `improvements` | Description from goal body |

---

## Multi-Task Goals

Some goals require multiple tasks in sequence:

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

### Ambiguous Goal

If goal doesn't specify:
- **Target bundle** → Ask for clarification
- **Component type** → Infer from keywords or ask
- **Operation type** → Default to create unless "update/modify/fix" present

### Missing Information

If goal lacks required parameters:
- Generate task with available info
- Note missing parameters in task description
- Record lesson for future reference

---

## Integration

**Caller**: `cui-plugin-development-tools:plugin-task-plan-agent`

**Script Notations** (use EXACTLY as shown):
- `planning:manage-solution-outline:manage-solution-outline` - Read solution and list deliverables
- `planning:manage-tasks:manage-task` - Create tasks (add, list)
- `plan-marshall-core:lessons-learned:manage-lesson` - Record lessons on issues (add)
- `planning:manage-log:manage-work-log` - Log progress (add)

**Skills Delegated To**:
- `cui-plugin-development-tools:plugin-create` - Component creation (handles validation and verification internally)
- `cui-plugin-development-tools:plugin-maintain` - Component updates and refactoring (handles verification internally)
