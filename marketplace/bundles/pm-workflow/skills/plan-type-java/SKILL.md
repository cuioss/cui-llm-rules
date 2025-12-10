---
name: plan-type-java
description: Java plan type for Maven/Gradle projects
allowed-tools: Read, Bash
domain:
  solution_outline_agent: pm-java:java-solution-outline-agent
  task_plan_agent: pm-java:java-task-plan-agent
  verification_command: /pm-builder:builder-build-and-fix
  pr_workflow: true
  standards:
    - pm-java:cui-java-core
    - pm-java:cui-javadoc
    - pm-java:cui-java-unit-testing
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
| `solution_outline_agent` | `pm-java:java-solution-outline-agent` | Creates solution outline with deliverables |
| `task_plan_agent` | `pm-java:java-task-plan-agent` | Creates tasks from deliverables |
| `verification_command` | `/pm-builder:builder-build-and-fix` | Build verification |
| `pr_workflow` | `true` | Create PR after execution |
| `standards` | Java core, JavaDoc, Unit testing | Skills to load |

---

## Operation: configure

**Input**: `plan_id`

**References fields added** (via `pm-workflow:manage-references:manage-references set`):

| Field | Value |
|-------|-------|
| `standards` | `["pm-java:cui-java-core", "pm-java:cui-javadoc", "pm-java:cui-java-unit-testing"]` |
| `adrs` | `[]` |
| `interfaces` | `[]` |
| `dependencies` | `[]` |

**Config fields added** (via `pm-workflow:manage-config:manage-config set`):

| Field | Value |
|-------|-------|
| `create_pr` | `true` |
| `verification_required` | `true` |
| `verification_command` | `/pm-builder:builder-build-and-fix` |
| `branch_strategy` | `feature` |

---

## Agent Behavior

### java-solution-outline-agent

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
2. Add unit tests (load `pm-java:cui-java-unit-testing`)
3. Add JavaDoc (load `pm-java:cui-javadoc`)
4. Follow CUI patterns (load `pm-java:cui-java-core`)
5. Verify `mvn test -pl {module}` passes

**Returns**: `{status, task_ids[], lessons_recorded}`
