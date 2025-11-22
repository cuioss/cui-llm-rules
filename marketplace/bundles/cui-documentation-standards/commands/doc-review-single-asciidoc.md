---
name: doc-review-single-asciidoc
description: Validate and review a single AsciiDoc file with format, links, and content checks
---

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

### Step 3: Execute Validation Workflows

Execute three workflows in sequence:

**3.1: Format Validation**

Execute workflow: validate-format
- target: {file}
- apply_fixes: {apply_fixes}

Collect: format_status, format_issues

**3.2: Link Verification**

Execute workflow: verify-links
- target: {file}
- fix_links: {apply_fixes}

Collect: link_status, link_issues

**3.3: Content Review**

Execute workflow: review-content
- target: {file}
- apply_fixes: {apply_fixes}

Collect: content_status, content_issues

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
- Provides: validate-format, verify-links, review-content workflows
- Scripts: asciidoc-validator.sh, verify-adoc-links.py, review-content.py

## Related

- `/doc-review-technical-docs` - Batch command for all AsciiDoc files
- `cui-documentation` skill - Provides all validation workflows
