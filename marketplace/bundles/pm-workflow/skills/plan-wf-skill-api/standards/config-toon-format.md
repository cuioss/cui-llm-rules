# Config TOON Format

Defines the structure of `config.toon` after init phase. This file stores plan-level configuration settings.

## Purpose

The `config.toon` file:
- Stores detected domains (array) for the plan
- Provides commit and branch strategy settings
- Contains finalization settings

Note: `workflow_skills` are NOT stored in config.toon. They are resolved at runtime from `marshal.json` via `plan-marshall-config resolve-workflow-skill`.

## File Format

```toon
# Multiple domains supported (e.g., fullstack feature)
domains:
  - java
  - javascript

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
| `domains` | list | Array of detected domains (java, javascript, plugin, generic) |
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
| Generic tasks | Documentation work | `[generic]` |

Each deliverable/task selects ONE domain from this array.

## Workflow Skills Resolution

Workflow skills are resolved at runtime from `marshal.json`:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill --domain {domain} --phase {phase}
```

| Phase | Purpose |
|-------|---------|
| `solution_outline` | Skill for creating solution outlines |
| `task_plan` | Skill for task planning |
| `implementation` | Skill for code implementation |
| `testing` | Skill for test implementation |

### Domain-Specific Skills

| Domain | solution_outline | task_plan | implementation | testing |
|--------|------------------|-----------|----------------|---------|
| java | pm-workflow:solution-outline | pm-workflow:task-plan | pm-workflow:task-implementation | pm-workflow:task-testing |
| javascript | pm-workflow:solution-outline | pm-workflow:task-plan | pm-workflow:task-implementation | pm-workflow:task-testing |
| plugin | pm-plugin-development:plugin-solution-outline | pm-plugin-development:plugin-task-plan | pm-plugin-development:plugin-plan-implement | - |
| generic | pm-workflow:solution-outline | pm-workflow:task-plan | pm-workflow:task-implementation | - |

## Workflow Phase Usage

| Phase | Operation | Purpose |
|-------|-----------|---------|
| Init | Creates config.toon | Stores domains and settings |
| Refine | Resolves workflow_skill from marshal.json | Creates deliverables and tasks |
| Execute | Resolves workflow_skill from marshal.json | Executes task |
| Finalize | Reads finalize settings | Creates PR |

## Commit Strategy

| Strategy | Behavior |
|----------|----------|
| `per_task` | One commit per completed task |
| `per_plan` | Single commit for all tasks |
| `none` | No commits (manual) |

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
3. **Task level**: Each task has single `domain` field
4. **Runtime resolution**: workflow_skills resolved from marshal.json (not stored in config.toon)
5. **Same resolve path**: All domains use same resolution via `resolve-workflow-skill` command

## Example: Single Domain (Java)

```toon
domains:
  - java

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

commit_strategy: per_task
create_pr: true
verification_required: true
verification_command: python3 test/run-tests.py
branch_strategy: feature
```
