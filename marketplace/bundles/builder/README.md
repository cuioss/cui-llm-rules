# Builder Bundle

Unified build tools for Maven, Gradle, and npm projects.

## Overview

This bundle consolidates build execution, output parsing, and issue routing for all supported build systems:

- **Maven** - Java project builds with multi-module support
- **Gradle** - Java/Kotlin project builds with OpenRewrite integration
- **npm/npx** - JavaScript project builds and test execution

## Skills

### Environment

- **environment-detection** - Detect and cache build systems (maven, gradle, npm)

### Maven

- **builder-maven-rules** - Maven build execution and output parsing
- **builder-pom-maintenance** - POM file management and dependency updates

### Gradle

- **builder-gradle-rules** - Gradle build execution and output parsing
- **builder-gradle-dependencies** - Gradle dependency management

### npm

- **builder-npm-rules** - npm/npx build execution and output parsing

## Agents

- **maven-builder** - Autonomous Maven build agent
- **gradle-builder** - Autonomous Gradle build agent
- **npm-builder** - Autonomous npm/npx build agent

## Commands

### Maven Commands

- `/maven-build-and-fix` - Execute Maven build and fix issues iteratively
- `/maven-pom-maintenance` - POM dependency and BOM maintenance

### Gradle Commands

- `/gradle-build-and-fix` - Execute Gradle build and fix issues iteratively
- `/gradle-dependency-maintenance` - Gradle dependency maintenance

### npm Commands

- `/npm-build-and-fix` - Execute npm build and fix issues iteratively
- `/npm-package-maintenance` - Package.json maintenance and auditing

## Common Features

All build tools share:

- **Build Execution** - Run builds with timeout management
- **Output Parsing** - Extract errors, warnings, and test failures
- **Issue Routing** - Direct issues to appropriate fix commands
- **Log Management** - Timestamped logs in target/ directory
- **Acceptable Warnings** - Filter known/expected warnings

## Usage

### Maven Project

```
Skill: builder:builder-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean verify
  output_mode: structured
```

### Gradle Project

```
Skill: builder:builder-gradle-rules
Workflow: Execute Gradle Build
Parameters:
  tasks: clean build
  output_mode: structured
```

### npm Project

```
Skill: builder:builder-npm-rules
Workflow: Execute npm Build
Parameters:
  command: run test
  output_mode: structured
```

## Related Bundles

- **cui-java-expert** - Java development standards
- **cui-frontend-expert** - JavaScript development standards
- **cui-task-workflow** - PR and issue workflows
