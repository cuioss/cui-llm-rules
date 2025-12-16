# Task Contract

Standard structure for tasks created by task-plan skills. Tasks represent committable units of work derived from deliverables.

## Purpose

Each task:

- References one or more deliverables (M:N relationship)
- Contains domain and profile for workflow routing
- Includes explicit skills array for domain knowledge
- Includes verification criteria
- Specifies dependencies on other tasks (for ordering/parallelization)
- Results in exactly one commit

## Task File Format (TOON)

```toon
id: TASK-1
title: "Create CacheConfig class"
domain: java
profile: implementation
skills:
  - pm-dev-java:java-core
  - pm-dev-java:java-cdi
deliverables: [1]
depends_on: none

description: |
  Create CacheConfig class with Redis configuration...

steps[N]{number,title,status}:
1,src/main/java/com/example/CacheConfig.java,pending
2,src/main/java/com/example/CacheManager.java,pending

verification:
  commands:
    - mvn test -Dtest=CacheConfigTest
  criteria: All tests pass
```

## Key Fields

| Field | Type | Purpose |
|-------|------|---------|
| `id` | string | Unique task identifier (TASK-N) |
| `title` | string | Task title for display |
| `domain` | string | Single domain from deliverable (java, javascript, plugin) |
| `profile` | string | Workflow type (implementation, testing) |
| `skills` | list | Domain skills to load (explicit, from resolve-domain-skills) |
| `deliverables` | list | Referenced deliverable numbers |
| `depends_on` | string | Task dependencies for ordering |
| `description` | string | Detailed task description |
| `steps` | table | File paths to process |
| `verification` | object | Commands and criteria |

## Domain and Profile

### Domain Field

The `domain` field is inherited from the deliverable:

| Domain | Description |
|--------|-------------|
| `java` | Java code |
| `javascript` | JavaScript code |
| `plugin` | Marketplace plugins |

### Profile Field

The `profile` field determines which workflow skill is loaded:

| Profile | Workflow Skill | Description |
|---------|----------------|-------------|
| `implementation` | `config.workflow_skills.{domain}.implementation` | Create/modify production code |
| `testing` | `config.workflow_skills.{domain}.testing` | Create/modify test code |

## Skills Array

The `skills` array contains domain-specific skills resolved during task-plan:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
    resolve-domain-skills --domain java --profile implementation
```

Returns defaults and optionals. Task-plan:
1. Adds all defaults to `skills`
2. Selects relevant optionals based on task content
3. Writes final list to `task.skills`

**Two-tier skill loading at execution**:
- **Tier 1 (implicit)**: System skills loaded by agent automatically
- **Tier 2 (explicit)**: `task.skills` loaded by agent from task file

## Deliverable-to-Task Relationship

Tasks and deliverables have a **many-to-many relationship**:

| Pattern | Description | Example |
|---------|-------------|---------|
| 1:1 | One deliverable -> one task | Large coherent deliverable |
| N:1 | Multiple deliverables -> one task | Similar small changes (aggregation) |
| 1:N | One deliverable -> multiple tasks | Mixed execution modes (split) |

### When to Use Each Pattern

**1:1 (Keep separate)**:
- Large deliverables that form a coherent unit
- Single-file changes
- Deliverables with unique verification requirements

**N:1 (Aggregate)**:
- Same change_type
- Same domain and profile
- Same execution_mode (must be `automated`)
- No dependency between them
- Combined file count < 10

**1:N (Split)**:
- Mixed execution_mode (auto + manual parts)
- Different concerns within one deliverable
- Very large file counts (> 15)

## Optimization Workflow

Task-plan skills MUST follow this workflow:

### Step 1: Load All Deliverables

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
- `execution_mode: mixed` -> MUST split
- Different concerns -> SHOULD split
- File count > 15 -> CONSIDER splitting

### Step 5: Create Optimized Tasks

For each task:
1. Resolve skills: `resolve-domain-skills --domain {domain} --profile {profile}`
2. Add all defaults to `skills`
3. Select relevant optionals based on task content
4. Set `domain` and `profile` from deliverable
5. Consolidate verification commands
6. Generate steps from file lists
7. Compute task dependencies from deliverable dependencies
8. Identify parallelizable tasks

### Step 6: Log Optimization Decisions

Record why deliverables were grouped/split for audit trail.

## Optimization Decision Table

| Factor | Aggregate | Split | Keep |
|--------|-----------|-------|------|
| Same change_type | Y | | |
| Same domain and profile | Y | | |
| Combined files < 10 | Y | | |
| Same execution_mode | Y | | |
| Both depends: none | Y | | |
| One depends on other | N (NEVER) | | |
| execution_mode: mixed | | Y | |
| Different concerns | | Y | |
| File count > 15 | | Consider | |
| Large but coherent | | | Y |
| Single file | | | Y |

## Task Creation API

Uses stdin-based API with heredoc to avoid shell metacharacter issues:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
  --plan-id {plan_id} <<'EOF'
title: {aggregated title}
deliverables: [{n1}, {n2}, {n3}]
domain: {domain}
profile: {profile}
skills:
  - pm-dev-java:java-core
  - pm-dev-java:java-cdi
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

## Task-Plan Output

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

### Input Format (API calls)

When calling `manage-tasks add`, use YAML list format:

```yaml
steps:
  - marketplace/bundles/planning/agents/plan-init-agent.md
  - marketplace/bundles/planning/agents/plan-refine-agent.md
  - marketplace/bundles/planning/agents/plan-execute-agent.md
```

### Stored Format (.toon files)

The script converts input to TOON tabular format in task files:

```toon
steps[3]{number,title,status}:
1,marketplace/bundles/planning/agents/plan-init-agent.md,pending
2,marketplace/bundles/planning/agents/plan-refine-agent.md,pending
3,marketplace/bundles/planning/agents/plan-execute-agent.md,pending
```

### Valid Steps Requirements

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
