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

**Optionally load marketplace architecture standards**:

You may optionally load the marketplace architecture skill for additional architectural context:
```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components that may be useful for understanding agent design principles.

### Step 2: Discover Agents

**Parse parameters** to determine scope.

**For marketplace scope (default):**

Execute plugin-inventory command to get complete marketplace inventory:
```
SlashCommand: /plugin-inventory --json
```

**CRITICAL:** Must get complete inventory (agents, commands, AND skills) because analyze-plugin-references agents need skill data to validate Skill invocations.

Parse JSON output:
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

**If specific agent name provided:**
- Filter list to matching agent only
- If no match found: Display error and exit

**If no parameters (interactive mode):**
- Display numbered list of all agents found
- Separate standalone and bundle agents
- Let user select which to analyze or change scope

**Error Handling:**
- If Task fails (marketplace scope): Display error with message, exit with error status
- If inventory.bundles is empty: Display "No agents found in marketplace", suggest trying different scope
- If Glob fails (global/project scope): Display error with path and suggestions, exit with error status
- If no agents found: Display scopes searched and suggest trying different scope, exit gracefully

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
1. cui-plugin-development-tools ({agent_count} agents)
2. {bundle-name} ({agent_count} agents)
...
```

### Step 4: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps for one bundle before moving to the next.

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

**Collect results** for this bundle's agents.

**Error Handling:**
- If Task fails: Display warning with agent name and error, mark as "Analysis Failed", continue with remaining agents
- If malformed response: Display warning, mark as "Malformed Response", continue
- If timeout: Display warning, mark as "Timeout", continue

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

**Launch reference validation agents in parallel** (single message, multiple Task calls) for all agents in current bundle.

**Collect results** for this bundle's reference validation.

**Error Handling:**
- If Task fails: Display warning with agent name and error, mark as "Reference Check Failed", continue
- If unexpected format: Display warning, mark as "Reference Check Error", continue

**Aggregate reference findings for this bundle:**
Track for each agent: references_found, references_correct, references_fixed, references_ambiguous.
Bundle totals: agents_checked, total_references, correct, fixed, issues.

**Step 4c: Validate Architectural Constraints for Bundle**

For each agent in current bundle:

Check for architectural violations using pattern detection from Pattern 22 (agent-analysis-patterns.md).

**A. Self-Invocation Detection:**

Search agent content for patterns indicating agent is instructed to call commands:

```
Grep patterns to detect:
- "YOU MUST.*using\s+/plugin-"
- "YOU MUST.*using\s+/cui-"
- "invoke\s+/plugin-"
- "call\s+/plugin-"
- "SlashCommand:\s*/plugin-"
```

Use Grep with these patterns across agents in current bundle.

**B. Verify Flagged Violations (MANDATORY):**

**CRITICAL**: Before reporting violations, re-verify each flagged file to eliminate false positives.

**For each file flagged by Grep in Step A:**

1. **Read exact flagged lines with context**:
   ```
   Read: {agent_file_path}
   ```
   Focus on lines matching patterns from Step A, include ±2 lines context.

2. **Distinguish runtime invocations from documentation**:

   **✅ ACTUAL VIOLATIONS (runtime invocations)**:
   - Direct tool usage: `SlashCommand: /plugin-update-agent`
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
   - Track: `violations_flagged_by_grep`, `violations_verified`, `false_positives_filtered`

**Error Handling:**
- If Read fails: Log warning, mark as "Verification Failed", exclude from violation count
- If context unclear: Include in manual review list rather than auto-reporting as violation

**C. Categorize findings:**

**CRITICAL Violation - Agent Self-Invocation (Pattern 22):**
- Pattern: Agent instructed to invoke SlashCommand directly
- Common location: CONTINUOUS IMPROVEMENT RULE sections
- Issue: Violates Rule 6 - agents cannot invoke commands (SlashCommand tool unavailable at runtime)
- Example: `YOU MUST immediately update this file using /plugin-update-agent`

**Correct Pattern:**
- Agent reports improvements to caller with structured suggestion
- Caller invokes command based on agent's report
- Agent returns improvement opportunity, not command invocation

**C. Track architectural violations for this bundle:**
- `agents_with_self_invocation`: Count of agents with Pattern 22 violation
- `self_invocation_details`: List of (agent_name, line_number, matched_pattern) tuples

**Error Handling:**
- If Grep fails: Log warning, mark validation as "Pattern Check Failed", continue
- If pattern matching errors: Display warning, continue with other validations

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

```
==================================================
Bundle: {bundle_name}
==================================================

Agents Analyzed: {total}
- Clean: {count} ✅
- With warnings: {count} ⚠️
- With critical issues: {count} ❌

Issue Statistics:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}

Quality Scores:
- Average Tool Fit: {score}/100
- Average Precision: {score}/100
- Average Compliance: {score}/100

Reference Validation:
- Total references: {total_references}
- Correct: {references_correct}
- Fixed: {references_fixed}
- Issues: {references_with_issues}

Architectural Violations:
- Self-invocation violations (Pattern 22): {agents_with_self_invocation}

Per-Agent Summary:
- {agent-1}: {status} | TF: {score} | P: {score} | C: {score} | Refs: {correct}/{found}
- {agent-2}: {status} | TF: {score} | P: {score} | C: {score} | Refs: {correct}/{found}
...
```

**If architectural violations found (Pattern 22):**
```
⚠️ CRITICAL: {count} agents in {bundle_name} contain self-invocation instructions

Agents with violations:
- {agent-name}: Line {line} - Instructs agent to invoke /{command-name}

❌ Issue: Agents CANNOT invoke commands (Rule 6 - SlashCommand tool unavailable at runtime)

Recommended Fix:
Update CONTINUOUS IMPROVEMENT RULE sections to REPORT improvements to caller.

Reference: agent-analysis-patterns.md Pattern 22
```

**Step 4f: Categorize Issues for Bundle ⚠️ FIX PHASE STARTS

**If any issues found in this bundle:**

**Load fix workflow skill (once, if not already loaded):**
```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

**Categorize issues for this bundle into Safe vs Risky:**

**Agent-specific safe fix types:**
- YAML frontmatter syntax errors
- Missing YAML fields (add defaults: `description`)
- Remove unused tools from `allowed-tools` frontmatter
- Add missing tools to `allowed-tools` based on workflow usage
- Add missing CONTINUOUS IMPROVEMENT RULE template
- Formatting/whitespace normalization

**Agent-specific risky fix categories:**
1. **Tool Violations** - Task tool misuse, missing tool declarations
2. **Architectural Issues** - Pattern 22 violations, self-invocation instructions
3. **Best Practice Violations** - Maven anti-patterns, ambiguous instructions, precision issues

**Step 4g: Apply Safe Fixes for Bundle

**When to execute**: If auto-fix=true (default) AND safe fixes exist in this bundle

**Apply safe fixes for agents in this bundle using Edit tool:**

Track fixes: `bundle_safe_fixes_applied`, `by_type` (yaml, tools, continuous_improvement, formatting)

**Step 4h: Prompt for Risky Fixes for Bundle

**When to execute**: If risky fixes exist in this bundle

**Use AskUserQuestion for risky fixes in this bundle:**

Group by categories: Tool Violations, Architectural Issues, Best Practice Violations

Track: `bundle_risky_fixes_prompted`, `bundle_risky_fixes_applied`, `bundle_risky_fixes_skipped`

**Step 4i: Verify Fixes for Bundle

**When to execute**: After any fixes applied in this bundle

**Re-run analysis on modified agents in this bundle:**

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

**Step 4j: Repeat for Next Bundle**

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

**Key Architecture Characteristics:**
- **Bundle-by-bundle processing**: Process one bundle completely before moving to next
- **Bundle ordering**: cui-plugin-development-tools first, then alphabetically
- **Complete workflow per bundle**: Analysis → Reference validation → Fix → Verify
- **Token-optimized**: Standards pre-loading, streamlined output, scoped processing
- **Parallel execution within bundle**: All agents for a bundle run in parallel
- **Sequential across bundles**: Next bundle only starts after previous is complete

**Processing Flow:**
1. Discover all bundles and sort (cui-plugin-development-tools first, then alphabetical)
2. For each bundle:
   - Analyze all agents in bundle (parallel)
   - Validate all references in bundle (parallel)
   - Validate architectural constraints
   - Aggregate bundle results
   - Generate bundle report
   - Categorize issues for bundle
   - Apply safe fixes for bundle
   - Prompt for risky fixes for bundle
   - Verify fixes for bundle
3. Generate overall cross-bundle summary

**All analysis logic is in specialized agents:**
- diagnose-agent (comprehensive agent analysis with streamlined output support)
- analyze-plugin-references (plugin reference validation)

## TOOL USAGE

- **SlashCommand**: Execute /plugin-inventory --json (marketplace discovery with complete inventory)
- **Glob**: Discover agents in global/project scopes (non-prompting)
- **Skill**: Load diagnostic patterns, marketplace architecture, and fix workflow patterns
- **Task**: Launch diagnose-agent and analyze-plugin-references agents (parallel within bundle)
- **Grep**: Detect architectural violations (Pattern 22 self-invocation)
- **Edit**: Apply safe and approved risky fixes
- **AskUserQuestion**: Prompt for risky fix approval per bundle

## RELATED

- `/plugin-update-agent` - Apply fixes to agents
- `/plugin-diagnose-commands` - Diagnose commands
- `/plugin-diagnose-skills` - Diagnose skills
- `/plugin-diagnose-bundle` - Diagnose entire bundle

## STANDARDS

Agent analysis follows:
- Agent quality standards (bundles/cui-plugin-development-tools/standards/agent-quality-standards.md)
- Agent analysis patterns (bundles/cui-plugin-development-tools/standards/agent-analysis-patterns.md)

**Token Optimization**: Standards are pre-loaded once in Step 2a and passed to all agents to avoid 28+ redundant file reads.
