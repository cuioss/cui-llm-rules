# Task Plan Skill Contract

Workflow skill for plan phase - transforms solution outline deliverables into optimized, committable tasks.

## Purpose

Task plan skills analyze solution outline deliverables and create optimized tasks. Each task represents a committable unit of work with explicit domain, profile, and pre-resolved skills fields.

**Flow**: Solution Outline (Deliverables) → Tasks with pre-resolved skills

---

## Invocation

**Phase**: `plan`

**Agent invocation**:
```bash
plan-phase-agent plan_id={plan_id} phase=plan
```

**Skill resolution**:
```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill --phase plan
```

Result:
```toon
status: success
domain: system
phase: plan
workflow_skill: pm-workflow:task-plan
```

---

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

## Workflow Skill Responsibilities

The workflow skill autonomously:

1. **Loads planning knowledge**: Calls `resolve-domain-skills --profile planning` per domain
2. **Loads deliverables**: From solution_outline.md
3. **Builds dependency graph**: From deliverable `depends` fields
4. **Analyzes for optimization**: Aggregation and split decisions
5. **Resolves task skills**: `resolve-domain-skills --domain X --profile Y`
6. **Creates tasks**: With explicit `domain`, `profile`, `skills`

```
Workflow Skill Execution:
┌──────────────────────────────────────────────────────────────────┐
│ 1. Get unique domains from deliverables                          │
│ 2. For each domain: resolve-domain-skills --profile planning     │
│    → Loads planning-level knowledge                              │
│ 3. Load deliverables via manage-solution-outline                 │
│ 4. Build dependency graph                                        │
│ 5. Analyze for aggregation/split                                 │
│ 6. For each task:                                                │
│    a. resolve-domain-skills --domain X --profile Y               │
│    b. Create task with domain, profile, skills                   │
│ 7. Write tasks via manage-tasks add                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Domain Knowledge Loading

**Profile used**: `planning`

```bash
# For each unique domain in deliverables
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-domain-skills --domain java --profile planning
```

**Knowledge includes**:
- Task decomposition patterns
- Domain-specific planning conventions
- How to structure tasks for the domain
- Verification patterns

**Knowledge excludes**:
- Full implementation details
- Specific coding patterns
- Test framework details

---

## Domain Source: From Deliverable

The plan phase reads domain from each deliverable:

```
solution_outline.md                      TASK-001.toon
┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐
│ ### 1. Create CacheConfig class      │ │ domain: java          ← Inherited   │
│ **Metadata:**                        │ │ profile: implementation              │
│ - domain: java        ← Reads domain │ │ skills:                              │
│ - profile: implementation            │ │   - pm-dev-java:java-core            │
│                                      │ │   - pm-dev-java:java-cdi             │
└──────────────────────────────────────┘ └──────────────────────────────────────┘
                     ↓ task-plan inherits domain/profile
                     ↓ resolves skills for execution
```

---

## Key Responsibilities

Apply optimization to package deliverables efficiently while maintaining:

1. **Atomic committability**: Each task = one coherent commit
2. **Testability**: Each task has verification
3. **Execution efficiency**: Minimize agent spawns and skill loads
4. **Dependency ordering**: Tasks execute in valid dependency order
5. **Parallelization**: Independent tasks can run concurrently
6. **Skill pre-resolution**: Each task gets pre-resolved skills array for execution

## Optimization Workflow

Task-plan skills MUST follow the 6-step optimization workflow:

### Step 1: Load All Deliverables

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline list-deliverables \
  --plan-id {plan_id}
```

Extract for each deliverable:
- `metadata.change_type`
- `metadata.execution_mode`
- `metadata.domain`
- `metadata.profile`
- `metadata.depends`
- `affected_files`
- `verification`

### Step 2: Build Dependency Graph

- Parse `depends` field for each deliverable
- Identify independent deliverables (`depends: none`)
- Identify dependency chains
- Detect cycles (INVALID - reject)

### Step 3: Analyze for Aggregation

For each pair of deliverables, check:
- Same change_type?
- Same domain and profile?
- Same execution_mode?
- Combined file count < 10?
- Verification can be merged?
- **NO dependency between them?** (CRITICAL)

Cannot aggregate if one depends on the other.

### Step 4: Analyze for Splits

For each deliverable, check:
- `execution_mode: mixed` → MUST split
- Different concerns → SHOULD split
- File count > 15 → CONSIDER splitting

### Step 5: Create Optimized Tasks

For each task:
1. Resolve skills: `resolve-domain-skills --domain {domain} --profile {profile}`
2. Add all defaults to `skills` array
3. Select relevant optionals based on task content
4. Set `domain` and `profile` from deliverable
5. Consolidate verification commands
6. Generate steps from file lists
7. Compute task dependencies from deliverable dependencies
8. Identify parallelizable tasks

### Step 6: Log Optimization Decisions

Record why deliverables were grouped/split for audit trail.

> **Full Decision Tables**: See [task-contract.md](task-contract.md) for optimization decision tables and dependency rules.

## Task Creation

Uses stdin-based API with heredoc to avoid shell metacharacter issues:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
  --plan-id {plan_id} <<'EOF'
title: {aggregated title}
deliverables: [{n1}, {n2}, {n3}]
domain: {domain}
profile: {profile}
skills:
  - {bundle}:{skill1}
  - {bundle}:{skill2}
phase: execute
description: |
  {combined description}

steps:
  - {file_1}
  - {file_2}
  - {file_3}

origin: plan
depends_on: TASK-001, TASK-002

verification:
  commands:
    - {cmd1}
    - {cmd2}
  criteria: {criteria}
EOF
```

## Return Structure

```toon
status: success|error
plan_id: {plan_id}

optimization_summary:
  deliverables_processed: {N}
  tasks_created: {M}
  aggregations: {count of deliverable groups}
  splits: {count of split deliverables}
  parallelizable_groups: {count of independent task groups}

tasks_created[M]{id,title,deliverables,depends_on}:
TASK-001,Update misc agents to TOON,[1 2 4],none
TASK-002,Update pm-dev-java agents to TOON,[3],TASK-001
TASK-003,Update TOON documentation,[5],none

execution_order:
  parallel_group_1: [TASK-001, TASK-003]
  parallel_group_2: [TASK-002]

lessons_recorded: {count}
message: {error message if status=error}
```

## Skill Resolution

The `resolve-domain-skills` script returns skills for the task:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
    resolve-domain-skills --domain java --profile implementation
```

Returns defaults and optionals. Task-plan:
1. Adds all defaults to `skills`
2. Selects relevant optionals based on task content
3. Writes final list to `task.skills`

## Error Handling

| Scenario | Action |
|----------|--------|
| Solution outline not found | Return `{status: error, message: "Solution outline not found"}` |
| Circular dependencies | Reject deliverables, return error with cycle |
| Invalid domain | Return error with valid domains |
| Script execution fails | Record lesson-learned, return error |

## Integration

**Callers**: `pm-workflow:task-plan-agent` (thin agent)

**Data Layer**:
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Solution outline queries
- `pm-workflow:manage-tasks:manage-tasks` - Task creation with deliverable references
- `plan-marshall:plan-marshall-config:plan-marshall-config` - Skill resolution

**Prerequisites**: [Solution Outline Skill](solution-outline-skill-contract.md) completion and [User Review Protocol](user-review-protocol.md) approval

---

## Related Documents

- [solution-outline-skill-contract.md](solution-outline-skill-contract.md) - Previous phase (outline)
- [task-execution-skill-contract.md](task-execution-skill-contract.md) - Next phase (execute)
- [task-contract.md](task-contract.md) - Task structure and optimization rules
- [deliverable-contract.md](deliverable-contract.md) - Deliverable structure
- [user-review-protocol.md](user-review-protocol.md) - Approval gate before plan phase
