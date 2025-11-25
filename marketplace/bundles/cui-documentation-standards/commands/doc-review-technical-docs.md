---
name: doc-review-technical-docs
description: Execute comprehensive AsciiDoc review for all documentation files
---

> **DEPRECATED**: This command is deprecated. Use `/doc-doctor` instead.
> - For batch review: `/doc-doctor target=<directory>`
> - For thorough review: `/doc-doctor target=<directory> depth=thorough`

# Review Technical Docs Command

Thin orchestrator for batch AsciiDoc review. Discovers files and invokes workflows.

## Parameters

- **path** (optional): Root path to search (default: current directory)
- **apply_fixes** (optional): Apply automatic fixes (default: false)
- **push** (optional): Commit and push after fixes (default: false)

## Workflow

### Step 1: Show Usage (if no context)

```
/doc-review-technical-docs [path=<directory>] [apply_fixes=true] [push]

Parameters:
  path        - Optional: Directory to search (default: .)
  apply_fixes - Optional: Apply automatic fixes
  push        - Optional: Commit and push changes

Examples:
  /doc-review-technical-docs
  /doc-review-technical-docs path=standards/
  /doc-review-technical-docs apply_fixes=true
  /doc-review-technical-docs apply_fixes=true push
```

### Step 2: Discover AsciiDoc Files

```
Glob: pattern="{path}/**/*.adoc"

Filter:
- Exclude target/
- Exclude hidden directories
- Exclude node_modules/
```

If no files found: Report and exit

### Step 3: Load Documentation Skill

```
Skill: cui-documentation-standards:cui-documentation
```

### Step 4: Execute Comprehensive Review

**Use comprehensive-review workflow** on the directory:

Execute workflow: comprehensive-review
- target: {path}
- stop_on_error: false (continue through all files)
- apply_fixes: {apply_fixes}
- skip_content: false

This workflow handles:
- File discovery (*.adoc, non-recursive)
- Phase 1: Format validation for all files
- Phase 2: Link verification with false-positive detection and manual Read verification
- Phase 3: Content review with ULTRATHINK tone analysis
- Aggregated results across all files

References:
- standards/orchestration-workflow.md
- standards/link-verification-protocol.md
- standards/content-review-framework.md

Collect: aggregated results with per-file and overall statistics

### Step 5: Aggregate Results

```
total_files = discovered file count
total_issues = sum of all issues
format_issues_total = sum of format issues
link_issues_total = sum of link issues
content_issues_total = sum of content issues
```

### Step 6: Generate Report

```
╔════════════════════════════════════════════════════════════╗
║          Documentation Review Report                       ║
╚════════════════════════════════════════════════════════════╝

Files Discovered: {total_files}
Files Reviewed: {files_reviewed}

Overall Statistics:
- Clean files: {files_clean} ✅
- Files with issues: {files_with_issues}
- Total issues found: {total_issues}

Issues by Category:
- Format issues: {format_issues_total}
- Link issues: {link_issues_total}
- Content issues: {content_issues_total}

Files by Status:
✅ Clean: {list}
⚠️ Issues: {list with counts}
```

### Step 7: Commit Changes (if push flag)

If push=true AND files modified:

```
Skill: cui-task-workflow:cui-git-workflow

Execute workflow: commit
- message: "docs: fix AsciiDoc issues across {modified_count} files"
- push: true
```

## Architecture

**Pattern**: Thin Orchestrator Command (<100 lines)
- Discovers files via Glob
- Delegates ALL validation to cui-documentation skill workflows
- No business logic in command

**Skill Dependencies**:
- cui-documentation-standards:cui-documentation - comprehensive-review workflow (orchestrates all validation)
- cui-task-workflow:cui-git-workflow - Commit workflow (optional)

**Standards Referenced**:
- orchestration-workflow.md - Comprehensive review orchestration
- link-verification-protocol.md - Manual Read verification before link removal
- content-review-framework.md - ULTRATHINK-based tone analysis

## Related

- `/doc-review-single-asciidoc` - Single file review command
- `cui-documentation` skill - Provides all validation workflows
