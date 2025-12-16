---
name: manage-config
description: Manage per-plan configuration with schema validation
allowed-tools: Read, Glob, Bash
---

# Manage Config Skill

Per-plan configuration management for plan-specific settings stored in `config.toon`.

## What This Skill Provides

- Per-plan config.toon management with schema validation
- Domain-based workflow skills configuration
- Field-level get/set operations with nested access support
- Multi-field retrieval

## When to Activate This Skill

Activate this skill when:
- Creating initial plan configuration
- Reading or updating plan settings
- Retrieving workflow skills for domain/profile combinations

---

## Storage Location

Configuration is stored in the plan directory:

```
.plan/plans/{plan_id}/config.toon
```

---

## File Format

TOON format with typed fields:

```toon
# Plan Configuration

domains[1]:
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

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `domains` | array | List of domains (e.g., java, javascript, plugin) |
| `workflow_skills` | object | Workflow skills keyed by domain, then by profile |
| `commit_strategy` | enum | `per_task`, `per_plan`, `none` |

### Optional Fields

| Field | Values | Default | Description |
|-------|--------|---------|-------------|
| `create_pr` | true, false | true | Create PR on finalize |
| `verification_required` | true, false | true | Require verification before finalize |
| `verification_command` | string | - | Command to run for verification |
| `branch_strategy` | feature, direct | feature | Feature branch or direct-to-main |

---

## Operations

Script: `pm-workflow:manage-config:manage-config`

### create

Create config.toon with domains and workflow_skills configuration.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config create \
  --plan-id {plan_id} \
  --domains java \
  --workflow-skills '{"java":{"solution_outline":"pm-workflow:solution-outline","task_plan":"pm-workflow:task-plan","implementation":"pm-workflow:task-implementation","testing":"pm-workflow:task-testing"}}' \
  [--commit-strategy per_task] \
  [--create-pr true] \
  [--verification-required true] \
  [--verification-command "/pm-dev-builder:builder-build-and-fix"] \
  [--branch-strategy feature] \
  [--force]
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--domains` | string (comma-separated) | Yes | Domain list (e.g., `java` or `java,javascript`) |
| `--workflow-skills` | JSON string | Yes | Workflow skills keyed by domain |
| `--commit-strategy` | enum | No | `per_task` (default), `per_plan`, `none` |
| `--create-pr` | bool | No | Create PR on finalize (default: true) |
| `--verification-required` | bool | No | Require verification (default: true) |
| `--verification-command` | string | No | Verification command |
| `--branch-strategy` | enum | No | `feature` (default), `direct` |
| `--force` | flag | No | Overwrite existing config |

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: config.toon
created: true
domains_count: 1

config:
  domains[1]:
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

### get-workflow-skill

Get workflow skill for a specific domain and profile combination.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config \
  get-workflow-skill --plan-id {plan_id} --domain java --profile implementation
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--plan-id` | string | Yes | Plan identifier |
| `--domain` | string | Yes | Domain name (java, javascript, plugin) |
| `--profile` | string | Yes | Profile name (implementation, testing, solution_outline, task_plan) |

**Output** (TOON):
```toon
status: success
plan_id: my-feature
domain: java
profile: implementation
workflow_skill: pm-workflow:task-implementation
```

**Error Cases**:
- Config not found → `error: file_not_found`
- Domain not in config.domains → `error: domain_not_found` (includes `available_domains`)
- Profile not in workflow_skills → `error: profile_not_found` (includes `available_profiles`)

### get-domains

Get the domains array from config.toon.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config \
  get-domains --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
domains[2]:
- java
- javascript
count: 2
```

### read

Read entire config.toon content.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

config:
  domains[1]:
  - java
  workflow_skills:
    java:
      solution_outline: pm-workflow:solution-outline
  commit_strategy: per_task
```

### get

Get a specific field value. Supports nested field access via dot notation.

```bash
# Simple field
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} \
  --field commit_strategy

# Nested field (dot notation)
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} \
  --field workflow_skills.java.implementation
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: workflow_skills.java.implementation
value: pm-workflow:task-implementation
```

### set

Set a specific field value.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field commit_strategy \
  --value per_plan
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: commit_strategy
value: per_plan
previous: per_task
```

### get-multi

Get multiple fields in one call.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get-multi \
  --plan-id {plan_id} \
  --fields "commit_strategy,branch_strategy"
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
commit_strategy: per_task
branch_strategy: feature
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `pm-workflow:manage-config:manage-config` | Per-plan config.toon operations | `python3 .plan/execute-script.py pm-workflow:manage-config:manage-config {subcommand} --help` |

---

## Validation Rules

| Field | Valid Values |
|-------|--------------|
| domains | lowercase identifiers (e.g., java, javascript, plugin) |
| workflow_skills | bundle:skill notation per profile |
| commit_strategy | per_task, per_plan, none |
| create_pr | true, false |
| verification_required | true, false |
| verification_command | any string |
| branch_strategy | feature, direct |

---

## Error Handling

```toon
status: error
plan_id: my-feature
error: domain_not_found
message: Domain 'python' not found in config.domains
available_domains[1]:
- java
```

---

## Integration Points

| Consumer | Operation | Purpose |
|----------|-----------|---------|
| plan-init-agent | `create` | Create config.toon with domains and workflow_skills |
| solution-outline-agent | `get-domains` | Get domains for deliverable assignment |
| task-execute-agent | `get-workflow-skill` | Get workflow skill for task execution |
| plan-execute | `read`, `get` | Read commit strategy, verification settings |
| plan-finalize | `get` | Check create_pr, branch_strategy |

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `plan-marshall:plan-marshall-config` | Project-level marshal.json configuration |
