---
name: cui-orchestrate-js-task
description: Implements JavaScript tasks end-to-end with automated testing and coverage verification
---

# CUI JavaScript Task Manager Command

Orchestrates complete JavaScript task implementation through code creation, unit testing, and coverage verification workflow.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-orchestrate-js-task update="[your improvement]"` with:
1. Task breakdown patterns - How to decompose JavaScript tasks into implementation + testing phases, recognizing when components need separate test utilities or fixtures
2. Implementation strategy refinement - Best practices for handling async code, module imports, external dependencies, framework-specific patterns (Vue, React, etc.)
3. Test implementation approaches - Unit test patterns for JavaScript, mocking strategies, fixture setup efficiency, achieving meaningful coverage vs line coverage
4. Coverage verification patterns - Understanding coverage thresholds by file type, identifying false coverage, recognizing when integration tests are needed vs unit tests
5. Any lessons learned about JavaScript tooling patterns, common implementation mistakes, test framework quirks, or iteration efficiency improvements

This ensures the command evolves to handle increasingly complex JavaScript tasks with better technical accuracy and more efficient testing strategies.

## PARAMETERS

- **files** - File(s), component(s), or name(s) of file(s) to implement/create
- **description** - Detailed, precise description of what to implement
- **workspace** - (Optional) Workspace name for monorepo projects

## WORKFLOW

### Step 1: Determine Entry Point

Analyze `description` parameter:
- Contains "implement", "create", "add feature" → Start at Step 2 (Implementation)
- Contains "test", "unit test", "jest" → Start at Step 3 (Testing)
- Contains "coverage", "verify coverage" → Start at Step 4 (Coverage)

### Step 2: Implementation Phase

```
SlashCommand: /cui-frontend-expert:cui-js-implement-code
Parameters:
- files: {files}
- description: {description}
- workspace: {workspace}

Self-contained command handles implementation + verification + iteration.
```

**On success**: Continue to Step 3
**On error**: Handle and potentially retry

### Step 3: Unit Testing Phase

```
SlashCommand: /cui-frontend-expert:cui-js-implement-tests
Parameters:
- files: {files}
- description: Implement unit tests for {files}
- workspace: {workspace}

Self-contained command handles test implementation + verification.
```

**On success**: Continue to Step 4
**On error indicating production issue**: Return to Step 2 with fix description

### Step 4: Coverage Verification Phase

```
SlashCommand: /cui-frontend-expert:cui-js-generate-coverage
Parameters:
- files: {files}
- workspace: {workspace}

Generate and analyze coverage.
```

**On insufficient coverage**:
- Return to Step 3 with description: "Add tests for {uncovered areas}"
- Process sequentially

**On sufficient coverage**: Workflow complete

### Step 5: Iterative Refinement

Continue cycling through Steps 2-4 until:
- All coverage reports show sufficient coverage
- No production or test errors remain

**Maximum iterations**: 5 cycles

## STATISTICS TRACKING

- `implementation_retries`
- `test_retries`
- `coverage_fixes`
- `total_cycles`

## USAGE EXAMPLES

**Full implementation:**
```
/cui-orchestrate-js-task files="src/services/auth.js" description="Implement user authentication with JWT tokens" workspace="packages/core"
```

**Testing existing code:**
```
/cui-orchestrate-js-task files="src/utils/formatter.js" description="Implement unit tests for formatter utilities"
```

## RELATED

- `/cui-js-implement-code` - Self-contained implementation command (Layer 2)
- `/cui-js-implement-tests` - Self-contained test command (Layer 2)
- `/cui-js-generate-coverage` - Coverage generation/analysis (Layer 2)
