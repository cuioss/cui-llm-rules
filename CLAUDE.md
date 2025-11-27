# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains LLM rules and standards for CUI (Common User Interface) OSS projects. It serves as a comprehensive documentation system defining coding standards, processes, and guidelines for AI assistants working with CUI codebases.

## Architecture

### Documentation Structure
- `/standards/` - Primary standards documentation in AsciiDoc format, organized by domain (Java, JavaScript, CSS, Testing, Documentation, Logging)
- Root README files provide entry points and overview documentation
- Clear separation between standards (technical requirements) and implementation processes

### Document Format
All standards use AsciiDoc format with consistent structure:

- Table of contents on left side
- Section numbering enabled
- Cross-references using `xref:path/to/document.adoc[Link Text]` syntax
- Standard header format with `:toc: left`, `:toclevels: 3`, `:sectnums:`
- **AsciiDoc Grammar**: Always ensure proper AsciiDoc formatting, especially for lists - there must always be a blank line before any list (consult AsciiDoc documentation when in doubt)

## Key Standards Categories

- **Java Standards** - Java development standards including DSL-style constants pattern
- **JavaScript Standards** - Modern JavaScript, web components, project structure, Maven integration, linting, testing, JSDoc
- **CDI/Quarkus Standards** - CDI aspects, container standards, integration testing, security
- **CSS Standards** - Development standards, linting, formatting, best practices
- **Testing Standards** - Core testing requirements and quality standards
- **Documentation Standards** - General documentation, Javadoc standards and maintenance, README structure
- **Logging Standards** - Core logging requirements, implementation guide, testing guide
- **Requirements Standards** - Requirements documents, specifications, new project guide

## Documentation Review Guidelines

When performing comprehensive documentation review/rework:

### Quality Standards
- **Consistency**: Ensure uniform terminology, formatting, and structure across all documents
- **Completeness**: Verify all standards areas are fully documented without gaps
- **Correctness**: Validate all technical information and cross-references
- **Focus**: Keep content concise but preserve all essential information

### Content Requirements
- **No Duplication**: Eliminate duplicate information across documents; use cross-references instead
- **Current State Only**: Document present requirements only - remove transitional, status, or deprecation information
- **No Version History**: NEVER add version history, changelogs, "RECENT IMPROVEMENTS", "RECENT CHANGES", or dated update sections to any documentation
- **No Timestamps**: NEVER add dates, version numbers, or timestamps to document content
- **Source Attribution**: Always link to authoritative sources when referencing best practices or external standards
- **Standards Linking**: Cross-reference related standards documents using `xref:` syntax

### Document Maintenance
- Update all cross-references when restructuring content
- Verify all `xref:` links remain valid after changes
- Maintain AsciiDoc formatting conventions and document header structure
- Focus on technical requirements rather than implementation procedures

### File Structure and Organization
- **Adapt structure when necessary**: Reorganize files and directories to improve logical organization and usability
- **Single aspect per document**: Each document should represent one coherent aspect or domain; split overly broad documents into focused components
- **Logical linking**: Use README files to provide overview and link related documents together in a coherent structure
- **Optimal document size**: Documents should be neither too large (>400 lines) nor too small (<50 lines) - aim for comprehensive but focused content
- **Consistent naming**: Use self-describing, consistent file naming conventions (e.g., `kebab-case.adoc`, descriptive names that clearly indicate content)
- **Cross-reference updates**: When restructuring, ensure all cross-references are updated to reflect new file locations and names

## Development Notes

- This is a documentation-only repository with no build system, compilation, or testing
- Uses standard git workflow on main branch
- Allways use target-directory for documents or scripts you create on the fly. Do not use temp or proliferate within working-directory. Allways use proper tools  like Edit, Read, Write, NEVER use stuff like echo, cat and such