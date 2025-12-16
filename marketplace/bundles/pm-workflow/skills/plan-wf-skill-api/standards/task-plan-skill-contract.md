# Task Plan Skill Contract

Standard contract for task plan skills that transform deliverables into optimized, committable tasks.

## Purpose

Task plan skills analyze solution outline deliverables and create optimized tasks. Each task represents a committable unit of work with explicit domain, profile, and skills fields.

**Flow**: Solution Outline (Deliverables) → Tasks

## Invocation

**Invoked by**: `pm-workflow:task-plan-agent` (thin agent that loads this skill from config.toon)

The agent reads `config.workflow_skills.{domain}.task_plan` to determine which skill to load.

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

## Key Responsibilities

Apply optimization to package deliverables efficiently while maintaining:

1. **Atomic committability**: Each task = one coherent commit
2. **Testability**: Each task has verification
3. **Execution efficiency**: Minimize agent spawns and skill loads
4. **Dependency ordering**: Tasks execute in valid dependency order
5. **Parallelization**: Independent tasks can run concurrently
6. **Skill resolution**: Each task gets explicit skills array for execution

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

depends_on: TASK-1, TASK-2

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

tasks_created[M]{number,title,deliverables,depends_on}:
1,Update misc agents to TOON,[1 2 4],none
2,Update pm-dev-java agents to TOON,[3],"TASK-1"
3,Update TOON documentation,[5],none

execution_order:
  parallel_group_1: [TASK-1, TASK-3]
  parallel_group_2: [TASK-2]

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
