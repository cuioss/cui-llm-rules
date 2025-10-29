# Diagnostic Commands Tool Usage Analysis

## Problem Statement

The cui-diagnose-* commands currently instruct agents to use Bash commands extensively, which triggers user prompts for every operation. This creates a poor user experience during diagnostics.

**Example from cui-diagnose-bundle.md (lines 100-145):**
```bash
# Check directories
test -d {bundle_path}/.claude-plugin
test -d {bundle_path}/agents

# Check files
test -f {bundle_path}/.claude-plugin/plugin.json
test -f {bundle_path}/README.md

# List files
ls -la {bundle_path}/

# Find components
find {bundle_path}/agents -name "*.md" -type f
find {bundle_path}/commands -name "*.md" -type f
```

**Issues:**
- 185 bash/find/grep/test occurrences across 4 diagnostic commands
- 41 bash code blocks with prompt-triggering commands
- Every `test`, `find`, `ls`, `grep` command requires user confirmation
- Makes diagnostics slow and interrupting

## Root Cause Analysis

The diagnostic commands were written before Claude Code had robust non-prompting tools. They rely on:

1. **Bash for file discovery**: `find`, `ls`
2. **Bash for existence checks**: `test -f`, `test -d`
3. **Bash for content search**: `grep`, `rg`
4. **Bash for directory listing**: `ls -la`

All of these trigger user prompts because Bash is designed for potentially dangerous operations.

## Solution: Use Non-Prompting Tools

Claude Code provides tools that don't require prompts:

| Operation | Current (Prompts) | Replace With (No Prompts) |
|-----------|------------------|---------------------------|
| Find files by pattern | `find dir -name "*.md"` | `Glob(pattern="**/*.md", path="dir")` |
| Check file exists | `test -f path/file` | `Read(file_path="path/file")` + error handling |
| Check directory exists | `test -d path/dir` | `Glob(pattern="*", path="path/dir")` |
| Search file content | `grep pattern file` | `Grep(pattern="...", path="file")` |
| List directory | `ls -la dir` | `Glob(pattern="*", path="dir")` |
| Count files | `find ... \| wc -l` | `Glob(...)` + count results |

## Proposed Fixes by Command

### 1. cui-diagnose-bundle.md

**Current approach:** 15 bash blocks with test/find/ls/grep

**Replacements needed:**

#### Discovery (Step 1)
```bash
# OLD (prompts):
find ~/git/cui-llm-rules/claude/marketplace/bundles -mindepth 1 -maxdepth 1 -type d

# NEW (no prompts):
Glob(pattern="*", path="~/git/cui-llm-rules/claude/marketplace/bundles")
```

#### Structure Validation (Step 3)
```bash
# OLD (prompts):
test -d {bundle_path}/.claude-plugin
test -f {bundle_path}/.claude-plugin/plugin.json

# NEW (no prompts):
Glob(pattern=".claude-plugin", path="{bundle_path}")
# If empty result → directory doesn't exist
Read(file_path="{bundle_path}/.claude-plugin/plugin.json")
# If error → file doesn't exist
```

#### Component Discovery (Step 6)
```bash
# OLD (prompts):
find {bundle_path}/agents -name "*.md" -type f
find {bundle_path}/commands -name "*.md" -type f
find {bundle_path}/skills -mindepth 1 -maxdepth 1 -type d

# NEW (no prompts):
Glob(pattern="*.md", path="{bundle_path}/agents")
Glob(pattern="*.md", path="{bundle_path}/commands")
Glob(pattern="*", path="{bundle_path}/skills")
```

#### Integration Checks (Step 7)
```bash
# OLD (prompts):
grep -r "SlashCommand\|/cui-" {bundle_path}/agents/
grep -r "Skill:\|skill:" {bundle_path}/agents/

# NEW (no prompts):
Grep(pattern="SlashCommand|/cui-", path="{bundle_path}/agents")
Grep(pattern="Skill:|skill:", path="{bundle_path}/agents")
```

### 2. cui-diagnose-agents.md

**Current approach:** 10 bash blocks with find/grep

**Replacements needed:**

#### Agent Discovery
```bash
# OLD:
find ~/git/cui-llm-rules/claude/marketplace/agents -name "*.md"
find ~/.claude/agents -name "*.md"

# NEW:
Glob(pattern="*.md", path="~/git/cui-llm-rules/claude/marketplace/agents")
Glob(pattern="*.md", path="~/.claude/agents")
```

#### Tool Coverage Analysis
```bash
# OLD:
grep -n "Read\|Edit\|Write" agent_file

# NEW:
Grep(pattern="Read|Edit|Write", path="agent_file", output_mode="content", -n=true)
```

### 3. cui-diagnose-commands.md

**Current approach:** 7 bash blocks with find/grep

**Replacements needed:**

#### Command Discovery
```bash
# OLD:
find ~/git/cui-llm-rules/claude/marketplace/bundles/*/commands -name "*.md"

# NEW:
Glob(pattern="*/commands/*.md", path="~/git/cui-llm-rules/claude/marketplace/bundles")
```

### 4. cui-diagnose-skills.md

**Current approach:** 9 bash blocks with find/grep/test

**Replacements needed:**

#### Skill Discovery
```bash
# OLD:
find ~/git/cui-llm-rules/claude/marketplace/skills -mindepth 1 -maxdepth 1 -type d

# NEW:
Glob(pattern="*", path="~/git/cui-llm-rules/claude/marketplace/skills")
```

#### Standards File Discovery
```bash
# OLD:
find {skill_path}/standards -name "*.md" -o -name "*.adoc"

# NEW:
Glob(pattern="standards/*.md", path="{skill_path}")
Glob(pattern="standards/*.adoc", path="{skill_path}")
```

## Implementation Strategy

### Phase 1: Add Tool Usage Guidelines (Quick Win)

Add to the beginning of each cui-diagnose-* command:

```markdown
## TOOL USAGE REQUIREMENTS

**CRITICAL**: Use non-prompting tools for all operations:

✅ **DO USE:**
- `Glob` - File/directory discovery (replaces find, ls)
- `Read` - Read files and check existence (replaces test -f, cat)
- `Grep` - Search content (replaces grep, rg)

❌ **DO NOT USE:**
- `Bash` with: find, test, ls, grep (triggers prompts)
- Use Bash ONLY for: git operations that require it

**File Existence Checks:**
```
# Check file exists:
Read(file_path="path/file")
# If successful → exists
# If error → doesn't exist

# Check directory exists:
Glob(pattern="*", path="path/dir")
# If results returned → exists
# If empty → doesn't exist
```

**File Discovery:**
```
# Find all .md files in directory:
Glob(pattern="*.md", path="directory")

# Find all .md files recursively:
Glob(pattern="**/*.md", path="directory")

# List directories:
Glob(pattern="*", path="parent_dir")
```

**Content Search:**
```
# Search for pattern:
Grep(pattern="search_term", path="file_or_dir", output_mode="content")

# Search with line numbers:
Grep(pattern="search_term", path="file", output_mode="content", -n=true)

# Find files containing pattern:
Grep(pattern="search_term", path="dir", output_mode="files_with_matches")
```
```

### Phase 2: Rewrite Bash Examples (Comprehensive Fix)

Replace every bash code block example with equivalent tool usage:

**Template for replacements:**

```markdown
#### Original Instruction:
```bash
find {path} -name "*.md" -type f
```

#### Updated Instruction:
Use Glob tool to discover files:
```
Glob(pattern="*.md", path="{path}")
```

Result: Array of file paths matching pattern
```

### Phase 3: Update Workflow Steps

For each step in diagnostic commands, update instructions:

**Before:**
```markdown
1. Use bash to find all agents:
   ```bash
   find ~/git/cui-llm-rules/claude/marketplace/agents -name "*.md"
   ```
2. For each agent file...
```

**After:**
```markdown
1. Use Glob tool to discover all agents:
   ```
   Glob(pattern="*.md", path="~/git/cui-llm-rules/claude/marketplace/agents")
   ```

2. For each file path in results...
```

## Benefits

1. **No User Prompts**: Entire diagnosis runs without interruption
2. **Faster Execution**: No waiting for user confirmations
3. **Better UX**: Professional, automated diagnostics
4. **Clearer Instructions**: Tool usage more explicit
5. **Consistent Patterns**: Same tool usage across all diagnostic commands

## Testing Strategy

After implementing fixes:

1. Run each diagnostic command
2. Verify no user prompts appear
3. Confirm all validations still work correctly
4. Check error handling when files don't exist

## Estimated Impact

- **cui-diagnose-bundle**: 15 bash blocks → 0 (100% reduction)
- **cui-diagnose-agents**: 10 bash blocks → 0 (100% reduction)
- **cui-diagnose-commands**: 7 bash blocks → 0 (100% reduction)
- **cui-diagnose-skills**: 9 bash blocks → 0 (100% reduction)
- **Total**: 41 prompt-triggering operations → 0

## Priority

**HIGH**: This significantly impacts usability of diagnostic tools.

Users expect diagnostics to run automatically without constant interruptions. Current behavior makes diagnostics frustrating and slow.

## Recommendation

Implement Phase 1 immediately (add guidelines), then Phase 2 systematically (rewrite examples) for each diagnostic command.
