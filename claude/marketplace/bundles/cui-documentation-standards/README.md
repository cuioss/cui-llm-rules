# CUI Documentation Standards

## Purpose

AsciiDoc and documentation standards enforcement for CUI projects. This bundle provides specialized tools for reviewing, validating, and maintaining technical documentation according to CUI project standards including proper AsciiDoc formatting, cross-references, and content quality.

## Components Included

This bundle includes the following components:

### Agents
- **asciidoc-reviewer** - Reviews AsciiDoc documents for standards compliance and quality

### Commands
- **review-technical-docs** - Orchestrates comprehensive documentation review workflow

### Skills
- **cui-documentation** - Documentation standards including AsciiDoc conventions, structure requirements, and quality guidelines

## Installation Instructions

To install this plugin bundle, run:

```
/plugin install cui-documentation-standards
```

This will make all agents, commands, and skills available in your Claude Code environment.

## Usage Examples

### Example 1: Review Technical Documentation

Use the review-technical-docs command for comprehensive documentation review:

```
/review-technical-docs

Review all AsciiDoc documentation in the standards/ directory.
```

The command will:
1. Identify all AsciiDoc files in scope
2. Review each document for standards compliance
3. Check formatting (headers, TOC, section numbering)
4. Validate cross-references and links
5. Assess content quality and completeness
6. Report issues with specific line numbers
7. Suggest improvements

### Example 2: Review Single Document

Use asciidoc-reviewer for focused document review:

```
/agent asciidoc-reviewer

Review the Java coding standards document at standards/java/java-core-standards.adoc
```

The agent will:
- Load cui-documentation skill for standards reference
- Validate AsciiDoc formatting and structure
- Check for required document header (`:toc: left`, `:toclevels:`, `:sectnums:`)
- Verify blank lines before lists (critical AsciiDoc grammar rule)
- Validate cross-reference syntax (`xref:` usage)
- Assess content organization and clarity
- Check for duplication or inconsistencies
- Provide detailed feedback with corrections

### Example 3: Validate Documentation Structure

Review documentation organization and linking:

```
/agent asciidoc-reviewer

Verify that all cross-references in the documentation standards are valid and properly formatted.
```

The agent will:
- Parse all `xref:` references
- Verify target files exist
- Check reference syntax correctness
- Identify broken or invalid links
- Suggest proper cross-reference patterns
- Validate link text clarity

### Example 4: Pre-Commit Documentation Check

Before committing documentation changes:

```
/review-technical-docs

Review my changes to the CSS standards documentation for quality and compliance.
```

This ensures documentation changes meet CUI standards before submission.

## Dependencies

### Inter-Bundle Dependencies
- None - This bundle is self-contained and has no dependencies on other plugin bundles

### External Dependencies
- AsciiDoc files (.adoc) to review
- No build tools required (documentation-only workflow)

### Internal Component Dependencies
- **review-technical-docs** command invokes **asciidoc-reviewer** agent
- **asciidoc-reviewer** agent automatically loads **cui-documentation** skill for standards reference

### Standards Enforced
The cui-documentation skill defines requirements including:
- AsciiDoc formatting conventions
- Document structure requirements (TOC, section numbering)
- Cross-reference patterns
- Content quality standards (consistency, completeness, correctness)
- Grammar rules (blank lines before lists)
- Header format and metadata
