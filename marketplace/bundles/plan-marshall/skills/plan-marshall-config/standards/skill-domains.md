# Skill Domains

Implementation skill management with defaults and optionals per domain.

## Purpose

Skill domains configure which implementation skills are loaded when working on code in different domains (Java, JavaScript, testing, etc.).

## Structure

```json
{
  "skill_domains": {
    "java": {
      "defaults": ["pm-dev-java:cui-java-core"],
      "optionals": ["pm-dev-java:cui-java-cdi"]
    },
    "java-testing": {
      "defaults": ["pm-dev-java:cui-java-unit-testing"],
      "optionals": []
    },
    "javascript": {
      "defaults": ["pm-dev-frontend:cui-javascript"],
      "optionals": []
    },
    "javascript-testing": {
      "defaults": ["pm-dev-frontend:cui-javascript-unit-testing"],
      "optionals": ["pm-dev-frontend:cui-cypress"]
    }
  }
}
```

## Fields

### defaults

Skills that are **always loaded** when working in this domain.

```json
"defaults": ["pm-dev-java:cui-java-core", "pm-dev-java:cui-javadoc"]
```

Implementation agents automatically load these skills before starting work.

### optionals

Skills that are **available for selection** but not automatically loaded.

```json
"optionals": ["pm-dev-java:cui-java-cdi", "pm-dev-java:cui-java-maintenance"]
```

Solution outline agents may suggest loading optionals based on task requirements.

## Standard Domains

### java

Production Java code.

| Field | Default Skills |
|-------|---------------|
| defaults | `pm-dev-java:cui-java-core` |
| optionals | `pm-dev-java:cui-java-cdi` |

### java-testing

Java test code (JUnit, integration tests).

| Field | Default Skills |
|-------|---------------|
| defaults | `pm-dev-java:cui-java-unit-testing` |
| optionals | (none) |

### javascript

Production JavaScript code.

| Field | Default Skills |
|-------|---------------|
| defaults | `pm-dev-frontend:cui-javascript` |
| optionals | (none) |

### javascript-testing

JavaScript test code (Jest, Cypress, Playwright).

| Field | Default Skills |
|-------|---------------|
| defaults | `pm-dev-frontend:cui-javascript-unit-testing` |
| optionals | `pm-dev-frontend:cui-cypress` |

### plugin

Claude Code marketplace plugin development.

| Field | Default Skills |
|-------|---------------|
| defaults | `pm-plugin-development:plugin-architecture` |
| optionals | `pm-plugin-development:plugin-script-architecture` |

## Usage Patterns

### Implementation Agent: Load Skills

```bash
# Get skills to load for Java work
plan-marshall-config skill-domains get-defaults --domain java

# Output:
# status: success
# domain: java
# defaults[1]:
# - pm-dev-java:cui-java-core
```

Agent then loads: `Skill: pm-dev-java:cui-java-core`

### Solution Outline Agent: Suggest Optionals

```bash
# Get available optional skills
plan-marshall-config skill-domains get-optionals --domain java

# Output:
# status: success
# domain: java
# optionals[1]:
# - pm-dev-java:cui-java-cdi
```

Agent may suggest: "Consider loading CDI skill if using dependency injection"

### Validate Skill Availability

```bash
# Check if skill is valid for domain
plan-marshall-config skill-domains validate \
  --domain java \
  --skill pm-dev-java:cui-java-cdi

# Output:
# status: success
# valid: true
# in_defaults: false
# in_optionals: true
```

## Adding Custom Domains

For projects with special requirements:

```bash
# Add a new domain
plan-marshall-config skill-domains add \
  --domain quarkus \
  --defaults "pm-dev-java:cui-java-core,pm-dev-java:cui-java-cdi" \
  --optionals "pm-dev-java:cui-java-maintenance"
```

## Modifying Existing Domains

```bash
# Add JavaDoc to Java defaults
plan-marshall-config skill-domains set \
  --domain java \
  --defaults "pm-dev-java:cui-java-core,pm-dev-java:cui-javadoc"
```

## Integration with Modules

Modules reference domains in their configuration:

```json
{
  "modules": {
    "my-module": {
      "domains": ["java", "java-testing"]
    }
  }
}
```

When working on `my-module`, agents:
1. Get domains: `["java", "java-testing"]`
2. For each domain, load default skills
3. Consider optionals based on task requirements

## Workflow

```
Module → get-domains → [java, java-testing]
                            ↓
         skill-domains get-defaults --domain java
                            ↓
                    Load: pm-dev-java:cui-java-core
                            ↓
         skill-domains get-defaults --domain java-testing
                            ↓
                    Load: pm-dev-java:cui-java-unit-testing
```

## Best Practices

### Defaults

- Include skills that are **always needed** for the domain
- Keep defaults minimal to reduce context load
- Core coding standards belong in defaults

### Optionals

- Include specialized skills (CDI, specific frameworks)
- Include maintenance/refactoring skills
- Solution outline agents decide when to suggest these

### Domain Naming

- Use lowercase with hyphens
- Suffix testing domains with `-testing`
- Be specific: `javascript-testing` not just `testing`
