---
name: cui-diagnostic-patterns
description: Tool usage patterns and best practices for diagnostic commands - use non-prompting tools (Glob, Read, Grep) instead of Bash to avoid user interruptions
allowed-tools: Read, Grep
---

# CUI Diagnostic Patterns

Tool usage patterns and best practices for building diagnostic commands that run without user interruptions.

## What This Skill Provides

### Core Tool Usage Patterns
- File discovery using Glob (replaces find, ls)
- Existence checking using Read and Glob (replaces test)
- Content searching using Grep (replaces grep via Bash)
- Error handling strategies
- Result parsing patterns

### Why Non-Prompting Tools?

**Problem**: Bash commands (find, test, ls, grep) trigger user prompts for confirmation.

**Impact**:
- Diagnostics interrupt users constantly
- Cannot run in automated workflows
- Poor user experience
- Slow execution with interaction delays

**Solution**: Use non-prompting tools (Glob, Read, Grep) that execute automatically.

### Design Principle

**CRITICAL**: Diagnostic commands must run completely unattended without user prompts.

This skill documents the approved patterns for all file operations, content searches, and validation checks.

## When to Activate This Skill

Activate this skill when:
- Building diagnostic commands
- Implementing file discovery logic
- Checking file/directory existence
- Searching file content
- Validating project structure
- Analyzing component health
- Performing automated quality checks

## Standards Organization

All patterns are organized in the `standards/` directory:

- `tool-usage-patterns.md` - Core tool selection guide and basic patterns
- `file-operations.md` - File and directory checking patterns with error handling
- `search-operations.md` - Content search patterns and result parsing
- `error-handling.md` - Error handling strategies and graceful degradation

## Tool Access

This skill requires:
- **Read**: To load standards files
- **Grep**: To search within standards

## Usage Pattern

When this skill is activated, it loads all tool usage patterns. Diagnostic commands can then:

1. **Reference patterns by name**: "Use Pattern 1: File Discovery from cui-diagnostic-patterns"
2. **Follow guidelines**: "Follow file existence check pattern from cui-diagnostic-patterns"
3. **Apply error handling**: "Use error handling strategy from cui-diagnostic-patterns"

## Integration with Commands

### Diagnostic Commands

All diagnostic commands should activate this skill:

```
Skill: cui-diagnostic-patterns
```

Then reference patterns throughout their workflows:
- "Use Glob pattern for file discovery (Pattern 1)"
- "Use Read pattern for existence checks (Pattern 2)"
- "Use Grep pattern for content search (Pattern 3)"

### Benefits for Commands

Commands benefit by:
- Not duplicating tool usage guidelines
- Getting updated patterns automatically
- Following consistent standards
- Avoiding prompt-triggering operations

## Pattern Coverage

### File Discovery ✅
- Find files by extension
- Find files recursively
- Find directories
- List directory contents
- Count files

### Existence Checks ✅
- Check if file exists
- Check if directory exists
- Check if directory is empty
- Validate required structure

### Content Search ✅
- Search for patterns in files
- Find files containing patterns
- Search with line numbers
- Multi-pattern searches
- Case-sensitive/insensitive search

### Error Handling ✅
- Handle missing files gracefully
- Handle missing directories
- Handle empty results
- Provide meaningful error messages

## Related Skills

This skill is foundational for:
- All cui-diagnose-* commands
- Any command that needs file system operations
- Validation and quality check tools

## Maintenance Notes

This skill provides the authoritative patterns for:
- All file system operations in diagnostic commands
- Tool selection for non-prompting execution
- Error handling in automated workflows

When tool usage patterns need updates, modify files in `standards/` directory and all commands using this skill automatically benefit.

## Version

Version: 1.0.0 (Initial release)

Part of: cui-plugin-development-tools bundle

---

*This skill eliminates user prompts from diagnostic workflows by providing non-prompting tool usage patterns.*
