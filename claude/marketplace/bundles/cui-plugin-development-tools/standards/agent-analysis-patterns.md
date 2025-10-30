# Agent Analysis Patterns

Common issues and patterns to detect when analyzing agents.

## Pattern 1: Missing Critical Tools

**Problem:** Agent task requires tools not listed in `tools` field
**Example:** Agent description says "reads and modifies files" but tools only include `[Read]` (missing Edit/Write)
**Detection:** Parse agent workflow, identify tool calls, compare with tools list
**Fix:** Add missing tools to frontmatter

## Pattern 2: Over-Permission (Unused Tools)

**Problem:** Agent lists tools in frontmatter but never uses them
**Example:** `tools: [Read, Write, Edit, Bash, Grep, Glob]` but agent only uses Read and Write
**Impact:** Unnecessary permissions, security concern
**Fix:** Remove unused tools from frontmatter

## Pattern 3: Invalid YAML Frontmatter

**Problem:** Invalid YAML syntax, missing delimiters, missing required fields
**Example:** No `---` markers, missing `name` or `description`, using tabs instead of spaces
**Fix:** Repair YAML structure, add missing fields

## Pattern 4: Wrong Tool Field Name

**Problem:** Using `allowed-tools` instead of `tools`
**Example:** `allowed-tools: [Read, Write]` (agents use `tools`, skills use `allowed-tools`)
**Fix:** Rename field to `tools`

## Pattern 5: Absolute Paths

**Problem:** Hardcoded system-specific paths
**Example:** `~/specific-user/project/`, `/Users/john/`, `/home/jane/`
**Impact:** Agent not portable across systems
**Fix:** Use relative paths or environment variables

## Pattern 6: Temp Directory Violation

**Problem:** Maven/build agents using `/tmp` instead of `target/`
**Example:** Agent generates files in `/tmp/build-output/`
**Impact:** Violates Maven project context principle
**Fix:** Change to use `target/` directory

## Pattern 7: Orphaned Essential Rules

**Problem:** Rules in "Essential Rules" section with no source attribution
**Example:** Rule without `(from: source.md)` suffix
**Impact:** Cannot verify rule accuracy or sync with source
**Fix:** Add source attribution or remove rule

## Pattern 8: Out-of-Date Essential Rules

**Problem:** Rule content doesn't match current source document
**Detection:** Compare rule text with source document content
**Impact:** Agent uses outdated guidelines
**Fix:** Update rule from source, add sync metadata

## Pattern 9: Permission Pattern Violations

**Problem:** Agent uses Bash commands not in approved patterns
**Example:** Agent runs `git push` but tools list doesn't include `Bash(git:push)`
**Impact:** Requires user approval on every run (poor UX)
**Fix:** Add missing permission pattern

## Pattern 10: Ambiguous Instructions

**Problem:** Vague language that doesn't provide clear guidance
**Example:** "Process files appropriately", "Use when needed", "Handle errors well"
**Detection:** Search for vague terms (appropriately, when needed, well, etc.)
**Fix:** Replace with specific criteria

## Pattern 11: Internal Duplication

**Problem:** Same information repeated in multiple sections
**Example:** Task description duplicated in workflow steps
**Fix:** Remove duplication, use cross-references

## Pattern 12: Missing Description

**Problem:** Description field empty or too short (< 10 chars)
**Example:** `description: "Agent"` or `description: ""`
**Impact:** User doesn't understand what agent does
**Fix:** Write clear description (50-200 chars recommended)

## Pattern 13: Description Too Long

**Problem:** Description exceeds 1024 characters (Claude Code limit)
**Example:** Multi-paragraph description in frontmatter
**Fix:** Condense to essential information, move details to agent body

## Pattern 14: Inconsistent Naming

**Problem:** Filename doesn't match frontmatter `name`
**Example:** File: `test-runner.md`, YAML name: `maven-test-executor`
**Fix:** Align naming (filename should match frontmatter name)

## Pattern 15: Missing Response Format

**Problem:** Agent produces output but doesn't specify format
**Example:** Agent generates report but no "## Response Format" section
**Impact:** User doesn't know what to expect
**Fix:** Add response format section

## Pattern 16: Tool Coverage Score Low

**Problem:** Tool Fit Score < 75%
**Calculation:** `(tools_used / tools_listed) * 100`
**Example:** Agent lists 8 tools but only uses 4 (50% score)
**Fix:** Remove unused tools or add missing workflow steps

## Pattern 17: Agent Too Complex

**Problem:** Agent exceeds 300 lines with complex branching
**Example:** Single agent handling 5+ distinct tasks
**Impact:** Hard to maintain, test, understand
**Fix:** Split into multiple focused agents

## Pattern 18: Documentation-Only Noise

**Problem:** Sections with only broken external links
**Example:** "See Also" section with xref links to non-existent files
**Fix:** Remove section (zero information loss)

## Pattern 19: Missing Task Description

**Problem:** No clear task section explaining what agent does
**Example:** Agent jumps directly to workflow without context
**Fix:** Add task description section

## Pattern 20: Stale Permission Patterns

**Problem:** Approved patterns no longer used by agent
**Example:** `Bash(docker:*)` approved but agent doesn't use Docker anymore
**Fix:** Remove outdated patterns

## Pattern Detection Priority

### CRITICAL (Must Fix Before Use):
- Pattern 1: Missing Critical Tools
- Pattern 3: Invalid YAML Frontmatter
- Pattern 5: Absolute Paths
- Pattern 7: Orphaned Essential Rules
- Pattern 9: Permission Pattern Violations
- Pattern 12: Missing Description

### WARNING (Should Fix for Quality):
- Pattern 2: Over-Permission
- Pattern 4: Wrong Tool Field Name
- Pattern 6: Temp Directory Violation
- Pattern 8: Out-of-Date Essential Rules
- Pattern 10: Ambiguous Instructions
- Pattern 11: Internal Duplication
- Pattern 13: Description Too Long
- Pattern 16: Tool Coverage Score Low
- Pattern 18: Documentation-Only Noise
- Pattern 20: Stale Permission Patterns

### SUGGESTION (Nice to Have):
- Pattern 14: Inconsistent Naming
- Pattern 15: Missing Response Format
- Pattern 17: Agent Too Complex
- Pattern 19: Missing Task Description

## Pattern Detection Logic

When analyzing agents, check patterns in this order:

1. **Structural Issues** (Patterns 3, 12, 13, 14) - Agent must be loadable
2. **Tool Coverage** (Patterns 1, 2, 16) - Core functionality
3. **Portability** (Patterns 5, 6) - Must work across systems
4. **Permissions** (Patterns 9, 20) - Security and UX
5. **Essential Rules** (Patterns 7, 8) - Accuracy of guidance
6. **Content Quality** (Patterns 10, 11, 15, 18, 19) - Clarity and usability
7. **Configuration** (Pattern 4) - Correct frontmatter format
8. **Complexity** (Pattern 17) - Maintainability

## Anti-Patterns to Avoid

**Swiss Army Knife Agent:**
- Tries to do too many things
- Low cohesion, high coupling
- Split into focused agents

**Tool Hoarder:**
- Lists every possible tool
- Most tools never used
- Remove unused tools

**Path Hard-Coder:**
- Uses absolute paths
- Not portable
- Use relative paths

**The Vague Agent:**
- Ambiguous instructions
- "Handle appropriately"
- Use specific criteria

**The Duplicator:**
- Repeats same info in multiple places
- Maintenance burden
- Consolidate content

**The Orphan:**
- Rules without sources
- Cannot verify accuracy
- Add source attribution

**The Permission Violator:**
- Uses commands without approval
- Triggers user prompts
- Add permission patterns

**The /tmp User:**
- Maven agent using /tmp
- Violates project context
- Use target/ directory
