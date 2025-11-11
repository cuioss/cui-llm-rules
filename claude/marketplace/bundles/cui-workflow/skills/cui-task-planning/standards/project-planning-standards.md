# Project Planning Standards

Standards for long-term, project-wide planning documents that track implementation progress while maintaining traceability to requirements and specifications.

## Purpose

Project planning documents are designed for:
- Large-scale, multi-month/multi-year projects
- Comprehensive feature tracking across entire codebase
- Coordination across teams or modules
- Long-term progress visibility

## When to Use Project Planning

Use this approach when:
- Planning entire project implementation
- Tracking multiple related features
- Coordinating work across teams
- Need hierarchical organization by component/feature/phase
- Require extended status indicators (partial, blocked)

**Not appropriate for:**
- Single GitHub issues (use Issue Planning)
- Quick improvements (use Refactoring Planning)
- Short-term tasks (use Issue Planning)

## Document Structure

### File Locations

**Primary planning document:**
```
doc/TODO.adoc
```

**Additional planning documents** (if needed):
```
doc/ROADMAP.adoc     # Long-term planning, future features
doc/BACKLOG.adoc     # Future work items, not yet prioritized
```

### Document Header

```asciidoc
= [Project Name] TODO List
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js
```

### Core Sections

Every planning document should include:

1. **Overview** - Purpose and scope of the document
2. **Implementation Tasks** - Organized by functional area
3. **Testing Tasks** - Test implementation requirements  
4. **Documentation Tasks** - Documentation needs
5. **Additional Sections** - As needed (Security, Performance, etc.)

## Task Organization

### Hierarchical Structure

Organize tasks by functional area using AsciiDoc section levels:

```asciidoc
== Implementation Tasks

=== Core Components

==== Token Validator
_See Requirement JWT-1: Token Validation Framework in link:Requirements.adoc[Requirements]_

* [ ] Implement TokenValidator interface
* [ ] Add signature validation
* [ ] Add expiration checking

==== Signature Validator  
_See Requirement JWT-1.1: Signature Validation in link:Requirements.adoc[Requirements]_

* [ ] Implement RS256 algorithm support
* [ ] Implement HS256 algorithm support
* [ ] Add constant-time comparison

=== Configuration

==== Configuration Properties
_See Requirement JWT-7: Configuration Management in link:Requirements.adoc[Requirements]_

* [ ] Define configuration property structure
* [ ] Add issuer configuration
* [ ] Add algorithm configuration
```

### Grouping Strategies

Choose organization that best fits your project:

**By Component:**
```asciidoc
=== Token Validation Component
=== Configuration Component  
=== Error Handling Component
```

**By Feature:**
```asciidoc
=== User Authentication Feature
=== API Integration Feature
=== Reporting Feature
```

**By Layer:**
```asciidoc
=== Data Layer
=== Business Logic Layer
=== API Layer
=== UI Layer
```

**By Phase:**
```asciidoc
=== Phase 1: Core Infrastructure
=== Phase 2: Feature Implementation  
=== Phase 3: Polish and Optimization
```

## Status Indicators

For complete status indicator definitions and rationale, see **[task-planning-core.md](task-planning-core.md)** section "Status Indicators".

Project planning uses all four status markers:
- `[ ]` - Pending (not started or in progress)
- `[x]` - Completed (fully implemented and verified)
- `[~]` - Partially Completed (some criteria met, needs more work)
- `[!]` - Blocked (cannot proceed due to external dependency)

**Examples:**
```asciidoc
* [ ] Implement token validation         # Pending
* [x] Implement token parsing            # Completed
* [~] Implement error handling           # Partially done (basic errors done, need edge cases)
* [!] Add Redis caching                   # Blocked (waiting for Redis infrastructure)
```

Project planning is the only use case that supports all four markers. Issue and refactoring planning use only the two basic markers ([ ] and [x]).

## Traceability Requirements

### Linking to Requirements

**REQUIRED:** Every task group MUST reference its source requirement:

```asciidoc
==== Token Validation
_See Requirement JWT-1: Token Validation Framework in link:Requirements.adoc[Requirements]_

* [ ] Implement TokenValidator interface
* [ ] Add signature validation
```

### Linking to Specifications

Task groups can also reference detailed specifications:

```asciidoc
==== Token Validation
_See Requirement JWT-1: Token Validation Framework in link:Requirements.adoc[Requirements]_

_See link:specification/token-validation.adoc[Token Validation Specification] for implementation details_

* [ ] Implement TokenValidator interface
* [ ] Add signature validation
```

### Multiple References

When tasks relate to multiple requirements or specs:

```asciidoc
==== Security Hardening
_See Requirements:_

* _JWT-1: Token Validation Framework in link:Requirements.adoc[Requirements]_
* _SEC-1: Security Standards in link:Requirements.adoc[Requirements]_

_See link:specification/security.adoc[Security Specification] for implementation details_

* [ ] Implement constant-time signature comparison
* [ ] Add input validation
```

## Task Notes and Details

Add context using italics and sub-bullets:

```asciidoc
* [ ] Implement JWT validation
  ** Must support RS256 and HS256 algorithms
  ** Need to decide on key rotation strategy
* _Note: Key rotation design needs review with security team_
* _Important: This blocks API authentication implementation_
* _Blocked: Waiting for security review approval_
* _Depends on: Completion of token parsing in Core Components section_
* _Decision needed: Choose between Redis and Hazelcast for caching_
```

### Note Types

**General notes:**
```asciidoc
* _Note: Consider caching validated tokens for performance_
```

**Important information:**
```asciidoc
* _Important: This must be completed before phase 2 can start_
```

**Blockers:**
```asciidoc
* _Blocked: Waiting for security review approval_
```

**Dependencies:**
```asciidoc
* _Depends on: Completion of task XYZ in section ABC_
```

**Decisions needed:**
```asciidoc
* _Decision needed: Choose between Redis and Hazelcast for caching_
```

## Testing Task Organization

Always include dedicated testing section:

```asciidoc
== Testing

=== Unit Testing
_See link:specification/testing.adoc#_unit_testing[Unit Testing Specification]_

==== Core Components
* [ ] Unit tests for TokenValidator
* [ ] Unit tests for SignatureValidator
* [ ] Unit tests for ClaimExtractor

==== Edge Cases
* [ ] Test expired tokens
* [ ] Test malformed tokens
* [ ] Test invalid signatures

=== Integration Testing
_See link:specification/testing.adoc#_integration_testing[Integration Testing Specification]_

==== End-to-End Flows
* [ ] Test complete token validation flow
* [ ] Test error handling across components

=== Test Coverage
* [x] Achieve 80% line coverage on core components
* [ ] Achieve 90% branch coverage on validation logic
* [ ] Achieve 100% coverage on security-critical paths
```

## Maintenance

### Keeping Documents Current

**Update frequency** - Update whenever:
- Tasks are completed
- New tasks are discovered
- Tasks are blocked or unblocked
- Implementation priorities change

**Regular reviews** - Review planning documents:
- At start of each development sprint/cycle
- When major milestones are reached
- When project scope changes

### Task Lifecycle Management

**Adding tasks:**
1. Identify the appropriate section
2. Link to relevant requirement or specification
3. Provide clear, actionable description
4. Mark with appropriate status (usually `[ ]`)
5. Add notes for context if needed

**Completing tasks:**
1. Change status from `[ ]` to `[x]`
2. Verify implementation meets requirements
3. Update related specifications if needed
4. Leave completed tasks for project history

**Refactoring tasks:**
1. Break down tasks that are too large
2. Merge tasks that are too granular
3. Reorganize sections as understanding improves
4. Maintain traceability links throughout

### Archive Strategy

**Do NOT archive** planning documents - they serve as project history.

**Completed tasks** remain in place with `[x]` status.

**New features** get new sections or documents.

## Quality Checklist

Before finalizing planning document, verify:

- [ ] All sections have clear headings
- [ ] Every task group links to requirements or specifications  
- [ ] Tasks are clear and actionable
- [ ] Status indicators are current
- [ ] Testing section is comprehensive
- [ ] Notes provide helpful context
- [ ] Organization is logical and navigable
- [ ] Document header is complete with TOC configuration

## Example Structure

The examples throughout this document demonstrate the complete TODO.adoc structure, including:
- Status indicators ([ ], [x], [~], [!]) with hierarchical task organization
- Requirements traceability using xref links
- Testing section organization
- Task notes and context (_Note:_, _Blocked:_, _Important:_)
- Hierarchical organization (sections, subsections, task items)

## Related Standards

- task-planning-core.md - Core concepts and status indicators
- issue-planning-standards.md - Short-term issue planning
- refactoring-planning-standards.md - Refactoring task tracking
