---
name: js-task-plan
description: Create implementation tasks from deliverables with direct storage
allowed-tools: Read, Bash
---

# JavaScript Task Plan Skill

**Role**: Domain planning skill for JavaScript implementation tasks. Transforms solution outline deliverables into executable tasks by applying JavaScript-specific knowledge and writing TASKs directly.

**Key Pattern**: Reads deliverables from `solution_outline.md` via `manage-solution-outline`, creates tasks via `manage-tasks` script.

## Operation: plan

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `deliverable_number` | number | No | Single deliverable number (omit to process all deliverables) |

**Process**:

### Step 1: Load Solution Document

Read the solution document to get all deliverables:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline \
  list-deliverables \
  --plan-id {plan_id}
```

The output contains an array of deliverables with `number` and `title` fields. Use `read` for full document content if needed.

### Step 2: For Each Deliverable

#### 2a. Analyze Deliverable Content

Parse the deliverable body to determine:
- Component type and target path
- Task granularity (single task or multiple)
- JavaScript-specific implementation steps
- Test requirements
- Standards to apply

#### 2b. Create Task(s)

Generate task(s) with JavaScript-specific steps:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --goal {n} \
  --title "Implement {component}" \
  --description "{goal from solution}" \
  --steps \
    "Create/modify implementation at {path}" \
    "Add unit tests (load pm-dev-frontend:cui-javascript-unit-testing)" \
    "Add JSDoc (load pm-dev-frontend:cui-jsdoc)" \
    "Follow CUI patterns (load pm-dev-frontend:cui-javascript)" \
    "Verify npm test passes"
```

**Note**: The `--goal` parameter is numeric (e.g., `--goal 1`) referencing the deliverable section number in solution_outline.md.

#### 2c. Record Issues as Lessons

On ambiguous deliverable or planning issues:

```bash
python3 .plan/execute-script.py pm-core:lessons-learned:manage-lesson add \
  --component-type skill \
  --component-name js-task-plan \
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
- TASK-1
- TASK-2
- TASK-3
- TASK-4
- TASK-5

lessons_recorded: {count}
```

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
Run /pm-builder:builder-build-and-fix system=npm
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
- `pm-workflow:manage-tasks:manage-task` - Create tasks (add --goal N --title --steps)
- `pm-core:lessons-learned:manage-lesson` - Record lessons on issues (add)

**Standards Referenced in Task Steps**:
- `pm-dev-frontend:cui-javascript` - Core JavaScript patterns
- `pm-dev-frontend:cui-javascript-unit-testing` - Jest testing standards
- `pm-dev-frontend:cui-jsdoc` - JSDoc documentation standards
- `pm-dev-frontend:cui-cypress` - E2E testing (when applicable)
