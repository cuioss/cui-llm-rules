# Cascade Commands

## Purpose
Defines all available Cascade commands and their usage patterns.

## Important Note
All commands prefixed with `cp:` are AI assistant commands and must NEVER be executed in a shell. These commands are exclusively for communication with the AI assistant and are processed internally by the AI system.

## Related Documentation
- [Command Prompt Interface](commands/core/cp.md): Command prompt interface
- [Documentation Management](documentation-management.md): Documentation management
- [Documentation Standards](../core/standards/documentation-standards.md): Documentation standards

## Command Categories

### 1. Core Commands 
- `[1] cp: list` - Command prompt interface
  * Lists all available commands
  * Interactive command selection
  * Command execution management
  * Documentation: [Command Prompt Interface](commands/core/cp.md)

### 2. Java Maintenance Commands
- `[2] cp: maintenance java prepare`
  * Creates feature branch
  * Performs initial verification
  * Sets up maintenance context
  * Documentation: [Java Process](../maintenance/java/process.md)

- `[3] cp: maintenance java perform`
  * Updates dependencies
  * Applies code cleanup
  * Improves code quality
  * Documentation: [Java Process](../maintenance/java/process.md)

- `[4] cp: maintenance java finalize`
  * Runs OpenRewrite recipes
  * Verifies build stability
  * Prepares pull request
  * Documentation: [Java Process](../maintenance/java/process.md)

- `[5] cp: fix javadoc`
  * Fixes Javadoc errors and warnings
  * Makes minimal modifications
  * Preserves content
  * Documentation: [Java Process](../maintenance/java/process.md)

### 3. Memory Management Commands
- `[6] cp: commit llm-rules to memory` *(AI Assistant Command)*
  * One-time transfer from @llm-rules to AI memory
  * Creates/updates AI assistant memories
  * Establishes memory source of truth
  * Documentation: [Memory Commit](commands/memory/commit.md)

- `[7] cp: persist memory to llm-rules` *(AI Assistant Command)*
  * Updates @llm-rules from AI memories
  * Maintains documentation structure
  * Ensures completeness
  * Documentation: [Memory Persist](commands/memory/persist.md)

### 4. Quality Assurance Commands
- `[8] cp: verify sonar`
  * Reviews quality gates
  * Examines new issues
  * Verifies coverage metrics
  * Documentation: [Sonar Verification](../maintenance/sonar.md)

### 5. Documentation Commands
- `[9] cp: verify llm-rules`
  * Verifies all documentation against documentation-management.md rules
  * Checks document structure and organization
  * Validates cross-references and links
  * Documentation: [Rules Verification](commands/verify/rules.md)

- `[10] cp: update llm-rules`
  * Interactively updates or creates documentation
  * Ensures complete understanding before changes
  * Maintains documentation standards
  * Documentation: [Rules Update](commands/update/rules.md)

- `[11] cp: requirements create`
  * Creates requirements and specification structure
  * Sets up Requirements.adoc
  * Establishes specification subdocuments
  * Documentation: [Requirements Structure](../requirements/requirements-document.md)

## Usage Instructions

### Command Selection
1. Use `cp: list` or number [1-11] to display/select commands
2. Enter exact command with colon format (e.g. `cp: fix javadoc`)
3. Follow the defined workflow for each command
4. User confirmation may be required based on command type

### Command Execution
1. Commands are executed in defined order
2. Each command follows its documented process
3. Success criteria must be met to complete
4. Error handling is provided for each command

## Success Criteria
1. All commands are properly documented
2. Command selection works reliably
3. Command execution follows defined process
4. Error handling is effective
5. User feedback is clear

## See Also
- [Command Prompt Interface](commands/core/cp.md): Command prompt interface
- [Documentation Management](documentation-management.md): Documentation management
- Individual command documentation in respective directories
