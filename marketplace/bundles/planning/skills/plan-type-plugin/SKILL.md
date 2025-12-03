---
name: plan-type-plugin
description: Plugin development plan type providing 4-phase workflow (init→refine→execute→finalize) with mandatory /plugin-doctor verification
allowed-tools: Read
---

# Plan Type: Plugin Development

**Phases**: 4 (init → refine → execute → finalize)

**Use Cases**:
- Creating new marketplace components (agents, commands, skills)
- Updating existing marketplace components
- Plugin maintenance and refactoring
- Bundle restructuring

**Analysis Skill**: `cui-plugin-development-tools:plugin-analysis`

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 4 |
| Technology | none |
| Build System | none |
| Analysis Skill | `cui-plugin-development-tools:plugin-analysis` |
| Branch Required | false |
| Issue Required | false |
| PR Workflow | false |
| Verification | `/plugin-doctor` |

---

## Operation: get-phase-structure

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`, `task_title`

**Output**:

```toon
status: success
current_phase: init
initial_status: pending

phases[4]{name,order}:
init,1
refine,2
execute,3
finalize,4

phase_tasks:
  init:
    - title: Detect Environment
      steps: git branch --show-current, Identify target bundle in marketplace/bundles/
    - title: Analyze Task
      steps: Read task.md, List components to create/modify, Determine scope
    - title: Detect Plan Type
      steps: Verify plugin-development type, Confirm target bundle
    - title: Confirm Configuration
      steps: Display config, List components, Confirm naming conventions
  refine:
    - title: Assess Complexity
      steps: Evaluate approaches, Evaluate changes, Evaluate cross-cutting, Decide
    - title: Component Breakdown
      steps: Identify similar components, Analyze patterns, Review scripts, Document
    - title: Generate Tasks
      steps: Create TASK files via manage-tasks, Use templates, Include verification
  execute: (generated dynamically)
  finalize:
    - title: Verify All Components
      steps: Run /plugin-doctor for each, Address issues, Re-run until clean
    - title: Commit Changes
      steps: Stage changes, Create commit, Push branch
    - title: Verify Completion
      steps: Verify components, Verify plugin.json, Mark complete
```

---

## Operation: get-config-template

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `branch`, `target_bundle`, `component_types`

**Output**:

```toon
plan_type: plugin-development
branch: {branch}
issue: none

technology: none
build_system: none

compatibility: breaking
commit_strategy: fine-granular
finalizing: commit-only

target_bundle: {target_bundle}
component_types: {component_types}
```

---

## Operation: get-references-template

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `branch`, `target_bundle`

**Output**:

```toon
branch: {branch}
base_branch: main

target_bundle: {target_bundle}
bundle_path: marketplace/bundles/{target_bundle}/
plugin_config: marketplace/bundles/{target_bundle}/plugin.json

components:
  add: []
  modify: []

verification_commands:
  - "/plugin-doctor agent={name}"
  - "/plugin-doctor command={name}"
  - "/plugin-doctor skill={name}"
  - "/plugin-doctor metadata"

notes: []
```

---

## Operation: generate-tasks

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`, `components[]`

**Components Input** (from `cui-plugin-development-tools:plugin-analysis`):

```toon
components[3]{name,type,scope,bundle,path,complexity}:
manage-auth,skill,create,planning,skills/manage-auth/,medium
auth-workflow,command,create,planning,commands/auth-workflow.md,low
auth-doctor,agent,create,planning,agents/auth-doctor.md,low
```

**Process**:

1. For each component, call `manage-task.py add` (writes directly to disk)
2. Use templates for component-specific steps
3. Add verification step for each component

**Task Generation**:

```bash
python3 manage-task.py add \
  --plan-id {plan_id} \
  --specification SPEC-{n} \
  --title "Create {type} {component-name}" \
  --description "Create/modify {type} in {bundle}" \
  --steps \
    "Identify target bundle in marketplace/bundles/" \
    "Load skill: cui-plugin-development-tools:plugin-create" \
    "Create/locate {type}.md with proper frontmatter" \
    "{type-specific steps from template}" \
    "Verify: /plugin-doctor {type}={component-name}"
```

**Task Template Selection**:

| Component Type | Template | Key Steps |
|----------------|----------|-----------|
| script | `templates/script-task.md` | TDD workflow, test file, implementation |
| skill | `templates/skill-task.md` | SKILL.md, standards/, scripts/ |
| command | `templates/command-task.md` | Frontmatter, workflow, delegation |
| agent | `templates/agent-task.md` | Frontmatter, tool selection, focus |

**Output** (confirmation only, tasks already written):

```toon
status: success
plan_id: {plan_id}
tasks_created: 3

tasks[3]{number,title,specification,file}:
1,Create skill manage-auth,SPEC-1,TASK-001-create-skill-manage-auth.toon
2,Create command auth-workflow,SPEC-1,TASK-002-create-command-auth-workflow.toon
3,Create agent auth-doctor,SPEC-1,TASK-003-create-agent-auth-doctor.toon
```

---

## Operation: get-next-phase

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `current_phase`

**Phase Transitions**:

| Current Phase | Next Phase |
|---------------|------------|
| init | refine |
| refine | execute |
| execute | finalize |
| finalize | complete |

**Output**:

```toon
status: success
phase: {next}
```

---

## Operation: get-finalize-config

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`

**Output**:

```toon
status: success
commit_strategy: fine-granular
create_pr: false
verification_required: true
verification_command: /plugin-doctor
branch_strategy: direct
```

---

## Templates

Internal templates for component-specific task generation (in `templates/` directory):

| Template | Purpose |
|----------|---------|
| `script-task.md` | TDD workflow for Python scripts |
| `skill-task.md` | Skill creation with SKILL.md structure |
| `command-task.md` | Command orchestration patterns |
| `agent-task.md` | Agent frontmatter and tool selection |

---

## Quality Checklist

- [x] Loads `planning:plan-type-api` for contract reference
- [x] Implements all 7 operations with correct signatures
- [x] Uses manage-tasks skill for task generation
- [x] Returns `status` field in all outputs
- [x] Defines phase transition matrix (4 phases)
- [x] Defines characteristics matrix
- [x] Handles errors with status and message
- [x] Includes verification via `/plugin-doctor`
