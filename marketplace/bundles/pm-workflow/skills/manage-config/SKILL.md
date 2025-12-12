---
name: manage-config
description: Manage per-plan configuration with schema validation
allowed-tools: Read, Glob, Bash
---

# Manage Config Skill

Per-plan configuration management for plan-specific settings stored in `config.toon`.

## What This Skill Provides

- Per-plan config.toon management with schema validation
- Field-level get/set operations
- Multi-field retrieval

## When to Activate This Skill

Activate this skill when:
- Creating initial plan configuration
- Reading or updating plan settings

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

plan_type: pm-workflow:plan-type-java
compatibility: deprecations
commit_strategy: phase-specific

# Finalize Configuration (from plan-type frontmatter plan_defaults)
create_pr: true
verification_required: true
verification_command: /pm-dev-builder:builder-build-and-fix
branch_strategy: feature
```

### Base Schema Fields (set during plan creation)

| Field | Values | Description |
|-------|--------|-------------|
| `plan_type` | bundle:skill notation (e.g., pm-workflow:plan-type-java) | Type of plan workflow (extension point) |
| `compatibility` | deprecations, breaking | Compatibility strategy (user choice) |
| `commit_strategy` | fine-granular, phase-specific, complete | Git commit granularity (user choice) |

### Finalize Configuration Fields (from plan-type frontmatter)

| Field | Values | Description |
|-------|--------|-------------|
| `create_pr` | true, false | Whether to create a pull request |
| `verification_required` | true, false | Whether verification must pass before finalize |
| `verification_command` | command string or null | Command to run for verification |
| `branch_strategy` | feature, direct | Feature branch or direct-to-main |

---

## Operations

Script: `pm-workflow:manage-config:manage-config`

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
  plan_type: pm-workflow:plan-type-java
  compatibility: deprecations
  commit_strategy: phase-specific
```

### get

Get a specific field value.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} \
  --field plan_type
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: plan_type
value: pm-workflow:plan-type-java
```

### set

Set a specific field value.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
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

### get-multi

Get multiple fields in one call.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get-multi \
  --plan-id {plan_id} \
  --fields "plan_type,compatibility,commit_strategy"
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
plan_type: pm-workflow:plan-type-java
compatibility: deprecations
commit_strategy: phase-specific
```

### create

Create config.toon with initial values. Automatically extracts `plan_defaults` from the plan-type skill's frontmatter and applies finalize configuration fields.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config create \
  --plan-id {plan_id} \
  --plan-type pm-workflow:plan-type-java \
  [--compatibility deprecations] \
  [--commit-strategy phase-specific] \
  [--force]
```

**Automatic Plan Defaults**: The command reads the plan-type skill's SKILL.md frontmatter and extracts `plan_defaults` to populate finalize configuration:

| Frontmatter Field | Config Field | Derivation |
|-------------------|--------------|------------|
| `plan_defaults.verification_command` | `verification_command` | Direct copy |
| `plan_defaults.pr_workflow` | `create_pr` | Direct copy |
| `plan_defaults.pr_workflow` | `branch_strategy` | `feature` if true, else `direct` |
| `plan_defaults.verification_command` | `verification_required` | `true` if command exists |

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: config.toon
created: true
plan_defaults_applied: true

config:
  plan_type: pm-workflow:plan-type-java
  compatibility: deprecations
  commit_strategy: phase-specific
  create_pr: true
  verification_required: true
  verification_command: /pm-dev-builder:builder-build-and-fix
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
| plan_type | bundle:skill notation (e.g., pm-workflow:plan-type-java) |
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
message: Invalid plan_type format: unknown. Must be bundle:skill notation (e.g., pm-workflow:plan-type-java)
```

---

## Integration Points

| Consumer | Operation | Purpose |
|----------|-----------|---------|
| plan-init-agent | `create` | Create config.toon with base and finalize fields |
| plan-execute | `read`, `get` | Read commit strategy, verification settings |
| plan-finalize | `get` | Check create_pr, branch_strategy |

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `plan-marshall:plan-marshall-config` | Project-level marshal.json configuration |
