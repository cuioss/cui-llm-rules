---
name: javascript-implement-tests
description: Self-contained command for JavaScript test implementation with verification and iteration
---

# JavaScript Implement Tests Command

Self-contained command that orchestrates test implementation through test creation and test execution verification workflow.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=javascript-implement-tests update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **files** - Fully qualified path(s) of file(s) to be tested
- **description** - Detailed description of what aspects/behaviors to test
- **workspace** - (Optional) Workspace name for monorepo projects

## WORKFLOW

### Step 1: Verify Build and Test Precondition

```
Task: npm-builder
Parameters:
- command: run test
- outputMode: DEFAULT
- workspace: {if specified}

Verify all existing tests pass before adding new ones.
```

### Step 2: Implement Tests

```
Task: javascript-test-implementer
Parameters:
- files: {files}
- description: {description}
- workspace: {workspace}

Implement Jest/Vitest tests following CUI standards.
```

### Step 3: Execute Tests

```
Task: npm-builder
Parameters:
- command: run test
- outputMode: STRUCTURED
- workspace: {if specified}

Run tests and analyze results.
```

### Step 4: Iterative Fix (if test failures)

**Categorize failures:**
- test_bug: Test implementation issue → Fix test
- production_bug: Code under test issue → Report to user

**Fix test bugs** (max 5 iterations):
```
Task: javascript-test-implementer
Fix test implementation issues found.
```

**Report production bugs** (do not fix):
```
PRODUCTION CODE ISSUES DETECTED

Test implementation complete but production code has bugs:
{list of production issues with details}

Tests will pass once production code fixed.
```

### Step 5: Return Results

Success or partial success with production bugs identified.

## RELATED

- `javascript-test-implementer` - Implements tests (Layer 3)
- `npm-builder` - Executes tests (Layer 3)
