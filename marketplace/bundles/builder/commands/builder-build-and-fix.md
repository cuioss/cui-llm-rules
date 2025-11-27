---
name: builder-build-and-fix
description: Execute build, analyze errors, delegate fixes, and iterate until clean (auto-detects build system)
---

# Build and Fix Command

Unified build-and-fix loop that auto-detects or accepts build system specification.

## PARAMETERS

| Parameter | Default | Description |
|-----------|---------|-------------|
| `system` | (auto-detect) | Build system: `maven`, `gradle`, `npm` |
| `goals` | varies | Maven goals / Gradle tasks / npm command |
| `profile` | `pre-commit` | Maven profile (-P flag) |
| `module` | (none) | Maven module (-pl) / Gradle project (-p) / npm workspace |
| `push` | `false` | Auto-commit on clean build |

**Goal defaults by system:**
- maven: `clean install`
- gradle: `clean build`
- npm: `run test`

## WORKFLOW

### Step 1: Determine Build System

**If `system` parameter provided:** Use specified system.

**If `system` not provided:** Auto-detect:

```
Skill: builder:environment-detection
Workflow: Get Build Environment
```

Use `default_system` from result.

**If no system detected:** Report error and exit.

### Step 2: Parse System-Specific Parameters

Apply defaults based on detected system:

| System | Goals Default | Module Param |
|--------|---------------|--------------|
| maven | `clean install` | `-pl {module}` |
| gradle | `clean build` | `-p {module}` |
| npm | `run test` | `--workspace={module}` |

### Step 3: Load Previous Execution Data

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: commands.builder-build-and-fix.{system}.last_execution
```

**Calculate timeout:** `duration_ms * 1.25` (25% safety margin)

### Step 4: Build Loop (max 5 iterations)

**Dispatch to system-specific skill:**

| System | Skill | Workflow |
|--------|-------|----------|
| maven | `builder:builder-maven-rules` | Execute Maven Build |
| gradle | `builder:builder-gradle-rules` | Execute Gradle Build |
| npm | `builder:builder-npm-rules` | Execute npm Build |

**On SUCCESS with 0 issues:** Proceed to Step 5

**On issues:** Route to fix commands:

**Maven/Gradle issues:**
| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/java-implement-code files="{file}" task="Fix: {message}"` |
| `test_failure` | `/java-implement-tests files="{file}" task="Fix: {message}"` |
| `javadoc_warning` | `/java-fix-javadoc files="{file}"` |
| `dependency_error` | Report to user (manual fix required) |

**npm issues:**
| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/js-implement-code files="{file}" task="Fix: {message}"` |
| `test_failure` | `/js-implement-tests files="{file}" task="Fix: {message}"` |
| `lint_error` | `/js-enforce-eslint files="{file}"` |
| `dependency_error` | Report to user (manual fix required) |

**Iteration limits:**
- issues_remaining > 0 AND iteration < 5 -> re-run (without `clean`)
- issues_remaining == 0 -> Proceed to Step 5
- iteration >= 5 -> Report partial (skip Step 5)

### Step 5: Record Execution Results

On successful build (0 issues):

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: commands.builder-build-and-fix.{system}.last_execution
Value: {
  "date": "{current-date}",
  "status": "SUCCESS",
  "duration_ms": {total-duration}
}
```

### Step 6: Report Results

**Success:**
```
BUILD SUCCESS ({system})
Goals: {goals} | Iterations: {n} | Fixed: {n}
```
If `push=true`: Invoke `/cui-task-workflow:commit-changes`

**Partial (max iterations reached):**
```
BUILD PARTIAL ({system})
Resolved: {n}/{total} | Remaining: compilation({n}), test({n})
```

## EXAMPLE USAGE

```bash
# Auto-detect build system
/builder-build-and-fix

# Specify build system explicitly
/builder-build-and-fix system=maven goals="clean verify"
/builder-build-and-fix system=gradle goals="build test"
/builder-build-and-fix system=npm goals="run lint"

# With module targeting
/builder-build-and-fix module=api
/builder-build-and-fix system=gradle module=":core"

# Build and commit on success
/builder-build-and-fix push=true
```

## CRITICAL RULES

- NEVER execute build tools directly - use skill workflows
- Maximum 5 iterations to prevent infinite loops
- Dependency errors require manual intervention
- System parameter takes precedence over auto-detection

## RELATED

- Skill: `builder:environment-detection` - Build system auto-detection
- Skill: `builder:builder-maven-rules` - Maven builds
- Skill: `builder:builder-gradle-rules` - Gradle builds
- Skill: `builder:builder-npm-rules` - npm builds
