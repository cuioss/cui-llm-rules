---
name: build-operations
description: Build system abstraction with unified API for Maven, Gradle, and npm operations
allowed-tools: Read, Bash
---

# Build Operations Skill

Unified build system abstraction using **static routing** - one script per build system, config stores full commands.

## What This Skill Provides

- Build system and module detection
- Build execution with timeout management
- Output parsing and issue categorization
- OpenRewrite marker handling
- Warning classification
- Unified TOON output format across build systems

## When to Activate This Skill

Activate when:
- Detecting build systems from project structure
- Executing build commands (compile, test, verify)
- Parsing build output for errors and warnings
- Generating module commands for marshal.json
- Finding module paths

---

## Architecture

**Static Routing Pattern**: Config stores full commands, wizard generates build-system-specific paths.

```
marshal.json                          Scripts
modules.default.commands.test ─────► maven.py execute
modules.core.commands.verify ─────► maven.py execute
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
│   ├── architecture.md          # Static routing, skill boundaries
│   ├── api-contract.md          # Shared TOON output formats
│   ├── maven-impl.md            # Maven-specific: execution, parsing
│   ├── gradle-impl.md           # Gradle-specific: execution, parsing
│   ├── npm-impl.md              # npm-specific: execution
│   └── pom-maintenance.md       # POM file operations
└── scripts/
    ├── build_env.py             # Detection, module discovery, persist
    ├── maven.py                 # Maven operations
    ├── gradle.py                # Gradle operations
    └── npm.py                   # npm operations
```

---

## Scripts

| Script | Notation | Purpose |
|--------|----------|---------|
| build_env | `plan-marshall:build-operations:build_env` | Build system & module detection |
| maven | `plan-marshall:build-operations:maven` | Maven operations |
| gradle | `plan-marshall:build-operations:gradle` | Gradle operations |
| npm | `plan-marshall:build-operations:npm` | npm operations |

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

modules[3]{name,path,commands_count}:
default	.	5
oauth-sheriff-core	oauth-sheriff-core	5
oauth-sheriff-ui	oauth-sheriff-ui	5
```

This generates `modules.{name}.commands` entries in marshal.json:

```json
{
  "modules": {
    "default": {
      "path": ".",
      "commands": {
        "test-compile": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"test-compile\"",
        "test": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\""
      }
    }
  }
}
```

---

## Workflow: Execute Build

**Pattern**: Config-Driven Execution

Execute a build using config-stored command.

### Step 1: Resolve Command from Config

```bash
COMMAND=$(jq -r '.modules["default"].commands.test' .plan/marshal.json)
```

### Step 2: Execute with Timeout

```bash
# Get adaptive timeout
TIMEOUT=$(python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout get \
    --command "build:default:test" --default 300)

# Execute with timing
START=$(date +%s)
timeout ${TIMEOUT}s eval "$COMMAND"
EXIT_CODE=$?
END=$(date +%s)
DURATION=$((END - START))

# Update timeout on success
if [ $EXIT_CODE -eq 0 ]; then
    python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout set \
        --command "build:default:test" --duration $DURATION
fi
```

### Alternative: Direct Script Invocation

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven execute \
    --goals "clean test" \
    --module oauth-sheriff-core \
    --profile coverage
```

### Step 3: Process Result

```toon
status: success
operation: execute
exit_code: 0
duration_ms: 45230
log_file: .plan/temp/build-20250115-103045.log
command_executed: ./mvnw clean test -pl oauth-sheriff-core
```

---

## Workflow: Parse Build Output

**Pattern**: Command Chain Execution

Parse build output and categorize issues.

### Step 1: Parse Log File

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven parse \
    --log .plan/temp/build-20250115-103045.log \
    --mode structured
```

### Step 2: Process Result

```toon
status: success
build_status: FAILURE
total_issues: 3

issues[3]{type,file,line,message}:
compilation_error	src/Main.java	45	cannot find symbol
test_failure	src/test/MainTest.java	23	expected true but was false
javadoc_warning	src/Utils.java	12	missing @param tag
```

---

## Workflow: Find Module Path

**Pattern**: Simple Query

Find Maven module path from artifactId.

### Step 1: Execute

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven find-module \
    --artifact-id oauth-sheriff-core
```

### Step 2: Process Result

```toon
status: success
artifact_id: oauth-sheriff-core
module_path: oauth-sheriff-core
pom_file: oauth-sheriff-core/pom.xml
maven_pl_argument: -pl oauth-sheriff-core
```

---

## Workflow: Check Acceptable Warnings

**Pattern**: Command Chain Execution

Categorize warnings against acceptable patterns.

### Step 1: Execute

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven check-warnings \
    --warnings '{"issues": [...]}' \
    --acceptable-warnings '{"patterns": [...]}'
```

### Step 2: Process Result

```toon
status: success
total: 15
acceptable: 3
fixable: 10
unknown: 2
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

## Standard Command Labels

| Label | Maven Goals | Gradle Tasks | npm Scripts |
|-------|-------------|--------------|-------------|
| `test-compile` | `test-compile` | `testClasses` | - |
| `test` | `clean test` | `clean test` | `run test` |
| `verify` | `clean verify` | `clean check` | `run test && run lint` |
| `install` | `clean install` | `publishToMavenLocal` | - |
| `pre-commit` | `clean install -Ppre-commit` | `preCommit` | - |
| `coverage` | `clean verify -Pcoverage` | `jacocoTestReport` | `run test:coverage` |

---

## Integration

### With marshall-steward

- Steward wizard calls `build_env persist` to generate commands (Step 4)
- Steward does NOT contain build detection logic

### With run-config

- Build operations use `run_config timeout get/set` for adaptive timeouts
- Command key format: `build:{module}:{label}`

### With plan-marshall-config

- Modules section managed via `modules get-command`, `modules set-command`
- Fallback to `build_systems[]` for backward compatibility

---

## References

- `standards/architecture.md` - Static routing and skill boundaries
- `standards/api-contract.md` - Shared TOON output formats
- `standards/maven-impl.md` - Maven-specific implementation
- `standards/gradle-impl.md` - Gradle-specific implementation
- `standards/npm-impl.md` - npm-specific implementation
- `standards/pom-maintenance.md` - POM file operations
