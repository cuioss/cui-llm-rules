# Skill Domains

Implementation skill management with defaults and optionals per domain.

## Purpose

Skill domains configure which implementation skills are loaded when working on code in different domains. Domains are organized into two categories:

- **System Domains**: Applied globally to all agents and skills
- **Technical Domains**: Language-specific with core/implementation/testing variants

## Structure

```json
{
  "skill_domains": {
    "system": {
      "defaults": ["plan-marshall:general-development-rules"],
      "optionals": ["plan-marshall:diagnostic-patterns"]
    },
    "java-core": {
      "defaults": ["pm-dev-java:java-core"],
      "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok", "pm-dev-java:javadoc"]
    }
  }
}
```

## Fields

### defaults

Skills that are **always loaded** when working in this domain.

```json
"defaults": ["pm-dev-java:java-core"]
```

Implementation agents automatically load these skills before starting work.

### optionals

Skills that are **available for selection** but not automatically loaded.

```json
"optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
```

Solution outline agents may suggest loading optionals based on task requirements.

## System Domains

### system

Applied to all agents and skills. Provides general development rules.

| Field | Skills |
|-------|--------|
| defaults | `plan-marshall:general-development-rules` |
| optionals | `plan-marshall:diagnostic-patterns` |

### plugin-development

Creating, updating, and verifying agents, commands, skills.

| Field | Skills |
|-------|--------|
| defaults | `pm-plugin-development:plugin-architecture`, `pm-plugin-development:plugin-script-architecture` |
| optionals | `plan-marshall:toon-usage`, `plan-marshall:script-executor` |

## Technical Domain Pattern

Each technical domain follows a three-variant pattern:

| Variant | Purpose | Example |
|---------|---------|---------|
| `{lang}-core` | Common standards applicable to both implementation and testing | `java-core` |
| `{lang}-implementation` | Production code specific standards | `java-implementation` |
| `{lang}-testing` | Test code specific standards | `java-testing` |

### Java Domains

#### java-core

Common Java standards applicable to implementation and testing.

| Field | Skills |
|-------|--------|
| defaults | `pm-dev-java:java-core` |
| optionals | `pm-dev-java:java-null-safety`, `pm-dev-java:java-lombok`, `pm-dev-java:javadoc` |

#### java-implementation

Production Java code.

| Field | Skills |
|-------|--------|
| defaults | (none - inherits from java-core) |
| optionals | `pm-dev-java:java-cdi`, `pm-dev-java:java-maintenance` |

#### java-testing

Java test code (JUnit, integration tests).

| Field | Skills |
|-------|--------|
| defaults | `pm-dev-java:junit-core` |
| optionals | `pm-dev-java:junit-integration` |

### JavaScript Domains

#### javascript-core

Common JavaScript standards applicable to implementation and testing.

| Field | Skills |
|-------|--------|
| defaults | `pm-dev-frontend:cui-javascript` |
| optionals | `pm-dev-frontend:cui-jsdoc`, `pm-dev-frontend:cui-javascript-project` |

#### javascript-implementation

Production JavaScript code.

| Field | Skills |
|-------|--------|
| defaults | (none - inherits from javascript-core) |
| optionals | `pm-dev-frontend:cui-javascript-maintenance`, `pm-dev-frontend:cui-javascript-linting` |

#### javascript-testing

JavaScript test code (Jest, Cypress).

| Field | Skills |
|-------|--------|
| defaults | `pm-dev-frontend:cui-javascript-unit-testing` |
| optionals | `pm-dev-frontend:cui-cypress` |

## Usage Patterns

### Implementation Agent: Load Skills

```bash
# Get skills to load for Java core
plan-marshall-config skill-domains get-defaults --domain java-core

# Output:
# status: success
# domain: java-core
# defaults[1]:
# - pm-dev-java:java-core
```

Agent then loads: `Skill: pm-dev-java:java-core`

### Solution Outline Agent: Suggest Optionals

```bash
# Get available optional skills
plan-marshall-config skill-domains get-optionals --domain java-implementation

# Output:
# status: success
# domain: java-implementation
# optionals[2]:
# - pm-dev-java:java-cdi
# - pm-dev-java:java-maintenance
```

Agent may suggest: "Consider loading CDI skill if using dependency injection"

### Validate Skill Availability

```bash
# Check if skill is valid for domain
plan-marshall-config skill-domains validate \
  --domain java-core \
  --skill pm-dev-java:java-lombok

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
  --defaults "pm-dev-java:java-core,pm-dev-java:java-cdi" \
  --optionals "pm-dev-java:java-maintenance"
```

## Modifying Existing Domains

```bash
# Add null-safety to Java core defaults
plan-marshall-config skill-domains set \
  --domain java-core \
  --defaults "pm-dev-java:java-core,pm-dev-java:java-null-safety"
```

## Integration with Modules

Modules reference domains in their configuration:

```json
{
  "modules": {
    "my-module": {
      "domains": ["java-core", "java-implementation", "java-testing"]
    }
  }
}
```

When working on `my-module`, agents:
1. Get domains: `["java-core", "java-implementation", "java-testing"]`
2. For each domain, load default skills
3. Consider optionals based on task requirements

## Workflow

```
Module → get-domains → [java-core, java-implementation, java-testing]
                            ↓
         skill-domains get-defaults --domain java-core
                            ↓
                    Load: pm-dev-java:java-core
                            ↓
         skill-domains get-defaults --domain java-implementation
                            ↓
                    (no additional defaults)
                            ↓
         skill-domains get-defaults --domain java-testing
                            ↓
                    Load: pm-dev-java:junit-core
```

## Best Practices

### Defaults

- Include skills that are **always needed** for the domain
- Keep defaults minimal to reduce context load
- Core coding standards belong in `*-core` domain defaults

### Optionals

- Include specialized skills (CDI, specific frameworks)
- Include maintenance/refactoring skills
- Solution outline agents decide when to suggest these

### Domain Naming

- Use lowercase with hyphens
- Follow the pattern: `{language}-core`, `{language}-implementation`, `{language}-testing`
- System domains use descriptive names: `system`, `plugin-development`
