# Domain Manifest Schema

Human-readable documentation for the domain manifest schema.

## Overview

Domain manifests declare a bundle's domain capabilities. Each domain bundle MUST include a `skills/plan-marshall-plugin/plugin.json` file with a domain manifest.

## File Location

```
{bundle}/skills/plan-marshall-plugin/plugin.json
```

## Schema Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `$schema` | string | Schema URL with version: `...domain-manifest-v1.json` |
| `domain` | object | Domain identification |
| `domain.key` | string | Domain identifier (kebab-case, e.g., `java`, `javascript`) |
| `domain.name` | string | Human-readable name (e.g., `Java Development`) |
| `profiles` | object | Profile-based skill organization |
| `profiles.core` | object | Core skills loaded for all profiles |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `domain.description` | string | Description for UI display |
| `extensions` | object | Workflow extension references |
| `extensions.outline` | string | Outline extension skill (bundle:skill) |
| `extensions.triage` | string | Triage extension skill (bundle:skill) |
| `profiles.implementation` | object | Production code implementation skills |
| `profiles.testing` | object | Test code skills |
| `profiles.quality` | object | Documentation and verification skills |

### Profile Structure

Each profile MUST contain:

| Field | Type | Description |
|-------|------|-------------|
| `defaults` | array | Skills loaded by default (bundle:skill format) |
| `optionals` | array | Skills available as options (bundle:skill format) |

## Skill Reference Format

All skill references use `bundle:skill` format:

```
pm-dev-java:java-core
pm-dev-java:java-null-safety
```

**Pattern**: `^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$`

## Example

```json
{
  "$schema": "https://raw.githubusercontent.com/cuioss/cui-llm-rules/main/marketplace/bundles/plan-marshall/skills/domain-extension-api/schemas/domain-manifest-v1.json",
  "domain": {
    "key": "java",
    "name": "Java Development",
    "description": "Java code patterns, CDI, JUnit testing, Maven/Gradle builds"
  },
  "extensions": {
    "outline": "pm-dev-java:java-outline-ext",
    "triage": "pm-dev-java:java-triage"
  },
  "profiles": {
    "core": {
      "defaults": ["pm-dev-java:java-core"],
      "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok"]
    },
    "implementation": {
      "defaults": [],
      "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
    },
    "testing": {
      "defaults": ["pm-dev-java:junit-core"],
      "optionals": ["pm-dev-java:junit-integration"]
    },
    "quality": {
      "defaults": ["pm-dev-java:javadoc"],
      "optionals": []
    }
  }
}
```

## Validation Rules

1. **Schema compliance**: Must match JSON schema
2. **Domain key format**: kebab-case, starts with letter
3. **Skill references**: All must use `bundle:skill` format
4. **Profile structure**: Must have `defaults` and `optionals` arrays
5. **Core profile**: Required; others optional
6. **Extensions**: If declared, referenced skills must exist in bundle

## Profiles

### core

Skills loaded for ALL task profiles. Always loaded regardless of task type.

**Use for**: Fundamental domain patterns, code organization, core language features.

### implementation

Skills for production code implementation tasks.

**Use for**: CDI/DI patterns, framework-specific patterns, maintenance rules.

### testing

Skills for test code tasks.

**Use for**: Unit testing patterns, integration testing, test organization.

### quality

Skills for documentation and verification tasks.

**Use for**: JavaDoc/JSDoc standards, code quality rules, verification procedures.

## Extensions

### outline

Provides domain-specific guidance for solution outline generation.

See: [outline-extension.md](outline-extension.md)

### triage

Provides domain-specific guidance for finding triage during plan finalization.

See: [triage-extension.md](triage-extension.md)
