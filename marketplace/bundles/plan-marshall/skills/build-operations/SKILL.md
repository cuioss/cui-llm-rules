---
name: build-operations
description: Central build system detection and extension discovery for modular build operations
allowed-tools: Read, Bash
---

# Build Operations Skill

Central build system detection with **extension-based architecture** - domain bundles provide build-system-specific scripts via `extension.py`.

## What This Skill Provides

- Build system detection from project structure
- Module discovery across multi-module projects
- Extension discovery (finds applicable domain bundles)
- Skill profile auto-detection
- Command generation in marshal.json

**Note**: Actual build execution is provided by domain bundles (`pm-dev-java:build-operations`, `pm-dev-frontend:build-operations`).

## When to Activate This Skill

Activate when:
- Detecting build systems from project structure
- Discovering project modules
- Generating module commands for marshal.json
- Detecting applicable skill profiles (java, javascript, documentation, requirements)

---

## Architecture

**Extension Discovery Pattern**: Domain bundles register via `extension.py` in their `plan-marshall-plugin` skill.

```
build_env.py                        Domain Bundle Extensions
   │                                    │
   ├── detect ─────► Find build files   │
   │                                    │
   ├── persist ────► discover_extensions() ─────► pm-dev-java/skills/plan-marshall-plugin/extension.py
   │                     │                            ├── is_applicable(project_root) → True
   │                     │                            ├── provides_build_systems() → ["maven", "gradle"]
   │                     │                            ├── get_command_mappings() → {"module-tests": "..."}
   │                     │                            └── get_skill_domains() → {"domain": "java", ...}
   │                     │
   │                     └─────────────► pm-dev-frontend/skills/plan-marshall-plugin/extension.py
   │                                         ├── is_applicable(project_root) → True
   │                                         └── provides_build_systems() → ["npm"]
   │
   └── marshal.json ─────► modules.default.commands
                               ├── module-tests → "pm-dev-java:build-operations:maven run ..."
                               └── quality-gate → "pm-dev-java:build-operations:maven run ..."
```

**Load Reference**: For full architecture details:
```
Read standards/architecture.md
```

---

## Skill Structure

```
build-operations/
├── SKILL.md                     # This file
├── standards/
│   ├── architecture.md          # Extension discovery, skill boundaries
│   ├── api-contract.md          # Shared TOON output formats
│   └── canonical-vocabulary.md  # Canonical command names for lookup API
└── scripts/
    └── build_env.py             # Detection, extension discovery, persist
```

**Domain Bundle Scripts** (provided by extensions):
- `pm-dev-java:build-operations` - Maven and Gradle operations
- `pm-dev-frontend:build-operations` - npm operations

---

## Scripts

| Script | Notation | Purpose |
|--------|----------|---------|
| build_env | `plan-marshall:build-operations:build_env` | Build system detection, extension discovery, persist |

**Execution scripts** are in domain bundles:

| Script | Notation | Purpose |
|--------|----------|---------|
| maven | `pm-dev-java:build-operations:maven` | Maven run, execute, parse |
| gradle | `pm-dev-java:build-operations:gradle` | Gradle run, execute, parse |
| npm | `pm-dev-frontend:build-operations:npm` | npm run, execute, parse |

---

## Workflow: Detect Build Systems

**Pattern**: Command Chain Execution

Detect available build systems in the project.

### Step 1: Run Detection

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect
```

### Step 2: Process Result

```toon
status: success
default_system: maven
available_systems: maven,npm

detected[2]{name,priority,technology,detected_by}:
maven	1	java	pom.xml
npm	3	javascript	package.json
```

---

## Workflow: Detect Modules

**Pattern**: Command Chain Execution

Detect project modules and their build systems.

### Step 1: Run Detection

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-modules
```

### Step 2: Process Result

```toon
status: success
module_count: 3

modules[3]{name,path,build_systems,domains}:
default	.	maven	java
oauth-sheriff-core	oauth-sheriff-core	maven	java
oauth-sheriff-ui	oauth-sheriff-ui	npm	javascript
```

---

## Workflow: Persist Build Configuration

**Pattern**: Command Chain Execution

Detect build systems, modules, generate commands, and persist to marshal.json.

### Step 1: Run Persist

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist
```

### Step 2: Process Result

```toon
status: success
persisted_to: marshal.json
build_systems: maven,npm
modules_updated: 3
commands_generated: 15

modules[3]{name,path,type,commands_count}:
default	.	jar	8
oauth-sheriff-core	oauth-sheriff-core	jar	8
oauth-sheriff-ui	oauth-sheriff-ui	npm	5
```

This generates `modules.{name}.commands` entries in marshal.json using **canonical command names**:

```json
{
  "modules": {
    "default": {
      "path": ".",
      "type": "jar",
      "build_systems": ["maven"],
      "commands": {
        "module-tests": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\"",
        "quality-gate": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\"",
        "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\""
      }
    }
  }
}
```

### Hybrid Module Format

For modules with multiple build systems (e.g., Maven + npm), commands are nested by build system:

```json
{
  "modules": {
    "hybrid-module": {
      "path": "hybrid-module",
      "type": "jar",
      "build_systems": ["maven", "npm"],
      "commands": {
        "module-tests": {
          "maven": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\"",
          "npm": "python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command \"run test\""
        },
        "quality-gate": {
          "maven": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify -Ppre-commit\"",
          "npm": "python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command \"run lint && npm run format:check\""
        }
      }
    }
  }
}
```

---

## Workflow: Execute Build

**Pattern**: Config-Driven Execution via Domain Bundles

Execute a build using the `run` subcommand from domain bundles.

### Recommended: Use `run` Subcommand

The `run` subcommand combines execute + parse, using actionable mode by default:

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven run \
    --targets "clean test" \
    --module oauth-sheriff-core
```

### Output (TOON format)

```toon
status: success
exit_code: 0
duration_seconds: 45.2
log_file: target/build-20250115-103045.log
command_executed: ./mvnw clean test -pl oauth-sheriff-core
```

On failure, parsed errors are included automatically:

```toon
status: error
exit_code: 1
duration_seconds: 23.1
log_file: target/build-20250115-103045.log

issues[2]{type,file,line,message}:
compilation_error	src/Main.java	45	cannot find symbol
test_failure	src/test/MainTest.java	23	expected true but was false
```

### Mode Options

| Mode | Description |
|------|-------------|
| `actionable` (default) | Filters out accepted warnings, shows only fixable issues |
| `errors` | Only errors, no warnings |
| `structured` | All issues with `[accepted]` markers |

---

## Workflow: Parse Build Output (Standalone)

Domain bundles provide separate `parse` subcommand for analyzing existing log files:

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven parse \
    --log target/build-20250115-103045.log \
    --mode structured
```

See `pm-dev-java:build-operations` SKILL.md for full details.

---

## Workflow: Detect Module Type

**Pattern**: Simple Query

Detect the module type (pom, jar, war, quarkus, npm) from build files.

### Step 1: Execute

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-module-type \
    --module "oauth-sheriff-core"
```

### Step 2: Process Result

```toon
status: success
module: oauth-sheriff-core
build_system: maven
type: jar
```

Possible types:
- `pom` - Parent/BOM module
- `jar` - Library module (default)
- `war` - Web application
- `quarkus` - Quarkus application
- `npm` - npm project

---

## Workflow: Detect Profiles

**Pattern**: Simple Query

Detect Maven/Gradle profiles and classify them to canonical command names.

### Step 1: Execute

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-profiles \
    --module "default"
```

### Step 2: Process Result

```toon
status: success
module: default
path: /path/to/project
count: 3

profiles[3]{id,canonical,activation_type}:
integration-tests	integration-tests	command-line
coverage	coverage	command-line
benchmark	performance	command-line
```

Profile activation types:
- `command-line` - Activated via `-P` flag
- `property` - Activated via `-D` property
- `jdk` - Activated by JDK version
- `os` - Activated by operating system
- `default` - Always active

---

## Workflow: Lookup Canonical Command

**Pattern**: Simple Query

Look up a canonical command for a module. Returns the full executable command string.

### Step 1: Execute

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env lookup \
    --canonical "module-tests" --module "oauth-sheriff-core"
```

### Step 2: Process Result

Returns plain text (for shell capture):
```
python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals "clean test" --module oauth-sheriff-core
```

For hybrid modules (multiple build systems), specify `--build-system`:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env lookup \
    --canonical "module-tests" --module "default" --build-system "maven"
```

---

## Workflow: Get Available Commands

**Pattern**: Simple Query

List all canonical commands configured for a module.

### Step 1: Execute

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env get-available-commands \
    --module "oauth-sheriff-core"
```

### Step 2: Process Result

```toon
status: success
module: oauth-sheriff-core
count: 3

commands[3]{name}:
module-tests
verify
quality-gate
```

---

## Workflow: Validate Required Commands

**Pattern**: Validation Pipeline

Validate that all required commands are configured for a module type.

### Step 1: Execute

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env validate-required \
    --module "oauth-sheriff-core"
```

### Step 2: Process Result

Success (all required present):
```toon
status: success
module: oauth-sheriff-core
module_type: jar
message: All required commands are configured
```

Incomplete (missing required):
```toon
status: incomplete
module: oauth-sheriff-core
module_type: jar
missing_count: 1

missing[1]{name,description}:
quality-gate	Static analysis, linting, formatting checks
```

---

## Storage Pattern

**Split storage** (shared vs local):

| File | Content | Shared |
|------|---------|--------|
| `.plan/marshal.json` | `modules.{name}.commands`, `build_systems[]` | Yes (git) |
| `.plan/run-configuration.json` | `build.available_systems`, command timeouts | No (local) |

---

## Error Handling

All operations return TOON error format on failure:

```toon
status: error
operation: execute
error: Build failed with exit code 1
context: Compilation errors found
```

Exit codes:
- `0`: Success (stdout)
- `1`: Error (stderr)

---

## Canonical Command Names

Commands use **canonical names** for programmatic lookup. See `standards/canonical-vocabulary.md` for full specification.

| Canonical Name | Phase | Maven Goals | Gradle Tasks | npm Scripts |
|----------------|-------|-------------|--------------|-------------|
| `compile` | build | `compile` | `compileJava` | - |
| `test-compile` | build | `test-compile` | `testClasses` | - |
| `module-tests` | test | `clean test` | `clean test` | `run test` |
| `integration-tests` | test | `clean verify -Pintegration-tests` | `clean integrationTest` | `run test:e2e` |
| `coverage` | test | `clean verify -Pcoverage` | `clean test jacocoTestReport` | `run test:coverage` |
| `performance` | test | `clean verify -Pbenchmark` | `clean jmh` | `run test:perf` |
| `quality-gate` | quality | `clean verify -Ppre-commit` | `clean check` | `run lint && npm run format:check` |
| `verify` | verify | `clean verify` | `clean build` | `run test && npm run lint` |
| `install` | deploy | `clean install` | `clean publishToMavenLocal` | - |
| `package` | deploy | `package` | `clean assemble` | `run build` |

**Required commands** (must be configured for testable modules): `module-tests`, `quality-gate`, `verify`

**Module type filtering**: Commands are filtered by module type (e.g., `pom` modules only get `install` and `quality-gate`).

---

## Extension API

Domain bundles register with the central build_env.py via `extension.py`:

```python
# marketplace/bundles/{bundle}/skills/plan-marshall-plugin/extension.py

def is_applicable(project_root: str) -> bool:
    """Return True if this bundle applies to the project."""

def provides_build_systems() -> list:
    """Return list of build system keys (e.g., ['maven', 'gradle'])."""

def get_command_mappings() -> dict:
    """Return command templates with placeholders."""

def get_skill_domains() -> dict:
    """Return domain metadata for skill loading."""
```

**Available Extensions**:
- `pm-dev-java` - Maven, Gradle detection and commands
- `pm-dev-frontend` - npm detection and commands
- `pm-documents` - doc/ directory detection (no build commands)
- `pm-requirements` - Requirements.adoc detection (no build commands)

---

## Integration

### With marshall-steward

- Steward wizard calls `build_env persist` to generate commands
- persist discovers extensions and generates domain-specific commands
- Steward does NOT contain build detection logic

### With run-config

- Domain bundles use `run_config` for warning filtering
- Warning API: `warning add/list/remove` in run-config
- Warning patterns filter actionable output in `run` subcommand

### With Domain Bundles

- `pm-dev-java:build-operations` provides Maven and Gradle scripts
- `pm-dev-frontend:build-operations` provides npm scripts
- Domain scripts use unified TOON output format

---

## References

- `standards/architecture.md` - Extension discovery and skill boundaries
- `standards/api-contract.md` - Shared TOON output formats
- `standards/canonical-vocabulary.md` - Canonical command names for lookup API
- `pm-dev-java:build-operations` - Maven and Gradle implementation details
- `pm-dev-frontend:build-operations` - npm implementation details
