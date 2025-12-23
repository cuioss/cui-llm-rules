# Profile Contract

Contract for profile structure in domain and supplement manifests.

## Overview

Profiles organize skills by task type. Each profile contains default and optional skills that are loaded during task execution.

## Standard Profiles

| Profile | Phase | Purpose |
|---------|-------|---------|
| `core` | all | Skills loaded for all task types |
| `implementation` | execute | Production code implementation |
| `testing` | execute | Test code tasks |
| `quality` | finalize | Documentation and verification |

## Profile Structure

### Required Fields

Each profile MUST contain:

```json
{
  "defaults": [],
  "optionals": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `defaults` | array | Skills loaded automatically |
| `optionals` | array | Skills available for selection |

### Skill Reference Format

All skill references use `bundle:skill` format:

```
pm-dev-java:java-core
pm-dev-java:junit-core
```

**Pattern**: `^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$`

## Profile Requirements

### core (Required)

The `core` profile is REQUIRED in domain manifests.

**Purpose**: Fundamental domain knowledge loaded for all tasks.

**Include**:
- Core language/framework patterns
- Code organization standards
- Fundamental best practices

**Example**:
```json
{
  "core": {
    "defaults": ["pm-dev-java:java-core"],
    "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok"]
  }
}
```

### implementation (Optional)

**Purpose**: Skills for production code tasks.

**Include**:
- Framework-specific patterns (CDI, Spring, etc.)
- Integration patterns
- Maintenance guidelines

**Example**:
```json
{
  "implementation": {
    "defaults": [],
    "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
  }
}
```

### testing (Optional)

**Purpose**: Skills for test code tasks.

**Include**:
- Unit testing patterns
- Integration testing patterns
- Test organization

**Example**:
```json
{
  "testing": {
    "defaults": ["pm-dev-java:junit-core"],
    "optionals": ["pm-dev-java:junit-integration"]
  }
}
```

### quality (Optional)

**Purpose**: Skills for documentation and verification.

**Include**:
- Documentation standards (JavaDoc, JSDoc)
- Code quality rules
- Verification procedures

**Example**:
```json
{
  "quality": {
    "defaults": ["pm-dev-java:javadoc"],
    "optionals": []
  }
}
```

## Skill Loading

### Domain Skills

During task execution:

1. Load `system.defaults` (always)
2. Load `{domain}.core.defaults`
3. Load `{domain}.{profile}.defaults` for task profile
4. Optionally load selected skills from optionals

### Supplemented Skills

When supplements are configured:

1. Load domain skills as above
2. Merge supplement defaults into domain defaults
3. Merge supplement optionals into domain optionals

## Validation Rules

1. **Profile names**: Only `core`, `implementation`, `testing`, `quality`
2. **Required fields**: Both `defaults` and `optionals` must be arrays
3. **Skill format**: All entries must match `bundle:skill` pattern
4. **Skill existence**: Referenced skills must exist in the bundle

## Empty Profiles

Profiles MAY have empty arrays:

```json
{
  "implementation": {
    "defaults": [],
    "optionals": []
  }
}
```

This is valid and indicates no additional skills for that profile.

## Supplement Profiles

Supplements follow the same structure but add to existing profiles:

```json
{
  "supplements": {
    "domain": "java",
    "skills": {
      "core": {
        "defaults": [],
        "optionals": ["pm-dev-java-cui:cui-logging"]
      }
    }
  }
}
```

Supplement skills are merged with domain skills at runtime.
