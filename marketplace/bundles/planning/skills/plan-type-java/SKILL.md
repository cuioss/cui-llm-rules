---
name: plan-type-java
description: Java plan type providing domain-specific configuration and refinement for Java/Maven/Gradle projects
allowed-tools: Read, Bash
---

# Plan Type: Java

**Use Cases**:
- Java implementation tasks
- Maven/Gradle projects
- CUI Java libraries and modules
- Quarkus/CDI applications

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | java |
| Verification | `/builder-build-and-fix` |
| PR Workflow | true |

---

## Operation: configure

**Input**: `plan_id`

**References fields added**:

| Field | Value |
|-------|-------|
| `standards` | `["cui-java-expert:cui-java-core", "cui-java-expert:cui-javadoc", "cui-java-expert:cui-java-unit-testing"]` |
| `adrs` | `[]` |
| `interfaces` | `[]` |
| `dependencies` | `[]` |

**Config fields added**:

| Field | Value |
|-------|-------|
| `create_pr` | `true` |
| `verification_required` | `true` |
| `verification_command` | `/builder-build-and-fix` |
| `branch_strategy` | `feature` |

---

## Operation: specify

**Input**: `plan_id`

**Java-Specific Content** (included in specifications):
- Class/interface design decisions
- Package placement rationale
- Dependencies (CDI, Spring, external libs)
- Module assignment (for multi-module projects)
- Integration points with existing code

---

## Operation: plan

**Input**: `plan_id`

**Java-Specific Task Steps** (standard for implementation tasks):
1. Create/modify implementation file at `{path}`
2. Add unit tests (load `cui-java-expert:cui-java-unit-testing`)
3. Add JavaDoc (load `cui-java-expert:cui-javadoc`)
4. Follow CUI patterns (load `cui-java-expert:cui-java-core`)
5. Verify `mvn test -pl {module}` passes
