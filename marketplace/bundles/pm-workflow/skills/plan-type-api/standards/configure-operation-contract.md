# Configure Operation Contract

Standard contract for the `configure` operation that all plan-type skills must implement.

## Purpose

The `configure` operation initializes domain-specific fields in plan references and configuration files. It is called during plan initialization after plan-type detection.

## Invocation

**Called by**: `plan-init` (after plan-type detection)

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

## Process

1. Add domain-specific fields to references.toon via `pm-workflow:manage-references:manage-references set`
2. Add finalize configuration to config.toon via `pm-workflow:manage-config:manage-config set`

## Finalize Configuration Fields

All plan types MUST set these fields in config.toon:

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `create_pr` | boolean | Whether to create a pull request | `true`, `false` |
| `verification_required` | boolean | Whether verification must pass before finalize | `true`, `false` |
| `verification_command` | string\|null | Command for verification | `/pm-dev-builder:builder-build-and-fix`, `null` |
| `branch_strategy` | string | Branch creation strategy | `feature`, `direct` |

## Script Commands

### Set References

```bash
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references set \
  --plan-id {plan_id} \
  --key {domain_field_name} \
  --value "{domain_field_value}"
```

### Set Configuration

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
  --plan-id {plan_id} \
  --key create_pr \
  --value true
```

## Plan Type Configurations

### Java Plan Type

```bash
# Finalize config
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key create_pr --value true
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_required --value true
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_command --value "/pm-dev-builder:builder-build-and-fix"
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key branch_strategy --value feature
```

### JavaScript Plan Type

```bash
# Finalize config
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key create_pr --value true
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_required --value true
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_command --value "/pm-dev-builder:builder-build-and-fix system=npm"
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key branch_strategy --value feature
```

### Plugin Development Plan Type

```bash
# Finalize config
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key create_pr --value false
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_required --value true
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_command --value "/pm-plugin-development:plugin-doctor"
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key branch_strategy --value direct
```

### Generic Plan Type

```bash
# Finalize config
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key create_pr --value false
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_required --value false
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key verification_command --value null
pm-workflow:manage-config:manage-config set --plan-id {plan_id} --key branch_strategy --value direct
```

## Return Structure

```toon
status: success|error
plan_id: {plan_id}
references_updated: {count}
config_updated: {count}
message: {error message if status=error}
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Plan not found | Return `{status: error, message: "Plan not found"}` |
| Invalid plan_id | Return `{status: error, message: "Invalid plan_id"}` |
| Script execution fails | Return error with script output |

## Integration

**Callers**: `plan-init`

**Data Layer**:
- `pm-workflow:manage-references:manage-references` - Reference operations
- `pm-workflow:manage-config:manage-config` - Configuration operations

**Consumers**: `plan-finalize` reads config.toon directly (no operation call needed)
