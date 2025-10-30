---
name: cui-requirements
description: Requirements engineering and planning standards for CUI projects
allowed-tools: [Read, Edit, Write, Grep, Glob]
---

# CUI Requirements Skill

Standards for requirements engineering, planning, and specification in CUI projects.

## Workflow

### Step 1: Load Requirements Standards

**CRITICAL**: Load requirements standards based on context.

1. **Always load core requirements standards**:
   ```
   Read: standards/requirements-core.md
   ```

2. **Conditional loading based on context**:

   - If creating specifications:
     ```
     Read: standards/specification-standards.md
     ```

   - If creating planning or TODO documents:
     ```
     Read: standards/planning.md
     ```

   - If implementing features based on specifications:
     ```
     Read: standards/specification-and-implementation.md
     ```

### Step 2: Analyze Requirements Context

**When to Execute**: Before creating requirements documentation

**What to Analyze**:

1. **Requirements Type**:
   - Feature requirements
   - Technical requirements
   - Non-functional requirements
   - Constraints and dependencies

2. **Stakeholders**:
   - Development team
   - Product owners
   - End users
   - System integrators

3. **Scope and Complexity**:
   - Single feature
   - Module or component
   - System-wide changes
   - Integration requirements

4. **Documentation Needs**:
   - Requirements document
   - Specification document
   - Implementation plan
   - Test plan

### Step 3: Apply Requirements Standards

**When to Execute**: During requirements creation

**What to Apply**:

1. **Requirements Document Structure**:
   - Clear title and overview
   - Background and context
   - Functional requirements (MUST, SHOULD, MAY)
   - Non-functional requirements
   - Constraints and dependencies
   - Success criteria
   - Acceptance criteria

2. **Requirements Quality**:
   - Specific and measurable
   - Achievable and realistic
   - Relevant to business goals
   - Time-bound where applicable
   - Testable and verifiable

3. **Specification Documents**:
   - Technical architecture
   - Component design
   - Interface specifications
   - Data models
   - API specifications
   - Integration points

4. **Planning Standards**:
   - Break down into tasks
   - Identify dependencies
   - Estimate effort
   - Define milestones
   - Risk assessment

### Step 4: Verify Requirements Quality

**When to Execute**: After creating requirements

**Quality Checks**:

1. **Completeness Verification**:
   - [ ] All functional requirements documented
   - [ ] Non-functional requirements included
   - [ ] Constraints identified
   - [ ] Success criteria defined
   - [ ] Acceptance criteria clear

2. **Clarity Verification**:
   - [ ] Requirements are specific
   - [ ] No ambiguous language
   - [ ] Technical terms defined
   - [ ] Examples provided
   - [ ] Testable criteria

3. **Consistency Verification**:
   - [ ] No conflicting requirements
   - [ ] Consistent terminology
   - [ ] Aligned with architecture
   - [ ] Compatible with constraints

4. **Traceability Verification**:
   - [ ] Requirements linked to business goals
   - [ ] Implementation tasks identified
   - [ ] Test cases defined
   - [ ] Dependencies mapped

### Step 5: Document and Review

**When to Execute**: After verification passes

**Review Process**:
- Stakeholder review
- Technical review
- Approval and sign-off
- Version control

**Commit Standards**:
```bash
git commit -m "docs: Add requirements for [feature-name]

- Functional requirements defined
- Technical specifications included
- Acceptance criteria documented
- Implementation plan outlined

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Common Requirements Patterns

### Requirements Document Structure
```asciidoc
= Feature Name Requirements

== Overview
Brief description of the feature and its purpose.

== Background
Context and motivation for the feature.

== Functional Requirements

=== REQ-001: [Requirement Title]
**Priority**: MUST

**Description**: Clear description of what the system must do.

**Acceptance Criteria**:
* Criterion 1
* Criterion 2
* Criterion 3

== Non-Functional Requirements

=== NFR-001: Performance
**Description**: System must handle X requests per second.

=== NFR-002: Security
**Description**: Authentication and authorization requirements.

== Constraints
* Technical constraints
* Resource constraints
* Time constraints

== Dependencies
* Dependency on other features
* External dependencies
* Infrastructure requirements

== Success Criteria
* Measurable success indicators
* Business value delivered
* User satisfaction metrics
```

### Specification Document Structure
```asciidoc
= Feature Name Specification

== Technical Architecture

=== Component Diagram
[source,plantuml]
----
@startuml
component [Frontend] as FE
component [Backend] as BE
database [Database] as DB

FE --> BE : REST API
BE --> DB : SQL
@enduml
----

=== API Specification

==== Endpoint: GET /api/resource
**Request**: Query parameters
**Response**: JSON format
**Status Codes**: 200, 404, 500

== Data Models

=== Entity: Resource
```java
public class Resource {
    private String id;
    private String name;
    // ...
}
```

== Implementation Plan

=== Phase 1: Core Implementation
* Task 1: Database schema
* Task 2: Backend API
* Task 3: Frontend integration

=== Phase 2: Testing and Deployment
* Unit tests
* Integration tests
* Deployment

== Test Plan

=== Unit Tests
* Test case 1
* Test case 2

=== Integration Tests
* Integration scenario 1
* Integration scenario 2
```

## Quality Verification

All requirements must pass:
- [x] Complete and specific
- [x] Clear and unambiguous
- [x] Testable and verifiable
- [x] Consistent and non-conflicting
- [x] Traceable to business goals
- [x] Approved by stakeholders

## References

* Requirements Standards: standards/requirements-core.md
* Specification Standards: standards/specification-standards.md
* Planning Standards: standards/planning.md
* Implementation Guide: standards/specification-and-implementation.md
