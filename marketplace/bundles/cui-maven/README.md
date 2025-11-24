# CUI Maven Tools

Maven build, verification, and POM maintenance tools for CUI projects.

## Purpose

This bundle provides comprehensive Maven workflow support including build verification, quality gate enforcement, POM maintenance standards, and automated issue categorization. All agent functionality has been absorbed into skill workflows with Python scripts for deterministic analysis.

## Components Included

### Skills (1 skill with workflow)

1. **cui-maven-rules** - Complete Maven standards covering build processes, POM maintenance, dependency management, and Maven integration
   - **Workflow: Parse Maven Build Output** - Parse and categorize Maven build errors/warnings

### Scripts (1 automation script)

| Script | Location | Purpose |
|--------|----------|---------|
| `parse-maven-output.py` | cui-maven-rules | Parse Maven build logs, categorize issues |

### Commands (1 goal-based orchestrator)

1. **maven-build-and-fix** - Executes Maven build, analyzes issues, delegates fixes to appropriate commands, iterates until clean

## Architecture

```
cui-maven/
├── commands/                # 1 goal-based orchestrator
│   └── maven-build-and-fix.md
└── skills/
    └── cui-maven-rules/     # Standards + workflow
        ├── SKILL.md         # Workflow: Parse Maven Build Output
        ├── scripts/
        │   └── parse-maven-output.py
        └── standards/
            ├── pom-maintenance.md
            └── maven-integration.md
```

## Workflow Pattern

Commands are thin orchestrators that invoke skill workflows:

```
/maven-build-and-fix
  ├─> Bash: ./mvnw -l target/build-output.log {goals}
  ├─> Skill(cui-maven-rules) workflow: Parse Maven Build Output
  ├─> Route issues to fix commands:
  │   ├─> /java-implement-code (compilation errors)
  │   ├─> /java-implement-tests (test failures)
  │   └─> /java-fix-javadoc (javadoc warnings)
  └─> Iterate until clean or max iterations
```

## Usage Examples

### Basic Build and Fix

```
/maven-build-and-fix
```

### Build with Custom Goals

```
/maven-build-and-fix goals="clean verify -Pcoverage"
```

### Build, Fix, and Commit

```
/maven-build-and-fix push
```

## Issue Categorization

The parse-maven-output.py script categorizes issues:

| Issue Type | Description | Fix Route |
|------------|-------------|-----------|
| `compilation_error` | Java compilation failures | `/java-implement-code` |
| `test_failure` | JUnit test failures | `/java-implement-tests` |
| `javadoc_warning` | JavaDoc documentation issues | `/java-fix-javadoc` |
| `dependency_error` | Maven dependency issues | Manual POM fix |
| `deprecation_warning` | Deprecated API usage | Manual code update |
| `unchecked_warning` | Generic type issues | Manual code update |

## Bundle Statistics

- **Commands**: 1 (thin orchestrator)
- **Skills**: 1 (with Parse Maven Build Output workflow)
- **Scripts**: 1 (Python automation)
- **Agents**: 0 (all absorbed into skill workflows)

## Dependencies

### Inter-Bundle Dependencies

- **cui-java-expert** - For `/java-implement-code`, `/java-implement-tests`, `/java-fix-javadoc`
- **cui-task-workflow** - For commit functionality when `push` flag is used

### External Dependencies

- Python 3 for automation scripts
- Maven wrapper (`./mvnw`) in project root

## Configuration

### Project Configuration

Maven projects can configure build behavior in `.claude/run-configuration.md`:

```markdown
# Command Configuration

## ./mvnw -Ppre-commit clean install

### Last Execution Duration
- **Duration**: 120000ms (2 minutes)
- **Last Updated**: 2025-10-29
```

### Build Profiles

Projects should define a `pre-commit` profile in their POM for quality checks.

## Support

- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-maven/
