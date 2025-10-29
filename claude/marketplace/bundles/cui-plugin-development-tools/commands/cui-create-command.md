---
name: cui-create-command
description: Guide users through creating a new well-structured slash command with comprehensive questionnaire
---

# Slash Command Creation Wizard

Guide users through creating a new, well-structured slash command with a comprehensive questionnaire.

## PARAMETERS

- **scope=marketplace** (default): Create command in marketplace bundle (~/git/cui-llm-rules/claude/marketplace/bundles/)
- **scope=global**: Create command in global location (~/.claude/commands/)
- **scope=project**: Create command in project location (.claude/commands/)

## PARAMETER VALIDATION

**If `scope=marketplace` (default):**
- Work in: `~/git/cui-llm-rules/claude/marketplace/bundles/`
- Prompt for bundle name (or create new bundle)
- Command file location: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/commands/{command_name}.md`

**If `scope=global`:**
- Work in: `~/.claude/commands/`
- No bundle structure (flat directory)
- Command file location: `~/.claude/commands/{command_name}.md`

**If `scope=project`:**
- Work in: `.claude/commands/`
- No bundle structure (flat directory)
- Command file location: `.claude/commands/{command_name}.md`

## WORKFLOW INSTRUCTIONS

### Step 1: Display Welcome and Overview

Display:
```
╔════════════════════════════════════════════════════════════╗
║          Slash Command Creation Wizard                     ║
╔════════════════════════════════════════════════════════════╝
║
║ This wizard will guide you through creating a new slash
║ command with proper structure, parameters, and workflow.
║
║ You'll answer questions about:
║ - Command location and basic info
║ - Continuous improvement rule
║ - Parameters and validation
║ - State management
║ - Workflow structure
║ - Essential documentation
║ - Critical constraints and conditions
║
║ Let's begin!
║
╚════════════════════════════════════════════════════════════

Ready to start? Enter 'y' to continue:
```

Wait for user acknowledgment (any input will proceed).

### Step 2: Collect Basic Information

#### Step 2.1: Determine Scope and Location

Parse the `scope` parameter (defaults to "marketplace"):

**If scope=marketplace:**
- Set `location` = "marketplace"
- Set `base_path` = "~/git/cui-llm-rules/claude/marketplace/bundles/"
- Prompt for bundle name:
  ```
  Which bundle should contain this command?

  Existing bundles:
  - cui-utility-commands (project utilities)
  - cui-plugin-development-tools (plugin/command/agent creation)
  - cui-pull-request-workflow (PR management)
  - cui-issue-implementation (issue planning and implementation)
  - cui-documentation-standards (documentation review)
  - cui-project-quality-gates (build and quality checks)

  Enter bundle name or "new" to create a new bundle:
  ```
  Store response as `bundle_name`.

**If scope=global:**
- Set `location` = "global"
- Set `base_path` = "~/.claude/commands/"
- No bundle (flat structure)
- Set `bundle_name` = "" (empty)

**If scope=project:**
- Set `location` = "project"
- Set `base_path` = ".claude/commands/"
- No bundle (flat structure)
- Set `bundle_name` = "" (empty)

#### Step 2.2: Command Name
```
[Question 2/11] What is the command name?

- Use lowercase with hyphens (e.g., build-and-verify, handle-pull-request)
- Should be descriptive and concise
- Must be unique (not conflict with existing commands)

Command name (without leading slash):
```

Store response as `command_name`.
Validate: No spaces, lowercase, hyphens only, doesn't already exist.

#### Question 2.3: Command Description
```
[Question 3/11] Provide a brief description of the command.

This will appear in the YAML frontmatter and is required for command discovery.
Be concise but descriptive (1-2 sentences, max 100 characters).

Description:
```

Store response as `description`.
Validate: Length <= 100 characters for frontmatter compatibility.

#### Question 2.4: Continuous Improvement Rule

```
[Question 4/11] Continuous Improvement Rule

Should this command include a CONTINUOUS IMPROVEMENT RULE section?

This rule instructs the AI to update the command file when discovering
better approaches during execution.

Examples of commands with this rule:
- handle-pull-request: Evolves based on API usage discoveries
- docs-adoc: Improves based on validation patterns found

Recommended for:
- Commands that interact with external APIs
- Commands that discover edge cases during execution
- Commands that may need workflow refinements over time

NOT recommended for:
- Simple, stable workflows (e.g., basic file operations)
- Commands with fixed, deterministic steps
- Commands that orchestrate other commands without own logic

Should this command include the CONTINUOUS IMPROVEMENT RULE?

1. Yes - Include the rule (command will self-improve)
2. No - Skip the rule (command is stable/deterministic)

Enter 1 or 2:
```

Store response as `include_continuous_improvement` (boolean).

### Step 3: Collect Parameter Information

#### Question 3.1: Include Standard Parameters

```
[Question 5/11] Standard Parameters

Many commands support the "push" parameter to auto-commit and push changes.

Examples from existing commands:
- /build-and-verify push
- /handle-pull-request create
- /docs-adoc file=path/to/file.adoc push

Should this command support the "push" parameter?
(Automatically commits and pushes changes after successful execution)

1. Yes - Include push parameter
2. No - Skip push parameter

Enter 1 or 2:
```

Store response as `include_push` (boolean).

#### Question 3.2: Custom Parameters

```
[Question 6/11] Custom Parameters

Does this command need custom parameters?

Examples:
- file=<path> (docs-adoc)
- url=<github-url> (handle-pull-request)
- plantuml_dir=<path> (verify-architecture-diagrams)

1. Yes - Add custom parameters
2. No - No custom parameters needed

Enter 1 or 2:
```

If yes, collect for EACH parameter:
```
Parameter #{n}:

Name (without prefix, e.g., "file" not "file="):
```

```
Is this parameter required or optional?

1. Required - Must be provided
2. Optional - Has a default or can be omitted

Enter 1 or 2:
```

```
Description (what does this parameter do?):
```

```
Does this parameter have a default value?

1. Yes - Specify default value
2. No - No default value

Enter 1 or 2:
```

If yes:
```
Default value:
```

```
Validation rules (e.g., "must be .adoc file", "must be GitHub URL"):
```

```
Add another parameter?
1. Yes
2. No

Enter 1 or 2:
```

Store all parameters in `custom_parameters` array.

### Step 4: State Management Configuration

#### Question 4.1: State Persistence

```
[Question 7/11] State Management in .claude/run-configuration.md

Many commands persist state/configuration in .claude/run-configuration.md.

Examples:
- build-and-verify: Stores last execution duration, acceptable warnings
- handle-pull-request: Stores CI/Sonar duration
- docs-adoc: Stores skipped files, acceptable warnings

Should this command use .claude/run-configuration.md for state persistence?

1. Yes - Use .claude/run-configuration.md
2. No - No state persistence needed

Enter 1 or 2:
```

If yes:
```
What aspects should be persisted? (Select all that apply)

1. Execution duration (track how long command takes)
2. Acceptable warnings (warnings user approved to ignore)
3. Skipped items (files/resources to skip)
4. Configuration values (other settings)
5. Done selecting

Enter numbers separated by spaces (e.g., "1 2 5"):
```

Store selections in `state_config` object.

### Step 5: Essential Documentation

#### Question 5.1: Required Reading

```
[Question 8/11] Essential Documentation

Should users read specific documentation before the command executes?

Examples:
- docs-adoc reads: asciidoc-standards.adoc
- Commands may read: project standards, API docs, style guides

1. Yes - Specify documents to read
2. No - No required reading

Enter 1 or 2:
```

If yes, collect for EACH document:
```
Document #{n}:

Path (absolute or relative to project root):
```

```
What should be extracted/understood from this document?
```

```
Add another document?
1. Yes
2. No

Enter 1 or 2:
```

Store in `required_docs` array.

### Step 6: Workflow Structure

#### Question 6.1: Step Execution Model

```
[Question 9/11] Workflow Execution Model

How should the command's workflow steps be executed?

1. Strict Sequential
   - Steps execute one at a time in order
   - Each step completes before next begins
   - Use for: verification workflows, builds
   - Examples: build-and-verify, verify-all

2. Parallel Execution
   - Some steps can run concurrently
   - Speeds up independent operations
   - Use for: analysis tasks, multi-file processing
   - Examples: analyzing multiple files at once

3. Conditional/Loop
   - Steps may repeat or branch based on results
   - Use for: fix-verify cycles, iterative processing
   - Examples: handle-pull-request (loop until Sonar clean)

Enter 1, 2, or 3:
```

Store response as `execution_model`.

### Step 7: Define Command Workflow

#### Question 7.1: Workflow Steps

```
[Question 10/11] Define Workflow Steps

Now describe the actual workflow this command should execute.

Be as detailed as possible. For each step, describe:
- What the step does
- What tools/commands it uses
- What it checks/validates
- What happens on success/failure
- Whether it loops or branches

You can provide this in free-form text. I'll structure it into
proper workflow steps based on best practices from existing commands.

Describe the workflow:
```

Store response as `workflow_description`.

#### Question 7.2: Critical Constraints and Conditions

```
[Question 11/11] Critical Constraints and Conditions

To ensure robust command execution, define the constraints and conditions:

CRITICAL CONSTRAINTS (What must NOT happen):
- What are the absolute limitations?
- What operations are forbidden?
- What states are invalid?
- What would cause unrecoverable failure?

Examples:
- NEVER remove files without user approval
- NEVER push to main without testing
- NEVER skip error fixes
- MUST NOT proceed if build fails

Your critical constraints:
```

Store response as `critical_constraints`.

```
PRE-CONDITIONS (What must be true BEFORE execution):
- What state must exist before the command runs?
- What files/resources must be available?
- What tools must be installed?
- What permissions are required?

Examples:
- Project must be a git repository
- Maven must be installed and in PATH
- File specified in parameter must exist
- User must have write permissions

Your pre-conditions:
```

Store response as `pre_conditions`.

```
POST-CONDITIONS (What must be true AFTER execution):
- What guarantees does the command provide?
- What state should exist after success?
- What artifacts should be created?
- What verifications prove success?

Examples:
- All tests must pass (0 failures)
- Build artifacts must exist in target/
- No uncommitted changes remain (if push parameter used)
- Documentation is updated to reflect changes

Your post-conditions:
```

Store response as `post_conditions`.

### Step 8: Generate Command Structure

Based on collected information, generate the command file with proper structure:

**Components to include:**

1. **YAML Frontmatter** (REQUIRED - MUST be first)
   ```yaml
   ---
   name: {command_name}
   description: {description}
   ---
   ```
   **CRITICAL**: This frontmatter is REQUIRED for command discovery by Claude Code.
   Without it, the command will not appear in the command palette.

2. **Title and Description**
   ```markdown
   # {CommandName} Command

   {description}
   ```

3. **CONTINUOUS IMPROVEMENT RULE** (if include_continuous_improvement is true)
   ```markdown
   ## CONTINUOUS IMPROVEMENT RULE

   **CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** with:
   1. The improved method/approach
   2. Updated commands or validation techniques
   3. Better examples or clarifications
   4. Any lessons learned

   This ensures the command evolves and becomes more effective with each execution.
   ```
   Customize the list items to match the command's domain (e.g., for API commands mention "API endpoints, data formats"; for validation commands mention "validation patterns, edge cases").

4. **PARAMETERS Section**
   - Document all parameters (push + custom)
   - Include examples

5. **PARAMETER VALIDATION Section**
   - Validation logic for each parameter
   - Handle all combinations

6. **WORKFLOW INSTRUCTIONS Section**
   - Structure workflow_description into numbered steps
   - Add substeps as needed
   - Include decision points
   - Add loop markers if execution_model is conditional/loop
   - **PRE-CONDITIONS**: If pre_conditions provided, add verification step BEFORE main workflow
   - **POST-CONDITIONS**: If post_conditions provided, add verification step AFTER main workflow

7. **State Management Steps** (if state_config provided)
   - Step for reading .claude/run-configuration.md
   - Step for updating .claude/run-configuration.md

8. **CRITICAL RULES Section**
   - Best practices from similar commands
   - Specific rules for this command's domain
   - **CONSTRAINTS**: Incorporate critical_constraints as NEVER/MUST NOT rules
   - **PRE-CONDITIONS**: List as requirements that must be checked
   - **POST-CONDITIONS**: List as guarantees/success criteria

9. **Example .claude/run-configuration.md Structure** (if state_config provided)

10. **Usage Examples**

11. **Important Notes** (if applicable)

**Apply these structural patterns from existing commands:**

From `build-and-verify`:
- Clear step numbering (Step 1, Step 2, etc.)
- Timeout calculation with safety margin
- Loop back instructions
- Duration update logic (>10% threshold)

From `handle-pull-request`:
- Conditional step execution markers
- Loop point labeling
- User prompt patterns
- Comprehensive final report

From `docs-adoc`:
- Detailed substep breakdown (Step 4.1, 4.2, etc.)
- User decision points with options
- Acceptable warnings pattern
- File skipping pattern

From `verify-all`:
- Orchestrator pattern (if command coordinates others)
- Duration estimation display
- Comprehensive summary report

**File Generation:**

1. Determine full path based on scope:
   - If scope=marketplace: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/commands/{command_name}.md`
   - If scope=global: `~/.claude/commands/{command_name}.md`
   - If scope=project: `.claude/commands/{command_name}.md`

2. If scope=marketplace and bundle doesn't exist:
   - Create bundle directory structure: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/`
   - Create subdirectories: `commands/`, `agents/`, `skills/`
   - Create `.claude-plugin/plugin.json` with minimal structure (see bundling-architecture.adoc)
   - Create bundle README.md

3. Generate content with proper structure (MUST start with YAML frontmatter)

4. Write file using Write tool

5. Verify frontmatter is present and valid

### Step 9: Display Creation Summary

```
╔════════════════════════════════════════════════════════════╗
║          Command Created Successfully!                     ║
╔════════════════════════════════════════════════════════════╝

Command: /{command_name}
Location: {full_path}
Length: {line_count} lines

Parameters:
{list all parameters}

Continuous Improvement Rule: {Yes or No based on include_continuous_improvement}

State Management:
{describe state_config or "None"}

Execution Model: {execution_model}

Required Docs:
{list required_docs or "None"}

Constraints & Conditions:
- Critical Constraints: {count or "None"}
- Pre-conditions: {count or "None"}
- Post-conditions: {count or "None"}

Next Steps:
1. Review the generated command at: {full_path}
2. Running /diagnose-commands to verify command structure...

╚════════════════════════════════════════════════════════════
```

### Step 10: Auto-Verify with Slash Doctor

1. Automatically invoke `/diagnose-commands {command_name}`
2. Wait for diagnose-commands to complete analysis
3. If issues found, offer to fix them immediately

```
Slash Doctor Analysis Results:
- Issues found: {count}
- Critical: {critical_count}
- Warnings: {warning_count}
- Suggestions: {suggestion_count}

Would you like to review and fix these issues now?
1. Yes - Review with diagnose-commands
2. No - I'll review manually later

Enter 1 or 2:
```

If yes, the diagnose-commands analysis will continue in interactive mode.

### Step 11: Final Completion

```
╔════════════════════════════════════════════════════════════╗
║          Setup Complete!                                   ║
╔════════════════════════════════════════════════════════════╝

Your new command is ready: /{command_name}

To use it:
/{command_name} {example with parameters}

The command follows best practices from existing commands:
✅ YAML frontmatter for command discovery
✅ Proper structure and sections
✅ Clear parameter validation
✅ Comprehensive workflow steps
✅ Appropriate critical rules
✅ Verified by diagnose-commands

Happy coding! 🚀

╚════════════════════════════════════════════════════════════
```

## CRITICAL RULES

- **ALWAYS include YAML frontmatter** as the FIRST element in the file (required for command discovery)
- **ALWAYS collect ALL information** before generating the command
- **NEVER skip validation** of command name and location
- **ALWAYS check for existing commands** to avoid conflicts
- **USE patterns from existing commands** - don't reinvent structures
- **ALWAYS run diagnose-commands** after creation to verify quality
- **PROVIDE clear examples** in parameters and usage sections
- **STRUCTURE workflows** with proper numbering and substeps
- **INCLUDE state management** only if genuinely needed
- **APPLY anti-bloat principles** - concise but complete
- **USE proper markdown formatting** - consistent with existing commands
- **DEFAULT to marketplace scope** (scope=marketplace is default)
- **VERIFY frontmatter syntax** is valid YAML with name and description fields

## PATTERN MATCHING GUIDE

When generating command structure, match patterns from similar commands:

**Verification Commands** (build-and-verify, verify-integration-tests):
- Execution duration tracking
- Acceptable warnings pattern
- Maven build with timeout
- Loop on fixes
- Post-verification step

**Documentation Commands** (docs-adoc):
- File processing loop
- Skipped files pattern
- Multiple validation tools
- User prompts for decisions
- Detailed substeps

**Orchestrator Commands** (verify-all):
- Serial execution emphasis
- Duration estimation
- Comprehensive final report
- No state modification

**Integration Commands** (handle-pull-request):
- Conditional loops
- External service interaction
- Multi-phase workflow
- User approval gates

## VALIDATION RULES

Before writing the command file:

1. **Name Validation:**
   - Lowercase only
   - Hyphens for spaces
   - No special characters
   - Unique (doesn't exist)
   - Descriptive and concise

2. **Parameter Validation:**
   - No duplicate parameter names
   - Clear validation rules
   - Reasonable defaults
   - Proper examples

3. **Workflow Validation:**
   - All steps numbered
   - Decision points defined
   - Error handling included
   - Success criteria clear

4. **Structure Validation:**
   - All required sections present
   - Proper markdown formatting
   - Consistent style
   - No typos in section headers

## USAGE

**Create command in marketplace (default):**
```
/cui-create-command
/cui-create-command scope=marketplace
```

**Create global command:**
```
/cui-create-command scope=global
```

**Create project-local command:**
```
/cui-create-command scope=project
```

The wizard will guide you through all questions.
