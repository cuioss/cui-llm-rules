---
description: Gradle dependency maintenance, version catalog management, and build quality verification
allowed_tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Bash(./gradlew:*)
  - Skill
---

# builder-gradle-dependencies Skill

Dependency maintenance, version catalog management, and build quality verification for Gradle projects.

## Workflows

### Workflow 1: Analyze Dependency Issues

**Pattern**: Pattern 3 (Search-Analyze-Report)

**Parameters**:
- `project` (optional): Specific subproject to analyze
- `scope` (optional): Analysis scope - `dependencies`, `catalog`, `scopes`, `all` (default: `all`)

**Steps**:

1. **Run Dependency Analysis**:
   ```
   Skill: builder-gradle:builder-gradle-rules
   Workflow: Execute Gradle Build
   Parameters: tasks=dependencies, project, output_mode=structured
   ```

2. **Run Dependency Insight** (for conflicts):
   ```bash
   ./gradlew dependencyInsight --dependency {suspected_conflict}
   ```

3. **Analyze Version Catalog Usage**:
   - Check for `libs.versions.toml` presence
   - Grep: hardcoded versions in `build.gradle(.kts)` files
   - Pattern: `implementation\s*\(\s*["'].*:.*:.*["']\s*\)`

4. **Report Findings**:
```json
{
  "unused_dependencies": [...],
  "undeclared_dependencies": [...],
  "hardcoded_versions": [...],
  "catalog_violations": [...],
  "scope_issues": [...],
  "version_conflicts": [...]
}
```

---

### Workflow 2: Optimize Dependencies

**Pattern**: Pattern 2 (Read-Process-Write)

**Parameters**:
- `issues` (required): Issues from Analyze workflow
- `auto_fix` (optional): Auto-fix safe issues (default: true)

**Safe to Auto-Fix**:
- Move hardcoded versions to version catalog
- Remove unused dependencies (with verification)
- Fix obvious scope issues (testImplementation)
- Update dependency notation to use catalog references

**Requires User Confirmation**:
- Version catalog restructuring
- Scope changes affecting runtime (api → implementation)
- Dependency removal in api configuration
- Version constraint changes

**Process**:
1. Load `standards/gradle-dependencies.md`
2. Categorize issues (safe vs. requires confirmation)
3. Apply fixes with incremental build verification
4. Return categorized results

**Fix Patterns**:

**Hardcoded to Catalog**:
```kotlin
// Before
implementation("com.example:lib:1.2.3")

// After (in build.gradle.kts)
implementation(libs.example.lib)

// In libs.versions.toml
[libraries]
example-lib = "com.example:lib:1.2.3"
```

**Scope Correction**:
```kotlin
// Before
implementation("org.junit.jupiter:junit-jupiter")

// After
testImplementation(libs.junit.jupiter)
```

---

### Workflow 3: Manage Version Catalog

**Pattern**: Pattern 2 (Read-Process-Write)

**Parameters**:
- `project` (optional): Project root (default: current directory)
- `operation` (optional): `organize`, `extract`, `update` (default: `organize`)

**Operations**:

**organize**: Reorganize catalog sections
```toml
[versions]
# Framework versions
spring = "6.1.0"
quarkus = "3.6.0"

# Testing versions
junit = "5.10.0"

[libraries]
# Spring libraries
spring-core = { module = "org.springframework:spring-core", version.ref = "spring" }

[bundles]
# Logical groupings
spring = ["spring-core", "spring-context", "spring-beans"]
```

**extract**: Find hardcoded versions and extract to catalog
1. Grep all `build.gradle(.kts)` for hardcoded versions
2. Generate catalog entries
3. Update build files to use catalog references

**update**: Update versions in catalog
1. Check for available updates
2. Apply updates with verification build

---

### Workflow 4: Update Gradle Wrapper

**Pattern**: Pattern 4 (Command Chain Execution)

**Parameters**:
- `version` (optional): Specific Gradle version (default: latest)

**Steps**:

1. **Check Current Version**:
   ```bash
   ./gradlew --version
   ```

2. **Update Wrapper**:
   ```bash
   ./gradlew wrapper --gradle-version={version}
   ```

3. **Verify Update**:
   ```bash
   ./gradlew --version
   ./gradlew build
   ```

4. **Report**:
```json
{
  "previous_version": "8.4",
  "new_version": "8.5",
  "build_status": "SUCCESS|FAILURE"
}
```

---

### Workflow 5: Verify Build Quality

**Pattern**: Pattern 9 (Validation Pipeline)

**Parameters**:
- `project` (optional): Specific subproject to verify

**Validation Pipeline** (5 stages):

1. **Clean Build**:
   ```bash
   ./gradlew clean build
   ```

2. **Dependency Analysis**:
   ```bash
   ./gradlew dependencies --configuration compileClasspath
   ```

3. **Dependency Health Check**:
   - Check for deprecated dependencies
   - Check for known vulnerabilities (if plugin available)

4. **Configuration Validation**:
   ```bash
   ./gradlew validatePlugins  # if available
   ```

5. **Build Scan** (optional):
   ```bash
   ./gradlew build --scan
   ```

**Return Quality Report**:
```json
{
  "build": "PASS|FAIL",
  "dependency_analysis": "PASS|FAIL",
  "health_check": "PASS|FAIL",
  "configuration": "PASS|FAIL",
  "overall": "PASS|FAIL",
  "issues": [...],
  "scan_url": "https://gradle.com/s/..."
}
```

## Standards References

- [Gradle Dependency Standards](standards/gradle-dependencies.md)
