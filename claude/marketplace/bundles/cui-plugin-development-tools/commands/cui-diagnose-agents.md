---
name: cui-diagnose-agents
description: Analyze, verify, and fix agents for tool coverage, best practices, and structural issues
---

# Agents Doctor - Verify and Fix Agents

Analyze, verify, and fix agents for tool coverage, best practices, and structural issues.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace agents (standalone + bundle agents)
- **scope=global**: Analyze agents in global location (~/.claude/agents/)
- **scope=project**: Analyze agents in project location (.claude/agents/)
- **agent-name** (optional): Review a specific agent by name (e.g., `maven-project-builder`)
- **No parameters**: Interactive mode with marketplace default - display menu of all agents and let user select

## PARAMETER VALIDATION

**If `scope=marketplace` (default):**
- Process all `.md` files in two locations:
  - Standalone: `~/git/cui-llm-rules/claude/marketplace/agents/`
  - Bundle agents: `~/git/cui-llm-rules/claude/marketplace/bundles/*/agents/`
- Search across all marketplace locations
- Example paths:
  - `~/git/cui-llm-rules/claude/marketplace/agents/research-best-practices.md` (standalone)
  - `~/git/cui-llm-rules/claude/marketplace/bundles/cui-project-quality-gates/agents/maven-project-builder.md` (bundle)

**If `scope=global`:**
- Process all `.md` files in `~/.claude/agents/` directory
- Flat directory structure (no bundles)

**If `scope=project`:**
- Process all `.md` files in `.claude/agents/` directory
- Skip if directory doesn't exist (display message)

**If specific agent name is provided:**
- Search based on current scope parameter
- If no scope specified, search marketplace first, then global, then project
- Process the first match found
- Report error if agent not found

**If no parameters provided:**
- Use default scope (marketplace)
- Display interactive menu with numbered list of all agents from marketplace
- Let user select which agent(s) to review or change scope

## WORKFLOW INSTRUCTIONS

### Step 1: Determine Scope and Discover Agents

**A. Parse Parameters**

Determine what to process based on scope parameter (defaults to "marketplace"):

1. If `scope=marketplace` (default) → Set scope to both marketplace locations (standalone + bundle agents)
2. If `scope=global` → Set scope to `~/.claude/agents/`
3. If `scope=project` → Set scope to `.claude/agents/`
4. If agent name provided → Search in current scope only
5. If no parameters → Interactive mode with marketplace default

**B. Discover Agents**

Based on scope, find all agent files:

```bash
# For marketplace scope (default) - search both standalone and bundle agents
(find ~/git/cui-llm-rules/claude/marketplace/agents -name "*.md" -type f 2>/dev/null; \
 find ~/git/cui-llm-rules/claude/marketplace/bundles/*/agents -name "*.md" -type f 2>/dev/null) | sort

# For global scope
find ~/.claude/agents -name "*.md" -type f 2>/dev/null | sort

# For project scope
find .claude/agents -name "*.md" -type f 2>/dev/null | sort

# For specific agent in marketplace scope - search both locations
(find ~/git/cui-llm-rules/claude/marketplace/agents -name "<agent-name>.md" -type f 2>/dev/null; \
 find ~/git/cui-llm-rules/claude/marketplace/bundles/*/agents -name "<agent-name>.md" -type f 2>/dev/null) | head -1

# For specific agent in global scope
find ~/.claude/agents -name "<agent-name>.md" -type f 2>/dev/null | head -1

# For specific agent in project scope
find .claude/agents -name "<agent-name>.md" -type f 2>/dev/null | head -1
```

**C. Interactive Mode (if no parameters)**

Display menu based on scope:

```
Available Agents (scope=marketplace):

STANDALONE AGENTS (~/git/cui-llm-rules/claude/marketplace/agents/):
1. research-best-practices

BUNDLE AGENTS (~/git/cui-llm-rules/claude/marketplace/bundles/*/agents/):
2. maven-project-builder (cui-project-quality-gates bundle)
3. commit-changes (cui-project-quality-gates bundle)
4. asciidoc-reviewer (cui-documentation-standards bundle)
5. pr-quality-fixer (cui-pull-request-workflow bundle)
6. pr-review-responder (cui-pull-request-workflow bundle)
7. task-breakdown-agent (cui-issue-implementation bundle)
8. task-executor (cui-issue-implementation bundle)
9. task-reviewer (cui-issue-implementation bundle)
...

Options:
- Enter number to select single agent
- Enter "all" to review all agents in current scope
- Enter "scope=global" to switch to global agents
- Enter "scope=project" to switch to project agents
- Enter "quit" to exit

Your choice:
```

Wait for user input and set scope accordingly.

### Step 2: Read Architectural Principles

**CRITICAL**: Load agent architecture principles to use as verification criteria.

1. **Read architecture document**:
   ```
   Read: ~/git/cui-llm-rules/claude/agents-architecture.md
   ```

2. **Extract verification criteria**:
   - Best Practices for Well-Formed Agents (9 practices)
   - Tool Coverage Analysis guidelines (when each tool is required)
   - Essential Rules format specification
   - Tool Fit Score calculation formula
   - Response Format requirements
   - Lessons Learned vs Continuous Improvement distinction

3. **Store in working memory** for use during agent analysis

**Purpose**: Single source of truth for what makes a well-formed agent. All verification logic references this document.

### Step 3: Initialize Analysis Statistics

Create tracking variables:
- `total_agents`: Total number of agents to analyze
- `agents_with_issues`: Number of agents with problems
- `agents_fixed`: Number of agents fixed
- `total_issues`: Total issues found across all agents
- `issues_fixed`: Total issues fixed
- `critical_issues`: Number of critical issues found
- `warnings`: Number of warnings found
- `tool_coverage_issues`: Number of agents with tool coverage problems
- `rules_verified`: Total rule sets checked across all agents
- `rules_out_of_date`: Count needing sync
- `rules_orphaned`: Count with missing sources
- `rules_updated`: Count successfully synced
- `rules_old_sync`: Count with old sync warnings
- `duplication_issues`: Total duplication problems found (Step 4.7)
- `ambiguity_issues`: Total ambiguity problems found (Step 4.8)
- `precision_issues`: Total precision problems found (Step 4.9)
- `precision_scores`: List of precision scores for each agent (Step 4.9)
- `compliance_issues`: Total compliance problems found (Step 4.10)
- `checklist_compliance_scores`: List of checklist compliance percentages (Step 4.10)
- `antipatterns_found`: Total anti-patterns detected (Step 4.10)
- `temp_directory_violations`: Agents using /tmp instead of target/ (Step 4.5)
- `permission_issues`: Total permission pattern problems found (Step 4.12)
- `missing_approvals`: Count of commands needing approval
- `over_permissions`: Count of approved patterns not used by agent
- `stale_patterns`: Count of outdated/redundant patterns

### Step 4: Analyze Each Agent

For EACH agent file, execute the following analysis:

#### Step 4.1: Display Agent Header

```
==================================================
Analyzing: <agent-name>
Location: <file-path>
==================================================
```

#### Step 4.2: Read and Parse Agent

1. Read the entire agent file
2. Parse frontmatter (YAML between `---` markers):
   - name
   - description
   - tools
   - model
   - color

3. Parse body content:
   - Extract task description
   - Extract workflow instructions
   - Extract response format
   - Extract any other major sections

4. Count agent length:
   - Total lines
   - Total sections
   - Complexity score

Display:
```
Agent Overview:
- Name: <name>
- Model: <model>
- Tools: <list of tools>
- Length: <lines> lines
- Sections: <count>
- Complexity: <Low/Medium/High>
```

#### Step 4.2.5: Validate YAML Frontmatter (CRITICAL)

**REQUIRED**: Every agent MUST have valid YAML frontmatter at the very beginning.

```yaml
---
name: agent-name
description: Brief description of agent purpose
tools: Read, Write, Bash
model: sonnet
color: green
---
```

**Validation Checks:**

**A. Frontmatter Presence**
- ✅ Frontmatter exists at line 1
- ✅ Starts with `---` and ends with `---`
- ❌ **CRITICAL**: Without frontmatter, agent will NOT be discovered by Claude Code

**B. Required Fields**
- ✅ `name:` field present and matches filename (without .md extension)
  - Example: `maven-project-builder.md` → `name: maven-project-builder`
- ✅ `description:` field present (1-2 sentences describing when to use this agent)
- ✅ `tools:` field present (comma-separated list of tools)
- ✅ `model:` field present (typically: sonnet, opus, or haiku)
- ✅ `color:` field present (for UI visualization)

**C. YAML Syntax Validation**
- ✅ No tabs (must use spaces for indentation)
- ✅ Proper YAML syntax (key: value format)
- ✅ Tools list is comma-separated or YAML array
- ✅ Description is properly quoted if contains special characters

**D. Semantic Validation**
- ✅ Description clearly states WHEN agent should be invoked
- ✅ Description includes invocation examples (optional but recommended)
- ✅ Tools list will be validated against workflow in Step 4.3 (Tool Fit Analysis)

Display:
```
Frontmatter Validation:
✅ Valid YAML frontmatter present
✅ All required fields present
✅ Name matches filename
⚠️  Description could be more specific about invocation examples
✅ YAML syntax is valid
```

**If frontmatter is missing or invalid:**
```
❌ CRITICAL: No YAML frontmatter found!
   Agent will NOT be discovered by Claude Code.

   Required format at line 1:
   ---
   name: {agent-name}
   description: {description}
   tools: {tool-list}
   model: sonnet
   color: green
   ---
```

#### Step 4.3: Perform Tool Coverage Analysis

**CRITICAL: This is the most important analysis for agents**

**A. Extract Required Tools from Workflow**

Scan workflow instructions for tool usage:
- `Read` tool: References to reading files
- `Edit` tool: References to editing files
- `Write` tool: References to writing/creating files
- `Bash` tool: References to shell commands, git, maven, etc.
- `Grep` tool: References to searching content
- `Glob` tool: References to finding files by pattern
- `WebFetch` tool: References to fetching URLs
- `NotebookEdit` tool: References to Jupyter notebooks

**B. Compare Required vs Configured**

```
Tool Coverage Analysis:

Configured Tools: {tools from frontmatter}

Required Tools (from workflow):
✅ Read - Found in workflow, configured
✅ Edit - Found in workflow, configured
❌ Write - Found in workflow, NOT configured  <-- CRITICAL
✅ Bash - Found in workflow, configured
⚠️  Grep - Not found in workflow, but configured (unnecessary)

Issues:
CRITICAL: Missing tools that workflow requires
- Write tool needed in Step 4 but not configured
- Agent will request user approval when trying to use Write

WARNING: Unnecessary tools configured
- Grep tool configured but never used
- Increases permission surface area unnecessarily
```

**C. Categorize Tool Coverage Issues**

**CRITICAL Issues:**
- Required tool missing → Agent will fail or request approval
- Impact: Agent cannot complete task autonomously

**WARNINGS:**
- Extra tools configured → Bloat, unnecessary permissions
- Impact: Larger permission surface, potential confusion

**D. Calculate Tool Fit Score**

```
Tool Fit Score: <percentage>

Formula: (Correctly Configured Tools / (Required Tools + Unnecessary Tools)) * 100

Example:
- Required: 5 tools
- Configured: 5 tools
- Missing: 1 tool
- Unnecessary: 1 tool
Score: (4 / 7) * 100 = 57% (Poor fit)

Ratings:
- 100%: Perfect fit
- 90-99%: Good fit
- 70-89%: Fair fit
- <70%: Poor fit (needs fixing)
```

#### Step 4.4: Perform Structural Analysis

Check for common structural issues:

**A. Frontmatter Validation**

Required fields:
- ✅ `name`: Present and matches filename
- ✅ `description`: Present, clear, and actionable
- ✅ `tools`: Present and is a valid comma-separated list
- ✅ `model`: Present and valid (sonnet, haiku, opus)
- ✅ `color`: Present and valid (green, blue, purple, etc.)

**B. Description Quality**

The description should:
- ✅ Clearly state agent's purpose
- ✅ Include usage examples showing when to invoke
- ✅ Be specific, not generic
- ✅ Explain benefits/outcomes

**Example GOOD description:**
```yaml
description: Use this agent when the user needs to build and verify the entire project with quality checks. This agent should be used proactively after code changes are made to ensure the project still compiles and passes all quality gates.\n\nExamples:\n- User: "I've finished implementing the new token validation logic"\n  Assistant: "Let me use the maven-project-builder agent to verify the project builds successfully with all quality checks."
```

**Example BAD description:**
```yaml
description: Builds the project
```

**C. Workflow Structure**

Check workflow quality:
- ✅ Clear step-by-step instructions
- ✅ Steps are numbered/ordered
- ✅ Decision points clearly marked
- ✅ Error handling described
- ✅ Tool invocations use correct syntax
- ✅ NO references to self-modification or continuous improvement

**D. Anti-Self-Modification Check**

Agents should NOT:
- ❌ Modify their own .md file
- ❌ Have "CONTINUOUS IMPROVEMENT RULE" sections
- ❌ Update themselves based on lessons learned

Agents SHOULD:
- ✅ Report lessons learned to user
- ✅ Allow manual improvement
- ✅ Track tool usage for analysis

**E. Response Format**

Check if agent has:
- ✅ Defined response format section
- ✅ Structured output template
- ✅ Tool usage tracking in output
- ✅ Lessons learned reporting (optional but recommended)

Display findings:
```
Structural Analysis:
✅ Frontmatter complete and valid
✅ Description is clear and actionable
❌ Workflow missing error handling in Step 3
✅ No self-modification references (correct)
⚠️  Response format could be more structured
```

#### Step 4.5: Best Practices Compliance

Check against agent best practices:

**A. Tool Best Practices**

- ✅ Minimal tool set (only what's needed)
- ✅ Read tool included if Edit/Write used (Edit requires prior Read)
- ✅ No redundant tools (e.g., both Bash and mcp__jetbrains__execute_terminal_command)
- ✅ Tools match the agent's domain (don't give WebFetch to file processor)

**B. Autonomy Best Practices**

- ✅ Agent can complete task without user input (except for decision points)
- ✅ All tools needed are configured
- ✅ No permission gates block workflow
- ✅ Clear success/failure criteria

**C. Communication Best Practices**

- ✅ Structured output format defined
- ✅ Progress updates included
- ✅ Tool usage tracked and reported
- ✅ Lessons learned reported (not applied)

**D. Scope Best Practices**

- ✅ Single, well-defined responsibility
- ✅ Not too broad ("do everything")
- ✅ Not too narrow ("fix one specific typo")
- ✅ Clear boundaries with other agents

**E. Maven/Build Context Best Practices**

Search agent workflow for temp directory usage:
```bash
grep -E '/tmp/|/private/tmp/|mktemp|tempfile|~/tmp/' {agent_file}
```

Check for violations:
- ❌ Uses system temp directories (`/tmp/`, `/private/tmp/`) - should use `target/` in Maven projects
- ❌ Uses `mktemp` or `tempfile` commands - should create directories in `target/`
- ❌ Writes to home directory temp (`~/tmp/`) - should use project `target/` directory
- ✅ Uses project-local directories (e.g., `target/`, `build/`) for temporary files

**Note**: In Maven/Gradle build contexts, ALL temporary files and build artifacts should go in the project's `target/` or `build/` directory, not system temp directories. This ensures proper cleanup with `mvn clean` and keeps artifacts project-scoped.

**Update Statistics**: If violations found, increment `temp_directory_violations`

Display findings:
```
Best Practices Analysis:
✅ Tool set is minimal and appropriate
❌ Edit tool used but Read not configured (violates Read-before-Edit rule)
✅ Agent has clear, single responsibility
⚠️  No tool usage tracking in response format
✅ Lessons learned reporting present
```

#### Step 4.6: Verify Essential Rules Synchronization

**CRITICAL**: Ensure embedded rules are current with source standards.

**A. Check for Essential Rules Section**

Look for "## Essential Rules" section in agent body.

If NOT present:
- Display: "ℹ️ No Essential Rules section (agent may reference standards externally)"
- Continue to Step 4.7

If present, proceed with verification:

**B. Parse Embedded Rules**

For each subsection under "## Essential Rules":

Extract:
```
### {Domain} Standards
Source: {absolute_path}#{optional_section_anchor}
Last Synced: {YYYY-MM-DD} (optional)

{Embedded rules content - bullet points or prose}
```

Example:
```
### Logging Standards
Source: ~/git/cui-llm-rules/standards/logging/cui-logging-standards.adoc#logrecord-pattern
Last Synced: 2025-10-15

- All INFO/WARN/ERROR must use LogRecord constants
- Use %s for all string substitutions
...
```

**C. Verify Each Rule Set**

For each embedded rule set:

1. **Parse source reference**:
   - Extract file path
   - Extract optional section anchor (text after #)
   - Extract last synced date if present

2. **Read source file**:
   ```bash
   # Check if source exists
   if file exists:
       Read source file

       if section_anchor specified:
           # Extract only that section
           # (find section heading, read until next heading)
       else:
           # Use entire file or heuristic to find relevant content
   else:
       Mark as ORPHANED
   ```

3. **Compare content**:
   ```
   # Simple comparison (can enhance with checksums)
   embedded_lines = extract_rule_content(agent_file)
   source_lines = extract_source_content(source_file, section_anchor)

   if embedded_lines == source_lines:
       status = UP_TO_DATE
   else:
       status = OUT_OF_DATE
       diff_count = count_differences(embedded_lines, source_lines)
   ```

4. **Check sync age** (if Last Synced present):
   ```
   days_since_sync = today - last_synced_date

   if days_since_sync > 30:
       warning = OLD_SYNC  # Warn even if content matches
   ```

**D. Report Synchronization Status**

Display:
```
Essential Rules Verification:

✅ Logging Standards: Up-to-date
   Source: /Users/.../cui-logging-standards.adoc#logrecord-pattern
   Last synced: 2025-10-15 (5 days ago)

❌ JavaDoc Standards: OUT OF DATE
   Source: /Users/.../javadoc-standards.adoc#mandatory-javadoc
   Last synced: 2025-10-10 (10 days ago)
   Changes detected: 3 lines modified in source
   Impact: Agent may enforce outdated rules

⚠️  CUI Coding Standards: ORPHANED
   Source: /Users/.../deleted-file.adoc
   Error: Source file no longer exists
   Impact: Agent references non-existent standards

⚠️  Error Handling Standards: OLD SYNC
   Source: /Users/.../error-handling.adoc
   Last synced: 2025-09-01 (49 days ago)
   Status: Content matches, but sync is old (>30 days)
   Recommendation: Re-sync to ensure no recent changes

Summary:
- Total rule sets: 4
- Up-to-date: 1
- Out of date: 1
- Orphaned: 1
- Old sync warnings: 1
```

**E. Add to Issue Report**

Categorize synchronization issues:

**CRITICAL Issues:**
- OUT_OF_DATE: Embedded rules don't match source
- ORPHANED: Source file no longer exists

**WARNINGS:**
- OLD_SYNC: Content matches but >30 days since sync

Add to issue counts:
```
rules_out_of_date++  # for each OUT_OF_DATE
rules_orphaned++     # for each ORPHANED
rules_old_sync++     # for each OLD_SYNC
```

**F. Offer Synchronization** (if issues found)

Display:
```
Essential Rules Issues Found: <count>

Options:
U - Update all out-of-date rules from sources
R - Review changes and update selectively
V - View detailed diff for each out-of-date rule
S - Skip synchronization (continue with other analysis)

Please choose [U/r/v/s]:
```

**If user selects U (Update all):**

For each OUT_OF_DATE rule set:
1. Read source file (with section anchor if specified)
2. Extract source content
3. Use Edit tool to replace embedded rules:
   ```
   old_string: ### {Domain} Standards
               Source: {path}
               Last Synced: {old_date}

               {old embedded content}

   new_string: ### {Domain} Standards
               Source: {path}
               Last Synced: {today}

               {new source content}
   ```
4. Display: "✅ Updated {Domain} Standards from source"
5. Update tracking: `rules_updated++`

For each ORPHANED rule set:
- Display: "⚠️ Cannot update {Domain} Standards - source missing"
- Ask: "Remove orphaned rules? [y/N]:"
- If yes: Remove entire subsection

**If user selects R (Review):**

For each OUT_OF_DATE rule set:
1. Display current embedded content
2. Display source content
3. Highlight differences
4. Ask: "Update this rule set? [Y/n]:"
5. If yes: Apply update as above

**If user selects V (View diff):**

For each OUT_OF_DATE rule set:
```
Diff for {Domain} Standards:

- Old (embedded): "All public methods must have JavaDoc"
+ New (source):   "All public and protected methods must have JavaDoc"

- Old (embedded): "Missing JavaDoc = warning"
+ New (source):   "Missing JavaDoc = mandatory fix"
```

After viewing, return to options menu.

**G. Update Statistics**

Track in statistics:
- `rules_verified`: Total rule sets checked
- `rules_out_of_date`: Count needing sync
- `rules_orphaned`: Count with missing sources
- `rules_updated`: Count successfully synced
- `rules_old_sync`: Count with old sync warnings

#### Step 4.6A: Validate Architecture Compliance

**CRITICAL**: Validate agent follows marketplace architecture rules for skill usage.

**Invoke Architecture Skill**:
```
Skill: cui-marketplace-architecture
```

This loads architecture rules and validation patterns for marketplace components.

**A. Check if Agent Uses Standards**

Scan agent content for standards usage indicators:

```bash
# Look for references to standards, patterns, rules
grep -i "standard\|pattern\|guideline\|rule\|requirement" <agent-path>
```

If no standards references found:
- Display: "ℹ️ Agent does not reference standards (pure implementation agent)"
- Set `architecture_score = 100` (N/A)
- Continue to Step 4.7

If standards references found, proceed with validation:

**B. Validate Proper Skill Usage**

Apply validation from loaded standards (skill-usage-patterns.md):

1. **Check tools list**:
   ```yaml
   # Agent frontmatter should have:
   tools: [..., Skill]
   ```

   If `Skill` missing but agent uses standards:
   - Issue: "CRITICAL - Agent uses standards but missing 'Skill' in tools list"
   - Deduct 30 points from architecture score

2. **Check for Skill invocations**:
   ```
   # Look for proper skill usage pattern
   grep "Skill: cui-" <agent-path>
   ```

   If no `Skill:` invocations found but agent uses standards:
   - Issue: "CRITICAL - Agent references standards but has no Skill: invocations"
   - Deduct 30 points from architecture score

3. **Check for prohibited direct file references**:

   Apply detection from loaded standards (reference-patterns.md):

   ```bash
   # Check for escape sequences
   grep -n "\.\..*\.\..*\.\." <agent-path>

   # Check for absolute paths (excluding URLs)
   grep -n "~/\|^/" <agent-path> | grep -v "https://"

   # Check for direct .adoc references
   grep -n "Read:.*\.adoc" <agent-path>
   ```

   For each violation found:
   - Issue: "ARCHITECTURE VIOLATION - Direct file reference: {reference}"
   - Deduct 20 points from architecture score per violation
   - Add to issue report

**C. Calculate Architecture Score**

Apply scoring criteria from loaded standards (scoring-criteria.md):

```
Base score: 100

Deductions:
- Missing Skill in tools: -30 points
- No Skill: invocations: -30 points
- Direct file reference: -20 points each
- Absolute path: -20 points each
- Escape sequence: -20 points each

architecture_score = 100 - total_deductions
Min score: 0
```

**D. Report Architecture Status**

Display:
```
Architecture Compliance:

✅ Tools List: Has 'Skill' in allowed tools
✅ Skill Usage: Invokes Skill: cui-java-core, Skill: cui-javadoc
✅ Reference Patterns: No prohibited file references

Architecture Score: 100/100
Status: ✅ Excellent - Marketplace ready
```

Or if violations found:
```
Architecture Compliance:

❌ Tools List: Missing 'Skill' in tools list
   Impact: Cannot invoke skills at runtime
   Fix: Add 'Skill' to tools: [...] in frontmatter

❌ Direct References: 2 prohibited file references found
   Line 45: Read: ~/git/cui-llm-rules/standards/java-core.adoc
   Line 78: Read: ../../../../standards/logging/logging.adoc
   Impact: Breaks portability, bypasses skill abstraction
   Fix: Replace with Skill: cui-java-core, Skill: cui-logging

Architecture Score: 40/100
Status: ❌ Poor - Significant architecture violations
```

**E. Add to Issue Report**

Categorize architecture issues:

**CRITICAL Issues:**
- Missing `Skill` in tools list
- No skill invocations despite using standards
- Direct file references (escape sequences or absolute paths)

**WARNINGS:**
- Old pattern usage (if agent has Essential Rules but could use Skills)

Add to issue counts:
```
architecture_violations++  # for each violation
```

**F. Integrate with Tool Fit Score**

The architecture score should inform the overall Tool Fit Score:

```
# If architecture_score < 60:
#   Consider adding warning to Tool Fit assessment
#   Agent may need refactoring to use proper skill patterns

# Example integration:
if architecture_score < 60 and tool_fit_score > 75:
    display: "⚠️ Tool Fit is good but Architecture Compliance is poor"
    display: "   Recommendation: Refactor to use Skills instead of direct file references"
```

**G. Update Statistics**

Track in statistics:
- `architecture_score`: Architecture compliance (0-100)
- `architecture_violations`: Count of violations found
- `uses_skills`: Boolean - does agent properly invoke skills?

#### Step 4.7: Internal Duplication Analysis

**Purpose**: Detect and report duplicated instructions, rules, or content within the agent file.

**Execution**:

1. Read module: `~/git/cui-llm-rules/claude/agents/diagnose-agents/duplication-analysis.md`
2. Follow all instructions in the module to analyze the agent file
3. Update statistics as specified in module section F

#### Step 4.8: Ambiguity Detection

**Purpose**: Flag vague, ambiguous language that could have multiple interpretations.

**Execution**:

1. Read module: `~/git/cui-llm-rules/claude/agents/diagnose-agents/ambiguity-detection.md`
2. Follow all instructions in the module to analyze the agent file
3. Update statistics as specified in module section G

#### Step 4.9: Precision Analysis

**Purpose**: Measure instruction specificity and calculate precision score.

**Execution**:

1. Read module: `~/git/cui-llm-rules/claude/agents/diagnose-agents/precision-analysis.md`
2. Follow all instructions in the module to analyze the agent file
3. Update statistics as specified in module section G

#### Step 4.10: Industry Best Practices Compliance

**Purpose**: Verify agent follows industry standards from authoritative sources.

**Execution**:

1. Read module: `~/git/cui-llm-rules/claude/agents/diagnose-agents/compliance-checking.md`
2. Follow all instructions in the module to analyze the agent file
3. Update statistics as specified in module section E

#### Step 4.11: Detect Absolute Path Issues

**CRITICAL**: Scan for hardcoded absolute paths that should be user-relative.

**Search for absolute path patterns:**
```bash
# Search for common absolute path patterns
grep -n "~/" <agent-file>
grep -n "/home/[^/]*/" <agent-file>
```

**Categorize absolute paths:**

**CRITICAL - Must Replace:**
- `~/` → `~/`
- `/home/username/` → `~/`
- Hardcoded user paths in:
  - Essential Rules source references
  - Script paths in workflow (bash commands)
  - File paths in instructions
  - Directory references

**Acceptable - No Change:**
- Paths in user-facing examples showing format (if clearly marked as example)
- Generic paths like `/tmp/`, `/etc/`, `/usr/`

**Count absolute path issues:**
- Store in `absolute_path_count`
- Track each occurrence: file, line number, path pattern

**Example findings:**
```
Absolute Path Issues (2 found):

Line 38: Source: ~/git/cui-llm-rules/standards/logging.adoc
  → Should be: Source: ~/git/cui-llm-rules/standards/logging.adoc
  Impact: Essential Rules reference breaks for other users

Line 140: ~/git/cui-llm-rules/scripts/validator.sh
  → Already correct (user-relative)

Line 245: ~/git/cui-llm-rules/scripts/verify.sh {file_path} 2>&1
  → Should be: ~/git/cui-llm-rules/scripts/verify.sh {file_path} 2>&1
  Impact: Script path not portable across users
```

#### Step 4.12: Verify Permission Patterns

**Purpose**: Extract bash commands from agent workflow and ensure they're approved via `/setup-project-permissions`.

**SIMPLIFIED WORKFLOW**: diagnose-agents just extracts, setup-project-permissions handles all the verification and fixing.

**A. Extract Bash Commands from Agent Workflow**

Scan agent file for bash command usage:

1. **Extract bash code blocks**:
   ```bash
   # Find all ```bash blocks in agent file
   awk '/```bash/,/```/' <agent-file>
   ```

2. **Extract commands and convert to permission format**:

   **Script paths**:
   - `~/git/cui-llm-rules/scripts/validator.sh` → `Bash(~/git/cui-llm-rules/scripts/validator.sh:*)`
   - `python3 ~/git/cui-llm-rules/scripts/verify.py` → `Bash(python3 ~/git/cui-llm-rules/scripts/verify.py:*)`

   **Commands**:
   - `grep` → `Bash(grep:*)`
   - `find` → `Bash(find:*)`
   - `wc` → `Bash(wc:*)`
   - `sed` → `Bash(sed:*)`
   - `sort` → `Bash(sort:*)`
   - `test` → `Bash(test:*)`

   **Control structures**:
   - `for` loops → `Bash(for:*)`
   - `while` loops → `Bash(while:*)`

3. **Build comma-separated list of required permissions**:
   ```
   required_permissions="Bash(grep:*),Bash(find:*),Bash(wc:*),Bash(~/git/cui-llm-rules/scripts/validator.sh:*)"
   ```

**B. Delegate to setup-project-permissions**

Invoke setup-project-permissions with ensurePermissions parameter:

```bash
/setup-project-permissions ensurePermissions="$required_permissions"
```

This triggers setup-project-permissions Step 3.5 which:
- Checks global and local settings for each required permission
- Reports globally approved (no local action needed)
- Reports locally approved (already configured)
- Detects missing permissions (not approved anywhere)
- Detects over-permissions (approved locally but not required)
- Calculates Permission Fit Score
- Offers to fix issues (add missing, remove over-permissions)
- Handles all user prompts and safety checks

**C. Display Results from setup-project-permissions**

setup-project-permissions returns a report like:

```
Permission Status Analysis for <agent-name>:

✅ GLOBALLY APPROVED (no local action needed):
- Bash(grep:*) - Available via global settings
- Bash(find:*) - Available via global settings

✅ LOCALLY APPROVED (already configured):
- Bash(~/git/cui-llm-rules/scripts/validator.sh:*)

❌ MISSING (needs approval):
- Bash(wc:*) - Not approved globally or locally

⚠️  OVER-PERMISSIONS (approved locally but not required):
- Bash(asciidoctor:*) - Agent doesn't use this (SECURITY RISK)
- Bash(npm:*) - Agent doesn't use this

Permission Fit Score: 67% (Fair fit)
- Will prompt for: wc
- Over-permissions: 2
- Security risks: 1 (asciidoctor)

Fix issues? [F/r/s]: <user response>

[If user fixes:]
✅ Permission Sync Complete:
- Added: 1 permission
- Removed: 2 over-permissions
- New Permission Fit Score: 100% (Perfect)
```

**D. Parse Results and Update Statistics**

Extract from setup-project-permissions report:
- Permission Fit Score: `<percentage>`
- Missing permissions count: `<count>`
- Over-permissions count: `<count>`

Update tracking:
```
permission_issues += (missing_count + over_permission_count)
missing_approvals += missing_count
over_permissions += over_permission_count
```

**E. Benefits of Delegation**

**No Code Duplication**:
- All permission logic in setup-project-permissions only
- Consistent behavior across diagnose-commands, diagnose-agents, and direct usage

**Automatic Global/Local Handling**:
- setup-project-permissions understands global vs local architecture
- Decides placement automatically based on permission type
- Never duplicates global permissions in local settings

**Comprehensive Safety Checks**:
- Duplicate detection
- Suspicious permission flagging
- Path normalization (user-absolute → user-relative)
- Global/local architecture enforcement
- Security risk assessment

**Consistent Reporting**:
- Same Permission Fit Score calculation everywhere
- Same categorization (globally approved, locally approved, missing, over-permissions)
- Same user prompts and fix options

**Easier Maintenance**:
- Update permission logic once in setup-project-permissions
- Automatically benefits all callers (diagnose-commands, diagnose-agents)
- No synchronization needed between commands

#### Step 4.13: Generate Issue Report

Categorize all issues found:

**CRITICAL Issues (Must Fix):**
- Hardcoded absolute paths → Not portable across users
- Missing required tools → Agent will fail
- Tool configuration errors → Agent requests approval
- Broken workflow logic → Agent cannot complete
- Self-modification references → Wrong pattern for agents
- Over-permissions (security risk) → Dangerous commands auto-approved unnecessarily
- Missing bash command approvals → Agent will prompt user frequently

**WARNINGS (Should Fix):**
- Unnecessary tools configured → Bloat, security
- Missing error handling → Fragile execution
- Poor description → Unclear when to use
- Missing response format → Inconsistent output
- Missing tool usage tracking → No visibility
- Stale permission patterns → Confusing, maintenance burden

**SUGGESTIONS (Nice to Have):**
- Add lessons learned reporting
- Enhance progress updates
- Add verification steps
- Improve documentation

Display categorized report:
```
Issue Report for <agent-name>:

CRITICAL (2 issues):
1. Tool Coverage: Write tool required but not configured
   Location: Step 4 uses Write but tools list has: "Read, Edit, Bash"
   Impact: Agent will request user approval when attempting to write files
   Fix: Add "Write" to tools list in frontmatter

2. Tool Coverage: Edit requires Read but Read not configured
   Location: Step 3 uses Edit but tools list missing Read
   Impact: Edit tool will fail (requires prior Read)
   Fix: Add "Read" to tools list in frontmatter

WARNINGS (3 issues):
1. Unnecessary Tool: Grep configured but never used
   Impact: Larger permission surface, potential confusion
   Fix: Remove "Grep" from tools list

2. Missing Tool Usage Tracking
   Impact: No visibility into agent's tool usage patterns
   Fix: Add "Tools Used" section to response format

3. Description too generic: "Builds the project"
   Impact: Unclear when to invoke this agent
   Fix: Add usage examples and specific scenarios

SUGGESTIONS (1 item):
1. Add Lessons Learned reporting
   Benefit: Enables manual improvement over time
   Fix: Add "Lessons Learned Reporting" section

Total: 6 issues found
Tool Fit Score: 60% (Poor fit - needs fixing)
```

#### Step 4.14: Decision Point - Fix Issues?

**If NO issues found:**
- Display: "✅ Agent is well-formed and follows best practices - No issues found"
- Continue to next agent

**If issues found:**

Display:
```
Found <count> issues in <agent-name>:
- Critical: <count>
- Warnings: <count>
- Suggestions: <count>

Tool Fit Score: <percentage> (<rating>)

Essential Rules: <rules_out_of_date> out of date, <rules_orphaned> orphaned

Options:
F - Fix all issues automatically
R - Review each issue individually before fixing
S - Skip this agent (do not fix)
Q - Quit analysis entirely

Please choose [F/r/s/q]:
```

**If user responds:**
- `F` or `f` → Fix all issues automatically (Step 4.15)
- `R` or `r` → Review each issue individually (Step 4.16)
- `S` or `s` → Skip this agent, move to next
- `Q` or `q` → Stop analysis, exit command

#### Step 4.15: Auto-Fix All Issues

**For absolute path issues:**
1. Use Edit tool to replace all occurrences of `~/` with `~/`
2. Use Edit tool to replace all occurrences of `/home/username/` patterns with `~/`
3. Display: "✅ Fixed: Replaced <count> absolute paths with user-relative paths"

**For tool coverage CRITICAL issues:**
1. Read the agent file
2. Parse frontmatter
3. Update tools list:
   - Add missing required tools
   - Remove unnecessary tools
4. Write updated frontmatter
5. Display: "✅ Fixed: Added <tool> to tools list"

**For other CRITICAL issues:**
1. Apply the specific fix using Edit tool
2. Update tracking: `critical_issues_fixed++`
3. Display: "✅ Fixed: <issue-summary>"

**For WARNINGS:**
1. Apply fixes when deterministic
2. Skip warnings that need user judgment
3. Update tracking: `warnings_fixed++`
4. Display: "✅ Fixed: <issue-summary>" or "⚠️ Skipped: <reason>"

**For SUGGESTIONS:**
- Skip suggestions in auto-fix mode
- Display: "ℹ️ Skipped <count> suggestions (auto-fix mode)"

After fixing:
```
Auto-Fix Complete:
- Critical issues fixed: <count>
- Warnings fixed: <count>
- Remaining issues: <count>
- New Tool Fit Score: <percentage> (<rating>)
```

Continue to Step 4.16 (Verification)

#### Step 4.16: Review and Fix Individually

For EACH issue (in order: Critical → Warnings → Suggestions):

Display:
```
Issue <number> of <total>:
Severity: <CRITICAL/WARNING/SUGGESTION>
Location: <description>
Problem: <description>

Current Configuration:
<show relevant content>

Proposed Fix:
<describe the fix>

Options:
Y - Apply this fix
N - Skip this issue
E - Edit fix (provide alternative)
Q - Stop reviewing, skip remaining issues

Please choose [Y/n/e/q]:
```

**If user responds:**
- `Y` or `y` → Apply the fix, continue to next issue
- `N` or `n` → Skip this issue, continue to next issue
- `E` or `e` → Ask for user's alternative fix, apply it, continue
- `Q` or `q` → Stop reviewing, move to Step 4.12

After review:
```
Review Complete:
- Issues fixed: <count>
- Issues skipped: <count>
- Remaining: <count>
- New Tool Fit Score: <percentage> (<rating>)
```

Continue to Step 4.17 (Verification)

#### Step 4.17: Verify Fixes

If any fixes were applied:

1. Re-read the agent file
2. Re-run analysis (Steps 4.3, 4.4, 4.5)
3. Recalculate Tool Fit Score
4. Compare before/after:
   ```
   Verification Results:
   - Issues before: <old_count>
   - Issues after: <new_count>
   - Issues fixed: <fixed_count>
   - Tool Fit Score: <old_score>% → <new_score>%
   - New issues introduced: <count>
   ```

5. If new issues introduced:
   - Display: "⚠️ WARNING: Fixes introduced <count> new issues"
   - Offer to revert: "Revert changes? [y/N]:"

6. Update statistics:
   - `agents_fixed++`
   - `issues_fixed += <count>`

#### Step 4.18: Display Agent Summary

```
Summary for <agent-name>:
- Initial issues: <count>
- Issues fixed: <count>
- Remaining issues: <count>
- Tool Fit Score: <old>% → <new>%
- Essential Rules: <rules_out_of_date> out of date, <rules_updated> updated
- Duplication issues: <count>
- Ambiguity issues: <count>
- Precision Score: <percentage>% (<rating>)
- Compliance Score: <percentage>% (<rating>)
- Anti-patterns found: <count>
- Status: ✅ Excellent / ⚠️ Has warnings / ❌ Has critical issues
```

### Step 5: Generate Final Report

After processing all agents, display comprehensive summary:

```
==================================================
Agents Doctor - Analysis Complete
==================================================

Agents Analyzed: <total_agents>
- With issues: <agents_with_issues>
- Fixed: <agents_fixed>
- Still have issues: <remaining>

Issue Statistics:
- Total issues found: <total_issues>
- Critical: <critical_count>
- Warnings: <warning_count>
- Suggestions: <suggestion_count>
- Issues fixed: <issues_fixed>

Tool Coverage Analysis:
- Agents with perfect tool fit (100%): <count>
- Agents with good tool fit (90-99%): <count>
- Agents with fair tool fit (70-89%): <count>
- Agents with poor tool fit (<70%): <count>

Essential Rules Verification:
- Total rule sets checked: <rules_verified>
- Up-to-date: <rules_up_to_date>
- Out of date: <rules_out_of_date>
- Orphaned (source missing): <rules_orphaned>
- Old sync warnings: <rules_old_sync>
- Successfully updated: <rules_updated>

Internal Duplication Analysis:
- Total duplication issues found: <duplication_issues>
- Agents with duplication: <count>
- Most common: Exact duplicates in workflow and CRITICAL RULES

Ambiguity Detection:
- Total ambiguity issues found: <ambiguity_issues>
- Vague conditionals: <count>
- Generic verbs: <count>
- Undefined scope: <count>
- Unmeasurable goals: <count>

Precision Analysis:
- Average precision score: <average_precision_score>% (<rating>)
- Agents with excellent precision (90-100%): <count>
- Agents with good precision (75-89%): <count>
- Agents with fair precision (60-74%): <count>
- Agents with poor precision (<60%): <count>
- Total precision issues: <precision_issues>

Industry Best Practices Compliance:
- Average checklist compliance: <average_compliance>% (<rating>)
- Agents fully compliant (100%): <count>
- Agents mostly compliant (90-99%): <count>
- Agents partially compliant (70-89%): <count>
- Agents non-compliant (<70%): <count>
- Total anti-patterns detected: <antipatterns_found>
- Total compliance issues: <compliance_issues>

Build Context Compliance:
- Agents using system temp directories (/tmp): <temp_directory_violations>
- Should use project target/ directory instead

Permission Pattern Analysis:
- Total permission issues found: <permission_issues>
- Missing bash command approvals: <missing_approvals>
- Over-permissions (security risks): <over_permissions>
- Stale/redundant patterns: <stale_patterns>
- Agents with perfect permission fit (100%): <count>
- Agents with permission issues: <count>

By Agent:
<for each agent with issues>
- <agent-name>: <issue_count> issues (<critical>C / <warnings>W / <suggestions>S)
  Tool Fit: <percentage>% (<rating>)
  Permission Fit: <percentage>% (<rating>)
  Essential Rules: <rules_out_of_date> out of date, <rules_orphaned> orphaned
  Duplication: <count> issues
  Ambiguity: <count> issues
  Precision: <percentage>% (<rating>)
  Compliance: <percentage>% (<rating>)
  Anti-patterns: <count>
  Permission Issues: <missing> missing, <over> over-permissions, <stale> stale
  Status: <Excellent/Good/Fair/Poor>
</for each>

Recommendations:
<if critical issues remain>
⚠️  CRITICAL: <count> agents still have critical issues
- <agent-1>: Tool coverage incomplete - missing <tool>
- <agent-2>: Workflow broken - <issue>
Re-run diagnose-agents on these agents to fix.
</if>

<if all excellent>
✅ All analyzed agents follow best practices with perfect tool fit!
</if>
```

## CRITICAL RULES

- **READ ENTIRE AGENT** before analyzing - context is essential
- **TOOL COVERAGE IS CRITICAL** - Agent must run without user approval
- **VERIFY ESSENTIAL RULES** - Check embedded rules are current with sources
- **CATEGORIZE ISSUES PROPERLY** - Critical vs Warning vs Suggestion
- **EXPLAIN FIXES CLEARLY** - User should understand why each change is made
- **VERIFY AFTER FIXING** - Always re-analyze to ensure fixes worked
- **PRESERVE INTENT** - Fix structure/tools but preserve agent's purpose
- **USE EDIT TOOL** - Never rewrite entire files, use targeted edits
- **TRACK STATISTICS** - Maintain counters throughout analysis
- **HANDLE ERRORS** - If agent file is malformed/unreadable, report and skip
- **CALCULATE TOOL FIT** - Track how well tools match workflow needs
- **NO SELF-MODIFICATION** - Agents should not modify themselves
- **SYNC RULES AUTOMATICALLY** - Offer to update out-of-date embedded rules

## USAGE EXAMPLES

### Analyze All Marketplace Agents (default)
```
/cui-diagnose-agents
/cui-diagnose-agents scope=marketplace
```

### Analyze All Global Agents
```
/cui-diagnose-agents scope=global
```

### Analyze All Project Agents
```
/cui-diagnose-agents scope=project
```

### Analyze Specific Agent (uses scope to determine where to search)
```
/cui-diagnose-agents maven-project-builder
/cui-diagnose-agents scope=global maven-project-builder
/cui-diagnose-agents scope=project custom-validator
```

### Interactive Mode (defaults to marketplace)
```
/cui-diagnose-agents
[Select from menu or change scope]
```

## ERROR HANDLING

**If agent file not found:**
```
❌ ERROR: Agent '<name>' not found
Searched in:
- .claude/agents/
- ~/.claude/agents/

Available agents: <list>
```

**If agent file is malformed:**
```
⚠️ WARNING: Agent '<name>' could not be parsed
Error: <description>

Options:
V - View file contents
S - Skip this agent
Q - Quit analysis

Please choose [V/s/q]:
```

**If frontmatter is invalid:**
```
❌ ERROR: Agent '<name>' has invalid frontmatter
Missing required fields: <list>

This must be fixed manually.
```

## INTEGRATION

Run `diagnose-agents` periodically to:
- After creating new agents
- After major updates to existing agents
- When agents request unexpected user approvals
- As part of project maintenance
- Before deploying agents to production

## NOTES

- This command analyzes agent STRUCTURE, TOOLS, and BEST PRACTICES
- It does NOT test agent FUNCTIONALITY
- For functionality testing, actually invoke the agent
- Agents-doctor focuses on: tool coverage, autonomy, best practices
- Always backup important agents before fixing
- Git tracks agent files, so changes can be reverted
- Tool fit score is the most critical metric for agents
