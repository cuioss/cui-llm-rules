# Data Model

JSON structure and field definitions for project configuration.

## File Location

`.plan/marshal.json`

## Complete Structure

```json
{
  "skill_domains": {
    "system": {
      "defaults": ["plan-marshall:general-development-rules"],
      "optionals": ["plan-marshall:diagnostic-patterns"]
    },
    "plugin-development": {
      "defaults": ["pm-plugin-development:plugin-architecture", "pm-plugin-development:plugin-script-architecture"],
      "optionals": ["plan-marshall:toon-usage", "plan-marshall:script-executor"]
    },
    "java-core": {
      "defaults": ["pm-dev-java:java-core"],
      "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok", "pm-dev-java:javadoc"]
    },
    "java-implementation": {
      "defaults": [],
      "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
    },
    "java-testing": {
      "defaults": ["pm-dev-java:junit-core"],
      "optionals": ["pm-dev-java:junit-integration"]
    },
    "javascript-core": {
      "defaults": ["pm-dev-frontend:cui-javascript"],
      "optionals": ["pm-dev-frontend:cui-jsdoc", "pm-dev-frontend:cui-javascript-project"]
    },
    "javascript-implementation": {
      "defaults": [],
      "optionals": ["pm-dev-frontend:cui-javascript-maintenance", "pm-dev-frontend:cui-javascript-linting"]
    },
    "javascript-testing": {
      "defaults": ["pm-dev-frontend:cui-javascript-unit-testing"],
      "optionals": ["pm-dev-frontend:cui-cypress"]
    }
  },
  "modules": {
    "my-core": {
      "path": "my-core",
      "domains": ["java-core", "java-implementation"],
      "build_systems": ["maven"]
    },
    "my-ui": {
      "path": "my-ui",
      "domains": ["java-core", "java-implementation", "javascript-core", "javascript-implementation"],
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

### Domain Categories

#### System Domains

| Domain | Purpose |
|--------|---------|
| `system` | Applied to all agents and skills |
| `plugin-development` | Creating, updating, and verifying agents, commands, skills |

#### Technical Domains

Each technical domain follows the pattern: `{language}-core`, `{language}-implementation`, `{language}-testing`.

| Domain | Purpose |
|--------|---------|
| `java-core` | Common Java standards (applies to implementation and testing) |
| `java-implementation` | Production Java code |
| `java-testing` | Java test code |
| `javascript-core` | Common JavaScript standards (applies to implementation and testing) |
| `javascript-implementation` | Production JavaScript code |
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

## Section: ci

CI provider configuration (project-level, shared via git).

### Structure

```json
{
  "ci": {
    "repo_url": "https://github.com/org/repo",
    "provider": "github",
    "detected_at": "2025-01-15T10:30:00Z"
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo_url` | string | No | Git remote origin URL |
| `provider` | string | Yes | CI provider: `github`, `gitlab`, `unknown` |
| `detected_at` | string | No | ISO timestamp of last detection |

### Provider Values

| Value | CLI Tool | Description |
|-------|----------|-------------|
| `github` | `gh` | GitHub (github.com or enterprise) |
| `gitlab` | `glab` | GitLab (gitlab.com or self-hosted) |
| `unknown` | - | Could not detect provider |

### Note: Authenticated Tools

Tool availability (`authenticated_tools`) is stored in `run-configuration.json` (local, not shared via git) since it varies per developer machine. See run-config skill for the `ci` section schema.

## Template Location

Default values are provided by:

```
plan-marshall/skills/plan-marshall-config/templates/marshal-defaults.json
```

Copied to `.plan/marshal.json` during `init`.
