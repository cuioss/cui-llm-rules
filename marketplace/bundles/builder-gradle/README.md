# builder-gradle Bundle

Gradle build, verification, and dependency maintenance tools for CUI projects.

## Overview

This bundle provides comprehensive Gradle build automation with automatic error fixing, dependency management, and quality verification. The API mirrors the `builder-maven` bundle for easy adoption.

## Components

### Commands

| Command | Description |
|---------|-------------|
| `/gradle-build-and-fix` | Iterative build loop with automatic issue routing |
| `/gradle-dependency-maintenance` | Dependency analysis, version catalog management |

### Agents

| Agent | Description |
|-------|-------------|
| `gradle-builder` | Autonomous single-build execution with project detection |

### Skills

| Skill | Description |
|-------|-------------|
| `builder-gradle:builder-gradle-rules` | Build execution, output parsing, issue routing |
| `builder-gradle:builder-gradle-dependencies` | Dependency maintenance, version catalog management |

## Quick Start

### Basic Build

```bash
# Build and fix errors
/gradle-build-and-fix

# Build specific subproject
/gradle-build-and-fix project=":api"

# Custom tasks
/gradle-build-and-fix tasks="clean test"
```

### Dependency Maintenance

```bash
# Analyze dependencies
/gradle-dependency-maintenance action=analyze

# Optimize (apply fixes)
/gradle-dependency-maintenance action=optimize

# Update version catalog
/gradle-dependency-maintenance action=catalog

# Update Gradle wrapper
/gradle-dependency-maintenance action=wrapper
```

## API Comparison with Maven

The API is designed to be parallel to `builder-maven`:

| Maven | Gradle | Notes |
|-------|--------|-------|
| `/maven-build-and-fix` | `/gradle-build-and-fix` | Same parameters (goals→tasks) |
| `/maven-pom-maintenance` | `/gradle-dependency-maintenance` | Same actions |
| `maven-builder` agent | `gradle-builder` agent | Same behavior |
| `builder-maven:builder-maven-rules` | `builder-gradle:builder-gradle-rules` | Same workflows |
| `builder-maven:builder-pom-maintenance` | `builder-gradle:builder-gradle-dependencies` | Same workflows |

### Parameter Mapping

| Maven Parameter | Gradle Parameter |
|-----------------|------------------|
| `goals` | `tasks` |
| `profile` | (use `-P` in tasks) |
| `module` | `project` |

## Workflows

### /gradle-build-and-fix

1. Parse parameters and load previous execution duration
2. Execute Gradle build with calculated timeout
3. Parse output and categorize issues
4. Route issues to appropriate fix commands
5. Re-run build (up to 5 iterations)
6. Report results

**Issue Routing**:
- `compilation_error` → `/java-implement-code`
- `test_failure` → `/java-implement-tests`
- `javadoc_warning` → `/java-fix-javadoc`
- `dependency_error` → Report to user

### /gradle-dependency-maintenance

| Action | Purpose |
|--------|---------|
| `analyze` | Identify dependency issues |
| `optimize` | Apply fixes from analysis |
| `catalog` | Manage version catalog |
| `wrapper` | Update Gradle wrapper |
| `verify` | Run quality gate checks |

## Scripts

| Script | Purpose |
|--------|---------|
| `execute-gradle-build.py` | Execute Gradle with log capture |
| `parse-gradle-output.py` | Parse and categorize build output |
| `find-gradle-project.py` | Locate projects by name |
| `check-acceptable-warnings.py` | Categorize warnings |
| `search-openrewrite-markers.py` | Find OpenRewrite markers |

## Standards

- [Gradle Build Execution](skills/builder-gradle-rules/standards/gradle-build-execution.md)
- [Gradle OpenRewrite Handling](skills/builder-gradle-rules/standards/gradle-openrewrite-handling.md)
- [Gradle Acceptable Warnings](skills/builder-gradle-rules/standards/gradle-acceptable-warnings.md)
- [Gradle Dependencies](skills/builder-gradle-dependencies/standards/gradle-dependencies.md)

## Requirements

- Gradle wrapper (`./gradlew`) in project root
- Python 3.x for scripts
- Java project structure

## Configuration

Build configuration stored in `.claude/run-configuration.json`:

```json
{
  "commands": {
    "gradle-build-and-fix": {
      "last_execution": {
        "date": "2025-01-15T10:30:00Z",
        "status": "SUCCESS",
        "duration_ms": 120000
      }
    }
  },
  "gradle": {
    "acceptable_warnings": {
      "dependency_resolution": [],
      "plugin_compatibility": [],
      "platform_specific": []
    }
  }
}
```

## Dependencies

This bundle integrates with:

- `cui-java-expert` - For Java code fixes
- `cui-utilities` - For configuration management
- `cui-task-workflow` - For commit operations

## License

Apache-2.0
