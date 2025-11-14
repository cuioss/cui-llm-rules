---
name: cui-requirements:setup
source_bundle: cui-requirements
description: Standards for setting up requirements and specification documentation in new CUI projects with proper directory structure and initial documents
version: 1.0.0
allowed-tools: []
---

# Project Setup Standards for Requirements Documentation

Standards for establishing requirements and specification documentation structure in new CUI projects, including directory layout, initial document creation, and prefix selection.

## Core Principles

### Documentation-First Approach

New projects should establish their documentation structure before implementing core functional components (i.e., before writing business logic, APIs, or main feature code). This ensures:

- Clear understanding of project goals and scope through documented and approved requirements
- Traceability from the start
- Consistent documentation practices
- Foundation for implementation guidance

### Standard Structure

All CUI projects follow a consistent documentation structure that facilitates:

- Easy navigation across projects
- Predictable document locations
- Standard tooling and processes
- Reduced onboarding time

## Directory Structure Standards

### Required Directory Layout

```
project-root/
├── doc/
│   ├── Requirements.adoc
│   ├── Specification.adoc
│   ├── LogMessages.adoc
│   └── specification/
│       ├── technical-components.adoc
│       ├── configuration.adoc
│       ├── error-handling.adoc
│       ├── testing.adoc
│       ├── security.adoc
│       ├── integration-patterns.adoc
│       └── internationalization.adoc
```

### Directory Purposes

**`doc/`**: Root documentation directory containing all project documentation

**`doc/Requirements.adoc`**: Main requirements document

**`doc/Specification.adoc`**: Main specification document (index to detailed specs)

**`doc/LogMessages.adoc`**: Logging standards and log message definitions

**`doc/specification/`**: Individual specification documents organized by concern

### Specification File Organization

Common specification documents include:

- **technical-components.adoc**: Core implementation components and architecture
- **configuration.adoc**: Configuration properties, files, and management
- **error-handling.adoc**: Error handling strategies and exception design
- **testing.adoc**: Testing approach, unit tests, integration tests
- **security.adoc**: Security requirements, authentication, authorization
- **integration-patterns.adoc**: Integration examples and patterns
- **internationalization.adoc**: i18n/l10n requirements and implementation

Projects may include additional specification documents based on their specific needs.

## Requirement Prefix Selection

### Prefix Purpose

The requirement prefix serves as:

- Unique identifier namespace for requirements
- Quick project/domain identifier
- Basis for requirement numbering scheme
- Reference point for cross-document linking

### Prefix Characteristics

**Length**: 3-5 characters

**Format**: Uppercase letters, may include hyphens

**Uniqueness**: Must be unique within your organization

**Relevance**: Should be meaningful and domain-appropriate

### Selection Process

When starting a new project:

1. **Analyze project domain**: What is the primary focus?
2. **Review recommended prefixes**: Check standard prefix list
3. **Check for conflicts**: Ensure prefix isn't already used
4. **Select prefix**: Choose the most appropriate option
5. **Document decision**: Record prefix in Requirements.adoc overview

### Recommended Prefixes by Domain

| Domain | Prefix | Usage Example | Typical Projects |
|--------|--------|---------------|------------------|
| Apache NiFi | `NIFI-` | NIFI-PROC-1 | NiFi processors, integrations |
| Security | `SEC-` | SEC-AUTH-1 | Security frameworks, auth systems |
| API Development | `API-` | API-REST-1 | REST APIs, GraphQL services |
| User Interface | `UI-` | UI-COMP-1 | UI components, frameworks |
| Database | `DB-` | DB-MIGR-1 | Database layers, migration tools |
| Integration | `INT-` | INT-KAFKA-1 | Integration middleware, connectors |
| Logging | `LOG-` | LOG-AUDIT-1 | Logging frameworks, audit systems |
| Testing | `TEST-` | TEST-PERF-1 | Testing frameworks, tools |
| Configuration | `CONF-` | CONF-MGMT-1 | Configuration management |
| Workflow | `WF-` | WF-ENGINE-1 | Workflow engines, orchestration |
| Message Queue | `MQ-` | MQ-BROKER-1 | Message queue systems |
| Cache | `CACHE-` | CACHE-DIST-1 | Caching systems |
| JWT | `JWT-` | JWT-VALID-1 | JWT processing, validation |
| Cloud | `CLOUD-` | CLOUD-DEPLOY-1 | Cloud infrastructure, deployment |

### Custom Prefixes

For projects not covered by standard prefixes:

**Guidelines**:
- Use project or product acronym
- Keep it short and memorable
- Ensure it's clearly related to the domain
- Document the prefix meaning in Requirements.adoc

**Examples**:
- Payment system: `PAY-`
- Document processing: `DOC-`
- Analytics platform: `ANLYT-`
- Notification service: `NOTIF-`

**Cross-Domain Projects**:

When a project spans multiple domains (e.g., "Security API" or "NiFi Integration"):
- **Primary domain approach**: Choose the domain that best represents the project's core purpose
  - Example: Security-focused API → Use `SEC-` with hierarchical structure: `SEC-API-1`
  - Example: NiFi processor development → Use `NIFI-` with context: `NIFI-PROC-1`
- **Composite approach**: For truly balanced multi-domain projects, create a composite prefix
  - Example: Security + API project → `SECAPI-` or `SEC-API-`
  - Example: Workflow + Integration → `WFINT-` or `WF-INT-`
- **Document the choice**: Always explain the prefix rationale in Requirements.adoc to avoid confusion

### Hierarchical Prefixes

For complex multi-component projects:

**Pattern**: `[SYSTEM]-[COMPONENT]-NUM`

**Examples**:
```
[#PLAT-AUTH-1]     # Platform Authentication requirement 1
[#PLAT-DB-1]       # Platform Database requirement 1
[#PLAT-API-1]      # Platform API requirement 1
```

## Initial Document Creation

### Requirements.adoc Template

```asciidoc
= [Project Name] Requirements
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Overview

This document outlines the requirements for [Project Name], a [brief description of what the project is and does].

Project prefix: `[PREFIX]-`

== General Requirements

[#PREFIX-1]
=== PREFIX-1: Project Overview

* [High-level project requirement 1]
* [High-level project requirement 2]
* [High-level project requirement 3]

[#PREFIX-2]
=== PREFIX-2: Core Functionality

* [Core functionality requirement 1]
* [Core functionality requirement 2]
* [Core functionality requirement 3]

== Functional Requirements

[#PREFIX-3]
=== PREFIX-3: [Feature/Component Name]

* [Specific functional requirement 1]
* [Specific functional requirement 2]

[#PREFIX-3.1]
==== PREFIX-3.1: [Sub-feature Name]

* [Detailed requirement 1]
* [Detailed requirement 2]

== Non-Functional Requirements

[#PREFIX-4]
=== PREFIX-4: Performance Requirements

* [Performance requirement 1]
* [Performance requirement 2]

[#PREFIX-5]
=== PREFIX-5: Security Requirements

* [Security requirement 1]
* [Security requirement 2]

[#PREFIX-6]
=== PREFIX-6: Logging Requirements

* [Logging requirement 1]
* [Logging requirement 2]
```

### Specification.adoc Template

```asciidoc
= [Project Name] Specification
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Overview
_See Requirement link:Requirements.adoc#PREFIX-1[PREFIX-1: Project Overview]_

This document provides the technical specification for implementing [Project Name].
For functional requirements, see link:Requirements.adoc[Requirements Document].

== Document Structure

This specification is organized into the following documents:

* link:specification/technical-components.adoc[Technical Components] - Core implementation details and architecture
* link:specification/configuration.adoc[Configuration] - Configuration properties and management
* link:specification/error-handling.adoc[Error Handling] - Error handling implementation and exception design
* link:specification/testing.adoc[Testing] - Unit and integration testing approach
* link:specification/security.adoc[Security] - Security considerations and implementation
* link:specification/integration-patterns.adoc[Integration Patterns] - Integration examples and patterns
* link:specification/internationalization.adoc[Internationalization] - i18n/l10n implementation

Additional documentation:

* link:LogMessages.adoc[Log Messages] - Logging standards and implementation
```

### Individual Specification Template

```asciidoc
= [Project Name] [Component Name]
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

link:../Specification.adoc[Back to Main Specification]

== Overview
_See Requirement link:../Requirements.adoc#PREFIX-N[PREFIX-N: Requirement Title]_

This document specifies the [component name] implementation for [Project Name].

== [Section 1 Title]
_See Requirement link:../Requirements.adoc#PREFIX-N.1[PREFIX-N.1: Sub-requirement Title]_

[Content describing the specification details]

=== Design Approach

[High-level design approach and rationale]

=== Key Components

[Description of key components and their relationships]

=== Implementation Guidance

[Specific guidance for implementation]

== [Section 2 Title]
_See Requirement link:../Requirements.adoc#PREFIX-M[PREFIX-M: Another Requirement]_

[Additional specification content]
```

### LogMessages.adoc Template

```asciidoc
= [Project Name] Log Messages
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

link:Specification.adoc[Back to Main Specification]

== Overview
_See Requirement link:Requirements.adoc#PREFIX-6[PREFIX-6: Logging Requirements]_

This document defines the log messages for [Project Name] following CUI logging standards.

== Logging Standards

All log messages must follow the CUI logging standards:

* Use LogRecords pattern for structured logging
* Include appropriate log levels (ERROR, WARN, INFO, DEBUG, TRACE)
* Provide meaningful log keys and messages
* Support internationalization where appropriate

== Log Message Definitions

=== Error Messages

==== PREFIX_ERROR_001: [Error Description]

* *Level*: ERROR
* *Message*: [Error message template]
* *Usage*: [When this error is logged]
* *Parameters*: [Any dynamic parameters]

=== Warning Messages

==== PREFIX_WARN_001: [Warning Description]

* *Level*: WARN
* *Message*: [Warning message template]
* *Usage*: [When this warning is logged]
* *Parameters*: [Any dynamic parameters]

=== Info Messages

==== PREFIX_INFO_001: [Info Description]

* *Level*: INFO
* *Message*: [Info message template]
* *Usage*: [When this info is logged]
* *Parameters*: [Any dynamic parameters]
```

## Setup Workflow

### Step-by-Step Process

1. **Create directory structure**
   ```bash
   mkdir -p doc/specification
   ```

2. **Select requirement prefix**
   - Analyze project domain
   - Choose from recommended prefixes or create custom
   - Document prefix selection

3. **Create Requirements.adoc**
   - Start from template
   - Replace `[Project Name]` with actual project name
   - Replace `PREFIX` with selected prefix
   - Fill in initial requirements based on project scope

4. **Create Specification.adoc**
   - Start from template
   - Update project name and prefix
   - Adjust specification document list based on project needs
   - Add backtracking links to requirements

5. **Create individual specification documents**
   - Create files in `doc/specification/`
   - Use template structure
   - Add backtracking links to requirements
   - Fill in specification details as available

6. **Create LogMessages.adoc**
   - Start from template
   - Define initial log message structure
   - Reference logging standards

7. **Verify structure**
   - Check all files are in correct locations
   - Verify all cross-references work
   - Ensure consistent prefix usage
   - Test document navigation

## Integration with Project Lifecycle

### Initial Project Setup

During initial project setup:

1. Create documentation structure **before** implementing core functional components (business logic, APIs, main features)
2. Define requirements based on project goals
3. Create specifications with architectural overview and design approach
4. Use specifications to guide implementation planning

### During Implementation

As implementation progresses:

1. Update specifications with detailed design decisions
2. Add implementation links as code is written
3. Update requirement status indicators
4. Keep cross-references current

### Post-Implementation

After features are implemented:

1. Update specifications to mark sections as IMPLEMENTED
2. Add links to implementation classes
3. Add links to test classes
4. Remove redundant pre-implementation examples
5. Ensure traceability is complete

## Quality Checklist

### Documentation Structure

- [ ] `doc/` directory exists at project root
- [ ] `Requirements.adoc` exists in `doc/`
- [ ] `Specification.adoc` exists in `doc/`
- [ ] `specification/` subdirectory exists
- [ ] Individual specification documents created
- [ ] `LogMessages.adoc` created if logging is required

### Content Quality

- [ ] Project name is correct and consistent
- [ ] Requirement prefix is selected and documented
- [ ] All requirements follow PREFIX-NUM format
- [ ] All requirements have unique IDs
- [ ] All specification sections have backtracking links
- [ ] All cross-references use correct relative paths
- [ ] Table of contents is configured correctly

### Traceability

- [ ] Every specification section links to a requirement
- [ ] Every requirement can be traced to specifications
- [ ] Cross-references are functional
- [ ] Document structure is navigable
- [ ] Links use consistent format

## Common Setup Issues

### Incorrect Paths in Cross-References

**Problem**: Links break when documents are in subdirectories

**Solution**: Use correct relative paths:
- From `doc/specification/`: `../Requirements.adoc#REQ-1`
- From `doc/`: `Requirements.adoc#REQ-1`

### Inconsistent Prefix Usage

**Problem**: Requirements use different prefixes within same document

**Solution**: Establish single prefix at project start, use consistently

### Missing Backtracking Links

**Problem**: Specification sections don't reference requirements

**Solution**: Add backtracking link to every major specification section

### Skipping Initial Documentation

**Problem**: Starting implementation without requirements and specifications

**Solution**: Create at least minimal requirements and specification structure before coding

## Minimal vs. Complete Setup

### Minimal Setup (MVP)

For rapid prototyping or small projects:

**When to use minimal setup**:
- Projects with < 10 requirements (limited scope doesn't justify separate specification documents)
- Expected development time < 2 weeks (short timeline favors consolidated documentation)
- Proof-of-concept work (exploratory projects where requirements may change significantly)

```
doc/
├── Requirements.adoc (basic structure, key requirements)
└── Specification.adoc (overview only)
```

Expand to complete setup as project scope increases or transitions to production.

### Complete Setup (Recommended)

For production projects:

**When to use complete setup**:
- Projects with 10+ requirements (scope justifies organized separation of concerns)
- Multi-component architecture (complexity requires detailed technical specifications)
- Intended for production deployment (production systems require comprehensive documentation)

```
doc/
├── Requirements.adoc (comprehensive)
├── Specification.adoc (full index)
├── LogMessages.adoc (if logging required)
└── specification/
    ├── technical-components.adoc
    ├── configuration.adoc
    ├── error-handling.adoc
    ├── testing.adoc
    ├── security.adoc
    └── [additional as needed]
```

## Related Standards

### Related Skills in Bundle

- `cui-requirements:requirements-authoring` - Comprehensive standards for creating and maintaining requirements and specifications
- `cui-requirements:planning` - Standards for creating planning documents after setup
- `cui-requirements:traceability` - Standards for linking documentation to implementation code

### External Standards

- AsciiDoc formatting standards (for document formatting)
- Logging standards (for LogMessages.adoc content)
- Git commit standards (for committing documentation)
