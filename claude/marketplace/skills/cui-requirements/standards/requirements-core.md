# Requirements Core Standards

## Purpose
Defines the structure and format for requirements documents in CUI projects, ensuring consistency and traceability.

## Document Location and Naming

* Requirements must be located in the project under `doc/Requirements.adoc`
* The document must follow AsciiDoc format with proper headings, sections, and formatting

## Document Structure

The document must include:

1. Title: `= [Project Name] Requirements`
2. Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
3. Overview section explaining the purpose of the requirements
4. General Requirements section
5. Specific requirements sections organized by component or feature

## Requirements Format

### Requirement IDs

Each requirement must have a unique ID with a consistent prefix:

* Format: `[#PREFIX-NUM]`
* Example: `[#NIFI-AUTH-1]`

### Requirement Titles

Each requirement must have a descriptive title:

* Format: `=== PREFIX-NUM: Descriptive Title`
* Example: `=== NIFI-AUTH-1: REST API Support Enhancement`

### Requirements Organization

Requirements must be organized hierarchically:

* Major requirements: Level 3 headings (`===`)
* Sub-requirements: Level 4 headings (`====`)

### Requirements Description

Each requirement must be described using bullet points:

* Main points should be clear and concise
* Use sub-bullets for additional details

### Traceability

Each requirement must be traceable to corresponding specification documents:

* Specifications must include backtracking links to requirements
* Requirements should reference implementation specifications where appropriate

## Requirements Numbering

* Major requirements must use a sequential number (e.g., `PREFIX-1`, `PREFIX-2`)
* Sub-requirements must use a decimal notation (e.g., `PREFIX-1.1`, `PREFIX-1.2`)
* Requirements must maintain a consistent numbering scheme throughout the document
* When adding new requirements, assign the next available number in the sequence
* Never reuse requirement IDs, even if a requirement is removed or replaced
* When a requirement is no longer applicable, mark it as deprecated rather than removing it:
  * Format: `=== PREFIX-NUM: [DEPRECATED] Descriptive Title`

## Requirements Content

* Requirements must be specific, measurable, achievable, relevant, and time-bound ([SMART principles](https://www.atlassian.com/blog/productivity/how-to-write-smart-goals))
* Requirements must clearly state what is needed, not how it should be implemented
* Requirements must be testable
* Requirements must be traceable to corresponding specification documents
* For logging requirements, refer to the logging standards and ensure requirements align with established standards

## Prefix Selection

When creating requirements for a new project:

1. Prompt the user to select a prefix
2. Provide a numbered list of recommended prefixes based on the project domain
3. Suggested prefixes should be short (3-5 characters) and relevant to the project

### Example Prefixes

* `NIFI-` for Apache NiFi related projects
* `SEC-` for security-related projects
* `API-` for API-related projects
* `UI-` for user interface projects
* `DB-` for database projects
* `INT-` for integration projects

## Updating Requirements

* When adding new requirements, maintain the existing structure and formatting
* When modifying requirements, preserve the requirement ID and update only the content
* When removing requirements, mark them as deprecated rather than deleting them
* When refactoring requirements, ensure all specification documents are updated to maintain traceability

## Example Requirements Document Structure

```asciidoc
= Project Name Requirements
:toc:
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Overview
This document outlines the requirements for Project Name...

== General Requirements

[#PREFIX-1]
=== PREFIX-1: Project Overview
* High-level requirement 1
* High-level requirement 2

[#PREFIX-2]
=== PREFIX-2: Core Functionality
* Core functionality requirement 1
* Core functionality requirement 2

[#PREFIX-2.1]
==== PREFIX-2.1: Sub-requirement
* Detailed requirement 1
* Detailed requirement 2
```

## Quality Checklist

- [ ] Document location correct (doc/Requirements.adoc)
- [ ] Proper AsciiDoc header with all required attributes
- [ ] Unique requirement IDs with consistent prefix
- [ ] Descriptive titles for all requirements
- [ ] Hierarchical organization maintained
- [ ] Requirements follow SMART principles
- [ ] All requirements are testable
- [ ] Traceability links present

## References

* Specification Standards: specification-standards.md
