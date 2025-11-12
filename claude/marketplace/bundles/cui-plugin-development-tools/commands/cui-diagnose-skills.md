---
name: cui-diagnose-skills
description: Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality
---

# Skill Doctor - Verify and Fix Skills

Orchestrates comprehensive analysis of skills by coordinating diagnose-skill agent for each skill.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-diagnose-skills update="[your improvement]"` with:
1. Improved skill analysis detection patterns and quality metrics
2. Better methods for identifying skill structural issues and YAML problems
3. More effective cross-skill duplication detection and consolidation recommendations
4. Enhanced marketplace architecture validation techniques
5. Any lessons learned about skill design patterns and self-containment principles

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace skills (standalone + bundle skills)
- **scope=global**: Analyze skills in global location (~/.claude/skills/)
- **scope=project**: Analyze skills in project location (.claude/skills/)
- **skill-name** (optional): Review a specific skill by name (e.g., `cui-java-core`)
- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **--check-cross-duplication** (optional): Detect content duplication BETWEEN skills. Expensive O(n²) operation. Default: false
- **No parameters**: Interactive mode with marketplace default

## WORKFLOW

### Step 1: Activate Diagnostic Patterns

**CRITICAL**: Load non-prompting tool patterns:

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

**Optionally load marketplace architecture standards**:

You may optionally load the marketplace architecture skill for additional architectural context:
```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components that may be useful for understanding skill design principles.

### Step 2: Discover Skills

**Parse parameters** to determine scope.

**For marketplace scope (default):**
```
Glob: pattern="*/SKILL.md", path="~/git/cui-llm-rules/claude/marketplace/skills"
Glob: pattern="*/skills/*/SKILL.md", path="~/git/cui-llm-rules/claude/marketplace/bundles"
```

**For global scope:**
```
Glob: pattern="*/SKILL.md", path="~/.claude/skills"
```

**For project scope:**
```
Glob: pattern="*/SKILL.md", path=".claude/skills"
```

**Extract skill paths** from SKILL.md file paths (remove `/SKILL.md` suffix).

**If specific skill name provided:**
- Filter list to matching skill only

**If no parameters (interactive mode):**
- Display numbered list of all skills found
- Let user select which to analyze or change scope

### Step 3: Analyze Skills (Parallel)

**For EACH skill discovered:**

Launch diagnose-skill agent:

```
Task:
  subagent_type: diagnose-skill
  description: Analyze {skill-name}
  prompt: |
    Analyze this skill comprehensively.

    Parameters:
    - skill_path: {absolute_path_to_skill}

    Return complete JSON report with all issues found.
```

**CRITICAL**: Launch ALL agents in PARALLEL (single message, multiple Task calls).

**Collect results** from each agent as they complete.

### Step 4: Aggregate Results

**Combine findings from all skills:**

```json
{
  "total_skills_analyzed": {count},
  "skills_with_issues": {count},
  "issue_summary": {
    "critical": {total_count},
    "warnings": {total_count},
    "suggestions": {total_count}
  },
  "by_skill": {
    "skill-name-1": {
      "status": "Clean|Warnings|Critical",
      "issues": {...},
      "scores": {...}
    },
    ...
  },
  "overall_metrics": {
    "avg_architecture_score": {score},
    "avg_integrated_content_score": {score},
    "skills_excellent": {count},
    "skills_good": {count},
    "skills_fair": {count},
    "skills_poor": {count}
  }
}
```

### Step 5: Detect Cross-Skill Duplication (Optional)

**When to Execute**: When `--check-cross-duplication` flag is provided

**Purpose**: Identify content duplication BETWEEN different skills to recommend consolidation or skill invocation.

**Prepare skill paths**:
- Collect all skill paths from Step 2 (from discovered SKILL.md files)
- Pass as array to cross-skill analyzer

**Launch analyze-cross-skill-duplication agent**:

```
Task:
  subagent_type: analyze-cross-skill-duplication
  description: Detect cross-skill duplication
  prompt: |
    Analyze content duplication between all marketplace skills.

    Parameters:
    - skill_paths: [{array of absolute skill paths}]

    Return complete JSON report with:
    - Duplicate skill pairs with similarity percentages
    - Specific duplicate sections with locations
    - Consolidation recommendations
    - Skill composition suggestions (Skill: invocations)
```

**Collect cross-skill analysis results**:
- Receive JSON report from agent
- Include in aggregated findings for summary report (Step 6)

**Notes**:
- This is an expensive O(n²) operation comparing all skill pairs
- Only run when needed: before releases, monthly reviews, after adding skills
- Agent compares skills with OTHER SKILLS only (not with /standards/ directory)
- Distinguishes intentional overlap (different domains) from harmful duplication

### Step 6: Generate Summary Report

**Display:**

```
==================================================
Skill Doctor - Analysis Complete
==================================================

Skills Analyzed: {total}
- Clean: {count} ✅
- With warnings: {count} ⚠️
- With critical issues: {count} ❌

Issue Statistics:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}
- Total: {count}

Quality Scores:
- Average Architecture: {score}/100
- Average Integrated Content: {score}/100

By Skill:
- {skill-1}: {status} | Arch: {score} | Content: {score}
- {skill-2}: {status} | Arch: {score} | Content: {score}
...

Recommendations:
{if critical issues}
⚠️ CRITICAL: {count} skills need immediate attention
- {skill-name}: {issue summary}
{endif}

{if all clean}
✅ All skills are well-formed and high quality!
{endif}

{if --check-cross-duplication flag set}
==================================================
Cross-Skill Duplication Analysis
==================================================

Duplicate Pairs Found: {count}
- High similarity (>80%): {count} ⚠️
- Moderate similarity (70-80%): {count} ℹ️

Top Duplication Issues:
1. {skill-a} ↔ {skill-b}: {similarity}% overlap
   - Duplicate section: {section-name}
   - Recommendation: {recommendation}

2. {skill-c} ↔ {skill-d}: {similarity}% overlap
   - Duplicate section: {section-name}
   - Recommendation: {recommendation}

Consolidation Opportunities:
- {opportunity-1}
- {opportunity-2}

{if no cross-skill duplication}
✅ No significant content duplication detected between skills!
{endif}
{endif}
```

**If --save-report flag is set:**
- Write the complete report above to `skills-diagnosis-report.md` in project root
- Inform user: "Report saved to: skills-diagnosis-report.md"

**Default behavior (no flag):**
- Display report only (as shown above)
- Do NOT create any files

### Step 7: Categorize Issues for Fixing

**Categorize all issues into Safe vs Risky:**

**Safe fixes** (auto-apply when auto-fix=true):
- YAML frontmatter syntax errors
- Formatting/whitespace normalization
- Missing YAML fields (add defaults: `description`, `audience`, `prerequisites`)
- Broken file references (remove or comment out)

**Risky fixes** (always prompt user):
- Duplication consolidation (requires judgment on what to keep)
- Missing standards files (create stub vs remove reference - user decides)
- Zero-information content removal (may have context we don't understand)
- Conflicting guidance resolution (requires domain expertise)

### Step 8: Apply Safe Fixes

**When to execute**: If auto-fix=true (default) AND safe fixes exist

**For each safe fix:**

**YAML syntax errors:**
```
Edit: {skill-file}
- Fix YAML frontmatter syntax
- Add missing required fields with defaults
- Correct field name typos (e.g., `tools` → `allowed-tools`)
```

**Formatting normalization:**
```
Edit: {skill-file}
- Normalize whitespace and indentation
- Ensure blank lines before lists (AsciiDoc requirement)
- Fix heading hierarchy
```

**Broken references:**
```
Edit: {skill-file}
- Remove or comment out references to non-existent files
- Add comment: "<!-- Reference removed: file not found -->"
```

**Track fixes applied:**
```json
{
  "safe_fixes_applied": {count},
  "by_type": {
    "yaml_fixes": {count},
    "formatting_fixes": {count},
    "reference_fixes": {count}
  }
}
```

### Step 9: Prompt for Risky Fixes

**When to execute**: If risky fixes exist (regardless of auto-fix setting)

**For each risky fix, prompt user:**

```
[PROMPT] Risky fix detected in {skill-name}:

Issue: {issue description}
Location: {file path and line number}
Proposed fix: {fix description}

Apply this fix? [Y]es / [N]o / [S]kip all remaining
```

**Handle responses:**
- **Yes**: Apply the fix using Edit tool
- **No**: Skip this fix, continue to next
- **Skip all remaining**: Exit fixing phase, proceed to verification

**Track risky fixes:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count}
}
```

### Step 10: Verify Fixes

**When to execute**: After any fixes applied (Step 8 or Step 9)

**Re-run analysis** on modified skills:
```
Task:
  subagent_type: diagnose-skill
  description: Verify fixes for {skill-name}
  prompt: |
    Re-analyze this skill after fixes.

    Parameters:
    - skill_path: {absolute_path_to_skill}

    Return complete JSON report.
```

**Compare before/after:**
```json
{
  "verification": {
    "skills_fixed": {count},
    "issues_resolved": {count},
    "issues_remaining": {count},
    "new_issues": {count}  // Should be 0!
  }
}
```

**Report verification results:**
```
Verification Complete:
✅ {issues_resolved} issues resolved
{if issues_remaining > 0}
⚠️ {issues_remaining} issues remain (require manual intervention)
{endif}
{if new_issues > 0}
❌ {new_issues} NEW issues introduced (fixes need review!)
{endif}
```

## ARCHITECTURE

This command is a simple orchestrator:
- Discovers skills using Glob (non-prompting)
- Launches diagnose-skill agents in parallel (for each skill)
- Optionally launches analyze-cross-skill-duplication (when --check-cross-duplication flag set)
- Aggregates and reports results

All analysis logic is in specialized agents:
- **analyze-standards-file**: Single file quality analysis
- **analyze-integrated-standards**: Cross-file quality within a skill
- **diagnose-skill**: Skill orchestrator (coordinates above two agents)
- **analyze-cross-skill-duplication**: Cross-skill duplication detection (optional, O(n²))

## TOOL USAGE

- **Glob**: Discover skills (non-prompting)
- **Task**: Launch diagnose-skill agents (parallel)
- **Skill**: Load diagnostic patterns

## RELATED

- `/cui-diagnose-agents` - Diagnose agents
- `/cui-diagnose-commands` - Diagnose commands
- `/cui-diagnose-bundle` - Diagnose entire bundle

## UNDERSTANDING DIAGNOSTIC RESULTS

### Marketplace Self-Containment Principle

**IMPORTANT**: Marketplace skills MUST be self-contained and CANNOT reference the `/standards/` directory.

**Why**:
- Skills may be distributed independently
- Skills may be installed globally outside the cui-llm-rules repo
- External dependencies break portability and marketplace distribution

**This means**:
- ✅ Skills having similar content to `/standards/` is EXPECTED and CORRECT
- ✅ Skills must contain all standards within their own `standards/` directory
- ❌ Skills should NOT reference `~/git/cui-llm-rules/standards/`
- ❌ Skills should NOT use relative paths like `../../../../standards/`

**What diagnostics check**:
- Duplication WITHIN the skill's own files (flagged as warning/suggestion)
- Prohibited references TO `/standards/` directory (flagged as CRITICAL violation)
- NOT similarity with `/standards/` content (this is expected)

### Issue Severity Levels

**CRITICAL**:
- Invalid YAML or missing required fields
- Broken file references (files don't exist)
- Prohibited references to `/standards/` directory or repo paths
- Critical conflicts between standards files

**WARNING**:
- Harmful duplication within skill's own files
- Zero-information content
- Contradictory guidance

**SUGGESTION**:
- Contextual duplication that may be acceptable
- Minor formatting improvements
- Missing cross-references between skill's own files

## STANDARDS

Skill analysis follows marketplace architecture principles and content quality standards.
Standards validation is performed automatically by specialized agents (analyze-standards-file, analyze-integrated-standards).
