# Specification Standards

## Purpose
Defines the structure and format for specification documents in CUI projects, ensuring consistency and traceability to requirements.

## Document Location and Naming

* The main specification document must be located at `doc/Specification.adoc`
* Individual specification documents must be located in `doc/specification/` directory
* Individual specification documents must follow a consistent naming convention:
  * Use lowercase with hyphens for multi-word names
  * Example: `technical-components.adoc`, `error-handling.adoc`
* All specification documents must follow AsciiDoc format

## Main Specification Document Structure

The main specification document (`Specification.adoc`) must include:

1. Title: `= [Project Name] Specification`
2. Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
3. Overview section with a backtracking link to the corresponding requirement
4. Document Structure section listing all individual specification documents with links
5. Each section must include a backtracking link to the corresponding requirement

### Example Main Specification

```asciidoc
= Project Name Specification
:toc:
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Overview
_See Requirement link:Requirements.adoc#PREFIX-1[PREFIX-1: Project Overview]_

This document provides the technical specification for implementing Project Name.
For functional requirements, see link:Requirements.adoc[Requirements Document].

== Document Structure
This specification is organized into the following documents:

* link:specification/technical-components.adoc[Technical Components]
* link:specification/configuration.adoc[Configuration]
* link:specification/error-handling.adoc[Error Handling]
* link:specification/testing.adoc[Testing]
* link:specification/security.adoc[Security]
* link:specification/integration-patterns.adoc[Integration Patterns]
* link:specification/internationalization.adoc[Internationalization]
* link:LogMessages.adoc[Log Messages]
```

## Individual Specification Document Structure

Each individual specification document must include:

1. Title: `= [Project Name] [Component/Feature]`
2. Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
3. A link back to the main specification document at the top: `link:../Specification.adoc[Back to Main Specification]`
4. Sections organized by component, feature, or aspect
5. Each section must include a backtracking link to the corresponding requirement

### Example Individual Specification

```asciidoc
= Project Name Technical Components
:toc:
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

link:../Specification.adoc[Back to Main Specification]

== Core Components
_See Requirement link:../Requirements.adoc#PREFIX-2[PREFIX-2: Core Functionality]_

This section describes the core components of the Project Name implementation.

=== Component 1
_See Requirement link:../Requirements.adoc#PREFIX-2.1[PREFIX-2.1: Sub-requirement]_

The Component 1 is responsible for...

[source,java]
----
public class Component1 {
    // Implementation details
}
----
```

## Backtracking Links Format

Each specification section must include a backtracking link to the corresponding requirement.

### Format Rules

1. The backtracking link must follow this exact format:
   ```
   _See Requirement link:../Requirements.adoc#PREFIX-NUM[PREFIX-NUM: Requirement Title]_
   ```

2. For specification files in subdirectories, use relative paths:
   ```
   _See Requirement link:../Requirements.adoc#PREFIX-NUM[PREFIX-NUM: Requirement Title]_
   ```

3. For specification files in the root directory, use direct path:
   ```
   _See Requirement link:Requirements.adoc#PREFIX-NUM[PREFIX-NUM: Requirement Title]_
   ```

4. There must be exactly ONE empty line after each backtracking link before the content begins
5. This empty line is required to create a proper paragraph separation in the rendered document

## Specification Content

* Specifications must provide detailed implementation guidance
* Include code examples where appropriate
* Provide diagrams for complex components or workflows
* Reference external documentation when necessary
* Ensure all implementation details are traceable to requirements

## Common Specification Documents

Typical individual specification documents include:

1. **technical-components.adoc**: Core implementation details
2. **configuration.adoc**: Configuration properties and UI
3. **error-handling.adoc**: Error handling implementation
4. **testing.adoc**: Unit and integration testing
5. **security.adoc**: Security considerations
6. **integration-patterns.adoc**: Integration examples
7. **internationalization.adoc**: i18n implementation

## Maintaining Traceability

1. Always ensure each specification section has a backtracking link to a requirement
2. When adding new requirements, update the corresponding specification documents
3. When updating specifications, ensure they remain aligned with requirements
4. Regularly review documentation to ensure consistency and completeness

## Quality Checklist

- [ ] Main specification document in correct location
- [ ] Individual specifications in doc/specification/ directory
- [ ] All documents have proper AsciiDoc headers
- [ ] Backtracking links to requirements present
- [ ] Navigation links between documents functional
- [ ] Code examples complete and compilable
- [ ] All implementation details traceable to requirements
- [ ] Empty line after backtracking links

## References

* Requirements Core: requirements-core.md
