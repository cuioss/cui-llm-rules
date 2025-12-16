# Config TOON Format

Defines the structure of `config.toon` after init phase. This file is self-contained and used by all subsequent workflow phases.

## Purpose

The `config.toon` file:
- Stores detected domains (array) from init phase
- Contains workflow_skills mapping for each domain
- Provides finalization settings
- Is self-contained after init (no runtime lookups needed)

## File Format

```toon
# Multiple domains supported (e.g., fullstack feature)
domains:
  - java
  - javascript

# Workflow skills (written by init, read by refine/execute)
workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
  javascript:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing

commit_strategy: per_task

# Finalize settings
create_pr: true
verification_required: true
verification_command: /pm-dev-builder:builder-build-and-fix
branch_strategy: feature
```

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `domains` | list | Array of detected domains (java, javascript, plugin) |
| `workflow_skills` | object | Domain-keyed mapping of workflow phase -> skill |
| `commit_strategy` | string | per_task, per_plan, or none |
| `create_pr` | boolean | Whether to create PR on finalize |
| `verification_required` | boolean | Whether to run verification before PR |
| `verification_command` | string | Command to run for verification |
| `branch_strategy` | string | feature or direct |

## Domains Array

The `domains` array supports multi-domain plans:

| Scenario | Example | Domains |
|----------|---------|---------|
| Java backend feature | Add caching to UserService | `[java]` |
| Frontend feature | Add dashboard component | `[javascript]` |
| Fullstack feature | Add metrics API + dashboard | `[java, javascript]` |
| Plugin development | Create new skill | `[plugin]` |

Each deliverable/task selects ONE domain from this array.

## Workflow Skills Block

The `workflow_skills` block maps workflow phases to skills:

```toon
workflow_skills:
  {domain}:
    solution_outline: {skill for solution outline phase}
    task_plan: {skill for task planning phase}
    implementation: {skill for implementation profile}
    testing: {skill for testing profile}
```

### Domain-Agnostic Skills (Java/JavaScript)

For java and javascript domains, workflow skills are domain-agnostic:

```toon
workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
```

### Plugin Domain (Hardcoded)

Plugin uses domain-specific workflow skills (hardcoded during init):

```toon
workflow_skills:
  plugin:
    solution_outline: pm-plugin-development:plugin-solution-outline
    task_plan: pm-plugin-development:plugin-task-plan
    implementation: pm-plugin-development:plugin-plan-implement
```

## Workflow Phase Usage

| Phase | Reads | Purpose |
|-------|-------|---------|
| Init | - | Writes config.toon with domains + workflow_skills |
| Refine | `workflow_skills.{domain}.solution_outline` | Creates deliverables |
| Refine | `workflow_skills.{domain}.task_plan` | Creates tasks |
| Execute | `workflow_skills.{task.domain}.{task.profile}` | Executes task |
| Finalize | finalize settings | Creates PR |

## Source of Workflow Skills

| Domain | Source | Reason |
|--------|--------|--------|
| java | `skill_domains.java.workflow_skills` | Configurable per project |
| javascript | `skill_domains.javascript.workflow_skills` | Configurable per project |
| plugin | Hardcoded in init | Fixed toolset, not exposed |

## Commit Strategy

| Strategy | Behavior |
|----------|----------|
| `per_task` | One commit per completed task |
| `batch` | Single commit for all tasks |

## Branch Strategy

| Strategy | Behavior |
|----------|----------|
| `feature` | Create feature branch from main |
| `direct` | Work on current branch |

## Finalize Settings

| Field | Description |
|-------|-------------|
| `create_pr` | Create pull request when all tasks complete |
| `verification_required` | Run verification before PR creation |
| `verification_command` | Command to execute for verification |

## Key Architectural Points

1. **Plan level**: `domains` is an array (supports multi-domain plans)
2. **Deliverable level**: Each deliverable has single `domain` field
3. **Task level**: Each task has single `domain` field (used by resolve-domain-skills)
4. **Self-contained**: After init, config.toon has everything needed - no runtime lookup
5. **Same refine/execute path**: All domains use same code path - read config.workflow_skills

## Example: Single Domain (Java)

```toon
domains:
  - java

workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing

commit_strategy: per_task
create_pr: true
verification_required: true
verification_command: /pm-dev-builder:builder-build-and-fix
branch_strategy: feature
```

## Example: Multi-Domain (Fullstack)

```toon
domains:
  - java
  - javascript

workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
  javascript:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing

commit_strategy: per_task
create_pr: true
verification_required: true
verification_command: /pm-dev-builder:builder-build-and-fix
branch_strategy: feature
```

## Example: Plugin Domain

```toon
domains:
  - plugin

workflow_skills:
  plugin:
    solution_outline: pm-plugin-development:plugin-solution-outline
    task_plan: pm-plugin-development:plugin-task-plan
    implementation: pm-plugin-development:plugin-plan-implement

commit_strategy: per_task
create_pr: true
verification_required: true
verification_command: python3 test/run-tests.py
branch_strategy: feature
```
