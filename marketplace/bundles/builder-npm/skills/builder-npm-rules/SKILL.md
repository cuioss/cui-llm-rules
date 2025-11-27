---
name: builder-npm-rules
description: npm/npx build execution, output parsing, and issue routing for CUI JavaScript projects
allowed-tools:
  - Read
  - Grep
  - Bash(npm:*)
  - Bash(npx:*)
  - Bash(python3:*)
---

# Builder npm Build Rules

npm/npx build execution skill for CUI JavaScript projects. Handles build commands, output parsing, error categorization, and issue routing.

## What This Skill Provides

### Build Execution
- npm/npx command construction with workspace targeting
- Log capture and timestamped output
- Build timeout management
- Exit code and status determination
- Command detection (npm vs npx automatic selection)

### Output Parsing
- Compilation error extraction (SyntaxError, TypeError, ReferenceError)
- Test failure categorization (Jest, Vitest, Playwright)
- Lint error detection (ESLint, Prettier, StyleLint)
- Dependency error identification (module not found, npm 404)
- Playwright-specific error handling

### Issue Routing
- Categorized issue reports (JSON structured)
- Fix command recommendations
- File location extraction

## When to Activate

Activate when:
- Executing npm/npx builds
- Parsing npm build output
- Routing build issues to fix commands
- Running test suites or linting
- Building with workspace targeting (monorepos)

**For project structure and dependencies:**
```
Skill: cui-frontend-expert:cui-javascript-project
```

## Standards Reference

**Load for build execution context:**
```
Read standards/npm-build-execution.md
```

---

## Workflow: Execute npm Build

**Pattern**: Pattern 4 (Command Chain Execution)

This workflow executes npm/npx builds and returns structured results. Use this workflow whenever npm builds are needed.

### When to Use

Use this workflow when:
- Running npm scripts (test, build, lint, format)
- Executing npx commands (playwright, eslint, prettier)
- Building specific workspaces in monorepos
- Running with specific environment variables

### Parameters

- **command** (required): npm/npx command to execute (e.g., "run test", "run build", "playwright test")
- **workspace** (optional): Specific workspace package to target (--workspace flag)
- **working_dir** (optional): Working directory for command execution
- **env** (optional): Environment variables (e.g., "NODE_ENV=test CI=true")
- **timeout** (optional): Build timeout in milliseconds (default: 120000)
- **output_mode** (optional): How to process output - "default", "errors", "structured" (default: "structured")

### Step 1: Execute npm Build

Use `execute-npm-build.py` which handles log file pre-creation, timestamping, and npm/npx execution atomically:

```bash
python3 scripts/execute-npm-build.py \
    --command "{command}" \
    --workspace {workspace} \
    --env {env} \
    --timeout {timeout}
```

**Output**: JSON with `log_file`, `exit_code`, `duration_ms`, `command_executed`

**Examples:**
```bash
# Basic test run
python3 scripts/execute-npm-build.py --command "run test"

# Workspace-specific build
python3 scripts/execute-npm-build.py --command "run build" --workspace e-2-e-playwright

# Playwright tests with environment
python3 scripts/execute-npm-build.py --command "playwright test" --env "CI=true"

# Lint with extended timeout
python3 scripts/execute-npm-build.py --command "run lint" --timeout 180000
```

The script:
- Determines npm vs npx automatically based on command
- Generates timestamped log filename automatically
- Pre-creates log file (handles output correctly)
- Executes npm/npx and captures exit code
- Prints `[EXEC] <command>` to stderr for visibility
- Returns structured JSON result

### Step 2: Parse Build Output

```bash
python3 scripts/parse-npm-output.py \
    --log {log_file from step 1} \
    --mode {output_mode}
```

### Step 3: Return Results

Return structured JSON with:
- Build status (SUCCESS/FAILURE)
- Categorized issues (compilation_error, test_failure, lint_error, dependency_error, playwright_error, npm_error)
- Summary counts
- Metrics (duration, tests run/failed if applicable)

### Usage from Commands

Commands invoke this workflow as:
```
Skill: builder-npm:builder-npm-rules
Workflow: Execute npm Build
Parameters:
  command: run test
  workspace: e-2-e-playwright (optional)
  output_mode: structured (optional)
```

### Issue Routing

Based on returned issue categories, route to appropriate fix commands:

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/js-implement-code` |
| `test_failure` | `/js-implement-tests` |
| `lint_error` | `/js-enforce-eslint` |
| `dependency_error` | Manual package.json fix |
| `playwright_error` | `/js-implement-tests` |

---

## Workflow: Parse npm Build Output

**Pattern**: Pattern 4 (Command Chain Execution)

This workflow parses npm/npx build output logs and categorizes issues for systematic fix orchestration.

### When to Use

Use this workflow when:
- Analyzing npm build output for errors and warnings
- Categorizing build issues for orchestrated fixing
- Generating structured issue reports

### Step 1: Execute Script

**Parse the build log file:**

```bash
python3 scripts/parse-npm-output.py \
    --log <path-to-log-file> \
    --mode <output-mode>
```

**Output Modes:**
- `default` - Summary with all errors and warnings (human-readable)
- `errors` - Only errors (no warnings)
- `structured` - Full JSON output for machine processing

### Step 2: Process Results

**JSON Output Contract (structured mode):**

```json
{
  "status": "failure",
  "data": {
    "output_file": "target/npm-output-2024-01-15.log",
    "issues": [
      {
        "type": "lint_error",
        "file": "src/components/Button.js",
        "line": 15,
        "column": 3,
        "message": "'PropTypes' is defined but never used",
        "severity": "ERROR",
        "log_line": 45
      }
    ]
  },
  "metrics": {
    "compilation_errors": 0,
    "test_failures": 0,
    "lint_errors": 2,
    "dependency_errors": 0,
    "playwright_errors": 0,
    "npm_errors": 0,
    "total_errors": 5,
    "total_warnings": 3,
    "total_issues": 8
  }
}
```

### Step 3: Route to Appropriate Fix Commands

Based on issue category, delegate to appropriate commands:

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/js-implement-code` |
| `test_failure` | `/js-implement-tests` |
| `lint_error` | `/js-enforce-eslint` |
| `dependency_error` | Manual package.json fix |
| `playwright_error` | `/js-implement-tests` |

### Script Location

`scripts/parse-npm-output.py`

---

## Standards Organization

Standards in `standards/` directory:

- `npm-build-execution.md` - Build execution, command construction, workspace targeting, timeout management

## Tool Access

- **Read**: Load standards files
- **Grep**: Search patterns
- **Bash(npm:*)**: Execute npm commands
- **Bash(npx:*)**: Execute npx commands (Playwright, ESLint, etc.)
- **Bash(python3:*)**: Execute scripts:
  - `execute-npm-build.py` - Atomic build execution
  - `parse-npm-output.py` - Output parsing

## Integration

### Commands Using This Skill

- `/js-implement-code` - Code implementation with build verification
- `/js-implement-tests` - Test implementation with verification
- `/js-enforce-eslint` - ESLint enforcement
- `/js-generate-coverage` - Coverage generation

### Related Skills

- `cui-frontend-expert:cui-javascript-project` - Project structure and Maven integration
- `cui-frontend-expert:cui-jsdoc` - JSDoc standards
- `cui-frontend-expert:cui-javascript-unit-testing` - Test standards
- `cui-frontend-expert:cui-javascript-linting` - Linting standards
