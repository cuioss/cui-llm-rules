---
name: analyze-plugin-references
description: Analyzes agents/commands for plugin references and validates/fixes incorrect cross-references with 80% false positive reduction via Markdown pre-filtering
tools:
  - Read
  - Grep
  - Edit
  - AskUserQuestion
  - Write
model: sonnet
---

# Analyze Plugin References Agent

Scans agent and command files to find references to other agents, commands, and skills, then validates that references point to existing resources with correct paths. Optionally auto-fixes incorrect references.

**Key Feature:** Pre-filters Markdown documentation patterns (workflow steps, examples, code blocks) BEFORE Grep execution, reducing false positive rate by ~80% and improving performance by eliminating unnecessary context verification operations.

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
**marketplace_inventory** (required) - JSON inventory from cui-plugin-development-tools:plugin-inventory-scanner agent containing all marketplace bundles, agents, commands, and skills
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
- If marketplace_inventory not provided: "ERROR: marketplace_inventory parameter required - pass JSON from cui-plugin-development-tools:plugin-inventory-scanner agent"
- If marketplace_inventory invalid: "ERROR: marketplace_inventory must be JSON object with 'bundles' array"
- If file not found: "ERROR: File not found: {path}"
- If not agent/command: "ERROR: File must be in agents/ or commands/ directory"

### Step 1.5: Pre-filter Markdown Documentation Patterns

**CRITICAL:** Pre-filter documentation sections BEFORE running Grep to reduce false positive rate by ~80%.

**Goal:** Identify line numbers in Markdown documentation sections and exclude them from reference detection.

**Actions:**

1. **Parse file content to identify documentation patterns:**
   - Read file content (already loaded in Step 1)
   - Process line-by-line to build exclusion set

2. **Track Example/Usage sections (high priority):**
   ```
   - If line matches: ^#{2,3}\s+(Example|Usage|Demonstration) → set in_example = true
   - While in example section → add all lines to excluded_lines
   - If new header at same/higher level → set in_example = false
   ```

3. **Track workflow step Markdown documentation patterns:**
   ```
   - If line matches pattern: ^#{2,3}\s+Step\s+\d+: → set in_workflow_step = true
   - While in workflow step:
     - If line matches: ^\s*-\s+\*\*[^*]+\*\*: → add to excluded_lines
   - If new header at same/higher level → set in_workflow_step = false
   ```

4. **Track pseudo-YAML documentation in .md files:**
   ```
   - If line is exactly "Task:" or "Agent:" or "Command:" (standalone labels)
   - Check next lines: if indented (starts with spaces/tabs)
   - Add indented lines to excluded_lines (these are documentation, not YAML config)
   - Stop when non-indented line encountered
   ```

5. **Track CONTINUOUS IMPROVEMENT RULE instructions:**
   ```
   - If line contains "caller can then invoke" or "invoke `/plugin-update"
   - Add to excluded_lines (these are instructions, not actual invocations)
   ```

**Output:**
```
Pre-filter analysis:
- Total lines in file: {total_lines}
- Documentation lines excluded: {excluded_count}
- Searchable lines remaining: {total_lines - excluded_count}
- Exclusion rate: {(excluded_count/total_lines)*100}%
```

**Store exclusion set:** `excluded_lines` (set of line numbers to skip during Grep result processing)

**Performance Impact:**
- Before: Grep finds 38 matches → 38 context verifications → 38 filtered as false positives
- After: Pre-filter excludes ~80% of documentation → Grep finds ~8 matches → 8 context verifications → ~0-2 false positives

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
   - **FILTER:** Skip matches where line_number is in excluded_lines (from Step 1.5)
   - **TAG as type: "SlashCommand"**
   - For each match: Read the specific line to verify exact text
   - Parse reference from verified line text (e.g., `/plugin-update-agent`)

2. **Use Grep to search for Task patterns:**
   ```
   Grep: pattern="subagent_type[:\s]+[\"']?([a-z:-]+)[\"']?", output_mode="content", -n=true
   ```
   - Extract line number and matched text
   - **FILTER:** Skip matches where line_number is in excluded_lines (from Step 1.5)
   - **TAG as type: "Task"**
   - For each match: Read the specific line to verify exact text
   - Parse reference from verified line text (e.g., `diagnose-skill` or `bundle:agent-name`)

3. **Use Grep to search for Skill patterns:**
   ```
   Grep: pattern="Skill:\s*[^\s]+", output_mode="content", -n=true
   ```
   - Extract line number and matched text
   - **FILTER:** Skip matches where line_number is in excluded_lines (from Step 1.5)
   - **TAG as type: "Skill"**
   - For each match: Read the specific line to verify exact text
   - Parse reference from verified line text (e.g., `cui-java-expert:cui-java-core`)

4. **Use Read with manual parsing to detect natural language references**
   - TAG as type: "Natural"
   - Apply same exclusion filtering using excluded_lines

5. **Track pre-filter effectiveness:**
   - `grep_matches_raw`: Total Grep matches before filtering
   - `grep_matches_prefiltered`: Matches excluded by Step 1.5 pre-filter
   - `grep_matches_remaining`: Matches after pre-filter (passed to validation)

6. **Validation and Error Handling:**
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

### Step 2a: Verify Context to Eliminate Remaining False Positives

**CRITICAL:** Pre-filtering (Step 1.5) eliminates ~80% of false positives. This step handles remaining edge cases.

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
   - **Markdown workflow documentation patterns:**
     * Markdown list with bold labels: `- **Action**: Skill:...`, `- **Skill**: Skill:...`, `- **Purpose**:...`, `- **Reason**:...`
     * Workflow step headers: `Step N: Load Standards` followed by `- **label**: value` lists
     * Markdown pseudo-YAML: `Task:` followed by indented fields in .md files (not actual YAML)
     * Documentation fields: Lines with `Description:`, `Parameters:`, `Purpose:` under `Task:` in .md files
   - **File format context:**
     * .md (Markdown) files: References in workflow documentation sections are descriptions, not invocations
     * .md files without code blocks (```yaml```, ```json```): Plain text references are documentation

   **✅ ACTUAL INVOCATION - Runtime Usage:**
   - In .yaml or .json configuration files: All references are actual invocations
   - In .md files within code blocks: References in ```yaml``` or ```json``` blocks are actual code
   - In workflow steps with execution context: "Execute:" or "Run:" followed by actual tool invocation
   - In direct execution instructions (not explaining patterns or documenting structure)

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

❌ Line 23: - **Action**: Skill: cui-marketplace-architecture
   Verification: Pattern found in line
   Context check: Markdown list under "Step 2: Load Analysis Standards"
                  Format: "- **{label}**: {value}" (Markdown documentation list)
   File format: .md (Markdown command definition file)
   Action: FILTER - This is Markdown workflow documentation, not actual invocation

❌ Line 31: Task:\n  subagent_type: "plugin-diagnose-agents"
   Verification: Pattern found in line
   Context check: Indented under "Task:" label in Markdown workflow section
                  Format: Markdown pseudo-YAML describing task structure
   File format: .md (Markdown), not .yaml (actual configuration)
   Action: FILTER - This is Markdown workflow description, not actual YAML

✅ Line 74: Skill: cui-marketplace-architecture
   Verification: Pattern found in line
   Context check: Direct Skill invocation in workflow execution step
   File format: .yaml or in ```yaml``` code block
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
- `grep_matches_raw`: Total Grep matches before pre-filtering (Step 2)
- `grep_matches_prefiltered`: Matches excluded by Step 1.5 pre-filter
- `grep_matches_remaining`: Matches after pre-filter (Step 2)
- `references_filtered`: Additional false positives removed in Step 2a context verification
- `references_found`: Actual invocations (after all filtering)
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

### Pre-Filter Performance (Step 1.5)
- Total file lines: {total_lines}
- Documentation lines excluded: {excluded_count}
- Exclusion rate: {(excluded_count/total_lines)*100}%

### Reference Detection
- Raw Grep matches: {grep_matches_raw}
- Pre-filtered by Step 1.5: {grep_matches_prefiltered} ({prefilter_rate}%)
- Remaining after pre-filter: {grep_matches_remaining}
- Additional false positives filtered (Step 2a): {references_filtered}
- Actual references found: {references_found}

### Validation Results
- Correct references: {references_correct}
- Auto-fixed references: {references_fixed}
- Critical architectural violations: {references_critical}
- Ambiguous/unfixed references: {references_ambiguous}

## Details

### Pre-Filtered Documentation Lines (Step 1.5)
Excluded {grep_matches_prefiltered} potential matches in:
- Example/usage/demonstration sections (## Example, ## Usage)
- Workflow step Markdown patterns (## Step N: with - **Label**: format)
- Markdown bold label lines (- **Action**: ..., - **Tool**: ..., - **Purpose**: ...)
- Pseudo-YAML documentation (standalone Task:/Agent:/Command: with indented fields)
- CONTINUOUS IMPROVEMENT RULE instructions (caller invocation instructions)

### Additional False Positives (Step 2a - Context Verification)
{references_filtered} matches required detailed context verification:
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

Pre-Filter Performance:
- Documentation lines excluded: {excluded_count}/{total_lines} ({exclusion_rate}%)
- Pre-filtered false positives: {grep_matches_prefiltered}
- Context-verified false positives: {references_filtered}
- Total false positives eliminated: {grep_matches_prefiltered + references_filtered}

Validation Results:
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
