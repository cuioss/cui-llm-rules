# API Reference

Complete noun-verb API for plan-marshall-config.

## Execution Pattern

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  {noun} {verb} [--param value]
```

## Noun: skill-domains

Manage implementation skill defaults and optionals per domain.

### list

List all configured domains.

```bash
plan-marshall-config skill-domains list
```

**Output:**
```toon
status: success
domains[4]:
- java
- java-testing
- javascript
- javascript-testing
count: 4
```

### get

Get full domain configuration.

```bash
plan-marshall-config skill-domains get --domain java
```

**Output:**
```toon
status: success
domain: java
defaults[1]:
- pm-dev-java:cui-java-core
optionals[1]:
- pm-dev-java:cui-java-cdi
```

### get-defaults

Get default skills for a domain.

```bash
plan-marshall-config skill-domains get-defaults --domain java
```

### get-optionals

Get optional skills for a domain.

```bash
plan-marshall-config skill-domains get-optionals --domain java
```

### set

Update domain configuration.

```bash
plan-marshall-config skill-domains set \
  --domain java \
  --defaults "pm-dev-java:cui-java-core,pm-dev-java:cui-javadoc" \
  --optionals "pm-dev-java:cui-java-cdi"
```

### add

Add a new domain.

```bash
plan-marshall-config skill-domains add \
  --domain python \
  --defaults "pm-dev-python:cui-python-core"
```

### validate

Check if a skill is valid for a domain.

```bash
plan-marshall-config skill-domains validate \
  --domain java \
  --skill pm-dev-java:cui-java-cdi
```

**Output:**
```toon
status: success
domain: java
skill: pm-dev-java:cui-java-cdi
valid: true
in_defaults: false
in_optionals: true
```

---

## Noun: modules

Manage project modules with domain and build system mappings.

### list

List all modules.

```bash
plan-marshall-config modules list
```

**Output:**
```toon
status: success
modules[2]:
- name: my-core
  path: my-core
  domains: ["java"]
  build_systems: ["maven"]
- name: my-ui
  path: my-ui
  domains: ["java", "javascript"]
  build_systems: ["maven", "npm"]
count: 2
```

### get

Get full module configuration.

```bash
plan-marshall-config modules get --module my-ui
```

### get-domains

Get skill domains for a module.

```bash
plan-marshall-config modules get-domains --module my-ui
```

**Output:**
```toon
status: success
module: my-ui
domains[2]:
- java
- javascript
```

### get-build-systems

Get available build systems for a module.

```bash
plan-marshall-config modules get-build-systems --module my-ui
```

### get-command

Get build command with override resolution.

```bash
plan-marshall-config modules get-command \
  --module my-ui \
  --system npm \
  --label test
```

**Output (module override):**
```toon
status: success
module: my-ui
system: npm
label: test
command: custom:test
source: module_override
```

**Output (project level fallback):**
```toon
status: success
module: my-core
system: maven
label: verify
command: clean verify
source: project_level
```

### add

Add a new module.

```bash
plan-marshall-config modules add \
  --module new-module \
  --path path/to/module \
  --domains "java,java-testing" \
  --build-systems "maven"
```

### set

Update module configuration.

```bash
plan-marshall-config modules set \
  --module my-core \
  --domains "java,java-testing"
```

### remove

Remove a module.

```bash
plan-marshall-config modules remove --module old-module
```

### detect

Auto-detect modules from project files.

```bash
plan-marshall-config modules detect
```

**Output:**
```toon
status: success
detected[3]:
- my-core
- my-ui
- my-tests
count: 3
total_modules: 3
```

---

## Noun: build-systems

Manage build system configuration.

### list

List configured build systems.

```bash
plan-marshall-config build-systems list
```

### get

Get build system configuration.

```bash
plan-marshall-config build-systems get --system maven
```

**Output:**
```toon
status: success
system: maven
skill: pm-dev-builder:builder-maven-rules
commands:
  compile: compile
  test: clean test
  verify: clean verify
```

### get-command

Get command for a label.

```bash
plan-marshall-config build-systems get-command \
  --system maven \
  --label verify
```

**Output:**
```toon
status: success
system: maven
label: verify
command: clean verify
skill: pm-dev-builder:builder-maven-rules
```

### add

Add build system with default commands.

```bash
plan-marshall-config build-systems add --system gradle
```

### remove

Remove a build system.

```bash
plan-marshall-config build-systems remove --system gradle
```

### detect

Auto-detect build systems from project.

```bash
plan-marshall-config build-systems detect
```

---

## Noun: system

Manage system-level settings.

### retention get

Get all retention settings.

```bash
plan-marshall-config system retention get
```

**Output:**
```toon
status: success
retention:
  logs_days: 1
  archived_plans_days: 5
  memory_days: 5
  temp_on_maintenance: true
```

### retention set

Set a retention field.

```bash
plan-marshall-config system retention set \
  --field logs_days \
  --value 7
```

---

## Noun: plan

Manage plan-related configuration.

### defaults list

List all plan defaults.

```bash
plan-marshall-config plan defaults list
```

**Output:**
```toon
status: success
defaults:
  compatibility: deprecations
  commit_strategy: phase-specific
  create_pr: false
  verification_required: true
  branch_strategy: direct
```

### defaults get

Get a specific default value.

```bash
plan-marshall-config plan defaults get --field commit_strategy
```

### defaults set

Set a default value.

```bash
plan-marshall-config plan defaults set \
  --field create_pr \
  --value true
```

---

## init

Initialize marshal.json.

```bash
plan-marshall-config init [--force]
```

**Output:**
```toon
status: success
created: .plan/marshal.json
build_systems_detected: 2
```

## Error Responses

All errors follow this pattern:

```toon
status: error
error: {message}
```

Common errors:
- `marshal.json not found. Run command /plan-marshall first`
- `skill_domains not configured. Run command /plan-marshall first`
- `Unknown domain: {name}`
- `Unknown module: {name}`
- `Build system not found: {name}`
