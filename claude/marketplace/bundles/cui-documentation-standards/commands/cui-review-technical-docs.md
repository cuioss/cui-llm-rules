---
name: cui-review-technical-docs
description: Execute comprehensive AsciiDoc review for all documentation files
---

# Review Technical Docs Command

Batch command for comprehensive AsciiDoc documentation review. Discovers all .adoc files and delegates to /cui-review-single-asciidoc for each file, aggregating results.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using /plugin-update-command command-name=cui-review-technical-docs update="[your improvement]"

**Areas for continuous improvement:**
1. Improved file discovery patterns and filtering
2. Better result aggregation and summary generation
3. More effective parallel execution strategies
4. Enhanced error handling for partial failures
5. Any lessons learned about batch documentation review workflows

## PARAMETERS

- **path** (optional): Root path to search for .adoc files (default: current directory)
- **apply_fixes** (optional): Apply automatic fixes where possible (default: false)
- **push** (optional): Auto-commit and push after fixes (default: false)

## WORKFLOW

### Step 1: Discover AsciiDoc Files

**Use Glob to find all .adoc files:**
```
Glob: pattern="**/*.adoc", path={path parameter or current directory}
```

**Filter results:**
- Exclude `target/` directories
- Exclude hidden directories (starting with `.`)
- Exclude `node_modules/` if present

**Validate discovery:**
```
If no files found:
  ℹ️ No AsciiDoc files found in: {path}

  Try:
  - Check path parameter
  - Verify .adoc files exist
  - Check file permissions

  Exit gracefully.
```

**Sort files:**
- Alphabetically by path
- Enables consistent reporting order

### Step 2: Review Files (Batch Pattern)

**For EACH file discovered:**

**Delegate to Layer 2 self-contained command:**
```
SlashCommand: /cui-documentation-standards:cui-review-single-asciidoc file={file_path} apply_fixes={apply_fixes}
```

**Collect results:**
- Parse structured result from each command execution
- Track file-by-file status
- Aggregate issue counts

**Error handling:**
```
If /cui-review-single-asciidoc fails for a file:
  ⚠️ Review failed: {file_path}
  Error: {error_message}

  Options:
  - [C]ontinue with remaining files
  - [R]etry this file
  - [A]bort entire review

  Track failure in failed_files list.
```

**Partial Success:**
- Continue processing remaining files after single file failure
- Report failed files in final summary
- Aggregate results from successful reviews only

### Step 3: Aggregate Results

**Calculate totals across all files:**
```
total_files = files_discovered count
files_reviewed = successful_reviews count
files_failed = failed_reviews count
files_clean = files with 0 issues
files_with_issues = files with issues > 0

total_issues = sum of all file issue counts
format_issues_total = sum of format issues across files
link_issues_total = sum of link issues across files
content_issues_total = sum of content issues across files
```

**Categorize files by status:**
- **Clean** (✅): 0 issues found
- **Minor Issues** (⚠️): 1-5 issues found
- **Major Issues** (❌): 6+ issues found
- **Failed** (💥): Review execution failed

### Step 4: Generate Comprehensive Report

**Display batch summary:**
```
╔════════════════════════════════════════════════════════════╗
║          Documentation Review Report                       ║
╚════════════════════════════════════════════════════════════╝

Files Discovered: {total_files}
Files Reviewed: {files_reviewed}
Files Failed: {files_failed}

Overall Statistics:
- Clean files: {files_clean} ✅
- Files with issues: {files_with_issues}
- Total issues found: {total_issues}

Issues by Category:
- Format issues: {format_issues_total}
- Link issues: {link_issues_total}
- Content issues: {content_issues_total}

Files by Status:
✅ Clean ({files_clean}):
{list of clean files}

⚠️  Minor Issues ({minor_issues_count}):
{list of files with 1-5 issues and issue counts}

❌ Major Issues ({major_issues_count}):
{list of files with 6+ issues and issue counts}

{if files_failed > 0}
💥 Failed Reviews ({files_failed}):
{list of failed files with error messages}
{endif}

{if total_issues > 0}
Top Recommendations:
1. {most common issue type}: affects {file_count} files
2. {second most common}: affects {file_count} files
3. {third most common}: affects {file_count} files
{endif}
```

### Step 5: Handle Fixes (if apply_fixes=true)

**If apply_fixes parameter was true:**
- Fixes were applied by /cui-review-single-asciidoc for each file
- Report files modified count
- Display: "Fixes applied to {modified_files_count} files"

**If apply_fixes parameter was false:**
- No modifications made
- Display: "Run with apply_fixes=true to auto-fix issues"

### Step 6: Commit Changes (if push flag)

**If push parameter is true AND files were modified:**

```
Task:
  subagent_type: commit-changes
  description: Commit documentation fixes
  prompt: |
    Commit all modified AsciiDoc files.

    Commit message: "docs: fix AsciiDoc issues across {modified_files_count} files

    - Format issues: {format_issues_fixed}
    - Link issues: {link_issues_fixed}
    - Content issues: {content_issues_fixed}

    Total issues resolved: {total_issues_fixed}"

    Push to remote.
```

**Error handling:**
- If commit fails: Display error but don't rollback fixes
- Files remain modified in working directory
- User can commit manually

## STATISTICS TRACKING

Track throughout workflow:
- `total_files`: Files discovered
- `files_reviewed`: Successfully reviewed files
- `files_failed`: Failed review executions
- `files_clean`: Files with 0 issues
- `files_with_issues`: Files with 1+ issues
- `total_issues`: Sum of all issues across all files
- `format_issues_total`: Total format issues
- `link_issues_total`: Total link issues
- `content_issues_total`: Total content issues
- `modified_files_count`: Files modified (if apply_fixes=true)

Display all statistics in final report.

## CRITICAL RULES

**Three-Layer Pattern (Layer 1 - Batch):**
- This command discovers files and delegates to Layer 2
- Uses SlashCommand (NOT Task) to invoke /cui-review-single-asciidoc
- Layer 2 (/cui-review-single-asciidoc) orchestrates Layer 3 agents
- This enables: reusability, testability, parallel execution

**Batch Processing:**
- Process all files even if some fail
- Aggregate results from successful reviews
- Report failures separately
- Never abort entire batch due to single file failure

**Delegation Pattern:**
- Delegate to /cui-review-single-asciidoc for EACH file
- Let Layer 2 command handle agent orchestration
- Don't invoke agents directly from this command
- Collect structured results for aggregation

**Error Resilience:**
- Continue on single file failure
- Track and report all failures
- Provide partial results
- Enable user decisions on retry/skip/abort

## USAGE EXAMPLES

**Review all docs in current directory:**
```
/cui-review-technical-docs
```

**Review specific directory:**
```
/cui-review-technical-docs path=standards/
```

**Review and apply fixes:**
```
/cui-review-technical-docs apply_fixes=true
```

**Review, fix, and commit:**
```
/cui-review-technical-docs apply_fixes=true push
```

## ARCHITECTURE

**Pattern**: Three-Layer Batch Command (Layer 1)

```
Layer 1: /cui-review-technical-docs (THIS COMMAND)
  ├─> Glob for all *.adoc files
  ├─> For each file:
  │    └─> SlashCommand(/cui-review-single-asciidoc file={path})
  └─> Aggregate results and report

Layer 2: /cui-review-single-asciidoc
  ├─> Task(asciidoc-format-validator)
  ├─> Task(asciidoc-link-verifier)
  └─> Task(asciidoc-content-reviewer)

Layer 3: Focused agents
  └─> Execute specific validation only
```

**Why This Works:**
- ✅ Commands can invoke other commands (SlashCommand available)
- ✅ Layer 2 commands are reusable (users can call /cui-review-single-asciidoc directly)
- ✅ Layer 3 agents are focused (no orchestration, no Task delegation)
- ✅ Scalable (handles 1 or 1000 files same way)
- ✅ Testable (test each layer independently)

**Reference**: See architecture-rules.md Rule 8 (Three-Layer Pattern)

## RELATED

- `/cui-review-single-asciidoc` - Self-contained single file review (Layer 2)
- `asciidoc-format-validator` - Format validation agent (Layer 3)
- `asciidoc-link-verifier` - Link verification agent (Layer 3)
- `asciidoc-content-reviewer` - Content review agent (Layer 3)
- `commit-changes` - Commit utility agent
