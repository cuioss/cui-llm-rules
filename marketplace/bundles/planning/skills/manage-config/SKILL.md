---
name: manage-config
description: Manage config.toon files with schema validation and field-level access
allowed-tools: Read, Glob, Bash
---

# Manage Config Skill

Manage config.toon files with schema validation and field-level access. Provides typed configuration for plan execution.

## What This Skill Provides

- Read/write config.toon with schema validation
- Field-level get/set operations
- Default value initialization
- Enum validation for typed fields

## When to Activate This Skill

Activate this skill when:
- Creating initial plan configuration
- Reading or updating plan settings
- Querying specific configuration values

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

plan_type: planning:plan-type-java
compatibility: deprecations
commit_strategy: phase-specific

# Finalize Configuration (added by plan-type configure)
create_pr: true
verification_required: true
verification_command: /builder-build-and-fix
branch_strategy: feature
```

### Base Schema Fields (set during plan creation)

| Field | Values | Description |
|-------|--------|-------------|
| `plan_type` | bundle:skill notation (e.g., planning:plan-type-java) | Type of plan workflow (extension point) |
| `compatibility` | deprecations, breaking | Compatibility strategy (user choice) |
| `commit_strategy` | fine-granular, phase-specific, complete | Git commit granularity (user choice) |

### Finalize Configuration Fields (added by plan-type configure)

| Field | Values | Description |
|-------|--------|-------------|
| `create_pr` | true, false | Whether to create a pull request |
| `verification_required` | true, false | Whether verification must pass before finalize |
| `verification_command` | command string or null | Command to run for verification |
| `branch_strategy` | feature, direct | Feature branch or direct-to-main |

---

## Operations

Script: `planning:manage-config`

### read

Read entire config.toon content.

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

config:
  plan_type: planning:plan-type-java
  compatibility: deprecations
  commit_strategy: phase-specific
```

### get

Get a specific field value.

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config get \
  --plan-id {plan_id} \
  --field plan_type
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: plan_type
value: planning:plan-type-java
```

### set

Set a specific field value.

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field compatibility \
  --value breaking
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: compatibility
value: breaking
previous: deprecations
```

### create

Create config.toon with initial values.

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config create \
  --plan-id {plan_id} \
  --plan-type planning:plan-type-java \
  [--compatibility deprecations] \
  [--commit-strategy phase-specific]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: config.toon
created: true

config:
  plan_type: planning:plan-type-java
  compatibility: deprecations
  commit_strategy: phase-specific
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-config` | All config operations via subcommands | `python3 .plan/execute-script.py planning:manage-config::{command} --help` |

---

## Validation Rules

| Field | Valid Values |
|-------|--------------|
| plan_type | bundle:skill notation (e.g., planning:plan-type-java) |
| compatibility | deprecations, breaking |
| commit_strategy | fine-granular, phase-specific, complete |
| create_pr | true, false |
| verification_required | true, false |
| verification_command | any string or null |
| branch_strategy | feature, direct |

---

## Error Handling

```toon
status: error
plan_id: my-feature
field: plan_type
error: invalid_value
message: Invalid plan_type format: unknown. Must be bundle:skill notation (e.g., planning:plan-type-java)
```

---

## Integration Points

### With plan-init

Plan initialization creates config.toon with base user-selected values (`plan_type`, `compatibility`, `commit_strategy`).

### With plan-type configure

After base config is created, plan-type skills add finalize configuration fields (`create_pr`, `verification_required`, `verification_command`, `branch_strategy`).

### With plan-execute

Execution phase reads config to determine build commands, commit strategy, and finalize behavior.
