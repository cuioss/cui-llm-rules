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
| `--targets` | string | Yes | Build targets/goals (e.g., `"clean verify -Ppre-commit"`) |
| `--format` | string | No | Output format: `toon` (default) or `json` |
| `--mode` | string | No | Content mode: `actionable` (default), `structured`, or `errors` |
| `--module` | string | No | Module path for scoped builds |
| `--timeout` | int | No | Timeout in seconds (default: 300) |

**Note**: Build-system-specific options (profiles, flags) are passed as part of the `--targets` string.

**Mode values**:
- `actionable` - Filter out accepted warnings, show only actionable items (default)
- `structured` - Keep all warnings, mark accepted ones with `[accepted]` flag
- `errors` - Only show errors, no warnings

### Output

Both formats return the same fields; only the serialization differs.

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success`, `error`, or `timeout` |
| `exit_code` | int | Process exit code (-1 for timeout/execution failure) |
| `duration_seconds` | int | Actual execution time |
| `log_file` | string | Path to captured output |
| `command` | string | Full command that was executed |

See [build-return.md](build-return.md) for complete field definitions, format examples, and error context structure.

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

Extensions expose a single `run` subcommand with format and mode selection:

```bash
python3 .plan/execute-script.py {bundle}:plan-marshall-plugin:{script} run \
  --targets "clean verify" \
  --format toon \             # or --format json
  --mode actionable           # or --mode structured, --mode errors
```

### R4: Dual Format Support

Implementations **must** support both output formats via `--format` parameter:

| Format | Default | Use Case |
|--------|---------|----------|
| `toon` | Yes | Interactive agent builds, human-readable |
| `json` | No | Script integration, programmatic parsing |

**Testing requirement**: Each implementation must have tests verifying both formats produce equivalent data.

### R5: Content Mode Support

Implementations **must** support content filtering via `--mode` parameter:

| Mode | Default | Use Case |
|------|---------|----------|
| `actionable` | Yes | Focus on issues requiring action, filter accepted warnings |
| `structured` | No | Full diagnostics with acceptance status for analysis |
| `errors` | No | Errors only, minimal output for CI pipelines |

**Accepted warnings**: Patterns configured in `.plan/run-configuration.json` under `{build_system}.acceptable_warnings`.

## Invocation Patterns

### From Aggregated Output

The orchestrator resolves commands per module in `.plan/raw-project-data.json`:

```json
{
  "modules": {
    "oauth-sheriff-core": {
      "commands": {
        "module-tests": "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets \"clean test\" --module oauth-sheriff-core",
        "verify": "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets \"clean verify\" --module oauth-sheriff-core"
      }
    }
  }
}
```

See [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) for command resolution.

### From extension.py

```python
def get_command_mappings(self) -> dict:
    base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"
    return {
        "maven": {
            "module-tests": f'{base} --targets "clean test"{{module}}',
            "verify": f'{base} --targets "clean verify"{{module}}',
        }
    }
```

The `{module}` placeholder is resolved to ` --module <name>` or empty string by the config layer.

### Interactive (agents)

```bash
# Default TOON output for interactive use (actionable mode)
python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run \
  --targets "clean verify -Ppre-commit" --module core-api

# JSON output for script integration
python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run \
  --targets "clean verify" --format json

# Structured mode for full diagnostics (shows all warnings with acceptance status)
python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run \
  --targets "clean verify" --mode structured

# Errors-only mode for CI pipelines
python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run \
  --targets "clean verify" --mode errors --format json
```

## Direct Execution API

For module discovery and other non-interactive build operations, extensions use `execute_direct()` from their `{build_system}_execute.py` module.

### Python API

```python
from maven_execute import execute_direct  # or gradle_execute, npm_execute
from build_result import DirectCommandResult

result: DirectCommandResult = execute_direct(
    args="-f pom.xml help:all-profiles dependency:tree",
    command_key="maven:discover-modules",
    project_dir="."  # Optional, defaults to current directory
)

if result["status"] == "success":
    log_content = Path(result["log_file"]).read_text()
    # Parse log content...
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `args` | string | Yes | Build tool arguments (without wrapper command) |
| `command_key` | string | Yes | Key for timeout learning (e.g., `"maven:discover-modules"`) |
| `project_dir` | string | No | Project root directory (default: `.`) |

### Return Value: DirectCommandResult

All `execute_direct()` implementations return `DirectCommandResult` (TypedDict from `build_result.py`):

**Required fields** (always present):

| Field | Type | Description |
|-------|------|-------------|
| `status` | `Literal["success", "error", "timeout"]` | Execution outcome |
| `exit_code` | int | Process exit code (-1 for timeout/failure) |
| `duration_seconds` | int | Actual execution time |
| `log_file` | string | Path to captured output (R1 requirement) |
| `command` | string | Full command executed |

**Optional fields** (build-system specific):

| Field | Type | Description |
|-------|------|-------------|
| `timeout_used_seconds` | int | Timeout that was applied |
| `wrapper` | string | Maven/Gradle: wrapper path used |
| `command_type` | string | npm: "npm" or "npx" |
| `error` | string | Error message (on error/timeout only) |

### Implementation

Each domain bundle provides its own `{build_system}_execute.py` module that:
- Detects and uses project wrappers (R2)
- Creates log files per R1
- Integrates with timeout learning (R3)
- Returns `DirectCommandResult` structure

Location: `{bundle}/skills/plan-marshall-plugin/scripts/{build_system}_execute.py`

| Build System | Module |
|--------------|--------|
| Maven | `maven_execute.py` |
| Gradle | `gradle_execute.py` |
| npm | `npm_execute.py` |

Import the TypedDict for type hints:
```python
from build_result import DirectCommandResult

def execute_direct(...) -> DirectCommandResult:
    ...
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

- [ ] Capture output to log file (R1)
- [ ] Prefer project wrappers over system commands (R2)
- [ ] Integrate with timeout learning (R3)
- [ ] Support `--format toon` and `--format json` (R4)
- [ ] Support `--mode actionable`, `structured`, `errors` (R5)
- [ ] Return `log_file` path in all results
- [ ] Parse and return structured issues on build failure
- [ ] Have tests for both output formats and all modes

## Related Specifications

- [build-return.md](build-return.md) - Return value structure
- [build-project-structure.md](build-project-structure.md) - Project structure discovery
- [extension-contract.md](extension-contract.md) - Extension API contract
- [canonical-commands.md](canonical-commands.md) - Command vocabulary
