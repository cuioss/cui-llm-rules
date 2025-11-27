# CUI npm Build Rules

Build execution and output parsing skill for npm/npx commands in CUI JavaScript projects.

## Purpose

This skill provides centralized npm/npx build execution logic, similar to how `builder-maven-rules` handles Maven builds. It handles:

- Atomic build execution with automatic log file management
- npm vs npx command detection
- Workspace targeting for monorepos
- Output parsing and error categorization
- Issue routing to fix commands

## Architecture

This skill follows the same pattern as `builder-maven:builder-maven-rules`:

```
npm-builder agent (Layer 3)
  ├─> Detects project structure
  ├─> Validates workspace configuration
  └─> Delegates to cui-npm-rules skill

cui-npm-rules skill
  ├─> execute-npm-build.py - Atomic build execution
  ├─> parse-npm-output.py - Output parsing and categorization
  └─> standards/npm-build-execution.md - Build standards
```

## Usage

### From Commands

```
Skill: cui-frontend-expert:cui-npm-rules
Workflow: Execute npm Build
Parameters:
  command: run test
  workspace: e-2-e-playwright
  output_mode: structured
```

### From Agents

The `npm-builder` agent automatically delegates to this skill:

```
Task:
  subagent_type: npm-builder
  description: Verify build
  prompt: |
    Execute npm build to verify implementation.

    Command: run test
    Workspace: e-2-e-playwright
    Output mode: STRUCTURED
```

## Workflows

### Execute npm Build

Executes npm/npx commands with full parameter support:

- Command construction (npm vs npx auto-detection)
- Workspace targeting
- Environment variable support
- Timeout management
- Log file capture

**Returns**: Structured JSON with exit code, log file path, duration, and command executed

### Parse npm Build Output

Parses existing build logs and categorizes issues:

- Compilation errors (SyntaxError, TypeError, etc.)
- Test failures (Jest, Vitest, Playwright)
- Lint errors (ESLint, Prettier, StyleLint)
- Dependency errors (module not found, npm 404)
- File location extraction

**Returns**: Categorized issue list with file locations for fix routing

## Scripts

### execute-npm-build.py

Atomic build execution script that handles:

- Timestamped log file generation
- Directory pre-creation
- npm vs npx detection
- Command construction with workspace/env support
- Timeout handling

**Usage:**
```bash
python3 execute-npm-build.py --command "run test"
python3 execute-npm-build.py --command "playwright test" --workspace e-2-e-playwright
python3 execute-npm-build.py --command "run build" --env "NODE_ENV=production"
```

### parse-npm-output.py

Output parsing script that categorizes issues:

**Usage:**
```bash
python3 parse-npm-output.py --log target/npm-output-2025-11-26.log
python3 parse-npm-output.py --log build.log --mode structured
python3 parse-npm-output.py --log test.log --mode errors
```

## Standards

### npm-build-execution.md

Comprehensive standards for:

- Command construction (npm vs npx)
- Workspace targeting
- Environment variables
- Log file management
- Timeout configuration
- Exit code interpretation
- Output parsing patterns
- File location extraction

## Integration

### Commands

This skill is used by:

- `/js-implement-code` - Build verification
- `/js-implement-tests` - Test verification
- `/js-enforce-eslint` - Lint execution
- `/js-generate-coverage` - Coverage generation

### Related Skills

- `cui-frontend-expert:cui-javascript-project` - Project structure and dependencies
- `cui-frontend-expert:cui-javascript-unit-testing` - Test standards
- `cui-frontend-expert:cui-javascript-linting` - Linting standards

## Comparison with Maven

| Aspect | builder-maven-rules | cui-npm-rules |
|--------|----------------|---------------|
| **Build tool** | ./mvnw | npm/npx |
| **Execution script** | execute-maven-build.py | execute-npm-build.py |
| **Parsing script** | parse-maven-output.py | parse-npm-output.py |
| **Agent** | maven-builder | npm-builder |
| **Module targeting** | -pl flag | --workspace flag |
| **Log location** | target/build-output-*.log | target/npm-output-*.log |
| **Default timeout** | 120000ms | 120000ms |

## Migration Notes

### From Direct npm Execution

**Before** (commands executing npm directly):
```bash
npm run test > target/npm-output.log 2>&1
python3 parse-npm-output.py --log target/npm-output.log
```

**After** (using skill):
```
Skill: cui-frontend-expert:cui-npm-rules
Workflow: Execute npm Build
Parameters:
  command: run test
  output_mode: structured
```

### From cui-javascript-project

The `parse-npm-output.py` script was moved from `cui-javascript-project` to `cui-npm-rules`. Update references:

**Before:**
```
Skill: cui-utilities:script-runner
Resolve: cui-frontend-expert:cui-javascript-project/scripts/parse-npm-output.py
```

**After:**
```
Skill: cui-frontend-expert:cui-npm-rules
Workflow: Parse npm Build Output
```
