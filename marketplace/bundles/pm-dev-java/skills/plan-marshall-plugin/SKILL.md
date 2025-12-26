---
name: plan-marshall-plugin
description: Java domain extension with Maven/Gradle build operations and workflow integration
allowed-tools: [Read, Bash]
---

# Plan Marshall Plugin - Java Domain

Domain extension providing Java development capabilities to plan-marshall workflows, including Maven and Gradle build execution with output parsing.

## Purpose

- Domain identity and workflow extensions (outline, triage)
- Maven and Gradle build execution with parsed output
- Module detection and profile classification
- Profile-based skill organization

## Extension API

Configuration in `extension.py` implements the Extension API contract:

| Function | Purpose |
|----------|---------|
| `is_applicable(project_root)` | Detect Java project (pom.xml, build.gradle) |
| `provides_build_systems()` | Returns `["maven", "gradle"]` |
| `get_command_mappings()` | Canonical to script mappings |
| `get_skill_domains()` | Domain metadata with profiles |
| `provides_triage()` | Returns `pm-dev-java:java-triage` |
| `get_modules(project_root)` | Detect Maven/Gradle modules |
| `get_module_type(module_path)` | Detect jar/war/pom/quarkus type |
| `get_profiles(module_path)` | Detect Maven profiles |

---

## Build Operations

Scripts for Maven and Gradle build execution.

### Maven run (Primary API)

Unified command that executes build and returns parsed output on failure.

```bash
python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run \
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

Build Failed:
```
status: error
error: build_failed
log_file: target/build-output-2025-01-15-143022.log
exit_code: 1
duration_seconds: 23

errors[2]{file,line,message,category}:
src/main/java/Foo.java    42    cannot find symbol       compile
src/main/java/Bar.java    15    null pointer             test

tests:
  passed: 40
  failed: 2
  skipped: 1
```

### Gradle run

```bash
python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run \
    --targets "<tasks>" \
    [--module <module>] \
    [--timeout <seconds>] \
    [--mode <mode>]
```

### Low-level Operations

| Command | Purpose |
|---------|---------|
| `maven execute` | Execute build, return log file reference |
| `maven parse` | Parse build output from log file |
| `maven find-module` | Find module path from artifactId |
| `maven search-markers` | Search OpenRewrite TODO markers |
| `maven check-warnings` | Categorize warnings against patterns |
| `gradle execute` | Execute Gradle tasks |
| `gradle parse` | Parse Gradle build output |
| `gradle find-project` | Find Gradle subproject |
| `gradle search-markers` | Search markers in Gradle project |
| `gradle check-warnings` | Check Gradle warnings |

---

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

---

## Warning Handling

Manage warnings via run-config:

```bash
# Add accepted warning
python3 .plan/execute-script.py plan-marshall:run-config:run_config warning add \
    --category transitive_dependency \
    --pattern "commons-logging via spring-core"

# List accepted warnings
python3 .plan/execute-script.py plan-marshall:run-config:run_config warning list
```

---

## Integration

This extension is discovered by:
- `extension-api` - Build system detection and command generation
- `skill-domains` - Domain configuration
- `marshall-steward` - Project setup wizard

## References

- `plan-marshall:extension-api` - Extension API contract
- `standards/maven-impl.md` - Maven execution details
- `standards/gradle-impl.md` - Gradle execution details
