# Cascade Commands

## Command Format
The "cp" command is a standardized command format that triggers specific workflows.

## Available Commands

[1] Core Commands
   - `cp: list` - Command prompt interface
     * Lists all available commands
     * Interactive command selection
     * Command execution management

[2] Java Maintenance Commands
   - `cp: maintenance java prepare`
     * Creates feature branch
     * Performs initial verification
     * Sets up maintenance context

[3] - `cp: maintenance java perform`
     * Updates dependencies
     * Applies code cleanup
     * Improves code quality

[4] - `cp: maintenance java finalize`
     * Runs OpenRewrite recipes
     * Verifies build stability
     * Prepares pull request

[5] - `cp: fix javadoc`
     * Fixes Javadoc errors and warnings
     * Makes minimal modifications
     * Preserves content

[6] Memory Management Commands
   - `cp: commit llm-rules to memory`
     * One-time transfer from @llm-rules
     * Creates/updates memories
     * Establishes memory source of truth

[7] - `cp: persist memory to llm-rules`
     * Updates @llm-rules from memories
     * Maintains documentation structure
     * Ensures completeness

[8] Quality Assurance Commands
   - `cp: verify sonar`
     * Reviews quality gates
     * Examines new issues
     * Verifies coverage metrics

[9] Documentation Commands
   - `cp: verify llm-rules`
     * Checks consistency
     * Updates documentation
     * Ensures completeness

## Usage
- Enter `cp: list` or number [1-9] to display/select commands
- Enter the exact command with colon format (e.g. `cp: fix javadoc`)
- Follow the defined workflow for each command
- User confirmation may be required based on command type

## See Also
- cascade/cp.md: Command prompt interface documentation
- Individual command documentation files in maintenance/ and cascade/ directories
