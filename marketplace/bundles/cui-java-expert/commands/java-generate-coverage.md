---
name: java-generate-coverage
description: Generate coverage with Maven and analyze results (self-contained command)
---

# Java Coverage Report Command

Self-contained command that generates JaCoCo coverage reports using maven-builder and analyzes results using java-coverage-analyzer.

## CONTINUOUS IMPROVEMENT RULE

**This command should be improved using**: `/plugin-update-command cui-java-generate-coverage`

**Improvement areas**:
- Enhanced report parsing for multi-module project coverage aggregation
- Better visualization of coverage trends across modules
- Improved low-coverage detection with historical comparison
- Expanded analysis of uncovered critical paths and business logic
- Advanced filtering and threshold customization per module type

## WORKFLOW

### Step 1: Generate Coverage

```
Task:
  subagent_type: maven-builder
  description: Generate coverage
  prompt: |
    Execute Maven build with goals: clean test -Pcoverage

    Generate JaCoCo coverage reports.
```

### Step 2: Analyze Coverage

```
Task:
  subagent_type: java-coverage-analyzer
  description: Analyze coverage reports
  prompt: |
    Analyze JaCoCo coverage reports in target/site/jacoco/

    Return structured coverage data.
```

### Step 3: Return Results

Return combined results from maven-builder and java-coverage-analyzer.

## CRITICAL RULES

- **Self-Contained**: Generates AND analyzes coverage
- **Uses Task**: Invokes agents (maven-builder, java-coverage-analyzer)
- **No SlashCommand**: Single-item focus, no command delegation

## USAGE

```
/java-generate-coverage
```

## ARCHITECTURE

```
/java-generate-coverage
  ├─> Task(maven-builder) [generates coverage]
  └─> Task(java-coverage-analyzer) [analyzes reports]
```

## RELATED

- `maven-builder` - Coverage generation (Layer 3)
- `java-coverage-analyzer` - Report analysis (Layer 3)
