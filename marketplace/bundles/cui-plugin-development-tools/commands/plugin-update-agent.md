---
name: plugin-update-agent
description: Update an agent with improvements, verify quality, and prevent duplication
---

# Update Agent

Updates an existing agent with proposed improvements while ensuring quality, correctness, and preventing duplication.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-update-agent update="[your improvement]"` with:
1. Improved validation patterns for proposed agent updates
2. Better methods for detecting tool coverage gaps
3. More effective strategies for ensuring agent correctness
4. Enhanced quality verification techniques specific to agents
5. Any lessons learned about agent evolution and maintenance

This ensures the command evolves and becomes more effective with each execution.

## PURPOSE

When you need to update an existing agent based on lessons learned or improvements discovered, this command:

1. Validates the proposed update is sound and applicable
2. Checks for duplication with existing agent content and other agents
3. Applies the update using appropriate tools
4. Runs formal verification via `/plugin-diagnose-agents`
5. Reports results and any issues found

## PARAMETERS

**Required Parameters** (will prompt if missing):

- **agent-name**: Name of agent to update (e.g., `pr-review-responder`)
- **update-description**: Description of what to update and why

**Optional Parameters**:

- **scope**: Where to find agent - `marketplace` (default), `global`, `project`
- **--skip-diagnosis**: Skip post-update diagnosis (not recommended)

## WORKFLOW

### Step 1: Validate Input Parameters

**Prompt for missing parameters:**
- `agent-name`: "Which agent should be updated? (provide agent name)"
- `update-description`: "What improvement should be applied? (describe the update)"

**Validation:**
1. Verify agent exists in specified scope
   - Use Glob to find agent file: `{scope-path}/agents/{agent-name}.md`
   - If not found: Display error "Agent '{agent-name}' not found in {scope}" and abort
2. Verify update-description is clear and actionable (not empty)
3. Parse scope parameter (default: marketplace)

**Error handling:** If agent not found or parameters invalid, display clear error message and abort.

### Step 2: Load Agent Analysis Standards

**Activate diagnostic patterns:**
```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

**Read agent quality standards:**
```
Read: ~/git/cui-llm-rules/marketplace/bundles/cui-plugin-development-tools/standards/agent-quality-standards.md
Read: ~/git/cui-llm-rules/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/agent-design-principles.md
```

### Step 3: Read Current Agent

**Read the complete agent file:**
```
Read: {agent-path}
```

**Analyze current state:**
1. Note current structure, workflow, line count
2. Identify tool usage and coverage
3. Check existing CONTINUOUS IMPROVEMENT RULE section
4. Store baseline metrics: `current_lines`, `tools_used`, `workflow_steps`

**Track statistics:** Initialize counters for reporting.

### Step 4: Analyze Proposed Update

**Validate update soundness:**

1. **Applicability Check**
   - Does the update apply to this specific agent's purpose?
   - Is it relevant to the agent's workflow?
   - Does it solve a real problem or improve clarity/efficiency?

2. **Correctness Check**
   - Is the proposed change technically correct?
   - Does it align with agent design principles?
   - Does it follow anti-bloat rules?
   - Will it break existing agent logic?

3. **Tool Coverage Check**
   - If adding new tools: Are they in the agent's allowed tools list?
   - If changing workflow: Does tool usage remain appropriate?
   - Does update improve or maintain tool fit score?

4. **Specificity Check**
   - Is the update specific enough to implement?
   - Are there clear before/after examples?
   - Is the scope well-defined?

**Decision logic:**
- If update fails any check: Report why and prompt user to refine or abort
- If update passes all checks: Continue to Step 5

**Error handling:** If analysis is inconclusive, present findings to user and ask [C]ontinue/[R]efine/[A]bort.

### Step 5: Duplication Detection

**CRITICAL: Check for duplication across all agents**

**Scope of duplication check:**
1. **Within agent**: Is this improvement already present in the agent?
   - Check if similar content exists in any workflow step
   - Verify it's not just rewording existing logic

2. **Across marketplace agents**: Could this be extracted to a skill?
   - Use Glob to find all marketplace agents
   - Grep for similar patterns/workflows in other agents
   - If found in 3+ agents: Suggest extracting to skill instead

3. **In existing skills**: Is this already covered by a skill?
   - Check if update content overlaps with existing skills
   - If yes: Suggest referencing skill instead of adding content

**Duplication resolution:**
```
If duplication found:
  - Within agent: Consolidate with existing workflow steps
  - Across agents: Suggest creating/updating shared skill
  - In skills: Replace update with skill reference
```

**Track statistics:** `duplicates_found`, `skills_suggested`, `content_consolidated`

**Error handling:** If duplication check fails (files not readable), log warning and continue with update but flag in report.

### Step 6: Apply Update

**Determine update type:**

1. **CONTINUOUS IMPROVEMENT RULE update**
   - If updating CONTINUOUS IMPROVEMENT RULE section
   - Add new item to the list
   - Ensure proper formatting and numbering

2. **Workflow enhancement**
   - If adding/modifying workflow steps
   - Maintain step numbering and logical flow
   - Update related sections

3. **Tool addition/modification**
   - If adding new tool usage
   - Verify tool is in allowed tools list
   - Update tool usage section
   - Add appropriate error handling

4. **Error handling addition**
   - If adding error handling
   - Place in appropriate workflow step
   - Follow error handling patterns from standards

5. **General improvement**
   - Apply based on context
   - Maintain agent structure
   - Follow anti-bloat rules

**Apply the update:**
```
Use Edit tool to make targeted changes
- Preserve existing structure
- Maintain formatting consistency
- Keep line count minimal (anti-bloat)
- Verify tool usage remains coherent
```

**Track statistics:** `edits_made`, `lines_added`, `lines_removed`, `steps_modified`, `tools_added`

**Error handling:** If Edit fails, display error details and abort. Do not leave agent in partial state.

### Step 7: Verify Update Quality

**Post-update checks:**

1. **File integrity**
   - Verify file is still valid Markdown
   - Check frontmatter is intact (if present)
   - Ensure no syntax errors introduced

2. **Structure preservation**
   - All required sections still present
   - Workflow numbering is correct
   - Tool references are valid

3. **Tool coverage**
   - Calculate tool fit score
   - Verify no tool bloat (unnecessary tools)
   - Check all used tools are declared

4. **Metrics comparison**
   - Calculate new line count
   - Verify anti-bloat compliance (0 to -10% change preferred)
   - Check no unnecessary growth

**Track statistics:** `final_lines`, `line_change_pct`, `tool_fit_score`

### Step 8: Run Formal Diagnosis

**Execute diagnosis command (unless --skip-diagnosis):**

```
SlashCommand: /cui-plugin-development-tools:plugin-diagnose-agents agent-name={agent-name}
```

**Parse diagnosis results:**
1. Check overall quality score
2. Review tool coverage and fit
3. Note critical issues, warnings, suggestions
4. Compare to pre-update state (if available)

**Decision logic:**
- If diagnosis reveals CRITICAL issues introduced by update: Offer to revert or fix
- If diagnosis shows improvement: Report success
- If diagnosis shows degradation: Investigate why

**Error handling:** If diagnosis command fails, report warning but don't abort (update was still applied).

### Step 9: Update CONTINUOUS IMPROVEMENT RULE (Meta-Update)

**If this update itself reveals an improvement to the agent update process:**

Apply the CONTINUOUS IMPROVEMENT RULE to this command (`plugin-update-agent`):
```
Edit: plugin-update-agent.md
Add to CONTINUOUS IMPROVEMENT RULE section
```

This ensures the update command itself evolves.

### Step 10: Display Update Report

**Generate comprehensive report:**

```
==================================================
Agent Update Complete: {agent-name}
==================================================

Update Applied:
- Description: {update-description}
- Type: {update-type}
- Scope: {scope}

Changes Made:
- Lines added: {lines_added}
- Lines removed: {lines_removed}
- Net change: {line_change_pct}% (target: 0 to -10%)
- Workflow steps modified: {steps_modified}
- Tools added: {tools_added}

Duplication Check:
- Duplicates found: {duplicates_found}
- Within agent: {consolidated_count}
- Across agents: {cross_agent_duplicates}
- Skills suggested: {skills_suggested}

Quality Verification:
- Diagnosis status: {PASSED/FAILED/SKIPPED}
- Overall quality: {score}/100
- Tool fit score: {tool_fit}/100
- Critical issues: {count}
- Warnings: {count}
- Suggestions: {count}

{if diagnosis_passed}
✅ Update successfully applied and verified!
{endif}

{if diagnosis_failed}
⚠️ Update applied but quality issues detected:
{list critical issues}

Recommended actions:
- Review issues above
- Run /plugin-diagnose-agents {agent-name} for details
- Consider reverting or fixing issues
{endif}

{if skills_suggested}
💡 Suggestion: Consider extracting to skill
Content found in {count} agents could be centralized:
- {list agents with similar content}
- Suggested skill: {skill-name}
{endif}
```

## CRITICAL RULES

**Validation Rules:**
- **MUST verify** agent exists before attempting update
- **MUST check** update is applicable, correct, and specific
- **MUST scan** for duplication within agent and across marketplace
- **ALWAYS preserve** agent structure and workflow integrity
- **NEVER break** existing agent logic

**Update Rules:**
- **PREFER consolidation** over addition (anti-bloat)
- **PREFER skill references** over duplicating content
- **MAINTAIN structure** - don't reorganize without good reason
- **TARGET 0 to -10% line change** (reduce or maintain, don't grow)
- **PRESERVE CONTINUOUS IMPROVEMENT RULE** - never remove it
- **VERIFY tool coverage** - ensure tools used are appropriate

**Verification Rules:**
- **ALWAYS run** diagnosis after update (unless explicitly skipped)
- **REVIEW diagnosis results** before marking success
- **OFFER to revert** if critical issues introduced
- **TRACK metrics** for all updates (lines changed, tool fit, quality scores)

**Meta-Update Rule:**
- **APPLY CONTINUOUS IMPROVEMENT RULE** to this command when improvements discovered
- **DOCUMENT patterns** that emerge from updates
- **EVOLVE the process** based on learnings

## TOOL USAGE

- **Glob**: Discover agent location, scan for duplicates
- **Read**: Load agent file, read standards
- **Edit**: Apply targeted updates to agent
- **Grep**: Search for duplication patterns across agents
- **SlashCommand**: Run `/plugin-diagnose-agents` for verification
- **Skill**: Load diagnostic patterns and architecture standards

## STATISTICS TRACKING

Track throughout workflow:
- `current_lines`: Pre-update line count
- `final_lines`: Post-update line count
- `line_change_pct`: Percentage change
- `lines_added`: Lines added
- `lines_removed`: Lines removed
- `steps_modified`: Count of workflow steps changed
- `tools_added`: Count of new tools added
- `edits_made`: Number of Edit operations
- `duplicates_found`: Total duplicates detected
- `content_consolidated`: Duplicates merged within agent
- `cross_agent_duplicates`: Similar content in other agents
- `skills_suggested`: Skills recommended for extraction
- `diagnosis_passed`: Boolean - post-update diagnosis success
- `quality_score`: Final diagnosis quality score
- `tool_fit_score`: Tool coverage fit score
- `critical_issues`: Count of critical issues from diagnosis

## USAGE EXAMPLES

### Example 1: Add Error Handling

```bash
/plugin-update-agent \
  agent-name=pr-review-responder \
  update-description="Add error handling for gh command failures when fetching PR comments"
```

### Example 2: Update CONTINUOUS IMPROVEMENT RULE

```bash
/plugin-update-agent \
  agent-name=maven-project-builder \
  update-description="Add to CONTINUOUS IMPROVEMENT RULE: Better Maven wrapper detection patterns"
```

### Example 3: Improve Tool Usage

```bash
/plugin-update-agent \
  agent-name=task-executor \
  update-description="Replace Bash grep with Grep tool for non-prompting execution"
```

### Example 4: Global Agent Update

```bash
/plugin-update-agent \
  agent-name=custom-deployer \
  scope=global \
  update-description="Add deployment rollback logic on verification failure"
```

## RELATED

- `/plugin-diagnose-agents` - Formal agent verification
- `/plugin-create-agent` - Create new agents
- `/plugin-update-command` - Update commands (similar workflow)
- Agent design principles - Architecture standards
- Agent quality standards - Quality requirements
