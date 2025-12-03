---
name: plan-type-plugin
description: Plugin development plan type providing 4-phase workflow (init→refine→execute→finalize) with mandatory /plugin-doctor verification
allowed-tools: Read, Bash
---

# Plan Type: Plugin Development

**Phases**: 4 (init → refine → execute → finalize)

**Use Cases**:
- Creating new marketplace components (agents, commands, skills)
- Updating existing marketplace components
- Plugin maintenance and refactoring
- Bundle restructuring

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 4 |
| Technology | none |
| Build System | none |
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
    - title: Add Requirements
      steps: Create REQ files via manage-requirements
    - title: Detect Plan Type
      steps: Verify plugin-development type, Confirm target bundle
    - title: Confirm Configuration
      steps: Display config, List components, Confirm naming conventions
  refine:
    - title: Refine Plan
      steps: Call plan-type-plugin:refine, Iterates REQ→SPEC→TASK
  execute: (generated dynamically from TASK files)
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

**Input**: (none)

**Output**:

```toon
plan_type: plugin-development
compatibility: breaking
commit_strategy: fine-granular
```

**Note**: `target_bundle` and `component_types` are stored in references.toon, not config.toon.

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

## Operation: refine

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`

**Process**:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Requirements → Specifications                             │
├─────────────────────────────────────────────────────────────────────┤
│  1. Load requirements:                                              │
│     python3 {manage-requirement.py} findAll --plan-id {plan_id}     │
│                                                                     │
│  2. FOR EACH requirement:                                           │
│     - Analyze plugin-specific implications                          │
│     - Identify affected components (skill, command, agent, script)  │
│     - Create specification with component details:                  │
│       python3 {manage-specification.py} add \                       │
│         --plan-id {plan_id} \                                       │
│         --title "{component-type} {name}" \                         │
│         --requirements "REQ-{n}" \                                  │
│         --body "{component structure, standards, patterns}"         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Specifications → Tasks                                    │
├─────────────────────────────────────────────────────────────────────┤
│  3. Load specifications:                                            │
│     python3 {manage-specification.py} findAll --plan-id {plan_id}   │
│                                                                     │
│  4. FOR EACH specification:                                         │
│     - Generate creation task with component-specific steps          │
│     - Add verification step                                         │
│     python3 {manage-task.py} add \                                  │
│       --plan-id {plan_id} \                                         │
│       --specification SPEC-{n} \                                    │
│       --title "Create {type} {name}" \                              │
│       --description "{goal}" \                                      │
│       --steps \                                                     │
│         "Identify target bundle" \                                  │
│         "Load skill: cui-plugin-development-tools:plugin-create" \  │
│         "Create {type}.md with proper frontmatter" \                │
│         "{type-specific steps}" \                                   │
│         "Verify: /plugin-doctor {type}={name}"                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Plugin-Specific Specification Content**:

When creating specifications, include:
- Component type (skill, command, agent, script)
- Target bundle location
- Frontmatter requirements
- Standards to follow
- Integration points

**Plugin-Specific Task Steps by Component Type**:

| Component Type | Key Steps |
|----------------|-----------|
| skill | Create SKILL.md, Add standards/, Add scripts/, Register in plugin.json |
| command | Create command.md, Define workflow, Add delegation |
| agent | Create agent.md, Select tools, Define focus |
| script | Create test file first (TDD), Implement script, Verify tests pass |

**Output**:

```toon
status: success
plan_id: {plan_id}

phase_1:
  requirements_processed: 2
  specs_created: 3

phase_2:
  specs_processed: 3
  tasks_created: 3

specifications[3]{number,title,requirements,file}:
1,Skill manage-auth,REQ-1,SPEC-001-skill-manage-auth.toon
2,Command auth-workflow,REQ-1,SPEC-002-command-auth-workflow.toon
3,Agent auth-doctor,REQ-2,SPEC-003-agent-auth-doctor.toon

tasks[3]{number,title,specification,file}:
1,Create skill manage-auth,SPEC-1,TASK-001-create-skill-manage-auth.toon
2,Create command auth-workflow,SPEC-2,TASK-002-create-command-auth-workflow.toon
3,Create agent auth-doctor,SPEC-3,TASK-003-create-agent-auth-doctor.toon
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
- [x] Implements all 6 operations with correct signatures
- [x] Uses manage-* tools for all data I/O
- [x] Returns `status` field in all outputs
- [x] Defines phase transition matrix (4 phases)
- [x] Defines characteristics matrix
- [x] Handles errors with status and message
- [x] refine operation iterates REQ→SPEC→TASK with plugin-specific content
- [x] Includes verification via `/plugin-doctor`
