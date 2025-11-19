---
name: analyze-plugin-references
description: Analyzes agents/commands for plugin references and validates/fixes incorrect cross-references
tools:
  - Read
  - Grep
  - Edit
  - AskUserQuestion
  - Write
model: haiku
---

# Analyze Plugin References Agent

Scans agent and command files to find references to other agents, commands, and skills, then validates that references point to existing resources with correct paths. Optionally auto-fixes incorrect references.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this agent and discover a more precise, better, or more efficient approach, **REPORT the improvement to your caller** with:
1. Better reference detection patterns (SlashCommand, Task subagent_type, Skill invocations, natural language)
2. More accurate context verification to reduce false positives
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

The caller can then invoke `/plugin-update-agent agent-name=analyze-plugin-references update="[improvement]"` based on your report.

## PARAMETERS

**path** (required) - Path to agent or command file to analyze
**marketplace_inventory** (required) - JSON inventory from /plugin-inventory --json containing all marketplace bundles, agents, commands, and skills
**auto-fix** (optional, default: true) - Automatically fix references when confident

## WORKFLOW

### Step 1: Validate Input Parameters

**Actions:**
1. Verify `path` parameter provided
2. Verify `marketplace_inventory` parameter provided (JSON object with bundles array)
3. Read target file
4. Verify file is agent or command (in agents/ or commands/ directory)

**Error Handling:**
- If path not provided: "ERROR: path parameter required"
- If marketplace_inventory not provided: "ERROR: marketplace_inventory parameter required - pass JSON from /plugin-inventory --json"
- If marketplace_inventory invalid: "ERROR: marketplace_inventory must be JSON object with 'bundles' array"
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

**CRITICAL: Each detected reference MUST be validated against actual file content to prevent hallucination.**

1. **Use Grep to search for SlashCommand patterns:**
   ```
   Grep: pattern="SlashCommand:\s*/[^\s]+", output_mode="content", -n=true
   ```
   - Extract line number and matched text
   - **TAG as type: "SlashCommand"**
   - For each match: Read the specific line to verify exact text
   - Parse reference from verified line text (e.g., `/plugin-update-agent`)

2. **Use Grep to search for Task patterns:**
   ```
   Grep: pattern="subagent_type[:\s]+[\"']?([a-z:-]+)[\"']?", output_mode="content", -n=true
   ```
   - Extract line number and matched text
   - **TAG as type: "Task"**
   - For each match: Read the specific line to verify exact text
   - Parse reference from verified line text (e.g., `diagnose-skill` or `bundle:agent-name`)

3. **Use Grep to search for Skill patterns:**
   ```
   Grep: pattern="Skill:\s*[^\s]+", output_mode="content", -n=true
   ```
   - Extract line number and matched text
   - **TAG as type: "Skill"**
   - For each match: Read the specific line to verify exact text
   - Parse reference from verified line text (e.g., `cui-java-expert:cui-java-core`)

4. **Use Read with manual parsing to detect natural language references**
   - TAG as type: "Natural"

5. **Validation and Error Handling:**
   - For each Grep match:
     - Read the specific line using line number
     - Verify the pattern match actually appears in that line
     - If mismatch detected: Log error and skip reference
     - If format unexpected: Log error with actual vs expected format
   - Only include verified references in final list

6. **Compile list with explicit type tags and actual line text:**
   ```
   Found references:
   - Line 74: [Skill] Skill: cui-requirements:requirements-maintenance
     Actual text: "Skill: cui-requirements:requirements-maintenance"
   - Line 105: [SlashCommand] /java-implement-code
     Actual text: "SlashCommand: /java-implement-code"
   - Line 142: [Task] subagent_type: "cui-plugin-development-tools:diagnose-skill"
     Actual text: 'subagent_type: "cui-plugin-development-tools:diagnose-skill"'
   ```

**CRITICAL - Bundle Prefix Enforcement Rules (Architecture Rule 6):**

**For AGENTS (detected by path containing /agents/):**
- ❌ **Task invocations**: CRITICAL violation - agents CANNOT invoke other agents (Task tool unavailable at runtime)
- ❌ **SlashCommand invocations**: CRITICAL violation - agents CANNOT invoke commands (SlashCommand tool unavailable)
- ✅ **Skill invocations**: MUST use bundle prefix - Format: `Skill: bundle:skill-name`
  - Example: `Skill: cui-java-expert:cui-java-core` ✅
  - Invalid: `Skill: cui-java-core` ❌ (missing bundle prefix)

**For COMMANDS (detected by path containing /commands/):**
- ✅ **Task invocations**: MUST use bundle prefix - Format: `subagent_type: bundle:agent-name`
  - Example: `subagent_type: cui-plugin-development-tools:diagnose-skill` ✅
  - Invalid: `subagent_type: diagnose-skill` ❌ (missing bundle prefix)
- ✅ **Skill invocations**: MUST use bundle prefix - Format: `Skill: bundle:skill-name`
  - Example: `Skill: cui-java-expert:cui-java-core` ✅
  - Invalid: `Skill: cui-java-core` ❌ (missing bundle prefix)
- ✅ **SlashCommand invocations**: MUST NOT use bundle prefix - Format: `/command-name`
  - Example: `/plugin-update-agent` ✅
  - Invalid: `/cui-plugin-development-tools:plugin-update-agent` ❌ (unnecessary bundle prefix)

**For SKILLS (detected by path containing /skills/):**
- ✅ **Skill invocations**: MUST use bundle prefix - Format: `Skill: bundle:skill-name`
- ❌ **Task invocations**: CRITICAL violation - skills CANNOT invoke agents (breaks abstraction)
- ❌ **SlashCommand invocations**: CRITICAL violation - skills CANNOT invoke commands (breaks abstraction)

**Output:**
```
Found references:
- Line 45: [SlashCommand] /cui-java-expert:cui-java-implement-code
  Actual text: "SlashCommand: /cui-java-expert:cui-java-implement-code"
- Line 89: [Task] code-reviewer
  Actual text: 'subagent_type: "code-reviewer"'
- Line 112: [Skill] cui-marketplace-architecture
  Actual text: "Skill: cui-marketplace-architecture"
- Line 203: [Natural] "use the test-runner agent"
  Actual text: "use the test-runner agent"
```

### Step 2a: Verify Context to Eliminate False Positives

**CRITICAL:** Before validating references, verify each match is an actual runtime invocation, not documentation.

**For EACH reference found in Step 2:**

**Actions:**
1. **Read context around flagged line** (±2 lines before and after):
   ```
   Read: {path}, offset={line-2}, limit=5
   ```

2. **MANDATORY: Verify pattern actually exists in line content:**
   - Extract the actual line text from Read output
   - Check if the Grep pattern match ACTUALLY appears in the line text
   - If pattern does NOT appear in line: **DISCARD - Hallucination/Grep error**

   **Examples of pattern verification:**
   ```
   Grep matched line 104 with pattern "subagent_type"
   Read line 104: "- File B says 'prefer Y'"
   Verification: "subagent_type" NOT in line text → DISCARD as false positive

   Grep matched line 74 with pattern "Skill: cui-marketplace"
   Read line 74: "Skill: cui-marketplace-architecture"
   Verification: Pattern found → PROCEED to context check
   ```

3. **Check for false positive indicators:**

   **❌ FALSE POSITIVE - Documentation/Examples:**
   - Line in code block (preceded by ``` or heavy indentation)
   - Example pattern in documentation: `Grep: pattern="SlashCommand:..."`
   - Comment explaining format: `# Example: /plugin-update-agent`
   - CONTINUOUS IMPROVEMENT RULE instructions: "The caller can then invoke..."
   - Architecture rules documentation: "Pattern: subagent_type:"
   - Template/format specifications: `Line {line}: {reference}`
   - Lines starting with: `- **Example**:`, `- Pattern:`, `# Search for`, `## Examples`

   **✅ ACTUAL INVOCATION - Runtime Usage:**
   - In workflow steps: "Step 3: Use SlashCommand to invoke..."
   - In Task delegation: "Task:" followed by "subagent_type: bundle:agent"
   - In Skill activation: "Skill: bundle:skill-name" (not in examples section)
   - In direct execution instructions (not explaining patterns)

4. **Determine classification:**
   - If pattern not in line text: **DISCARD** immediately as Grep hallucination
   - If FALSE POSITIVE context: **Remove from references list**, log as "Filtered: Line {line} - Documentation/Example"
   - If ACTUAL INVOCATION: **Keep in references list** for validation

5. **Track statistics:**
   - `references_detected`: Raw Grep matches
   - `references_filtered`: False positives removed
   - `references_found`: Actual invocations (after filtering)

**Examples of False Positives to Filter:**

```
❌ Line 104: Grep matched "subagent_type" pattern
   Read line 104: "- File B says 'prefer Y'"
   Verification: Pattern NOT in line text
   Action: DISCARD - Grep hallucination/error

❌ Line 105: Grep: pattern="subagent_type[:\s]+[\"']?([a-z:-]+)[\"']?"
   Read line 105: "Grep: pattern=\"subagent_type...\""
   Verification: Pattern found in line
   Context check: Documentation showing Grep pattern syntax
   Action: FILTER - This is pattern documentation

❌ Line 204: # Example: /plugin-update-agent -> plugin-update-agent
   Verification: Pattern found in line
   Context check: Comment explaining reference format
   Action: FILTER - This is a comment example

❌ Line 363: The caller can then invoke `/plugin-update-agent agent-name=...`
   Verification: Pattern found in line
   Context check: CONTINUOUS IMPROVEMENT RULE explaining caller responsibility
   Action: FILTER - This is instruction documentation

❌ Line 189: - **Correct Pattern**: Commands SHOULD use... `/plugin-update-command`
   Verification: Pattern found in line
   Context check: Architecture rules explaining patterns
   Action: FILTER - This is pattern definition

✅ Line 74: Skill: cui-marketplace-architecture
   Verification: Pattern found in line
   Context check: Step 2: Load Analysis Standards
                  Skill: cui-marketplace-architecture
                  This loads all necessary agent analysis standards
   Action: KEEP - This is actual Skill invocation in workflow
```

**Output:**
```
Verification Results:
- References detected (raw Grep): {references_detected}
- References filtered (false positives): {references_filtered}
- References found (actual invocations): {references_found}

Verified references:
- Line 74: [Skill] cui-marketplace-architecture ✅
  Context: "Step 2: Load Analysis Standards"
- Line 112: [Skill] cui-java-core ✅
  Context: "Step 5: Validate patterns"

Filtered references (not actual invocations):
- Line 105: [Task] subagent_type pattern - Documentation/Example
- Line 204: [SlashCommand] /plugin-update-agent - Comment example
```

### Step 3: Validate Each Reference

**For each detected reference:**

**A. Parse reference components using type tag:**
- **Type tag**: [SlashCommand], [Task], [Skill], or [Natural] (from Step 2)
- **Reference text**: Actual verified text from file
- **Bundle**: if specified (e.g., `bundle:name`)
- **Name**: resource name

**CRITICAL: Use type tag to determine validation logic - prevents confusing Skill with SlashCommand.**

**B. Search marketplace inventory for matching resource:**

**Use pre-loaded marketplace_inventory JSON to find matches.**

**Commands (ONLY for type tag [SlashCommand]):**
```
# CRITICAL: Only process if type tag is [SlashCommand]
# Do NOT process [Skill] or [Task] references here

# Search inventory.bundles[].commands[] for matching name
# Parse reference to extract name without bundle prefix
# Example: /cui-plugin-development-tools:plugin-update-agent -> plugin-update-agent
# Example: /plugin-update-agent -> plugin-update-agent
# Search all bundles' commands (bundle prefix ignored for SlashCommand)
# Match on: command.name === {name}
# Return: command.path

# VALIDATION:
# If reference contains bundle prefix (e.g., /bundle:command):
#   - Mark as ⚠️ FIXABLE (unnecessary bundle prefix)
#   - Auto-fix removes prefix: /cui-plugin-development-tools:plugin-update-agent -> /plugin-update-agent
```

**Agents (ONLY for type tag [Task]):**
```
# CRITICAL: Only process if type tag is [Task]
# Do NOT process [Skill] or [SlashCommand] references here

# Parse reference to extract components:
#   - If contains ':' → bundle = before ':', name = after ':'
#   - If no ':' → bundle = null, name = entire reference
# Example: "cui-plugin-development-tools:diagnose-agent" → bundle="cui-plugin-development-tools", name="diagnose-agent"
# Example: "diagnose-skill" → bundle=null, name="diagnose-skill"

# Search inventory.bundles[].agents[] for matching name
# If bundle specified in reference: filter to that bundle's agents
# If unspecified: search all bundles' agents
# Match on: agent.name === {name}
# Return: agent.path, agent.bundle

# CRITICAL VALIDATION BASED ON FILE TYPE:

# If analyzing an AGENT file (/agents/ in path):
#   - Mark as ❌ CRITICAL (agents cannot invoke agents via Task tool)
#   - NO auto-fix - architectural violation requiring manual refactoring

# If analyzing a COMMAND file (/commands/ in path):
#   - Parse reference to extract bundle and name
#   - Find matching agent in inventory
#   - If bundle IS specified in reference:
#     - Check if bundle matches agent.bundle from inventory
#     - If matches: Mark as ✅ CORRECT
#     - If mismatch: Mark as ⚠️ FIXABLE (incorrect bundle prefix)
#       - Example fix: "wrong-bundle:diagnose-skill" → "cui-plugin-development-tools:diagnose-skill"
#   - If bundle NOT specified:
#     - Mark as ⚠️ FIXABLE (missing bundle prefix)
#     - Construct correct reference: {agent.bundle}:{agent.name}
#     - Example fix: "diagnose-skill" → "cui-plugin-development-tools:diagnose-skill"

# If analyzing a SKILL file (/skills/ in path):
#   - Mark as ❌ CRITICAL (skills cannot invoke agents via Task tool)
#   - NO auto-fix - architectural violation requiring manual refactoring
```

**Skills (ONLY for type tag [Skill]):**
```
# CRITICAL: Only process if type tag is [Skill]
# Do NOT process [Task] or [SlashCommand] references here

# Parse reference to extract components:
#   - If contains ':' → bundle = before ':', name = after ':'
#   - If no ':' → bundle = null, name = entire reference
# Example: "cui-java-expert:cui-java-core" → bundle="cui-java-expert", name="cui-java-core"
# Example: "cui-java-core" → bundle=null, name="cui-java-core"

# Search inventory.bundles[].skills[] for matching name
# If bundle specified in reference: filter to that bundle's skills
# If unspecified: search all bundles' skills
# Match on: skill.name === {name}
# Return: skill.path (directory path), skill.bundle

# VALIDATION:

# For ALL file types (agents, commands, skills):
#   - Parse reference to extract bundle and name
#   - Find matching skill in inventory
#   - If bundle IS specified in reference:
#     - Check if bundle matches skill.bundle from inventory
#     - If matches: Mark as ✅ CORRECT
#     - If mismatch: Mark as ⚠️ FIXABLE (incorrect bundle prefix)
#       - Example fix: "wrong-bundle:cui-java-core" → "cui-java-expert:cui-java-core"
#   - If bundle NOT specified:
#     - Mark as ⚠️ FIXABLE (missing bundle prefix)
#     - Construct correct reference: {skill.bundle}:{skill.name}
#     - Example fix: "cui-java-core" → "cui-java-expert:cui-java-core"
```

**Performance Note:** Using pre-loaded inventory eliminates 3 Glob operations per reference validation (commands, agents, skills). For files with 10+ references, this saves 30+ file system scans.

**C. Categorize result:**
- ✅ **Correct**: Found exactly 1 match and reference has proper bundle prefix (where required/prohibited)
- ⚠️ **Fixable - Missing Bundle Prefix**: Found exactly 1 match but missing required bundle prefix
  - Task invocations in commands: `diagnose-skill` → `cui-plugin-development-tools:diagnose-skill`
  - Skill invocations (all file types): `cui-java-core` → `cui-java-expert:cui-java-core`
- ⚠️ **Fixable - Unnecessary Bundle Prefix**: Found exactly 1 match but has unnecessary bundle prefix
  - SlashCommand invocations: `/cui-plugin-development-tools:plugin-update-agent` → `/plugin-update-agent`
- ⚠️ **Fixable - Incorrect Path**: Found exactly 1 match but reference path incorrect
- ❌ **CRITICAL - Architectural Violation**: Reference violates architecture rules
  - Agents using Task tool (cannot invoke other agents)
  - Agents using SlashCommand tool (cannot invoke commands)
  - Skills using Task tool (cannot invoke agents)
  - Skills using SlashCommand tool (cannot invoke commands)
- ❌ **Ambiguous**: Found multiple matches (requires user selection)
- ❌ **Not Found**: Found 0 matches (resource doesn't exist)

**Track statistics:**
- `references_detected`: Raw Grep matches (before verification)
- `references_filtered`: False positives removed in Step 2a
- `references_found`: Actual invocations (after filtering)
- `references_correct`: References that are already correct
- `references_fixed`: References auto-fixed
- `references_critical`: Architectural violations detected
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

**C. Architectural violation references:**
- Display: "❌ CRITICAL - Architectural violation on line {line}: {reference}"
- Display: "{file_type} cannot use {tool_type} tool - violates Architecture Rule 6"
- Display: "Required action: Manual refactoring needed"
- Increment `references_critical`
- Add to critical violations section in report
- NO auto-fix - these require manual architectural refactoring

**D. Fixable references (auto-fix=false):**
- Display: "⚠️ Incorrect reference on line {line}: {reference}"
- Display: "Suggested fix: {correct_reference}"
- Increment `references_ambiguous` (for reporting)

**E. Ambiguous references (multiple matches):**
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

**F. Not found references:**
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

- Raw references detected: {references_detected}
- False positives filtered: {references_filtered}
- Actual references found: {references_found}
- Correct references: {references_correct}
- Auto-fixed references: {references_fixed}
- Critical architectural violations: {references_critical}
- Ambiguous/unfixed references: {references_ambiguous}

## Details

### Filtered False Positives ({references_filtered})
Documentation/examples excluded from analysis:
- Line {line}: {pattern} - {reason}
  Context: {surrounding_text}

### Correct References ({references_correct})
- Line {line}: {reference} ✅

### Fixed References ({references_fixed})
- Line {line}: {old_reference} → {new_reference}

### Critical Architectural Violations ({references_critical})
- Line {line}: {reference} - ❌ CRITICAL
  - Violation: {file_type} cannot use {tool_type} tool
  - Reason: Violates Architecture Rule 6 - {explanation}
  - Action Required: Manual refactoring needed

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
- Critical violations: {references_critical}
- Issues: {references_ambiguous}

Report: {report_path}

{status_message}
```

**Status messages:**
- All correct: "✅ All references are valid!"
- Critical violations: "❌ CRITICAL: {count} architectural violations require manual refactoring!"
- Some fixed: "⚠️ Fixed {count} references. Review changes."
- Issues remain: "❌ {count} issues require attention. See report."

## TOOL USAGE

**Read:**
- Load target file for analysis
- Parse file content for natural language references

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

**Glob:** ~~REMOVED~~ - No longer needed. Marketplace inventory is provided as parameter.

## CRITICAL RULES

**Reference Detection:**
- Must detect SlashCommand, Task subagent_type, Skill patterns
- Must detect natural language references ("use the X agent")
- Must extract line numbers for all references
- Must handle both qualified (bundle:name) and unqualified (name) references
- **MUST verify context to eliminate false positives** (Step 2a)
- **MUST distinguish runtime invocations from documentation/examples**

**Validation Logic:**
- Reference is correct if: exists + path accurate + proper bundle prefix (where required)
- Reference is fixable if: found exactly 1 match AND no architectural violation
- Reference is critical if: architectural violation (agent using Task/SlashCommand, skill using Task/SlashCommand)
- Reference is ambiguous if: found 2+ matches
- Reference is invalid if: found 0 matches

**Bundle Prefix Requirements:**
- Task invocations in commands: REQUIRED (add if missing)
- Skill invocations in all file types: REQUIRED (add if missing)
- SlashCommand invocations: PROHIBITED (remove if present)

**Auto-Fix Constraints:**
- Only fix when auto-fix=true
- Only fix when confidence=100% (exactly 1 match)
- NEVER fix architectural violations (require manual refactoring)
- Always preserve original line structure
- Never fix ambiguous references without user input

**User Interaction:**
- Always prompt for ambiguous references
- Provide clear numbered choices
- Include "Skip" option in all prompts
- Display resource descriptions when available

**Reporting:**
- Always generate report file
- Include all statistics (including critical violations count)
- Document every reference (correct, fixed, critical, issue)
- Prioritize critical architectural violations at top of report
- Provide actionable next steps

**Error Handling:**
- Validate all parameters before processing
- Continue analysis if single reference fails
- Report all errors in final report
- Never silently skip references
