---
name: cui-diagnose-skills
description: Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality
---

# Skill Doctor - Verify and Fix Skills

Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace skills (standalone + bundle skills)
- **scope=global**: Analyze skills in global location (~/.claude/skills/)
- **scope=project**: Analyze skills in project location (.claude/skills/)
- **skill-name** (optional): Review a specific skill by name (e.g., `cui-java-core`)
- **No parameters**: Interactive mode with marketplace default

## PARAMETER VALIDATION

**If `scope=marketplace` (default):**
- Process all skill directories in two locations:
  - Standalone: `~/git/cui-llm-rules/claude/marketplace/skills/`
  - Bundle skills: `~/git/cui-llm-rules/claude/marketplace/bundles/*/skills/`

**If `scope=global`:**
- Process all skill directories in `~/.claude/skills/`

**If `scope=project`:**
- Process all skill directories in `.claude/skills/`
- Skip if directory doesn't exist

**If specific skill name provided:**
- Search based on current scope parameter
- If no scope specified, search marketplace first, then global, then project

**If no parameters provided:**
- Display interactive menu with numbered list of all skills
- Let user select which skill(s) to review or change scope

## TOOL USAGE REQUIREMENTS

**CRITICAL**: This command must use non-prompting tools to avoid user interruptions during diagnosis.

### Activate Diagnostic Patterns Skill

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

This loads all tool usage patterns for non-prompting file operations.

### Required Tool Usage Patterns

✅ **File Discovery**: Use `Glob` tool (never `find` via Bash)
✅ **Existence Checks**: Use `Read` + try/except or `Glob` (never `test -f`/`test -d` via Bash)
✅ **Content Search**: Use `Grep` tool (never `grep`/`awk` via Bash)
✅ **File Reading**: Use `Read` tool (never `cat` via Bash)

**Why**: Bash commands trigger user prompts which interrupt the diagnostic flow.

## WORKFLOW INSTRUCTIONS

### Overview

The skill doctor performs comprehensive analysis in these phases:

1. **Discover** - Find all skills in specified scope
2. **Analyze** - Run validation checks on each skill
3. **Fix** - Apply automated fixes (if user approves)
4. **Report** - Generate comprehensive summary

### Load Analysis Standards

Before starting analysis, load the quality standards skill:

```
Skill: cui-plugin-development-tools:cui-skill-quality-standards
```

This skill provides:
- 16 common issue patterns (Pattern 1-16)
- Quality scoring criteria
- Structural requirements
- Content quality requirements
- Fix patterns and strategies
- "Minimize without information loss" principle

### Step 1: Determine Scope and Discover Skills

**A. Parse Parameters**

Determine what to process based on scope parameter:
1. If `scope=marketplace` (default) → Search both standalone and bundle skills
2. If `scope=global` → Search `~/.claude/skills/`
3. If `scope=project` → Search `.claude/skills/`
4. If skill name provided → Search in current scope only
5. If no parameters → Interactive mode with marketplace default

**B. Discover Skills**

Use Glob to discover skill directories:

```
# For marketplace scope (default)
standalone_skills = Glob(pattern="*", path="~/git/cui-llm-rules/claude/marketplace/skills")
bundle_skill_dirs = Glob(pattern="*/skills", path="~/git/cui-llm-rules/claude/marketplace/bundles")

# Combine and sort
marketplace_skills = standalone_skills + bundle_skills
marketplace_skills.sort()
```

**C. Interactive Mode (if no parameters)**

Display menu with all discovered skills:
```
Available Skills (scope=marketplace):

STANDALONE SKILLS:
1. cui-frontend-development
2. cui-java-cdi
3. cui-java-core
...

BUNDLE SKILLS:
7. cui-documentation (cui-documentation-standards bundle)
8. cui-javadoc (cui-project-quality-gates bundle)
...

Options: Enter number, "all", "scope=X", or "quit"
```

### Step 2: Initialize Analysis Statistics

Create tracking variables for reporting:
- `total_skills`, `skills_with_issues`, `skills_fixed`
- `total_issues`, `issues_fixed`
- `critical_issues`, `warnings`
- `yaml_errors`, `broken_references`, `structure_issues`
- `tool_warnings`, `documentation_noise_instances`, `removable_lines`
- `content_duplication_issues`, `content_conflicts`, `content_ambiguities`
- `avg_integrated_content_score`, `skills_excellent_score`, `skills_poor_score`

### Step 3: Analyze Each Skill

For EACH skill directory, execute comprehensive analysis:

#### Step 3.1: Display Skill Header

```
==================================================
Analyzing: <skill-name>
Location: <skill-path>
==================================================
```

#### Step 3.2-3.8: Run Validation Checks

Apply all validation checks from standards (in order):

**Structural Validation:**
- Verify SKILL.md exists (Pattern 5)
- Check directory structure
- Validate supporting files

**YAML Frontmatter Validation:**
- Parse and validate YAML syntax (Pattern 1)
- Verify required fields (`name`, `description`)
- Check optional fields (`allowed-tools` not `tools` - Pattern 2)
- Validate field values (lengths, formats, naming)

**Standards References Validation:**
- Extract all `Read: standards/` references (Pattern 3)
- Verify each file exists in skill directory
- Check for absolute paths (Pattern 4)
- Validate no external file references

**Directory Structure Validation:**
- Check primary files (SKILL.md, README.md)
- Check supporting directories (standards/, templates/, examples/)
- Verify referenced files exist

**Tool Restrictions Review:**
- Extract `allowed-tools` configuration (Pattern 6)
- Assess appropriateness for skill type
- Flag excessive permissions for knowledge skills

**Cross-References Analysis:**
- Find agent references to this skill (Pattern 7)
- Find skill-to-skill dependencies (Pattern 9)
- Detect circular dependencies
- Check for unused skills

**Content Quality Validation:**
- Check workflow structure (Pattern 8)
- Scan for common quality issues
- Validate code blocks and markdown

**Integrated Content Coherence:**
- Load all referenced standards files
- Analyze for duplication (Pattern 11)
- Detect conflicts (Pattern 12)
- Check for ambiguities (Pattern 13)
- Validate coherence and completeness (Pattern 14)
- Calculate integrated content score (Pattern 15)

**Architecture Compliance:**
- Check self-containment (no external refs)
- Detect documentation-only noise (Pattern 16)
- Verify internal references
- Categorize references (URLs, skills, internal files)
- Calculate architecture score

**Pattern 10**: Check for inconsistent naming

### Step 4: Generate Issue Report

For each skill, categorize all issues found:

**CRITICAL Issues (Must Fix):**
- Structural failures (missing SKILL.md, invalid YAML)
- Broken references (files not found, absolute paths)
- Content issues (harmful duplication, critical conflicts, too vague)

**Warnings (Should Fix):**
- Configuration issues (wrong tool field, excessive access)
- Quality issues (redundant duplication, contextual conflicts, ambiguities)
- Documentation noise (broken external links providing zero information)
- Integration issues (unused skills, content gaps)

**Suggestions (Nice to Have):**
- Missing optional features (templates/, examples/)
- Enhancement opportunities (better descriptions, more examples)

Display categorized report:
```
Issue Report for <skill-name>:

CRITICAL (X issues):
1. [Description]
   Impact: [Impact]
   Fix: [Fix strategy]

WARNINGS (X issues):
...

SUGGESTIONS (X items):
...

Total: X issues found
```

### Step 5: Fix Issues (If User Approves)

**Decision Point:**
```
Found <count> issues in <skill-name>:
- Critical: <count>
- Warnings: <count>
- Suggestions: <count>

Options:
F - Fix all issues automatically
R - Review each issue individually before fixing
S - Skip this skill (do not fix)
Q - Quit analysis entirely

Please choose [F/r/s/q]:
```

**Auto-Fix Behavior:**
- YAML issues → Add/fix frontmatter structure
- Path issues → Convert absolute to relative
- Structure issues → Rename files, create missing files
- Tool access → Restrict to appropriate tools
- Documentation noise → Remove sections with only broken/external links

**After Fixing:**
- Re-run analysis to verify fixes
- Compare before/after
- Update statistics
- Offer revert if new issues introduced

### Step 6: Generate Final Report

After processing all skills, display comprehensive summary:

```
==================================================
Skill Doctor - Analysis Complete
==================================================

Skills Analyzed: <total_skills>
- With issues: <skills_with_issues>
- Fixed: <skills_fixed>
- Still have issues: <remaining>

Issue Statistics:
- Total issues found: <total_issues>
- Critical: <critical_count>
- Warnings: <warning_count>
- Suggestions: <suggestion_count>
- Issues fixed: <issues_fixed>

Issue Breakdown by Category:
- YAML frontmatter errors: <yaml_errors>
- Broken standards references: <broken_references>
- Structure issues: <structure_issues>
- Tool restriction warnings: <tool_warnings>
- Documentation-only noise: <documentation_noise_instances> (<removable_lines> removable lines)
- Content duplication issues: <content_duplication_issues>
- Content conflicts: <content_conflicts>
- Content ambiguities: <content_ambiguities>

Integrated Content Quality:
- Average content score: <avg_integrated_content_score>/100
- Skills with excellent score (>= 90): <skills_excellent_score>
- Skills with good score (75-89): <skills_good_score>
- Skills with fair score (60-74): <skills_fair_score>
- Skills with poor score (< 60): <skills_poor_score> ⚠️

By Skill:
<for each skill analyzed>
- <skill-name>: <issue_count> issues (<critical>C / <warnings>W / <suggestions>S)
  Status: <Clean/Warnings/Critical>
  Content Score: <score>/100 (<Excellent/Good/Fair/Poor>)
</for each>

Recommendations:
<if critical issues remain>
⚠️  CRITICAL: <count> skills still have critical issues
- <skill-1>: <issue>
Re-run diagnose-skills on these skills to fix.
</if>

<if content quality issues>
⚠️  CONTENT QUALITY: <count> skills have content quality concerns
- Skills with conflicts: <list>
- Skills with harmful duplication: <list>
- Skills with poor score (< 60): <list>
</if>

<if all clean and high quality>
✅ All analyzed skills are well-formed, properly integrated, and have excellent content quality!
</if>
```

## CRITICAL RULES

- **READ ENTIRE SKILL** before analyzing - context is essential
- **USE NON-PROMPTING TOOLS** - Follow diagnostic patterns skill guidance
- **LOAD STANDARDS FIRST** - Read quality standards and patterns before analysis
- **CATEGORIZE ISSUES PROPERLY** - Critical vs Warning vs Suggestion based on loaded patterns
- **EXPLAIN FIXES CLEARLY** - User should understand why each change is made
- **VERIFY AFTER FIXING** - Always re-analyze to ensure fixes worked
- **PRESERVE INTENT** - Fix structure/consistency but preserve skill's purpose
- **USE EDIT TOOL** - Never rewrite entire files, use targeted edits
- **TRACK STATISTICS** - Maintain counters throughout analysis for final report
- **HANDLE ERRORS** - If skill file is malformed/unreadable, report and skip
- **INTERACTIVE BY DEFAULT** - Ask before making changes unless told otherwise
- **APPLY "MINIMIZE WITHOUT INFORMATION LOSS"** - Remove documentation-only noise safely

## STANDARDS REFERENCED

This command relies on the skill quality standards skill:

**Skill: cui-plugin-development-tools:cui-skill-quality-standards**

This skill provides:
- Quality requirements, scoring criteria, structural standards
- 16 common issue patterns and detection logic
- Fix strategies and best practices

Load this skill at the beginning of execution to guide analysis and fixes.

## RELATED DOCUMENTATION

See README.md for:
- Usage examples
- Error handling scenarios
- Integration with other commands
- When to run this command
