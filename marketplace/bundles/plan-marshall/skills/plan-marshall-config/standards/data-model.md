# Data Model

JSON structure and field definitions for project configuration.

## File Location

`.plan/marshal.json`

## Complete Structure

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
  },
  "modules": {
    "my-core": {
      "path": "my-core",
      "domains": ["java"],
      "build_systems": ["maven"]
    },
    "my-ui": {
      "path": "my-ui",
      "domains": ["java", "javascript"],
      "build_systems": ["maven", "npm"],
      "commands": {
        "npm": {
          "test": "custom:test"
        }
      }
    }
  },
  "build_systems": [
    {
      "system": "maven",
      "skill": "pm-dev-builder:builder-maven-rules",
      "commands": {
        "compile": "compile",
        "test": "clean test",
        "verify": "clean verify",
        "install": "clean install"
      }
    }
  ],
  "system": {
    "retention": {
      "logs_days": 1,
      "archived_plans_days": 5,
      "memory_days": 5,
      "temp_on_maintenance": true
    }
  },
  "plan": {
    "defaults": {
      "compatibility": "deprecations",
      "commit_strategy": "phase-specific",
      "create_pr": false,
      "verification_required": true,
      "branch_strategy": "direct"
    }
  }
}
```

## Section: skill_domains

Implementation skill configuration per domain.

### Structure

```json
{
  "skill_domains": {
    "{domain-name}": {
      "defaults": ["bundle:skill", ...],
      "optionals": ["bundle:skill", ...]
    }
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `defaults` | array | Skills always loaded for this domain |
| `optionals` | array | Skills available for selection |

### Standard Domains

| Domain | Purpose |
|--------|---------|
| `java` | Production Java code |
| `java-testing` | Java test code |
| `javascript` | Production JavaScript code |
| `javascript-testing` | JavaScript test code |

## Section: modules

Project module configuration with domain and build system mappings.

### Structure

```json
{
  "modules": {
    "{module-name}": {
      "path": "relative/path",
      "domains": ["domain1", "domain2"],
      "build_systems": ["system1", "system2"],
      "commands": {
        "{system}": {
          "{label}": "command"
        }
      }
    }
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Relative path from project root |
| `domains` | array | Yes | Skill domains for this module |
| `build_systems` | array | Yes | Available build systems |
| `commands` | object | No | Module-specific command overrides |

### Command Resolution

1. Check module-specific override: `modules.{name}.commands.{system}.{label}`
2. Fall back to project-level: `build_systems[system].commands.{label}`

## Section: build_systems

Build system configuration with command mappings.

### Structure

```json
{
  "build_systems": [
    {
      "system": "maven",
      "skill": "pm-dev-builder:builder-maven-rules",
      "commands": {
        "label": "command"
      }
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `system` | string | Build system identifier |
| `skill` | string | Skill for executing builds |
| `commands` | object | Label to command mapping |

### Standard Command Labels

| Label | Purpose |
|-------|---------|
| `compile` | Compile source code |
| `test` | Run unit tests |
| `verify` | Full verification |
| `install` | Install artifacts |
| `pre-commit` | Pre-commit checks |
| `coverage` | Coverage analysis |

## Section: system

System-level infrastructure settings.

### Structure

```json
{
  "system": {
    "retention": {
      "logs_days": 1,
      "archived_plans_days": 5,
      "memory_days": 5,
      "temp_on_maintenance": true
    }
  }
}
```

### Retention Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `logs_days` | int | 1 | Days to keep execution logs |
| `archived_plans_days` | int | 5 | Days to keep archived plans |
| `memory_days` | int | 5 | Days to keep memory entries |
| `temp_on_maintenance` | bool | true | Clean temp on maintenance |

## Section: plan

Plan-related configuration.

### Structure

```json
{
  "plan": {
    "defaults": {
      "compatibility": "deprecations",
      "commit_strategy": "phase-specific",
      "create_pr": false,
      "verification_required": true,
      "branch_strategy": "direct"
    }
  }
}
```

### Defaults Fields

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `compatibility` | string | "breaking" | deprecations, breaking |
| `commit_strategy` | string | "phase-specific" | fine-granular, phase-specific, complete |
| `create_pr` | bool | false | true, false |
| `verification_required` | bool | true | true, false |
| `branch_strategy` | string | "direct" | direct, feature |

## Template Location

Default values are provided by:

```
plan-marshall/skills/plan-marshall-config/templates/marshal-defaults.json
```

Copied to `.plan/marshal.json` during `init`.
