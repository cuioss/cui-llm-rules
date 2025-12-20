# Canonical Command Vocabulary

Fixed command names for programmatic lookup across all build systems. This vocabulary is the **contract** between plan orchestration and build execution.

---

## Design Principle

```
Plan Management System
        │
        │ lookup("module-tests", module="oauth-sheriff-core")
        ▼
Canonical Command Vocabulary
        │
        │ resolves to actual build command
        ▼
Build System Adapter (Maven/Gradle/npm)
        │
        │ executes: mvn clean test -pl oauth-sheriff-core
        ▼
Build Output
```

---

## Canonical Command Definitions

| Canonical Name | Semantic Meaning | Phase | Required | Applicable To |
|----------------|------------------|-------|----------|---------------|
| `compile` | Compile production sources only | build | No | jar, war, quarkus |
| `test-compile` | Compile production + test sources | build | No | jar, war, quarkus |
| `module-tests` | Unit tests for a single module | test | **Yes** | jar, war, quarkus, npm |
| `integration-tests` | Integration/E2E tests | test | No | jar, war, quarkus, npm |
| `coverage` | Test execution with coverage report | test | No | jar, war, quarkus, npm |
| `performance` | Performance/benchmark tests | test | No | jar, quarkus, npm |
| `quality-gate` | Static analysis + linting | quality | **Yes** | jar, war, quarkus, pom, npm |
| `verify` | Full verification (tests + quality) | verify | **Yes** | jar, war, quarkus, npm |
| `install` | Install to local repository | deploy | No | jar, war, quarkus, pom |
| `package` | Create deployable artifact | deploy | No | jar, war, quarkus, npm |

---

## Canonical Name Semantics

### Build Phase

| Name | Description | When to Use |
|------|-------------|-------------|
| `compile` | Compile production sources only | Fast feedback on syntax errors |
| `test-compile` | Compile production and test sources | Verify test code compiles |

### Test Phase

| Name | Description | When to Use |
|------|-------------|-------------|
| `module-tests` | Unit tests for the module (JUnit, Jest, pytest) | **Required** for every testable module |
| `integration-tests` | Integration tests (containers, external services) | Detected from profiles |
| `coverage` | Test execution with coverage measurement | When coverage reporting needed |
| `performance` | Performance/benchmark tests (JMH, k6, wrk) | Detected from profiles |

### Quality Phase

| Name | Description | When to Use |
|------|-------------|-------------|
| `quality-gate` | Static analysis, linting, formatting checks | **Required** for every module |

### Verify Phase

| Name | Description | When to Use |
|------|-------------|-------------|
| `verify` | Full verification (compile + test + quality) | **Required** for final validation |

### Deploy Phase

| Name | Description | When to Use |
|------|-------------|-------------|
| `install` | Install artifact to local repository | When other modules depend on this |
| `package` | Create deployable artifact (jar, war, native) | When creating deployables |

---

## Build System Mappings

Canonical names map to build-system-specific commands:

### Maven

| Canonical | Maven Goals |
|-----------|-------------|
| `compile` | `compile` |
| `test-compile` | `test-compile` |
| `module-tests` | `clean test` |
| `integration-tests` | `clean verify -Pintegration-tests` |
| `coverage` | `clean verify -Pcoverage` |
| `performance` | `clean verify -Pbenchmark` |
| `quality-gate` | `clean verify -Ppre-commit` |
| `verify` | `clean verify` |
| `install` | `clean install` |
| `package` | `package` |

### Gradle

| Canonical | Gradle Tasks |
|-----------|--------------|
| `compile` | `compileJava` |
| `test-compile` | `testClasses` |
| `module-tests` | `clean test` |
| `integration-tests` | `clean integrationTest` |
| `coverage` | `clean test jacocoTestReport` |
| `performance` | `clean jmh` |
| `quality-gate` | `clean check` |
| `verify` | `clean build` |
| `install` | `clean publishToMavenLocal` |
| `package` | `clean assemble` |

### npm

| Canonical | npm Scripts |
|-----------|-------------|
| `compile` | - |
| `test-compile` | - |
| `module-tests` | `run test` |
| `integration-tests` | `run test:e2e` |
| `coverage` | `run test:coverage` |
| `performance` | `run test:perf` |
| `quality-gate` | `run lint && run format:check` |
| `verify` | `run test && run lint` |
| `install` | - |
| `package` | `run build` |

---

## Profile to Canonical Mapping

Maven/Gradle profiles are automatically classified to canonical names:

### Integration Test Patterns → `integration-tests`

- `integration-tests`
- `integration-test`
- `integrationTest`
- `it`
- `e2e`
- `acceptance`

### Coverage Patterns → `coverage`

- `coverage`
- `jacoco`

### Quality Patterns → `quality-gate`

- `sonar`
- `pre-commit`
- `precommit`
- `lint`
- `check`
- `quality`

### Performance Patterns → `performance`

- `benchmark`
- `benchmarks`
- `jmh`
- `perf`
- `performance`
- `stress`
- `load`

---

## Profile Modifiers

Modifiers append suffixes to base canonical names:

| Modifier | Suffix | Description |
|----------|--------|-------------|
| `quick` | `-quick` | Fast execution mode |
| `stress` | `-stress` | Stress testing mode |
| `max` | `-max` | Maximum load mode |

Example: Profile `quick` in a benchmark module → `performance-quick`

---

## Old to Canonical Migration

| Old Label | New Canonical | Notes |
|-----------|---------------|-------|
| `test` | `module-tests` | Renamed for clarity |
| `pre-commit` | `quality-gate` | Merged into quality-gate |
| `lint` | `quality-gate` | Merged into quality-gate |

**Migration**: Re-run `/marshall-steward` to regenerate configuration.

---

## Module Type Applicability

Commands are filtered based on module type:

| Module Type | Applicable Commands |
|-------------|---------------------|
| `pom` | `install`, `quality-gate` |
| `jar` | All commands |
| `war` | All except `performance` |
| `quarkus` | All commands |
| `npm` | `module-tests`, `integration-tests`, `coverage`, `performance`, `quality-gate`, `verify`, `package` |

---

## Lookup API

Plan execution agents use canonical names for build operations:

```bash
# Look up command for canonical name
python3 .plan/execute-script.py plan-marshall:build-operations:build_env lookup \
  --canonical "module-tests" --module "oauth-sheriff-core"

# Get all available commands for module
python3 .plan/execute-script.py plan-marshall:build-operations:build_env get-available-commands \
  --module "oauth-sheriff-core"

# Validate required commands are configured
python3 .plan/execute-script.py plan-marshall:build-operations:build_env validate-required \
  --module "oauth-sheriff-core"
```

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Required command missing | Exit with error message and recovery guidance |
| Optional command missing | Return empty, caller decides fallback |
| Module not found | Exit with module list |
| Config file missing | Exit with setup instructions |

---

## Integration with Timeout Handling

Commands use two-layer timeout handling:

```bash
# 1. Get adaptive timeout
TIMEOUT=$(python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout get \
  --command "build:module-tests:oauth-sheriff-core" --default 300)

# 2. Look up canonical command
COMMAND=$(python3 .plan/execute-script.py plan-marshall:build-operations:build_env lookup \
  --canonical "module-tests" --module "oauth-sheriff-core")

# 3. Execute with timeout
timeout ${TIMEOUT}s ${COMMAND}
```

See: `plan-marshall:run-config` skill for timeout handling patterns.
