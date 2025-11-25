---
name: cui-maven-rules
description: Complete Maven standards covering build processes, POM maintenance, dependency management, and Maven integration for CUI projects
allowed-tools: Read, Grep, Bash(./mvnw:*), Bash(python3:*)
---

# CUI Maven Rules

Comprehensive Maven standards for CUI projects covering build verification, POM maintenance, dependency management, Maven wrapper updates, and integration with build tools.

## What This Skill Provides

### Maven Build Standards
- Pre-commit profile configuration and execution
- Build success criteria and verification
- Quality gate enforcement
- Execution time tracking and optimization
- Error and warning analysis
- OpenRewrite marker handling

### POM Maintenance Standards
- BOM (Bill of Materials) management
- Dependency management with properties
- Version naming conventions (version.*, maven.*.plugin.version)
- Scope optimization (compile, provided, runtime, test)
- OpenRewrite integration for automated cleanup
- Maven wrapper updates and maintenance

### Maven Build Execution Standards
- Module builds with `-pl`, `--also-make`, `--also-make-dependents`
- Reactor build order and dependency resolution
- Build timeout calculation and management
- Maven phase integration (validate, compile, test, etc.)
- SonarQube integration and coverage reporting
- CI/CD build environment standards

### Quality Standards
- Compilation error resolution
- Test failure handling
- Code warning fixes
- JavaDoc mandatory fixes
- Dependency analysis
- Acceptable warning management

## When to Activate This Skill

Activate this skill when:
- Building Maven projects with quality checks
- Analyzing Maven build output
- Fixing Maven build errors or warnings
- Executing module or reactor builds
- Maintaining POM files
- Managing dependencies or BOMs
- Updating Maven wrappers
- Setting up CI/CD Maven builds
- Troubleshooting Maven issues

## Workflow

### Step 1: Load Maven Standards

**CRITICAL**: Load Maven standards based on the task context.

1. **For build execution tasks** (running builds, module targeting, reactor builds):
   ```
   Read: standards/maven-build-execution.md
   ```

2. **For POM maintenance tasks** (editing POM files, managing dependencies, updating BOMs):
   ```
   Read: standards/pom-maintenance.md
   ```

3. **For comprehensive Maven work** (build verification, complete project setup):
   ```
   Read: standards/maven-build-execution.md
   Read: standards/pom-maintenance.md
   ```

### Step 2: Apply Standards to Task

After loading the appropriate standards:

1. Extract key requirements relevant to your specific task
2. Follow the patterns and guidelines from the loaded standards
3. Apply quality gates and verification criteria as specified
4. Ensure all changes align with CUI Maven best practices

---

## Workflow: Execute Maven Build

**Pattern**: Pattern 4 (Command Chain Execution)

This workflow executes Maven builds and returns structured results. Use this workflow whenever Maven builds are needed.

### When to Use

Use this workflow when:
- Running Maven builds (clean, compile, test, verify, install, package)
- Executing builds with specific profiles (-Ppre-commit, -Pcoverage, -Pintegration-tests)
- Building specific modules (-pl module-name)
- Building native images (-Dnative)

### Parameters

- **goals** (required): Maven goals to execute (e.g., "clean install", "clean verify -DskipTests")
- **module** (optional): Specific module to build (-pl flag)
- **profile** (optional): Maven profile to activate (-P flag)
- **timeout** (optional): Build timeout in milliseconds (default: 120000)
- **output_mode** (optional): How to process output - "default", "errors", "structured" (default: "structured")

### Step 1: Execute Maven Build

Use `execute-maven-build.py` which handles log file pre-creation, timestamping, and Maven execution atomically:

```bash
python3 scripts/execute-maven-build.py \
    --goals "{goals}" \
    --profile {profile} \
    --module {module} \
    --timeout {timeout}
```

**Output**: JSON with `log_file`, `exit_code`, `duration_ms`, `command_executed`

**Examples:**
```bash
# Basic build
python3 scripts/execute-maven-build.py --goals "clean install"

# Module-specific build
python3 scripts/execute-maven-build.py --goals "clean install" --module auth-service

# With profile
python3 scripts/execute-maven-build.py --goals "clean verify" --profile pre-commit

# Coverage build
python3 scripts/execute-maven-build.py --goals "clean test" --profile coverage

# Native image with extended timeout
python3 scripts/execute-maven-build.py --goals "clean package -Dnative" --timeout 600000
```

The script:
- Generates timestamped log filename automatically
- Pre-creates log file (handles `clean` goal correctly)
- Executes Maven and captures exit code
- Prints `[EXEC] <command>` to stderr for visibility
- Returns structured JSON result

### Step 2: Parse Build Output

```bash
python3 scripts/parse-maven-output.py \
    --log {log_file from step 1} \
    --mode {output_mode}
```

### Step 3: Return Results

Return structured JSON with:
- Build status (SUCCESS/FAILURE)
- Categorized issues (compilation_error, test_failure, javadoc_warning, dependency_error)
- Summary counts
- Metrics (duration, tests run/failed)

### Usage from Commands

Commands invoke this workflow as:
```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean install
  module: auth-service (optional)
  profile: pre-commit (optional)
  output_mode: structured (optional)
```

### Issue Routing

Based on returned issue categories, route to appropriate fix commands:

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/java-implement-code` |
| `test_failure` | `/java-implement-tests` |
| `javadoc_warning` | `/java-fix-javadoc` |
| `dependency_error` | Manual POM fix |

---

## Workflow: Parse Maven Build Output

**Pattern**: Pattern 4 (Command Chain Execution)

This workflow parses Maven build output logs and categorizes issues for systematic fix orchestration.

### When to Use

Use this workflow when:
- Analyzing Maven build output for errors and warnings
- Categorizing build issues for orchestrated fixing
- Filtering out OpenRewrite-related messages
- Generating structured issue reports

### Step 1: Execute Script

**Parse the build log file:**

```bash
python3 scripts/parse-maven-output.py \
    --log <path-to-log-file> \
    --mode <output-mode>
```

**Output Modes:**
- `default` - Summary with all errors and warnings (human-readable)
- `errors` - Only errors (no warnings)
- `structured` - Full JSON output for machine processing
- `no-openrewrite` - Errors/warnings excluding OpenRewrite messages

### Step 2: Process Results

**JSON Output Contract (structured mode):**

```json
{
  "status": "success|error",
  "data": {
    "build_status": "SUCCESS|FAILURE",
    "issues": [
      {
        "type": "compilation_error|test_failure|dependency_error|javadoc_warning|other",
        "file": "path/to/File.java",
        "line": 45,
        "column": 20,
        "message": "error message",
        "severity": "ERROR|WARNING",
        "suggestions": ["fix suggestion 1", "fix suggestion 2"]
      }
    ],
    "summary": {
      "compilation_errors": 0,
      "test_failures": 0,
      "javadoc_warnings": 0,
      "dependency_errors": 0,
      "total_issues": 0
    }
  },
  "metrics": {
    "duration_ms": 21635,
    "tests_run": 13,
    "tests_failed": 0
  }
}
```

### Step 3: Route to Appropriate Fix Commands

Based on issue category, delegate to appropriate commands:

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/java-implement-code` |
| `test_failure` | `/java-implement-tests` |
| `javadoc_warning` | `/java-fix-javadoc` |
| `dependency_error` | Manual POM fix |

### Script Location

`scripts/parse-maven-output.py`

---

## Workflow: Handle OpenRewrite Markers

**Pattern**: Pattern 3 (Search-Analyze-Report)

This workflow searches for OpenRewrite TODO markers in source code and handles suppression based on marker type.

### When to Use

Use this workflow when:
- Build completes but OpenRewrite markers remain in source files
- Need to suppress known false-positive markers
- Iterating on build to clear marker warnings

### Parameters

- **source_dir** (optional): Directory to search (default: `src`)

### Step 1: Search for Markers

```
Grep: pattern="/\*~~\(TODO:" path="{source_dir}" output_mode="files_with_matches"
```

If no files found, workflow completes successfully (no markers).

### Step 2: Analyze Markers

For each file with markers:
1. Read file content
2. Extract marker messages with line numbers
3. Categorize by recipe type:
   - **CuiLogRecordPatternRecipe** → LogRecord warning
   - **InvalidExceptionUsageRecipe** → Exception warning
   - **Other** → Unknown type

### Step 3: Handle by Type

**LogRecord warnings (AUTO-SUPPRESS):**
```java
// cui-rewrite:disable CuiLogRecordPatternRecipe
LOGGER.info(INFO.SOME_MESSAGE, param);
```

**Exception warnings (AUTO-SUPPRESS):**
```java
// cui-rewrite:disable InvalidExceptionUsageRecipe
catch (SomeException e) {
```

**Other types (ASK USER):**
Present marker to user with:
- File and line number
- Marker message
- Options: Suppress, Ignore, Manual fix

### Step 4: Verify After Changes

After suppression changes:
- Re-run Maven build
- Verify markers are gone
- If markers persist after 3 iterations, report failure

### Reference

See `standards/maven-openrewrite-handling.md` for full documentation.

---

## Workflow: Manage Acceptable Warnings

**Pattern**: Pattern 2 (Read-Process-Write)

This workflow manages the acceptable warnings list in `.claude/run-configuration.json`.

### When to Use

Use this workflow when:
- Adding infrastructure warnings to acceptable list
- Removing resolved warnings from acceptable list
- Listing current acceptable warnings

### Parameters

- **action** (required): `add`, `remove`, or `list`
- **pattern** (optional): Warning pattern to add/remove
- **command** (optional): Maven command key (default: `./mvnw clean install`)
- **config_file** (optional): Config file path (default: `.claude/run-configuration.json`)

### Step 1: Read Configuration

```
Read: {config_file}
```

Access JSON path: `maven.{command}.acceptable_warnings`

If file doesn't exist, create with initial structure:
```json
{
  "version": 1,
  "maven": {
    "{command}": {
      "acceptable_warnings": []
    }
  }
}
```

### Step 2: Process Action

**Action: list**
- Return `acceptable_warnings` array for the command

**Action: add**
- Validate pattern is not a JavaDoc warning (NEVER acceptable)
- Validate pattern matches infrastructure warning criteria
- Add to `acceptable_warnings` array:
  ```json
  {
    "pattern": "{pattern}",
    "category": "{transitive_dependency|plugin_compatibility|platform_specific}",
    "reason": "{why this is acceptable}",
    "added": "{YYYY-MM-DD}"
  }
  ```

**Action: remove**
- Find entry with matching pattern
- Remove from `acceptable_warnings` array

### Step 3: Write Configuration

If add/remove action:
- Write updated JSON to config file
- Return confirmation with updated array

### Infrastructure Warning Criteria

Only these warning types can be added to acceptable list:
- Transitive dependency version conflicts (beyond project control)
- Plugin compatibility warnings (locked by parent POM)
- Platform-specific warnings (OS, JVM version)

**NEVER acceptable:**
- JavaDoc warnings (ALWAYS fix)
- Compilation warnings (ALWAYS fix)
- Deprecation warnings (ALWAYS fix unless from external dependency)

### Reference

See `standards/maven-acceptable-warnings.md` for full documentation.

---

## Standards Organization

All standards are organized in the `standards/` directory:

- `maven-build-execution.md` - Build execution, module targeting, reactor builds, timeout management, output handling
- `pom-maintenance.md` - Comprehensive POM maintenance process, BOM management, dependency management, scope optimization
- `maven-openrewrite-handling.md` - OpenRewrite marker search, categorization, and suppression patterns
- `maven-acceptable-warnings.md` - Infrastructure vs fixable warning classification, acceptable list management

## Tool Access

This skill requires:
- **Read**: To load standards files
- **Grep**: To search for patterns in standards
- **Bash(./mvnw:*)**: To execute Maven builds
- **Bash(python3:*)**: To execute parse-maven-output.py script

## Usage Pattern

When this skill is activated, it loads all Maven-related standards into the agent's context. Agents can then reference these standards when:

1. **Executing builds**: Module targeting, reactor builds, timeout management, output handling
2. **Fixing issues**: Knowing how to handle errors, warnings, JavaDoc issues, OpenRewrite markers
3. **Maintaining POMs**: Following BOM patterns, property naming, dependency management rules
4. **Optimizing dependencies**: Applying scope rules, consolidation criteria
5. **Configuring CI/CD**: Quality profiles, non-interactive builds, environment setup
6. **Updating wrappers**: Following Maven wrapper update procedures

## Integration with Commands

### maven-build-and-fix Command

The `/maven-build-and-fix` command activates this skill to:
- Load build verification standards
- Understand quality gate criteria
- Know how to handle OpenRewrite markers
- Follow JavaDoc fix requirements
- Apply acceptable warning rules
- Parse build output for issue categorization

The skill provides the authoritative standards that guide all build-related decisions and fixes.

## Standards Coverage

### Build Execution
- ✅ Module builds with `-pl`, `--also-make`, `--also-make-dependents`
- ✅ Reactor builds with `-rf` (resume from)
- ✅ Timeout calculation (duration * 1.25 safety margin)
- ✅ Output capture with Maven's `-l` flag
- ✅ Build status determination (exit code + output content)
- ✅ Quality profiles (pre-commit, coverage, integration-tests)

### Build Process
- ✅ Pre-commit profile execution
- ✅ Build success criteria (exit code, BUILD SUCCESS text, no ERROR lines)
- ✅ Output analysis patterns
- ✅ Iteration workflow

### Issue Handling
- ✅ Compilation error fixes
- ✅ Test failure resolution
- ✅ Code warning handling
- ✅ JavaDoc mandatory fixes (NEVER optional)
- ✅ OpenRewrite marker auto-suppression (LogRecord, Exception)
- ✅ Acceptable warning management

### POM Maintenance
- ✅ BOM implementation patterns
- ✅ Property naming conventions
- ✅ Dependency aggregation rules
- ✅ Scope optimization guidelines
- ✅ Version management (handled by Dependabot)
- ✅ OpenRewrite recipe execution

## Related Skills

- **cui-javadoc**: JavaDoc standards used for mandatory JavaDoc fixes
- **cui-java-unit-testing**: Testing standards referenced in build verification

## Maintenance Notes

Standards in this skill are authoritative for:
- All Maven build processes in CUI projects
- All POM maintenance activities
- All Maven-related quality checks
- All Maven integration configurations

When standards need updates, modify the files in the `standards/` directory and the skill will automatically reflect the changes when next activated.

