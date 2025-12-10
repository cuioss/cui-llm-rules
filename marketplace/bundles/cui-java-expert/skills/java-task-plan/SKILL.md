---
name: java-task-plan
description: Create implementation tasks from goals with direct storage
allowed-tools: Read, Bash
---

# Java Plan Skill

**Role**: Domain planning skill for Java implementation tasks. Transforms solution goals into executable tasks by applying Java-specific knowledge and writing TASKs directly.

**Key Pattern**: Reads goals from `solution_outline.md` via `manage-plan-documents`, creates tasks via `manage-tasks` script.

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
- Component type and target path
- Task granularity (single task or multiple)
- Java-specific implementation steps
- Test requirements
- Standards to apply

#### 2b. Create Task(s)

Generate task(s) with Java-specific steps:

```bash
python3 .plan/execute-script.py planning:manage-tasks:manage-task add \
  --plan-id {plan_id} \
  --goal {n} \
  --title "Implement {component}" \
  --description "{goal from solution}" \
  --steps \
    "Create/modify implementation at {path}" \
    "Add unit tests (load cui-java-expert:cui-java-unit-testing)" \
    "Add JavaDoc (load cui-java-expert:cui-javadoc)" \
    "Follow CUI patterns (load cui-java-expert:cui-java-core)" \
    "Verify build passes"
```

**Note**: The `--goal` parameter is now numeric (e.g., `--goal 1`) referencing the goal section number in solution_outline.md.

#### 2c. Record Issues as Lessons

On ambiguous goal or planning issues:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component-type skill \
  --component-name java-task-plan \
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

One goal → one task when:
- Single class/interface to implement
- Localized change in one file
- Simple feature addition

**Steps**:
1. Create/modify implementation at `{path}`
2. Add unit tests (load `cui-java-expert:cui-java-unit-testing`)
3. Add JavaDoc (load `cui-java-expert:cui-javadoc`)
4. Verify `mvn test -pl {module}` passes

### Multi-Step Component Task

One goal → multiple tasks when:
- Implementation + tests require separation
- Config + service + controller pattern
- Refactoring with multiple phases

**Example for Service + Repository**:
- TASK-1: Implement repository interface and class
- TASK-2: Implement service with repository injection
- TASK-3: Add unit tests for both components
- TASK-4: Add integration tests

---

## Standard Task Steps by Component Type

### Service Class
```
1. Create service interface at {interface_path}
2. Create service implementation at {impl_path}
3. Add CDI annotations (@ApplicationScoped, @Inject)
4. Add unit tests (load cui-java-expert:cui-java-unit-testing)
5. Add JavaDoc (load cui-java-expert:cui-javadoc)
6. Verify build passes
```

### Repository Class
```
1. Create repository interface at {interface_path}
2. Create repository implementation at {impl_path}
3. Add data access logic with proper exception handling
4. Add integration tests (load cui-java-expert:cui-java-unit-testing)
5. Add JavaDoc (load cui-java-expert:cui-javadoc)
6. Verify build passes
```

### Configuration Class
```
1. Create configuration class at {path}
2. Add @ConfigProperty annotations for properties
3. Add validation logic if needed
4. Add unit tests for configuration validation
5. Add JavaDoc (load cui-java-expert:cui-javadoc)
6. Verify build passes
```

### Controller/Resource Class
```
1. Create resource class at {path}
2. Add JAX-RS annotations (@Path, @GET, @POST, etc.)
3. Inject required services
4. Add validation and error handling
5. Add integration tests
6. Add OpenAPI annotations if applicable
7. Verify build passes
```

---

## Task Dependencies

When creating multiple tasks from one goal, consider:

| Dependency Type | Ordering |
|-----------------|----------|
| Interface before implementation | Interface task first |
| Repository before service | Data layer first |
| Config before dependent classes | Configuration first |
| Implementation before tests | If tests need implementation |

---

## Verification Steps

All Java tasks should include verification:

**For Maven projects**:
```
Verify `mvn test -pl {module}` passes
```

**For Gradle projects**:
```
Verify `./gradlew :{module}:test` passes
```

**Final verification**:
```
Run /builder:builder-build-and-fix
```

---

## Error Handling

### Ambiguous Goal

If goal doesn't clearly indicate:
- Target path → Ask for clarification
- Component type → Infer from context or ask
- Module placement → Check project structure

### Missing Information

If goal lacks detail:
- Generate task with placeholder
- Add lesson-learned for future reference
- Note ambiguity in task description

---

## Integration

**Caller**: `cui-java-expert:java-task-plan-agent`

**Scripts Used**:
- `planning:manage-plan-documents` - Read solution document (solution read)
- `planning:manage-tasks` - Create tasks
- `planning:manage-lessons` - Record lessons on issues

**Standards Referenced in Task Steps**:
- `cui-java-expert:cui-java-core` - Core Java patterns
- `cui-java-expert:cui-java-unit-testing` - Testing standards
- `cui-java-expert:cui-javadoc` - Documentation standards
- `cui-java-expert:cui-java-cdi` - CDI/Quarkus patterns (when applicable)
