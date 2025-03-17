# Cascade Command Prompt

## Command: cp

### Purpose
Displays and manages the execution of all available Cascade commands through an interactive prompt.

### Important Note
All commands prefixed with `cp:` are AI assistant commands and must NEVER be executed in a shell. These commands are exclusively for communication with the AI assistant and are processed internally by the AI system.

### Process Overview

1. Command Display
   - Lists all available commands with numbers [1-11]
   - Shows command descriptions
   - Groups by category
   - Maintains consistent order

2. Command Selection
   - Accepts numeric input [1-11]
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
   - Shows numbered list [1-11] of all commands
   - Waits for user selection

2. List Commands
   ```
   cp: list
   ```
   or
   ```
   [1]
   ```
   - Shows numbered list [1-11] of all commands
   - Waits for user selection

3. Direct Command
   ```
   cp: [command-name]
   ```
   or
   ```
   [command-number]
   ```
   - Directly executes specific command
   - Example: `cp: fix javadoc` or `[5]`

### Command Categories

See [Complete Command Listing](../commands.md) for the complete numbered list [1-11]:
[1] Core Commands
[2-5] Java Maintenance Commands
[6-7] Memory Management Commands
[8] Quality Assurance Commands
[9-11] Documentation Commands

### Success Criteria
1. All commands from commands.md are listed correctly
2. Command selection works reliably
3. Command execution is successful
4. Error handling is effective
5. User feedback is clear

### See Also
- [Complete Command Listing](../commands.md): Complete command listing and categories
- [Command Documentation Overview](../../../README.adoc): Command documentation overview
- Individual command documentation files
