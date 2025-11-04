---
name: cui-review-technical-docs
description: Execute comprehensive AsciiDoc review with format validation, link verification, and quality analysis
---

# Review Technical Docs Command

Comprehensive AsciiDoc documentation review orchestrating validation, link verification, and content quality agents across documentation directories.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using /cui-update-command command-name=cui-review-technical-docs update="[your improvement]"

**Areas for continuous improvement:**
1. Improved directory discovery patterns for AsciiDoc files
2. Better agent coordination strategies for parallel execution
3. More effective result aggregation and reporting methods
4. Enhanced error handling for agent failures
5. Any lessons learned about documentation review workflows

## PARAMETERS

**push** - Auto-push after fixes (optional flag)

## WORKFLOW

### Step 1: Discover Documentation Directories

Use Glob to find all directories containing .adoc files. Group intelligently (e.g., standards/, doc/, docs/).

### Step 2: Launch Review Agents (Parallel)

For each directory group, launch in parallel:

**Format Validation:**
```
Task:
  subagent_type: asciidoc-format-validator
  description: Validate format in {dir}
  prompt: Validate AsciiDoc format in {dir}
```

**Error handling:** If asciidoc-format-validator fails, increment agent_failures counter and prompt user "[R]etry/[S]kip validation/[A]bort all".

**Link Verification:**
```
Task:
  subagent_type: asciidoc-link-verifier
  description: Verify links in {dir}
  prompt: Verify all xref links in {dir}
```

**Error handling:** If asciidoc-link-verifier fails, increment agent_failures counter and prompt user "[R]etry/[S]kip verification/[A]bort all".

**Content Review:**
```
Task:
  subagent_type: asciidoc-content-reviewer
  description: Review content in {dir}
  prompt: Review content quality in {dir}
```

**Error handling:** If asciidoc-content-reviewer fails, increment agent_failures counter and prompt user "[R]etry/[S]kip review/[A]bort all".

### Step 3: Collect and Aggregate Results

Wait for all agents, aggregate:
- Format issues by severity (track in validation_errors counter)
- Broken links count (track in link_errors counter)
- Content quality issues (track in content_issues counter)
- Files analyzed count (track in files_analyzed counter)

**Handle partial results:**
- If agent returned PARTIAL: Display partial results and prompt "[C]ontinue with partial data/[R]etry agent/[A]bort"
- If agent returned FAILURE: Prompt "[R]etry agent/[C]ontinue without this data/[A]bort"
- Track all decisions for final report

### Step 4: Consolidate Lessons Learned

Extract lessons learned from all agent reports, update run-configuration.md if needed.

### Step 5: Report Consolidated Issues

Display comprehensive report:
```
╔════════════════════════════════════════════════════════════╗
║          Documentation Review Report                       ║
╚════════════════════════════════════════════════════════════╝

Directories analyzed: {count}
Files analyzed: {count}
Agents executed: {count}

Issues by Category:
- Format errors: {validation_errors}
- Broken links: {link_errors}
- Content quality: {content_issues}
- Total issues: {total_issues}

Statistics:
- Agent failures: {agent_failures}
- Directories processed: {count}
- Files analyzed: {files_analyzed}

Recommendations:
{aggregated recommendations}
```

### Step 6: Handle Fixes (if issues found)

Prompt user to apply recommended fixes or skip.

### Step 7: Commit Changes (if push flag)

Use commit-changes agent to commit documentation improvements.

## STATISTICS TRACKING

Track throughout workflow:
- `files_analyzed`: Count of .adoc files analyzed
- `validation_errors`: Format validation issues found
- `link_errors`: Broken links found
- `content_issues`: Content quality issues found
- `agent_failures`: Count of agent execution failures
- `total_issues`: Sum of all issues (validation_errors + link_errors + content_issues)

Display all statistics in final report.

## CRITICAL RULES

**Parallel Execution:**
- Launch all directory reviews in parallel
- Don't wait between agent launches
- Collect results after all complete

**Agent Coordination:**
- Each directory reviewed by 3 agents
- Agents run independently
- Results aggregated at end

**Error Handling:**
- Prompt user on agent failures
- Allow retry/skip/abort decisions
- Track all failures in agent_failures counter

**State Management:**
- Track in run-configuration.md
- Update lessons learned
- Persist review state

## USAGE EXAMPLES

**Review all docs:**
```
/cui-review-technical-docs
```

**Review and push:**
```
/cui-review-technical-docs push
```

## ARCHITECTURE

Orchestrates:
- asciidoc-format-validator agent
- asciidoc-link-verifier agent
- asciidoc-content-reviewer agent
- commit-changes agent

## RELATED

- asciidoc-format-validator agent
- asciidoc-link-verifier agent
- asciidoc-content-reviewer agent
