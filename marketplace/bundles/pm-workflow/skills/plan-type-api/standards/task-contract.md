# Task Contract

Standard structure for tasks created by task-plan agents. Tasks represent committable units of work derived from deliverables.

## Purpose

Each task:

- References one or more deliverables (M:N relationship)
- Contains delegation information for execution
- Includes verification criteria
- Specifies dependencies on other tasks (for ordering/parallelization)
- Results in exactly one commit

> **Full Specification**: See [manage-tasks/standards/task-format.md](../../manage-tasks/standards/task-format.md) for the complete task file format and field definitions.

## Key Fields for Task Planning

| Field | Purpose in Planning |
|-------|---------------------|
| `deliverables` | Track which solution outline items are covered |
| `depends_on` | Enable execution ordering and parallelization |
| `delegation.skill` | Skill to execute task |
| `delegation.workflow` | Workflow within skill |
| `delegation.domain` | Domain for loading default skills |
| `delegation.context_skills` | Optional skills from domain |
| `verification` | Consolidated from deliverable verification criteria |

## Deliverable-to-Task Relationship

Tasks and deliverables have a **many-to-many relationship**:

| Pattern | Description | Example |
|---------|-------------|---------|
| 1:1 | One deliverable → one task | Large coherent deliverable |
| N:1 | Multiple deliverables → one task | Similar small changes (aggregation) |
| 1:N | One deliverable → multiple tasks | Mixed execution modes (split) |

### When to Use Each Pattern

**1:1 (Keep separate)**:
- Large deliverables that form a coherent unit
- Single-file changes
- Deliverables with unique verification requirements

**N:1 (Aggregate)**:
- Same change_type
- Same suggested_skill and workflow
- Same execution_mode (must be `automated`)
- No dependency between them
- Combined file count < 10

**1:N (Split)**:
- Mixed execution_mode (auto + manual parts)
- Different concerns within one deliverable
- Very large file counts (> 15)

## Optimization Workflow

Task-plan agents MUST follow this workflow:

### Step 1: Load All Deliverables

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

## Optimization Decision Table

| Factor | Aggregate | Split | Keep |
|--------|-----------|-------|------|
| Same change_type | ✓ | | |
| Same suggested_skill | ✓ | | |
| Same suggested_workflow | ✓ | | |
| Combined files < 10 | ✓ | | |
| Same execution_mode | ✓ | | |
| Both depends: none | ✓ | | |
| One depends on other | ✗ (NEVER) | | |
| execution_mode: mixed | | ✓ | |
| Different concerns | | ✓ | |
| File count > 15 | | Consider | |
| Large but coherent | | | ✓ |
| Single file | | | ✓ |

## Dependency Rules for Aggregation

| D1.depends | D2.depends | Can Aggregate? | Reason |
|------------|------------|----------------|--------|
| none | none | Yes | Both independent |
| none | D1 | **No** | D2 depends on D1 |
| D3 | D3 | Yes | Same dependency, can run together |
| D3 | D4 | Yes | Different deps, no conflict |
| D2 | D1 | **No** | Creates cycle if aggregated |

## Task Creation API

Uses stdin-based API with heredoc to avoid shell metacharacter issues:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
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

## Task Plan Agent Output

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
1,Update misc agents to TOON,[1 2 4],none
2,Update pm-dev-java agents to TOON,[3],"TASK-1"
3,Update TOON documentation,[5],none
4,Create verification script,[6],"TASK-1" "TASK-2"
5,Measure token savings,[6],"TASK-4"

execution_order:
  parallel_group_1: [TASK-1, TASK-3]
  parallel_group_2: [TASK-2]
  parallel_group_3: [TASK-4]
  parallel_group_4: [TASK-5]

lessons_recorded: {count}
```

## Steps Field Contract

**CRITICAL**: The `steps` field MUST contain file paths from the deliverable's `Affected files` section.

### Valid Steps (File Paths)

```yaml
steps:
  - marketplace/bundles/planning/agents/plan-init-agent.md
  - marketplace/bundles/planning/agents/plan-refine-agent.md
  - marketplace/bundles/planning/agents/plan-execute-agent.md
```

**Why valid:**
- Each step is an explicit file path
- Steps are derived from deliverable's `Affected files`
- Execution progress can be tracked per file

### Invalid Steps (Descriptive Text)

```yaml
steps:
  - Update plan-init-agent to use TOON output
  - Migrate plan-refine-agent output format
  - Convert all remaining agents
```

**Why invalid:**
- Steps are action descriptions, not file paths
- Cannot track which files have been processed
- "all remaining agents" is vague
- Validation will reject this task

### Invalid Steps (Task Numbers)

```yaml
steps[2]{number,title,status}:
1,Convert plan-init-agent outputs,pending
2,Convert plan-refine-agent outputs,pending
```

**Why invalid:**
- Title column contains descriptions, not file paths
- This was the old format - now rejected by contract validation
