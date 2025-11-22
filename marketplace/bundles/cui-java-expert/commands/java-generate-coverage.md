---
name: java-generate-coverage
description: Generate coverage with Maven and analyze results (self-contained command)
---

# Java Coverage Report Command

Thin orchestrator that generates JaCoCo coverage reports using maven-builder agent and analyzes results using cui-java-unit-testing skill workflow.

## Parameters

- **threshold** (optional): Coverage threshold percentage (default: 80)
- **module** (optional): Specific module to analyze (default: all)

## Workflow

### Step 1: Load Testing Skill

```
Skill: cui-java-expert:cui-java-unit-testing
```

### Step 2: Generate Coverage

```
Task:
  subagent_type: cui-maven:maven-builder
  description: Generate coverage
  prompt: |
    Execute Maven build with goals: clean test -Pcoverage

    Generate JaCoCo coverage reports.
```

### Step 3: Analyze Coverage

Execute workflow: Analyze Coverage
- report_path: target/site/jacoco/jacoco.xml
- threshold: {threshold}

Or run script directly:
```bash
{baseDir}/scripts/analyze-coverage.py --file target/site/jacoco/jacoco.xml --threshold {threshold}
```

### Step 4: Generate Report

```
╔════════════════════════════════════════════════════════════╗
║              Coverage Analysis Report                      ║
╚════════════════════════════════════════════════════════════╝

Build Status: {build_status}

Overall Coverage:
- Line Coverage: {line_coverage}% {status_emoji}
- Branch Coverage: {branch_coverage}% {status_emoji}
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
- Invokes maven-builder agent for coverage generation
- Delegates analysis to cui-java-unit-testing skill workflow
- No business logic in command

```
/java-generate-coverage
  ├─> Task(maven-builder) [generates coverage]
  └─> Skill(cui-java-unit-testing) workflow: Analyze Coverage
```

## Usage

```
/java-generate-coverage
/java-generate-coverage threshold=90
```

## Related

- `cui-java-unit-testing` skill - Coverage analysis workflow
- `maven-builder` agent - Coverage generation
