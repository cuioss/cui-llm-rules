---
name: review-single-asciidoc
description: Validate and review a single AsciiDoc file with format, links, and content checks
---

# Review Single AsciiDoc Command

Self-contained command that orchestrates format validation, link verification, and content review for a single AsciiDoc file.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using /cui-update-command command-name=review-single-asciidoc update="[your improvement]"

**Areas for continuous improvement:**
1. Better coordination between validation agents
2. More effective issue aggregation and reporting
3. Enhanced error recovery strategies
4. Improved fix suggestions based on issue patterns
5. Any lessons learned about single-file AsciiDoc review workflows

## PARAMETERS

- **file** (required): Path to AsciiDoc file to review (e.g., `standards/java-core.adoc`)
- **apply_fixes** (optional): Apply automatic fixes where possible (default: false)

## WORKFLOW

### Step 1: Validate Input

**Check file parameter:**
- Must be provided (required)
- Must have `.adoc` extension
- Must exist (use Read to verify)

**Error handling:**
```
If missing or invalid:
  ❌ Error: Invalid file parameter

  Required: file=path/to/document.adoc
  Received: {parameter_value}

  Example: /review-single-asciidoc file=standards/java-core.adoc
```
Exit with error status.

### Step 2: Format Validation (Layer 3 Agent)

**Launch asciidoc-format-validator:**
```
Task:
  subagent_type: asciidoc-format-validator
  description: Validate format of {file}
  prompt: |
    Validate AsciiDoc format compliance for file: {file}

    Parameters:
    - target: {file}
    - apply_fixes: {apply_fixes parameter value}

    Return all format issues found.
```

**Collect results:**
- Format issues count
- Issue categories (blank lines, headers, lists, etc.)
- Suggested fixes

**Error handling:**
- If agent fails: Set format_status = "ERROR", format_issues = ["Agent execution failed"]
- If agent succeeds: Parse results, extract issue count and details
- Continue to next step regardless (partial results acceptable)

### Step 3: Link Verification (Layer 3 Agent)

**Launch asciidoc-link-verifier:**
```
Task:
  subagent_type: asciidoc-link-verifier
  description: Verify links in {file}
  prompt: |
    Verify all xref links and external references in file: {file}

    Parameters:
    - target: {file}

    Return all broken links and invalid references.
```

**Collect results:**
- Broken links count
- Invalid xref targets
- External link issues

**Error handling:**
- If agent fails: Set link_status = "ERROR", link_issues = ["Agent execution failed"]
- If agent succeeds: Parse results, extract broken link count and details
- Continue to next step regardless (partial results acceptable)

### Step 4: Content Review (Layer 3 Agent)

**Launch asciidoc-content-reviewer:**
```
Task:
  subagent_type: asciidoc-content-reviewer
  description: Review content of {file}
  prompt: |
    Review content quality for file: {file}

    Parameters:
    - target: {file}

    Check: clarity, completeness, consistency, organization.
    Return all content quality issues.
```

**Collect results:**
- Content issues count
- Issue categories (clarity, completeness, consistency)
- Improvement suggestions

**Error handling:**
- If agent fails: Set content_status = "ERROR", content_issues = ["Agent execution failed"]
- If agent succeeds: Parse results, extract issue count and details
- Continue to next step regardless (partial results acceptable)

### Step 5: Aggregate Results

**Calculate totals:**
```
total_issues = format_issues_count + link_issues_count + content_issues_count
overall_status = "CLEAN" if total_issues == 0 else "ISSUES_FOUND"

If any agent status == "ERROR":
  overall_status = "PARTIAL"
```

**Categorize by severity:**
- CRITICAL: Broken links, invalid xrefs, missing required sections
- WARNING: Format issues, minor content problems
- SUGGESTION: Style improvements, optional enhancements

### Step 6: Generate Report

**Display comprehensive results:**
```
════════════════════════════════════════════════════════════
Single File Review: {file}
════════════════════════════════════════════════════════════

Overall Status: {overall_status}
Total Issues: {total_issues}

Format Validation: {format_status}
- Issues found: {format_issues_count}
- Categories: {format_categories}

Link Verification: {link_status}
- Broken links: {link_issues_count}
- Invalid xrefs: {invalid_xref_count}

Content Review: {content_status}
- Issues found: {content_issues_count}
- Categories: {content_categories}

Summary:
- ✅ Clean: {aspect_count where status == CLEAN}
- ⚠️  Issues: {aspect_count where status == ISSUES_FOUND}
- ❌ Errors: {aspect_count where status == ERROR}

{if total_issues > 0}
Recommendations:
{aggregated_recommendations}
{endif}
```

### Step 7: Return Structured Result

**For caller aggregation (Layer 1 batch command):**
```json
{
  "file": "{file}",
  "status": "{overall_status}",
  "total_issues": {total_issues},
  "format": {
    "status": "{format_status}",
    "issues_count": {format_issues_count},
    "details": [...]
  },
  "links": {
    "status": "{link_status}",
    "issues_count": {link_issues_count},
    "details": [...]
  },
  "content": {
    "status": "{content_status}",
    "issues_count": {content_issues_count},
    "details": [...]
  }
}
```

## STATISTICS TRACKING

Track throughout workflow:
- `format_issues_count`: Format validation issues
- `link_issues_count`: Broken links and invalid xrefs
- `content_issues_count`: Content quality issues
- `total_issues`: Sum of all issues
- `agents_executed`: Count of agents successfully executed
- `agent_failures`: Count of agent execution failures

Display all statistics in report.

## CRITICAL RULES

**Single File Focus:**
- This command handles EXACTLY ONE file
- No directory recursion
- No file discovery
- Caller provides explicit file path

**Layer 3 Agents:**
- All three agents are focused executors (format, links, content)
- Each returns results without orchestration
- This command (Layer 2) orchestrates and aggregates

**Error Resilience:**
- Continue execution even if one agent fails
- Report partial results
- Mark failed aspects clearly in report
- Never abort entire review due to single agent failure

**Structured Results:**
- Return JSON-like structure for caller aggregation
- Enable Layer 1 batch commands to aggregate multiple files
- Consistent result format across all files

## USAGE EXAMPLES

**Review single file:**
```
/review-single-asciidoc file=standards/java-core.adoc
```

**Review and apply fixes:**
```
/review-single-asciidoc file=standards/java-core.adoc apply_fixes=true
```

## ARCHITECTURE

**Pattern**: Self-Contained Command (Layer 2)
- Called by: `/cui-review-technical-docs` (Layer 1 batch command)
- Calls: Layer 3 focused agents (format-validator, link-verifier, content-reviewer)
- Can be invoked: Directly by users OR by batch command

**Three-Layer Pattern:**
```
Layer 1: /cui-review-technical-docs (batch - all files)
  └─> For each file: SlashCommand(/review-single-asciidoc)

Layer 2: /review-single-asciidoc (self-contained - one file)
  ├─> Task(asciidoc-format-validator)
  ├─> Task(asciidoc-link-verifier)
  └─> Task(asciidoc-content-reviewer)

Layer 3: Focused agents
  └─> Execute specific validation only
```

## RELATED

- `/cui-review-technical-docs` - Batch command for all AsciiDoc files
- `asciidoc-format-validator` - Format validation agent
- `asciidoc-link-verifier` - Link verification agent
- `asciidoc-content-reviewer` - Content review agent
