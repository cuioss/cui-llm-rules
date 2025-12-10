---
name: manage-config
description: Manage plan and project configuration with schema validation
allowed-tools: Read, Glob, Bash
---

# Manage Config Skill

Configuration management at two levels:
1. **Per-plan** (`config.toon`) - Plan-specific settings
2. **Project-level** (`marshal.json`) - Domain agents, plan-type routing, defaults

## What This Skill Provides

- Per-plan config.toon management with schema validation
- Project-level marshal.json for domain agent routing
- Field-level get/set operations
- Plan-type routing rules and keyword detection

## When to Activate This Skill

Activate this skill when:
- Creating initial plan configuration
- Reading or updating plan settings
- Configuring domain agent mappings
- Setting up plan-type routing rules

---

## Storage Location

Configuration is stored in the plan directory:

```
.plan/plans/{plan_id}/config.toon
```

---

## File Format

TOON format with typed fields:

```toon
# Plan Configuration

plan_type: pm-workflow:plan-type-java
compatibility: deprecations
commit_strategy: phase-specific

# Finalize Configuration (added by plan-type configure)
create_pr: true
verification_required: true
verification_command: /builder-build-and-fix
branch_strategy: feature
```

### Base Schema Fields (set during plan creation)

| Field | Values | Description |
|-------|--------|-------------|
| `plan_type` | bundle:skill notation (e.g., pm-workflow:plan-type-java) | Type of plan workflow (extension point) |
| `compatibility` | deprecations, breaking | Compatibility strategy (user choice) |
| `commit_strategy` | fine-granular, phase-specific, complete | Git commit granularity (user choice) |

### Finalize Configuration Fields (added by plan-type configure)

| Field | Values | Description |
|-------|--------|-------------|
| `create_pr` | true, false | Whether to create a pull request |
| `verification_required` | true, false | Whether verification must pass before finalize |
| `verification_command` | command string or null | Command to run for verification |
| `branch_strategy` | feature, direct | Feature branch or direct-to-main |

---

## Operations

Script: `pm-workflow:manage-config:manage-config`

### read

Read entire config.toon content.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

config:
  plan_type: pm-workflow:plan-type-java
  compatibility: deprecations
  commit_strategy: phase-specific
```

### get

Get a specific field value.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} \
  --field plan_type
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: plan_type
value: pm-workflow:plan-type-java
```

### set

Set a specific field value.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set \
  --plan-id {plan_id} \
  --field compatibility \
  --value breaking
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: compatibility
value: breaking
previous: deprecations
```

### get-multi

Get multiple fields in one call.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get-multi \
  --plan-id {plan_id} \
  --fields "plan_type,compatibility,commit_strategy"
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
plan_type: pm-workflow:plan-type-java
compatibility: deprecations
commit_strategy: phase-specific
```

### create

Create config.toon with initial values.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config create \
  --plan-id {plan_id} \
  --plan-type pm-workflow:plan-type-java \
  [--compatibility deprecations] \
  [--commit-strategy phase-specific] \
  [--force]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: config.toon
created: true

config:
  plan_type: pm-workflow:plan-type-java
  compatibility: deprecations
  commit_strategy: phase-specific
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `pm-workflow:manage-config:manage-config` | Per-plan config.toon operations | `python3 .plan/execute-script.py pm-workflow:manage-config:manage-config {subcommand} --help` |
| `pm-workflow:manage-config:marshal-config` | Project-level marshal.json operations | `python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config {noun} {verb} --help` |

---

## Validation Rules

| Field | Valid Values |
|-------|--------------|
| plan_type | bundle:skill notation (e.g., pm-workflow:plan-type-java) |
| compatibility | deprecations, breaking |
| commit_strategy | fine-granular, phase-specific, complete |
| create_pr | true, false |
| verification_required | true, false |
| verification_command | any string or null |
| branch_strategy | feature, direct |

---

## Error Handling

```toon
status: error
plan_id: my-feature
field: plan_type
error: invalid_value
message: Invalid plan_type format: unknown. Must be bundle:skill notation (e.g., pm-workflow:plan-type-java)
```

---

## Integration Points

### With plan-init

Plan initialization creates config.toon with base user-selected values (`plan_type`, `compatibility`, `commit_strategy`).

### With plan-type configure

After base config is created, plan-type skills add finalize configuration fields (`create_pr`, `verification_required`, `verification_command`, `branch_strategy`).

### With plan-execute

Execution phase reads config to determine build commands, commit strategy, and finalize behavior.

---

# Marshal Config (Project-Level)

Project-level configuration for **optional overrides** of domain agent routing and plan-type detection.

## Storage Location

```
.plan/marshal.json
```

## Purpose

Provides project-specific overrides for domain agent routing. Default routing uses plan-type skill frontmatter (`domain:` section); marshal.json is only needed for custom agent mappings.

**Primary routing source**: Plan-type skill `domain:` frontmatter (see `pm-workflow:plan-type-api`)
**Override mechanism**: marshal.json `domain_agents` section

## Noun-Verb Operations

Script: `pm-workflow:manage-config:marshal-config`

### domain-agents

Manage domain agent mappings per plan-type.

```bash
# Get agents for plan-type
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  domain-agents get --plan-type pm-workflow:plan-type-java

# Set agents
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  domain-agents set --plan-type pm-workflow:plan-type-java \
  --solution-outline-agent pm-dev-java:java-solution-outline-agent \
  --task-plan-agent pm-dev-java:java-task-plan-agent

# List all
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  domain-agents list
```

### defaults

Manage default configuration values.

```bash
# Get field
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  defaults get --field verification_required

# Set field
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  defaults set --field create_pr --value true

# List all
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  defaults list
```

### rules

Manage file pattern → plan-type routing rules.

```bash
# Match file to plan-type
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  rules match --file src/main/java/Foo.java

# Add rule
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  rules add --pattern "*.kt" --plan-type pm-workflow:plan-type-java \
  --description "Kotlin files"

# Remove rule
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  rules remove --pattern "*.kt"

# List rules
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  rules list
```

### keywords

Manage keyword-based plan-type detection.

```bash
# Match text to plan-type
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  keywords match --text "implement junit test for service"

# List all keywords (or filter by plan-type)
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  keywords list [--plan-type pm-workflow:plan-type-java]

# Add keyword
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  keywords add --plan-type pm-workflow:plan-type-java --keyword quarkus
```

### plan-type-defaults

Manage per-plan-type default settings.

```bash
# Get defaults for plan-type
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  plan-type-defaults get --plan-type pm-workflow:plan-type-java

# Set defaults for plan-type
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  plan-type-defaults set --plan-type pm-workflow:plan-type-java \
  --verification-command "/builder-build-and-fix" \
  --pr-workflow true
```

### build-systems

Manage build system configuration.

```bash
# List detected build systems
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  build-systems list

# Enable/disable a build system
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  build-systems set --system maven --active true

# Auto-detect build systems from project files
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  build-systems detect
```

### custom-types

Manage custom plan types.

```bash
# List custom types
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  custom-types list

# Add custom type
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  custom-types add --name my-custom-type --skill-path ./skills/my-type/SKILL.md \
  --solution-outline-agent my-bundle:my-solution-outline-agent \
  --task-plan-agent my-bundle:my-task-plan-agent

# Remove custom type
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  custom-types remove --name my-custom-type
```

### state

Manage generation state for marshal.json.

```bash
# Get current state
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  state get

# Set state field
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  state set --field last_run --value "2025-01-15"

# Update checksum
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config \
  state update-checksum
```

### init

Initialize marshal.json with defaults.

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config init
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config init --force
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config init --template java-project
```

## Output Format

All marshal-config commands return TOON for token efficiency:

```toon
status: success
data:
  solution_outline_agent: pm-dev-java:java-solution-outline-agent
  task_plan_agent: pm-dev-java:java-task-plan-agent
```

## Integration Points

### Per-Plan Config (manage-config)

| Consumer | Operation | Purpose |
|----------|-----------|---------|
| plan-init-agent | `create` | Create initial config.toon |
| plan-type configure | `set` | Add finalize configuration fields |
| plan-execute | `read`, `get` | Read commit strategy, verification settings |
| plan-finalize | `get` | Check create_pr, branch_strategy |

### Project-Level Config (marshal-config)

| Consumer | Operation | Purpose |
|----------|-----------|---------|
| /plan-manage | `domain-agents get` | Check for project-level agent override |
| /plan-manage | `rules match` | Auto-detect plan-type from file patterns |
| /plan-manage | `keywords match` | Detect plan-type from description text |
| /plan-marshall | `init` | First-run project setup |
| /plan-marshall | `build-systems detect` | Auto-detect project build systems |
| plan-init | `defaults list` | Set plan config defaults |
| plan-finalize | `plan-type-defaults get` | Get verification command |

**Note**: `/plan-manage` checks marshal-config for overrides, then falls back to plan-type skill frontmatter for default agent routing.
