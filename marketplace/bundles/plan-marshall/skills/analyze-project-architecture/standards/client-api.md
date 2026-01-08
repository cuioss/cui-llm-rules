# Architecture Client API

Script API for accessing architectural data. Output in TOON format.

## Script Pattern

Following `{noun}.py {verb}` convention:

```
architecture.py {verb} [options]
```

**Invocation**:
```bash
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture {verb} [options]
```

## Commands

### info

Get project summary with metadata, technologies, and module overview.

```bash
architecture.py info
```

**Output** (TOON):
```toon
project:
  name: oauth-sheriff
  description: JWT validation library for Quarkus
  root: /path/to/oauth-sheriff

technologies[2]:
  - maven
  - java

modules[4]{name,path,purpose}:
oauth-sheriff-parent,.,parent
oauth-sheriff-core,oauth-sheriff-core,library
oauth-sheriff-quarkus,oauth-sheriff-quarkus,extension
oauth-sheriff-quarkus-deployment,oauth-sheriff-quarkus-deployment,deployment
```

---

### modules

List available module names. Always includes "default" (project root).

```bash
architecture.py modules
```

**Output** (TOON):
```toon
modules[4]:
  - default
  - oauth-sheriff-core
  - oauth-sheriff-quarkus
  - oauth-sheriff-quarkus-deployment
```

---

### module

Get complete module information including description, paths, and commands.

```bash
architecture.py module [--name NAME]
```

**Options**:
| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--name` | No | default | Module name |

**Output** (TOON):
```toon
module:
  name: oauth-sheriff-core
  description: Core JWT validation logic
  path: oauth-sheriff-core

paths:
  sources[1]:
    - src/main/java
  tests[1]:
    - src/test/java
  descriptor: pom.xml

commands[3]:
  - module-tests
  - verify
  - quality-gate
```

---

### commands

Get available commands for a module.

```bash
architecture.py commands [--name NAME]
```

**Options**:
| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--name` | No | default | Module name |

**Output** (TOON):
```toon
module: oauth-sheriff-core

commands[5]{name,description}:
module-tests,Run unit tests for this module
verify,Full verification (compile + test + package)
quality-gate,Run static analysis and linting
clean,Clean build artifacts
install,Install to local repository
```

---

### resolve

Resolve a command to its executable form.

```bash
architecture.py resolve --command COMMAND [--name NAME]
```

**Options**:
| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--command` | Yes | - | Command name to resolve |
| `--name` | No | default | Module name |

**Output** (TOON):
```toon
module: oauth-sheriff-core
command: module-tests
executable: python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --module oauth-sheriff-core --targets test
```

**Hybrid module example** (both Maven and npm):
```toon
module: nifi-cuioss-ui
command: module-tests

executables[2]{build_system,command}:
maven,python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --module nifi-cuioss-ui --targets test
npm,python3 .plan/execute-script.py pm-dev-frontend:plan-marshall-plugin:npm run --package nifi-cuioss-ui --targets test
```

---

## Command Summary

| Command | Purpose | Output |
|---------|---------|--------|
| `info` | Project overview | Project metadata + module list |
| `modules` | List modules | Module names (always includes default) |
| `module` | Module details | Description, paths, command names |
| `commands` | Module commands | Command names with descriptions |
| `resolve` | Executable command | Full python3 invocation |

## Error Handling

**Module not found**:
```toon
error: Module not found
module: unknown-module
available[4]:
  - default
  - oauth-sheriff-core
  - oauth-sheriff-quarkus
  - oauth-sheriff-quarkus-deployment
```

**Command not found**:
```toon
error: Command not found
module: oauth-sheriff-core
command: unknown-command
available[5]:
  - module-tests
  - verify
  - quality-gate
  - clean
  - install
```

## Data Source

All commands read from persisted architecture data:
- `.plan/raw-project-data.json` - Module discovery output
- `.plan/project-structure.json` - Enriched structure (if available)

If no data exists, commands return error with instructions to run discovery first.
