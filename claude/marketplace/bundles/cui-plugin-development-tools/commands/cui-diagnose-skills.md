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
- **--check-cross-duplication** (optional): Detect content duplication BETWEEN skills. Expensive O(n²) operation. Default: false
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

### Step 5: Detect Cross-Skill Duplication (Optional)

**When to Execute**: When `--check-cross-duplication` flag is provided

**Purpose**: Identify content duplication BETWEEN different skills to recommend consolidation or skill invocation.

**Approach**:

1. **Extract Content Fingerprints**:
   - For each skill analyzed, extract key content blocks from all standards files
   - Generate content hashes for sections (by heading)
   - Track: skill name, file name, section heading, content hash, line numbers

2. **Compare Across Skills**:
   ```
   For each pair of skills (A, B):
     - Compare content hashes
     - Identify sections with high similarity (>80%)
     - Record: both skills, duplicate content summary, similarity %
   ```

3. **Analyze Duplication Patterns**:

   **Pattern 1: Identical Content Blocks**
   - Same section heading + nearly identical content
   - Example: "Constructor Injection" in both cui-java-core and cui-java-cdi
   - **Severity**: WARNING if intentional domain overlap, SUGGESTION to review

   **Pattern 2: Substantial Overlap**
   - 50%+ of one skill's content duplicated in another
   - **Severity**: WARNING - Consider consolidation or skill invocation
   - **Recommendation**: Have smaller skill invoke larger skill, or extract to shared skill

   **Pattern 3: Complementary Duplication**
   - Similar topics but different focus/context
   - Example: JavaScript testing in cui-frontend-development vs generic testing in cui-java-unit-testing
   - **Assessment**: ACCEPTABLE - Different domains, keep separate

4. **Generate Recommendations**:

   **For Identical Content**:
   - Option A: Extract to new shared skill, both skills invoke it
   - Option B: Have Skill B invoke Skill A (if Skill A is authoritative)
   - Option C: Accept duplication if different contexts warrant it

   **For Substantial Overlap**:
   - Consider merging skills if they serve similar purposes
   - Or have one skill depend on another via Skill: invocation

5. **Report Cross-Skill Duplication**:

   ```json
   "cross_skill_duplication": {
     "total_duplicate_pairs": {count},
     "by_severity": {
       "warnings": {count},
       "suggestions": {count}
     },
     "findings": [
       {
         "severity": "WARNING",
         "skills": ["cui-java-core", "cui-java-cdi"],
         "similarity_percent": 35,
         "duplicate_sections": [
           {
             "section": "Constructor Injection Pattern",
             "skill_a_location": "cui-java-core/standards/java-core-patterns.md:45-60",
             "skill_b_location": "cui-java-cdi/standards/cdi-aspects.md:120-135",
             "similarity": 95,
             "content_summary": "Identical explanation of constructor injection benefits"
           }
         ],
         "recommendation": "Extract constructor injection pattern to shared skill 'cui-java-dependency-injection' or have cui-java-cdi invoke cui-java-core for this pattern",
         "rationale": "Reduces maintenance burden and ensures consistency"
       }
     ],
     "consolidation_opportunities": [
       {
         "skills": ["cui-requirements", "cui-project-setup"],
         "overlap_percent": 45,
         "recommendation": "Consider having cui-project-setup invoke cui-requirements for requirements standards rather than duplicating"
       }
     ]
   }
   ```

6. **Include in Summary Report**:
   - Add cross-skill duplication section after individual skill results
   - Show top duplication pairs
   - Provide consolidation recommendations

**Implementation Notes**:

- This check is OPTIONAL (--check-cross-duplication flag)
- Expensive operation: O(n²) skill comparisons
- Should use content hashing for performance
- Only flag duplications above similarity threshold (>70%)
- Distinguish intentional overlap (complementary domains) from harmful duplication

**Example Usage**:
```
/cui-diagnose-skills --check-cross-duplication
/cui-diagnose-skills --check-cross-duplication --save-report
```

**Benefits**:
- Identifies opportunities for skill consolidation
- Reduces marketplace bloat
- Improves maintenance (one source of truth)
- Suggests proper skill composition via Skill: invocations

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
