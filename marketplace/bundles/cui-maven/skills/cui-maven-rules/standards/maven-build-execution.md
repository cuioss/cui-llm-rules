# Maven Build Execution Standards

## Purpose

This document defines standards for executing Maven builds, including module targeting, reactor builds, timeout management, and output handling. These standards ensure consistent, reliable, and efficient Maven build execution across CUI projects.

## Build Command Construction

### Base Command

All Maven builds use the Maven Wrapper from the project root:

```bash
./mvnw {goals} {options}
```

**Output Capture**: Use Maven's `-l` (log file) flag for output capture with timestamped filenames:

```bash
./mvnw -l target/build-output-2025-11-25-143022.log clean install
```

**Rationale**: Using `-l` instead of shell redirection (`> file 2>&1`) avoids permission issues with `Bash(./mvnw:*)` patterns.

### Common Goals

| Goal Combination | Purpose |
|-----------------|---------|
| `clean install` | Full build with artifact installation |
| `clean verify` | Full build without installation |
| `clean test` | Compile and run tests only |
| `clean package` | Build without integration tests |
| `clean package -Dnative` | Native image build |
| `-Ppre-commit clean install` | Pre-commit quality checks |
| `-Pcoverage clean verify` | Coverage analysis build |

### Log File Handling (CRITICAL)

**Problem**: When using `-l target/build.log` with `clean`, the `clean` phase deletes `target/` before Maven can create the log file, causing build failures.

**Solution**: ALWAYS pre-create the log file before executing Maven:

#### Step 1: Generate Timestamped Filename

```
Format: target/build-output-{YYYY-MM-DD-HHmmss}.log
Example: target/build-output-2025-11-25-143022.log
```

#### Step 2: Pre-Create Log File

**MANDATORY**: Use the Write tool to create an empty log file BEFORE calling Maven:

```
Write: target/build-output-{timestamp}.log
Content: ""  (empty string)
```

This ensures:
- The `target/` directory exists
- The log file exists before `clean` runs
- Maven can append to the file throughout the build

#### Step 3: Execute Maven Build

```bash
./mvnw -l target/build-output-{timestamp}.log {goals}
```

#### Complete Workflow Example

```
1. Generate timestamp: 2025-11-25-143022
2. Write empty file: target/build-output-2025-11-25-143022.log
3. Execute: ./mvnw -l target/build-output-2025-11-25-143022.log -Ppre-commit clean install
4. Parse output from: target/build-output-2025-11-25-143022.log
```

**Why Pre-Create Instead of Separate Clean?**

| Approach | Problems |
|----------|----------|
| Separate `./mvnw clean` then `./mvnw install` | Two builds, inconsistent state, doubled execution time |
| Pre-create log file | Single build, reliable, clean works correctly |

**NEVER** execute Maven with `-l` flag without pre-creating the log file first.

## Module Builds

### Single Module Build

Use `-pl` (project list) to build specific modules:

```bash
./mvnw -l target/module-build.log clean install -pl module-name
```

For nested modules, specify the full path:

```bash
./mvnw -l target/module-build.log clean install -pl parent/child-module
```

### Module Path Detection

To find the correct module path:

1. Search for module in pom.xml files:
   ```bash
   grep -r "<artifactId>module-name</artifactId>" --include="pom.xml"
   ```

2. Identify parent directory structure from results

3. Construct `-pl` parameter:
   - Root module: `-pl module`
   - Nested module: `-pl parent/module`
   - Deep structure: `-pl grandparent/parent/module`

### Building with Dependencies

| Flag | Purpose | Example |
|------|---------|---------|
| `-pl` | Build specific modules | `-pl module-a,module-b` |
| `-am` / `--also-make` | Build required dependencies | `-pl module-a -am` |
| `-amd` / `--also-make-dependents` | Build dependent modules | `-pl module-a -amd` |

**Common Patterns**:

```bash
# Build module and its dependencies
./mvnw -l target/build.log clean install -pl auth-module -am

# Build module and everything that depends on it
./mvnw -l target/build.log clean install -pl core-module -amd

# Build specific modules with dependencies
./mvnw -l target/build.log clean install -pl api,service -am
```

## Reactor Builds

### Resume From Module

Use `-rf` (resume from) to restart a failed multi-module build:

```bash
./mvnw -l target/resume-build.log clean install -rf :module-name
```

**Note**: The colon prefix (`:`) before module name is Maven standard syntax.

**Use Case**: When a reactor build fails midway, resume from the failure point instead of rebuilding everything:

```bash
# Original build failed at auth-service
./mvnw clean install
# [ERROR] Build failed at auth-service

# Resume from auth-service (skipping already-built modules)
./mvnw -l target/resume.log clean install -rf :auth-service
```

### Reactor Build Order

Maven determines build order automatically based on module dependencies. The reactor:

1. Analyzes inter-module dependencies
2. Creates a directed acyclic graph (DAG)
3. Builds modules in topological order
4. Fails fast on first error (unless `-fae` is used)

**Fail-At-End Option**:

```bash
# Continue building other modules after failure
./mvnw -l target/build.log clean install -fae
```

## Timeout Management

### Timeout Calculation

Calculate build timeout using the formula:

```
timeout = last_successful_duration * 1.25
```

The 25% safety margin accounts for:
- System load variations
- Dependency resolution fluctuations
- Network latency for remote resources

### Default Timeouts

| Build Type | Default Timeout |
|------------|-----------------|
| Unit tests only | 60,000ms (1 min) |
| Full build | 120,000ms (2 min) |
| Integration tests | 300,000ms (5 min) |
| Native image | 600,000ms (10 min) |

### Duration Tracking

Track build durations for accurate timeout calculation:

1. Record duration only for **successful** builds
2. Update tracking when duration changes by >10%
3. Failed builds have unpredictable durations and should not update tracking

**Storage**: Use `.claude/run-configuration.md` for duration tracking:

```markdown
# Maven Build Configuration

## ./mvnw -Ppre-commit clean install

### Last Execution Duration
- **Duration**: 120000ms (2 minutes)
- **Last Updated**: 2025-10-31

## ./mvnw clean install -pl auth-module

### Last Execution Duration
- **Duration**: 45000ms (45 seconds)
- **Last Updated**: 2025-10-31
```

## Build Output Modes

### Output Filtering

| Mode | Description |
|------|-------------|
| `FILE` | Status + file path only |
| `DEFAULT` | Status + all errors and warnings |
| `ERRORS` | Status + errors only (no warnings) |
| `NO_OPEN_REWRITE` | Errors/warnings excluding OpenRewrite messages |

### OpenRewrite Filtering

When filtering OpenRewrite messages, exclude lines containing:
- `org.openrewrite`
- `rewrite-maven-plugin`
- OpenRewrite recipe names

## Build Status Determination

Determine build status from both exit code AND output content:

| Exit Code | Output Content | Status |
|-----------|---------------|--------|
| 0 | Contains "BUILD SUCCESS" | SUCCESS |
| 0 | Contains "BUILD FAILURE" | FAILURE |
| ≠ 0 | Any | FAILURE |
| 0 | Contains [ERROR] lines | FAILURE |

**Never assume success from exit code alone.**

## Quality Profiles

### Pre-Commit Profile

```bash
./mvnw -l target/pre-commit.log -Ppre-commit clean install
```

Includes:
- Compilation with all warnings
- Unit test execution
- Code quality checks (Checkstyle, PMD)
- JavaDoc validation
- License header verification

### Coverage Profile

```bash
./mvnw -l target/coverage.log -Pcoverage clean verify
```

Includes:
- All pre-commit checks
- JaCoCo coverage collection
- Coverage report generation
- Coverage threshold verification

### Integration Tests Profile

```bash
./mvnw -l target/integration.log -Pintegration-tests clean verify
```

Includes:
- Skips unit tests (already run in main build)
- Runs integration tests (*IT.java, *ITCase.java)
- Uses Maven Failsafe plugin

## CI/CD Build Standards

### Environment Variables

```bash
# Suppress download progress
export MAVEN_OPTS="-Dorg.slf4j.simpleLogger.log.org.apache.maven.cli.transfer.Slf4jMavenTransferListener=warn"

# Parallel builds (use with caution)
./mvnw -l target/build.log clean install -T 1C
```

### Non-Interactive Builds

```bash
# Batch mode (no interactive prompts)
./mvnw -l target/build.log clean install -B

# Skip tests for deployment builds
./mvnw -l target/deploy.log clean deploy -DskipTests
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Out of memory | Increase heap: `MAVEN_OPTS="-Xmx2g"` |
| Dependency conflicts | Use `mvn dependency:tree -Dverbose` |
| Stale artifacts | Delete `~/.m2/repository/com/yourorg` |
| Failed downloads | Use `-U` to force update snapshots |

### Debug Output

```bash
# Debug level logging
./mvnw -l target/debug.log clean install -X

# Show effective POM
./mvnw help:effective-pom -pl module-name
```

## See Also

- [POM Maintenance Standards](pom-maintenance.md) - Dependency and BOM management
- [Integration Testing](../../../../cui-java-expert/skills/cui-java-unit-testing/standards/integration-testing.md) - Maven Surefire/Failsafe configuration
