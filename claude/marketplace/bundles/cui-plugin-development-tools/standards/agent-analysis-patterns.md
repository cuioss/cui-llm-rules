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

## Pattern 21: Incorrect Skill Script References

**Problem:** Agent references scripts within skills using wrong paths or patterns
**Context:** Skills can contain executable scripts (e.g., validation, processing scripts) in their `scripts/` subdirectory
**Standard Pattern:** `./.claude/skills/{skill-name}/scripts/{script-name}`

**Examples of INCORRECT patterns:**
- `scripts/asciidoc-validator.sh` (relative path - fails due to cwd reset between bash calls)
- `~/git/cui-llm-rules/...` (absolute development path - not portable)
- `$HOME/git/...` (environment-specific - not portable)
- Multiple path checking with fallbacks (overly complex, unnecessary)

**Examples of CORRECT pattern:**
```yaml
tools: Bash(./.claude/skills/cui-documentation/scripts/asciidoc-validator.sh)
```
```bash
./.claude/skills/cui-documentation/scripts/asciidoc-validator.sh {file_path} 2>&1
```

**Why This Pattern:**
1. **System Constraint:** Agent threads have cwd reset between bash calls, requiring absolute-style paths
2. **Standard Location:** Skills install to `./.claude/skills/` directory when using `/plugin install`
3. **Portability:** Works across projects, requires proper skill installation (correct dependency management)
4. **Consistency:** All skill-based scripts use the same pattern
5. **Documentation:** Documented in skill SKILL.md and README.md files

**Detection:**
- Find agents with `Bash` tool that reference `.sh` or `.py` files
- Check if path uses non-standard format
- Verify against `./.claude/skills/{skill-name}/scripts/` pattern

**Fix:**
1. Update tool declaration: `Bash(./.claude/skills/{skill-name}/scripts/{script-name})`
2. Update workflow execution paths to use `./.claude/skills/...`
3. Remove dynamic path checking or fallback logic
4. Document that skill must be installed for agent to work

**Impact:** Scripts may fail to execute or require complex environment setup. Using standard pattern ensures reliability and proper dependency declaration.

**Reference Implementation:**
- `asciidoc-link-verifier.md` (lines 12, 72-77) - Correct implementation
- `asciidoc-format-validator.md` (lines 12, 68-73) - Correct implementation

## Pattern 22: Agent Self-Invocation Instructions

**Problem:** Agent contains instructions telling it to invoke slash commands directly
**Context:** CONTINUOUS IMPROVEMENT RULE sections that instruct agent to call `/plugin-update-agent` or other commands
**Architecture Rule Violation:** Rule 6 - Agents CANNOT invoke commands (SlashCommand tool unavailable at runtime)

**Examples of INCORRECT patterns:**

```markdown
❌ **CRITICAL:** Every time you execute this agent... **YOU MUST immediately update this file**
   using `/plugin-update-agent agent-name={agent-name} update="[your improvement]"`

❌ After analysis, invoke `/plugin-diagnose-agents` to verify changes

❌ When improvements found, call `/plugin-update-command` to apply them
```

**Why This is Wrong:**
1. **Architecture Constraint:** Agents do not have access to SlashCommand tool at runtime (Rule 6)
2. **Impossible Instruction:** Creates instructions that cannot be executed
3. **Violates Agent Design:** Agents must be focused executors that REPORT to caller
4. **Breaks Layer Separation:** Agents (Layer 2) cannot invoke Commands (Layer 3)

**CORRECT pattern - Agent Reports to Caller:**

```markdown
✅ ## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this agent and discover improvements:

1. Document the improvement in your analysis result
2. Report specific enhancement opportunity to caller
3. Return structured improvement suggestion with:
   - Improvement area description
   - Current limitation
   - Suggested enhancement
   - Expected impact

The CALLER can then invoke `/plugin-update-agent agent-name={agent-name}`
based on your improvement report.
```

**Detection Patterns:**

```bash
# Grep patterns to detect violation:
Grep: "YOU MUST.*(\/plugin-|\/cui-|SlashCommand)"
Grep: "(invoke|call|execute|trigger|run)\s+/plugin-"
Grep: "immediately.*update this file.*using\s+/"
Grep: "SlashCommand:\s*/plugin-update"
```

**Fix Strategy:**
1. Replace "YOU MUST invoke /command" with "REPORT improvement to caller"
2. Change imperative command invocation to structured result return
3. Add caller invocation example in documentation (not instruction)
4. Verify agent workflow never attempts SlashCommand usage

**Impact:**
- **Critical:** Agent attempts impossible action at runtime
- **Confusion:** Mixed messaging about agent capabilities
- **Architecture:** Violates fundamental layer separation principle

**Reference:**
- Architecture Rule 6: Agent Delegation Constraints (architecture-rules.md)
- `/plugin-create-agent` validation lines 65-101 (Task/Maven checks as precedent)

**Priority:** CRITICAL (same as Pattern 1, 3, 5, 7, 9, 12)

**Validation Location:**
- `/plugin-diagnose-agents`: Step 4.5 - Architectural constraint validation
- `/plugin-create-agent`: Step 3C - CONTINUOUS IMPROVEMENT RULE validation
- `diagnose-agent` (sub-agent): Include in architectural compliance check

## Pattern Detection Priority

### CRITICAL (Must Fix Before Use):
- Pattern 1: Missing Critical Tools
- Pattern 3: Invalid YAML Frontmatter
- Pattern 5: Absolute Paths
- Pattern 7: Orphaned Essential Rules
- Pattern 9: Permission Pattern Violations
- Pattern 12: Missing Description
- Pattern 22: Agent Self-Invocation Instructions

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
- Pattern 21: Incorrect Skill Script References

### SUGGESTION (Nice to Have):
- Pattern 14: Inconsistent Naming
- Pattern 15: Missing Response Format
- Pattern 17: Agent Too Complex
- Pattern 19: Missing Task Description

## Pattern Detection Logic

When analyzing agents, check patterns in this order:

1. **Structural Issues** (Patterns 3, 12, 13, 14) - Agent must be loadable
2. **Tool Coverage** (Patterns 1, 2, 16) - Core functionality
3. **Portability** (Patterns 5, 6, 21) - Must work across systems and environments
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

**The Script Path Guesser:**
- Tries multiple script locations with fallbacks
- Uses relative or development-specific paths
- Violates standard skill installation pattern
- Use `./.claude/skills/{skill-name}/scripts/` pattern
