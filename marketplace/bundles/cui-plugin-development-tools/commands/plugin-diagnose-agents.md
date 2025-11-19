---
name: plugin-diagnose-agents
description: Analyze, verify, and fix agents for tool coverage, best practices, and structural issues
---

# Agents Doctor - Verify and Fix Agents

Orchestrates comprehensive analysis of agents by coordinating diagnose-agent for each agent.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-agents update="[your improvement]"` with:
1. Improved agent quality analysis patterns and tool fit detection
2. Better methods for identifying tool coverage gaps and precision issues
3. More effective compliance checking and structural validation approaches
4. Enhanced error handling and partial success detection in parallel analysis
5. Any lessons learned about agent design patterns and best practices

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace agents (standalone + bundle agents)
- **scope=global**: Analyze agents in global location (~/.claude/agents/)
- **scope=project**: Analyze agents in project location (.claude/agents/)
- **agent-name** (optional): Review a specific agent by name (e.g., `maven-project-builder`)
- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Interactive mode with marketplace default

## WORKFLOW

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-6)**
- Discover components
- Analyze each component
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

This provides architecture rules and validation patterns for marketplace components.

**Load bundle orchestration compliance patterns (MANDATORY)**:

```
Skill: cui-plugin-development-tools:bundle-orchestration-compliance
```

This enforces mandatory completion checklists, anti-skip protections, and post-fix verification requirements for bundle-by-bundle workflows.

### Step 2: Discover Agents

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

**CRITICAL:** Must get complete inventory (agents, commands, AND skills) because analyze-plugin-references agents need skill data to validate Skill invocations.

Parse JSON output from agent:
- Extract `bundles[]` array from JSON response
- For each bundle, collect `bundle.agents[]` with `name` and `path` fields
- Build flat list of agent paths from all bundles

**For global scope:**
```
Glob: pattern="*.md", path="~/.claude/agents"
```

**For project scope:**
```
Glob: pattern="*.md", path=".claude/agents"
```

**Extract agent names** from file paths.

**If specific agent name provided:** Filter list to matching agent only; display error and exit if no match found.

**If no parameters (interactive mode):** Display numbered list, separate standalone/bundle agents, let user select.

**Error Handling:** Display descriptive errors and suggest alternatives for discovery failures; exit gracefully if no agents found.

### Step 2a: Load Analysis Standards (Once)

**CRITICAL**: Activate marketplace architecture skill to load agent analysis standards.

**Activate skill:**
```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This loads all necessary agent analysis standards including:
- agent-quality-standards.md - Quality criteria and best practices
- agent-analysis-patterns.md - Common issues and detection patterns
- architecture-rules.md - Architectural compliance requirements

**Token Optimization**: Skill activation provides standards automatically without explicit file reads, avoiding 28+ redundant Read operations.

### Step 3: Group Agents by Bundle

**CRITICAL**: Organize agents by bundle for sequential processing.

**Parse inventory from Step 2:**
- Extract `bundles[]` array from inventory JSON
- For each bundle, identify bundle name and collect all agents with their paths
- Create bundle-to-agents mapping

**Sort bundles:**
1. **First**: `cui-plugin-development-tools` (always first)
2. **Then**: All other bundles alphabetically by name

Display: `Processing {total_bundles} bundles in order: {bundle_list}`

### Step 4: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps (4a-4j) for one bundle before moving to the next.

**⚠️ MANDATORY COMPLETION CHECK**: You MUST NOT skip Steps 4c-4j. Jumping directly to Step 5 (summary) without completing the fix workflow produces incomplete, invalid results.

**For EACH bundle in sorted order:**

Display: `Processing bundle: {bundle_name} ({agent_count} agents)`

**Step 4a: Analyze Bundle Agents**

For all agents in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:diagnose-agent
  description: Analyze {agent-name}
  prompt: |
    Analyze this agent comprehensively.

    Parameters:
    - agent_path: {absolute_path_to_agent}

    IMPORTANT: Standards have been pre-loaded by orchestrator.
    Skip Step 1 (Load Analysis Standards) - use standards from context instead.

    IMPORTANT: Use streamlined output format (issues only).
    Return minimal JSON - CLEAN agents get {"status": "CLEAN"},
    agents with issues get only critical_issues/warnings/suggestions arrays.

    This reduces token usage from ~600-800 to ~200-400 tokens per agent.
```

**Launch agents in parallel** (single message, multiple Task calls) for all agents in current bundle.

**Collect results** for this bundle's agents. On errors: Display warning, mark status, continue processing.

**Step 4b: Check Plugin References for Bundle**

For all agents in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:analyze-plugin-references
  description: Check references in {agent-name}
  prompt: |
    Check all plugin references in this agent.

    Parameters:
    - path: {absolute_path_to_agent}
    - marketplace_inventory: {complete_json_inventory_from_step_2}
    - auto-fix: true  # Auto-fix deterministic reference issues (missing/incorrect bundle prefixes)

    IMPORTANT: marketplace_inventory must contain COMPLETE inventory (agents, commands, AND skills) from Step 2's /plugin-inventory --json call.
    This complete data is required to validate Skill invocations and cross-references between all resource types.

    Return summary report with reference validation results.
```

**Launch reference validation agents in parallel** (single message, multiple Task calls) for **ALL agents in current bundle**.

**⚠️ CRITICAL**: You MUST validate references for ALL agents in the bundle, not a partial subset. Validating only some agents violates the workflow.

**Collect results** for this bundle's reference validation. On errors: Display warning, mark status, continue processing.

**Aggregate reference findings:** Track per-agent (found/correct/fixed/ambiguous) and bundle totals (checked/total/correct/fixed/issues).

**Step 4c: Validate Architectural Constraints for Bundle**

Validate architectural constraints using the architectural-validator agent:

```
Task:
  subagent_type: cui-plugin-development-tools:architectural-validator
  description: Validate architectural constraints for {bundle_name}
  prompt: |
    Validate architectural constraints for agents in this bundle.

    Parameters:
    - file_paths: {array_of_agent_paths_in_bundle}
    - validation_type: "self-invocation"

    Return validation results with verified violations only (false positives filtered).
```

**Parse validation results:** Extract `summary.files_with_violations`, `violations_by_file`, track violation counts and details for bundle metrics.

On errors: Log warning, mark as "Architectural Check Failed", continue processing.

**Step 4d: Aggregate Results for Bundle**

**Combine findings for this bundle's agents (diagnosis + reference checks + architectural validation):**

Track bundle metrics:
- `bundle_name`: Current bundle name
- `total_agents_analyzed`: Count for this bundle
- `agents_with_issues`: Count for this bundle
- Issue counts: `critical`, `warnings`, `suggestions`
- Reference stats: `total_references`, `correct`, `fixed`, `issues`
- Architectural violations: `agents_with_self_invocation`
- Per-agent data: status, issues, scores, reference counts

**Display bundle summary:**

Show: Bundle name, agents analyzed (clean/warnings/critical), issue counts, quality averages, reference stats, architectural violations.

Per-agent: status, scores (TF/P/C), refs (correct/found).

If Pattern 22 violations: Display warning with agent names, line numbers, and fix guidance.

**Steps 4f-4i: Apply Fix Workflow for Bundle ⚠️ FIX PHASE STARTS**

**⚠️ ANTI-SKIP PROTECTION**: Steps 4f-4i are MANDATORY if any issues were found. Skipping these steps means:
- Reference fixes claimed by agents are not verified
- Safe fixes are not applied
- Risky fixes are not prompted
- No verification that fixes actually worked
- Invalid/incomplete diagnosis results

**EXPLICIT STOP POINT**: If you have NOT completed Steps 4a-4d above, STOP and complete them first. Do not proceed to fix workflow until analysis, reference validation, architectural validation, and aggregation are complete for the entire bundle.

**If any issues found in this bundle:**

Load and apply fix workflow from skill:
```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

Follow the skill's workflow: Categorize → Apply Safe Fixes → Prompt for Risky Fixes → Verify Fixes.

**If NO issues found:**
- Skip Steps 4f-4i (no fixes needed)
- Mark as N/A in completion checklist
- Proceed to Step 4i-verification

**Agent-specific configuration for categorization:**

**Safe fix types:**
- YAML frontmatter syntax errors, missing fields
- Add/remove tools in `allowed-tools` based on workflow
- Add missing CONTINUOUS IMPROVEMENT RULE template
- Formatting/whitespace normalization

**Risky fix categories:**
- Tool Violations, Architectural Issues, Best Practice Violations

Track: `bundle_safe_fixes_applied`, `bundle_risky_fixes_applied`, `bundle_issues_resolved`

**Step 4i-verification: POST-FIX VERIFICATION (MANDATORY)**

**⚠️ CRITICAL**: After applying ANY fixes (Steps 4f-4i), you MUST verify actual file changes occurred.

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
- Mark as N/A: "✓ Step 4i-verification: Git status checked (N/A - no fixes applied)"

**Step 4j: MANDATORY Bundle Completion Check**

**⚠️ BEFORE proceeding to next bundle, verify ALL of the following are complete:**

- [ ] **Step 4a**: All agents analyzed (not partial subset)
- [ ] **Step 4b**: All agents reference-validated (not partial subset)
- [ ] **Step 4c**: Architectural constraints validated
- [ ] **Step 4d**: Results aggregated for bundle
- [ ] **Steps 4f-4i**: Fix workflow complete (if any issues found) OR marked N/A (if no issues)
- [ ] **Step 4i-verification**: Git status checked (if any fixes applied) OR marked N/A (if no fixes)

**If ANY checkbox above is unchecked: STOP. Complete that step before proceeding.**

**Only after ALL steps complete: Proceed to next bundle**

**CRITICAL**: Return to Step 4 for the next bundle in sorted order.

Only proceed to Step 5 when ALL bundles have been processed (analysis + fixes).

### Step 5: Generate Overall Summary Report

**Execute ONLY after all bundles have been processed.**

**Aggregate cross-bundle metrics:**
- Total agents analyzed across all bundles
- Total issues found/resolved across all bundles
- Bundle-by-bundle breakdown
- Overall quality metrics

**Display final summary:**
```
==================================================
Agents Doctor - All Bundles Complete
==================================================

Bundles Processed: {total_bundles}
Total Agents: {total_agents}

Overall Statistics:
- Agents clean: {count} ✅
- Agents with warnings: {count} ⚠️
- Agents with critical issues: {count} ❌

Total Issues:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}

Fixes Applied:
- Safe fixes: {count}
- Risky fixes: {count}
- Issues resolved: {count}

By Bundle:
- cui-plugin-development-tools: {agents} agents | {issues} issues | {fixes} fixed
- {bundle-2}: {agents} agents | {issues} issues | {fixes} fixed
...

{if all clean}
✅ All agents across all bundles are high quality!
{endif}
```

**If --save-report flag is set:**
- Write complete cross-bundle report to `agents-diagnosis-report.md`
- Inform user: "Report saved to: agents-diagnosis-report.md"

## ARCHITECTURE

This command is a bundle-by-bundle orchestrator designed to prevent token overload by processing marketplace resources sequentially by bundle.

**For detailed orchestration architecture, see:**
```
Skill: cui-plugin-development-tools:cui-marketplace-orchestration-patterns
```

**Key Characteristics:**
- Bundle-by-bundle processing with cui-plugin-development-tools first, then alphabetically
- Complete workflow per bundle: Analysis → Reference validation → Architectural validation → Fix → Verify
- Token-optimized: Standards pre-loading, streamlined output, scoped processing
- Parallel execution within bundle, sequential across bundles

**Analysis delegated to specialized agents:**
- diagnose-agent (comprehensive agent analysis)
- analyze-plugin-references (reference validation)
- architectural-validator (constraint validation)

## TOOL USAGE

**SlashCommand** (/plugin-inventory), **Glob** (agent discovery), **Skill** (diagnostic/architecture patterns), **Task** (agent orchestration), **Edit** (fixes), **AskUserQuestion** (risky fix approval).

## RELATED

- `/plugin-update-agent` - Apply fixes to agents
- `/plugin-diagnose-commands` - Diagnose commands
- `/plugin-diagnose-skills` - Diagnose skills
- `/plugin-diagnose-metadata` - Validate bundle metadata (plugin.json, marketplace.json)

## STANDARDS

Agent analysis follows:
- Agent quality standards (bundles/cui-plugin-development-tools/standards/agent-quality-standards.md)
- Agent analysis patterns (bundles/cui-plugin-development-tools/standards/agent-analysis-patterns.md)

**Token Optimization**: Standards are pre-loaded once in Step 2a and passed to all agents to avoid 28+ redundant file reads.
