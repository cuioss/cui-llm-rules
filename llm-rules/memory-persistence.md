# Memory Persistence Process

This document outlines the process for persisting and updating memory rules in the repository.

## Process Overview

When triggered by the prompt "cp: persist memory", follow these steps:

1. Update Documentation
   - Identify relevant `.md` files in `/home/oliver/git/cui-llm-rules/llm-rules/`
   - Make necessary updates or create new files
   - Ensure changes follow documentation guidelines
   - Verify all references exist

2. Update README.adoc
   - Maintain list of available Cascade Prompts
   - Update memory files overview
   - Add new prompts to the command table
   - Keep file descriptions current

3. Commit Changes
   - Add modified files
   - Use clear, descriptive commit message
   - Include overview of changes
   - Reference related documentation

## File Organization

Memory rules are organized in topic-specific files:
- `README.adoc`: Overview of prompts and memory files
- `documentation.md`: Documentation standards and practices
- `logging.md`: Logging conventions and tools
- `project.md`: Build and project structure rules
- `technologies.md`: Core technology stack
- `testing.md`: Testing frameworks and practices
- `memory-persistence.md`: This file - process for updating memories

## Validation Requirements

Before committing changes:
1. Verify all references exist
2. Ensure no speculative features
3. Maintain consistent terminology
4. Follow documentation structure
5. Keep changes focused and atomic
6. Verify README.adoc is updated
7. Check Cascade Prompt documentation is complete

## Commit Message Format

```markdown
cp: persist memory - [Brief description]

### Changes
[Category 1]
- Change detail 1
- Change detail 2

[Category 2]
- Change detail 1
- Change detail 2

### README Updates
- Added new Cascade Prompts: [Y/N]
- Updated memory files overview: [Y/N]
- Updated file descriptions: [Y/N]

### Validation
- All additions based on existing practices
- No speculative features added
- All references verified
- Consistent terminology maintained
- README.adoc properly updated
```

## Cascade Prompt Structure

The "cp: persist memory" prompt ensures:
1. Documentation is properly organized and maintained
2. README.adoc reflects all available prompts and memory files
3. Changes are properly tracked
4. Documentation remains consistent and accurate
