# Build Operations API Contract

Shared TOON output formats and API specifications for all build operations.

---

## Output Format: TOON

All scripts output TOON format for consistency and easy parsing.

**Structure**:
```toon
status: success|error
operation: <operation_name>
{operation_specific_fields}

{optional_tables}
```

---

## Detection Operations (build_env.py)

### detect

Detect available build systems in the project.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect
```

**Success Output**:
```toon
status: success
default_system: maven
available_systems: maven,npm

detected[2]{name,priority,technology,detected_by}:
maven	1	java	pom.xml
npm	3	javascript	package.json
```

**Error Output**:
```toon
status: error
error: No build system detected
context: No pom.xml, build.gradle, or package.json found
```

---

### detect-modules

Detect project modules and their build systems.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-modules
```

**Success Output**:
```toon
status: success
module_count: 3

modules[3]{name,path,build_systems,domains}:
default	.	maven	java
oauth-sheriff-core	oauth-sheriff-core	maven	java
oauth-sheriff-ui	oauth-sheriff-ui	npm	javascript
```

---

### persist

Detect build systems, modules, generate commands, and persist to marshal.json.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist [--plan-dir .plan]
```

**Success Output**:
```toon
status: success
persisted_to: marshal.json
build_systems: maven,npm
modules_updated: 3
commands_generated: 15

modules[3]{name,path,commands_count}:
default	.	5
oauth-sheriff-core	oauth-sheriff-core	5
oauth-sheriff-ui	oauth-sheriff-ui	5
```

---

## Build Operations (maven.py / gradle.py / npm.py)

### execute

Execute a build command.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven execute \
    --goals "clean test" \
    [--module MODULE] \
    [--profile PROFILE] \
    [--timeout TIMEOUT_MS]
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `--goals` | Yes | Build goals to execute |
| `--module` | No | Target module (for multi-module builds) |
| `--profile` | No | Build profile to activate |
| `--timeout` | No | Timeout in milliseconds (default: 120000) |

**Success Output**:
```toon
status: success
operation: execute
exit_code: 0
duration_ms: 45230
log_file: .plan/temp/build-20250115-103045.log
command_executed: ./mvnw clean test -pl oauth-sheriff-core
```

**Failure Output** (build failed):
```toon
status: success
operation: execute
exit_code: 1
duration_ms: 12340
log_file: .plan/temp/build-20250115-103045.log
command_executed: ./mvnw clean test
```

Note: `status: success` means the script ran successfully; `exit_code: 1` means the build failed.

**Error Output** (script error):
```toon
status: error
operation: execute
error: Maven wrapper not found
context: Neither ./mvnw nor mvn available
```

---

### parse

Parse build output and categorize issues.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven parse \
    --log <path-to-log-file> \
    [--mode MODE]
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `--log` | Yes | Path to build log file |
| `--mode` | No | Output mode: default, errors, structured, no-openrewrite |

**Success Output (structured mode)**:
```toon
status: success
build_status: FAILURE
total_issues: 3

summary{category,count}:
compilation_error	1
test_failure	1
javadoc_warning	1

issues[3]{type,file,line,message}:
compilation_error	src/Main.java	45	cannot find symbol
test_failure	src/test/MainTest.java	23	expected true but was false
javadoc_warning	src/Utils.java	12	missing @param tag
```

---

### find-module

Find Maven module path from artifactId.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven find-module \
    --artifact-id ARTIFACT_ID
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `--artifact-id` | Yes* | ArtifactId to search for |
| `--module-path` | Yes* | Explicit module path to validate |

*One of `--artifact-id` or `--module-path` required.

**Success Output**:
```toon
status: success
artifact_id: oauth-sheriff-core
module_path: oauth-sheriff-core
pom_file: oauth-sheriff-core/pom.xml
maven_pl_argument: -pl oauth-sheriff-core
```

**Ambiguous Output**:
```toon
status: error
error: Ambiguous artifact ID
artifact_id: auth-service
context: Multiple modules found

choices[2]{path}:
services/auth-service
legacy/auth-service
```

---

### search-markers

Search for OpenRewrite TODO markers in source code.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven search-markers \
    [--source-dir SRC] \
    [--extensions EXT]
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `--source-dir` | No | Directory to search (default: src) |
| `--extensions` | No | File extensions (default: .java) |

**Success Output**:
```toon
status: success
total_markers: 5
files_affected: 3
auto_suppress_count: 3
ask_user_count: 2

by_recipe{recipe,count}:
CuiLogRecordPatternRecipe	2
InvalidExceptionUsageRecipe	1
SomeOtherRecipe	2

markers[5]{file,line,recipe,category}:
src/Main.java	45	CuiLogRecordPatternRecipe	auto_suppress
src/Utils.java	23	SomeOtherRecipe	ask_user
```

---

### check-warnings

Categorize build warnings against acceptable patterns.

**Command**:
```bash
python3 .plan/execute-script.py plan-marshall:build-operations:maven check-warnings \
    --warnings '<json>' \
    [--acceptable-warnings '<json>']
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `--warnings` | Yes | JSON array of warning objects |
| `--acceptable-warnings` | No | JSON object with acceptable patterns |

**Success Output**:
```toon
status: success
total: 15
acceptable: 3
fixable: 10
unknown: 2

by_category{category,count}:
acceptable	3
fixable	10
unknown	2
```

---

## Exit Codes

| Code | Meaning | Output Stream |
|------|---------|---------------|
| 0 | Success | stdout |
| 1 | Error | stderr |

---

## Error Format

All errors follow the same TOON structure:

```toon
status: error
operation: <operation_name>
error: <error_message>
context: <additional_context>
```

**Common Error Types**:

| Error | Context |
|-------|---------|
| No build system detected | No pom.xml, build.gradle, or package.json found |
| Maven wrapper not found | Neither ./mvnw nor mvn available |
| Module not found | No pom.xml found at specified path |
| Build timeout | Exceeded timeout of 300s |
| Parse error | Invalid log file format |

---

## Marshal.json Modules Structure

After `persist` command, marshal.json contains:

```json
{
  "modules": {
    "default": {
      "path": ".",
      "domains": ["java"],
      "build_systems": ["maven"],
      "commands": {
        "test-compile": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"test-compile\"",
        "test": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\"",
        "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\"",
        "install": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean install\"",
        "pre-commit": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean install\" --profile pre-commit"
      }
    },
    "oauth-sheriff-core": {
      "path": "oauth-sheriff-core",
      "domains": ["java"],
      "build_systems": ["maven"],
      "commands": {
        "test": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean test\" --module oauth-sheriff-core",
        "verify": "python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals \"clean verify\" --module oauth-sheriff-core"
      }
    }
  },
  "build_systems": [...]
}
```

---

## Run-Configuration.json Build Structure

Local machine-specific configuration:

```json
{
  "build": {
    "available_systems": "maven,npm",
    "default_system": "maven"
  },
  "commands": {
    "build:default:test": {
      "timeout_seconds": 180
    },
    "build:oauth-sheriff-core:verify": {
      "timeout_seconds": 240
    }
  }
}
```

---

## Standard Command Labels

| Label | Maven Goals | Gradle Tasks | npm Scripts |
|-------|-------------|--------------|-------------|
| `test-compile` | `test-compile` | `testClasses` | - |
| `test` | `clean test` | `clean test` | `run test` |
| `verify` | `clean verify` | `clean check` | `run test && run lint` |
| `install` | `clean install` | `publishToMavenLocal` | - |
| `pre-commit` | `clean install` | `preCommit` | - |
| `coverage` | `clean verify` | `jacocoTestReport` | `run test:coverage` |
| `integration` | `clean verify -Pintegration-tests` | `integrationTest` | `run test:integration` |

Profile mappings (added via `--profile` flag):
- `pre-commit` label uses `--profile pre-commit`
- `coverage` label uses `--profile coverage`
- `integration` label uses `--profile integration-tests`
