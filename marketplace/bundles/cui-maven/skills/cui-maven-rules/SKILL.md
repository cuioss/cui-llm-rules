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

## Workflow: Find Module Path

**Pattern**: Pattern 4 (Command Chain Execution)

This workflow finds Maven module paths from artifactId using `find-module-path.py` for use with module-targeted builds.

### When to Use

Use this workflow when:
- Need to build a specific module by name
- Need to resolve artifactId to module path for `-pl` argument
- Validating a module path exists

### Parameters

- **artifact_id** (option 1): ArtifactId to search for
- **module_path** (option 2): Explicit module path to validate
- **root** (optional): Project root directory (default: current directory)

### Step 1: Execute Find Script

**Search by artifactId:**
```bash
python3 scripts/find-module-path.py \
    --artifact-id {artifact_id}
```

**Validate explicit path:**
```bash
python3 scripts/find-module-path.py \
    --module-path {module_path}
```

### Step 2: Process Results

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "artifact_id": "auth-service",
    "module_path": "services/auth-service",
    "pom_file": "services/auth-service/pom.xml",
    "parent_modules": ["services"],
    "maven_pl_argument": "-pl services/auth-service"
  }
}
```

Use `maven_pl_argument` directly in Maven commands.

**Ambiguous ArtifactId Response:**
```json
{
  "status": "error",
  "error": "ambiguous_artifact_id",
  "message": "Multiple modules found for artifactId 'auth-service'. Select one.",
  "choices": ["services/auth-service", "legacy/auth-service"]
}
```

When ambiguous, present choices to user or caller, then use `--module-path` with selected choice.

### Exit Codes

- **0**: Module found successfully
- **1**: Error (not found, ambiguous, invalid path)

### Multi-Module Resolution

The script only matches `<artifactId>` in module definition context (direct child of `<project>`). It ignores:
- Dependencies (`<dependency><artifactId>`)
- Plugins (`<plugin><artifactId>`)
- Parent references (`<parent><artifactId>`)

### Script Location

`scripts/find-module-path.py`

---

## Workflow: Search OpenRewrite Markers

**Pattern**: Pattern 4 (Command Chain Execution)

This workflow searches for OpenRewrite TODO markers in source code using `search-openrewrite-markers.py` and categorizes them for handling.

### When to Use

Use this workflow when:
- Build completes but OpenRewrite markers remain in source files
- Need to find and categorize markers before suppression
- Iterating on build to clear marker warnings

### Parameters

- **source_dir** (optional): Directory to search (default: `src`)
- **extensions** (optional): File extensions to search (default: `.java`)

### Step 1: Execute Search Script

```bash
python3 scripts/search-openrewrite-markers.py \
    --source-dir {source_dir} \
    --extensions {extensions}
```

**Output**: JSON with categorized markers:

```json
{
  "status": "success",
  "data": {
    "total_markers": 5,
    "files_affected": 3,
    "recipe_summary": {"CuiLogRecordPatternRecipe": 2, "SomeOtherRecipe": 1},
    "by_category": {
      "auto_suppress": [...],
      "ask_user": [...]
    },
    "auto_suppress_count": 3,
    "ask_user_count": 2,
    "markers": [...]
  }
}
```

### Step 2: Process by Category

**auto_suppress markers** (CuiLogRecordPatternRecipe, InvalidExceptionUsageRecipe):
- Apply suppression comment from marker's `suppression_comment` field
- No user interaction needed

**ask_user markers** (other recipes):
- Present to user with file, line, message
- Options: Suppress, Ignore, Manual fix

### Step 3: Apply Suppressions

For each marker to suppress, add the suppression comment before the affected line:

```java
// cui-rewrite:disable RecipeName
<affected line>
```

### Step 4: Verify

Re-run the search to confirm markers are handled. Exit codes:
- **0**: No markers or all auto-suppressible
- **1**: Markers requiring user action exist

### Auto-Suppress Recipes

The script automatically categorizes these recipes for auto-suppression:
- `CuiLogRecordPatternRecipe` - LogRecord warnings
- `InvalidExceptionUsageRecipe` - Exception handling patterns

### Script Location

`scripts/search-openrewrite-markers.py`

### Reference

See `standards/maven-openrewrite-handling.md` for full documentation.

---

## Workflow: Check Acceptable Warnings

**Pattern**: Pattern 4 (Command Chain Execution)

This workflow checks build warnings against the acceptable warnings list using `check-acceptable-warnings.py` and categorizes them for action.

### When to Use

Use this workflow when:
- After parsing Maven build output, need to filter acceptable from fixable warnings
- Determining which warnings require attention
- Generating a report of actionable warnings

### Parameters

- **warnings** (required): JSON array of warning objects from parse-maven-output.py
- **acceptable_warnings** (optional): JSON object with acceptable patterns from run-configuration.json

### Step 1: Load Acceptable Patterns

Use `cui-utilities:json-file-operations` to read patterns from run-configuration:

```bash
python3 cui-utilities/json-file-operations/scripts/manage-json-file.py \
    read-field .claude/run-configuration.json \
    --field "maven.acceptable_warnings"
```

If file doesn't exist or field is missing, use empty object `{}`.

### Step 2: Extract Warnings from Parsed Output

From the parse-maven-output.py result, extract the `data.issues` array.

### Step 3: Categorize Warnings

Pass warnings and patterns to the categorization script:

```bash
python3 scripts/check-acceptable-warnings.py \
    --warnings '{issues_json}' \
    --acceptable-warnings '{patterns_json}'
```

Or via stdin:
```bash
echo '{"warnings": [...], "acceptable_warnings": {...}}' | \
    python3 scripts/check-acceptable-warnings.py
```

**Output**: JSON with categorized warnings:

```json
{
  "success": true,
  "total": 15,
  "acceptable": 3,
  "fixable": 10,
  "unknown": 2,
  "categorized": {
    "acceptable": [...],
    "fixable": [...],
    "unknown": [...]
  }
}
```

### Step 4: Process Results

**Exit Codes:**
- **0**: No fixable or unknown warnings (build clean)
- **1**: Fixable or unknown warnings exist (action needed)

**Warning Categories:**

| Category | Action |
|----------|--------|
| `acceptable` | Ignore - matches config patterns |
| `fixable` | Route to appropriate fix command |
| `unknown` | Requires classification (add to config or fix) |

### Always Fixable Types

These warning types are NEVER acceptable (script enforces this):
- `javadoc_warning` - Always fix
- `compilation_error` - Always fix
- `deprecation_warning` - Always fix
- `unchecked_warning` - Always fix

### Unknown Warning Handling

Unknown warnings in output have `requires_classification: true` flag. Agent should:
1. Analyze warning message
2. Either add to acceptable patterns (if infrastructure-related)
3. Or fix the warning

### Acceptable Warnings Format

Patterns are stored in `.claude/run-configuration.json` at path `maven.acceptable_warnings`:

```json
{
  "version": 1,
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": [
        "The POM for com.example:lib:jar:1.0 is missing"
      ],
      "plugin_compatibility": [
        "Using platform encoding UTF-8"
      ],
      "platform_specific": []
    }
  }
}
```

Use `cui-utilities:claude-run-configuration` to validate the file structure.
Use `cui-utilities:json-file-operations` to read/write patterns.

### Script Location

`scripts/check-acceptable-warnings.py` - Pure categorization logic, no file I/O.

---

## Workflow: Manage Acceptable Warnings Config

**Pattern**: Pattern 2 (Read-Process-Write)

This workflow manages the acceptable warnings configuration in `.claude/run-configuration.json`.

### When to Use

Use this workflow when:
- Adding infrastructure warnings to acceptable list
- Removing resolved warnings from acceptable list
- Reviewing current acceptable warnings

### Adding a Pattern

Use the `cui-utilities:json-file-operations` skill:

```bash
python3 scripts/manage-json-file.py add-entry \
    .claude/run-configuration.json \
    --field "maven.acceptable_warnings.transitive_dependency" \
    --value '"The POM for com.example:lib is missing"'
```

Or manually edit `.claude/run-configuration.json`:
1. Navigate to `maven.acceptable_warnings`
2. Add pattern to appropriate array:
   - `transitive_dependency` - For dependency resolution warnings
   - `plugin_compatibility` - For plugin version warnings
   - `platform_specific` - For OS/JVM warnings

### Removing a Pattern

Use the `cui-utilities:json-file-operations` skill:

```bash
python3 scripts/manage-json-file.py remove-entry \
    .claude/run-configuration.json \
    --field "maven.acceptable_warnings.transitive_dependency" \
    --value '"The POM for com.example:lib is missing"'
```

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
- **Bash(python3:*)**: To execute scripts:
  - `execute-maven-build.py` - Atomic Maven build execution
  - `parse-maven-output.py` - Build output parsing
  - `check-acceptable-warnings.py` - Warning categorization
  - `search-openrewrite-markers.py` - OpenRewrite marker search
  - `find-module-path.py` - Module path resolution

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

