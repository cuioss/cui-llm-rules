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

plan_type: java
compatibility: deprecations
commit_strategy: phase-specific
```

### Schema Fields

| Field | Values | Description |
|-------|--------|-------------|
| `plan_type` | java, javascript, plugin-development, simple | Type of plan workflow |
| `compatibility` | deprecations, breaking | Compatibility strategy (user choice) |
| `commit_strategy` | fine-granular, phase-specific, complete | Git commit granularity (user choice) |

### Derived from plan_type (not stored)

These values are derived from `plan_type` at runtime via `plan-type-{type}` skills:

| Derived | Source |
|---------|--------|
| `technology` | plan-type characteristics |
| `build_system` | `builder:environment-detection` or plan-type characteristics |
| `finalizing` | `get-finalize-config` operation |

---

## Operations

Script: `planning:manage-config/scripts/manage-config.py`

### read

Read entire config.toon content.

```bash
python3 {script_path} read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

config:
  plan_type: java
  compatibility: deprecations
  commit_strategy: phase-specific
```

### get

Get a specific field value.

```bash
python3 {script_path} get \
  --plan-id {plan_id} \
  --field plan_type
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: plan_type
value: java
```

### set

Set a specific field value.

```bash
python3 {script_path} set \
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
python3 {script_path} create \
  --plan-id {plan_id} \
  --plan-type java \
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
  plan_type: java
  compatibility: deprecations
  commit_strategy: phase-specific
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-config/scripts/manage-config.py` | All config operations via subcommands | `python3 {script_path} {command} --help` |

---

## Validation Rules

| Field | Valid Values |
|-------|--------------|
| plan_type | java, javascript, plugin-development, simple |
| compatibility | deprecations, breaking |
| commit_strategy | fine-granular, phase-specific, complete |

---

## Error Handling

```toon
status: error
plan_id: my-feature
field: plan_type
error: invalid_value
message: Invalid value 'unknown' for field 'plan_type'

valid_values[4]:
- java
- javascript
- plugin-development
- simple
```

---

## Integration Points

### With plan-init

Plan initialization creates config.toon with user-selected values.

### With plan-execute

Execution phase reads config to determine build commands and commit strategy.
