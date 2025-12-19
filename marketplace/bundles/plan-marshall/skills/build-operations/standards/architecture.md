# Build Operations Architecture

Architecture for unified build operations using static routing pattern.

---

## Design Decision: Unified Static Routing

**All domains use static routing** - config stores full commands, wizard generates build-system-specific paths.

| Domain | Config Example |
|--------|----------------|
| **Build** | `"test": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"test\""` |
| **CI** | `"pr-create": "python3 .plan/execute-script.py plan-marshall:ci-operations:github pr create"` |

**Benefits**:
- Single mental model across all domains
- Config shows exactly what runs
- Maximum transparency
- Full command customization possible
- No runtime routing logic needed

---

## Skill Boundaries

### build-operations Skill Owns

| Responsibility | Description |
|----------------|-------------|
| Build system abstraction | Unified API across Maven/Gradle/npm |
| Build execution | Execute builds with log capture |
| Output parsing | Extract errors, warnings, test failures |
| Module detection | Detect project modules |
| Command generation | Generate full command strings for config |

### build-operations Skill Does NOT Own

| Responsibility | Owner |
|----------------|-------|
| Menu presentation | marshall-steward |
| User interaction | marshall-steward |
| Configuration storage | plan-marshall-config |
| Timeout management | run-config |
| CI operations | ci-operations |

---

## Static Routing Architecture

```
                    UNIFIED STATIC ROUTING

    +-----------------------------------------------------------------+
    |                      marshal.json                               |
    |  +-----------------------------------------------------------+  |
    |  |  "modules": {                                             |  |
    |  |    "default": {                                           |  |
    |  |      "path": ".",                                         |  |
    |  |      "commands": {                                        |  |
    |  |        "test": "...build-operations:maven execute ...",   |  |
    |  |        "verify": "...build-operations:maven execute ..."  |  |
    |  |      }                                                    |  |
    |  |    }                                                      |  |
    |  |  }                                                        |  |
    |  +-----------------------------------------------------------+  |
    +-----------------------------------------------------------------+
                              |
                    +---------+---------+
                    |  Config stores    |
                    |  full commands    |
                    +---------+---------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
    +-----------------------------------------------------------------+
    |                     build-operations                            |
    |  +-------------+  +-------------+  +-------------+  +---------+ |
    |  |  build_env  |  |   maven     |  |   gradle    |  |   npm   | |
    |  | (detection) |  | (mvnw/mvn)  |  | (gradlew)   |  |  (npm)  | |
    |  +-------------+  +-------------+  +-------------+  +---------+ |
    +-----------------------------------------------------------------+
```

---

## Scripts Per Build System

| Script | CLI Tool | Purpose |
|--------|----------|---------|
| `build_env.py` | - | Build system detection, module discovery, persist |
| `maven.py` | `./mvnw` or `mvn` | Maven operations |
| `gradle.py` | `./gradlew` or `gradle` | Gradle operations |
| `npm.py` | `npm` | npm operations |

### Why Separate Scripts

| Aspect | Benefit |
|--------|---------|
| **Independence** | Each script handles one build system |
| **Maintainability** | Build-system-specific logic isolated |
| **Testing** | Test each build system independently |
| **No runtime routing** | Config determines which script runs |

---

## Module-Centric Configuration

Configuration is organized around **modules** (what you build), not build systems:

```json
{
  "modules": {
    "default": {
      "path": ".",
      "domains": ["java"],
      "build_systems": ["maven"],
      "commands": {
        "test": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\"",
        "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\""
      }
    },
    "oauth-sheriff-core": {
      "path": "oauth-sheriff-core",
      "domains": ["java"],
      "build_systems": ["maven"],
      "commands": {
        "test": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\" --module oauth-sheriff-core"
      }
    }
  }
}
```

---

## Detection Priority

Build systems are detected by checking for marker files:

| System | Marker Files | Priority | Technology |
|--------|--------------|----------|------------|
| Maven | `pom.xml` | 1 (highest) | java |
| Gradle | `build.gradle`, `build.gradle.kts`, `settings.gradle` | 2 | java |
| npm | `package.json` | 3 | javascript |

Priority determines the default build system when multiple are present.

---

## Module Detection

### Maven Modules

Parse `pom.xml` for `<modules>` section:

```xml
<modules>
    <module>oauth-sheriff-core</module>
    <module>oauth-sheriff-ui</module>
</modules>
```

### Gradle Modules

Parse `settings.gradle` or `settings.gradle.kts` for `include` statements:

```groovy
include 'core'
include 'web-app'
include ':nested:module'
```

### npm Workspaces

Parse `package.json` for `workspaces` array:

```json
{
  "workspaces": ["packages/*", "apps/web"]
}
```

---

## Command Generation

Commands are generated with full executable strings:

```python
def generate_command(build_system: str, label: str, module: str | None) -> str:
    base = f"python3 .plan/execute-script.py plan-marshall:build-operations:{build_system} execute"
    goals = GOAL_MAPPINGS[build_system][label]
    cmd = f'{base} --goals "{goals}"'
    if module and module != "default":
        cmd += f" --module {module}"
    if label == "pre-commit":
        cmd += " --profile pre-commit"
    return cmd
```

---

## Shared Infrastructure

All build operations share:

| Component | Purpose |
|-----------|---------|
| **Timeout handling** | `plan-marshall:run-config` for adaptive timeouts |
| **Output format** | TOON for all script outputs |
| **Two-layer execution** | Outer Bash timeout + inner shell timeout |

---

## Wizard Responsibility

The steward wizard:

1. **Detects build systems** via `build_env detect`
2. **Detects modules** via `build_env detect-modules`
3. **Generates full commands** with correct script paths
4. **Stores in marshal.json** under `modules.{name}.commands`

Example wizard step:
```markdown
1. Call: `plan-marshall:build-operations:build_env persist`
   (detects systems, modules, and generates commands)
2. Display detected modules and command counts to user
```

---

## Command Resolution

Callers resolve commands from config:

```bash
# Step 1: Get command from config
COMMAND=$(jq -r '.modules["default"].commands.test' .plan/marshal.json)

# Step 2: Get adaptive timeout
TIMEOUT=$(python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout get \
    --command "build:default:test" --default 300)

# Step 3: Execute with timing
START=$(date +%s)
timeout ${TIMEOUT}s eval "$COMMAND"
EXIT_CODE=$?
END=$(date +%s)
DURATION=$((END - START))

# Step 4: Update timeout on success
if [ $EXIT_CODE -eq 0 ]; then
    python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout set \
        --command "build:default:test" --duration $DURATION
fi
```

This pattern:
- Works with any build system (command already contains correct script)
- Allows user customization (edit marshal.json)
- Provides full transparency (config shows exact command)
- Learns optimal timeouts over time

---

## Backward Compatibility

For projects without `modules.{name}.commands`:

1. `get-command` falls back to `build_systems[]` expansion
2. Logs deprecation warning
3. Returns constructed command

Migration path: Re-run wizard or call `build_env persist`.

---

## Integration Points

### With marshall-steward

- Steward wizard calls `build_env persist` to generate commands
- Steward health check verifies build systems detected
- Steward does NOT contain build detection logic

### With run-config

- Build operations use `run_config timeout get/set` for adaptive timeouts
- Command key format: `build:{module}:{label}`
- Example: `build:oauth-sheriff-core:test`

### With plan-marshall-config

- `modules get-command` resolves from `modules.{name}.commands.{label}`
- `modules set-command` allows manual customization
- `modules list` shows all modules with command counts

---

## Error Handling

All scripts follow the output contract:

| Condition | Exit Code | Stream |
|-----------|-----------|--------|
| Success | 0 | stdout |
| Error | 1 | stderr |

Error output format (TOON):
```toon
status: error
operation: execute
error: Build failed with exit code 1
context: Compilation errors found in 3 files
```
