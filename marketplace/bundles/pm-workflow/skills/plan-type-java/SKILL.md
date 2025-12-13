---
name: plan-type-java
description: Java plan type for Maven/Gradle projects
allowed-tools: Read, Bash

# Detection patterns and keywords
patterns:
  - "*.java"
  - "pom.xml"
  - "build.gradle"
  - "build.gradle.kts"
keywords:
  - java
  - maven
  - gradle
  - junit
  - quarkus
  - spring

# Agent routing
domain:
  solution_outline_agent: pm-dev-java:java-plan-solution-outline-agent
  task_plan_agent: pm-dev-java:java-task-plan-agent
  implement_agent: pm-dev-java:java-plan-implement-agent

# Plan defaults for this type
plan_defaults:
  verification_command: /pm-dev-builder:builder-build-and-fix
  pr_workflow: true
  standards:
    - pm-dev-java:cui-java-core
    - pm-dev-java:cui-javadoc
    - pm-dev-java:cui-java-unit-testing
---

# Plan Type: Java (`pm-workflow:plan-type-java`)

**Use Cases**:
- Java implementation tasks
- Maven/Gradle projects
- CUI Java libraries and modules
- Quarkus/CDI applications

**API**: Implements `pm-workflow:plan-type-api` contract.

## Domain Configuration

The `domain:` frontmatter provides structured routing information for commands:

| Field | Value | Purpose |
|-------|-------|---------|
| `solution_outline_agent` | `pm-dev-java:java-plan-solution-outline-agent` | Creates solution outline with deliverables |
| `task_plan_agent` | `pm-dev-java:java-task-plan-agent` | Creates tasks from deliverables |
| `implement_agent` | `pm-dev-java:java-plan-implement-agent` | Executes tasks from plan |

The `plan_defaults:` frontmatter is automatically read by `manage-config create` during plan initialization:

| Field | Value | Config Field |
|-------|-------|--------------|
| `verification_command` | `/pm-dev-builder:builder-build-and-fix` | `verification_command`, `verification_required` |
| `pr_workflow` | `true` | `create_pr`, `branch_strategy` |
| `standards` | Java core, JavaDoc, Unit testing | (informational) |

---

## Agent Behavior

### java-plan-solution-outline-agent

Analyzes Java codebase and creates deliverables with:
- Class/interface design decisions
- Package placement rationale
- Dependencies (CDI, Spring, external libs)
- Module assignment (for multi-module projects)
- Integration points with existing code

**Returns**: `{status, deliverable_count, solution_document, lessons_recorded}`

### java-task-plan-agent

Creates tasks with Java-specific steps:
1. Create/modify implementation file at `{path}`
2. Add unit tests (load `pm-dev-java:cui-java-unit-testing`)
3. Add JavaDoc (load `pm-dev-java:cui-javadoc`)
4. Follow CUI patterns (load `pm-dev-java:cui-java-core`)
5. Verify build passes (via `/pm-dev-builder:builder-build-and-fix`)

**Returns**: `{status, task_ids[], lessons_recorded}`
