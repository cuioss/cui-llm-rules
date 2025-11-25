# CUI Maven Tools

Maven build execution, POM maintenance, and quality verification for CUI projects.

## Purpose

This bundle provides comprehensive Maven workflow support including build execution, output parsing, issue routing, POM maintenance, and quality verification. Skills use Python scripts for deterministic analysis.

## Components

### Skills

| Skill | Purpose |
|-------|---------|
| `cui-maven-rules` | Build execution, output parsing, issue routing |
| `cui-pom-maintenance` | POM maintenance, BOM optimization, scope analysis |

### Commands

| Command | Purpose |
|---------|---------|
| `/maven-build-and-fix` | Iterative build and fix loop |
| `/maven-pom-maintenance` | POM maintenance orchestration |

### Agents

| Agent | Purpose |
|-------|---------|
| `maven-builder` | Autonomous single-build execution (haiku model) |

## Architecture

```
cui-maven/
├── agents/
│   └── maven-builder.md          # Autonomous build agent
├── commands/
│   ├── maven-build-and-fix.md    # Build-fix loop orchestrator
│   └── maven-pom-maintenance.md  # POM maintenance orchestrator
└── skills/
    ├── cui-maven-rules/          # Build execution skill
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── execute-maven-build.py
    │   │   ├── parse-maven-output.py
    │   │   ├── check-acceptable-warnings.py
    │   │   ├── search-openrewrite-markers.py
    │   │   └── find-module-path.py
    │   └── standards/
    │       ├── maven-build-execution.md
    │       ├── maven-openrewrite-handling.md
    │       └── maven-acceptable-warnings.md
    └── cui-pom-maintenance/      # POM maintenance skill
        ├── SKILL.md
        └── standards/
            └── pom-standards.md
```

## Usage

### Build and Fix Loop

```
/maven-build-and-fix
/maven-build-and-fix goals="clean verify" profile="coverage"
/maven-build-and-fix push=true
```

### POM Maintenance

```
/maven-pom-maintenance action=analyze
/maven-pom-maintenance action=optimize
/maven-pom-maintenance action=openrewrite
/maven-pom-maintenance action=wrapper
/maven-pom-maintenance action=verify
```

### Direct Skill Usage

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean install
  profile: pre-commit
  module: auth-service
```

```
Skill: cui-maven:cui-pom-maintenance
Workflow: Analyze POM Issues
Parameters:
  module: auth-service
  scope: all
```

## Issue Routing

Build issues are categorized and routed to fix commands:

| Issue Type | Fix Command |
|------------|-------------|
| `compilation_error` | `/java-implement-code` |
| `test_failure` | `/java-implement-tests` |
| `javadoc_warning` | `/java-fix-javadoc` |
| `dependency_error` | Manual POM fix |

## Dependencies

### Inter-Bundle

- **cui-java-expert** - For fix commands (`/java-implement-code`, `/java-implement-tests`, `/java-fix-javadoc`)
- **cui-task-workflow** - For commit functionality
- **cui-utilities** - For `claude-run-configuration` skill

### External

- Python 3 (stdlib only)
- Maven wrapper (`./mvnw`) in project root

## Configuration

Acceptable warnings configured via `cui-utilities:claude-run-configuration`:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: maven.acceptable_warnings
```

Structure:
```json
{
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": [],
      "plugin_compatibility": [],
      "platform_specific": []
    }
  }
}
```
