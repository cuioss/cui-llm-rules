# LLM Command Execution Rules

## Purpose
Defines the critical rules and constraints for LLM assistants when executing commands and making changes to the @llm-rules repository.

## Related Documentation
- [Command Prompt Interface](../../cascade/commands/core/cp.md): Command execution interface
- [Documentation Management](../../cascade/documentation-management.md): Rules for documentation changes
- [Version Control Standards](version-control-standards.md): Standards for version control

## Critical Rules

### 1. Repository Changes
- LLM assistants CAN make file changes to @llm-rules
- LLM assistants must NEVER commit changes to @llm-rules
- All commits must be reviewed and executed by humans

### 2. Change Process
1. LLM makes necessary file changes
2. LLM notifies human that changes are ready for review
3. Human reviews and commits the changes
4. No automated commits under any circumstances

### 3. Allowed Operations
- Creating new files
- Modifying existing files
- Proposing documentation updates
- Suggesting structural changes

### 4. Forbidden Operations
- git commit
- git push
- Any other git operations that modify repository state

## Implementation Guidelines

### Making Changes
1. Use appropriate tools (write_to_file, edit_file)
2. Document changes clearly
3. Wait for human review
4. Never proceed with commit operations

### Error Prevention
1. Double-check before using git commands

### Common Mistakes to Avoid
1. Committing changes directly
2. Assuming permission to commit
3. Executing git commands that modify state
4. Not waiting for human review

## See Also
- [Progress Standards](progress-standards.md)
- [General Documentation Standards](../../standards/documentation/general-standard.md)
- [Javadoc Standards](../../standards/documentation/javadoc-standards.md)
- [Javadoc Maintenance](../../standards/documentation/javadoc-maintenance.md)
- [Change Management](change-management.md)
