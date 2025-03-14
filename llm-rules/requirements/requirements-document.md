# Requirements Document Structure and Format

## Document Location and Naming
1. Requirements must be located in the project under `doc/Requirements.adoc`
2. The document must follow AsciiDoc format with proper headings, sections, and formatting

## Document Structure
1. The document must include:
   - Title: `= [Project Name] Requirements`
   - Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
   - Overview section explaining the purpose of the requirements
   - General Requirements section
   - Specific requirements sections organized by component or feature

## Requirements Format
1. Each requirement must have a unique ID with a consistent prefix
   - Format: `[#PREFIX-NUM]`
   - Example: `[#NIFI-AUTH-1]`
2. Each requirement must have a descriptive title
   - Format: `=== PREFIX-NUM: Descriptive Title`
   - Example: `=== NIFI-AUTH-1: REST API Support Enhancement`
3. Requirements must be organized hierarchically
   - Major requirements: Level 3 headings (`===`)
   - Sub-requirements: Level 4 headings (`====`)
4. Each requirement must be described using bullet points
   - Main points should be clear and concise
   - Use sub-bullets for additional details
5. Each requirement must be traceable to corresponding specification documents
   - Specifications must include backtracking links to requirements
   - Requirements should reference implementation specifications where appropriate

## Requirements Numbering
1. Major requirements must use a sequential number (e.g., `PREFIX-1`, `PREFIX-2`)
2. Sub-requirements must use a decimal notation (e.g., `PREFIX-1.1`, `PREFIX-1.2`)
3. Requirements must maintain a consistent numbering scheme throughout the document
4. When adding new requirements, assign the next available number in the sequence
5. Never reuse requirement IDs, even if a requirement is removed or replaced
6. When a requirement is no longer applicable, mark it as deprecated rather than removing it
   - Format: `=== PREFIX-NUM: [DEPRECATED] Descriptive Title`

## Requirements Content
1. Requirements must be specific, measurable, achievable, relevant, and time-bound ([SMART principles](https://www.atlassian.com/blog/productivity/how-to-write-smart-goals))
2. Requirements must clearly state what is needed, not how it should be implemented
3. Requirements must be testable
4. Requirements must be traceable to corresponding specification documents
5. For logging requirements, refer to [Logging Standards](../core/standards/logging-standards.md) and ensure requirements align with established standards

## Prefix Selection
1. When creating requirements for a new project, prompt the user to select a prefix
2. Provide a numbered list of recommended prefixes based on the project domain
3. Suggested prefixes should be short (3-5 characters) and relevant to the project
4. Example prefixes to recommend:
   - `NIFI-` for Apache NiFi related projects
   - `SEC-` for security-related projects
   - `API-` for API-related projects
   - `UI-` for user interface projects
   - `DB-` for database projects
   - `INT-` for integration projects

## Updating Requirements
1. When adding new requirements, maintain the existing structure and formatting
2. When modifying requirements, preserve the requirement ID and update only the content
3. When removing requirements, mark them as deprecated rather than deleting them
4. When refactoring requirements, ensure all specification documents are updated to maintain traceability
