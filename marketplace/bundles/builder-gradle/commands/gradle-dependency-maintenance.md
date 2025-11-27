---
description: Orchestrate Gradle dependency maintenance workflows for dependency analysis, optimization, and quality verification
allowed_tools:
  - Skill
  - SlashCommand
  - Read
  - Grep
  - Glob
---

# /gradle-dependency-maintenance Command

Orchestrate Gradle dependency maintenance workflows including dependency analysis, version catalog management, and quality verification.

## Parameters

| Parameter | Default | Type | Description |
|-----------|---------|------|-------------|
| `action` | `analyze` | enum | Workflow: `analyze`, `optimize`, `catalog`, `wrapper`, `verify` |
| `project` | none | string | Specific subproject to target |
| `auto_fix` | `true` | boolean | Auto-fix safe issues (optimize action) |

## Actions

### action=analyze

Analyze dependency issues in Gradle build files.

```
Skill: builder-gradle:builder-gradle-dependencies
Workflow: Analyze Dependency Issues
Parameters:
  project: {project}
  scope: all
```

**Output**:
```json
{
  "unused_dependencies": [...],
  "undeclared_dependencies": [...],
  "hardcoded_versions": [...],
  "catalog_violations": [...],
  "scope_issues": [...]
}
```

### action=optimize

Apply fixes from analysis results.

```
Skill: builder-gradle:builder-gradle-dependencies
Workflow: Optimize Dependencies
Parameters:
  issues: {issues from analyze}
  auto_fix: {auto_fix}
```

**Safe to auto-fix**:
- Move hardcoded versions to version catalog
- Remove unused dependencies (with verification)
- Fix obvious scope issues (testImplementation)

**Requires user confirmation**:
- Version catalog restructuring
- Scope changes affecting runtime
- Dependency removal in api configuration

### action=catalog

Manage version catalog (libs.versions.toml).

```
Skill: builder-gradle:builder-gradle-dependencies
Workflow: Manage Version Catalog
Parameters:
  project: {project}
```

**Operations**:
- Extract hardcoded versions to catalog
- Organize catalog sections
- Update dependency references

### action=wrapper

Update Gradle wrapper to latest version.

```
Skill: builder-gradle:builder-gradle-dependencies
Workflow: Update Gradle Wrapper
Parameters:
  version: {version or latest}
```

**Steps**:
1. Check current version: `./gradlew --version`
2. Update wrapper: `./gradlew wrapper --gradle-version={version}`
3. Verify: `./gradlew --version && ./gradlew build`

### action=verify

Run quality gate checks on build configuration.

```
Skill: builder-gradle:builder-gradle-dependencies
Workflow: Verify Build Quality
Parameters:
  project: {project}
```

**Validation Pipeline**:
1. Clean build: `./gradlew clean build`
2. Dependency analysis: `./gradlew dependencies`
3. Dependency insight: `./gradlew dependencyInsight`
4. Build scan: `./gradlew build --scan` (if available)

## Workflow

### Step 1: Parse Parameters

Map user intent to action:
- "check dependencies" → `analyze`
- "fix dependencies" → `optimize`
- "update catalog" → `catalog`
- "update wrapper" → `wrapper`
- "verify build" → `verify`

### Step 2: Delegate to Skill

Route to `builder-gradle:builder-gradle-dependencies` with appropriate workflow.

### Step 3: Report Results

Format output based on action type.

## Typical Full Workflow

```bash
# 1. Update Gradle wrapper
/gradle-dependency-maintenance action=wrapper

# 2. Analyze dependencies
/gradle-dependency-maintenance action=analyze

# 3. Optimize (apply fixes)
/gradle-dependency-maintenance action=optimize

# 4. Update version catalog
/gradle-dependency-maintenance action=catalog

# 5. Verify quality
/gradle-dependency-maintenance action=verify
```

## Example Usage

```bash
# Analyze all dependencies
/gradle-dependency-maintenance

# Analyze specific subproject
/gradle-dependency-maintenance action=analyze project=":core"

# Optimize with auto-fix disabled
/gradle-dependency-maintenance action=optimize auto_fix=false

# Update Gradle wrapper
/gradle-dependency-maintenance action=wrapper

# Full verification
/gradle-dependency-maintenance action=verify
```
