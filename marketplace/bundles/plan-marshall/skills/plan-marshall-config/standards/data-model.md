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
    "default": {
      "path": ".",
      "type": "pom",
      "domains": ["java-core", "java-implementation"],
      "build_systems": ["maven"],
      "detected_profiles": [
        {"id": "pre-commit", "canonical": "quality-gate", "activation": {"type": "command-line"}}
      ],
      "commands": {
        "quality-gate": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\"",
        "install": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean install\""
      }
    },
    "my-module": {
      "path": "my-module",
      "type": "jar",
      "domains": ["java-core", "java-implementation"],
      "build_systems": ["maven"],
      "commands": {
        "module-tests": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\" --module my-module",
        "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\" --module my-module",
        "quality-gate": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\" --module my-module"
      }
    },
    "my-hybrid-ui": {
      "path": "my-hybrid-ui",
      "type": "war",
      "domains": ["java-core", "java-implementation", "javascript-core", "javascript-implementation"],
      "build_systems": ["maven", "npm"],
      "commands": {
        "module-tests": {
          "maven": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\" --module my-hybrid-ui",
          "npm": "python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command \"run test\" --module my-hybrid-ui"
        },
        "quality-gate": {
          "maven": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\" --module my-hybrid-ui",
          "npm": "python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command \"run lint && npm run format:check\" --module my-hybrid-ui"
        }
      }
    }
  },
  "build_systems": [
    {
      "system": "maven",
      "skill": "plan-marshall:build-operations"
    },
    {
      "system": "gradle",
      "skill": "plan-marshall:build-operations"
    },
    {
      "system": "npm",
      "skill": "plan-marshall:build-operations"
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
    },
    "finalize": {
      "commit": true
    }
  },
  "ci": {
    "enabled": true,
    "repo_url": "https://github.com/org/repo",
    "provider": "github",
    "sonar_project": null
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

Project module configuration with type, domain, build system, and canonical command mappings.

### Structure

```json
{
  "modules": {
    "{module-name}": {
      "path": "relative/path",
      "type": "jar|pom|war|quarkus|npm",
      "domains": ["domain1", "domain2"],
      "build_systems": ["system1", "system2"],
      "detected_profiles": [
        {"id": "profile-id", "canonical": "canonical-name", "activation": {"type": "command-line|property"}}
      ],
      "commands": {
        "{canonical-name}": "python3 .plan/execute-script.py plan-marshall:build-operations:{system} execute --goals \"{goals}\""
      }
    }
  }
}
```

### Example (Single Build System)

```json
{
  "modules": {
    "my-module": {
      "path": "my-module",
      "type": "jar",
      "domains": ["java-core", "java-implementation"],
      "build_systems": ["maven"],
      "detected_profiles": [
        {"id": "integration-tests", "canonical": "integration-tests", "activation": {"type": "command-line"}},
        {"id": "coverage", "canonical": "coverage", "activation": {"type": "command-line"}}
      ],
      "commands": {
        "module-tests": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\" --module my-module",
        "integration-tests": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Pintegration-tests\" --module my-module",
        "coverage": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Pcoverage\" --module my-module",
        "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\" --module my-module",
        "quality-gate": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\" --module my-module"
      }
    }
  }
}
```

### Example (Hybrid Module - Maven + npm)

For modules with multiple build systems, commands use nested format:

```json
{
  "modules": {
    "my-hybrid-ui": {
      "path": "my-hybrid-ui",
      "type": "war",
      "domains": ["java-core", "javascript-core"],
      "build_systems": ["maven", "npm"],
      "commands": {
        "module-tests": {
          "maven": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\" --module my-hybrid-ui",
          "npm": "python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command \"run test\" --module my-hybrid-ui"
        },
        "quality-gate": {
          "maven": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\" --module my-hybrid-ui",
          "npm": "python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command \"run lint && npm run format:check\" --module my-hybrid-ui"
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
| `type` | string | Yes | Module type: `pom`, `jar`, `war`, `quarkus`, `npm` |
| `domains` | array | Yes | Skill domains for this module |
| `build_systems` | array | Yes | Available build systems (for detection info) |
| `detected_profiles` | array | No | Maven/Gradle profiles with canonical mappings |
| `commands` | object | Yes | Canonical name to command string (or nested dict for hybrid) |

### Module Types

| Type | Description | Applicable Commands |
|------|-------------|---------------------|
| `pom` | Parent/BOM module | install, quality-gate (no tests) |
| `jar` | Library module | All canonical commands |
| `war` | Web application | All canonical commands |
| `quarkus` | Quarkus application | All canonical commands + native |
| `npm` | npm project | npm-specific commands only |

### Canonical Command Names

Commands use a fixed vocabulary for programmatic lookup:

| Canonical | Phase | Description |
|-----------|-------|-------------|
| `compile` | build | Compile production code |
| `test-compile` | build | Compile test code |
| `module-tests` | test | Unit tests for the module |
| `integration-tests` | test | Integration/E2E tests |
| `coverage` | test | Test coverage reports |
| `performance` | test | Benchmark/performance tests |
| `quality-gate` | quality | Pre-commit checks (lint, format, static analysis) |
| `verify` | verify | Full build verification |
| `install` | deploy | Install to local repository |
| `package` | deploy | Create distributable package |

### Command Resolution (Static Routing)

Commands are stored as **full executable strings** - no runtime routing needed:

1. Get command from `modules.{name}.commands.{canonical}`
2. For hybrid modules, specify build system: `modules.{name}.commands.{canonical}.{system}`
3. Execute directly with `eval "$COMMAND"`
4. If module doesn't have the canonical, fall back to `modules.default.commands.{canonical}`

### Lookup API

Use the build_env script for programmatic command lookup:

```bash
# Single build system module
python3 .plan/execute-script.py plan-marshall:build-operations:build_env lookup \
  --canonical "module-tests" --module "my-module"

# Hybrid module with build system filter
python3 .plan/execute-script.py plan-marshall:build-operations:build_env lookup \
  --canonical "module-tests" --module "my-hybrid-ui" --build-system "npm"
```

### Static Routing Benefits

- **Transparency**: Config shows exactly what runs
- **Customization**: User can edit marshal.json to customize any command
- **No runtime logic**: Command already contains correct script path
- **Single mental model**: Same pattern as CI commands
- **Programmatic lookup**: Agents use canonical names for consistent API

## Section: build_systems

Build system detection and skill reference. Used by wizard for initial setup.

### Structure

```json
{
  "build_systems": [
    {
      "system": "maven",
      "skill": "plan-marshall:build-operations"
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `system` | string | Build system identifier (maven, gradle, npm) |
| `skill` | string | Skill for executing builds |

### Role in Static Routing

The `build_systems` section serves as:
- **Detection reference**: Wizard uses this to map detected systems to skills
- **Skill lookup**: Agents can look up which skill handles which system

Command execution uses `modules.{name}.commands.{label}` directly - no runtime routing through build_systems is needed.

### Supported Systems

| System | Skill | Detection Files |
|--------|-------|-----------------|
| `maven` | `plan-marshall:build-operations` | `pom.xml` |
| `gradle` | `plan-marshall:build-operations` | `build.gradle`, `build.gradle.kts` |
| `npm` | `plan-marshall:build-operations` | `package.json` |

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

Plan-related configuration including execution defaults and finalize behavior.

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
    },
    "finalize": {
      "commit": true
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

### Finalize Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `commit` | bool | true | Commit changes after finalize phase |

Note: `create_pr` is in `defaults` as it applies to multiple phases. The finalize workflow skill reads both `plan.defaults.create_pr` and `plan.finalize.commit`.

## Section: ci

CI provider configuration (project-level, shared via git).

### Structure

```json
{
  "ci": {
    "enabled": true,
    "repo_url": "https://github.com/org/repo",
    "provider": "github",
    "detected_at": "2025-01-15T10:30:00Z",
    "sonar_project": "my-project-key"
  }
}
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | bool | No | true | Whether to wait for CI checks during finalize |
| `repo_url` | string | No | - | Git remote origin URL |
| `provider` | string | Yes | - | CI provider: `github`, `gitlab`, `unknown` |
| `detected_at` | string | No | - | ISO timestamp of last detection |
| `sonar_project` | string | No | null | SonarQube/Cloud project key (if Sonar analysis is configured) |

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
