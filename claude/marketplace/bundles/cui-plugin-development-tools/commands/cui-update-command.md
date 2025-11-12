---
name: cui-update-command
description: Update a command with improvements, verify quality, and prevent duplication
---

# Update Command

Updates an existing slash command with proposed improvements while ensuring quality, correctness, and preventing duplication.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-update-command update="[your improvement]"` with:
1. Improved validation patterns for proposed updates
2. Better methods for detecting duplication across commands
3. More effective strategies for ensuring update correctness
4. Enhanced quality verification techniques
5. Any lessons learned about command evolution and maintenance

This ensures the command evolves and becomes more effective with each execution.

## PURPOSE

When you need to update an existing command based on lessons learned or improvements discovered, this command:

1. Validates the proposed update is sound and applicable
2. Checks for duplication with existing command content and other commands
3. Applies the update using appropriate tools
4. Runs formal verification via `/cui-diagnose-commands`
5. Reports results and any issues found

## PARAMETERS

**Required Parameters** (will prompt if missing):

- **command-name**: Name of command to update (e.g., `cui-add-skill-knowledge`)
- **update-description**: Description of what to update and why

**Optional Parameters**:

- **scope**: Where to find command - `marketplace` (default), `global`, `project`
- **--skip-diagnosis**: Skip post-update diagnosis (not recommended)

## WORKFLOW

### Step 1: Validate Input Parameters

**Prompt for missing parameters:**
- `command-name`: "Which command should be updated? (provide command name)"
- `update-description`: "What improvement should be applied? (describe the update)"

**Validation:**
1. Verify command exists in specified scope
   - Use Glob to find command file: `{scope-path}/commands/{command-name}.md`
   - If not found: Display error "Command '{command-name}' not found in {scope}" and abort
2. Verify update-description is clear and actionable (not empty)
3. Parse scope parameter (default: marketplace)

**Error handling:** If command not found or parameters invalid, display clear error message and abort.

### Step 2: Load Command Analysis Standards

**Activate diagnostic patterns:**
```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

**Read command quality standards:**
```
Read: ~/git/cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/standards/command-quality-standards.md
Read: ~/git/cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/standards/command-analysis-patterns.md
```

### Step 3: Read Current Command

**Read the complete command file:**
```
Read: {command-path}
```

**Analyze current state:**
1. Note current structure, sections, line count
2. Identify existing CONTINUOUS IMPROVEMENT RULE section
3. Check for YAML frontmatter validity
4. Store baseline metrics: `current_lines`, `current_sections`

**Track statistics:** Initialize counters for reporting.

### Step 4: Analyze Proposed Update

**Validate update soundness:**

1. **Applicability Check**
   - Does the update apply to this specific command's purpose?
   - Is it relevant to the command's workflow?
   - Does it solve a real problem or improve clarity/efficiency?

2. **Correctness Check**
   - Is the proposed change technically correct?
   - Does it align with command quality standards?
   - Does it follow anti-bloat rules?
   - Will it break existing functionality?

3. **Specificity Check**
   - Is the update specific enough to implement?
   - Are there clear before/after examples?
   - Is the scope well-defined?

**Decision logic:**
- If update fails any check: Report why and prompt user to refine or abort
- If update passes all checks: Continue to Step 5

**Error handling:** If analysis is inconclusive, present findings to user and ask [C]ontinue/[R]efine/[A]bort.

### Step 5: Duplication Detection

**CRITICAL: Check for duplication across all commands**

**Scope of duplication check:**
1. **Within command**: Is this improvement already present in the command?
   - Check if similar content exists in any section
   - Verify it's not just rewording existing content

2. **Across marketplace commands**: Could this be extracted to a skill?
   - Use Glob to find all marketplace commands
   - Grep for similar patterns/content in other commands
   - If found in 3+ commands: Suggest extracting to skill instead

3. **In existing skills**: Is this already covered by a skill?
   - Check if update content overlaps with existing skills
   - If yes: Suggest referencing skill instead of adding content

**Duplication resolution:**
```
If duplication found:
  - Within command: Consolidate with existing content
  - Across commands: Suggest creating/updating shared skill
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
   - Maintain step numbering
   - Update related sections (CRITICAL RULES, etc.)

3. **Error handling addition**
   - If adding error handling
   - Place in appropriate workflow step
   - Follow error handling patterns from standards

4. **Parameter addition**
   - If adding new parameter
   - Update PARAMETERS section
   - Add validation in workflow
   - Update examples

5. **General improvement**
   - Apply based on context
   - Maintain command structure
   - Follow anti-bloat rules

**Apply the update:**
```
Use Edit tool to make targeted changes
- Preserve existing structure
- Maintain formatting consistency
- Keep line count minimal (anti-bloat)
```

**Track statistics:** `edits_made`, `lines_added`, `lines_removed`, `sections_modified`

**Error handling:** If Edit fails, display error details and abort. Do not leave command in partial state.

### Step 7: Verify Update Quality

**Post-update checks:**

1. **File integrity**
   - Verify file is still valid Markdown
   - Check YAML frontmatter is intact
   - Ensure no syntax errors introduced

2. **Structure preservation**
   - All required sections still present
   - Workflow numbering is correct
   - Cross-references are valid

3. **Metrics comparison**
   - Calculate new line count
   - Verify anti-bloat compliance (0 to -10% change preferred)
   - Check no unnecessary growth

**Track statistics:** `final_lines`, `line_change_pct`

### Step 8: Run Formal Diagnosis

**Execute diagnosis command (unless --skip-diagnosis):**

```
SlashCommand: /cui-diagnose-commands command-name={command-name}
```

**Parse diagnosis results:**
1. Check overall quality score
2. Review critical issues
3. Note warnings and suggestions
4. Compare to pre-update state (if available)

**Decision logic:**
- If diagnosis reveals CRITICAL issues introduced by update: Offer to revert or fix
- If diagnosis shows improvement: Report success
- If diagnosis shows degradation: Investigate why

**Error handling:** If diagnosis command fails, report warning but don't abort (update was still applied).

### Step 9: Update CONTINUOUS IMPROVEMENT RULE (Meta-Update)

**If this update itself reveals an improvement to the update process:**

Apply the CONTINUOUS IMPROVEMENT RULE to this command (`cui-update-command`):
```
Edit: cui-update-command.md
Add to CONTINUOUS IMPROVEMENT RULE section
```

This ensures the update command itself evolves.

### Step 10: Display Update Report

**Generate comprehensive report:**

```
==================================================
Command Update Complete: {command-name}
==================================================

Update Applied:
- Description: {update-description}
- Type: {update-type}
- Scope: {scope}

Changes Made:
- Lines added: {lines_added}
- Lines removed: {lines_removed}
- Net change: {line_change_pct}% ({target: 0 to -10%})
- Sections modified: {sections_modified}

Duplication Check:
- Duplicates found: {duplicates_found}
- Within command: {consolidated_count}
- Across commands: {cross_command_duplicates}
- Skills suggested: {skills_suggested}

Quality Verification:
- Diagnosis status: {PASSED/FAILED/SKIPPED}
- Overall quality: {score}/100
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
- Run /cui-diagnose-commands {command-name} for details
- Consider reverting or fixing issues
{endif}

{if skills_suggested}
💡 Suggestion: Consider extracting to skill
Content found in {count} commands could be centralized:
- {list commands with similar content}
- Suggested skill: {skill-name}
{endif}
```

## CRITICAL RULES

**Validation Rules:**
- **MUST verify** command exists before attempting update
- **MUST check** update is applicable, correct, and specific
- **MUST scan** for duplication within command and across marketplace
- **ALWAYS preserve** YAML frontmatter and required sections
- **NEVER break** existing workflow logic

**Update Rules:**
- **PREFER consolidation** over addition (anti-bloat)
- **PREFER skill references** over duplicating content
- **MAINTAIN structure** - don't reorganize without good reason
- **TARGET 0 to -10% line change** (reduce or maintain, don't grow)
- **PRESERVE CONTINUOUS IMPROVEMENT RULE** - never remove it

**Verification Rules:**
- **ALWAYS run** diagnosis after update (unless explicitly skipped)
- **REVIEW diagnosis results** before marking success
- **OFFER to revert** if critical issues introduced
- **TRACK metrics** for all updates (lines changed, quality scores)

**Meta-Update Rule:**
- **APPLY CONTINUOUS IMPROVEMENT RULE** to this command when improvements discovered
- **DOCUMENT patterns** that emerge from updates
- **EVOLVE the process** based on learnings

## TOOL USAGE

- **Glob**: Discover command location, scan for duplicates
- **Read**: Load command file, read standards
- **Edit**: Apply targeted updates to command
- **Grep**: Search for duplication patterns across commands
- **SlashCommand**: Run `/cui-diagnose-commands` for verification
- **Skill**: Load diagnostic patterns and architecture standards

## STATISTICS TRACKING

Track throughout workflow:
- `current_lines`: Pre-update line count
- `final_lines`: Post-update line count
- `line_change_pct`: Percentage change
- `lines_added`: Lines added
- `lines_removed`: Lines removed
- `sections_modified`: Count of sections changed
- `edits_made`: Number of Edit operations
- `duplicates_found`: Total duplicates detected
- `content_consolidated`: Duplicates merged within command
- `cross_command_duplicates`: Similar content in other commands
- `skills_suggested`: Skills recommended for extraction
- `diagnosis_passed`: Boolean - post-update diagnosis success
- `quality_score`: Final diagnosis quality score
- `critical_issues`: Count of critical issues from diagnosis

## USAGE EXAMPLES

### Example 1: Add Error Handling

```bash
/cui-update-command \
  command-name=cui-add-skill-knowledge \
  update-description="Add error handling for marketplace path detection failure in Step 5"
```

### Example 2: Update CONTINUOUS IMPROVEMENT RULE

```bash
/cui-update-command \
  command-name=cui-create-bundle \
  update-description="Add to CONTINUOUS IMPROVEMENT RULE: Better validation for bundle directory structure"
```

### Example 3: Consolidate Duplicate Content

```bash
/cui-update-command \
  command-name=cui-setup-project-permissions \
  update-description="Remove duplicate permission validation logic (already in permission-management skill)"
```

### Example 4: Global Command Update

```bash
/cui-update-command \
  command-name=custom-deploy \
  scope=global \
  update-description="Add deployment verification step after push"
```

## RELATED

- `/cui-diagnose-commands` - Formal command verification
- `/cui-create-command` - Create new commands
- `/cui-update-agent` - Update agents (similar workflow)
- Anti-bloat rules - Prevent command growth
- Command quality standards - Quality requirements
