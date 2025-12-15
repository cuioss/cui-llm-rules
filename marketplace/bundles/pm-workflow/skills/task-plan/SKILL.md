---
name: task-plan
description: Domain-agnostic task planning from deliverables with skill resolution and optimization
allowed-tools: Read, Bash
---

# Task Plan Skill

**Role**: Domain-agnostic workflow skill for transforming solution outline deliverables into optimized, executable tasks. Loaded by `pm-workflow:task-plan-agent`.

**Key Pattern**: Reads deliverables with metadata from `solution_outline.md`, uses `resolve-domain-skills` to determine task-specific skills, applies aggregation/split analysis, creates tasks with explicit skill lists.

## Contract Compliance

**MANDATORY**: All tasks MUST follow the structure defined in the central contracts:

| Contract | Location | Purpose |
|----------|----------|---------|
| Task Contract | `pm-workflow:plan-type-api/standards/task-contract.md` | Required task structure and optimization workflow |
| Task-Plan Skill Contract | `pm-workflow:plan-wf-skill-api/standards/task-plan-skill-contract.md` | Skill responsibilities |

**CRITICAL - Steps Field**:
- The `steps` field MUST contain file paths from the deliverable's `Affected files` section
- Steps must NOT be descriptive text (e.g., "Update AuthController.java" is INVALID)
- Validation rejects tasks with non-file-path steps

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

## Output

```toon
status: success | error
plan_id: {echo}
optimization_summary:
  deliverables_processed: N
  tasks_created: M
  aggregations: N
  splits: N
  parallelizable_groups: N
tasks_created[M]: {number, title, deliverables, depends_on}
execution_order: {parallel groups}
message: {error message if status=error}
```

## Workflow

### Step 1: Load All Deliverables

Read the solution document to get all deliverables with metadata:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline \
  list-deliverables \
  --plan-id {plan_id}
```

For each deliverable, extract:
- `metadata.change_type`, `metadata.execution_mode`
- `metadata.domain` (single value)
- `metadata.profile` (`implementation` or `testing`)
- `metadata.depends`
- `affected_files`
- `verification`

### Step 2: Build Dependency Graph

Parse `depends` field for each deliverable:
- Identify independent deliverables (`depends: none`)
- Identify dependency chains
- Detect cycles (INVALID - reject with error)

### Step 3: Analyze for Aggregation

For each pair of deliverables, check if they can be aggregated:
- Same `change_type`?
- Same `domain`?
- Same `profile`?
- Same `execution_mode` (must be `automated`)?
- Combined file count < 10?
- **NO dependency between them?** (CRITICAL - cannot aggregate if one depends on the other)

### Step 4: Analyze for Splits

For each deliverable, check for split requirements:
- `execution_mode: mixed` → MUST split
- Production + test code combined → SHOULD split (different profiles)
- File count > 15 → CONSIDER splitting

### Step 5: Resolve Skills for Each Task

For each task (aggregated or single), resolve domain skills:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-domain-skills \
  --domain {task.domain} \
  --profile {task.profile}
```

**Output format**:
```toon
domain: java
profile: implementation

defaults:
  pm-dev-java:java-core: Java patterns, CUI conventions, CuiLogger, null-safety

optionals:
  pm-dev-java:java-null-safety: JSpecify annotations (@NullMarked, @Nullable)
  pm-dev-java:java-cdi: CDI patterns (@ApplicationScoped, @Inject...)
  pm-dev-java:java-lombok: Lombok annotations (@Builder, @Value, @Delegate)
```

**Skill Selection**:
1. All `defaults` are automatically included in `task.skills`
2. Review `optionals` and select based on task content (LLM decision)
3. Write final selection to `task.skills`

### Step 6: Create Optimized Tasks

For aggregated deliverables or single deliverables, create tasks using heredoc:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
  --plan-id {plan_id} <<'EOF'
title: {aggregated title}
deliverables: [{n1}, {n2}, {n3}]
domain: {domain from deliverable}
profile: {profile from deliverable}
phase: execute
description: |
  {combined description}

steps:
  - {file1}
  - {file2}
  - {file3}

depends_on: TASK-1, TASK-2

skills:
  - {skill1 from defaults}
  - {skill2 from defaults}
  - {selected optional1}

verification:
  commands:
    - {cmd1}
  criteria: {criteria}
EOF
```

**Key Fields**:
- `domain`: Single domain from deliverable
- `profile`: `implementation` or `testing` (determines workflow skill at execution)
- `skills`: Domain skills only (system skills loaded by agent)
- `steps`: File paths from `Affected files` (NOT descriptive text)

### Step 7: Determine Execution Order

Compute parallel execution groups:

```toon
execution_order:
  parallel_group_1: [TASK-1, TASK-3]    # No dependencies
  parallel_group_2: [TASK-2, TASK-4]    # Both depend on group 1
  parallel_group_3: [TASK-5]            # Depends on group 2
```

**Parallelism rules**:
- Tasks with no `depends_on` go in first group
- Tasks depending on same prior tasks can run in parallel
- Sequential dependencies remain sequential

### Step 8: Record Issues as Lessons

On ambiguous deliverable or planning issues:

```bash
python3 .plan/execute-script.py plan-marshall:lessons-learned:manage-lesson add \
  --component-type skill \
  --component-name task-plan \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 9: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}

optimization_summary:
  deliverables_processed: {N}
  tasks_created: {M}
  aggregations: {count of deliverable groups}
  splits: {count of split deliverables}
  parallelizable_groups: {count of independent task groups}

tasks_created[M]{number,title,deliverables,depends_on}:
1,Implement UserService,[1],none
2,Implement UserRepository,[2],none
3,Add integration tests,[3],"TASK-1" "TASK-2"

execution_order:
  parallel_group_1: [TASK-1, TASK-2]
  parallel_group_2: [TASK-3]

lessons_recorded: {count}
```

## Optimization Decision Table

| Factor | Aggregate | Split | Keep |
|--------|-----------|-------|------|
| Same change_type | Yes | | |
| Same domain | Yes | | |
| Same profile | Yes | | |
| Combined files < 10 | Yes | | |
| Same execution_mode | Yes | | |
| Both depends: none | Yes | | |
| One depends on other | **Never** | | |
| execution_mode: mixed | | Yes | |
| Different profiles | | Yes | |
| File count > 15 | | Consider | |
| Large but coherent | | | Yes |
| Single file | | | Yes |

## Dependency Rules for Aggregation

| D1.depends | D2.depends | Can Aggregate? | Reason |
|------------|------------|----------------|--------|
| none | none | Yes | Both independent |
| none | D1 | **No** | D2 depends on D1 |
| D3 | D3 | Yes | Same dependency, can run together |
| D3 | D4 | Yes | Different deps, no conflict |
| D2 | D1 | **No** | Creates cycle if aggregated |

## Skill Selection Guidelines

When selecting from `optionals`, consider:

| Context | Select Skill |
|---------|--------------|
| Uses dependency injection | CDI skill (java-cdi, etc.) |
| Complex annotations | Lombok skill |
| Integration tests | Integration testing skill |
| API documentation | OpenAPI/JSDoc skill |
| Code cleanup | Maintenance skill |

## Error Handling

### Circular Dependencies

If deliverable dependencies form a cycle:
- Error: "Circular dependency detected: D1 -> D2 -> D1"
- Do NOT create tasks

### Missing Domain Skills

If `resolve-domain-skills` returns empty:
- Error: "No skills configured for domain: {domain}"
- Record as lesson learned

### Ambiguous Deliverable

If deliverable metadata incomplete:
- Generate task with defaults
- Add lesson-learned for future reference
- Note ambiguity in task description

## Integration

**Invoked by**: `pm-workflow:task-plan-agent` (thin agent)

**Script Notations** (use EXACTLY as shown):
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Read deliverables (list-deliverables, read)
- `pm-workflow:manage-tasks:manage-tasks` - Create tasks (add --plan-id X <<'EOF' ... EOF)
- `plan-marshall:plan-marshall-config:plan-marshall-config` - Resolve domain skills (resolve-domain-skills)
- `plan-marshall:lessons-learned:manage-lesson` - Record lessons on issues (add)

**Consumed By**:
- `pm-workflow:task-execute-agent` - Reads tasks and executes them
