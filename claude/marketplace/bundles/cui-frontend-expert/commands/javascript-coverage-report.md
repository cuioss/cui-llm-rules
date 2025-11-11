---
name: javascript-coverage-report
description: Self-contained command for coverage generation and analysis
---

# JavaScript Coverage Report Command

Self-contained command that generates test coverage reports and analyzes results.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=javascript-coverage-report update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **files** - (Optional) Specific files to check coverage for
- **workspace** - (Optional) Workspace name for monorepo projects

## WORKFLOW

### Step 1: Generate Coverage

```
Task: npm-builder
Parameters:
- command: run test:coverage  (or run test -- --coverage)
- outputMode: FILE
- workspace: {if specified}

Generate coverage reports in coverage/ directory.
```

### Step 2: Analyze Coverage

```
Task: javascript-coverage-analyzer
Analyze existing coverage reports in coverage/ directory.
Return structured coverage data.
```

### Step 3: Return Coverage Results

```json
{
  "overall_coverage": {
    "line_coverage": 87.3,
    "branch_coverage": 82.1
  },
  "low_coverage_files": [...],
  "summary": {...}
}
```

## RELATED

- `npm-builder` - Generates coverage (Layer 3)
- `javascript-coverage-analyzer` - Analyzes reports (Layer 3)
