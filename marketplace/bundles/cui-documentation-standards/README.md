# CUI Documentation Standards

## Purpose

AsciiDoc and documentation standards enforcement for CUI projects. This bundle provides specialized tools for reviewing, validating, and maintaining technical documentation according to CUI project standards including proper AsciiDoc formatting, cross-references, and content quality.

## Components Included

This bundle includes the following components:

### Agents (Focused Layer 3)
- **asciidoc-format-validator** - Validates AsciiDoc formatting and structure using automated scripts (focused validator)
- **asciidoc-auto-formatter** - Auto-fixes common AsciiDoc formatting issues with safety features (focused executor)
- **asciidoc-link-verifier** - Verifies cross-references and links in AsciiDoc documents (focused validator)
- **asciidoc-content-reviewer** - Reviews AsciiDoc content for quality, tone, and completeness (focused validator)

### Commands
- **/doc-review-technical-docs** - Layer 1 batch command that orchestrates review of all AsciiDoc files (Three-Layer Pattern)
- **/doc-review-single-asciidoc** - Layer 2 self-contained command that validates a single AsciiDoc file by coordinating the three focused validator agents

### Skills
- **cui-documentation** - Documentation standards including AsciiDoc conventions, structure requirements, and quality guidelines

### Utility Scripts
The bundle includes four powerful utility scripts in `skills/cui-documentation/scripts/`:

- **asciidoc-validator.sh** - Comprehensive format validation with multiple output formats (console, JSON, XML, JUnit)
- **asciidoc-formatter.sh** - Auto-fixes formatting issues (blank lines, xref syntax, headers, whitespace) with dry-run and backup modes
- **verify-adoc-links.py** - Validates cross-reference links, checks broken references, verifies anchor existence
- **documentation-stats.sh** - Generates comprehensive metrics (lines, words, sections, cross-references, code blocks)

These scripts power the specialized agents and can also be used directly for CI/CD integration.

## Installation Instructions

To install this plugin bundle, run:

```
/plugin install cui-documentation-standards
```

This will make all agents, commands, and skills available in your Claude Code environment.

## Usage Examples

### Example 1: Review All Technical Documentation (Three-Layer Pattern)

Use the /doc-review-technical-docs command for comprehensive batch review:

```
/doc-review-technical-docs

Review all AsciiDoc documentation in the standards/ directory.
```

**Architecture** (Pattern 2 - Three-Layer):
```
/doc-review-technical-docs (Layer 1: Batch)
  ├─> Glob *.adoc to find all files
  ├─> For each file:
  │    └─> SlashCommand(/doc-review-single-asciidoc {file}) (Layer 2: Self-Contained)
  │         ├─> Task(asciidoc-format-validator) (Layer 3: Focused)
  │         ├─> Task(asciidoc-link-verifier) (Layer 3: Focused)
  │         └─> Task(asciidoc-content-reviewer) (Layer 3: Focused)
  └─> Aggregate results from all files
```

The command will:
1. Identify all AsciiDoc files in scope
2. Delegate to /doc-review-single-asciidoc for each file
3. Each file gets validated by three focused agents
4. Aggregate and report all issues

### Example 2: Review Single Document

Use the /doc-review-single-asciidoc command for focused document review:

```
/doc-review-single-asciidoc standards/java/java-core-standards.adoc
```

**Architecture** (Pattern 1 - Self-Contained):
```
/doc-review-single-asciidoc (Layer 2: Self-Contained)
  ├─> Task(asciidoc-format-validator) - Check formatting and structure
  ├─> Task(asciidoc-link-verifier) - Verify cross-references and links
  ├─> Task(asciidoc-content-reviewer) - Review content quality
  └─> Combine results into comprehensive report
```

The command will:
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

### Example 4: Auto-Fix Formatting Issues

Use the asciidoc-auto-formatter agent to automatically fix common issues:

```
/agent asciidoc-auto-formatter

Preview formatting fixes for standards/java/java-core-standards.adoc (dry-run mode).
```

The agent will:
- Preview changes without modifying files (safe by default)
- Add blank lines before lists
- Convert deprecated `<<>>` syntax to `xref:`
- Fix header attributes and whitespace
- Create backups when applying changes
- Validate results after fixes

Then to apply the fixes:
```
/agent asciidoc-auto-formatter

Apply formatting fixes to standards/java/java-core-standards.adoc (create backups).
```

### Example 5: Pre-Commit Documentation Check

Before committing documentation changes:

```
/doc-review-technical-docs

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
- **doc-review-technical-docs** command invokes **asciidoc-reviewer** agent
- **asciidoc-reviewer** agent automatically loads **cui-documentation** skill for standards reference

### Standards Enforced
The cui-documentation skill defines requirements including:
- AsciiDoc formatting conventions
- Document structure requirements (TOC, section numbering)
- Cross-reference patterns
- Content quality standards (consistency, completeness, correctness)
- Grammar rules (blank lines before lists)
- Header format and metadata
