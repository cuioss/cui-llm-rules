---
name: java-generate-coverage
description: Generate coverage with Maven and analyze results (self-contained command)
---

# Java Coverage Report Command

Thin orchestrator that generates JaCoCo coverage reports and analyzes results using cui-java-unit-testing skill workflow.

## Parameters

- **threshold** (optional): Coverage threshold percentage (default: 80)
- **module** (optional): Specific module to analyze (default: all)

## Workflow

### Step 1: Load Testing Skill

```
Skill: cui-java-expert:cui-java-unit-testing
```

### Step 2: Generate Coverage

**Execute Maven coverage build:**
```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean test -Pcoverage
  module: {module if specified}
  output_mode: structured
```

### Step 3: Analyze Coverage

Execute workflow: Analyze Coverage
- report_path: target/site/jacoco/jacoco.xml
- threshold: {threshold}

Or run script directly:
```bash
python3 scripts/analyze-coverage.py --file target/site/jacoco/jacoco.xml --threshold {threshold}
```

### Step 4: Generate Report

```
COVERAGE ANALYSIS REPORT

Build Status: {build_status}

Overall Coverage:
- Line Coverage: {line_coverage}%
- Branch Coverage: {branch_coverage}%
- Method Coverage: {method_coverage}%

Threshold: {threshold}%
Status: {PASS|FAIL}

Low Coverage Classes:
{list of classes below threshold}

Next Steps:
{recommendations based on results}
```

## Architecture

**Pattern**: Thin Orchestrator Command (<100 lines)
- Uses cui-maven-rules skill for Maven execution
- Delegates analysis to cui-java-unit-testing skill workflow
- No business logic in command

```
/java-generate-coverage
  ├─> Skill(cui-maven:cui-maven-rules) workflow: Execute Maven Build
  └─> Skill(cui-java-unit-testing) workflow: Analyze Coverage
```

## Usage

```
/java-generate-coverage
/java-generate-coverage threshold=90
```

## Related

- `cui-java-unit-testing` skill - Coverage analysis workflow
- `cui-maven:cui-maven-rules` skill - Maven standards (optional for output parsing)
