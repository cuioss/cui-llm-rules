# CUI Tool Usage Patterns (Non-Prompting File Operations)

Tool usage patterns and best practices for building agents and commands that run without user interruptions.

## Overview

This skill provides comprehensive patterns for implementing file operations using non-prompting tools. It eliminates user interruptions by replacing Bash commands with specialized tools (Glob, Read, Grep) that execute automatically.

**This skill applies to ALL agents and commands that perform file operations**, not just diagnostic commands.

## Problem Statement

**Traditional Approach**: Agents and commands that use Bash for file operations (find, test, ls, grep) trigger user prompts for every operation, making them:
- Interrupt users constantly
- Impossible to run in automated workflows
- Provide poor user experience
- Execute slowly due to interaction delays

**Solution**: Use non-prompting tools that execute automatically without requiring user confirmation.

## What This Skill Provides

### Core Tool Usage Patterns

#### Pattern 1: File Discovery
- Replace `find` and `ls` commands with **Glob** tool
- Discover files by extension, recursively, or by pattern
- List directory contents without prompts

#### Pattern 2: Existence Checks
- Replace `test -f` and `test -d` with **Read** + try/except or **Glob**
- Check file and directory existence
- Validate required structure

#### Pattern 3: Content Search
- Replace `grep` via Bash with **Grep** tool
- Search for patterns in files
- Find files containing specific content
- Extract structured information

#### Pattern 4: File Reading
- Use **Read** tool for all file content access
- Read entire files or specific line ranges
- Parse JSON, YAML, and structured formats

#### Pattern 5: Combining Patterns
- Chain operations for complex validations
- Discover, validate, and analyze in one workflow
- Optimize performance with progressive filtering

### Standards Files

All patterns are organized in the `standards/` directory:

- **tool-usage-patterns.md** - Core tool selection guide mapping operations to tools with basic patterns
- **file-operations.md** - File and directory checking patterns with error handling strategies
- **search-operations.md** - Content search patterns, integration validation, and result parsing
- **error-handling.md** - Error handling strategies and graceful degradation (planned)

## Tool Comparison

| Operation | ❌ Don't Use (Prompts) | ✅ Use (No Prompts) |
|-----------|----------------------|-------------------|
| Find files | `find`, `ls` | `Glob` |
| Check file exists | `test -f`, `cat` | `Read` + try/except |
| Check directory exists | `test -d` | `Glob` |
| Search content | `grep`, `rg` via Bash | `Grep` |
| Read files | `cat` via Bash | `Read` |
| Count items | `wc -l` via Bash | Count results |
| List directory | `ls -la` via Bash | `Glob` |

## When to Use This Skill

Activate this skill when building any agent or command that:
- Performs file discovery or listing
- Checks file or directory existence
- Searches file content
- Validates project structure
- Analyzes code or components
- Performs automated quality checks
- Needs to run without user interruption

**Examples:**
- **Diagnostic commands** (cui-diagnose-*)
- **Validation commands** (cui-build-and-verify, etc.)
- **Analysis agents** (code reviewers, quality checkers)
- **Project setup commands** (initialization, scaffolding)
- **Any agent/command that performs file system operations**

## Usage in Agents and Commands

### Activation

All agents and commands that perform file operations should activate this skill:

```markdown
Skill: cui-diagnostic-patterns
```

### Referencing Patterns

Agents and commands reference patterns throughout their workflows:

```markdown
## TOOL USAGE

Follow cui-diagnostic-patterns skill:
- Use Glob for file discovery (Pattern 1)
- Use Read + try/except for file existence checks (Pattern 2)
- Use Grep for content search (Pattern 3)

Refer to skill standards for complete pattern details.
```

### Benefits

Agents and commands benefit by:
- Not duplicating tool usage guidelines
- Getting updated patterns automatically
- Following consistent standards
- Avoiding prompt-triggering operations
- Running fully automated without user interruption

### Enforcement by Diagnostic Commands

**CRITICAL**: Diagnostic commands enforce these patterns:

- **cui-diagnose-agents**: Scans agents for prohibited Bash usage (find, test, grep, cat, etc.)
- **cui-diagnose-commands**: Scans commands for prohibited Bash usage

When violations are found:
- Reported as **CRITICAL issues**
- Blocks agents/commands from high quality scores
- Provides remediation guidance referencing this skill
- Recommends: "Activate cui-diagnostic-patterns skill and replace Bash commands"

## Pattern Coverage

### File Discovery ✅
- Find files by extension
- Find files recursively
- Find specific files by name
- Find directories
- Find multiple file types
- Count files matching pattern

### Existence Checks ✅
- Check if file exists
- Check if directory exists
- Check if directory is empty
- Validate required structure
- Check multiple files/directories
- Compare expected vs actual structure

### Content Search ✅
- Search for patterns in files
- Find files containing patterns
- Search with line numbers
- Multi-pattern searches (regex OR)
- Case-sensitive/insensitive search
- Search with context lines
- Filter by file type

### Integration Validation ✅
- Validate agent→command references
- Validate agent→skill references
- Check tool declarations
- Extract structured information
- Cross-reference validation

### Error Handling ✅
- Handle missing files gracefully
- Handle missing directories
- Handle empty results
- Provide meaningful error messages
- Graceful degradation strategies

## Example: Bundle Discovery

**Before (with prompts):**
```bash
find ~/git/cui-llm-rules/claude/marketplace/bundles -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
```
Triggers user prompt for `find` command.

**After (no prompts):**
```python
# Discover all bundles
bundles = Glob(pattern="*", path="~/git/cui-llm-rules/claude/marketplace/bundles")

# Extract bundle names
bundle_names = [path.split("/")[-1] for path in bundles]

# Sort alphabetically
bundle_names.sort()
```
Executes automatically without user interaction.

## Example: File Existence Check

**Before (with prompts):**
```bash
test -f {bundle_path}/README.md && echo "exists" || echo "missing"
```
Triggers user prompt for `test` command.

**After (no prompts):**
```python
# Check if README exists
try:
    readme_content = Read(file_path=f"{bundle_path}/README.md")
    readme_exists = True
    # Content already loaded for further processing
except Exception:
    readme_exists = False

# Report
if readme_exists:
    print("✅ README.md exists")
else:
    print("❌ Missing: README.md")
```
Executes automatically and loads content for validation.

## Example: Content Search

**Before (with prompts):**
```bash
grep -r "Skill:" {bundle_path}/agents/
```
Triggers user prompt for `grep` command.

**After (no prompts):**
```python
# Search for skill references
skill_refs = Grep(
    pattern="Skill:",
    path=f"{bundle_path}/agents",
    output_mode="content",
    -n=true
)

# Parse results
for match in skill_refs:
    # Extract and validate skill references
    process_skill_reference(match)
```
Executes automatically with structured results.

## Performance Benefits

### Speed
- Non-prompting tools execute immediately
- No waiting for user confirmation
- Batch operations process efficiently

### Reliability
- Consistent behavior across runs
- No human interaction errors
- Suitable for CI/CD integration

### User Experience
- Zero interruptions during diagnostics
- Complete diagnostic reports in seconds
- Focus on results, not confirmations

## Integration with Commands and Agents

### Components Using This Skill

**Diagnostic commands** (use and enforce):
- `/cui-diagnose-bundle` - Bundle structure and health validation
- `/cui-diagnose-agents` - Agent quality and compliance analysis (enforces patterns)
- `/cui-diagnose-commands` - Command structure and quality checks (enforces patterns)
- `/cui-diagnose-skills` - Skill validation and standards compliance

**Other commands and agents** (should use):
- Any agent that performs file system operations
- Any command that needs to scan, validate, or analyze files
- Build and verification tools
- Quality check agents
- Analysis and reporting tools

### Related Skills

This skill is foundational for:
- All cui-diagnose-* commands (diagnostic tools)
- All agents that perform file operations
- All commands requiring file system operations
- Validation and quality check tools
- Automated workflow tools

## Maintenance

This skill provides the authoritative patterns for:
- All file system operations in diagnostic commands
- Tool selection for non-prompting execution
- Error handling in automated workflows

When tool usage patterns need updates, modify files in the `standards/` directory and all commands using this skill automatically benefit.

## Version

Version: 1.0.0 (Initial release)

Part of: cui-utility-commands bundle

## Summary

**Golden Rule**: If the operation involves the file system, use Glob/Read/Grep, never Bash.

**Result**: Zero user prompts, fully automated agents and commands with excellent performance.

**Quality Gate**: Diagnostic commands enforce these patterns - agents and commands using Bash for file operations will be flagged as having CRITICAL issues.

---

*This skill eliminates user prompts from all agents and commands by providing comprehensive non-prompting tool usage patterns for file operations.*
