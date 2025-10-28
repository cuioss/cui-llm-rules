# create-update-agents-md

Creates or updates project-specific agents.md following OpenAI agents.md specification, synthesizes content from multiple sources, and completes migration by removing deprecated doc/ai-rules.md.

## Purpose

Automates agents.md creation/updating by researching OpenAI format specification, analyzing project structure, synthesizing content from CLAUDE.md/doc/ai-rules.md/global standards, validating structure, and cleaning up deprecated files with reference updates.

## Usage

```bash
# Basic execution - creates/updates agents.md
/create-update-agents-md

# Execute and auto-commit/push changes
/create-update-agents-md push
```

## What It Does

The command performs comprehensive agents.md management across 9 steps:

1. **Research OpenAI Format** - Fetch OpenAI agents.md specification for structure requirements
2. **Check Existing** - Read current agents.md if it exists
3. **Determine Source** - Ask user about CLAUDE.md priority (if exists)
4. **Gather Content** - Collect from doc/ai-rules.md, global standards, or project analysis
5. **Create/Update** - Generate agents.md following OpenAI structure
6. **Review & Validate** - Check quality, structure, and content accuracy
7. **Cleanup** - **MANDATORY**: Remove doc/ai-rules.md and update all references
8. **Commit & Push** - If push parameter provided
9. **Verify Success** - Confirm agents.md exists, doc/ai-rules.md removed, structure valid

## Key Features

- **OpenAI Specification Compliance**: Fetches latest OpenAI agents.md structure from https://github.com/openai/agents.md
- **Intelligent Source Synthesis**: Combines CLAUDE.md, doc/ai-rules.md, global standards, and project analysis
- **User Choice for CLAUDE.md**: Asks user if CLAUDE.md should be primary source (if it exists)
- **Project Analysis**: Uses Explore agent for architecture, technologies, and conventions
- **Mandatory Migration**: **ALWAYS** removes doc/ai-rules.md if it exists
- **Reference Updates**: Updates CLAUDE.md and other files to reference agents.md instead
- **Structural Validation**: Verifies all required sections, markdown format, heading hierarchy
- **Content Quality**: Ensures concise, accurate, unambiguous, duplication-free content
- **Git Integration**: Optional push parameter for automated workflows
- **Pre/Post Conditions**: Verifies git repo before, confirms success after

## Parameters

### push (Optional)
- **Format**: `push` (flag)
- **Description**: Automatically commits and pushes changes after successful execution
- **Usage**: `/create-update-agents-md push`
- **Default**: Changes remain uncommitted for manual review

## Pre-Conditions

**Must be true BEFORE execution:**
- Project must be a git repository
- git rev-parse --is-inside-work-tree must succeed

**Error if not met:**
```
❌ ERROR: This command requires the project to be a git repository
```

## Source Hierarchy

The command uses this source priority:

1. **Highest Priority**: User-selected CLAUDE.md OR local doc/ai-rules.md
   - If CLAUDE.md exists: Ask user if it should be primary source
   - If doc/ai-rules.md exists: Use as PRIMARY source (unless user chose CLAUDE.md)

2. **Medium Priority**: Project Analysis
   - Uses Explore agent (medium thoroughness)
   - Discovers: build system, structure, modules, testing, technologies, standards

3. **Baseline Only**: Global Standards
   - Only for NEW creation when no local sources
   - Read from: ~/git/cui-llm-rules/standards/ai-rules.md
   - **NEVER MODIFIED** (read-only reference)

## Content Sources

### CLAUDE.md (if exists)
- **When Used**: User selects "Yes, use CLAUDE.md" in Step 3.2
- **Priority**: Highest (if user chooses)
- **Purpose**: Most recent project-specific instruction set

### doc/ai-rules.md (if exists)
- **When Used**: As PRIMARY source if no CLAUDE.md OR user chooses "No, use other sources"
- **Priority**: Highest (if used)
- **Purpose**: Legacy project-specific AI rules
- **CRITICAL**: **ALWAYS REMOVED** after agents.md creation (mandatory deletion)

### Global Standards
- **When Used**: NEW agents.md creation when no local sources
- **Location**: ~/git/cui-llm-rules/standards/ai-rules.md
- **Priority**: Baseline only
- **Purpose**: Template/starting point
- **NEVER MODIFIED**: Read-only reference

### Project Analysis
- **Always Used**: Combined with all sources
- **Tool**: Explore agent (medium thoroughness)
- **Discovers**:
  - Build system (Maven, Gradle, npm, etc.)
  - Project structure and modules
  - Testing frameworks
  - Key technologies and dependencies
  - Coding standards or style guides

## OpenAI agents.md Structure

### Step 1: Research Format

**Fetch Specification:**
- **Primary**: WebFetch or research-best-practices agent
- **URL**: https://github.com/openai/agents.md
- **Goal**: Understand target structure, required sections, format standards
- **Extract**: Required sections, optional sections, formatting conventions, examples

**If Fetch Fails:**
- Try alternative: search cached/local documentation
- Use research-best-practices agent to find specification

### Step 2: Apply Structure

**Ensure Compliance:**
- All required sections from OpenAI spec present
- Proper markdown formatting
- Correct heading hierarchy
- Valid links and references
- No duplications
- Clear, concise language

## Workflow Detail

### Step 1-2: Research and Check

1. Fetch OpenAI agents.md specification
2. Check if agents.md already exists in project root
3. Store current content if exists (for comparison)

### Step 3: Source Selection

**If CLAUDE.md exists:**
- Ask user: "Should CLAUDE.md be used as primary source?"
- **Option 1**: "Yes, use CLAUDE.md" → Use as most recent instruction set
- **Option 2**: "No, use other sources" → Use doc/ai-rules.md or standards

**If CLAUDE.md does NOT exist:**
- Skip to Step 4 (no user prompt needed)

### Step 4: Content Gathering

**Check local doc/ai-rules.md:**
- If exists: Use as PRIMARY source, flag for deletion
- If not exists: Check global standards (only for new creation)

**Analyze Project:**
- Always run Explore agent (medium thoroughness)
- Understand architecture, technologies, conventions

### Step 5: Create/Update

**Synthesize Content:**
- Combine: CLAUDE.md (if selected) + doc/ai-rules.md (if present) + project analysis
- Organize according to OpenAI structure

**Apply Standards:**
- Follow OpenAI format specification
- Remove duplications
- Maintain clear, concise language
- Use proper markdown formatting

**Write File:**
- If new: Write tool → `./agents.md`
- If update: Edit tool → `./agents.md`

### Step 6: Validation

**Quality Review:**
- Concise (no unnecessary verbosity)
- Correct (factually accurate for project)
- Unambiguous (clear instructions/guidelines)
- Duplication-free (no repeated information)

**Structural Validation:**
- All required sections from OpenAI spec present
- Valid markdown formatting
- Proper heading hierarchy
- Valid links and references

**Content Validation:**
- Project-specific details accurate
- Technical information matches project reality
- Guidelines practical and actionable
- No contradictions or conflicts

### Step 7: Cleanup (CRITICAL)

**7.1 Update References:**
- Search for references: `doc/ai-rules\.md|ai-rules\.md`
- For each file:
  - `agents.md`: Remove from "Important Files" section
  - `CLAUDE.md`: Update to point to `agents.md` instead
  - Other docs: Update or remove reference
- Verify all references removed

**7.2 Remove doc/ai-rules.md (MANDATORY):**
- **CRITICAL**: MUST be removed if it exists
- Check existence with Glob or test command
- If exists:
  - Remove: `rm ./doc/ai-rules.md`
  - Verify: `test ! -f ./doc/ai-rules.md`
  - Display: "✅ Removed deprecated doc/ai-rules.md"
- **Rationale**: agents.md is now single source of truth; doc/ai-rules.md causes confusion

### Step 8: Commit & Push

**If push parameter NOT provided:**
- Display summary of changes
- Inform user to review agents.md
- Exit successfully

**If push parameter provided:**
- Stage agents.md: `git add agents.md`
- Stage removed file: `git add doc/ai-rules.md` (if removed)
- Stage updated files: `git add CLAUDE.md` (if updated)
- Commit with message:
  ```
  docs: create/update agents.md

  - Generated agents.md following OpenAI agents.md specification
  - Sourced from [list sources used]
  - Removed deprecated doc/ai-rules.md [if existed]
  - Updated references in [list files] to point to agents.md

  agents.md is now the single source of truth for AI agent guidance.

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```
- Push to remote: `git push`

### Step 9: Post-Condition Verification

**Confirm Success:**
1. Verify agents.md exists and is readable
2. **CRITICAL**: Verify doc/ai-rules.md does NOT exist
   - Command: `test ! -f ./doc/ai-rules.md && echo "✅ Confirmed" || echo "❌ ERROR"`
   - If still exists: Display error
3. Verify OpenAI structure compliance
4. Confirm all required sections present
5. Validate markdown format

**Display Summary:**
- What was created/updated
- Sources used
- **CRITICAL**: doc/ai-rules.md removal status
- Files updated with reference changes
- Structural compliance confirmation
- Verify no references to doc/ai-rules.md remain
- Confirm agents.md is single source of truth

## File Modification Constraints

### ALLOWED Modifications:
- ✅ `agents.md` (create or update)
- ✅ `doc/ai-rules.md` (**MANDATORY deletion** if exists)
- ✅ `CLAUDE.md` (update references from doc/ai-rules.md to agents.md)
- ✅ Other project docs (update references from doc/ai-rules.md to agents.md)

### NEVER Modify:
- ❌ `~/git/cui-llm-rules/standards/ai-rules.md` (read-only baseline)
- ❌ Additional documentation files beyond agents.md
- ❌ Files unrelated to doc/ai-rules.md references

### CRITICAL:
- **MANDATORY**: doc/ai-rules.md MUST be removed if it exists (not optional)
- **ONLY MODIFY**: Files to update/remove references to doc/ai-rules.md

## Content Quality Standards

### ALWAYS Ensure:
- ✅ agents.md is concise and focused
- ✅ Remove duplicate or redundant information
- ✅ Verify project-specific details are accurate
- ✅ Maintain clear, unambiguous language

### NEVER Include:
- ❌ Generic boilerplate unless necessary
- ❌ Contradictory guidelines
- ❌ Outdated or incorrect information

## Expected Duration

- **New Creation** (no existing agents.md): 2-5 minutes
  - Research OpenAI format: 30-60 sec
  - Content gathering: 60-90 sec
  - Project analysis: 60-90 sec
  - Synthesis and writing: 30-60 sec
  - Validation: 15-30 sec

- **Update** (existing agents.md): 1-3 minutes
  - Format research: 30 sec
  - Content comparison: 30 sec
  - Update and validation: 30-60 sec
  - Cleanup: 15-30 sec

- **With doc/ai-rules.md Migration**: +1-2 minutes
  - Reference updates: 30-60 sec
  - Cleanup verification: 30-60 sec

## Integration

Use this command:
- When initializing new projects
- After significant project changes
- During migration from doc/ai-rules.md to agents.md
- Before committing major changes to CLAUDE.md
- As part of project setup checklist
- When adopting OpenAI agents.md specification

Often used with:
- Project initialization scripts
- CI/CD pipeline setup
- Documentation update workflows
- Standards migration projects

## Continuous Improvement

This command includes a **CONTINUOUS IMPROVEMENT RULE**:

**Every execution should discover and incorporate:**
1. Improved agents.md structure patterns or validation techniques
2. Better methods for extracting project requirements
3. More effective ways to analyze OpenAI agents.md format
4. Enhanced content organization strategies
5. Any lessons learned about agents.md creation/updating

**The command self-evolves** to become more effective with each use.

## Example Output

```
==================================================
create-update-agents-md - Starting
==================================================

Pre-Condition Check:
✅ Project is a git repository

Step 1: Researching OpenAI agents.md Format
Fetching specification from: https://github.com/openai/agents.md
✅ OpenAI format specification retrieved
Required sections identified: 7 sections

Step 2: Checking Existing agents.md
ℹ️ No existing agents.md found - new creation mode

Step 3: Determining Source of Truth
✅ CLAUDE.md found
❓ Use CLAUDE.md as primary source?
User selected: Yes, use CLAUDE.md

Step 4: Gathering Content Sources
✅ CLAUDE.md content loaded (primary source)
🔍 Analyzing project structure...
✅ Project analysis complete:
- Build system: Maven
- Technologies: Java 17, Quarkus, CDI
- Testing: JUnit 5, AssertJ
- Standards: CUI coding standards

Step 5: Creating agents.md
Synthesizing content from:
- CLAUDE.md (primary)
- Project analysis
Applying OpenAI structure...
✅ agents.md created (234 lines)

Step 6: Validating agents.md
✅ Quality check passed (concise, accurate, clear)
✅ Structural validation passed (all required sections)
✅ Content validation passed (project-specific, accurate)

Step 7: Cleanup and Migration
Searching for doc/ai-rules.md references...
✅ Found 2 references in CLAUDE.md
✅ Updated CLAUDE.md to reference agents.md
❌ doc/ai-rules.md not found (already migrated)

Step 8: Commit & Push
✅ Staged agents.md
✅ Staged CLAUDE.md
✅ Committed: "docs: create agents.md"
✅ Pushed to remote

Step 9: Post-Condition Verification
✅ agents.md exists and is readable
✅ Confirmed: doc/ai-rules.md removed (was already migrated)
✅ OpenAI structure compliance verified
✅ All required sections present
✅ Valid markdown format

==================================================
create-update-agents-md - Success!
==================================================

Summary:
- Created: agents.md (234 lines)
- Sources: CLAUDE.md (primary) + Project analysis
- Migration: doc/ai-rules.md was already migrated
- References updated: CLAUDE.md (2 updates)
- Structural compliance: ✅ Passed
- Single source of truth: agents.md

Next steps:
1. Review agents.md in your editor
2. Verify content accuracy for your project
3. agents.md is now the authoritative AI guidance document
```

## Notes

- **OpenAI Specification**: Always fetches latest format from https://github.com/openai/agents.md
- **Source Priority**: CLAUDE.md (if selected) > doc/ai-rules.md > global standards baseline
- **Mandatory Migration**: doc/ai-rules.md MUST be removed if it exists (completes migration)
- **Reference Updates**: All references to doc/ai-rules.md automatically updated to agents.md
- **Structural Validation**: Ensures compliance with OpenAI agents.md specification
- **Project Analysis**: Uses Explore agent for architecture discovery
- **Git Integration**: Optional push parameter for automated workflows
- **Manual Review**: Recommended for first-time creation (no push)
- **Continuous Improvement**: Command self-evolves with each execution
- **Single Source of Truth**: agents.md replaces doc/ai-rules.md entirely

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
