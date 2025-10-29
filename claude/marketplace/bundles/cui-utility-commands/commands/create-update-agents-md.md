# Verify Agents.md Command

Creates or update the project specific agents.md

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** with:
1. Improved agents.md structure patterns or validation techniques
2. Better methods for extracting project requirements
3. More effective ways to analyze OpenAI agents.md format
4. Enhanced content organization strategies
5. Any lessons learned about agents.md creation/updating

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

### Standard Parameters

**push** (optional)
- Automatically commits and pushes changes after successful execution
- Usage: `/create-update-agents-md push`
- If omitted: Changes remain uncommitted for manual review

### Usage Examples

```bash
# Basic execution - creates/updates agents.md
/create-update-agents-md

# Execute and auto-commit/push changes
/create-update-agents-md push
```

## PARAMETER VALIDATION

**Step: Validate Parameters**

1. Check if `push` parameter is provided
   - Store as boolean flag for later use
   - Valid values: presence of word "push" anywhere in arguments

2. Reject any unrecognized parameters
   - Only `push` is valid
   - Display error and exit if invalid parameters found

## WORKFLOW INSTRUCTIONS

### PRE-CONDITION VERIFICATION

**Step 0: Verify Pre-Conditions**

Before proceeding with the main workflow, verify:

1. **Git Repository Check**
   - Run: `git rev-parse --is-inside-work-tree`
   - If fails: Display error and exit
   - Error message: "This command requires the project to be a git repository"

### MAIN WORKFLOW

**Step 1: Research OpenAI agents.md Format**

1.1. Fetch OpenAI agents.md specification
   - Use WebFetch or research-best-practices agent to fetch: https://github.com/openai/agents.md
   - Goal: Understand the target structure, required sections, and format standards
   - Store structure requirements for later validation
   - Look for: required sections, optional sections, formatting conventions, examples

1.2. If fetch fails or content unclear
   - Try alternative approach: search for cached/local documentation
   - Use Task tool with research-best-practices agent to find agents.md documentation
   - Extract structural requirements from any found documentation

**Step 2: Check Existing agents.md**

2.1. Check if agents.md exists in project root
   - Use Read tool on `./agents.md` (relative to project root)
   - If exists: Store current content for comparison
   - If not exists: Flag as "new creation" mode

**Step 3: Determine Source of Truth**

3.1. Check for CLAUDE.md
   - Use Read tool to check if `./CLAUDE.md` exists
   - If exists: Read its content

3.2. Ask user about CLAUDE.md usage (only if CLAUDE.md exists from Step 3.1)
   - If CLAUDE.md does NOT exist: Skip to Step 4
   - If CLAUDE.md exists: Use AskUserQuestion tool:
     - Question: "A CLAUDE.md file exists in the project. Should this be used as the primary source for agents.md content?"
     - Header: "Source Choice"
     - Options:
       1. "Yes, use CLAUDE.md" - Description: "Use CLAUDE.md as the most recent instruction set"
       2. "No, use other sources" - Description: "Analyze project and use doc/ai-rules.md or standards"
   - Store user's choice

**Step 4: Gather Content Sources**

4.1. Check for project-specific doc/ai-rules.md
   - Use Read tool on `./doc/ai-rules.md`
   - If exists:
     - Store content as PRIMARY content source
     - Flag for deletion at end of process
     - Skip to Step 4.3

4.2. If no project doc/ai-rules.md, check global standards
   - Check if creating new agents.md (from Step 2)
   - If creating new AND (no CLAUDE.md OR Step 3.2 chose "No, use other sources"):
     - Use Read tool on `~/git/cui-llm-rules/standards/ai-rules.md`
     - Store as BASELINE content source
     - **CRITICAL**: Never modify this global standards file

4.3. Analyze project for requirements
   - Use Task tool with Explore agent (thoroughness: "medium")
   - Goal: Understand project architecture, key files, technologies, conventions
   - Look for:
     - Build system (Maven, Gradle, npm, etc.)
     - Project structure and modules
     - Testing frameworks
     - Key technologies and dependencies
     - Coding standards or style guides

**Step 5: Create/Update agents.md**

5.1. Synthesize content from sources
   - Combine information from:
     - CLAUDE.md (if user selected in Step 3.2)
     - doc/ai-rules.md (if present) OR global standards baseline
     - Project analysis results (Step 4.3)
   - Organize according to OpenAI agents.md structure (from Step 1)

5.2. Apply structural standards
   - Follow format from https://github.com/openai/agents.md
   - Ensure all required sections present
   - Remove duplications
   - Maintain clear, concise language
   - Use proper markdown formatting

5.3. Write agents.md
   - If new creation: Use Write tool to create `./agents.md`
   - If update: Use Edit tool to update existing `./agents.md`
   - Ensure content is project-specific and actionable

**Step 6: Review and Validate agents.md**

6.1. Review for quality
   - Read the generated agents.md using Read tool
   - Check against OpenAI structure requirements (Step 1)
   - Verify content is:
     - Concise (no unnecessary verbosity)
     - Correct (factually accurate for this project)
     - Unambiguous (clear instructions/guidelines)
     - Duplication-free (no repeated information)

6.2. Structural validation
   - Verify all required sections from OpenAI spec present
   - Check markdown formatting is valid
   - Ensure proper heading hierarchy
   - Validate links and references

6.3. Content validation
   - Confirm project-specific details are accurate
   - Verify technical information matches project reality
   - Check that guidelines are practical and actionable
   - Ensure no contradictions or conflicts

**Step 7: Cleanup doc/ai-rules.md and References**

7.1. Remove references to doc/ai-rules.md from project files
   - Use Grep tool to search for references: `doc/ai-rules\.md|ai-rules\.md`
   - For each file containing references:
     - If file is `agents.md`: Remove the reference from "Important Files" section
     - If file is `CLAUDE.md`: Update references to point to `agents.md` instead
     - If file is other documentation: Update to reference `agents.md` or remove if not applicable
   - Use Edit tool to update each file
   - Verify all references removed using Grep again

7.2. Remove doc/ai-rules.md file (MANDATORY if exists)
   - **CRITICAL**: If doc/ai-rules.md exists, it MUST be removed after creating/updating agents.md
   - Check if doc/ai-rules.md exists: Use Glob or test command
   - If exists:
     - Use Bash tool to remove: `rm ./doc/ai-rules.md`
     - Verify deletion successful with: `test ! -f ./doc/ai-rules.md`
     - Display: "✅ Removed deprecated doc/ai-rules.md"
   - If does not exist:
     - Display: "ℹ️ No doc/ai-rules.md found (already migrated)"
   - **Rationale**: agents.md is now the single source of truth; doc/ai-rules.md causes confusion and must be removed to complete migration

**Step 8: Commit and Push (if push parameter provided)**

8.1. If push parameter NOT provided
   - Display summary of changes
   - Inform user to review agents.md
   - Exit successfully

8.2. If push parameter provided
   - Invoke commit-changes agent to commit and push:
     - Use Task tool with subagent_type: "commit-changes"
     - Prompt: "Commit all changes with message 'docs: create/update agents.md

     - Generated agents.md following OpenAI agents.md specification
     - Sourced from [list sources used]
     - Removed deprecated doc/ai-rules.md [if existed]
     - Updated references in [list files] to point to agents.md

     agents.md is now the single source of truth for AI agent guidance.', and push"
     - Wait for agent completion
   - Display agent's final report showing commit and push status

### POST-CONDITION VERIFICATION

**Step 9: Verify Success**

9.1. Confirm agents.md exists
   - Use Read tool to verify `./agents.md` is readable
   - Verify file is not empty

9.2. Verify doc/ai-rules.md removal (CRITICAL)
   - Check that `./doc/ai-rules.md` does NOT exist
   - Use: `test ! -f ./doc/ai-rules.md && echo "✅ Confirmed: doc/ai-rules.md removed" || echo "❌ ERROR: doc/ai-rules.md still exists"`
   - If file still exists: Display error and instruct to remove manually
   - This is MANDATORY for migration completion

9.3. Structural correctness check
   - Verify agents.md follows OpenAI structure (from Step 1)
   - Check all required sections present
   - Confirm valid markdown format

9.4. Display completion summary
   - Show what was created/updated
   - List sources used
   - **CRITICAL**: Confirm doc/ai-rules.md was removed (if it existed)
   - List files updated with reference changes (CLAUDE.md, etc.)
   - Confirm structural compliance
   - Verify no references to doc/ai-rules.md remain in project
   - Confirm agents.md is now the single source of truth

## CRITICAL RULES

### File Modification Constraints

- **ALLOWED modifications**:
  - `agents.md` (create or update)
  - `doc/ai-rules.md` (MANDATORY deletion if exists - always remove to complete migration)
  - `CLAUDE.md` (update references from `doc/ai-rules.md` to `agents.md`)
  - Other project documentation files (update references from `doc/ai-rules.md` to `agents.md`)
- **NEVER modify** `~/git/cui-llm-rules/standards/ai-rules.md` (read-only baseline)
- **NEVER create** additional documentation files beyond agents.md
- **ONLY modify** files to update/remove references to `doc/ai-rules.md`
- **CRITICAL**: `doc/ai-rules.md` MUST be removed if it exists (not optional)

### Content Quality Standards

- **ALWAYS ensure** agents.md is concise and focused
- **ALWAYS remove** duplicate or redundant information
- **ALWAYS verify** project-specific details are accurate
- **NEVER include** generic boilerplate unless necessary
- **ALWAYS maintain** clear, unambiguous language

### Structural Compliance

- **ALWAYS follow** OpenAI agents.md structure specification
- **ALWAYS include** all required sections from OpenAI spec
- **ALWAYS use** proper markdown formatting
- **NEVER skip** structural validation (Step 6.2)

### Source Prioritization

- **IF** doc/ai-rules.md exists AND user chooses "No, use other sources": Use as PRIMARY source
- **IF** user selects CLAUDE.md: Use as PRIMARY source
- **IF** no project sources: Use global standards as BASELINE only
- **ALWAYS** combine with project analysis results
- **CRITICAL**: doc/ai-rules.md MUST be deleted if it exists (regardless of whether used as source)

### Pre/Post Condition Enforcement

- **MUST verify** project is git repository before starting
- **MUST confirm** agents.md exists and is structurally correct after completion
- **NEVER proceed** if pre-conditions fail
- **NEVER complete** if post-conditions not met

## Important Notes

1. **OpenAI agents.md Format**: This command follows the OpenAI agents.md specification. Research this format thoroughly at the start of each execution to ensure compliance with latest standards.

2. **Source Hierarchy**: The command uses this source priority:
   - Highest: Local doc/ai-rules.md (if present) or user-selected CLAUDE.md
   - Medium: Project analysis and discovery
   - Baseline: Global standards (only for new creation, never modified)

3. **Cleanup Behavior**: The command ALWAYS removes doc/ai-rules.md if it exists (regardless of whether it was used as a source) and updates all references to doc/ai-rules.md in project files (CLAUDE.md, etc.) to point to agents.md instead. This mandatory deletion is intentional to complete the migration from the old doc/ai-rules.md pattern to the new agents.md pattern. agents.md is now the single source of truth.

4. **Structural Validation**: Always perform thorough structural validation against OpenAI spec. The agents.md must be both structurally compliant AND content-accurate.

5. **Git Integration**: The push parameter provides convenience for automated workflows, but manual review mode (without push) is recommended for first-time creation.

6. **Content Synthesis**: When multiple sources exist (CLAUDE.md + doc/ai-rules.md + project analysis), synthesize intelligently - prefer project-specific details over generic guidelines.

7. **Research Approach**: Use the research-best-practices agent or WebFetch to deeply understand the OpenAI agents.md repository structure. Don't just skim - understand the intent and required sections.
