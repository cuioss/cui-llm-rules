---
name: plugin-diagnose-skills
description: Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality
---

# Skill Doctor - Verify and Fix Skills

Orchestrates comprehensive analysis of skills by coordinating diagnose-skill agent for each skill.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-skills update="[your improvement]"` with:
1. Improved skill analysis detection patterns and quality metrics
2. Better methods for identifying skill structural issues and YAML problems
3. More effective cross-skill duplication detection and consolidation recommendations
4. Enhanced marketplace architecture validation techniques
5. Improved plugin reference validation and correction strategies
6. Any lessons learned about skill design patterns and self-containment principles

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

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-7)**
- Discover components
- Analyze each component
- Generate report

**PHASE 2: Fix Workflow (Steps 8-11)**
- Categorize issues (safe vs risky)
- Apply safe fixes automatically
- Prompt user for risky fixes
- Verify all fixes worked

**CRITICAL: Do not stop after Step 7. Continue to Step 8.**

### Step 1: Activate Diagnostic Patterns

**CRITICAL**: Load non-prompting tool patterns:

```
Skill: cui-utilities:cui-diagnostic-patterns
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

Execute plugin-inventory command to get complete marketplace inventory:
```
SlashCommand: /plugin-inventory --json
```

**CRITICAL:** Must get complete inventory (agents, commands, AND skills) because analyze-plugin-references agents need complete data to validate cross-references between all resource types.

Parse JSON output:
- Extract `bundles[]` array from JSON response
- For each bundle, collect `bundle.skills[]` with `name` and `path` fields
- Build flat list of skill paths from all bundles

**For global scope:**
```
Glob: pattern="*/SKILL.md", path="~/.claude/skills"
```

**Extract skill paths** from SKILL.md file paths (remove `/SKILL.md` suffix).

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

### Step 3: Group Skills by Bundle

**CRITICAL**: Organize skills by bundle for sequential processing.

**Parse inventory from Step 2:**
- Extract `bundles[]` array from inventory JSON
- For each bundle, identify bundle name and collect all skills with their paths
- Create bundle-to-skills mapping

**Sort bundles:**
1. **First**: `cui-plugin-development-tools` (always first)
2. **Then**: All other bundles alphabetically by name

**Example bundle order:**
```
1. cui-plugin-development-tools
2. cui-documentation-standards
3. cui-frontend-expert
4. cui-java-expert
5. cui-maven
6. cui-task-workflow
7. cui-utilities
```

**Display processing plan:**
```
Processing {total_bundles} bundles in order:
1. cui-plugin-development-tools ({skill_count} skills)
2. {bundle-name} ({skill_count} skills)
...
```

### Step 4: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps for one bundle before moving to the next.

**For EACH bundle in sorted order:**

Display: `Processing bundle: {bundle_name} ({skill_count} skills)`

**Step 4a: Analyze Bundle Skills**

For all skills in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:diagnose-skill
  description: Analyze {skill-name}
  prompt: |
    Analyze this skill comprehensively.

    Parameters:
    - skill_path: {absolute_path_to_skill}

    IMPORTANT: Use streamlined output format (issues only).
    Return minimal JSON - CLEAN skills get {"status": "CLEAN"},
    skills with issues get only critical_issues/warnings/suggestions arrays.

    This reduces token usage from ~300-400 to ~100-200 tokens per skill.
```

**Launch skill analysis agents in parallel** (single message, multiple Task calls) for all skills in current bundle.

**Collect results** for this bundle's skills.

**Error Handling:**
- If Task fails: Display warning with skill name and error, mark as "Analysis Failed", continue
- If malformed response: Display warning, mark as "Malformed Response", continue
- If timeout: Display warning, mark as "Timeout", continue

**Step 4b: Check Plugin References for Bundle**

For all skills in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:analyze-plugin-references
  description: Check references in {skill-name}
  prompt: |
    Check all plugin references in this skill.

    Parameters:
    - path: {absolute_path_to_skill_SKILL.md}
    - marketplace_inventory: {complete_json_inventory_from_step_2}
    - auto-fix: true  # Auto-fix deterministic reference issues (missing/incorrect bundle prefixes)

    IMPORTANT: marketplace_inventory must contain COMPLETE inventory (agents, commands, AND skills) from Step 2's /plugin-inventory --json call.
    This complete data is required to validate Skill invocations and cross-references between all resource types.

    Return summary report with reference validation results.
```

**Launch reference validation agents in parallel** (single message, multiple Task calls) for all skills in current bundle.

**Collect results** for this bundle's reference validation.

**Error Handling:**
- If Task fails: Display warning with skill name and error, mark as "Reference Check Failed", continue
- If unexpected format: Display warning, mark as "Reference Check Error", continue

**Aggregate reference findings for this bundle:**
Track for each skill: references_found, references_correct, references_fixed, references_ambiguous.
Bundle totals: skills_checked, total_references, correct, fixed, issues.

**Step 4b.1: Verify Reference Violations (MANDATORY)**

**CRITICAL**: Before accepting reference violations, re-verify flagged issues to eliminate false positives.

**For each skill flagged with reference violations in Step 4b:**

1. **Read exact flagged lines with context**:
   ```
   Read: {skill_SKILL.md_file_path}
   ```
   Focus on lines flagged by analyze-plugin-references, include ±2 lines context.

2. **Distinguish runtime invocations from documentation**:

   **✅ ACTUAL VIOLATIONS (runtime invocations)**:
   - Direct tool usage: `SlashCommand: /plugin-update-command`
   - Agent configuration: `subagent_type: cui-utilities:research`
   - Task launches: `Task:` followed by subagent_type
   - In workflow steps describing actual execution

   **❌ FALSE POSITIVES (documentation text - DO NOT REPORT)**:
   - Pattern examples: "Pattern: subagent_type:" or "e.g., 'Task:'"
   - CONTINUOUS IMPROVEMENT RULE instructions: "The caller can then invoke `/plugin-update-agent`"
   - Documentation explaining how callers use commands: "Caller invokes /command-name"
   - Tool search patterns: "Search for tool mentions (e.g., 'Task:')"
   - Architecture descriptions: "When you need to use Task tool"

3. **Only report verified violations**:
   - Discard flagged lines that are documentation/examples
   - Keep only actual runtime invocations
   - Track: `violations_flagged`, `violations_verified`, `false_positives_filtered`

**Error Handling:**
- If Read fails: Log warning, mark as "Verification Failed", exclude from violation count
- If context unclear: Include in manual review list rather than auto-reporting as violation

**Step 4c: Aggregate Results for Bundle**

**Combine findings for this bundle's skills:**

Track bundle metrics:
- `bundle_name`: Current bundle name
- `total_skills_analyzed`: Count for this bundle
- `skills_with_issues`: Count for this bundle
- Issue counts: `critical`, `warnings`, `suggestions`
- Reference stats: `total_references`, `correct`, `fixed`, `issues`
- Quality scores: averages for architecture, integrated content
- Per-skill data: status, issues, scores, reference counts

**Step 4d: Generate Bundle Summary Report**

**Display bundle summary:**

```
==================================================
Bundle: {bundle_name}
==================================================

Skills Analyzed: {total}
- Clean: {count} ✅
- With warnings: {count} ⚠️
- With critical issues: {count} ❌

Issue Statistics:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}

Quality Scores:
- Average Architecture: {score}/100
- Average Integrated Content: {score}/100

Reference Validation:
- Total references: {total_references}
- Correct: {correct}
- Fixed: {fixed}
- Issues: {issues}

Per-Skill Summary:
- {skill-1}: {status} | Arch: {score} | Content: {score} | Refs: {correct}/{found}
- {skill-2}: {status} | Arch: {score} | Content: {score} | Refs: {correct}/{found}
...
```

**Step 4e: Categorize Issues for Bundle ⚠️ FIX PHASE STARTS**

**If any issues found in this bundle:**

**Load fix workflow skill (once, if not already loaded):**
```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

**Categorize issues for this bundle into Safe vs Risky:**

**Skill-specific safe fix types:**
- YAML frontmatter syntax errors
- Formatting/whitespace normalization
- Missing YAML fields (add defaults: `description`, `allowed-tools`)
- Broken file references (remove or comment out)

**Skill-specific risky fix categories:**
1. **Duplication Issues** - Content found in multiple places, consolidation needed
2. **Integration Issues** - Orphaned files, workflow disconnection
3. **Reference Problems** - Broken example references, unclear cross-references

**Step 4f: Apply Safe Fixes for Bundle**

**When to execute**: If auto-fix=true (default) AND safe fixes exist in this bundle

Apply safe fixes for skills in this bundle using Edit tool.

Track: `bundle_safe_fixes_applied`, `by_type` (yaml, formatting, broken_references)

**Step 4g: Prompt for Risky Fixes for Bundle**

**When to execute**: If risky fixes exist in this bundle

Use AskUserQuestion for risky fixes in this bundle.

Group by categories: Duplication Issues, Integration Issues, Reference Problems

Track: `bundle_risky_fixes_prompted`, `bundle_risky_fixes_applied`, `bundle_risky_fixes_skipped`

**Step 4h: Verify Fixes for Bundle**

**When to execute**: After any fixes applied in this bundle

Re-run analysis on modified skills in this bundle.

Track verification: `bundle_issues_resolved`, `bundle_issues_remaining`, `bundle_new_issues`

**Display bundle verification results:**
```
==================================================
Bundle {bundle_name} - Fixes Verified
==================================================

✅ {issues_resolved} issues resolved
{if issues_remaining > 0}
⚠️ {issues_remaining} issues remain
{endif}
```

**Step 4i: Repeat for Next Bundle**

**CRITICAL**: Return to Step 4 for the next bundle in sorted order.

Only proceed to Step 5 when ALL bundles have been processed (analysis + fixes).

### Step 5: Generate Overall Summary Report

**Execute ONLY after all bundles have been processed.**

**Aggregate cross-bundle metrics:**
- Total skills analyzed across all bundles
- Total issues found/resolved across all bundles
- Bundle-by-bundle breakdown
- Overall quality metrics

**Display final summary:**
```
==================================================
Skill Doctor - All Bundles Complete
==================================================

Bundles Processed: {total_bundles}
Total Skills: {total_skills}

Overall Statistics:
- Skills clean: {count} ✅
- Skills with warnings: {count} ⚠️
- Skills with critical issues: {count} ❌

Total Issues:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}

Fixes Applied:
- Safe fixes: {count}
- Risky fixes: {count}
- Issues resolved: {count}

By Bundle:
- cui-plugin-development-tools: {skills} skills | {issues} issues | {fixes} fixed
- {bundle-2}: {skills} skills | {issues} issues | {fixes} fixed
...

{if all clean}
✅ All skills across all bundles are well-formed and high quality!
{endif}
```

**If --save-report flag is set:**
- Write complete cross-bundle report to `skills-diagnosis-report.md`
- Inform user: "Report saved to: skills-diagnosis-report.md"

### Step 6: Detect Cross-Skill Duplication (Optional)

**When to Execute**: When `--check-cross-duplication` flag is provided

**Execute AFTER Step 5 (all bundles processed)**

**Purpose**: Identify content duplication BETWEEN different skills across ALL bundles.

**Launch analyze-cross-skill-duplication agent**:

```
Task:
  subagent_type: cui-plugin-development-tools:analyze-cross-skill-duplication
  description: Detect cross-skill duplication
  prompt: |
    Analyze content duplication between all marketplace skills.

    Parameters:
    - skill_paths: [{array of absolute skill paths from ALL bundles}]

    Return complete JSON report with duplication findings.
```

**Display cross-skill duplication report**:
```
==================================================
Cross-Skill Duplication Analysis (All Bundles)
==================================================

Duplicate Pairs Found: {count}
- High similarity (>80%): {count} ⚠️
- Moderate similarity (70-80%): {count} ℹ️

Top Duplication Issues:
1. {skill-a} ↔ {skill-b}: {similarity}% overlap
   - Recommendation: {recommendation}

{if no cross-skill duplication}
✅ No significant content duplication detected!
{endif}
```

**Notes**:
- This is an expensive O(n²) operation comparing all skill pairs across all bundles
- Only run when needed: before releases, monthly reviews, after adding skills


## ARCHITECTURE

This command is a bundle-by-bundle orchestrator designed to prevent token overload by processing marketplace resources sequentially by bundle.

**Key Architecture Characteristics:**
- **Bundle-by-bundle processing**: Process one bundle completely before moving to next
- **Bundle ordering**: cui-plugin-development-tools first, then alphabetically
- **Complete workflow per bundle**: Analysis → Reference validation → Categorize → Fix → Verify
- **Token-optimized**: Streamlined output, scoped processing
- **Parallel execution within bundle**: All skills for a bundle run in parallel
- **Sequential across bundles**: Next bundle only starts after previous is complete
- **Optional cross-skill duplication**: Runs AFTER all bundles (Step 6) when flag provided

**Processing Flow:**
1. Discover all bundles and sort (cui-plugin-development-tools first, then alphabetical)
2. For each bundle:
   - Analyze all skills in bundle (parallel)
   - Validate all references in bundle (parallel)
   - Aggregate bundle results
   - Generate bundle report
   - Categorize issues for bundle
   - Apply safe fixes for bundle
   - Prompt for risky fixes for bundle
   - Verify fixes for bundle
3. Generate overall cross-bundle summary
4. Optional: Detect cross-skill duplication across ALL skills (when --check-cross-duplication flag set)

**All analysis logic is in specialized agents:**
- **analyze-standards-file**: Single file quality analysis
- **analyze-integrated-standards**: Cross-file quality within a skill
- **diagnose-skill**: Skill orchestrator (coordinates above two agents, supports streamlined output)
- **analyze-plugin-references**: Plugin reference validation
- **analyze-cross-skill-duplication**: Cross-skill duplication detection (optional, O(n²), runs after all bundles)

## TOOL USAGE

- **SlashCommand**: Execute /plugin-inventory --json (marketplace discovery with complete inventory)
- **Glob**: Discover skills in global/project scopes (non-prompting)
- **Skill**: Load diagnostic patterns, marketplace architecture, and fix workflow patterns
- **Task**: Launch diagnose-skill and analyze-plugin-references agents (parallel within bundle)
- **Edit**: Apply safe and approved risky fixes
- **AskUserQuestion**: Prompt for risky fix approval per bundle

## RELATED

- `/plugin-diagnose-agents` - Diagnose agents
- `/plugin-diagnose-commands` - Diagnose commands
- `/plugin-diagnose-bundle` - Diagnose entire bundle

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
