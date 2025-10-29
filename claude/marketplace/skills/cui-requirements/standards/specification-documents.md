# Specification Documents Structure and Format

## Purpose
Defines the structure and format for specification documents in CUI projects, ensuring consistency and traceability to requirements.

## Document Location and Naming
1. The main specification document must be located at `doc/Specification.adoc`
2. Individual specification documents must be located in `doc/specification/` directory
3. Individual specification documents must follow a consistent naming convention:
   a. Use lowercase with hyphens for multi-word names
   b. Example: `technical-components.adoc`, `error-handling.adoc`
4. All specification documents must follow AsciiDoc format

## Main Specification Document Structure
1. The main specification document (`Specification.adoc`) must include:
   a. Title: `= [Project Name] Specification`
   b. Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
   c. Overview section with a backtracking link to the corresponding requirement
   d. Document Structure section listing all individual specification documents with links
   e. Each section must include a backtracking link to the corresponding requirement

## Individual Specification Document Structure
1. Each individual specification document must include:
   a. Title: `= [Project Name] [Component/Feature]`
   b. Table of contents: `:toc:`, `:toclevels: 3`, `:toc-title: Table of Contents`, `:sectnums:`
   c. A link back to the main specification document at the top: `link:../Specification.adoc[Back to Main Specification]`
   d. Sections organized by component, feature, or aspect
   e. Each section must include a backtracking link to the corresponding requirement

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
1. Specifications must provide detailed implementation guidance
2. Include code examples where appropriate
3. Provide diagrams for complex components or workflows
4. Reference external documentation when necessary
5. Ensure all implementation details are traceable to requirements

## Related Documentation
* [Requirements Document Structure](requirements-document.md)
* [New Project Guide](../../../cui-project-setup/standards/new-project-guide.md)
