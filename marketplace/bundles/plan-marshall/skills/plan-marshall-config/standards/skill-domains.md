# Skill Domains

Implementation skill management with nested structure for domains, profiles, and workflow skills.

## Purpose

Skill domains configure which implementation skills are loaded when working on code in different domains. The structure supports:

- **System Domains**: Applied globally to all agents (flat structure)
- **Technical Domains**: Language-specific with nested profiles (java, javascript)

## Structure

### Nested Domain Structure (Technical Domains)

```json
{
  "skill_domains": {
    "java": {
      "workflow_skills": {
        "solution_outline": "pm-workflow:solution-outline",
        "task_plan": "pm-workflow:task-plan",
        "implementation": "pm-workflow:task-implementation",
        "testing": "pm-workflow:task-testing"
      },
      "core": {
        "defaults": ["pm-dev-java:java-core"],
        "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok", "pm-dev-java:javadoc"]
      },
      "implementation": {
        "defaults": [],
        "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
      },
      "testing": {
        "defaults": ["pm-dev-java:junit-core"],
        "optionals": ["pm-dev-java:junit-integration"]
      }
    }
  }
}
```

### Flat Domain Structure (System Domain)

```json
{
  "skill_domains": {
    "system": {
      "defaults": ["plan-marshall:general-development-rules"],
      "optionals": ["plan-marshall:diagnostic-patterns"]
    }
  }
}
```

## Nested Structure Components

### workflow_skills

Defines workflow-specific skills loaded by thin agents during task execution.

| Key | Purpose |
|-----|---------|
| `solution_outline` | Skill for creating solution outlines |
| `task_plan` | Skill for task planning |
| `implementation` | Skill for code implementation |
| `testing` | Skill for test implementation |

### core

Foundation skills always included when the domain is selected.

```json
"core": {
  "defaults": ["pm-dev-java:java-core"],
  "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok"]
}
```

### implementation

Profile for production code tasks.

```json
"implementation": {
  "defaults": [],
  "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
}
```

### testing

Profile for test code tasks.

```json
"testing": {
  "defaults": ["pm-dev-java:junit-core"],
  "optionals": ["pm-dev-java:junit-integration"]
}
```

## Profile Naming Convention

| Element | Purpose | Examples |
|---------|---------|----------|
| `{domain}` | Top-level domain entry | `java`, `javascript` |
| `{domain}.core` | Foundation skills for domain | `java.core`, `javascript.core` |
| `{domain}.implementation` | Implementation profile skills | `java.implementation` |
| `{domain}.testing` | Testing profile skills | `java.testing` |

## System Domain

### system

Applied to all agents and skills. Uses flat structure (no profiles).

| Field | Skills |
|-------|--------|
| defaults | `plan-marshall:general-development-rules` |
| optionals | `plan-marshall:diagnostic-patterns` |

## Technical Domains

### java

Java development with CDI, JUnit, and standard patterns.

**workflow_skills**:
| Key | Skill |
|-----|-------|
| solution_outline | `pm-workflow:solution-outline` |
| task_plan | `pm-workflow:task-plan` |
| implementation | `pm-workflow:task-implementation` |
| testing | `pm-workflow:task-testing` |

**core**:
| Field | Skills |
|-------|--------|
| defaults | `pm-dev-java:java-core` |
| optionals | `pm-dev-java:java-null-safety`, `pm-dev-java:java-lombok`, `pm-dev-java:javadoc` |

**implementation**:
| Field | Skills |
|-------|--------|
| defaults | (none) |
| optionals | `pm-dev-java:java-cdi`, `pm-dev-java:java-maintenance` |

**testing**:
| Field | Skills |
|-------|--------|
| defaults | `pm-dev-java:junit-core` |
| optionals | `pm-dev-java:junit-integration` |

### javascript

JavaScript/Frontend development with Jest and Cypress testing.

**workflow_skills**: Same as java domain.

**core**:
| Field | Skills |
|-------|--------|
| defaults | `pm-dev-frontend:cui-javascript` |
| optionals | `pm-dev-frontend:cui-jsdoc`, `pm-dev-frontend:cui-javascript-project` |

**implementation**:
| Field | Skills |
|-------|--------|
| defaults | (none) |
| optionals | `pm-dev-frontend:cui-javascript-linting`, `pm-dev-frontend:cui-javascript-maintenance` |

**testing**:
| Field | Skills |
|-------|--------|
| defaults | `pm-dev-frontend:cui-javascript-unit-testing` |
| optionals | `pm-dev-frontend:cui-cypress` |

## Skill Resolution

### resolve-domain-skills Command

Aggregates `{domain}.core` + `{domain}.{profile}` skills with descriptions.

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-domain-skills --domain java --profile implementation
```

**Output**:
```toon
status: success
domain: java
profile: implementation

defaults:
  pm-dev-java:java-core: Java patterns, CUI conventions, CuiLogger, null-safety

optionals:
  pm-dev-java:java-null-safety: JSpecify annotations (@NullMarked, @Nullable)
  pm-dev-java:java-lombok: Lombok annotations (@Builder, @Value, @Delegate)
  pm-dev-java:java-cdi: CDI patterns (@ApplicationScoped, @Inject)
  pm-dev-java:java-maintenance: Code maintenance and refactoring patterns
```

### Aggregation Logic

| Profile | Defaults | Optionals |
|---------|----------|-----------|
| `implementation` | `{domain}.core.defaults` + `{domain}.implementation.defaults` | `{domain}.core.optionals` + `{domain}.implementation.optionals` |
| `testing` | `{domain}.core.defaults` + `{domain}.testing.defaults` | `{domain}.core.optionals` + `{domain}.testing.optionals` |

## Workflow Skills Access

### resolve-workflow-skill Command

Resolves the workflow skill for a specific domain and phase combination. This is the primary method for workflow skill resolution.

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill --domain java --phase implementation
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--domain` | string | Yes | Domain name (java, javascript, plugin, generic) |
| `--phase` | string | Yes | Phase name (solution_outline, task_plan, implementation, testing) |

**Output**:
```toon
status: success
domain: java
phase: implementation
workflow_skill: pm-workflow:task-implementation
```

**Error Cases**:
- Unknown domain → `error: Unknown domain: {domain}. Available: java, javascript, plugin, generic`
- No workflow_skills configured → `error: Domain '{domain}' has no workflow_skills configured`
- Unknown phase → `error: Unknown phase: {phase} for domain: {domain}. Available: {phases}`

### get-workflow-skills Command

Returns domain-agnostic workflow skills (backward compatible).

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  get-workflow-skills
```

**Output**:
```toon
status: success
solution_outline: pm-workflow:solution-outline
task_plan: pm-workflow:task-plan
implementation: pm-workflow:task-implementation
testing: pm-workflow:task-testing
```

## Usage Patterns

### Get Domain Configuration (Nested)

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get --domain java
```

Returns full nested structure including workflow_skills, core, implementation, and testing.

### Get Domain Defaults (Backward Compatible)

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-defaults --domain java
```

Returns `core.defaults` for nested domains.

### Get Domain Optionals (Backward Compatible)

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-optionals --domain java
```

Returns `core.optionals` for nested domains.

### Validate Skill in Domain

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains validate --domain java --skill pm-dev-java:junit-core
```

Searches all profiles (core, implementation, testing) for nested domains.

## Adding New Domains

### Adding a Technical Domain

```json
"python": {
  "workflow_skills": {
    "solution_outline": "pm-workflow:solution-outline",
    "task_plan": "pm-workflow:task-plan",
    "implementation": "pm-workflow:task-implementation",
    "testing": "pm-workflow:task-testing"
  },
  "core": {
    "defaults": ["pm-dev-python:python-core"],
    "optionals": ["pm-dev-python:python-typing"]
  },
  "implementation": {
    "defaults": [],
    "optionals": []
  },
  "testing": {
    "defaults": ["pm-dev-python:pytest-core"],
    "optionals": []
  }
}
```

No agent changes needed - thin agents work with any domain.

## Best Practices

### Defaults

- Include skills **always needed** for the profile
- Keep defaults minimal to reduce context load
- Core coding standards belong in `core.defaults`

### Optionals

- Include specialized skills (CDI, specific frameworks)
- Include maintenance/refactoring skills
- Task planning agents select based on task requirements

### Profiles

- Use `implementation` for production code tasks
- Use `testing` for test code tasks
- Core skills apply to both profiles
