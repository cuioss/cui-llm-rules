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

**Load marketplace architecture standards**:

```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components.

**Load bundle orchestration compliance patterns (MANDATORY)**:

```
Skill: cui-plugin-development-tools:bundle-orchestration-compliance
```

This enforces mandatory completion checklists, anti-skip protections, and post-fix verification requirements for bundle-by-bundle workflows.

### Step 2: Discover Skills

**Parse parameters** to determine scope.

**For marketplace scope (default):**

Execute plugin-inventory-scanner agent to get complete marketplace inventory:
```
Task:
  subagent_type: cui-plugin-development-tools:plugin-inventory-scanner
  description: Scan marketplace for all resources
  prompt: |
    Scan the marketplace directory structure and return complete inventory.

    scope: marketplace
    resourceTypes: null
    includeDescriptions: false
```

**CRITICAL:** Must get complete inventory (agents, commands, AND skills) because analyze-plugin-references agents need complete data to validate cross-references between all resource types.

Parse JSON output from agent:
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

Display: `Processing {total_bundles} bundles in order: {bundle_list}`

### Step 4: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps (4a-4i) for one bundle before moving to the next.

**⚠️ MANDATORY COMPLETION CHECK**: You MUST NOT skip Steps 4c-4i. Jumping directly to Step 5 (summary) without completing the fix workflow produces incomplete, invalid results.

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

**Collect results** for this bundle's skills. On errors: Display warning, mark status, continue processing.

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

**Launch reference validation agents in parallel** (single message, multiple Task calls) for **ALL skills in current bundle**.

**⚠️ CRITICAL**: You MUST validate references for ALL skills in the bundle, not a partial subset. Validating only some skills violates the workflow.

**Collect results** for this bundle's reference validation. On errors: Display warning, mark status, continue processing.

**Aggregate reference findings:** Track per-skill (found/correct/fixed/ambiguous) and bundle totals (checked/total/correct/fixed/issues).

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

Show: Bundle name, skills analyzed (clean/warnings/critical), issue counts, quality averages, reference stats.

Per-skill: status, scores (Arch/Content), refs (correct/found).

**Steps 4e-4h: Apply Fix Workflow for Bundle ⚠️ FIX PHASE STARTS**

**⚠️ ANTI-SKIP PROTECTION**: Steps 4e-4h are MANDATORY if any issues were found. Skipping these steps means:
- Reference fixes claimed by agents are not verified
- Safe fixes are not applied
- Risky fixes are not prompted
- No verification that fixes actually worked
- Invalid/incomplete diagnosis results

**EXPLICIT STOP POINT**: If you have NOT completed Steps 4a-4d above, STOP and complete them first. Do not proceed to fix workflow until analysis, reference validation, and aggregation are complete for the entire bundle.

**If any issues found in this bundle:**

Load and apply fix workflow from skill:
```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

Follow the skill's workflow: Categorize → Apply Safe Fixes → Prompt for Risky Fixes → Verify Fixes.

**If NO issues found:**
- Skip Steps 4e-4h (no fixes needed)
- Mark as N/A in completion checklist
- Proceed to Step 4h-verification

**Skill-specific configuration for categorization:**

**Safe fix types:**
- YAML frontmatter syntax errors, missing fields
- Formatting/whitespace normalization
- Broken file references

**Risky fix categories:**
- Duplication Issues, Integration Issues, Reference Problems

Track: `bundle_safe_fixes_applied`, `bundle_risky_fixes_applied`, `bundle_issues_resolved`

**Step 4h-verification: POST-FIX VERIFICATION (MANDATORY)**

**⚠️ CRITICAL**: After applying ANY fixes (Steps 4e-4h), you MUST verify actual file changes occurred.

**Execute:**
```
Bash: git status
```

**Verification checks:**
1. If reference fixes were "applied" by agents: `git status` MUST show modified .md files
2. If safe fixes were applied: `git status` MUST show modified files
3. If NO files show as modified but agents reported fixes: **FIXES FAILED** - agents did not actually edit files
4. Count actual modified files and compare to fix count

**Report verification:**
```
POST-FIX VERIFICATION:
- Fixes claimed: {total_fixes_from_agents}
- Files actually modified: {git_status_count}
- Verification: {PASS if counts match / FAIL if mismatch}
```

**If verification FAILS:**
- Report: "⚠️ WARNING: Agents claimed {X} fixes but only {Y} files were modified"
- Do NOT proceed to next bundle
- Investigate why fixes were not applied

**If NO fixes applied:**
- Mark as N/A: "✓ Step 4h-verification: Git status checked (N/A - no fixes applied)"

**Step 4i: MANDATORY Bundle Completion Check**

**⚠️ BEFORE proceeding to next bundle, verify ALL of the following are complete:**

- [ ] **Step 4a**: All skills analyzed (not partial subset)
- [ ] **Step 4b**: All skills reference-validated (not partial subset)
- [ ] **Step 4c**: Results aggregated for bundle
- [ ] **Step 4d**: Bundle summary displayed
- [ ] **Steps 4e-4h**: Fix workflow complete (if any issues found) OR marked N/A (if no issues)
- [ ] **Step 4h-verification**: Git status checked (if any fixes applied) OR marked N/A (if no fixes)

**If ANY checkbox above is unchecked: STOP. Complete that step before proceeding.**

**Only after ALL steps complete: Proceed to next bundle**

**Step 4j: Repeat for Next Bundle**

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

**Key Characteristics:**
- Bundle-by-bundle processing with cui-plugin-development-tools first, then alphabetically
- Complete workflow per bundle: Analysis → Reference validation → Fix → Verify
- Token-optimized: Streamlined output, scoped processing
- Parallel execution within bundle, sequential across bundles
- Optional cross-skill duplication detection (Step 6, O(n²), when --check-cross-duplication flag set)

**Analysis delegated to specialized agents:**
- diagnose-skill (skill orchestrator with streamlined output)
- analyze-plugin-references (reference validation)
- analyze-cross-skill-duplication (optional cross-skill duplication)

## TOOL USAGE

**SlashCommand** (/plugin-inventory), **Glob** (skill discovery), **Skill** (diagnostic/architecture patterns), **Task** (agent orchestration), **Edit** (fixes), **AskUserQuestion** (risky fix approval).

## RELATED

- `/plugin-diagnose-agents` - Diagnose agents
- `/plugin-diagnose-commands` - Diagnose commands
- `/plugin-diagnose-metadata` - Validate bundle metadata (plugin.json, marketplace.json)

## UNDERSTANDING DIAGNOSTIC RESULTS

**Marketplace Self-Containment**: Skills MUST be self-contained - content similarity to `/standards/` is expected, but references to `/standards/` directory are CRITICAL violations.

**Severity Levels**: CRITICAL (invalid YAML, broken references, prohibited `/standards/` references), WARNING (harmful duplication, zero-information content), SUGGESTION (minor improvements).

## STANDARDS

Skill analysis follows marketplace architecture principles and content quality standards.
Standards validation is performed automatically by specialized agents (analyze-standards-file, analyze-integrated-standards).
