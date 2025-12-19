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
domains[8]:
- system
- plugin-development
- java-core
- java-implementation
- java-testing
- javascript-core
- javascript-implementation
- javascript-testing
count: 8
```

### get

Get full domain configuration.

```bash
plan-marshall-config skill-domains get --domain java-core
```

**Output:**
```toon
status: success
domain: java-core
defaults[1]:
- pm-dev-java:java-core
optionals[3]:
- pm-dev-java:java-null-safety
- pm-dev-java:java-lombok
- pm-dev-java:javadoc
```

### get-defaults

Get default skills for a domain.

```bash
plan-marshall-config skill-domains get-defaults --domain java-core
```

### get-optionals

Get optional skills for a domain.

```bash
plan-marshall-config skill-domains get-optionals --domain java-implementation
```

### set

Update domain configuration.

```bash
plan-marshall-config skill-domains set \
  --domain java-core \
  --defaults "pm-dev-java:java-core,pm-dev-java:java-null-safety" \
  --optionals "pm-dev-java:java-lombok,pm-dev-java:javadoc"
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
  --domain java-core \
  --skill pm-dev-java:java-lombok
```

**Output:**
```toon
status: success
domain: java-core
skill: pm-dev-java:java-lombok
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
  domains: ["java-core", "java-implementation"]
  build_systems: ["maven"]
- name: my-ui
  path: my-ui
  domains: ["java-core", "java-implementation", "javascript-core", "javascript-implementation"]
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
domains[4]:
- java-core
- java-implementation
- javascript-core
- javascript-implementation
```

### get-build-systems

Get available build systems for a module.

```bash
plan-marshall-config modules get-build-systems --module my-ui
```

### get-command

Get build command using static routing.

```bash
plan-marshall-config modules get-command \
  --module my-ui \
  --label test
```

**Output (module command):**
```toon
status: success
module: my-ui
label: test
command: python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "run test"
source: module
```

**Output (default module fallback):**
```toon
status: success
module: my-core
label: verify
command: python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals "clean verify"
source: default
```

### set-command

Set a build command for a module.

```bash
plan-marshall-config modules set-command \
  --module my-ui \
  --label verify \
  --command 'python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "run lint && run test"'
```

**Output:**
```toon
status: success
module: my-ui
label: verify
command: python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "run lint && run test"
```

### add

Add a new module.

```bash
plan-marshall-config modules add \
  --module new-module \
  --path path/to/module \
  --domains "java-core,java-implementation,java-testing" \
  --build-systems "maven"
```

### set

Update module configuration.

```bash
plan-marshall-config modules set \
  --module my-core \
  --domains "java-core,java-implementation,java-testing"
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

Detection reference for available build systems. Commands are stored in modules using static routing.

### list

List configured build systems.

```bash
plan-marshall-config build-systems list
```

**Output:**
```toon
status: success
build_systems[2]:
- system: maven
  skill: plan-marshall:build-operations
- system: npm
  skill: plan-marshall:build-operations
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
skill: plan-marshall:build-operations
```

### add

Add build system to detection reference.

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

**Note:** Build commands are retrieved from modules, not build-systems. Use `modules get-command --module X --label Y`

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
- `marshal.json not found. Run command /marshall-steward first`
- `skill_domains not configured. Run command /marshall-steward first`
- `Unknown domain: {name}`
- `Unknown module: {name}`
- `Build system not found: {name}`
