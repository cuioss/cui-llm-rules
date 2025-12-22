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

## Workflow Skills Access (5-Phase Model)

### resolve-workflow-skill Command

Resolves the system workflow skill for a phase. Always returns from the `system` domain.

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill --phase outline
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--phase` | string | Yes | Phase name (init, outline, plan, execute, finalize) |

**Output**:
```toon
status: success
phase: outline
workflow_skill: pm-workflow:solution-outline
```

**Error Cases**:
- System domain missing → `error: System domain not configured. Run /marshall-steward to initialize.`
- Unknown phase → `error: Unknown phase: {phase}. Available: init, outline, plan, execute, finalize`

### resolve-workflow-skill-extension Command

Resolves domain-specific workflow skill extension. Returns null (not error) if extension doesn't exist.

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill-extension --domain java --type outline
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--domain` | string | Yes | Domain name (java, javascript, etc.) |
| `--type` | string | Yes | Extension type (outline, triage) |

**Output**:
```toon
status: success
domain: java
type: outline
extension: pm-dev-java:java-outline-ext
```

### get-workflow-skills Command

Returns all workflow skills from the system domain (5-phase model).

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  get-workflow-skills
```

**Output**:
```toon
status: success
init: pm-workflow:plan-init
outline: pm-workflow:solution-outline
plan: pm-workflow:task-plan
execute: pm-workflow:task-execute
finalize: pm-workflow:plan-finalize
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
