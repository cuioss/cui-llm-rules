---
name: js-task-plan
description: Create implementation tasks from deliverables with direct storage
allowed-tools: Read, Bash
---

# JavaScript Task Plan Skill

**Role**: Domain planning skill for JavaScript implementation tasks. Transforms solution outline deliverables into optimized, executable tasks by applying JavaScript-specific knowledge.

**Key Pattern**: Reads deliverables with metadata from `solution_outline.md`, applies aggregation/split analysis, creates tasks with delegation blocks and dependencies.

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
- Same package? (JS-specific: prefer aggregating within same npm package)
- Same `execution_mode` (must be `automated`)?
- Combined file count < 10?
- **NO dependency between them?** (CRITICAL)

### Step 4: Analyze for Splits

For each deliverable, check for split requirements:
- `execution_mode: mixed` → MUST split
- Production + test code combined → SHOULD split (different domains)
- File count > 15 → CONSIDER splitting

### Step 5: Create Optimized Tasks

For aggregated deliverables or single deliverables, create tasks using heredoc:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
  --plan-id {plan_id} <<'EOF'
title: Implement {component}
deliverables: [{n1}, {n2}, {n3}]
domain: {javascript|javascript-testing}
phase: execute
description: |
  {combined description}

steps:
  - {file1}
  - {file2}
  - {file3}

depends_on: TASK-1, TASK-2

delegation:
  skill: pm-dev-frontend:{js-implement|js-refactor|js-implement-tests}
  workflow: {implement|refactor|implement-tests}
  context_skills:
    - pm-dev-frontend:cui-cypress

verification:
  commands:
    - npm test
  criteria: All tests pass, no lint errors
EOF
```

**Stdin format fields**:
- `deliverables`: Array of deliverable numbers from solution_outline.md
- `domain`: `javascript` for production code, `javascript-testing` for test code
- `delegation.context_skills`: Add `pm-dev-frontend:cui-cypress` for E2E testing

### Step 6: Record Issues as Lessons

On ambiguous deliverable or planning issues:

```bash
python3 .plan/execute-script.py plan-marshall:lessons-learned:manage-lesson add \
  --component-type skill \
  --component-name js-task-plan \
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
1,Implement FormValidator,[1],none
2,Add validation styles,[2],none
3,Add unit tests,[3],"TASK-1" "TASK-2"

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
| `verification.command` | `verification: commands:` |
| `verification.criteria` | `verification: criteria:` |

### JavaScript-Specific Skill Mapping

| Change Type | Component Type | Skill | Workflow |
|-------------|----------------|-------|----------|
| create | module | pm-dev-frontend:js-implement | implement |
| create | test | pm-dev-frontend:js-implement-tests | implement-tests |
| modify | any | pm-dev-frontend:js-implement | implement |
| refactor | any | pm-dev-frontend:js-refactor | refactor |
| fix | lint | pm-dev-frontend:js-enforce-eslint | fix-lint |
| fix | docs | pm-dev-frontend:js-fix-jsdoc | fix-docs |

---

## Task Generation Patterns

### Single Component Task

One deliverable → one task when:
- Single module/class to implement
- Localized change in one file
- Simple feature addition

**Steps**:
1. Create/modify implementation at `{path}`
2. Add unit tests (load `pm-dev-frontend:cui-javascript-unit-testing`)
3. Add JSDoc (load `pm-dev-frontend:cui-jsdoc`)
4. Verify `npm test` passes

### Multi-Step Component Task

One deliverable → multiple tasks when:
- Implementation + tests require separation
- Web component + styles + tests pattern
- Refactoring with multiple phases

**Example for Web Component**:
- TASK-1: Implement component class
- TASK-2: Add component styles
- TASK-3: Add unit tests
- TASK-4: Add E2E tests (if applicable)

---

## Standard Task Steps by Component Type

### Module
```
1. Create module at {path}
2. Export functions/classes
3. Add unit tests (load pm-dev-frontend:cui-javascript-unit-testing)
4. Add JSDoc (load pm-dev-frontend:cui-jsdoc)
5. Verify npm test passes
```

### Class
```
1. Create class at {path}
2. Implement constructor and methods
3. Add unit tests with mocks
4. Add JSDoc (load pm-dev-frontend:cui-jsdoc)
5. Verify npm test passes
```

### Web Component
```
1. Create component class at {path}
2. Define custom element registration
3. Add component styles
4. Add unit tests (load pm-dev-frontend:cui-javascript-unit-testing)
5. Add E2E tests if interactive (load pm-dev-frontend:cui-cypress)
6. Add JSDoc (load pm-dev-frontend:cui-jsdoc)
7. Verify npm test passes
```

### Utility
```
1. Create utility module at {path}
2. Implement pure functions
3. Add comprehensive unit tests
4. Add JSDoc (load pm-dev-frontend:cui-jsdoc)
5. Verify npm test passes
```

### Configuration
```
1. Create/modify config at {path}
2. Add necessary options
3. Verify linting passes
4. Add documentation comments
5. Verify npm run lint passes
```

---

## Task Dependencies

When creating multiple tasks from one deliverable, consider:

| Dependency Type | Ordering |
|-----------------|----------|
| Module before consumer | Dependency first |
| Styles before component | Styles first (if separate) |
| Implementation before tests | If tests need implementation |
| Core before extensions | Foundation first |

---

## Verification Steps

All JavaScript tasks should include verification:

**For npm projects**:
```
Verify `npm test` passes
```

**For linting**:
```
Verify `npm run lint` passes
```

**Final verification**:
```
Run /pm-dev-builder:builder-build-and-fix system=npm
```

---

## Error Handling

### Ambiguous Deliverable

If deliverable doesn't clearly indicate:
- Target path → Ask for clarification
- Component type → Infer from context or ask
- Package placement → Check project structure

### Missing Information

If deliverable lacks detail:
- Generate task with placeholder
- Add lesson-learned for future reference
- Note ambiguity in task description

---

## Integration

**Caller**: `pm-dev-frontend:js-task-plan-agent`

**Script Notations** (use EXACTLY as shown):
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Read solution and list deliverables (list-deliverables, read)
- `pm-workflow:manage-tasks:manage-tasks` - Create tasks (add --plan-id X <<'EOF' ... EOF)
- `plan-marshall:lessons-learned:manage-lesson` - Record lessons on issues (add)

**Standards Referenced in Task Steps**:
- `pm-dev-frontend:cui-javascript` - Core JavaScript patterns
- `pm-dev-frontend:cui-javascript-unit-testing` - Jest testing standards
- `pm-dev-frontend:cui-jsdoc` - JSDoc documentation standards
- `pm-dev-frontend:cui-cypress` - E2E testing (when applicable)

**Contract Reference**:
- [plan-type-api/standards/task-contract.md](../../pm-workflow/skills/plan-type-api/standards/task-contract.md) - Optimization workflow and decision tables
