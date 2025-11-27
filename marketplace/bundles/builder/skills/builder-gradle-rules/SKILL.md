---
description: Gradle build execution, output parsing, and issue routing for CUI projects
allowed_tools:
  - Read
  - Grep
  - Bash(./gradlew:*)
  - Bash(python3:*)
---

# builder-gradle-rules Skill

Build execution, output parsing, and issue routing for Gradle projects.

## Workflows

### Workflow 1: Execute Gradle Build

**Pattern**: Pattern 4 (Command Chain Execution)

**Parameters**:
- `tasks` (required): Gradle tasks (e.g., "clean build", "test")
- `project` (optional): Specific subproject (-p flag)
- `skip_tests` (optional): Skip tests (-x test)
- `fail_at_end` (optional): Continue on failure (--continue)
- `timeout` (optional): Build timeout in milliseconds (default: 120000)
- `output_mode` (optional): "default", "errors", "structured" (default: "structured")

**Execution Steps**:

1. **Execute Gradle**:
   ```bash
   python3 scripts/execute-gradle-build.py \
       --tasks "{tasks}" \
       --project {project} \
       --skip-tests {skip_tests} \
       --timeout {timeout}
   ```
   Returns JSON with `log_file`, `exit_code`, `duration_ms`, `command_executed`

2. **Parse Output**:
   ```bash
   python3 scripts/parse-gradle-output.py \
       --log {log_file from step 1} \
       --mode {output_mode}
   ```

3. **Return Structured Result**

**Output Contract** (structured mode):
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
        "suggestions": ["fix 1", "fix 2"]
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
    "tasks_executed": 12,
    "tasks_failed": 0,
    "tests_run": 13,
    "tests_failed": 0
  }
}
```

---

### Workflow 2: Parse Gradle Build Output

**Pattern**: Pattern 4 (Command Chain Execution)

**Parameters**:
- `log` (required): Path to Gradle build log file
- `mode` (optional): "default", "errors", "structured" (default: "default")

**Execution**:
```bash
python3 scripts/parse-gradle-output.py --log <path> --mode <mode>
```

**Output Modes**:
- `default`: Summary with all errors and warnings (human-readable)
- `errors`: Only errors (no warnings)
- `structured`: Full JSON output for machine processing

**JSON Output Contract**:
```json
{
  "status": "success|error",
  "data": {
    "build_status": "SUCCESS|FAILURE",
    "issues": [...],
    "summary": {...}
  },
  "metrics": {
    "duration_ms": 21635,
    "tasks_executed": 12,
    "tests_run": 13,
    "tests_failed": 0
  }
}
```

---

### Workflow 3: Find Subproject Path

**Pattern**: Pattern 4 (Command Chain Execution)

**Parameters**:
- `project_name` (option 1): Project name to search for
- `project_path` (option 2): Explicit project path to validate
- `root` (optional): Project root directory (default: current directory)

**Execution**:
```bash
# Search by project name
python3 scripts/find-gradle-project.py --project-name {project_name}

# Validate explicit path
python3 scripts/find-gradle-project.py --project-path {project_path}
```

**Success Response**:
```json
{
  "status": "success",
  "data": {
    "project_name": "auth-service",
    "project_path": ":services:auth-service",
    "build_file": "services/auth-service/build.gradle.kts",
    "parent_projects": [":services"],
    "gradle_p_argument": "-p services/auth-service"
  }
}
```

**Ambiguous Response**:
```json
{
  "status": "error",
  "error": "ambiguous_project_name",
  "message": "Multiple projects found for name 'auth-service'. Select one.",
  "choices": [":services:auth-service", ":legacy:auth-service"]
}
```

---

### Workflow 4: Search OpenRewrite Markers

**Pattern**: Pattern 4 (Command Chain Execution)

**Parameters**:
- `source_dir` (optional): Directory to search (default: `src`)
- `extensions` (optional): File extensions to search (default: `.java,.kt`)

**Execution**:
```bash
python3 scripts/search-openrewrite-markers.py \
    --source-dir {source_dir} \
    --extensions {extensions}
```

**Output**:
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

**Auto-Suppress Recipes**:
- `CuiLogRecordPatternRecipe` - LogRecord warnings
- `InvalidExceptionUsageRecipe` - Exception handling patterns

**Suppression Syntax**:
```java
// cui-rewrite:disable RecipeName
<affected line>
```

---

### Workflow 5: Check Acceptable Warnings

**Pattern**: Pattern 4 (Command Chain Execution)

**Parameters**:
- `warnings` (required): JSON array from parse-gradle-output.py
- `acceptable_warnings` (optional): JSON object with acceptable patterns

**Steps**:
1. Load acceptable patterns via `cui-utilities:claude-run-configuration` skill
   - Read from field: `gradle.acceptable_warnings`
2. Execute categorization:
   ```bash
   python3 scripts/check-acceptable-warnings.py \
       --warnings '{issues_json}' \
       --acceptable-warnings '{patterns_json}'
   ```

**Output**:
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

**Exit Codes**:
- 0: No fixable or unknown warnings (build clean)
- 1: Fixable or unknown warnings exist (action needed)

**Always Fixable Types** (never acceptable):
- `javadoc_warning`
- `compilation_error`
- `deprecation_warning`
- `unchecked_warning`

---

### Workflow 6: Manage Acceptable Warnings Config

**Pattern**: Pattern 2 (Read-Process-Write)

**Operation**: Add/Remove patterns via `cui-utilities:claude-run-configuration` skill

**Add Pattern**:
```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Action: add-entry
Field: gradle.acceptable_warnings.dependency_resolution
Value: "Could not resolve com.example:lib"
```

**Remove Pattern**:
```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Action: remove-entry
Field: gradle.acceptable_warnings.dependency_resolution
Value: "Could not resolve com.example:lib"
```

**Pattern Categories**:
- `dependency_resolution`: Dependency resolution conflicts
- `plugin_compatibility`: Plugin version warnings
- `platform_specific`: OS/JVM warnings

**Configuration Structure**:
```json
{
  "gradle": {
    "acceptable_warnings": {
      "dependency_resolution": [
        "Could not resolve all files for configuration"
      ],
      "plugin_compatibility": [
        "Task :test has been deprecated"
      ],
      "platform_specific": []
    }
  }
}
```

## Standards References

- [Gradle Build Execution Standards](standards/gradle-build-execution.md)
- [Gradle OpenRewrite Handling](standards/gradle-openrewrite-handling.md)
- [Gradle Acceptable Warnings](standards/gradle-acceptable-warnings.md)
