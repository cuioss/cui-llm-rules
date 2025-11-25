---
name: cui-pom-maintenance
description: POM maintenance standards and workflows for dependency management, BOM optimization, and scope analysis
allowed-tools: Read, Grep, Bash(./mvnw:*), Skill
---

# CUI POM Maintenance Skill

Standards and workflows for maintaining Maven POM files including dependency management, BOM utilization, scope optimization, and quality verification.

## What This Skill Provides

### POM Standards
- BOM (Bill of Materials) structure and usage rules
- Dependency management patterns
- Property naming conventions
- Scope assignment guidelines

### Maintenance Workflows
- Analyze: Identify POM issues and improvement opportunities
- Optimize: Apply BOM consolidation and scope fixes
- Verify: Validate POM quality through build verification

## When to Activate

Activate when:
- Maintaining POM files (dependencies, BOMs, scopes)
- Analyzing dependency structure
- Consolidating dependency management
- Optimizing dependency scopes
- Running OpenRewrite POM cleanup

## Standards Reference

**Load on-demand based on task:**

```
Read standards/pom-standards.md
```

Contains:
- BOM structure requirements
- Property naming conventions
- Scope assignment rules
- Dependency aggregation criteria

---

## Workflow: Analyze POM Issues

**Pattern**: Pattern 3 (Search-Analyze-Report)

Analyzes POM files for issues and improvement opportunities.

### When to Use

- Before starting POM maintenance
- To identify dependency issues
- To audit BOM usage

### Parameters

- **module** (optional): Specific module to analyze
- **scope** (optional): Analysis scope - `dependencies`, `bom`, `scopes`, `all` (default: `all`)

### Step 1: Run Dependency Analysis

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: dependency:analyze
  module: {module}
  output_mode: structured
```

### Step 2: Run Dependency Tree

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: dependency:tree
  module: {module}
  output_mode: default
```

### Step 3: Analyze BOM Usage

Use Grep to find:
- Modules not importing project BOM
- Hardcoded versions outside BOM
- Version overrides in child modules

```
Grep: <version>[0-9] in **/pom.xml (excluding parent BOM)
```

### Step 4: Report Findings

Return structured report:
```json
{
  "unused_dependencies": [...],
  "undeclared_dependencies": [...],
  "hardcoded_versions": [...],
  "bom_violations": [...],
  "scope_issues": [...]
}
```

---

## Workflow: Optimize Dependencies

**Pattern**: Pattern 2 (Read-Process-Write)

Applies dependency optimizations based on analysis results.

### When to Use

- After Analyze workflow identifies issues
- To consolidate BOM usage
- To fix scope assignments

### Parameters

- **issues** (required): Issues from Analyze workflow
- **auto_fix** (optional): Auto-fix safe issues (default: false)

### Step 1: Load Standards

```
Read standards/pom-standards.md
```

### Step 2: Categorize Issues

**Safe to auto-fix:**
- Move hardcoded versions to properties
- Remove unused dependencies (with verification)
- Fix obvious scope issues (test dependencies)

**Requires user confirmation:**
- BOM restructuring
- Scope changes affecting runtime
- Dependency removal

### Step 3: Apply Fixes

For each safe fix:
1. Edit POM file
2. Verify with incremental build

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: compile
  module: {affected_module}
```

### Step 4: Report Changes

Return:
```json
{
  "fixed": [...],
  "requires_confirmation": [...],
  "skipped": [...]
}
```

---

## Workflow: Run OpenRewrite Cleanup

**Pattern**: Pattern 4 (Command Chain Execution)

Executes OpenRewrite POM cleanup recipes.

### When to Use

- Before manual POM maintenance
- To standardize POM structure
- To apply automated fixes

### Parameters

- **dry_run** (optional): Preview changes only (default: false)
- **module** (optional): Specific module

### Step 1: Execute OpenRewrite

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: rewrite:run
  profile: rewrite-maven-clean
  module: {module}
```

If dry_run=true, use `rewrite:dryRun` instead.

### Step 2: Parse Results

Check for:
- Files modified
- Recipes applied
- Errors encountered

### Step 3: Verify Build

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean verify
  module: {module}
```

### Step 4: Report

Return:
```json
{
  "files_modified": [...],
  "recipes_applied": [...],
  "build_status": "SUCCESS|FAILURE"
}
```

---

## Workflow: Update Maven Wrapper

**Pattern**: Pattern 4 (Command Chain Execution)

Updates Maven wrapper to latest version.

### When to Use

- Before major POM maintenance
- When wrapper is outdated
- To standardize Maven version

### Parameters

- **version** (optional): Specific Maven version (default: latest)

### Step 1: Check Current Version

```bash
./mvnw --version
```

### Step 2: Update Wrapper

```bash
./mvnw wrapper:wrapper -Dmaven={version}
```

### Step 3: Verify Update

```bash
./mvnw --version
./mvnw clean verify
```

### Step 4: Report

Return:
```json
{
  "previous_version": "...",
  "new_version": "...",
  "build_status": "SUCCESS|FAILURE"
}
```

---

## Workflow: Verify POM Quality

**Pattern**: Pattern 9 (Validation Pipeline)

Validates POM quality through multiple checks.

### When to Use

- After POM maintenance
- Before committing changes
- As quality gate

### Parameters

- **module** (optional): Specific module to verify

### Step 1: Clean Build

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean install
  module: {module}
```

### Step 2: Dependency Analysis

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: dependency:analyze
  module: {module}
```

### Step 3: Enforcer Check

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: enforcer:enforce
  module: {module}
```

### Step 4: OpenRewrite Validation

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: rewrite:dryRun
  profile: rewrite-maven-clean
  module: {module}
```

### Step 5: Return Quality Report

```json
{
  "build": "PASS|FAIL",
  "dependency_analysis": "PASS|FAIL",
  "enforcer": "PASS|FAIL",
  "openrewrite": "PASS|FAIL",
  "overall": "PASS|FAIL",
  "issues": [...]
}
```

---

## Integration

### With cui-maven-rules Skill

All Maven executions delegate to `cui-maven:cui-maven-rules`:
- Build execution
- Output parsing
- Error categorization

### With maven-pom-maintenance Command

The `/maven-pom-maintenance` command orchestrates these workflows:
- Parses user intent
- Selects appropriate workflow
- Reports results

## Tool Access

- **Read**: Load standards
- **Grep**: Search POM patterns
- **Bash(./mvnw:*)**: Direct wrapper commands (version check only)
- **Skill**: Delegate to cui-maven-rules

## Related

- Skill: `cui-maven:cui-maven-rules` - Maven build execution
- Command: `/maven-pom-maintenance` - POM maintenance orchestration
- Standards: `standards/pom-standards.md` - POM quality standards
