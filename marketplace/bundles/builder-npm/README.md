# builder-npm Bundle

npm/npx build execution, output parsing, and issue routing for JavaScript projects.

## Overview

This bundle provides npm/npx build automation with automatic error categorization and issue routing. The API mirrors `builder-maven` and `builder-gradle` bundles for consistent usage.

## Components

### Agents

| Agent | Description |
|-------|-------------|
| `npm-builder` | Autonomous single-build execution with project detection |

### Skills

| Skill | Description |
|-------|-------------|
| `builder-npm:builder-npm-rules` | Build execution, output parsing, issue routing |

## Quick Start

### Basic Build

```bash
# From commands - use the skill workflow
Skill: builder-npm:builder-npm-rules
Workflow: Execute npm Build
Parameters:
  command: run test
  output_mode: structured
```

### With Workspace (Monorepo)

```bash
Skill: builder-npm:builder-npm-rules
Workflow: Execute npm Build
Parameters:
  command: run test
  workspace: e-2-e-playwright
  output_mode: structured
```

### Using the Agent

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

## API Comparison

The API is designed to be parallel to `builder-maven`:

| Maven | npm | Notes |
|-------|-----|-------|
| `/maven-build-and-fix` | (use skill directly) | Same pattern |
| `maven-builder` agent | `npm-builder` agent | Same behavior |
| `builder-maven:builder-maven-rules` | `builder-npm:builder-npm-rules` | Same workflows |

### Parameter Mapping

| Maven Parameter | npm Parameter |
|-----------------|---------------|
| `goals` | `command` |
| `module` | `workspace` |
| `skip_tests` | (use CI=true env) |

## Workflows

### Execute npm Build

1. Detect npm vs npx command type
2. Construct command with workspace/env parameters
3. Execute with log capture and timeout
4. Return structured JSON result

**Issue Routing**:
- `compilation_error` → `/js-implement-code`
- `test_failure` → `/js-implement-tests`
- `lint_error` → `/js-enforce-eslint`
- `dependency_error` → Report to user

### Parse npm Build Output

Parse existing log files and categorize issues for systematic fix orchestration.

## Scripts

| Script | Purpose |
|--------|---------|
| `execute-npm-build.py` | Execute npm/npx with log capture |
| `parse-npm-output.py` | Parse and categorize build output |

## Standards

- [npm Build Execution](skills/builder-npm-rules/standards/npm-build-execution.md)

## Requirements

- Node.js and npm installed
- package.json in project root
- Python 3.x for scripts

## Dependencies

This bundle integrates with:

- `cui-frontend-expert` - For JavaScript code fixes
- `cui-utilities` - For configuration management

## License

Apache-2.0
