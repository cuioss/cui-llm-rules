---
name: plan-marshall-config
description: Project-level infrastructure configuration for marshal.json
allowed-tools: Read, Write, Edit, Bash
---

# Plan-Marshall Config Skill

Manages project-level infrastructure configuration in `.plan/marshal.json`.

## What This Skill Provides

- **Skill Domains**: Implementation skill defaults and optionals per domain
- **Modules**: Project module configuration with domain/build-system mappings
- **Build Systems**: Build system detection and command configuration
- **System Settings**: Retention and cleanup configuration
- **Plan Defaults**: Default values for new plans

## When to Activate This Skill

Activate this skill when:
- Initializing project configuration (`/plan-marshall` wizard)
- Querying implementation skills for a domain
- Resolving build commands for a module
- Managing retention settings
- Configuring plan defaults

---

## Workflow: Initialize Configuration

**Pattern**: Script Automation

Initialize marshal.json with defaults and auto-detection.

### Step 1: Initialize

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config init
```

### Step 2: Detect Build Systems

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems detect
```

### Step 3: Detect Modules

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules detect
```

---

## Workflow: Query Skill Domains

**Pattern**: Read-Process-Write

Get implementation skills for a specific domain.

### Get Domain Defaults

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-defaults --domain java-core
```

**Output**:
```toon
status: success
domain: java-core
defaults[1]:
- pm-dev-java:java-core
```

### Get Domain Optionals

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-optionals --domain java-implementation
```

### Validate Skill in Domain

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains validate --domain java-core --skill pm-dev-java:java-lombok
```

---

## Workflow: Query Module Configuration

**Pattern**: Read-Process-Write

Get module-specific configuration including domain and build system mappings.

### List All Modules

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  modules list
```

### Get Module Domains

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  modules get-domains --module my-module
```

### Get Build Command (with Override Resolution)

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  modules get-command --module my-module --system maven --label verify
```

**Output**:
```toon
status: success
module: my-module
system: maven
label: verify
command: clean verify
source: project_level
```

Command resolution order:
1. Module-specific override (if defined in `modules.{name}.commands`)
2. Project-level build system command (fallback)

---

## Workflow: Query Build Systems

**Pattern**: Read-Process-Write

Get build system configuration and commands.

### List Build Systems

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  build-systems list
```

### Get Command for Label

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  build-systems get-command --system maven --label verify
```

---

## Workflow: System Settings

**Pattern**: Read-Process-Write

Manage system-level infrastructure settings.

### Get Retention Settings

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  system retention get
```

### Set Retention Field

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  system retention set --field logs_days --value 7
```

---

## Workflow: Plan Defaults

**Pattern**: Read-Process-Write

Manage default values for new plans.

### List Plan Defaults

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  plan defaults list
```

### Get Specific Default

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  plan defaults get --field commit_strategy
```

### Set Default Value

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  plan defaults set --field create_pr --value true
```

---

## API Reference

### Noun: skill-domains

| Verb | Parameters | Purpose |
|------|------------|---------|
| `list` | (none) | List all domains |
| `get` | `--domain` | Get full domain config (returns nested structure for technical domains) |
| `get-defaults` | `--domain` | Get default skills (returns `core.defaults` for nested domains) |
| `get-optionals` | `--domain` | Get optional skills (returns `core.optionals` for nested domains) |
| `set` | `--domain [--defaults] [--optionals]` | Set domain config |
| `add` | `--domain --defaults [--optionals]` | Add new domain |
| `validate` | `--domain --skill` | Check if skill valid (searches all profiles for nested domains) |
| `detect` | (none) | Auto-detect domains from project files (pom.xml → java, package.json → javascript) |

### resolve-domain-skills

| Parameters | Purpose |
|------------|---------|
| `--domain --profile` | Resolve skills for domain and profile (aggregates `{domain}.core` + `{domain}.{profile}`) |

Profiles are convention-based (derived from domain config keys). Standard profiles: `implementation`, `testing`. Custom profiles can be added.

### get-workflow-skills

| Parameters | Purpose |
|------------|---------|
| (none) | Get domain-agnostic workflow skills (solution_outline, task_plan, implementation, testing) |

### Noun: modules

| Verb | Parameters | Purpose |
|------|------------|---------|
| `list` | (none) | List all modules with domains |
| `get` | `--module` | Get full module config |
| `get-domains` | `--module` | Get skill domains for module |
| `get-build-systems` | `--module` | Get available build systems for module |
| `get-command` | `--module --system --label` | Get command (with module override resolution) |
| `add` | `--module --path --domains --build-systems` | Add new module |
| `set` | `--module [--domains] [--build-systems]` | Update module config |
| `remove` | `--module` | Remove module |
| `detect` | (none) | Auto-detect modules from pom.xml/build.gradle/package.json |

### Noun: build-systems

| Verb | Parameters | Purpose |
|------|------------|---------|
| `list` | (none) | List configured systems with commands |
| `get` | `--system` | Get specific build system config |
| `get-command` | `--system --label` | Get command for label |
| `add` | `--system` | Add build system with default commands |
| `remove` | `--system` | Remove build system |
| `detect` | (none) | Auto-detect from project and populate commands |

### Noun: system

| Verb | Parameters | Purpose |
|------|------------|---------|
| `retention get` | (none) | Get all retention settings |
| `retention set` | `--field --value` | Set retention field |

### Noun: plan

| Verb | Parameters | Purpose |
|------|------------|---------|
| `defaults list` | (none) | List all plan defaults |
| `defaults get` | `--field` | Get default value |
| `defaults set` | `--field --value` | Set default value |

### init

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  init [--force]
```

---

## Data Model

### marshal.json Location

`.plan/marshal.json`

### Structure

The defaults template contains only `system` domain. Technical domains (java, javascript, etc.) are added during project initialization based on detection or manual configuration.

**Example** (Java project after init):

```json
{
  "skill_domains": {
    "system": {
      "defaults": ["plan-marshall:general-development-rules"],
      "optionals": ["plan-marshall:diagnostic-patterns"]
    },
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
  },
  "modules": {
    "my-module": {
      "path": "my-module",
      "domains": ["java"],
      "build_systems": ["maven"]
    }
  },
  "build_systems": [
    {
      "system": "maven",
      "skill": "pm-dev-builder:builder-maven-rules",
      "commands": {
        "verify": "clean verify"
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

---

## Standard Domains

### System Domains (Flat Structure)

| Domain | Purpose | Default Skills |
|--------|---------|----------------|
| `system` | Applied to all agents/skills | `plan-marshall:general-development-rules` |

### Technical Domains (Nested Structure)

Technical domains use nested structure with `workflow_skills`, `core`, `implementation`, and `testing` profiles.

| Domain | Purpose | Core Defaults | Core Optionals |
|--------|---------|---------------|----------------|
| `java` | Java development | `pm-dev-java:java-core` | `pm-dev-java:java-null-safety`, `pm-dev-java:java-lombok`, `pm-dev-java:javadoc` |
| `javascript` | JavaScript/Frontend | `pm-dev-frontend:cui-javascript` | `pm-dev-frontend:cui-jsdoc`, `pm-dev-frontend:cui-javascript-project` |

Use `resolve-domain-skills --domain {domain} --profile {profile}` to get aggregated skills.

---

## Standard Command Labels

| Label | Purpose | Maven | Gradle | npm |
|-------|---------|-------|--------|-----|
| `compile` | Compile source | `compile` | `compileJava` | `run build` |
| `test` | Run unit tests | `clean test` | `clean test` | `run test` |
| `verify` | Full verification | `clean verify` | `clean check` | `run test && run lint` |
| `install` | Install artifacts | `clean install` | `publishToMavenLocal` | - |
| `pre-commit` | Pre-commit checks | `-Ppre-commit clean install` | `preCommit` | - |
| `coverage` | Coverage analysis | `-Pcoverage clean verify` | `jacocoTestReport` | `run test:coverage` |

---

## Scripts

| Script | Notation |
|--------|----------|
| plan-marshall-config | `plan-marshall:plan-marshall-config` |

Script characteristics:
- Uses Python stdlib only (json, argparse, pathlib, xml.etree)
- Outputs TOON to stdout
- Exit code 0 for success, 1 for errors
- Supports `--help` flag

---

## Integration Points

### With plan-marshall Skill
- Called during wizard initialization
- Called from configuration menus

### With Implementation Agents
- `skill-domains get-defaults` provides skills to load
- `skill-domains get-optionals` provides available optionals

### With Build Commands
- `modules get-command` resolves build commands with overrides
- `build-systems get-command` provides project-level commands

### With Cleanup
- `system retention get` provides retention settings

---

## Error Handling

All operations validate prerequisites before proceeding:

```toon
status: error
error: marshal.json not found. Run command /plan-marshall first
```

Standard error conditions:
- `marshal.json not found` - Run `/plan-marshall` first
- `skill_domains not configured` - Run `/plan-marshall` first
- `Unknown domain: {name}` - Domain doesn't exist
- `Unknown module: {name}` - Module doesn't exist
- `Build system not found: {name}` - Build system not configured
