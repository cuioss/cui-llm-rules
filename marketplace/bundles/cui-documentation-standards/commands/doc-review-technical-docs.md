---
name: doc-review-technical-docs
description: Execute comprehensive AsciiDoc review for all documentation files
---

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

### Step 4: Review Each File

For each discovered file, execute:

**4.1: Format Validation**
Execute workflow: validate-format
- target: {file}
- apply_fixes: {apply_fixes}

**4.2: Link Verification**
Execute workflow: verify-links
- target: {file}

**4.3: Content Review**
Execute workflow: review-content
- target: {file}

Collect results per file.

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
- cui-documentation-standards:cui-documentation - Validation workflows
- cui-task-workflow:cui-git-workflow - Commit workflow (optional)

## Related

- `/doc-review-single-asciidoc` - Single file review command
- `cui-documentation` skill - Provides all validation workflows
