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

Execute plugin-inventory command with type filter:
```
SlashCommand: /plugin-inventory --type=agents --json
```

**Token Optimization:** Using --type=agents returns only agents, reducing JSON payload size.

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

**CRITICAL**: Load standards files once to avoid redundant reads in each agent.

**Load agent analysis standards:**
```
Read: marketplace/bundles/cui-plugin-development-tools/standards/agent-quality-standards.md
Read: marketplace/bundles/cui-plugin-development-tools/standards/agent-analysis-patterns.md
```

**Store standards content** in context to pass to agents in Step 3.

**Token Optimization**: These standards are loaded once here instead of 28+ times (once per agent in each diagnose-agent invocation).

### Step 3: Analyze Agents (Batched)

**CRITICAL**: Process agents in batches to manage token usage.

**Batch Configuration:**
- **Batch size**: 5 agents per batch
- **Processing**: Sequential batch execution
- **Results**: Accumulate across all batches

**For EACH batch of agents:**

1. **Select next batch** of up to 5 agents from discovery list

2. **Launch diagnose-agent agents in parallel for current batch:**

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

3. **Collect batch results** from all agents

4. **Accumulate to aggregate results**

5. **Repeat** until all agents processed

**Token Management:**
- Launch maximum 5 agents per batch
- Allow agents to complete before starting next batch
- Display progress: "Processing batch X/Y (agents N-M)..."

**Error Handling:**
- If Task fails: Display warning with agent name and error, mark as "Analysis Failed", continue with remaining in batch
- If malformed response: Display warning, mark as "Malformed Response", continue
- If timeout: Display warning, mark as "Timeout", continue
- If partial success: Include successful analyses, add "Failed Analyses" section, report partial metrics
- Continue with next batch even if current batch has failures

### Step 4: Check Plugin References (Batched)

**CRITICAL**: Process reference validation in batches matching Step 3 batches.

**For EACH batch of agents (same batches as Step 3):**

1. **Select next batch** of up to 5 agents

2. **Launch analyze-plugin-references agents in parallel for current batch:**

```
Task:
  subagent_type: cui-plugin-development-tools:analyze-plugin-references
  description: Check references in {agent-name}
  prompt: |
    Check all plugin references in this agent.

    Parameters:
    - path: {absolute_path_to_agent}
    - marketplace_inventory: {json_inventory_from_step_2}
    - auto-fix: false  # Collect issues only, don't modify in analysis phase

    IMPORTANT: marketplace_inventory is the JSON output from Step 2's /plugin-inventory --json call.
    Use this to validate references without re-discovering marketplace resources.

    Return summary report with reference validation results.
```

3. **Collect batch results** from all reference validation agents

4. **Accumulate to aggregate reference findings**

5. **Repeat** until all agents processed

**Token Management:**
- Launch maximum 5 reference validation agents per batch
- Process in same batches as Step 3 for consistency
- Display progress: "Validating references batch X/Y..."

**Error Handling:**
- If Task fails: Display warning with agent name and error, mark as "Reference Check Failed", continue
- If unexpected format: Display warning, mark as "Reference Check Error", continue
- Continue with next batch even if current batch has failures

**Aggregate reference findings:**
Track for each agent: references_found, references_correct, references_fixed, references_ambiguous.
Aggregate totals: agents_checked, total_references, correct, fixed, issues.

**Performance:**
- Analyzes 28 agents in ~6 batches
- 10 agents per batch (5 diagnose-agent + 5 analyze-plugin-references)
- ~56,000 tokens/batch (well within limits)

### Step 4.5: Validate Architectural Constraints

**For EACH agent discovered:**

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

Use Grep with these patterns across all discovered agents.

**B. Categorize findings:**

**CRITICAL Violation - Agent Self-Invocation (Pattern 22):**
- Pattern: Agent instructed to invoke SlashCommand directly
- Common location: CONTINUOUS IMPROVEMENT RULE sections
- Issue: Violates Rule 6 - agents cannot invoke commands (SlashCommand tool unavailable at runtime)
- Example: `YOU MUST immediately update this file using /plugin-update-agent`

**Correct Pattern:**
- Agent reports improvements to caller with structured suggestion
- Caller invokes command based on agent's report
- Agent returns improvement opportunity, not command invocation

**C. Track architectural violations:**
- `agents_with_self_invocation`: Count of agents with Pattern 22 violation
- `self_invocation_details`: List of (agent_name, line_number, matched_pattern) tuples

**D. Include in aggregate metrics:**

Add to overall issue tracking:
- Architectural violations as CRITICAL issues
- Track separately from tool/structure issues for clarity

**Error Handling:**
- If Grep fails: Log warning, mark validation as "Pattern Check Failed", continue
- If pattern matching errors: Display warning, continue with other validations

### Step 5: Aggregate Results

**Combine findings from all agents (diagnosis + reference checks):**

Track key metrics: total_agents_analyzed, agents_with_issues, issue counts (critical/warnings/suggestions), reference stats (total/correct/fixed/issues).
Per-agent data: status, issues, scores (tool_fit/precision/compliance), reference counts.
Overall metrics: average scores, agent quality distribution (excellent/good/fair/poor).

### Step 6: Generate Summary Report

**Display summary report with:**
- Header: "Agents Doctor - Analysis Complete"
- Agent counts by status (clean/warnings/critical)
- Issue statistics (critical/warnings/suggestions totals)
- Quality scores (avg tool_fit, precision, compliance)
- Reference validation stats (total/correct/fixed/issues)
- **Architectural violations (Pattern 22):** agents_with_self_invocation count
- Per-agent summary line: status, scores, reference counts, architectural violations
- Recommendations:
  - Critical issues requiring attention
  - Reference issues with details
  - **Architectural violations with specific agent names and recommended fixes**
  - Or success message if all clean

**If architectural violations found (Pattern 22):**
```
⚠️ CRITICAL: {count} agents contain self-invocation instructions (Pattern 22)

Agents with violations:
- {agent-name}: Line {line} - Instructs agent to invoke /{command-name}
- {agent-name}: Line {line} - Instructs agent to invoke /{command-name}

❌ Issue: Agents CANNOT invoke commands (Rule 6 - SlashCommand tool unavailable at runtime)

Recommended Fix:
Update CONTINUOUS IMPROVEMENT RULE sections to:
✅ REPORT improvements to caller (not invoke commands directly)
✅ Return structured improvement suggestions
✅ Let CALLER invoke /plugin-update-agent based on report

Use /plugin-update-agent to fix each agent's CONTINUOUS IMPROVEMENT RULE section.

Reference: agent-analysis-patterns.md Pattern 22
```

**If --save-report flag is set:**
- Write the complete report above to `agents-diagnosis-report.md` in project root
- Inform user: "Report saved to: agents-diagnosis-report.md"

**Default behavior (no flag):**
- Display report only (as shown above)
- Do NOT create any files

**Error Handling for Report Writing:**
- If file write fails: Display error with message and possible causes, note report was displayed, continue
- If path doesn't exist: Display error with current directory, note report was displayed, continue

==================================================
⚠️ CRITICAL: ANALYSIS PHASE COMPLETE
==================================================

You have completed PHASE 1 (Analysis).

**YOU MUST NOW PROCEED TO PHASE 2 (Fix Workflow)**

DO NOT STOP HERE. The analysis is useless without fixes.

If any issues were found (warnings or suggestions):
→ Continue to Step 7: Categorize Issues
→ Continue to Step 8: Apply Safe Fixes
→ Continue to Step 9: Prompt for Risky Fixes
→ Continue to Step 10: Verify Fixes

If zero issues found:
→ Skip to completion message

==================================================

### Step 7: Categorize Issues for Fixing ⚠️ PHASE 2 STARTS HERE

**ALWAYS execute this step if any issues were found (warnings or suggestions).**

**Load fix workflow skill:**

```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

**Categorize all issues into Safe vs Risky using patterns from cui-fix-workflow skill.**

Read categorization patterns:
```
Read: standards/categorization-patterns.md (from cui-fix-workflow)
```

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

### Step 8: Apply Safe Fixes

**When to execute**: If auto-fix=true (default) AND safe fixes exist

**CRITICAL: If you reached Step 6, you MUST execute this step if safe fixes exist. This is not optional.**

**Follow safe fix patterns from cui-fix-workflow skill.**

**Apply agent-specific safe fixes using Edit tool:**

**YAML syntax errors:**
```
Edit: {agent-file}
- Fix YAML frontmatter syntax
- Add missing required fields with defaults
- Correct field name typos
```

**Tool declaration fixes:**
```
Edit: {agent-file}
- Remove unused tools from allowed-tools array
- Add missing tools found in workflow (Read, Glob, Grep, etc.)
- Ensure proper tool declaration format
```

**Add missing CONTINUOUS IMPROVEMENT RULE:**
```
Edit: {agent-file}
- Insert CONTINUOUS IMPROVEMENT RULE template after description
- Include agent-specific improvement areas
```

**Formatting normalization:**
```
Edit: {agent-file}
- Normalize whitespace and indentation
- Fix heading hierarchy
- Ensure proper markdown structure
```

**Track fixes applied using tracking patterns from cui-fix-workflow:**
```json
{
  "safe_fixes_applied": {count},
  "by_type": {
    "yaml_fixes": {count},
    "tool_declaration_fixes": {count},
    "continuous_improvement_added": {count},
    "formatting_fixes": {count}
  }
}
```

### Step 9: Prompt for Risky Fixes

**When to execute**: If risky fixes exist (regardless of auto-fix setting)

**Follow prompting patterns from cui-fix-workflow skill.**

Read prompting patterns:
```
Read: standards/prompting-patterns.md (from cui-fix-workflow)
```

**Group risky fixes by agent-specific categories:**

1. **Tool Violations** - Task tool misuse, missing critical tools
2. **Architectural Issues** - Pattern 22 violations, self-invocation instructions
3. **Best Practice Violations** - Maven anti-patterns, ambiguous instructions, precision issues

**Use AskUserQuestion with standard structure from prompting patterns:**

```
AskUserQuestion:
  questions: [
    {
      question: "Apply fixes for {Category} issues?",
      header: "{Category}",
      multiSelect: true,
      options: [
        {
          label: "Fix: {specific-issue}",
          description: "Agent: {agent-name}. Impact: {what-changes}. Location: {file}:{line}"
        },
        ...
        {
          label: "Skip all {category} fixes",
          description: "Continue without fixing this category"
        }
      ]
    }
  ]
```

**Process user selections following prompting patterns:**
- For each selected fix: Apply using Edit tool (may require workflow changes), increment `risky_fixes_applied`
- For unselected fixes: Skip, increment `risky_fixes_skipped`
- If "Skip all" selected: Skip entire category, increment `risky_fixes_skipped` by count

**Note**: For complex architectural changes:
- Description should explain workflow restructuring required
- Consider deferring to `/plugin-update-agent` for complex refactoring
- Track deferred fixes separately

**Track risky fixes using tracking patterns from cui-fix-workflow:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "risky_fixes_deferred_to_update_agent": {count},
  "fixes_by_category": {
    "tool_violations": {applied: count, skipped: count, deferred: count},
    "architectural": {applied: count, skipped: count, deferred: count},
    "best_practices": {applied: count, skipped: count, deferred: count}
  }
}
```

### Step 10: Verify Fixes

**When to execute**: After any fixes applied (Step 8 or Step 9)

**Follow verification patterns from cui-fix-workflow skill.**

Read verification patterns:
```
Read: standards/verification-patterns.md (from cui-fix-workflow)
```

**Re-run analysis on modified agents:**
```
Task:
  subagent_type: cui-plugin-development-tools:diagnose-agent
  description: Verify fixes for {agent-name}
  prompt: |
    Re-analyze this agent after fixes.

    Parameters:
    - agent_path: {absolute_path_to_agent}

    Return complete JSON report.
```

**Compare before/after using verification patterns:**
```json
{
  "verification": {
    "agents_fixed": {count},
    "issues_resolved": {count},
    "issues_remaining": {count},
    "new_issues": {count}  // Should be 0!
  }
}
```

**Report verification results following verification patterns:**
```
==================================================
Verification Complete
==================================================

✅ {issues_resolved} issues resolved
{if issues_remaining > 0}
⚠️ {issues_remaining} issues remain (require manual intervention or /plugin-update-agent)
{endif}
{if new_issues > 0}
❌ {new_issues} NEW issues introduced (fixes need review!)
{endif}
```

## ARCHITECTURE

This command is a batched orchestrator designed to handle large-scale marketplace analysis following patterns from the cui-marketplace-orchestration-patterns skill.

**For detailed orchestration architecture, see:**
```
Skill: cui-plugin-development-tools:cui-marketplace-orchestration-patterns
```

**Key Architecture Characteristics:**
- Batched processing (5 agents per batch, 6 batches for 28 agents)
- Token-optimized (standards pre-loading, streamlined output, filtered inventory)
- Parallel execution within batches, sequential across batches
- Two-phase workflow: Analysis → Fix

**All analysis logic is in specialized agents:**
- diagnose-agent (comprehensive agent analysis with streamlined output support)
- analyze-plugin-references (plugin reference validation)

## TOOL USAGE

- **SlashCommand**: Execute /plugin-inventory --type=agents --json (marketplace discovery, filtered)
- **Glob**: Discover agents in global/project scopes (non-prompting)
- **Read**: Pre-load standards once (token optimization)
- **Task**: Launch diagnose-agent and analyze-plugin-references agents in batches (parallel within batch, sequential across batches)
- **Grep**: Detect architectural violations (Pattern 22 self-invocation)
- **Skill**: Load diagnostic patterns and fix workflow patterns
- **Edit**: Apply safe and approved risky fixes
- **AskUserQuestion**: Prompt for risky fix approval

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
