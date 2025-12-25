---
name: build-operations
description: npm and npx build execution with output parsing, error categorization, and warning handling
allowed-tools: [Bash, Read]
---

# JavaScript Build Operations

Build execution and output parsing for npm/npx-based JavaScript projects.

## Script Invocation

All scripts are invoked via the executor:

```
python3 .plan/execute-script.py pm-dev-frontend:build-operations:{script} {subcommand} {args}
```

## npm Operations

### run (Primary API)

Unified command that executes build and returns parsed output on failure.

```bash
python3 .plan/execute-script.py pm-dev-frontend:build-operations:npm run \
    --targets "<command>" \
    [--workspace <name>] \
    [--working-dir <path>] \
    [--env "NODE_ENV=production"] \
    [--timeout <ms>] \
    [--mode <mode>]
```

**Parameters**:
- `--targets` - npm/npx command to execute (required)
- `--workspace` - Workspace name for monorepo projects
- `--working-dir` - Working directory for command execution
- `--env` - Environment variables (e.g., 'NODE_ENV=test CI=true')
- `--timeout` - Timeout in milliseconds (default: 120000)
- `--mode` - Output mode: actionable (default), structured, errors

**Output Format (TOON)**:

Success:
```
status: success
log_file: target/npm-output-2025-01-15-143022.log
exit_code: 0
duration_seconds: 5
command_executed: npm run build
```

Build Failed (includes parsed errors):
```
status: error
error: build_failed
log_file: target/npm-output-2025-01-15-143022.log
exit_code: 1
duration_seconds: 3
command_executed: npm run build

errors[2]{file,line,message,category}:
src/index.js    42    SyntaxError: Unexpected token       compilation_error
src/utils.js    15    TypeError: Cannot read property     compilation_error
```

### execute (Low-level)

Execute npm/npx commands, return log file reference only.

```bash
python3 .plan/execute-script.py pm-dev-frontend:build-operations:npm execute \
  --command "run build" \
  [--workspace <name>] \
  [--working-dir <path>] \
  [--env "NODE_ENV=production"] \
  [--timeout 120000]
```

### parse (Low-level)

Parse build output from log file.

```bash
python3 .plan/execute-script.py pm-dev-frontend:build-operations:npm parse \
  --log target/npm-output-*.log \
  [--mode structured|errors|default]
```

## Output Modes

- **actionable** (default) - Errors + warnings NOT in acceptable_warnings
- **structured** - All errors + all warnings
- **errors** - Only errors, compact format

## JSON Output Format (execute/parse)

Low-level commands return structured JSON:

```json
{
  "status": "success|error",
  "data": {
    "log_file": "target/npm-output-2025-01-15-143022.log",
    "exit_code": 0,
    "duration_ms": 5432,
    "command_executed": "npm run build"
  }
}
```

## Error Categories

The parser categorizes issues into:

| Category | Description |
|----------|-------------|
| `compilation_error` | SyntaxError, TypeError, ReferenceError, TypeScript errors |
| `test_failure` | Jest/Vitest test failures, assertion errors |
| `lint_error` | ESLint, Prettier, StyleLint violations |
| `dependency_error` | Module not found, npm 404, ERESOLVE |
| `playwright_error` | Browser automation failures, timeouts |

## Command Type Detection

The script automatically detects whether to use `npm` or `npx` based on the command:

- **npx**: playwright, eslint, prettier, stylelint, tsc, jest, vitest
- **npm**: All other commands (run, install, test, etc.)

## Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| `build_failed` | Non-zero exit code | Errors included in response |
| `timeout` | Exceeded timeout | Increase timeout, check log_file |
| `execution_failed` | Process couldn't start | Check npm/node installed |
| `log_file_creation_failed` | Can't create log | Check permissions |

## Warning Handling

Warnings are filtered via acceptable_warnings in run-configuration.json:

```json
{
  "npm": {
    "acceptable_warnings": {
      "transitive_dependency": ["peer dep warning ..."],
      "deprecation": ["npm WARN deprecated ..."],
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
    --pattern "peer dep warning ..." \
    --build-system npm

# List accepted warnings
python3 .plan/execute-script.py plan-marshall:run-config:run_config warning list
```

## Integration

### With plan-marshall:build-operations

This bundle provides execution scripts registered via `extension.py`:

```python
# skills/plan-marshall-plugin/extension.py
def provides_build_systems() -> list:
    return ['npm']

def get_command_mappings() -> dict:
    return {
        'module-tests': 'python3 .plan/execute-script.py pm-dev-frontend:build-operations:npm run --targets "run test"',
        ...
    }
```

### With run-config

- Warning filtering via `acceptable_warnings`
- Build system-specific warning categories

## References

- `plan-marshall:build-operations` - Central detection and extension discovery
- `plan-marshall:build-operations/standards/api-contract.md` - Shared TOON output format
- `plan-marshall:build-operations/standards/canonical-vocabulary.md` - Canonical command names
- `standards/npm-impl.md` - npm execution and parsing details
