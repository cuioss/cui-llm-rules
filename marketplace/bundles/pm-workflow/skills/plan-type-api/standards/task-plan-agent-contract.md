# Task Plan Agent Contract

Standard contract for task plan agents that transform deliverables into optimized, committable tasks.

## Purpose

Task plan agents analyze solution outline deliverables and create optimized tasks. Each task represents a committable unit of work.

**Flow**: Solution Outline (Deliverables) → Tasks

## Invocation

**Invoked by**: `/plan-manage action=refine` command (after user approves solution outline via [User Review Protocol](user-review-protocol.md))

The command reads the `domain.task_plan_agent` field from the plan-type skill's frontmatter and invokes the agent via Task tool.

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

## Optimization Workflow

Task-plan agents MUST follow the 6-step optimization workflow:

### Step 1: Load All Deliverables

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline list-deliverables \
  --plan-id {plan_id}
```

Extract for each deliverable:
- `metadata.change_type`
- `metadata.execution_mode`
- `metadata.domain`
- `metadata.suggested_skill`
- `metadata.suggested_workflow`
- `metadata.context_skills`
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
- Same suggested_skill?
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

- Group aggregated deliverables
- Split mixed-mode deliverables
- Extract delegation (skill, workflow, domain, context_skills)
- Consolidate verification commands
- Generate steps from file lists
- Compute task dependencies from deliverable dependencies
- Identify parallelizable tasks

### Step 6: Log Optimization Decisions

Record why deliverables were grouped/split for audit trail.

> **Full Decision Tables**: See [task-contract.md](task-contract.md) for optimization decision tables and dependency rules.

## Task Creation

Uses stdin-based API with heredoc to avoid shell metacharacter issues:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-task add \
  --plan-id {plan_id} <<'EOF'
title: {aggregated title}
deliverables: [{n1}, {n2}, {n3}]
domain: {domain}
phase: execute
description: |
  {combined description}

steps:
  - {file_1}
  - {file_2}
  - {file_3}

depends_on: TASK-1, TASK-2

delegation:
  skill: {skill}
  workflow: {workflow}
  context_skills:
    - {skill1}
    - {skill2}

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

## Domain Agent Implementations

| Plan Type | Agent |
|-----------|-------|
| `java` | `pm-dev-java:java-task-plan-agent` |
| `javascript` | `pm-dev-frontend:js-task-plan-agent` |
| `plugin-development` | `pm-plugin-development:plugin-task-plan-agent` |
| `generic` | None (inline in command) |

## Error Handling

| Scenario | Action |
|----------|--------|
| Solution outline not found | Return `{status: error, message: "Solution outline not found"}` |
| Circular dependencies | Reject deliverables, return error with cycle |
| Invalid domain | Return error with valid domains |
| Script execution fails | Record lesson-learned, return error |

## Integration

**Callers**: `/plan-manage action=refine` command

**Data Layer**:
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Solution outline queries
- `pm-workflow:manage-tasks:manage-task` - Task creation with deliverable references

**Prerequisites**: [Solution Outline Agent](solution-outline-agent-contract.md) completion and [User Review Protocol](user-review-protocol.md) approval
