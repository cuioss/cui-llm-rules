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

plan_type: implementation
technology: java
build_system: maven

compatibility: deprecations
commit_strategy: phase-specific
finalizing: pr-workflow
```

### Schema Fields

| Field | Values | Description |
|-------|--------|-------------|
| `plan_type` | implementation, plugin-development, simple | Type of plan workflow |
| `technology` | java, javascript, plugin, mixed | Primary technology stack |
| `build_system` | maven, gradle, npm, none | Build system used |
| `compatibility` | deprecations, breaking | Compatibility strategy |
| `commit_strategy` | fine-granular, phase-specific, complete | Git commit granularity |
| `finalizing` | pr-workflow, commit-only | How to finalize work |

---

## Operations

### read

Read entire config.toon content.

```bash
python3 scripts/manage-config.py read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

config:
  plan_type: implementation
  technology: java
  build_system: maven
  compatibility: deprecations
  commit_strategy: phase-specific
  finalizing: pr-workflow
```

### get

Get a specific field value.

```bash
python3 scripts/manage-config.py get \
  --plan-id {plan_id} \
  --field plan_type
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: plan_type
value: implementation
```

### set

Set a specific field value.

```bash
python3 scripts/manage-config.py set \
  --plan-id {plan_id} \
  --field plan_type \
  --value java
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: plan_type
value: java
previous: implementation
```

### create

Create config.toon with initial values.

```bash
python3 scripts/manage-config.py create \
  --plan-id {plan_id} \
  --plan-type implementation \
  --technology java \
  --build-system maven \
  [--compatibility deprecations] \
  [--commit-strategy phase-specific] \
  [--finalizing pr-workflow]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: config.toon
created: true

config:
  plan_type: implementation
  technology: java
  build_system: maven
  compatibility: deprecations
  commit_strategy: phase-specific
  finalizing: pr-workflow
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `manage-config.py` | All config operations via subcommands | `python3 scripts/manage-config.py {command} --help` |

---

## Validation Rules

| Field | Valid Values |
|-------|--------------|
| plan_type | implementation, plugin-development, simple |
| technology | java, javascript, plugin, mixed |
| build_system | maven, gradle, npm, none |
| compatibility | deprecations, breaking |
| commit_strategy | fine-granular, phase-specific, complete |
| finalizing | pr-workflow, commit-only |

---

## Error Handling

```toon
status: error
plan_id: my-feature
field: plan_type
error: invalid_value
message: Invalid value 'unknown' for field 'plan_type'

valid_values[3]:
- implementation
- plugin-development
- simple
```

---

## Integration Points

### With plan-init

Plan initialization creates config.toon with user-selected values.

### With plan-execute

Execution phase reads config to determine build commands and commit strategy.
