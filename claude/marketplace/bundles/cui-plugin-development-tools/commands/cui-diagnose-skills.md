---
name: cui-diagnose-skills
description: Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality
---

# Skill Doctor - Verify and Fix Skills

Orchestrates comprehensive analysis of skills by coordinating cui-diagnose-single-skill agent for each skill.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace skills (standalone + bundle skills)
- **scope=global**: Analyze skills in global location (~/.claude/skills/)
- **scope=project**: Analyze skills in project location (.claude/skills/)
- **skill-name** (optional): Review a specific skill by name (e.g., `cui-java-core`)
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Interactive mode with marketplace default

## WORKFLOW

### Step 1: Activate Diagnostic Patterns

**CRITICAL**: Load non-prompting tool patterns:

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

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

### Step 5: Generate Summary Report

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
- Launches cui-diagnose-single-skill agents in parallel
- Aggregates and reports results

All analysis logic is in specialized agents:
- cui-analyze-standards-file (single file quality)
- cui-analyze-integrated-standards (cross-file quality)
- cui-diagnose-single-skill (skill orchestrator)

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
