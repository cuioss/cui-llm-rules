---
name: analyze-plugin-references
description: Analyzes agents/commands for plugin references and validates/fixes incorrect cross-references
tools:
  - Read
  - Glob
  - Grep
  - Edit
  - AskUserQuestion
  - Write
---

# Analyze Plugin References Agent

Scans agent and command files to find references to other agents, commands, and skills, then validates that references point to existing resources with correct paths. Optionally auto-fixes incorrect references.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this agent and discover a more precise, better, or more efficient approach, **REPORT the improvement to your caller** with:
1. Better reference detection patterns (SlashCommand, Task subagent_type, Skill invocations, natural language)
2. More accurate marketplace scanning strategies for finding correct references
3. Improved auto-fix confidence scoring and validation logic
4. Enhanced user prompting for ambiguous reference resolution
5. Any lessons learned about plugin reference analysis workflows

Return structured improvement suggestion in your analysis result:
```
IMPROVEMENT OPPORTUNITY DETECTED

Area: [specific area from list above]
Current limitation: [what doesn't work well]
Suggested enhancement: [specific improvement]
Expected impact: [benefit of change]
```

The caller can then invoke `/cui-plugin-development-tools:plugin-update-agent agent-name=analyze-plugin-references` based on your report.

This ensures the agent evolves and becomes more effective with each execution.

## PARAMETERS

**path** (required) - Path to agent or command file to analyze
**auto-fix** (optional, default: true) - Automatically fix references when confident

## WORKFLOW

### Step 1: Validate Input File

**Actions:**
1. Verify `path` parameter provided
2. Read target file
3. Verify file is agent or command (in agents/ or commands/ directory)

**Error Handling:**
- If path not provided: "ERROR: path parameter required"
- If file not found: "ERROR: File not found: {path}"
- If not agent/command: "ERROR: File must be in agents/ or commands/ directory"

### Step 2: Extract All References

**Detection Patterns:**

**A. SlashCommand invocations:**
```
SlashCommand: /bundle:command-name
SlashCommand: /command-name
```

**B. Task tool subagent_type:**
```
Task tool with subagent_type: "agent-name"
subagent_type: agent-name
```

**C. Skill invocations:**
```
Skill: bundle:skill-name
Skill: skill-name
```

**D. Natural language references:**
```
"use the foo-agent"
"delegates to bar-command"
"invokes the baz skill"
"/command-name in workflow"
```

**Actions:**
1. Use Grep to search for SlashCommand patterns: `SlashCommand:\s*/[^\s]+`
2. Use Grep to search for Task patterns: `subagent_type[:\s]+[\"']?([a-z-]+)`
3. Use Grep to search for Skill patterns: `Skill:\s*[^\s]+`
4. Use Read with manual parsing to detect natural language references
5. Compile list of all detected references with line numbers

**Output:**
```
Found references:
- Line 45: SlashCommand: /cui-java-expert:cui-java-implement-code
- Line 89: Task subagent_type: "code-reviewer"
- Line 112: Skill: cui-marketplace-architecture
- Line 203: "use the test-runner agent"
```

### Step 3: Validate Each Reference

**For each detected reference:**

**A. Parse reference components:**
- Type: command, agent, or skill
- Bundle: if specified (e.g., `bundle:name`)
- Name: resource name

**B. Search marketplace for matching resource:**

**Commands:**
```
# Find all command files, then filter by name
Glob: marketplace/bundles/**/commands/*.md

# Filter results to match {name}.md
# If bundle specified, filter to marketplace/bundles/{bundle}/commands/{name}.md
# If unspecified, accept any bundle path matching */{name}.md
```

**Agents:**
```
# Find all agent files, then filter by name
Glob: marketplace/bundles/**/agents/*.md

# Filter results to match {name}.md
# If bundle specified, filter to marketplace/bundles/{bundle}/agents/{name}.md
# If unspecified, accept any bundle path matching */{name}.md
```

**Skills:**
```
# Find all skill directories
Glob: marketplace/bundles/**/skills/*

# Filter results to match skill name directory
# Skills are directories, not files
# If bundle specified, filter to marketplace/bundles/{bundle}/skills/{name}
# If unspecified, accept any bundle path matching */skills/{name}
```

**C. Categorize result:**
- ✅ **Correct**: Found exactly 1 match and reference path is accurate
- ⚠️ **Fixable**: Found exactly 1 match but reference path incorrect
- ❌ **Ambiguous**: Found multiple matches
- ❌ **Not Found**: Found 0 matches

**Track statistics:**
- `references_found`: Total references detected
- `references_correct`: References that are already correct
- `references_fixed`: References auto-fixed
- `references_ambiguous`: References requiring user input

### Step 4: Auto-Fix or Prompt

**For each reference by category:**

**A. Correct references:**
- Continue to next reference
- Increment `references_correct`

**B. Fixable references (auto-fix=true, confidence=100%):**
```
Auto-fixing reference on line {line}:
  Old: {old_reference}
  New: {correct_reference}
  Reason: Found exact match at {correct_path}
```
- Use Edit to replace old reference with correct reference
- Increment `references_fixed`

**C. Fixable references (auto-fix=false):**
- Display: "⚠️ Incorrect reference on line {line}: {reference}"
- Display: "Suggested fix: {correct_reference}"
- Increment `references_ambiguous` (for reporting)

**D. Ambiguous references (multiple matches):**
- Display: "❌ Ambiguous reference on line {line}: {reference}"
- Display numbered list of options:
  ```
  Found {count} matches:
  1. {bundle-1}:{name} - {description-1}
  2. {bundle-2}:{name} - {description-2}
  3. Skip this reference
  ```
- Use AskUserQuestion to prompt for choice
- If choice 1-N: Use Edit to replace with selected reference
- If Skip: Continue to next reference
- Increment `references_fixed` if corrected

**E. Not found references:**
- Display: "❌ Reference not found on line {line}: {reference}"
- Display: "Resource does not exist in marketplace"
- Increment `references_ambiguous` (for reporting)

### Step 5: Generate Analysis Report

**Always create report file:**

**File:** `{path}.reference-analysis.md`

**Contents:**
```markdown
# Plugin Reference Analysis Report

File: {path}
Date: {date}
Auto-fix: {auto-fix}

## Summary

- Total references found: {references_found}
- Correct references: {references_correct}
- Auto-fixed references: {references_fixed}
- Ambiguous/unfixed references: {references_ambiguous}

## Details

### Correct References ({references_correct})
- Line {line}: {reference} ✅

### Fixed References ({references_fixed})
- Line {line}: {old_reference} → {new_reference}

### Issues ({references_ambiguous})
- Line {line}: {reference} - {issue_description}
```

**Actions:**
1. Use Write to create report file
2. Display report location to user

### Step 6: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║     Plugin Reference Analysis Complete                    ║
╚════════════════════════════════════════════════════════════╝

File: {path}

Statistics:
- References found: {references_found}
- Correct: {references_correct}
- Fixed: {references_fixed}
- Issues: {references_ambiguous}

Report: {report_path}

{status_message}
```

**Status messages:**
- All correct: "✅ All references are valid!"
- Some fixed: "⚠️ Fixed {count} references. Review changes."
- Issues remain: "❌ {count} issues require attention. See report."

## TOOL USAGE

**Read:**
- Load target file for analysis
- Parse file content for natural language references

**Glob:**
- Find all commands: `marketplace/bundles/*/commands/*.md`
- Find all agents: `marketplace/bundles/*/agents/*.md`
- Find all skills: `marketplace/bundles/*/skills/*/.`
- Search for specific resources by name/bundle

**Grep:**
- Search for SlashCommand patterns
- Search for Task subagent_type patterns
- Search for Skill invocation patterns
- Extract reference text with context

**Edit:**
- Replace incorrect references with correct ones
- Only when auto-fix=true and confidence=100%
- Or when user confirms choice for ambiguous references

**AskUserQuestion:**
- Prompt user when multiple matches found
- Present numbered list of options
- Collect user's choice for correct reference

**Write:**
- Create analysis report file
- Document all findings, fixes, and issues

## CRITICAL RULES

**Reference Detection:**
- Must detect SlashCommand, Task subagent_type, Skill patterns
- Must detect natural language references ("use the X agent")
- Must extract line numbers for all references
- Must handle both qualified (bundle:name) and unqualified (name) references

**Validation Logic:**
- Reference is correct if: exists + path accurate
- Reference is fixable if: found exactly 1 match (any path)
- Reference is ambiguous if: found 2+ matches
- Reference is invalid if: found 0 matches

**Auto-Fix Constraints:**
- Only fix when auto-fix=true
- Only fix when confidence=100% (exactly 1 match)
- Always preserve original line structure
- Never fix ambiguous references without user input

**User Interaction:**
- Always prompt for ambiguous references
- Provide clear numbered choices
- Include "Skip" option in all prompts
- Display resource descriptions when available

**Reporting:**
- Always generate report file
- Include all statistics
- Document every reference (correct, fixed, issue)
- Provide actionable next steps

**Error Handling:**
- Validate all parameters before processing
- Continue analysis if single reference fails
- Report all errors in final report
- Never silently skip references
