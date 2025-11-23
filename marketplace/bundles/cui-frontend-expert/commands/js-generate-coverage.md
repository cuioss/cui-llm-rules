---
name: js-generate-coverage
description: Self-contained command for coverage generation and analysis
---

# JavaScript Coverage Report Command

Self-contained command that generates test coverage reports and analyzes results.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=js-generate-coverage update="[your improvement]"` with:

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

**Execute npm coverage command:**
```bash
npm run test:coverage > target/npm-coverage-output.log 2>&1
# Or with workspace:
npm run test:coverage --workspace={workspace} > target/npm-coverage-output.log 2>&1
```

**Parse build output (if needed):**
```bash
python3 skills/cui-javascript-project/scripts/parse-npm-output.py \
    --log target/npm-coverage-output.log --mode structured
```

This generates coverage reports in coverage/ directory.

### Step 2: Analyze Coverage

**Load skill and execute workflow:**
```
Skill: cui-frontend-expert:cui-javascript-unit-testing
Execute workflow: Analyze Coverage
```

Or run script directly:
```bash
python3 scripts/analyze-js-coverage.py --report coverage/coverage-summary.json
# Or for LCOV format:
python3 scripts/analyze-js-coverage.py --report coverage/lcov.info --format lcov
```

Script returns structured JSON with overall_coverage, by_file, and low_coverage_files.

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

- Skill: `cui-frontend-expert:cui-javascript-unit-testing` - Analyze Coverage workflow
- Skill: `cui-frontend-expert:cui-javascript-project` - Parse npm Build Output workflow
- Command: `/js-implement-tests` - Add tests for low-coverage areas
