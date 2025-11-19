# TODO: Reduce False Positives in Reference Validation

## Priority: HIGH

## Problem Statement

The `analyze-plugin-references` agent currently generates significant false positives when validating plugin references in Markdown command files. During diagnosis of the cui-plugin-development-tools bundle (13 commands), agents reported filtering ~38 false positives from Markdown workflow documentation patterns.

**Impact**:
- Wastes computational resources on unnecessary context verification
- Increases token usage by ~30+ verification operations per file
- Slows down reference validation workflow
- Reported by 7 out of 13 reference validation agents as top improvement opportunity

## Affected Files

**Bundle**: `marketplace/bundles/cui-plugin-development-tools/commands/`

### High False Positive Rate (100% of matches were false positives):
- `plugin-create-agent.md` - 7 false positives filtered
- `plugin-create-skill.md` - 8 false positives filtered
- `plugin-diagnose-metadata.md` - 5 false positives filtered
- `plugin-diagnose-skills.md` - 6 false positives filtered
- `plugin-update-agent.md` - 7 false positives filtered
- `plugin-update-command.md` - 8 false positives filtered

### Mixed Results (some false positives, some true issues):
- `plugin-create-bundle.md` - 1 false positive filtered
- `plugin-create-command.md` - 2 true issues found (no false positives)
- `plugin-add-skill-knowledge.md` - 1 true issue found (no false positives)
- `plugin-diagnose-agents.md` - 7 true issues found (no false positives)
- `plugin-diagnose-commands.md` - 4 true issues found (no false positives)
- `plugin-maintain-readme.md` - 1 true issue found (no false positives)
- `plugin-update-command.md` - 1 true issue found (mixed with false positives)

**Total**: ~38 false positives across 13 command files in cui-plugin-development-tools bundle alone.

**Scope**: This issue affects ALL marketplace command files with Markdown workflow documentation patterns. The problem will recur across all 8 bundles (45 commands total) during reference validation.

## Current Limitation

The agent uses Grep to find potential plugin references (Task:, SlashCommand:, Skill:), but Markdown workflow documentation frequently contains these patterns in non-invocation contexts:

**Common False Positive Patterns:**
```markdown
## Step 3: Invoke Agent
- **Action**: Task: subagent_type="diagnose-command"
- **Tool**: SlashCommand: /plugin-diagnose-agents
- **Purpose**: Skill: cui-marketplace-architecture
```

These are documentation examples, not actual runtime invocations, but currently trigger Grep matches requiring manual context verification.

## Proposed Solution

Add pre-filtering logic to `analyze-plugin-references` agent to exclude Markdown workflow documentation patterns BEFORE detailed context verification:

### Filter Rules:
1. **Skip Markdown workflow steps**: Lines under headers matching `## Step N:` or `### Step N:`
2. **Skip Markdown list labels**: Lines with bold labels: `- **Action**:`, `- **Tool**:`, `- **Purpose**:`, `- **Parameters**:`
3. **Skip indented pseudo-YAML**: Indented YAML-like content under "Task:" in .md files (not actual YAML frontmatter)
4. **Skip code blocks**: Lines within triple-backtick code fences
5. **Skip example sections**: Lines under headers containing "Example", "Usage", "Demonstration"

### Implementation Strategy:
- Add pre-filtering step BEFORE Grep invocation
- Use Read tool to identify documentation sections
- Build exclusion line ranges
- Apply Grep with line filters
- Only perform detailed context verification on remaining matches

## Expected Impact

- **False positive reduction**: ~80% reduction in Markdown command files
- **Performance improvement**: Save 30+ context verification operations per file
- **Token savings**: Reduce token usage by ~40% for reference validation step
- **Accuracy improvement**: Higher signal-to-noise ratio in detected issues

## Files to Modify

### Primary Target:
- `marketplace/bundles/cui-plugin-development-tools/agents/analyze-plugin-references.md`
  - Add "Step 1.5: Pre-filter Markdown Documentation Patterns" before Grep invocation
  - Update reference detection workflow to apply exclusion rules
  - Document new filter patterns in agent description

### Testing Scope:
Validate against commands that previously generated false positives:
- `plugin-create-agent.md` (all 7 matches were false positives)
- `plugin-create-skill.md` (all 8 matches were false positives)
- `plugin-diagnose-skills.md` (all 6 matches were false positives)
- `plugin-update-agent.md` (all 7 matches were false positives)
- `plugin-update-command.md` (all 8 matches were false positives)

## Implementation Steps

1. ✅ **Read analyze-plugin-references agent** to understand current detection logic
2. ✅ **Design pre-filter algorithm** for Markdown documentation patterns
3. ✅ **Update agent workflow** to add pre-filtering step (Step 1.5) before Grep
4. ✅ **Update Step 2** to integrate pre-filter exclusions
5. ✅ **Update Step 2a** to acknowledge pre-filtering already applied
6. ✅ **Update statistics tracking** to include pre-filter metrics
7. ✅ **Update report generation** to show pre-filter performance
8. ✅ **Update agent description** to document new filtering capability
9. ⏳ **Test against known false positives** - Deferred (requires full workflow execution)
10. ⏳ **Verify no true positives filtered** - Deferred (requires full workflow execution)

## Implementation Complete

**Date**: 2025-01-19
**Changes**: Added Step 1.5 to analyze-plugin-references.md

**Pre-Filter Patterns Implemented:**
1. Example/Usage/Demonstration sections (## Example, ## Usage headers)
2. Workflow step Markdown documentation (## Step N: with `- **Label**:` format)
3. Markdown bold label lines (`- **Action**: ...`, `- **Tool**: ...`, `- **Purpose**: ...`)
4. Pseudo-YAML documentation (standalone `Task:`/`Agent:`/`Command:` with indented fields in .md files)
5. CONTINUOUS IMPROVEMENT RULE instructions (caller invocation documentation)

**Key Design Decisions:**
- **Conservative approach**: Did NOT filter all code blocks, as code blocks can contain actual YAML/JSON config
- **Targeted patterns**: Only filters clearly-documented patterns that cannot be actual invocations
- **Two-stage filtering**: Pre-filter (Step 1.5) + Context verification (Step 2a) for comprehensive coverage
- **Statistics tracking**: Added metrics to measure pre-filter effectiveness

**Files Modified:**
- `marketplace/bundles/cui-plugin-development-tools/agents/analyze-plugin-references.md` (+112 lines, -12 lines)

## Acceptance Criteria

- [x] Pre-filtering logic implemented in analyze-plugin-references.md
- [ ] False positive rate reduced by ≥80% on test commands (requires full workflow test)
- [ ] No true positives incorrectly filtered (requires full workflow test)
- [ ] Token usage for reference validation reduced by ~40% (requires full workflow test)
- [x] Agent description updated to document filtering
- [ ] Tested on all cui-plugin-development-tools commands (13 total) - **Next Step**

## Related Issues

- **Agent Bug**: Edit tool calls from analyze-plugin-references not actually modifying files (separate issue)
- **Reference Validation**: 20 detected issues across cui-plugin-development-tools bundle need manual fixing after agent bug resolved

## Notes

This improvement was consistently reported by multiple agents during the `/plugin-diagnose-commands` execution. The pattern recognition is solid - the agents correctly identified these as false positives through context verification, but pre-filtering would eliminate the need for that verification in the first place.
