---
name: cui-diagnose-skills
description: Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality
---

# Skill Doctor - Verify and Fix Skills

Orchestrates comprehensive analysis of skills by coordinating cui-diagnose-single-skill agent for each skill.

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

Launch cui-diagnose-single-skill agent:

```
Task:
  subagent_type: cui-diagnose-single-skill
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

**Launch cui-analyze-cross-skill-duplication agent**:

```
Task:
  subagent_type: cui-analyze-cross-skill-duplication
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

## FIXING ISSUES

This command currently REPORTS issues only. To fix:

1. Review recommendations in report
2. Manually edit affected files
3. Re-run cui-diagnose-skills to verify fixes

**Future enhancement**: Auto-fix capability with user approval.

## ARCHITECTURE

This command is a simple orchestrator:
- Discovers skills using Glob (non-prompting)
- Launches cui-diagnose-single-skill agents in parallel (for each skill)
- Optionally launches cui-analyze-cross-skill-duplication (when --check-cross-duplication flag set)
- Aggregates and reports results

All analysis logic is in specialized agents:
- **cui-analyze-standards-file**: Single file quality analysis
- **cui-analyze-integrated-standards**: Cross-file quality within a skill
- **cui-diagnose-single-skill**: Skill orchestrator (coordinates above two agents)
- **cui-analyze-cross-skill-duplication**: Cross-skill duplication detection (optional, O(n²))

## TOOL USAGE

- **Glob**: Discover skills (non-prompting)
- **Task**: Launch cui-diagnose-single-skill agents (parallel)
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
Standards validation is performed automatically by specialized agents (cui-analyze-standards-file, cui-analyze-integrated-standards).
