# Cascade Command Prompt

## Command: cp

### Purpose
Displays and manages the execution of all available Cascade commands through an interactive prompt.

### Process Overview

1. Command Display
   - Lists all available commands (from commands.md)
   - Shows numbered command list
   - Displays brief descriptions
   - Maintains alphabetical order

2. Command Selection
   - Accepts numeric input
   - Validates selection
   - Provides command preview
   - Confirms execution

3. Command Execution
   - Executes selected command
   - Maintains consistent workflow
   - Provides execution feedback
   - Handles errors gracefully

### Usage

1. Basic Command
   ```
   cp
   ```
   - Shows numbered list of all commands from commands.md
   - Waits for user selection

2. Direct Command
   ```
   cp: [command-name]
   ```
   - Directly executes specific command
   - Example: `cp: fix javadoc`

### Command Categories

See commands.md for the complete categorized list of commands:
1. Core Commands
2. Documentation Commands
3. Java Maintenance Commands
4. Memory Management Commands
5. Quality Assurance Commands

### Success Criteria
1. All commands from commands.md are listed correctly
2. Command selection works reliably
3. Command execution is successful
4. Error handling is effective
5. User feedback is clear

### See Also
- cascade/commands.md: Complete command listing and categories
- README.adoc: Command documentation overview
- Individual command documentation files
