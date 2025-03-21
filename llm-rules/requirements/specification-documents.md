# Specification Documents Structure and Format

> **Note:** This document has been migrated to the standards directory. Please refer to the [Specification Documents Structure](/standards/requirements/specification-documents.adoc) for the current version.

## Migration Notice
The detailed specification document standards have been migrated to the standards directory in AsciiDoc format. Please refer to the following documents for the current standards:

- [Specification Documents Structure](/standards/requirements/specification-documents.adoc)
- [Requirements Document Structure](/standards/requirements/requirements-document.adoc)
- [New Project Guide](/standards/requirements/new-project-guide.adoc)
1. Specifications must provide detailed implementation guidance for each requirement
2. Specifications must include:
   - Technical details
   - Code examples where appropriate
   - Interface definitions
   - Data structures
   - Algorithms
   - Error handling
   - Testing approaches
3. Code examples must be formatted using AsciiDoc source blocks:
   ```
   [source,java]
   ----
   // Code example
   ----
   ```
4. Each specification section should directly address one or more requirements
5. Complex implementations should include diagrams where appropriate
   - Use PlantUML or other diagramming tools
   - Include both the diagram source and rendered image
6. For logging specifications, refer to [Logging Implementation Guide](../java/logging-implementation.md) and [Logging Testing Guide](../testing/logging-testing.md)

## Examples

### Example Backtracking Link
```
_See Requirement link:../Requirements.adoc#NIFI-AUTH-1[NIFI-AUTH-1: REST API Support Enhancement]_

This section describes the implementation of the REST API support enhancement...
```

### Example Main Specification Document Structure
```
= Project Name Specification
:toc:
:toclevels: 3
:toc-title: Table of Contents
:sectnums:

== Overview
_See Requirement link:Requirements.adoc#PREFIX-1[PREFIX-1: Project Overview]_

This document provides the technical specification for implementing Project Name.
For functional requirements, see link:Requirements.adoc[Requirements Document].

== Document Structure
This specification is organized into the following documents:

* link:specification/technical-components.adoc[Technical Components] - Core implementation details
* link:specification/configuration.adoc[Configuration] - Configuration properties and UI
...

## Standard Specification Documents
The following standard specification documents should be included for comprehensive projects:
1. `technical-components.adoc` - Core implementation details
2. `configuration.adoc` - Configuration properties and UI
3. `error-handling.adoc` - Error handling implementation
4. `testing.adoc` - Unit and integration testing
5. `security.adoc` - Security considerations
6. `integration-patterns.adoc` - Integration examples
7. `internationalization.adoc` - i18n implementation

## Dialog Instructions
1. When a user says "add to requirements", this means adding to `Requirements.adoc`
2. When a user says "add to specifications", this means adding to the corresponding document under `specification/`
3. Always ensure that new requirements have corresponding specification entries
4. Always ensure that new specification entries have backtracking links to requirements
