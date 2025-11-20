---
name: plugin-diagnose-commands
description: Analyze, verify, and fix slash commands for clarity, structure, and bloat
---

# Commands Doctor - Verify and Fix Commands

Orchestrates comprehensive analysis of slash commands by coordinating diagnose-command for each command.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-commands update="[your improvement]"` with:
1. Improved command bloat detection and size classification metrics
2. Better methods for identifying structural issues and anti-bloat violations
3. More effective quality scoring and command organization assessment techniques
4. Enhanced detection of commands requiring extraction to skills
5. Any lessons learned about command design patterns and complexity reduction strategies

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace commands
- **scope=global**: Analyze commands in ~/.claude/commands/
- **scope=project**: Analyze commands in .claude/commands/
- **command-name** (optional): Review specific command
- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Interactive mode

## WORKFLOW

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-6)**
- Discover components
- Analyze each component
- Generate report

**PHASE 2: Fix Workflow (Steps 7-11)**
- Handle reference issues
- Categorize issues (safe vs risky)
- Apply safe fixes automatically
- Prompt user for risky fixes
- Verify all fixes worked

**CRITICAL: Do not stop after Step 6. Continue to Step 7.**

### Step 1: Activate Diagnostic Patterns

**CRITICAL**: Load non-prompting tool patterns:

```
Skill: cui-utilities:cui-diagnostic-patterns
```

**CRITICAL: Load marketplace architecture standards**:

```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This skill provides command quality standards and analysis patterns used throughout the diagnosis workflow. All agents will reference these standards from the loaded skill context.

### Step 2: Validate Parameters

**Validate scope** (marketplace/global/project, default: marketplace), **command-name** filter, **paths** (verify directories exist), **flags** (auto-fix default true, --save-report default false).

### Step 3: Discover Commands

**Using validated scope from Step 2:**

**For marketplace scope (default):**

Execute scan-marketplace-inventory.sh script to get complete marketplace inventory:
```
Bash: ./.claude/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh --scope marketplace
```

**CRITICAL:** Must get complete inventory (agents, commands, AND skills) because analyze-plugin-references agents need skill data to validate Skill invocations.

Parse JSON output from script:
- Extract `bundles[]` array from JSON response
- For each bundle, collect `bundle.commands[]` with `name` and `path` fields
- Build flat list of command paths from all bundles

**For global scope:**
```
Glob: pattern="*.md", path="~/.claude/commands"
```

**For project scope:**
```
Glob: pattern="*.md", path=".claude/commands"
```

**Extract command names** from file paths.

**If specific command name provided:**
- Filter list to matching command only

**If no parameters (interactive mode):**
- Display numbered list of all commands found
- Separate standalone and bundle commands
- Let user select which to analyze or change scope

### Step 4: Group Commands by Bundle

**CRITICAL**: Organize commands by bundle for sequential processing.

**Parse inventory from Step 3:**
- Extract `bundles[]` array from inventory JSON
- For each bundle, identify bundle name and collect all commands with their paths
- Create bundle-to-commands mapping

**Sort bundles:**
1. **First**: `cui-plugin-development-tools` (always first)
2. **Then**: All other bundles alphabetically by name

Display: `Processing {total_bundles} bundles in order: {bundle_list}`

### Step 5: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps (5a-5j) for one bundle before moving to the next.

**⚠️ MANDATORY COMPLETION CHECK**: You MUST NOT skip Steps 5c-5j. Jumping directly to Step 6 (summary) without completing the fix workflow produces incomplete, invalid results.

**For EACH bundle in sorted order:**

Display: `Processing bundle: {bundle_name} ({command_count} commands)`

**Step 5a: Analyze Bundle Commands**

For all commands in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:diagnose-command
  description: Analyze {command-name}
  prompt: |
    Analyze this command comprehensively.

    Parameters:
    - command_path: {absolute_path_to_command}

    IMPORTANT: Standards have been pre-loaded by orchestrator.
    Skip Step 1 (Load Analysis Standards) - use standards from context instead.

    IMPORTANT: Use streamlined output format (issues only).
    Return minimal JSON - CLEAN commands get {"status": "CLEAN"},
    commands with issues get only critical_issues/warnings/suggestions arrays.

    This reduces token usage from ~2,000 to ~200-800 tokens per command.
```

**Launch command analysis agents in parallel** (single message, multiple Task calls) for all commands in current bundle.

**Collect results** for this bundle's commands. On errors: Display warning, mark status, continue processing.

**Step 5b: Check Plugin References for Bundle**

For all commands in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:analyze-plugin-references
  description: Validate references in {command-name}
  prompt: |
    Analyze plugin references in this command.

    Parameters:
    - path: {absolute_path_to_command}
    - marketplace_inventory: {complete_json_inventory_from_step_3}
    - auto-fix: true  # Auto-fix deterministic reference issues (missing/incorrect bundle prefixes)

    IMPORTANT: marketplace_inventory must contain COMPLETE inventory (agents, commands, AND skills) from Step 3's /plugin-inventory --json call.
    This complete data is required to validate Skill invocations and cross-references between all resource types.

    Return complete reference analysis with all issues found.
```

**Launch reference validation agents in parallel** (single message, multiple Task calls) for **ALL commands in current bundle**.

**⚠️ CRITICAL**: You MUST validate references for ALL commands in the bundle, not a partial subset. Validating only 4 of 13 commands violates the workflow.

**Collect results** for this bundle's reference validation. On errors: Display warning, mark status, continue processing.

**Aggregate reference findings:** Track per-command (found/correct/fixed/ambiguous) and bundle totals (checked/total/correct/fixed/issues).

**Step 5c: Aggregate Results for Bundle**

**Combine findings for this bundle's commands:**

Track bundle metrics:
- `bundle_name`: Current bundle name
- `total_commands_analyzed`: Count for this bundle
- `commands_with_issues`: Count for this bundle
- `bloated_commands`: Count for this bundle
- Issue counts: `critical`, `warnings`, `suggestions`
- Reference stats: `total_references`, `correct`, `incorrect`, `ambiguous`
- Quality scores: averages for bloat, anti-bloat compliance, structure, quality
- Per-command data: status, classification, issues, scores, reference counts

**Step 5d: Generate Bundle Summary Report**

**Display bundle summary:**

Show: Bundle name, commands analyzed (acceptable/large/bloated), issue counts, quality averages, reference stats.

Per-command: classification, line count, quality score, refs (correct/found).

**Steps 5e-5i: Apply Fix Workflow for Bundle ⚠️ FIX PHASE STARTS**

**⚠️ ANTI-SKIP PROTECTION**: Steps 5e-5i are MANDATORY if any issues were found. Skipping these steps means:
- Reference fixes claimed by agents are not verified
- Safe fixes are not applied
- Risky fixes are not prompted
- No verification that fixes actually worked
- Invalid/incomplete diagnosis results

**EXPLICIT STOP POINT**: If you have NOT completed Steps 5a-5d above, STOP and complete them first. Do not proceed to fix workflow until analysis and reference validation are complete for the entire bundle.

**If any issues found in this bundle:**

Load and apply fix workflow:
```
Skill: cui-plugin-development-tools:diagnose-reporting-templates
```

Use "Fix Workflow Pattern" to:
1. Categorize issues as safe vs risky
2. Handle reference fixes
3. Auto-apply safe fixes
4. Prompt for risky fix approval
5. Verify fixes resolved issues

**Command-specific safe fixes**: YAML frontmatter errors, missing fields, obsolete content removal, CONTINUOUS IMPROVEMENT RULE template, formatting, broken cross-references

**Command-specific risky fixes**: Bloat issues (>500 lines), clarity issues, structural issues

Track: `bundle_safe_fixes_applied`, `bundle_reference_fixes_applied`, `bundle_risky_fixes_applied`, `bundle_issues_resolved`

**Step 5i-verification: POST-FIX VERIFICATION (MANDATORY)**

**⚠️ CRITICAL**: After applying ANY fixes (Steps 5e-5i), you MUST verify actual file changes occurred:

```
Bash: git status
```

**Verification requirements:**
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

**Step 5j: MANDATORY Bundle Completion Check**

**⚠️ BEFORE proceeding to next bundle, verify ALL of the following are complete:**

- [ ] Step 5a: All commands analyzed (not partial subset)
- [ ] Step 5b: All commands reference-validated (not partial subset)
- [ ] Step 5c: Results aggregated for bundle
- [ ] Step 5d: Bundle summary displayed
- [ ] Step 5e: Issues categorized (if any issues found)
- [ ] Step 5f: Reference issues handled (if any found)
- [ ] Step 5g: Safe fixes applied (if auto-fix=true and safe issues found)
- [ ] Step 5h: Risky fixes prompted (if any risky issues found)
- [ ] Step 5i: Fixes verified (if any fixes applied)
- [ ] Step 5i-verification: Git status checked (if any fixes applied)

**If ANY checkbox above is unchecked: STOP. Complete that step before proceeding.**

**Only after ALL steps complete: Proceed to next bundle**

**CRITICAL**: Return to Step 5 for the next bundle in sorted order.

Only proceed to Step 6 when ALL bundles have been processed (analysis + fixes).

### Step 6: Generate Overall Summary Report

**Execute ONLY after all bundles have been processed.**

**Aggregate cross-bundle metrics:**
- Total commands analyzed across all bundles
- Total issues found/resolved across all bundles
- Total bloated commands across all bundles
- Bundle-by-bundle breakdown
- Overall quality metrics

**Display final summary using template:**

```
Skill: cui-plugin-development-tools:diagnose-reporting-templates
```

Use "Summary Report Template" with:
- Component Type: "Commands"
- Components: "commands"

Populate with aggregated metrics from all bundles (include bloat classification stats).

**If --save-report flag is set:**
- Write complete cross-bundle report to `commands-diagnosis-report.md`
- Inform user: "Report saved to: commands-diagnosis-report.md"


## ARCHITECTURE

Bundle-by-bundle orchestrator for token efficiency. See: `Skill: cui-plugin-development-tools:cui-marketplace-orchestration-patterns`

**Workflow**: Analysis → Reference validation → Fix → Verify

**Delegates to**:
- diagnose-command (comprehensive analysis)
- analyze-plugin-references (validation)

## TOOL USAGE

**SlashCommand** (/plugin-inventory), **Glob** (command discovery), **Skill** (diagnostic/architecture patterns), **Task** (agent orchestration), **Edit** (fixes), **AskUserQuestion** (risky fix and reference approval).

## RELATED

- `/plugin-update-command` - Apply fixes to commands
- `/plugin-diagnose-agents` - Diagnose agents
- `/plugin-diagnose-skills` - Diagnose skills
- `/plugin-diagnose-metadata` - Validate bundle metadata (plugin.json, marketplace.json)
- `/plugin-create-skill` - Extract bloated content to skills

## STANDARDS

Command analysis follows standards from the cui-marketplace-architecture skill:
- Command quality standards
- Command analysis patterns
- 8 anti-bloat rules (CRITICAL for preventing bloat)

**Architecture Compliance**: Standards are loaded via skill activation in Step 1, following proper marketplace architecture patterns.
