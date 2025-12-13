---
name: java-task-plan
description: Create implementation tasks from deliverables with direct storage
allowed-tools: Read, Bash
---

# Java Task Plan Skill

**Role**: Domain planning skill for Java implementation tasks. Transforms solution outline deliverables into optimized, executable tasks by applying Java-specific knowledge.

**Key Pattern**: Reads deliverables with metadata from `solution_outline.md`, applies aggregation/split analysis, creates tasks with delegation blocks and dependencies.

## Contract Compliance

**MANDATORY**: All tasks MUST follow the structure defined in the central contracts:

| Contract | Location | Purpose |
|----------|----------|---------|
| Task Contract | `pm-workflow:plan-type-api/standards/task-contract.md` | Required task structure and optimization workflow |
| Task-Plan Agent Contract | `pm-workflow:plan-type-api/standards/task-plan-agent-contract.md` | Agent responsibilities |

**CRITICAL - Steps Field**:
- The `steps` field MUST contain file paths from the deliverable's `Affected files` section
- Steps must NOT be descriptive text (e.g., "Update AuthController.java" is INVALID)
- Validation rejects tasks with non-file-path steps

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
- Same module? (Java-specific: prefer aggregating within same Maven module)
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
domain: {java|java-testing}
phase: execute
description: |
  {combined description}

steps:
  - {file1}
  - {file2}
  - {file3}

depends_on: TASK-1, TASK-2

delegation:
  skill: pm-dev-java:{java-implement|java-refactor|java-implement-tests}
  workflow: {implement|refactor|implement-tests}
  context_skills:
    - pm-dev-java:java-cdi

verification:
  commands:
    - mvn test -pl {module}
  criteria: Build and tests pass
EOF
```

**Stdin format fields**:
- `deliverables`: Array of deliverable numbers from solution_outline.md
- `domain`: `java` for production code, `java-testing` for test code
- `delegation.context_skills`: Add `pm-dev-java:java-cdi` when CDI/Quarkus patterns needed

### Step 6: Record Issues as Lessons

On ambiguous deliverable or planning issues:

```bash
python3 .plan/execute-script.py plan-marshall:lessons-learned:manage-lesson add \
  --component-type skill \
  --component-name java-task-plan \
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
1,Implement UserService,[1],none
2,Implement UserRepository,[2],none
3,Add integration tests,[3],"TASK-1" "TASK-2"

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

### Java-Specific Skill Mapping

| Change Type | Component Type | Skill | Workflow |
|-------------|----------------|-------|----------|
| create | class/interface | pm-dev-java:java-implement | implement |
| create | test | pm-dev-java:java-implement-tests | implement-tests |
| modify | any | pm-dev-java:java-implement | implement |
| refactor | any | pm-dev-java:java-refactor | refactor |
| fix | build error | pm-dev-java:java-fix-build | fix-build |
| fix | test failure | pm-dev-java:java-fix-tests | fix-tests |

### Java-Specific Aggregation Rules

| Pattern | Aggregate? | Rationale |
|---------|------------|-----------|
| Same module, same type | Yes | Single build verification |
| Interface + implementation | Yes | Coherent unit |
| Class + its tests | No | Tests verify implementation (different domains) |
| Config + dependent classes | No | Config must exist first (dependency) |
| Multiple services, same module | Yes | Same compilation unit |
| Cross-module changes | Consider | May want single verification |

---

## Task Generation Patterns

### Single Component Task

One deliverable → one task when:
- Single class/interface to implement
- Localized change in one file
- Simple feature addition

**Steps**:
1. Create/modify implementation at `{path}`
2. Add unit tests (load `pm-dev-java:junit-core`)
3. Add JavaDoc (load `pm-dev-java:javadoc`)
4. Verify `mvn test -pl {module}` passes

### Multi-Step Component Task

One deliverable → multiple tasks when:
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
4. Add unit tests (load pm-dev-java:junit-core)
5. Add JavaDoc (load pm-dev-java:javadoc)
6. Verify build passes
```

### Repository Class
```
1. Create repository interface at {interface_path}
2. Create repository implementation at {impl_path}
3. Add data access logic with proper exception handling
4. Add integration tests (load pm-dev-java:junit-core)
5. Add JavaDoc (load pm-dev-java:javadoc)
6. Verify build passes
```

### Configuration Class
```
1. Create configuration class at {path}
2. Add @ConfigProperty annotations for properties
3. Add validation logic if needed
4. Add unit tests for configuration validation
5. Add JavaDoc (load pm-dev-java:javadoc)
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

When creating multiple tasks from one deliverable, consider:

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
Run /pm-dev-builder:builder-build-and-fix
```

---

## Error Handling

### Ambiguous Deliverable

If deliverable doesn't clearly indicate:
- Target path → Ask for clarification
- Component type → Infer from context or ask
- Module placement → Check project structure

### Missing Information

If deliverable lacks detail:
- Generate task with placeholder
- Add lesson-learned for future reference
- Note ambiguity in task description

---

## Integration

**Caller**: `pm-dev-java:java-task-plan-agent`

**Script Notations** (use EXACTLY as shown):
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Read solution and list deliverables (list-deliverables, read)
- `pm-workflow:manage-tasks:manage-tasks` - Create tasks (add --plan-id X <<'EOF' ... EOF)
- `plan-marshall:lessons-learned:manage-lesson` - Record lessons on issues (add)

**Standards Referenced in Task Steps**:
- `pm-dev-java:java-core` - Core Java patterns
- `pm-dev-java:junit-core` - Testing standards
- `pm-dev-java:javadoc` - Documentation standards
- `pm-dev-java:java-cdi` - CDI/Quarkus patterns (when applicable)

**Contract Reference**:
- [plan-type-api/standards/task-contract.md](../../pm-workflow/skills/plan-type-api/standards/task-contract.md) - Optimization workflow and decision tables
