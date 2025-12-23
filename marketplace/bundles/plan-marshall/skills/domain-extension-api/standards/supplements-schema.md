# Supplements Manifest Schema

Human-readable documentation for the supplement manifest schema.

## Overview

Supplement manifests add skills to an existing domain's profiles. Use supplements when a bundle provides additional skills for a domain without declaring its own domain.

## Use Case

`pm-dev-java-cui` provides CUI-specific Java patterns (logging, testing, HTTP). It shouldn't be a separate domain - it supplements the `java` domain.

## File Location

```
{bundle}/skills/plan-marshall-plugin/plugin.json
```

Same location as domain manifests, but uses different schema.

## Schema Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `$schema` | string | Schema URL with version: `...domain-supplements-v1.json` |
| `supplements` | object | Supplement configuration |
| `supplements.domain` | string | Target domain key to supplement (e.g., `java`) |
| `supplements.skills` | object | Profile-to-skills mapping |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `supplements.description` | string | Description for wizard UI |
| `supplements.skills.core` | object | Skills to add to core profile |
| `supplements.skills.implementation` | object | Skills to add to implementation profile |
| `supplements.skills.testing` | object | Skills to add to testing profile |
| `supplements.skills.quality` | object | Skills to add to quality profile |

### Profile Structure

Each profile in `skills` MAY contain:

| Field | Type | Description |
|-------|------|-------------|
| `defaults` | array | Skills added to domain defaults (bundle:skill format) |
| `optionals` | array | Skills added to domain optionals (bundle:skill format) |

## Example

```json
{
  "$schema": "https://raw.githubusercontent.com/cuioss/cui-llm-rules/main/marketplace/bundles/plan-marshall/skills/domain-extension-api/schemas/domain-supplements-v1.json",
  "supplements": {
    "domain": "java",
    "description": "CUI-specific Java patterns for logging, testing, and HTTP",
    "skills": {
      "core": {
        "defaults": [],
        "optionals": ["pm-dev-java-cui:cui-logging"]
      },
      "implementation": {
        "defaults": [],
        "optionals": ["pm-dev-java-cui:cui-http"]
      },
      "testing": {
        "defaults": [],
        "optionals": ["pm-dev-java-cui:cui-testing", "pm-dev-java-cui:cui-testing-http"]
      }
    }
  }
}
```

## Validation Rules

1. **Schema compliance**: Must match JSON schema
2. **Target domain**: Domain key must be valid (kebab-case)
3. **Profile names**: Only valid profiles (core, implementation, testing, quality)
4. **Skill references**: All must use `bundle:skill` format
5. **Skills exist**: All referenced skills must exist in the supplement bundle

## Runtime Merging

When a supplement is configured with its target domain, skills are merged:

**Original domain profile**:
```json
{
  "core": {
    "defaults": ["pm-dev-java:java-core"],
    "optionals": ["pm-dev-java:java-null-safety"]
  }
}
```

**Supplement skills**:
```json
{
  "core": {
    "defaults": [],
    "optionals": ["pm-dev-java-cui:cui-logging"]
  }
}
```

**Merged result**:
```json
{
  "core": {
    "defaults": ["pm-dev-java:java-core"],
    "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java-cui:cui-logging"]
  }
}
```

## Benefits

| Aspect | Description |
|--------|-------------|
| No coupling | Domain bundle doesn't need to know about supplement bundles |
| Auto-discovery | Supplements found by same mechanism as domains |
| Clear UX | User sees "supplements for java" relationship |
| Flexible | Supplements can target any profile in any domain |

## Wizard Integration

The marshall-steward wizard shows supplements after domain selection:

```
Step 4d: Skill Domain Configuration

Discovered domains:
  [x] java - Java Development
  [ ] javascript - JavaScript Development

Supplements available for selected domains:
  [x] pm-dev-java-cui (for java) - CUI-specific Java patterns

Selected supplements will be merged into domain profiles as optionals.
```
