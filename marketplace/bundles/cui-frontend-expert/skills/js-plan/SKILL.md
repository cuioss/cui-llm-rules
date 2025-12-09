---
name: js-plan
description: Create implementation tasks from specifications with direct storage
allowed-tools: Read, Bash
---

# JavaScript Plan Skill

**Role**: Domain planning skill for JavaScript implementation tasks. Transforms specifications into executable tasks by applying JavaScript-specific knowledge and writing TASKs directly.

**Key Pattern**: Direct storage - tasks are written immediately via `manage-tasks` script.

## Operation: plan

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `specification_id` | string | No | Single SPEC ID (omit for batch - queries all pending) |

**Process**:

### Step 1: Load Specifications

**Batch mode** (no specification_id):
```bash
python3 .plan/execute-script.py planning:manage-specifications:manage-specification findAll \
  --plan-id {plan_id}
```

**Single mode** (specification_id provided):
```bash
python3 .plan/execute-script.py planning:manage-specifications:manage-specification get \
  --plan-id {plan_id} \
  --number {specification_id}
```

### Step 2: For Each Specification

#### 2a. Analyze Specification Content

Parse the specification body to determine:
- Component type and target path
- Task granularity (single task or multiple)
- JavaScript-specific implementation steps
- Test requirements
- Standards to apply

#### 2b. Create Task(s)

Generate task(s) with JavaScript-specific steps:

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --specification SPEC-{n} \
  --title "Implement {component}" \
  --description "{goal from specification}" \
  --steps \
    "Create/modify implementation at {path}" \
    "Add unit tests (load cui-frontend-expert:cui-javascript-unit-testing)" \
    "Add JSDoc (load cui-frontend-expert:cui-jsdoc)" \
    "Follow CUI patterns (load cui-frontend-expert:cui-javascript)" \
    "Verify npm test passes"
```

#### 2c. Record Issues as Lessons

On ambiguous specification or planning issues:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component-type skill \
  --component-name js-plan \
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

One specification → one task when:
- Single module/class to implement
- Localized change in one file
- Simple feature addition

**Steps**:
1. Create/modify implementation at `{path}`
2. Add unit tests (load `cui-frontend-expert:cui-javascript-unit-testing`)
3. Add JSDoc (load `cui-frontend-expert:cui-jsdoc`)
4. Verify `npm test` passes

### Multi-Step Component Task

One specification → multiple tasks when:
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
3. Add unit tests (load cui-frontend-expert:cui-javascript-unit-testing)
4. Add JSDoc (load cui-frontend-expert:cui-jsdoc)
5. Verify npm test passes
```

### Class
```
1. Create class at {path}
2. Implement constructor and methods
3. Add unit tests with mocks
4. Add JSDoc (load cui-frontend-expert:cui-jsdoc)
5. Verify npm test passes
```

### Web Component
```
1. Create component class at {path}
2. Define custom element registration
3. Add component styles
4. Add unit tests (load cui-frontend-expert:cui-javascript-unit-testing)
5. Add E2E tests if interactive (load cui-frontend-expert:cui-cypress)
6. Add JSDoc (load cui-frontend-expert:cui-jsdoc)
7. Verify npm test passes
```

### Utility
```
1. Create utility module at {path}
2. Implement pure functions
3. Add comprehensive unit tests
4. Add JSDoc (load cui-frontend-expert:cui-jsdoc)
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

When creating multiple tasks from one specification, consider:

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
Run /builder:builder-build-and-fix system=npm
```

---

## Error Handling

### Ambiguous Specification

If specification doesn't clearly indicate:
- Target path → Ask for clarification
- Component type → Infer from context or ask
- Package placement → Check project structure

### Missing Information

If specification lacks detail:
- Generate task with placeholder
- Add lesson-learned for future reference
- Note ambiguity in task description

---

## Integration

**Caller**: `cui-frontend-expert:js-plan-agent`

**Scripts Used**:
- `planning:manage-specifications` - Load specifications
- `planning:manage-tasks` - Create tasks
- `planning:manage-lessons` - Record lessons on issues

**Standards Referenced in Task Steps**:
- `cui-frontend-expert:cui-javascript` - Core JavaScript patterns
- `cui-frontend-expert:cui-javascript-unit-testing` - Jest testing standards
- `cui-frontend-expert:cui-jsdoc` - JSDoc documentation standards
- `cui-frontend-expert:cui-cypress` - E2E testing (when applicable)
