---
name: cui-diagnostic-patterns
description: Tool usage patterns for non-prompting file operations - use Glob, Read, Grep instead of Bash commands to avoid user interruptions in all agents and commands
allowed-tools: Read, Grep
---

# CUI Tool Usage Patterns

Tool usage patterns and best practices for building agents and commands that run without user interruptions.

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
- Agents/commands interrupt users constantly
- Cannot run in automated workflows
- Poor user experience
- Slow execution with interaction delays

**Solution**: Use non-prompting tools (Glob, Read, Grep) that execute automatically.

### Design Principle

**CRITICAL**: All agents and commands should prefer non-prompting tools for file operations to avoid user interruptions.

**Bash should ONLY be used for:**
- Git operations
- Build commands (mvn, npm, etc.)
- Operations that truly require shell execution

**Never use Bash for:**
- File discovery (find, ls) → Use Glob
- Existence checks (test -f, test -d) → Use Read/Glob
- Content search (grep, awk) → Use Grep
- Reading files (cat) → Use Read

This skill documents the approved patterns for all file operations, content searches, and validation checks.

## When to Activate This Skill

Activate this skill when building:
- **Diagnostic commands** - Commands that analyze other components
- **Validation commands** - Commands that check project state
- **Analysis agents** - Agents that examine code or files
- **Quality check agents** - Agents that verify standards
- **Any agent/command that performs file operations** - To ensure non-prompting execution

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

When this skill is activated, it loads all tool usage patterns. Agents and commands can then:

1. **Reference patterns by name**: "Use Pattern 1: File Discovery from cui-diagnostic-patterns"
2. **Follow guidelines**: "Follow file existence check pattern from cui-diagnostic-patterns"
3. **Apply error handling**: "Use error handling strategy from cui-diagnostic-patterns"

## Integration with Agents and Commands

### All Agents and Commands Performing File Operations

Any agent or command that performs file operations should activate this skill:

```
Skill: cui-diagnostic-patterns
```

Then reference patterns throughout their workflows:
- "Use Glob for file discovery (Pattern 1)"
- "Use Read for existence checks (Pattern 2)"
- "Use Grep for content search (Pattern 3)"

### Diagnostic Commands: Enforcement Requirement

**CRITICAL**: Diagnostic commands (`cui-diagnose-agents`, `cui-diagnose-commands`) must:
1. Activate this skill themselves (to run without prompts)
2. **Enforce** that agents and commands they diagnose also follow these patterns

**Enforcement checks:**
- Scan for problematic Bash usage: `find`, `test -f`, `test -d`, `grep`, `cat`, `ls`, `awk`
- Report as CRITICAL issues if found
- Provide remediation guidance referencing this skill

**Example diagnostic check:**
```
# Check for prohibited bash commands
problematic_commands = Grep(
    pattern="find |test -f|test -d|grep |cat |ls |awk ",
    path="<agent-or-command-file>",
    output_mode="content",
    -n=true
)

if problematic_commands:
    report_critical_issue(
        "Uses prohibited Bash commands for file operations",
        "Replace with non-prompting tools from cui-diagnostic-patterns skill"
    )
```

### Benefits

Agents and commands benefit by:
- Not duplicating tool usage guidelines
- Getting updated patterns automatically
- Following consistent standards
- Avoiding prompt-triggering operations
- Running fully automated without user interruption

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
- All cui-diagnose-* commands (diagnostic tools)
- All agents that perform file operations
- All commands that need file system operations
- Validation and quality check tools
- Analysis and reporting agents

## Maintenance Notes

This skill provides the authoritative patterns for:
- All file system operations in agents and commands
- Tool selection for non-prompting execution
- Error handling in automated workflows
- Best practices for file operations

When tool usage patterns need updates, modify files in `standards/` directory and all agents/commands using this skill automatically benefit.

## Quality Gate

**Diagnostic commands must enforce this skill:**
- `cui-diagnose-agents` checks agents for compliance
- `cui-diagnose-commands` checks commands for compliance
- Both report violations as CRITICAL issues
- Both provide remediation guidance

## Version

Version: 1.0.0 (Initial release)

Part of: cui-utility-commands bundle

---

*This skill eliminates user prompts from all agents and commands by providing comprehensive non-prompting tool usage patterns for file operations.*
