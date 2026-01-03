# Build Execution API

Specification for build command execution in domain extensions.

## Purpose

Domain bundles that provide build capabilities expose a **unified execution API** that:
- Captures all output to a log file (not stdout/stderr)
- Provides adaptive timeout learning
- Returns structured results for caller interpretation

## Execution Contract

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | Yes | Full build command arguments (e.g., `"clean verify -Ppre-commit"`) |
| `command_key` | string | Yes | Identifier for timeout learning (e.g., `"maven:verify"`) |
| `timeout` | int | No | Timeout in seconds (default: 300) |
| `working_dir` | string | No | Execution directory (default: `.`) |

**Note**: Build-system-specific options (profiles, modules, flags) are passed as part of the `command` string, not as separate parameters.

### Output

```json
{
  "status": "success | error | timeout",
  "exit_code": 0,
  "duration_seconds": 45,
  "log_file": "target/build-output-2026-01-01-165846.log",
  "command": "./mvnw -l target/build-output-... clean verify"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success`, `error`, or `timeout` |
| `exit_code` | int | Process exit code (-1 for timeout/execution failure) |
| `duration_seconds` | int | Actual execution time |
| `log_file` | string | Path to captured output |
| `command` | string | Full command that was executed |

## Requirements

### R1: Log File Output

All build output **must** go to a log file, not stdout/stderr.

**Rationale**: Build tools produce verbose output that clutters conversation context. Log files allow:
- Full output available for error analysis
- Compact result returned to caller
- Persistent record for debugging

**Log file location**: `.plan/temp/build-output/{scope}/{build-system}-{timestamp}.log`

| Component | Values | Example |
|-----------|--------|---------|
| `{scope}` | `default` (root) or module name | `default`, `core-api` |
| `{build-system}` | `maven`, `gradle`, `npm` | `maven` |
| `{timestamp}` | `YYYY-MM-DD-HHMMSS` | `2026-01-03-141523` |

**Examples**:
- `.plan/temp/build-output/default/maven-2026-01-03-141523.log` - root Maven build
- `.plan/temp/build-output/core-api/maven-2026-01-03-141530.log` - module build
- `.plan/temp/build-output/default/npm-2026-01-03-141545.log` - npm build

Using `.plan/temp/` ensures:
- Already gitignored
- Part of temp cleanup maintenance
- Module-scoped logs easy to find
- Build system clearly identified

### R2: Wrapper Preference

Extensions **must** prefer project-local wrappers over system installations.

| Build System | Wrapper Priority |
|--------------|------------------|
| Maven | `./mvnw` → `mvn` |
| Gradle | `./gradlew` → `gradle` |
| npm | `npx` → `npm` |

**Rationale**: Project wrappers ensure consistent versions across environments.

### R3: Timeout Learning

Extensions **must** integrate with `run_config` for adaptive timeouts.

**Storage**: `.plan/run-configuration.json`
```json
{
  "commands": {
    "maven:clean_verify": { "timeout_seconds": 180 },
    "npm:test": { "timeout_seconds": 45 }
  }
}
```

**Python API** (import from `plan-marshall:run-config`):

```python
from run_config import timeout_get, timeout_set

# Before execution: get timeout to use
timeout = timeout_get(
    command_key="maven:clean_verify",  # Identifier for this command
    default=300,                        # Default if no learned value
    project_dir="."                     # Project root
)
# Returns: default (first run) or learned * 1.25 (subsequent runs)

# After execution: record actual duration
timeout_set(
    command_key="maven:clean_verify",
    duration=165,                       # Actual execution time
    project_dir="."
)
# Updates learned value with weighted average (80% higher, 20% lower)
```

**Algorithm**:
- `timeout_get`: Returns `persisted * 1.25` (safety margin) or default if none
- `timeout_set`: Computes `0.80 * max(existing, new) + 0.20 * min(existing, new)`

**CLI** (via execute-script):
```bash
# Get timeout
python3 .plan/execute-script.py plan-marshall:run-config:run_config \
  timeout get --command "maven:verify" --default 300

# Set timeout
python3 .plan/execute-script.py plan-marshall:run-config:run_config \
  timeout set --command "maven:verify" --duration 165
```

## CLI Interface

Extensions expose execution via CLI subcommands:

| Subcommand | Output Format | Use Case |
|------------|---------------|----------|
| `execute` | JSON | Stored commands, scripts |
| `run` | TOON | Interactive builds with error parsing |

### JSON Output (execute)

```json
{
  "status": "success",
  "data": {
    "log_file": "target/build-output-*.log",
    "exit_code": 0,
    "duration_ms": 45000,
    "command_executed": "./mvnw ..."
  }
}
```

### TOON Output (run)

```
status: success
log_file: target/build-output-*.log
exit_code: 0
duration_seconds: 45
command_executed: ./mvnw ...
```

On failure, `run` parses the log file and includes extracted errors/warnings.

## Invocation Patterns

### From project-structure.json

```json
{
  "build_commands": {
    "module-tests": "python3 .plan/execute-script.py {bundle}:plan-marshall-plugin:{script} execute --args \"clean test\"",
    "verify": "python3 .plan/execute-script.py {bundle}:plan-marshall-plugin:{script} execute --args \"clean verify\""
  }
}
```

### From extension.py

```python
def get_command_mappings(self) -> dict:
    base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven"
    return {
        "maven": {
            "module-tests": f'{base} execute --args "clean test"{{module}}',
            "verify": f'{base} execute --args "clean verify"{{module}}',
        }
    }
```

The `{module}` placeholder is resolved to ` -pl <name>` or empty string by the config layer.

### Interactive (agents)

```bash
python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run \
  --args "clean verify -Ppre-commit -pl core-api" \
  --mode actionable
```

## Error Handling

| Status | Exit Code | Meaning |
|--------|-----------|---------|
| `success` | 0 | Build completed successfully |
| `error` | 1+ | Build failed (check log file) |
| `error` | -1 | Execution failed (wrapper not found, etc.) |
| `timeout` | -1 | Build exceeded timeout |

## Implementation Location

```
{bundle}/skills/plan-marshall-plugin/scripts/
├── {build-system}.py          # CLI orchestrator
└── ...                        # Supporting modules
```

## Compliance

Extensions providing build commands must:

- [ ] Capture output to log file (not stdout)
- [ ] Prefer project wrappers over system commands
- [ ] Integrate with timeout learning
- [ ] Pre-create log files before execution
- [ ] Provide `execute` (JSON) and `run` (TOON) subcommands
- [ ] Return `log_file` path in all results
