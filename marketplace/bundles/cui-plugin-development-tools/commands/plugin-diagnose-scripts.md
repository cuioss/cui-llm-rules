---
name: plugin-diagnose-scripts
description: Analyze, verify, and fix marketplace scripts for structure, testing, and documentation compliance
---

# Scripts Doctor - Verify and Fix Scripts

Orchestrates comprehensive analysis of marketplace scripts by verifying documentation, testing, and execution for each script.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-scripts update="[your improvement]"` with:
1. Improved script quality analysis patterns and test coverage detection
2. Better methods for identifying missing documentation or test gaps
3. More effective test execution validation and failure detection approaches
4. Enhanced script-to-SKILL.md documentation verification strategies
5. Any lessons learned about script development standards and testing patterns

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace scripts
- **script-name** (optional): Review a specific script by name (e.g., `analyze-markdown-file.sh`)
- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Analyze all marketplace scripts

## WORKFLOW

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-6)**
- Discover scripts
- Analyze each script
- Generate report

**PHASE 2: Fix Workflow (Steps 7-10)**
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

**Load marketplace architecture standards**:

```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components including script development standards.

**Load bundle orchestration compliance patterns (MANDATORY)**:

```
Skill: cui-plugin-development-tools:bundle-orchestration-compliance
```

This enforces mandatory completion checklists, anti-skip protections, and post-fix verification requirements for bundle-by-bundle workflows.

### Step 2: Discover Scripts

**Parse parameters** to determine scope.

**For marketplace scope (default):**

Execute scan-marketplace-inventory.sh script to get complete marketplace inventory including scripts:
```
Bash: ./.claude/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh --scope marketplace --resource-types scripts
```

Parse JSON output from script:
- Extract `bundles[]` array from JSON response
- For each bundle, collect `bundle.scripts[]` with `name`, `path`, `skill_name`, and `runtime_mount` fields
- Build flat list of script paths from all bundles

**Extract script names** from file paths.

**If specific script name provided:** Filter list to matching script only; display error and exit if no match found.

**Error Handling:** Display descriptive errors and suggest alternatives for discovery failures; exit gracefully if no scripts found.

### Step 3: Group Scripts by Bundle and Skill

**CRITICAL**: Organize scripts by bundle and skill for sequential processing.

**Parse inventory from Step 2:**
- Extract `bundles[]` array from inventory JSON
- For each bundle, identify bundle name and collect all scripts with their paths and skill associations
- Create bundle-to-scripts mapping with skill context

**Sort bundles:**
1. **First**: `cui-plugin-development-tools` (always first)
2. **Then**: All other bundles alphabetically by name

Display: `Processing {total_bundles} bundles with {total_scripts} scripts`

### Step 4: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps (4a-4h) for one bundle before moving to the next.

**⚠️ MANDATORY COMPLETION CHECK**: You MUST NOT skip Steps 4d-4h. Jumping directly to Step 5 (summary) without completing the fix workflow produces incomplete, invalid results.

**For EACH bundle in sorted order:**

Display: `Processing bundle: {bundle_name} ({script_count} scripts)`

**Step 4a: Analyze Bundle Scripts**

For each script in current bundle, verify:

1. **SKILL.md documentation**: Search for script reference in `{skill_path}/SKILL.md`
2. **Test file existence**: Check `test/cui-plugin-development-tools/{skill_name}/test-{script_name}.sh`
3. **Test execution**: Run test file, parse pass/fail counts, verify 100% pass rate
4. **Help output**: Execute script with `--help` flag

Track per-script metrics: `documented_in_skill`, `has_test_file`, `test_status` (PASS/FAIL/NO_TEST), `tests_passed/failed/total`, `has_help_output`

**Issue categories:**
- CRITICAL: Missing documentation, missing tests, test failures, no help output
- WARNING: <5 test cases, incomplete documentation

**Step 4b: Aggregate Results for Bundle**

Combine findings: bundle metrics (name, scripts analyzed, issues by severity), test stats (total/passed/failed), documentation coverage (documented/undocumented), per-script data.

**Step 4c: Generate Bundle Summary Report**

Display: Bundle name, scripts by status, issue counts, test pass rates, documentation coverage. Per-script: name, test status, documented, issues.

**Steps 4d-4g: Apply Fix Workflow ⚠️ FIX PHASE**

**⚠️ MANDATORY if any issues found.** Complete Steps 4a-4c first.

```
Skill: cui-plugin-development-tools:diagnose-reporting-templates
```

Use "Fix Workflow Pattern": categorize (safe vs risky), auto-apply safe fixes, prompt for risky approval, verify resolution.

**Safe fixes**: Missing help output, incomplete SKILL.md updates
**Risky fixes**: Creating test files, fixing test failures

Track: `bundle_safe_fixes_applied`, `bundle_risky_fixes_applied`, `bundle_issues_resolved`

**Step 4g-verification: POST-FIX VERIFICATION (MANDATORY)**

After ANY fixes: `git status` to verify actual file changes. Compare fixes claimed vs files modified. Report PASS/FAIL.

**Step 4h: Bundle Completion Check**

Verify ALL complete: Steps 4a (analysis), 4b (aggregation), 4c (summary), 4d-4g (fixes if needed), 4g-verification (git check if fixes applied).

Only after ALL complete: Proceed to next bundle. Return to Step 4 for next bundle. Proceed to Step 5 only when ALL bundles processed.

### Step 5: Generate Overall Summary Report

After all bundles processed, aggregate cross-bundle metrics (total scripts, issues, fixes, test pass rates, documentation coverage).

```
Skill: cui-plugin-development-tools:diagnose-reporting-templates
```

Use "Summary Report Template" with Component Type: "Scripts", Components: "scripts". Populate with aggregated metrics.

If `--save-report`: Write to `scripts-diagnosis-report.md`

## ARCHITECTURE

Bundle-by-bundle orchestrator for token efficiency. See: `Skill: cui-plugin-development-tools:cui-marketplace-orchestration-patterns`

**Workflow**: Discovery → Documentation verification → Test verification → Test execution → Fix → Verify

**Delegates to**:
- scan-marketplace-inventory.sh (script discovery)
- Individual test scripts (validation)

## TOOL USAGE

**Bash** (scan-marketplace-inventory.sh, test execution, script validation), **Read** (SKILL.md verification), **Grep** (script name search in SKILL.md), **Skill** (diagnostic/architecture patterns), **Edit** (fixes), **AskUserQuestion** (risky fix approval).

## RELATED

- `/plugin-diagnose-agents` - Diagnose agents
- `/plugin-diagnose-commands` - Diagnose commands
- `/plugin-diagnose-skills` - Diagnose skills
- `/plugin-diagnose-metadata` - Validate bundle metadata (plugin.json, marketplace.json)

## CRITICAL RULES

ALL scripts MUST have: 100% test pass rate, SKILL.md documentation, test file in `test/cui-plugin-development-tools/{skill_name}/`, `--help` output.

## STANDARDS

Script development standards, test-driven development, ground truth validation (see cui-marketplace-architecture skill).
