# create-command

Interactive wizard that guides users through creating well-structured slash commands by asking 11 questions about location, parameters, state management, workflow structure, and critical constraints.

## Purpose

Simplifies slash command creation by providing a questionnaire-based approach that ensures all essential sections, proper structure, parameter validation, and comprehensive documentation are included.

## Usage

```bash
# Launch interactive wizard
/create-command
```

## What It Does

The wizard guides you through 11 questions in 6 categories:

1. **Basic Information** (Q1-4):
   - Command location (global vs project)
   - Command name
   - Description
   - Continuous improvement rule

2. **Parameter Configuration** (Q5-6):
   - Standard "push" parameter
   - Custom parameters

3. **State Management** (Q7):
   - Run configuration persistence
   - User decision tracking

4. **Workflow Structure** (Q8):
   - Step count and organization
   - Decision points

5. **Essential Documentation** (Q9-10):
   - Usage examples
   - Critical rules

6. **Constraints** (Q11):
   - Pre-conditions
   - Post-conditions
   - Anti-patterns

After collecting answers, the wizard generates a complete command file with:
- Proper structure and sections
- PARAMETERS section (if applicable)
- PARAMETER VALIDATION section
- WORKFLOW INSTRUCTIONS with numbered steps
- CRITICAL RULES section
- Usage examples
- Integration notes

## Key Features

- **Interactive Questionnaire**: 11 guided questions covering all aspects
- **Location Choice**: Global (~/.claude/commands/) or project (.claude/commands/)
- **Continuous Improvement Support**: Optional self-evolution rule
- **Standard Parameter**: "push" parameter for auto-commit/push
- **Custom Parameters**: Flexible parameter definition
- **State Persistence**: Run configuration tracking
- **Workflow Templating**: Generates numbered steps with decision points
- **Documentation Generation**: Creates examples and critical rules
- **Validation**: Checks command name uniqueness and format
- **File Creation**: Writes complete command file to correct location

## Question Breakdown

### Q1: Command Location

**Options:**
1. **Global** (~/.claude/commands/)
   - Available in all projects
   - Use for general-purpose commands
   - Examples: docs-adoc, handle-pull-request

2. **Project** (.claude/commands/)
   - Available only in this project
   - Use for project-specific workflows
   - Examples: verify-all, verify-integration-tests

### Q2: Command Name

**Requirements:**
- Lowercase with hyphens (e.g., build-and-verify, handle-pull-request)
- Descriptive and concise
- Unique (no conflicts with existing commands)
- No spaces, underscores only hyphens

**Validation:**
- Format check (lowercase, hyphens only)
- Existence check (doesn't already exist)

### Q3: Command Description

**Requirements:**
- Brief (1-2 sentences)
- Concise but descriptive
- Appears at top of command file

### Q4: Continuous Improvement Rule

**When to Include:**
- Commands that interact with external APIs
- Commands that discover edge cases during execution
- Commands that may need workflow refinements

**When to Skip:**
- Simple, stable workflows
- Fixed, deterministic steps
- Commands that orchestrate other commands

**Examples with Rule:**
- handle-pull-request - Evolves based on API usage
- docs-adoc - Improves based on validation patterns

### Q5: Standard "push" Parameter

**Purpose**: Automatically commit and push changes after successful execution

**Examples:**
- `/build-and-verify push`
- `/handle-pull-request create`
- `/docs-adoc file=path/to/file.adoc push`

**When to Include:**
- Commands that modify files
- Commands with clear success criteria
- Commands where auto-push makes sense

### Q6: Custom Parameters

**Examples:**
- `file=<path>` - Target file path
- `project=<name>` - Project selection
- `dry-run` - Preview mode
- `auto-fix` - Automatic fixes

**Information Collected:**
- Parameter names
- Types (string, boolean, path, number)
- Descriptions
- Whether required or optional

### Q7: Run Configuration

**Purpose**: Persist user decisions and state across runs

**Examples:**
- Approved suspicious permissions
- Domain security research results
- Previous workflow choices

**Storage**: `.claude/run-configuration.md`

**When to Use:**
- Commands that prompt for security decisions
- Commands with user approval workflows
- Commands that learn from previous runs

### Q8: Workflow Structure

**Information Collected:**
- Number of main workflow steps
- Whether steps have decision points
- Complexity level (simple/moderate/complex)

**Generated Structure:**
- Numbered steps (Step 1, Step 2, ...)
- Decision point templates
- Error handling sections
- Success/failure criteria

### Q9: Usage Examples

**Purpose**: Show users how to invoke the command

**Generated Examples:**
- Basic invocation
- With parameters
- Common use cases
- Edge cases

### Q10: Critical Rules

**Purpose**: Highlight constraints and important patterns

**Examples:**
- Tool usage order (Read before Edit/Write)
- Sequential vs parallel execution
- Safety limits (max retries)
- State management requirements

### Q11: Pre/Post Conditions

**Pre-Conditions:**
- What must be true before running
- Required tools/files/permissions
- Environment requirements

**Post-Conditions:**
- What will be true after success
- Verification checks
- Cleanup requirements

**Anti-Patterns:**
- What to avoid
- Common mistakes
- Security concerns

## Generated File Structure

```markdown
# <Command Name>

<Description>

## CONTINUOUS IMPROVEMENT RULE
[If included]

## PARAMETERS
[If command has parameters]

## PARAMETER VALIDATION
[If command has parameters]

## WORKFLOW INSTRUCTIONS

### Step 1: <First Step>
...

### Step N: <Final Step>
...

## CRITICAL RULES
- Important constraints
- Safety patterns
- Tool usage requirements

## USAGE EXAMPLES

### Example 1: <Basic Usage>
...

### Example N: <Advanced Usage>
...

## PRE-CONDITIONS
- Required environment
- Dependencies
- Permissions

## POST-CONDITIONS
- Expected state
- Verification
- Cleanup

## ANTI-PATTERNS
- What to avoid
- Common mistakes

## NOTES
- Integration points
- Performance expectations
- Known limitations
```

## Expected Duration

- **Question Phase**: 3-5 minutes
  - 11 questions with explanations
  - Some questions may prompt for additional details

- **Generation Phase**: 5-10 seconds
  - File structure creation
  - Content generation
  - File writing

- **Total**: 3-6 minutes

## Integration

Use this command:
- When creating new slash commands
- To ensure consistent command structure
- To avoid forgetting critical sections
- To standardize parameter handling
- Before manually writing command files

Often used with:
- `/diagnose-commands` - Verify generated command quality
- Manual editing - Refine generated template

## Example Session

```
╔════════════════════════════════════════════════════════════╗
║          Slash Command Creation Wizard                     ║
╔════════════════════════════════════════════════════════════╝

[Question 1/11] Where should the command be located?
1. Global command (~/.claude/commands/)
2. Project command (.claude/commands/)
Enter 1 or 2: 1

[Question 2/11] What is the command name?
Command name (without leading slash): verify-coverage

[Question 3/11] Provide a brief description.
Description: Verifies test coverage meets project thresholds and generates reports.

[Question 4/11] Continuous Improvement Rule
Should this command include the CONTINUOUS IMPROVEMENT RULE?
1. Yes - Include the rule
2. No - Skip the rule
Enter 1 or 2: 2

[Question 5/11] Standard Parameters
Should this command support the "push" parameter?
1. Yes - Include push parameter
2. No - Skip push parameter
Enter 1 or 2: 1

[Question 6/11] Custom Parameters
Does this command need custom parameters?
1. Yes - Define custom parameters
2. No - Only standard parameters
Enter 1 or 2: 1

Parameter 1 name: threshold
Parameter 1 type (string/boolean/path/number): number
Parameter 1 description: Minimum coverage percentage (default: 80)
Required or optional? (r/o): o

Add another parameter? (y/n): n

[Question 7/11] Run Configuration
Should this command persist state across runs?
1. Yes - Use .claude/run-configuration.md
2. No - Stateless command
Enter 1 or 2: 2

[Question 8/11] Workflow Structure
How many main workflow steps? 4

Do workflow steps have decision points requiring user input?
(y/n): n

[Question 9/11] Usage Examples
Provide example command invocations (one per line, empty line to finish):
Example 1: /verify-coverage
Example 2: /verify-coverage threshold=90
Example 3: /verify-coverage push
Example 4:

[Question 10/11] Critical Rules
List critical constraints or requirements (one per line, empty line to finish):
Rule 1: Must run after tests complete
Rule 2: Uses project's coverage tool (JaCoCo, Coverage.py, etc.)
Rule 3:

[Question 11/11] Pre/Post Conditions
Pre-conditions (comma-separated): Tests executed, coverage data available
Post-conditions (comma-separated): Coverage report generated, thresholds verified
Anti-patterns (comma-separated): Running before tests, modifying source during check

────────────────────────────────────────────────────

Generating command file...

✅ Command created: ~/.claude/commands/verify-coverage.md
✅ Structure verified
✅ All sections present

Next steps:
1. Review the generated command file
2. Customize workflow steps with specific implementation
3. Run /diagnose-commands verify-coverage to validate
4. Test the command with sample data
```

## Notes

- **Template Generation**: Creates skeleton, requires manual refinement
- **Workflow Steps**: Wizard provides structure, you add implementation details
- **Parameter Validation**: Basic validation generated, may need customization
- **Interactive Only**: No parameters, runs in wizard mode
- **File Overwrite**: Warns if command file already exists
- **Validation Built-in**: Checks name format and uniqueness
- **Post-Wizard**: Always run /diagnose-commands to verify generated command

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
