# Slash Command Creation Wizard

Guide users through creating a new, well-structured slash command with a comprehensive questionnaire.

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

#### Question 2.1: Command Location
```
[Question 1/11] Where should the command be located?

1. Global command (~/.claude/commands/)
   - Available in all projects
   - Use for general-purpose commands
   - Examples: docs-adoc, handle-pull-request, verify-plantuml-diagrams

2. Project command (.claude/commands/)
   - Available only in this project
   - Use for project-specific workflows
   - Examples: verify-all, verify-integration-tests

Enter 1 or 2:
```

Store response as `location` (global or project).

#### Question 2.2: Command Name
```
[Question 2/11] What is the command name?

- Use lowercase with hyphens (e.g., verify-project, handle-pull-request)
- Should be descriptive and concise
- Must be unique (not conflict with existing commands)

Command name (without leading slash):
```

Store response as `command_name`.
Validate: No spaces, lowercase, hyphens only, doesn't already exist.

#### Question 2.3: Command Description
```
[Question 3/11] Provide a brief description of the command.

This will appear at the top of the command file.
Be concise but descriptive (1-2 sentences).

Description:
```

Store response as `description`.

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
- /verify-project push
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
- plantuml_dir=<path> (verify-plantuml-diagrams)

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
- verify-project: Stores last execution duration, acceptable warnings
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
   - Examples: verify-project, verify-all

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

1. **Title and Description**
   ```markdown
   # {CommandName} Command

   {description}
   ```

2. **CONTINUOUS IMPROVEMENT RULE** (if include_continuous_improvement is true)
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

3. **PARAMETERS Section**
   - Document all parameters (push + custom)
   - Include examples

4. **PARAMETER VALIDATION Section**
   - Validation logic for each parameter
   - Handle all combinations

5. **WORKFLOW INSTRUCTIONS Section**
   - Structure workflow_description into numbered steps
   - Add substeps as needed
   - Include decision points
   - Add loop markers if execution_model is conditional/loop
   - **PRE-CONDITIONS**: If pre_conditions provided, add verification step BEFORE main workflow
   - **POST-CONDITIONS**: If post_conditions provided, add verification step AFTER main workflow

6. **State Management Steps** (if state_config provided)
   - Step for reading .claude/run-configuration.md
   - Step for updating .claude/run-configuration.md

7. **CRITICAL RULES Section**
   - Best practices from similar commands
   - Specific rules for this command's domain
   - **CONSTRAINTS**: Incorporate critical_constraints as NEVER/MUST NOT rules
   - **PRE-CONDITIONS**: List as requirements that must be checked
   - **POST-CONDITIONS**: List as guarantees/success criteria

8. **Example .claude/run-configuration.md Structure** (if state_config provided)

9. **Usage Examples**

10. **Important Notes** (if applicable)

**Apply these structural patterns from existing commands:**

From `verify-project`:
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

1. Determine full path:
   - If global: `~/.claude/commands/{command_name}.md`
   - If project: `.claude/commands/{command_name}.md`

2. Generate content with proper structure

3. Write file using Write tool

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
2. Running /slash-doctor to verify command structure...

╚════════════════════════════════════════════════════════════
```

### Step 10: Auto-Verify with Slash Doctor

1. Automatically invoke `/slash-doctor {command_name}`
2. Wait for slash-doctor to complete analysis
3. If issues found, offer to fix them immediately

```
Slash Doctor Analysis Results:
- Issues found: {count}
- Critical: {critical_count}
- Warnings: {warning_count}
- Suggestions: {suggestion_count}

Would you like to review and fix these issues now?
1. Yes - Review with slash-doctor
2. No - I'll review manually later

Enter 1 or 2:
```

If yes, the slash-doctor analysis will continue in interactive mode.

### Step 11: Final Completion

```
╔════════════════════════════════════════════════════════════╗
║          Setup Complete!                                   ║
╔════════════════════════════════════════════════════════════╝

Your new command is ready: /{command_name}

To use it:
/{command_name} {example with parameters}

The command follows best practices from existing commands:
✅ Proper structure and sections
✅ Clear parameter validation
✅ Comprehensive workflow steps
✅ Appropriate critical rules
✅ Verified by slash-doctor

Happy coding! 🚀

╚════════════════════════════════════════════════════════════
```

## CRITICAL RULES

- **ALWAYS collect ALL information** before generating the command
- **NEVER skip validation** of command name and location
- **ALWAYS check for existing commands** to avoid conflicts
- **USE patterns from existing commands** - don't reinvent structures
- **ALWAYS run slash-doctor** after creation to verify quality
- **PROVIDE clear examples** in parameters and usage sections
- **STRUCTURE workflows** with proper numbering and substeps
- **INCLUDE state management** only if genuinely needed
- **APPLY anti-bloat principles** - concise but complete
- **USE proper markdown formatting** - consistent with existing commands

## PATTERN MATCHING GUIDE

When generating command structure, match patterns from similar commands:

**Verification Commands** (verify-project, verify-integration-tests):
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

Simply invoke: `/slash-create`

The wizard will guide you through all questions.
