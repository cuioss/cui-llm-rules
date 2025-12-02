---
name: plan-type-plugin
description: Plugin development plan type providing 4-phase workflow (init→refine→execute→finalize) with mandatory /plugin-doctor verification for marketplace components.
allowed-tools: Read
---

# Plan Type: Plugin Development

**Phases**: 4 (init→refine→execute→finalize)

**Use Cases**:
- Creating new marketplace components (agents, commands, skills)
- Updating existing marketplace components
- Plugin maintenance and refactoring
- Bundle restructuring

---

## API Summary

All plan-type skills implement this uniform API:

| Operation | Input | Output | Used By |
|-----------|-------|--------|---------|
| `get-phase-structure` | `plan_id`, `task_title` | Phase structure for plan.md | plan-init |
| `generate-tasks` | `plan_id`, `components[]` | **Writes directly** to plan.md | plan-refine |
| `get-finalize-config` | `plan_id` | Finalize behavior (commit, PR) | plan-execute |
| `get-next-phase` | `plan_id`, `current_phase` | Next phase name | phase-management |

**Key Design**: `generate-tasks` writes directly to plan.md via scripts (no ping-pong between skills).

---

## Operation: get-phase-structure

**Input**: `plan_id`, `task_title`

**Output**: Complete phase structure for plan.md

```markdown
# Task Plan: {task_title}

**Configuration**: See [config.toon](./config.toon)
**References**: See [references.toon](./references.toon)

**Current Phase**: init
**Current Task**: task-1

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 0/2 |
| refine | pending | 4 | 0/4 |
| execute | pending | 0 | 0/0 |
| finalize | pending | 3 | 0/3 |

---

## Phase: init (in_progress)

### Task 1: Detect Environment

**Phase**: init
**Goal**: Gather marketplace and plugin context

**Acceptance Criteria**:
- Current branch identified
- Target bundle identified
- Component types to add/modify identified

**Checklist**:
- [ ] Check current git branch
- [ ] Identify target bundle(s) in marketplace/bundles/
- [ ] List components to add or modify
- [ ] Verify plugin.json exists for target bundle
- [ ] **Log**: Record completion in work-log

### Task 2: Confirm Configuration

**Phase**: init
**Goal**: Quick confirmation of defaults

**Acceptance Criteria**:
- User has confirmed settings
- Component scope is clear

**Checklist**:
- [ ] Display detected configuration
- [ ] List components to be created/modified
- [ ] Confirm component naming conventions
- [ ] Transition to refine phase
- [ ] **Log**: Record completion in work-log

---

## Phase: refine (pending)

**Artifacts**: The refine phase produces these artifacts (delegating to `plan-refine` skill):
- `analysis.md` (optional) - Created for complex tasks requiring strategic analysis
- `implementation-requirements.md` - Always created with component breakdown and task details

### Task 1: Assess Complexity

**Phase**: refine
**Goal**: Determine if strategic analysis is needed

**Acceptance Criteria**:
- Complexity assessed using plan-refine criteria
- Decision made: create analysis.md or skip to component breakdown

**Checklist**:
- [ ] Evaluate: Multiple architectural approaches possible?
- [ ] Evaluate: Breaking changes or migrations involved?
- [ ] Evaluate: Cross-cutting concerns across components?
- [ ] Decision: Create analysis.md OR skip to component breakdown
- [ ] **Log**: Record completion in work-log

### Task 2: Strategic Analysis (if complex)

**Phase**: refine
**Goal**: Document design decisions and trade-offs

*Skip this task if complexity assessment determined task is simple.*

**Acceptance Criteria**:
- analysis.md created with design decisions
- Options evaluated with rationale
- Risks identified with mitigations

**Checklist**:
- [ ] Document current state and affected components
- [ ] Record design decisions with alternatives considered
- [ ] Identify breaking changes (if any)
- [ ] Document risks and mitigations
- [ ] **Log**: Record completion in work-log

### Task 3: Component Breakdown

**Phase**: refine
**Goal**: Analyze existing patterns and plan structure

**Acceptance Criteria**:
- Reference components identified
- Patterns documented
- Directory structure planned

**Checklist**:
- [ ] Identify similar existing components in marketplace
- [ ] Analyze file structure and organization patterns
- [ ] Review script patterns (if applicable)
- [ ] Document conventions to follow
- [ ] **Log**: Record completion in work-log

### Task 4: Generate Implementation Requirements

**Phase**: refine
**Goal**: Create implementation-requirements.md with task details

**Acceptance Criteria**:
- implementation-requirements.md created
- Execute phase tasks clearly defined
- Each task has acceptance criteria and guidance

**Checklist**:
- [ ] Define tasks with goals and implementation guidance
- [ ] Add acceptance criteria for each task
- [ ] Include verification task for each component
- [ ] Update plan.md with execute phase tasks
- [ ] **Log**: Record completion in work-log

---

## Phase: execute (pending)

{Tasks generated by refine phase using sub-type templates}

**IMPORTANT**: After all implementation tasks, add verification sub-tasks:

For each component added/modified, add a verification task:
- **verify-{component-type}-{component-name}**: Run `/plugin-doctor {component-type}={component-name}`

---

## Phase: finalize (pending)

### Task 1: Verify All Components

**Phase**: finalize
**Goal**: Run plugin-doctor on all added/modified components

**Acceptance Criteria**:
- All components pass plugin-doctor checks
- No critical issues remaining

**Checklist**:
- [ ] For each added/modified agent: `/plugin-doctor agent={name}`
- [ ] For each added/modified command: `/plugin-doctor command={name}`
- [ ] For each added/modified skill: `/plugin-doctor skill={name}`
- [ ] Address any reported issues
- [ ] Re-run until clean
- [ ] **Log**: Record completion in work-log

### Task 2: Commit Changes

**Phase**: finalize
**Goal**: Commit all changes

**Acceptance Criteria**:
- All changes committed
- Commit message follows conventions

**Checklist**:
- [ ] Stage all changes
- [ ] Create commit with descriptive message
- [ ] Push to branch (if remote)
- [ ] **Log**: Record completion in work-log

### Task 3: Verify Completion

**Phase**: finalize
**Goal**: Ensure task is complete

**Acceptance Criteria**:
- All acceptance criteria met
- Plugin-doctor passes on all components

**Checklist**:
- [ ] Verify all components created/modified
- [ ] Verify plugin.json updated if needed
- [ ] Mark plan complete
- [ ] **Log**: Record completion in work-log

---

## Completion Criteria

Plan is complete when all phase tasks are marked `[x]`.
```

---

## Operation: get-config-template

**Input**: `branch`, `target_bundle`, `component_types`

**Output**: Config format for config.toon

```toon
# Plan Configuration

plan_type: plugin-development
branch: {branch}
issue: none

technology: none
build_system: none

compatibility: breaking
commit_strategy: fine-granular
finalizing: commit-only

# Plugin-specific
target_bundle: {target_bundle}
component_types: {component_types}
```

---

## Operation: get-references-template

**Input**: `branch`, `target_bundle`

**Output**: References format for references.toon

```markdown
# References

## Context

**Branch**: `{branch}`
**Target Bundle**: `{target_bundle}`

## Components

**Components to Add**:
- (populated during execute phase)

**Components to Modify**:
- (populated during execute phase)

## Related Files

**Bundle Path**: marketplace/bundles/{target_bundle}/
**Plugin Config**: marketplace/bundles/{target_bundle}/plugin.json

## Verification Commands

**After completing execute phase, run these verifications**:

```bash
# For agents
/plugin-doctor agent={name}

# For commands
/plugin-doctor command={name}

# For skills
/plugin-doctor skill={name}

# For full bundle
/plugin-doctor metadata
```

## Notes

(add any relevant notes)
```

---

## Operation: generate-tasks

**Input**: `plan_id`, `components[]`

**Purpose**: Generate execute phase tasks and write them directly to plan.md.

**Components Input**: Provided by `cui-plugin-development-tools:plugin-analysis` skill:
```yaml
components:
  - name: "{component-name}"
    type: "script|skill|command|agent"
    scope: "create|modify|refactor"
    bundle: "{bundle-name}"
    path: "{relative-path}"
    dependencies: [...]
    complexity: "low|medium|high"
```

**Process** (internal to this skill):
1. For each component, identify type (script, skill, command, agent)
2. Read corresponding template from `templates/` directory
3. Instantiate template with component context
4. Write tasks directly to plan.md via scripts
5. Return success confirmation

**Task Template Selection**:
| component.type | Template |
|---------------|----------|
| script | `templates/script-task.md` |
| skill | `templates/skill-task.md` |
| command | `templates/command-task.md` |
| agent | `templates/agent-task.md` |

**Write to plan.md**:
```bash
python3 {write-plan.py} --plan-dir .plan/plans/{plan_id} --add-task --phase execute --task-content "{task-yaml}"
```

**Output**:
```yaml
generate_tasks_result:
  status: success
  tasks_written: {count}
  plan_file: .plan/plans/{plan_id}/plan.md
  components_processed:
    - name: "{component-1}"
      task_id: "task-1"
    - name: "{component-2}"
      task_id: "task-2"
```

**Generated Task Structure** (per component):
```yaml
task:
  id: task-{n}
  title: "Create {component-type} {component-name}"
  phase: execute
  goal: "{goal-description}"
  target: "{bundle}:{component-name}"
  acceptance_criteria:
    - "{criterion-1}"
    - "{criterion-2}"
  checklist:
    - "Identify target bundle in marketplace/bundles/"
    - "Load skill: `cui-plugin-development-tools:plugin-create`"
    - "Create/locate {component-type}.md with proper frontmatter"
    - "... (remaining items from internal template)"
    - "**Verify**: `/plugin-doctor {component-type}={component-name}`"
    - "**Log**: Record completion in work-log"
```

**Internal Templates** (in `templates/` directory):
- `script-task.md` - TDD workflow for scripts
- `skill-task.md` - Skill creation workflow
- `command-task.md` - Command orchestration workflow
- `agent-task.md` - Agent frontmatter workflow

---

## Operation: get-next-phase

**Input**: `plan_id`, `current_phase`

**Output**: Next phase in workflow

| Current Phase | Next Phase |
|---------------|------------|
| init | refine |
| refine | execute |
| execute | finalize |
| finalize | complete |

---

## Operation: get-finalize-config

**Input**: `plan_id`

**Purpose**: Returns finalize phase behavior configuration.

**Output**:

```yaml
finalize_config:
  commit_strategy: fine-granular    # fine-granular | phase-specific | complete
  create_pr: false                  # Plugin development doesn't create PRs
  verification_required: true       # Must run /plugin-doctor before finalize
  verification_command: "/plugin-doctor"
```

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 4 |
| Refine Phase | Yes |
| Branch Requirement | Any branch |
| Issue | Not used |
| Build System | None |
| PR Workflow | No |
| **Verification** | `/plugin-doctor` |
| **Component Tracking** | Yes |
| Total Init Tasks | 2 |
| Total Refine Tasks | 4 |
| Total Finalize Tasks | 3 |

---

## Auto-Detection Criteria

Use plugin-development plan type when:
1. Task involves marketplace components (agents, commands, skills)
2. Path contains `marketplace/bundles/`
3. Task mentions "plugin", "component", "agent", "command", or "skill" creation/modification
4. Branch starts with `plugin/`, `component/`, or similar
