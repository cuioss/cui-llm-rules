---
name: cui-requirements:requirements-documentation
source_bundle: cui-requirements
description: Standards for creating and maintaining requirements documents with SMART principles, consistent formatting, and traceability
version: 1.0.0
allowed-tools: []
---

# Requirements Documentation Standards

Standards for creating, structuring, and maintaining requirements documents in CUI projects following SMART principles and ensuring complete traceability.

## Core Principles

### Document Purpose

Requirements documents serve as the authoritative source for what a system must do, not how it should be implemented. They establish clear, measurable goals that guide all subsequent specification and implementation work.

### SMART Requirements

All requirements must follow [SMART principles](https://www.atlassian.com/blog/productivity/how-to-write-smart-goals):

- **Specific**: Clear and unambiguous statements of what is needed
- **Measurable**: Testable and verifiable outcomes
- **Achievable**: Realistic within project constraints
- **Relevant**: Aligned with project goals and user needs
- **Time-bound**: Clear delivery expectations (when applicable)

### Traceability

Every requirement must be:

- Uniquely identifiable through a consistent ID scheme
- Traceable to corresponding specification documents
- Referenced by implementation code and tests
- Maintainable throughout the project lifecycle

## Document Structure Standards

### Location and Naming

**Required location**: `doc/Requirements.adoc`

**Format**: AsciiDoc with proper structure and formatting

### Document Header

```asciidoc
= [Project Name] Requirements
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js
```

### Content Organization

Requirements documents must include:

1. **Overview section**: Explains the purpose and scope of the requirements
2. **General Requirements section**: High-level project requirements
3. **Functional Requirements sections**: Organized by component or feature
4. **Non-Functional Requirements**: Performance, security, usability, etc.

## Requirements Format Standards

### Requirement ID Format

**Format**: `[#PREFIX-NUM]`

**Examples**:
- `[#NIFI-AUTH-1]`
- `[#API-SEC-2.1]`
- `[#UI-COMP-5]`

Each requirement anchor must be placed immediately before the heading:

```asciidoc
[#NIFI-AUTH-1]
=== NIFI-AUTH-1: REST API Support Enhancement
```

### Requirement Heading Format

**Major requirements**: Level 3 headings (`===`)
```asciidoc
=== PREFIX-NUM: Descriptive Title
```

**Sub-requirements**: Level 4 headings (`====`)
```asciidoc
==== PREFIX-NUM.1: Sub-requirement Title
```

### Requirement Content Format

Use bullet points for requirement details:

```asciidoc
[#API-AUTH-1]
=== API-AUTH-1: Authentication Framework

* The system must support OAuth 2.0 authentication
* Token expiration must be configurable
* Failed authentication attempts must be logged
  ** Log entries must include timestamp and client identifier
  ** Sensitive information must be redacted from logs
```

## Requirement Numbering Standards

### Numbering Scheme

**Major requirements**: Sequential numbers (PREFIX-1, PREFIX-2, PREFIX-3)

**Sub-requirements**: Decimal notation (PREFIX-1.1, PREFIX-1.2, PREFIX-2.1)

**Consistency**: Maintain the same prefix throughout the document

### Numbering Rules

1. **Never reuse requirement IDs**, even if a requirement is removed
2. **Assign next available number** when adding new requirements
3. **Maintain sequence** - don't skip numbers unless there's a deprecation
4. **Use decimal notation** for sub-requirements only

### Deprecated Requirements

When a requirement is no longer applicable:

```asciidoc
[#API-AUTH-5]
=== API-AUTH-5: [DEPRECATED] Basic Authentication Support

This requirement has been deprecated in favor of OAuth 2.0 (see API-AUTH-1).
```

**Do not delete deprecated requirements** - this maintains ID sequence integrity and project history.

## Prefix Selection Standards

### Choosing a Prefix

When creating requirements for a new project:

1. **Length**: Keep prefixes short (3-5 characters)
2. **Relevance**: Use domain-specific abbreviations
3. **Uniqueness**: Ensure the prefix is unique within your organization
4. **Consistency**: Use the same prefix throughout all project documentation

### Recommended Prefixes by Domain

| Domain | Prefix | Example |
|--------|--------|---------|
| Apache NiFi Integration | `NIFI-` | NIFI-PROC-1 |
| Security | `SEC-` | SEC-AUTH-1 |
| API Development | `API-` | API-REST-1 |
| User Interface | `UI-` | UI-COMP-1 |
| Database | `DB-` | DB-MIGR-1 |
| Integration | `INT-` | INT-KAFKA-1 |
| Logging | `LOG-` | LOG-AUDIT-1 |
| Testing | `TEST-` | TEST-PERF-1 |

### Multiple Component Prefixes

For complex projects with multiple major components, use hierarchical prefixes:

```asciidoc
[#SYS-AUTH-1]
=== SYS-AUTH-1: Authentication System Requirements

[#SYS-AUTH-1.1]
==== SYS-AUTH-1.1: OAuth Implementation

[#SYS-DB-1]
=== SYS-DB-1: Database Requirements

[#SYS-DB-1.1]
==== SYS-DB-1.1: Schema Design
```

## Maintaining Requirements

### Adding New Requirements

1. Identify the appropriate section for the new requirement
2. Assign the next available number in the sequence
3. Follow the established format and structure
4. Add backtracking links to corresponding specifications when created

### Modifying Requirements

1. **Preserve the requirement ID** - never change it
2. **Update only the content** that needs to change
3. **Document significant changes** in commit messages
4. **Update all dependent specifications** to maintain traceability

### Removing Requirements

**Never delete requirements** - instead:

1. Mark them as `[DEPRECATED]` in the heading
2. Add a brief explanation of why it was deprecated
3. Reference the replacement requirement if applicable
4. Keep the requirement ID in the sequence

### Refactoring Requirements

When reorganizing requirements:

1. **Maintain all existing requirement IDs**
2. **Update all specification documents** that reference affected requirements
3. **Verify all backtracking links** remain functional
4. **Document the refactoring** in commit messages

## Example Requirements Document

```asciidoc
= JWT Token Processor Requirements
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Overview

This document outlines the requirements for the JWT Token Processor, a component designed to validate, parse, and process JSON Web Tokens in enterprise applications.

== General Requirements

[#JWT-1]
=== JWT-1: Token Validation Framework

* The system must validate JWT tokens according to RFC 7519
* Token validation must check signature, expiration, and issuer
* Invalid tokens must be rejected with clear error messages
* Validation failures must be logged with appropriate security context

[#JWT-1.1]
==== JWT-1.1: Signature Validation

* The system must support RSA and HMAC signature algorithms
* Public keys must be configurable per issuer
* Signature validation failures must be logged as security events

[#JWT-2]
=== JWT-2: Token Parsing

* The system must parse JWT token headers and claims
* Parsing must handle both compact and JSON serialization formats
* Malformed tokens must result in clear parsing exceptions
* Custom claims must be accessible through a consistent API

== Functional Requirements

[#JWT-3]
=== JWT-3: Claim Extraction

* The system must extract standard JWT claims (iss, sub, aud, exp, iat)
* Custom claims must be extractable by name
* Missing optional claims must not cause failures
* Claim values must be typed appropriately (string, number, date)

[#JWT-4]
=== JWT-4: Token Expiration Handling

* The system must check token expiration timestamps
* Expired tokens must be rejected
* Clock skew tolerance must be configurable
* Expiration events must be logged for audit purposes

== Non-Functional Requirements

[#JWT-5]
=== JWT-5: Performance Requirements

* Token validation must complete within 50ms for 95% of requests
* The system must support concurrent token validation
* Memory usage must scale linearly with concurrent validation requests

[#JWT-6]
=== JWT-6: Security Requirements

* The system must protect against timing attacks
* Private keys must never be logged or exposed
* Token validation must be constant-time where possible
* Security-relevant events must be logged with full context
```

## Integration with Other Documentation

### Linking to Specifications

Requirements should reference specification documents:

```asciidoc
[#API-AUTH-1]
=== API-AUTH-1: Authentication Framework

* The system must support OAuth 2.0 authentication
* Token management must follow security best practices

See the link:specification/authentication.adoc[Authentication Specification] for implementation details.
```

### Linking from Specifications

Specifications must include backtracking links to requirements:

```asciidoc
== OAuth 2.0 Implementation
_See Requirement link:../Requirements.adoc#API-AUTH-1[API-AUTH-1: Authentication Framework]_

This section details the OAuth 2.0 implementation...
```

## Quality Standards

### Clarity

- Use clear, unambiguous language
- Avoid implementation details
- Focus on what, not how
- Define domain-specific terms

### Completeness

- Cover all functional areas
- Include non-functional requirements
- Address edge cases and error conditions
- Document constraints and limitations

### Consistency

- Use the same terminology throughout
- Follow the same format for all requirements
- Maintain consistent numbering
- Use the same level of detail across requirements

### Testability

- Each requirement must be verifiable
- Define clear success criteria
- Specify measurable outcomes
- Enable test case derivation

## Common Anti-Patterns to Avoid

### Over-Specification

**Bad**:
```asciidoc
The system must use a HashMap to store tokens with a capacity of 1000.
```

**Good**:
```asciidoc
The system must cache validated tokens to improve performance.
```

### Vague Requirements

**Bad**:
```asciidoc
The system should be fast and secure.
```

**Good**:
```asciidoc
Token validation must complete within 50ms for 95% of requests.
The system must validate token signatures using industry-standard algorithms.
```

### Implementation Details

**Bad**:
```asciidoc
The TokenValidator class must use the JWTVerifier from the jose4j library.
```

**Good**:
```asciidoc
The system must validate JWT signatures according to RFC 7519.
```

### Duplicate Information

**Bad**: Repeating the same requirement in multiple places

**Good**: Reference the original requirement using links

## Related Standards

### Related Skills in Bundle

- `cui-requirements:specification-documentation` - Standards for creating specification documents with traceability to requirements
- `cui-requirements:project-setup` - Standards for setting up requirements documentation in new projects
- `cui-requirements:planning-documentation` - Standards for creating planning documents linked to requirements
- `cui-requirements:implementation-linkage` - Standards for linking requirements to implementation code

### External Standards

- AsciiDoc formatting standards (for document structure)
- Git commit standards (for requirement change tracking)
