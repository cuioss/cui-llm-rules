# CUI Documentation Standards

AsciiDoc and documentation standards enforcement for CUI projects. This bundle provides comprehensive tools for validating, formatting, and reviewing technical documentation.

## Purpose

This bundle ensures documentation quality through:

1. **Format Validation** - Validate AsciiDoc structure, headers, lists, and code blocks
2. **Auto-Formatting** - Fix common formatting issues automatically
3. **Link Verification** - Verify cross-references and external links
4. **Content Review** - Analyze tone, clarity, and content quality

## Components Included

### Commands (2 goal-based orchestrators)

1. **/doc-review-single-asciidoc** - Review a single AsciiDoc file
   - Validates format compliance
   - Verifies links and cross-references
   - Reviews content quality
   - Returns comprehensive report

2. **/doc-review-technical-docs** - Batch review all AsciiDoc files
   - Discovers all .adoc files in directory
   - Reviews each file with all validations
   - Aggregates results into summary report
   - Optionally commits fixes

### Skills (1 skill with 4 workflows)

**cui-documentation** - Documentation standards skill with workflows:

| Workflow | Purpose | Script Used |
|----------|---------|-------------|
| **format-document** | Auto-fix formatting issues | `asciidoc-formatter.sh` |
| **validate-format** | Validate format compliance | `asciidoc-validator.sh` |
| **verify-links** | Verify links and xrefs | `verify-adoc-links.py` |
| **review-content** | Review content quality | `review-content.py` |

### Scripts (5 in cui-documentation skill)

- `asciidoc-formatter.sh` - Auto-fix formatting (lists, xrefs, headers)
- `asciidoc-validator.sh` - Validate AsciiDoc format compliance
- `verify-adoc-links.py` - Verify cross-references and links
- `review-content.py` - Analyze content quality and tone
- `documentation-stats.sh` - Generate documentation metrics

## Installation

```bash
/plugin install cui-documentation-standards
```

## Usage Examples

### Review Single File

```
/doc-review-single-asciidoc file=standards/java-core.adoc
```

### Review All Documentation

```
/doc-review-technical-docs
```

### Review with Fixes

```
/doc-review-technical-docs apply_fixes=true
```

### Review, Fix, and Commit

```
/doc-review-technical-docs apply_fixes=true push
```

## Architecture

```
cui-documentation-standards/
├── commands/                # 2 goal-based orchestrators
│   ├── doc-review-single-asciidoc.md
│   └── doc-review-technical-docs.md
└── skills/
    └── cui-documentation/   # Expanded skill with 4 workflows
        ├── SKILL.md         # 4 workflows: format, validate, verify, review
        ├── scripts/         # 5 automation scripts
        │   ├── asciidoc-formatter.sh
        │   ├── asciidoc-validator.sh
        │   ├── verify-adoc-links.py
        │   ├── review-content.py
        │   └── documentation-stats.sh
        └── standards/       # Documentation standards
            ├── documentation-core.md
            ├── asciidoc-formatting.md
            ├── tone-and-style.md
            ├── readme-structure.md
            └── organization-standards.md
```

## Workflow Pattern

Commands are thin orchestrators that invoke skill workflows:

```
/doc-review-single-asciidoc file=X
  └─> Skill: cui-documentation
      ├─> workflow: validate-format (asciidoc-validator.sh)
      ├─> workflow: verify-links (verify-adoc-links.py)
      └─> workflow: review-content (review-content.py)

/doc-review-technical-docs
  └─> For each .adoc file:
      └─> Skill: cui-documentation (all workflows)
```

## Bundle Statistics

- **Commands**: 2 (thin orchestrators, <100 lines each)
- **Skills**: 1 (with 4 workflows)
- **Scripts**: 5 (shell and Python)
- **Agents**: 0 (all absorbed into skill)

## Dependencies

### Inter-Bundle Dependencies

- **cui-task-workflow** (optional) - For commit workflow in batch processing

### External Dependencies

- Python 3 for link verification and content review
- Shell (bash) for formatting and validation scripts

## License

Apache-2.0

## Support

- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-documentation-standards/
