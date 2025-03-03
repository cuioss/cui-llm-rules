# Specification Documents Structure and Format

## Document Location and Naming
1. The main specification document must be located at `doc/Specification.adoc`
2. Individual specification documents must be located in `doc/specification/` directory
3. Individual specification documents must follow a consistent naming convention:
   - Use lowercase with hyphens for multi-word names
   - Example: `technical-components.adoc`, `error-handling.adoc`
4. All specification documents must follow AsciiDoc format

## Main Specification Document Structure
1. The main specification document (`Specification.adoc`) must include:
   - Title: `= [Project Name] Specification`
   - Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
   - Overview section with a backtracking link to the corresponding requirement
   - Document Structure section listing all individual specification documents with links
   - Each section must include a backtracking link to the corresponding requirement

## Individual Specification Document Structure
1. Each individual specification document must include:
   - Title: `= [Project Name] [Component/Feature]`
   - Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
   - A link back to the main specification document at the top: `link:../Specification.adoc[Back to Main Specification]`
   - Sections organized by component, feature, or aspect
   - Each section must include a backtracking link to the corresponding requirement

## Backtracking Links Format
1. Each specification section must include a backtracking link to the corresponding requirement
2. The backtracking link must follow this exact format:
   ```
   _See Requirement link:../Requirements.adoc#PREFIX-NUM[PREFIX-NUM: Requirement Title]_
   ```
3. For specification files in subdirectories, use relative paths:
   ```
   _See Requirement link:../Requirements.adoc#PREFIX-NUM[PREFIX-NUM: Requirement Title]_
   ```
4. For specification files in the root directory, use direct path:
   ```
   _See Requirement link:Requirements.adoc#PREFIX-NUM[PREFIX-NUM: Requirement Title]_
   ```
5. There must be exactly ONE empty line after each backtracking link before the content begins
6. This empty line is required to create a proper paragraph separation in the rendered document

## Specification Content
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
