---
name: cui-review-technical-docs
description: Execute comprehensive AsciiDoc review with format validation, link verification, and quality analysis
---

# Review Technical Docs Command

Comprehensive AsciiDoc documentation review orchestrating validation, link verification, and content quality agents across documentation directories.

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

**Link Verification:**
```
Task:
  subagent_type: asciidoc-link-verifier
  description: Verify links in {dir}
  prompt: Verify all xref links in {dir}
```

**Content Review:**
```
Task:
  subagent_type: asciidoc-content-reviewer
  description: Review content in {dir}
  prompt: Review content quality in {dir}
```

### Step 3: Collect and Aggregate Results

Wait for all agents, aggregate:
- Format issues by severity
- Broken links count
- Content quality issues
- Files analyzed count

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
- Format errors: {count}
- Broken links: {count}
- Content quality: {count}
- Total issues: {count}

Recommendations:
{aggregated recommendations}
```

### Step 6: Handle Fixes (if issues found)

Prompt user to apply recommended fixes or skip.

### Step 7: Commit Changes (if push flag)

Use commit-changes agent to commit documentation improvements.

## CRITICAL RULES

**Parallel Execution:**
- Launch all directory reviews in parallel
- Don't wait between agent launches
- Collect results after all complete

**Agent Coordination:**
- Each directory reviewed by 3 agents
- Agents run independently
- Results aggregated at end

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
