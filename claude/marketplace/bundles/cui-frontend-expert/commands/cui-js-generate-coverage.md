---
name: cui-js-generate-coverage
description: Self-contained command for coverage generation and analysis
---

# JavaScript Coverage Report Command

Self-contained command that generates test coverage reports and analyzes results.

## CONTINUOUS IMPROVEMENT RULE

**This command should be improved using**: `/cui-update-command cui-js-generate-coverage`

**Improvement areas**:
- Enhanced report parsing for different test frameworks (Jest, Vitest, Mocha)
- Better monorepo workspace coverage aggregation
- Improved low-coverage detection with component-specific thresholds
- Expanded analysis of uncovered user interaction paths
- Advanced filtering by file patterns and module boundaries

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
