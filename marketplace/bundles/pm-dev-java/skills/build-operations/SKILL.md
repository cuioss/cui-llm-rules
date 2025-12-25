---
name: build-operations
description: Maven and Gradle build execution with output parsing, error categorization, and warning handling
allowed-tools: [Bash, Read]
---

# Java Build Operations

Build execution and output parsing for Maven and Gradle projects.

## Script Invocation

All scripts are invoked via the executor:

```
python3 .plan/execute-script.py pm-dev-java:build-operations:{script} {subcommand} {args}
```

## Maven Operations

### run (Primary API)

Unified command that executes build and returns parsed output on failure.

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven run \
    --targets "<goals>" \
    [--module <module>] \
    [--profile <profile>] \
    [--timeout <seconds>] \
    [--mode <mode>]
```

**Parameters**:
- `--targets` - Maven goals to execute (required)
- `--module` - Target module for multi-module projects
- `--profile` - Maven profile to activate
- `--timeout` - Timeout in seconds (default from run-config)
- `--mode` - Output mode: actionable (default), structured, errors

**Output Format (TOON)**:

Success:
```
status: success
log_file: target/build-output-2025-01-15-143022.log
exit_code: 0
duration_seconds: 45
command_executed: ./mvnw -l target/build-output-... clean test -pl core
```

Build Failed (includes parsed errors):
```
status: error
error: build_failed
log_file: target/build-output-2025-01-15-143022.log
exit_code: 1
duration_seconds: 23
command_executed: ./mvnw -l target/build-output-... clean test -pl core

errors[2]{file,line,message,category}:
src/main/java/Foo.java    42    cannot find symbol       compile
src/main/java/Bar.java    15    null pointer             test

tests:
  passed: 40
  failed: 2
  skipped: 1
```

### execute (Low-level)

Execute Maven build, return log file reference only.

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven execute \
    --goals "<goals>" \
    [--module <module>] \
    [--profile <profile>] \
    [--timeout <ms>]
```

### parse (Low-level)

Parse build output from log file.

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven parse \
    --log <path> \
    [--mode <mode>]
```

### find-module

Find Maven module path from artifactId.

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven find-module \
    --artifact-id <id>
```

### search-markers

Search for OpenRewrite TODO markers in source files.

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven search-markers \
    --source-dir <dir>
```

### check-warnings

Categorize build warnings against acceptable patterns.

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:maven check-warnings \
    --warnings <json> \
    [--patterns <json>]
```

## Gradle Operations

### run (Primary API)

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:gradle run \
    --targets "<tasks>" \
    [--module <module>] \
    [--timeout <seconds>] \
    [--mode <mode>]
```

### execute (Low-level)

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:gradle execute \
    --tasks "<tasks>" \
    [--module <module>] \
    [--timeout <ms>]
```

### parse (Low-level)

```bash
python3 .plan/execute-script.py pm-dev-java:build-operations:gradle parse \
    --log <path> \
    [--mode <mode>]
```

## Output Modes

- **actionable** (default) - Errors + warnings NOT in acceptable_warnings
- **structured** - All errors + all warnings with `[accepted]` markers
- **errors** - Only errors, compact format

## Error Categories

| Category | Description |
|----------|-------------|
| `compilation_error` | Compile-time Java errors |
| `test_failure` | Test assertion failures |
| `dependency_error` | Dependency resolution issues |
| `javadoc_warning` | JavaDoc documentation issues |
| `deprecation_warning` | Deprecated API usage |
| `unchecked_warning` | Unchecked type conversions |
| `openrewrite_info` | OpenRewrite plugin output |

## Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| `build_failed` | Non-zero exit code | Errors included in response |
| `timeout` | Exceeded timeout | Increase timeout, check log_file |
| `execution_failed` | Process couldn't start | Check wrapper exists |
| `log_file_creation_failed` | Can't create log | Check permissions |

## Warning Handling

Warnings are filtered via acceptable_warnings in run-configuration.json:

```json
{
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": ["commons-logging via spring-core"],
      "plugin_compatibility": ["maven-compiler-plugin 3.8 on Java 21"],
      "platform_specific": []
    }
  }
}
```

**Manage warnings via run-config**:
```bash
# Add accepted warning
python3 .plan/execute-script.py plan-marshall:run-config:run_config warning add \
    --category transitive_dependency \
    --pattern "commons-logging via spring-core"

# List accepted warnings
python3 .plan/execute-script.py plan-marshall:run-config:run_config warning list

# Remove accepted warning
python3 .plan/execute-script.py plan-marshall:run-config:run_config warning remove \
    --category transitive_dependency \
    --pattern "commons-logging via spring-core"
```

## Integration

### With plan-marshall:build-operations

This bundle provides execution scripts registered via `extension.py`:

```python
# skills/plan-marshall-plugin/extension.py
def provides_build_systems() -> list:
    return ['maven', 'gradle']

def get_command_mappings() -> dict:
    return {
        'module-tests': 'python3 .plan/execute-script.py pm-dev-java:build-operations:maven run --targets "clean test"',
        ...
    }
```

### With run-config

- Adaptive timeouts via `timeout get/set`
- Warning filtering via `acceptable_warnings`

## References

- `plan-marshall:build-operations` - Central detection and extension discovery
- `plan-marshall:build-operations/standards/api-contract.md` - Shared TOON output format
- `plan-marshall:build-operations/standards/canonical-vocabulary.md` - Canonical command names
- `standards/maven-impl.md` - Maven execution and parsing details
- `standards/gradle-impl.md` - Gradle execution and parsing details
- `standards/pom-maintenance.md` - POM file operations
