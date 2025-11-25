---
name: doc-review-single-asciidoc
description: Validate and review a single AsciiDoc file with format, links, and content checks
---

> **DEPRECATED**: This command is deprecated. Use `/doc-doctor` instead.
> - For single file: `/doc-doctor target=<file>`
> - For thorough review: `/doc-doctor target=<file> depth=thorough`

# Review Single AsciiDoc Command

Thin orchestrator for single file AsciiDoc review. Invokes cui-documentation skill workflows.

## Parameters

- **file** (required): Path to AsciiDoc file to review
- **apply_fixes** (optional): Apply automatic fixes (default: false)

## Workflow

### Step 1: Parse and Validate Parameters

```
If file not provided:
  Show usage and exit
```

**Usage:**
```
/doc-review-single-asciidoc file=<path>

Parameters:
  file        - Required: Path to .adoc file
  apply_fixes - Optional: true to apply fixes (default: false)

Examples:
  /doc-review-single-asciidoc file=standards/java-core.adoc
  /doc-review-single-asciidoc file=README.adoc apply_fixes=true
```

### Step 2: Load Documentation Skill

```
Skill: cui-documentation-standards:cui-documentation
```

### Step 3: Execute Comprehensive Review

**Use comprehensive-review workflow** for orchestrated validation:

Execute workflow: comprehensive-review
- target: {file}
- stop_on_error: true
- apply_fixes: {apply_fixes}
- skip_content: false

This workflow handles:
- Phase 1: Format validation (fail-fast)
- Phase 2: Link verification with false-positive detection and manual Read verification
- Phase 3: Content review with ULTRATHINK tone analysis

References:
- standards/orchestration-workflow.md
- standards/link-verification-protocol.md
- standards/content-review-framework.md

Collect: format_status, link_status, content_status, all_issues

### Step 4: Generate Report

```
════════════════════════════════════════════════════════════
Single File Review: {file}
════════════════════════════════════════════════════════════

Overall Status: {overall_status}
Total Issues: {total_issues}

Format Validation: {format_status}
- Issues found: {format_issues_count}

Link Verification: {link_status}
- Broken links: {link_issues_count}

Content Review: {content_status}
- Quality score: {quality_score}/100
- Issues found: {content_issues_count}

Summary:
- ✅ Clean: {clean_aspects}
- ⚠️ Issues: {aspects_with_issues}
```

## Architecture

**Pattern**: Thin Orchestrator Command (<100 lines)
- Delegates ALL logic to cui-documentation skill workflows
- No business logic in command
- Uses Skill directive for workflow invocation

**Skill Dependency**: cui-documentation-standards:cui-documentation
- Provides: comprehensive-review workflow (orchestrates validate-format, verify-links, review-content)
- Scripts: asciidoc-validator.sh, verify-adoc-links.py, verify-links-false-positives.py, analyze-content-tone.py
- Standards: orchestration-workflow.md, link-verification-protocol.md, content-review-framework.md

## Related

- `/doc-review-technical-docs` - Batch command for all AsciiDoc files
- `cui-documentation` skill - Provides all validation workflows
